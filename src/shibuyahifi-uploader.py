import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import argparse
import re
import json
import csv
from datetime import datetime
import time
import sys
import pickle
from pathlib import Path


def clean_string(s):
    """Remove non-alphanumeric characters and return lowercase string"""
    return re.sub(r'[^a-zA-Z0-9\s]', '', s).lower()


class SearchCache:
    """Cache search results to avoid repeated API calls"""
    def __init__(self, cache_file=".search_cache.pkl"):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()

    def _load_cache(self):
        """Load cache from disk if it exists"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        """Save cache to disk"""
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)

    def get(self, artist, album):
        """Get cached result for artist:album"""
        key = f"{artist.lower()}:{album.lower()}"
        return self.cache.get(key)

    def set(self, artist, album, result):
        """Cache a search result"""
        key = f"{artist.lower()}:{album.lower()}"
        self.cache[key] = result
        self._save_cache()

    def size(self):
        """Return cache size"""
        return len(self.cache)


def load_playlist_data(file_path):
    """
    Load playlist data from a file. Supports both JSON and CSV formats.
    Returns a list of dictionaries containing album information.
    """
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    elif file_ext == '.csv':
        albums = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert year to integer if present
                if 'year' in row:
                    try:
                        row['year'] = int(row['year'])
                    except (ValueError, TypeError):
                        pass
                albums.append(row)
        return albums

    else:
        raise ValueError(f"Unsupported file format: {file_ext}")


def search_album(sp, artist, album, cache, dry_run=False, retry_count=0, max_retries=2):
    """Search for album with caching and smart retry logic"""
    # Check cache first
    cached_result = cache.get(artist, album)
    if cached_result is not None:
        return cached_result

    try:
        # Try exact search first (new limit: max 10 per Spotify Feb 2026 API changes)
        query = f"album:\"{album}\" artist:\"{artist}\""
        results = sp.search(q=query, type='album', limit=1, offset=0)
        albums_found = results['albums']['items']

        if not albums_found:
            # Try with "Vol." variations (Volume I → Vol.1, etc)
            album_with_vol = album.replace("Volume ", "Vol.")
            if album_with_vol != album:
                query = f"album:\"{album_with_vol}\" artist:\"{artist}\""
                results = sp.search(q=query, type='album', limit=1, offset=0)
                albums_found = results['albums']['items']

        if not albums_found:
            # Try with/without "The" prefix on artist name
            if not artist.startswith("The "):
                artist_with_the = f"The {artist}"
                query = f"album:\"{album}\" artist:\"{artist_with_the}\""
                results = sp.search(q=query, type='album', limit=1, offset=0)
                albums_found = results['albums']['items']
            elif artist.startswith("The "):
                artist_without_the = artist[4:]
                query = f"album:\"{album}\" artist:\"{artist_without_the}\""
                results = sp.search(q=query, type='album', limit=1, offset=0)
                albums_found = results['albums']['items']

        if not albums_found:
            # Fallback to simplified search without field filters
            simplified_query = f"{artist} {album}"
            simplified_query = clean_string(simplified_query)
            # Short delay before second search (1-2 seconds within 30-second window)
            time.sleep(1)
            results = sp.search(q=simplified_query, type='album', limit=1, offset=0)
            albums_found = results['albums']['items']

        # Cache the result (even if empty) to avoid re-searching
        cache.set(artist, album, albums_found)
        return albums_found

    except spotipy.exceptions.SpotifyException as e:
        error_str = str(e).lower()

        # Check for rate limit (429) or gateway errors (502)
        if e.http_status == 429 or "502" in error_str:
            # Try to extract Retry-After from response if available
            retry_after = 2 ** (retry_count + 1)  # Default: exponential backoff (2, 4, 8 seconds)

            if retry_count < max_retries:
                if not dry_run:
                    print(f"\nRate limited, waiting {retry_after}s before retry...", file=sys.stderr, flush=True)
                time.sleep(retry_after)
                return search_album(sp, artist, album, cache, dry_run, retry_count + 1, max_retries)
            else:
                # Cache failure so we don't retry endlessly
                cache.set(artist, album, [])
                return []
        else:
            raise
    except Exception as e:
        # Unexpected error - cache and skip
        cache.set(artist, album, [])
        return []


def main():
    # Add argument parser
    parser = argparse.ArgumentParser(description='Create Spotify playlist from album list')
    parser.add_argument('--dry-run', action='store_true',
                        help='Perform a dry run without creating playlist or adding tracks')
    parser.add_argument('--clear-cache', action='store_true',
                        help='Clear the search cache before running')
    parser.add_argument('--input-file', required=True,
                        help='Path to input file (JSON or CSV) containing album list')
    parser.add_argument('--playlist-name',
                        help='Name for the playlist (optional, defaults to month-based name)')
    args = parser.parse_args()

    # Clear cache if requested
    if args.clear_cache:
        cache_file = Path(".search_cache.pkl")
        if cache_file.exists():
            cache_file.unlink()
            print("Cache cleared.\n")

    load_dotenv()

    # Spotify Developer Credentials
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI", 'https://localhost:8888/callback')

    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: SPOTIFY_CLIENT_ID and CLIENT_SECRET not found in .env")
        print("Please set these environment variables in your .env file")
        return

    # Scope for accessing playlists
    SCOPE = 'playlist-modify-public'

    # Authenticate with Spotify
    # Disable built-in retries for development mode (too aggressive)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope=SCOPE),
                        retries=0)  # Disable auto-retries; we handle them manually

    # Initialize search cache
    cache = SearchCache()

    try:
        # Load albums from file
        albums = load_playlist_data(args.input_file)
    except Exception as e:
        print(f"Error loading playlist data: {e}")
        return

    # Determine month_year for description (always needed)
    try:
        first_date = datetime.strptime(albums[0]['date'], '%A %b %d, %Y %I:%M %p')
        month_year = first_date.strftime('%B %Y')
    except (KeyError, ValueError, IndexError):
        month_year = datetime.now().strftime('%B %Y')

    # Generate default playlist name if not provided
    if not args.playlist_name:
        playlist_name = f"Shibuya Hi-fi room, {month_year}"
    else:
        playlist_name = args.playlist_name

    if args.dry_run:
        print("=== DRY RUN MODE ===")
        print(f"Playlist: '{playlist_name}'")
        print(f"Albums: {len(albums)} | Cache: {cache.size()} entries")
        print(f"Estimated time: ~{len(albums) * 2 // 60} minutes\n")

        # Search for each album without creating playlist or adding tracks
        found_count = 0
        failed_albums = []
        for i, album in enumerate(albums, 1):
            album_name = album['album'][:40].ljust(40)
            artist_name = album['artist'][:20].ljust(20)
            print(f"[{i:2d}/{len(albums)}] {album_name} {artist_name}", end=" ", flush=True)
            albums_found = search_album(sp, album['artist'], album['album'], cache, dry_run=True)
            if albums_found:
                album_id = albums_found[0]['id']
                try:
                    album_tracks = sp.album_tracks(album_id)
                    track_count = len(album_tracks['items'])
                    found_artist = albums_found[0]['artists'][0]['name']
                    found_album = albums_found[0]['name']
                    print(f"✓")
                    found_count += 1
                    if found_artist != album['artist'] or found_album != album['album']:
                        print(f"     → Found: '{found_album}' by {found_artist}")
                except Exception as e:
                    print(f"✗")
                    failed_albums.append((album['album'], album['artist'], "rate limited"))
            else:
                print(f"✗")
                failed_albums.append((album['album'], album['artist'], "not found"))
            # Small delay between requests - respectful but not excessive
            time.sleep(1)

        print(f"\n{'='*70}")
        print(f"Result: {found_count}/{len(albums)} albums found")
        if failed_albums:
            print(f"\nFailed to find:")
            for album_name, artist_name, reason in failed_albums:
                print(f"  • {album_name} by {artist_name} ({reason})")
        print(f"\nCache: {cache.size()} entries")

    else:
        # Create a new playlist
        print(f"Creating playlist: '{playlist_name}'")
        user_id = sp.current_user()['id']
        playlist_description = f"Shibuya Hifi Room, Seattle - {month_year} playlist"
        playlist = sp.user_playlist_create(user=user_id, name=playlist_name,
                                           public=True, description=playlist_description)
        print(f"✓ Playlist created\n")

        # Search for each album and add the tracks to the playlist
        added_count = 0
        failed_albums = []
        for i, album in enumerate(albums, 1):
            album_name = album['album'][:40].ljust(40)
            artist_name = album['artist'][:20].ljust(20)
            print(f"[{i:2d}/{len(albums)}] {album_name} {artist_name}", end=" ", flush=True)
            albums_found = search_album(sp, album['artist'], album['album'], cache)
            if albums_found:
                try:
                    album_id = albums_found[0]['id']
                    album_tracks = sp.album_tracks(album_id)
                    track_uris = [track['uri'] for track in album_tracks['items']]
                    sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
                    found_artist = albums_found[0]['artists'][0]['name']
                    found_album = albums_found[0]['name']
                    print(f"✓")
                    added_count += 1
                    if found_artist != album['artist'] or found_album != album['album']:
                        print(f"     → Found: '{found_album}' by {found_artist}")
                except Exception as e:
                    print(f"✗")
                    failed_albums.append((album['album'], album['artist'], "rate limited"))
            else:
                print(f"✗")
                failed_albums.append((album['album'], album['artist'], "not found"))
            # Small delay between requests
            time.sleep(1)

        print(f"\n{'='*70}")
        print(f"Complete: {added_count}/{len(albums)} albums added")
        if failed_albums:
            print(f"\nFailed to add:")
            for album_name, artist_name, reason in failed_albums:
                print(f"  • {album_name} by {artist_name} ({reason})")
        print(f"\nPlaylist: https://open.spotify.com/playlist/{playlist['id']}")


if __name__ == "__main__":
    main()
