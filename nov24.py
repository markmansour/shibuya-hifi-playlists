import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import argparse
import re  # Add this import for string cleaning


def clean_string(s):
    """Remove non-alphanumeric characters and return lowercase string"""
    return re.sub(r'[^a-zA-Z0-9\s]', '', s).lower()


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


# Add argument parser
parser = argparse.ArgumentParser(description='Create Spotify playlist from album list')
parser.add_argument('--dry-run', action='store_true',
                    help='Perform a dry run without creating playlist or adding tracks')
args = parser.parse_args()

load_dotenv()

# Spotify Developer Credentials
CLIENT_ID = 'bd22311518324fe58bb6be430781b9af'
# CLIENT_SECRET is in .env
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = 'https://localhost:8888/callback'

# Scope for accessing playlists
SCOPE = 'playlist-modify-public'

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

# List of albums to add to the playlist
# Define a new set of bands/artists and albums
albums = [
    {"artist": "Daft Punk", "album": "Random Access Memories"},
    {"artist": "Radiohead", "album": "OK Computer"},
    {"artist": "Stan Getz", "album": "Getz/Gilberto #2"},
    {"artist": "Sade", "album": "Love Deluxe"},
    {"artist": "Various Artists", "album": "Xen Cuts"},
    {"artist": "Sly & The Family Stone", "album": "There's A Riot Goin' On"},
    {"artist": "Funkadelic", "album": "America Eats Its Young"},
    {"artist": "Sir Georg Solti", "album": "Mahler: Symphonies"},
    {"artist": "Radiohead", "album": "In Rainbows"},
    {"artist": "Fela Kuti", "album": "Fela's London Scene"},
    {"artist": "Mazzy Star", "album": "So Tonight That I Might See"},
    {"artist": "John Coltrane", "album": "Giant Steps"},
    {"artist": "DJ Shadow", "album": "Endtroducing....."},
    {"artist": "Omar Apollo", "album": "Ivory"},
    {"artist": "The Band", "album": "The Last Waltz"},
    {"artist": "Jeff Buckley", "album": "Grace"},
    {"artist": "Tame Impala", "album": "Current"},
    {"artist": "Massive Attack", "album": "Mezzanine"},
    {"artist": "Sigur Rós", "album": "Ágætis Byrjun"},
    {"artist": "Hermanos Gutierrez", "album": "Sonido Cósmico"},
    {"artist": "Led Zeppelin", "album": "II"},
    {"artist": "Miles Davis", "album": "Kind of Blue"},
    {"artist": "Marvin Gaye", "album": "What's Going On"},
    {"artist": "Kikagaku Moyo", "album": "Masana Temples"},
    {"artist": "Portishead", "album": "Dummy"},
    {"artist": "Outkast", "album": "Speakerboxx"},
    {"artist": "Outkast", "album": "The Love Below"},
    {"artist": "Talking Heads", "album": "Stop Making Sense"},
    {"artist": "Jimi Hendrix", "album": "Are You Experienced"},
    {"artist": "The National", "album": "Alligator"},
    {"artist": "Khruangbin", "album": "Texas Sun"},
    {"artist": "Khruangbin", "album": "Texas Moon"},
    {"artist": "J. Cole", "album": "2014 Forest Hills Drive"},
    {"artist": "David Bowie", "album": "Station to Station"},
    {"artist": "Daft Punk", "album": "Discovery"},
    {"artist": "D'Angelo", "album": "Voodoo"},
    {"artist": "Frank Ocean", "album": "Blonde"},
    {"artist": "Isaac Hayes", "album": "Hot Buttered Soul"},
    {"artist": "Beck", "album": "Hyperspace"},
    {"artist": "Pink Floyd", "album": "Wish You Were Here"},
    {"artist": "Pink Floyd", "album": "Dark Side of the Moon"},
    {"artist": "Ray LaMontagne", "album": "Supernova"},
    {"artist": "The Weeknd", "album": "House of Balloons"},
    {"artist": "Nine Inch Nails", "album": "The Downward Spiral"},
    {"artist": "Radiohead", "album": "The Bends"},
    {"artist": "Radiohead", "album": "OK Computer"},
    {"artist": "Radiohead", "album": "Kid A"},
    {"artist": "Radiohead", "album": "Amnesiac"},
    {"artist": "Radiohead", "album": "Hail To The Thief"},
    {"artist": "Radiohead", "album": "In Rainbows"}
]

if args.dry_run:
    print("=== DRY RUN MODE ===")
    print(f"Would create playlist: 'Shibuya Seattle - November 2024'")

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
    playlist_name = "Shibuya Seattle - November 2024"
    playlist_description = "Shibuya Hifi Room, Seattle - November 2024 playlist"
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=playlist_description)

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

# query = f"album:\"Voodoo\" artist:\"D'Angelo\""
# results = sp.search(q=query, type='album', limit=1)
# albums_found = results['albums']['items']
#
# query = f"album:\"Nothing's Shocking\" artist:\"Jane's Addiction\""
# sp.search(q= f"album:\"Nothing's Shocking\" artist:\"Jane's Addiction\"", type='album', limit=1)['albums']['items']
