import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import argparse
import re
import json
import csv
from datetime import datetime


def clean_string(s):
    """Remove non-alphanumeric characters and return lowercase string"""
    return re.sub(r'[^a-zA-Z0-9\s]', '', s).lower()


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


def search_album(sp, artist, album, dry_run=False):
    """Search for album with fallback to simplified search"""
    # Try exact search first
    query = f"album:\"{album}\" artist:\"{artist}\""
    results = sp.search(q=query, type='album', limit=1)
    albums_found = results['albums']['items']

    if not albums_found:
        # Fallback to simplified search
        simplified_query = f"{artist} {album}"
        simplified_query = clean_string(simplified_query)
        if dry_run:
            print(f"Initial search failed. Trying simplified search: '{simplified_query}'")
        results = sp.search(q=simplified_query, type='album', limit=1)
        albums_found = results['albums']['items']

    return albums_found


def main():
    # Add argument parser
    parser = argparse.ArgumentParser(description='Create Spotify playlist from album list')
    parser.add_argument('--dry-run', action='store_true',
                        help='Perform a dry run without creating playlist or adding tracks')
    parser.add_argument('--input-file', required=True,
                        help='Path to input file (JSON or CSV) containing album list')
    parser.add_argument('--playlist-name',
                        help='Name for the playlist (optional, defaults to month-based name)')
    args = parser.parse_args()

    load_dotenv()

    # Spotify Developer Credentials
    CLIENT_ID = 'bd22311518324fe58bb6be430781b9af'
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URI = 'https://localhost:8888/callback'

    # Scope for accessing playlists
    SCOPE = 'playlist-modify-public'

    # Authenticate with Spotify
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope=SCOPE))

    try:
        # Load albums from file
        albums = load_playlist_data(args.input_file)
    except Exception as e:
        print(f"Error loading playlist data: {e}")
        return

    # Generate default playlist name if not provided
    if not args.playlist_name:
        # Try to get date from first album, fallback to current month
        try:
            first_date = datetime.strptime(albums[0]['date'], '%A %b %d, %Y %I:%M %p')
            month_year = first_date.strftime('%B %Y')
        except (KeyError, ValueError, IndexError):
            month_year = datetime.now().strftime('%B %Y')
        playlist_name = f"Shibuya Seattle - {month_year}"
    else:
        playlist_name = args.playlist_name

    if args.dry_run:
        print("=== DRY RUN MODE ===")
        print(f"Would create playlist: '{playlist_name}'")

        # Search for each album without creating playlist or adding tracks
        for album in albums:
            albums_found = search_album(sp, album['artist'], album['album'], dry_run=True)
            if albums_found:
                album_id = albums_found[0]['id']
                album_tracks = sp.album_tracks(album_id)
                track_count = len(album_tracks['items'])
                found_artist = albums_found[0]['artists'][0]['name']
                found_album = albums_found[0]['name']
                print(f"Would add: '{found_album}' by {found_artist} ({track_count} tracks)")
                if found_artist != album['artist'] or found_album != album['album']:
                    print(f"  Note: Found slightly different version of album:")
                    print(f"  Searched for: '{album['album']}' by {album['artist']}")
                    print(f"  Found: '{found_album}' by {found_artist}")
            else:
                print(f"WARNING: Album '{album['album']}' by '{album['artist']}' not found on Spotify")

        print("=== DRY RUN COMPLETE ===")

    else:
        # Create a new playlist
        user_id = sp.current_user()['id']
        playlist_description = f"Shibuya Hifi Room, Seattle - {month_year} playlist"
        playlist = sp.user_playlist_create(user=user_id, name=playlist_name,
                                           public=True, description=playlist_description)

        # Search for each album and add the tracks to the playlist
        for album in albums:
            albums_found = search_album(sp, album['artist'], album['album'])
            if albums_found:
                album_id = albums_found[0]['id']
                album_tracks = sp.album_tracks(album_id)
                track_uris = [track['uri'] for track in album_tracks['items']]
                sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
                found_artist = albums_found[0]['artists'][0]['name']
                found_album = albums_found[0]['name']
                print(f"Added album '{found_album}' by {found_artist}")
                if found_artist != album['artist'] or found_album != album['album']:
                    print(f"  Note: Found slightly different version of album:")
                    print(f"  Searched for: '{album['album']}' by {album['artist']}")
                    print(f"  Found: '{found_album}' by {found_artist}")
            else:
                print(f"Album '{album['album']}' by '{album['artist']}' not found on Spotify.")

        print(f"Playlist '{playlist_name}' created successfully!")


if __name__ == "__main__":
    main()