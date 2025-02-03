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
    {"date": "Tuesday, Dec 3, 2024 6:00 PM", "artist": "Herbert von Karajan, Berlin Philharmonic", "album": "Ludwig van Beethoven, Symphony No. 7", "year": 1962},
    {"date": "Tuesday, Dec 3, 2024 8:00 PM", "artist": "Funkadelic", "album": "Maggot Brain", "year": 1971},
    {"date": "Wednesday, Dec 4, 2024 8:00 PM", "artist": "KISS", "album": "Destroyer", "year": 1976},
    {"date": "Thursday, Dec 5, 2024 7:30 PM", "artist": "Chappell Roan", "album": "The Rise and Fall of a Midwest Princess", "year": 2023},
    {"date": "Friday, Dec 6, 2024 6:00 PM", "artist": "Rogê", "album": "Curyman II (Diamond West Record Release!)", "year": 2024},
    {"date": "Friday, Dec 6, 2024 7:30 PM", "artist": "Stevie Wonder", "album": "Fulfillingness' First Finale", "year": 1974},
    {"date": "Friday, Dec 6, 2024 9:00 PM", "artist": "Mac Miller", "album": "Circles", "year": 2020},
    {"date": "Saturday, Dec 7, 2024 7:30 PM", "artist": "Beastie Boys", "album": "The In Sound From Way Out", "year": 1996},
    {"date": "Saturday, Dec 7, 2024 9:00 PM", "artist": "Charli xcx", "album": "Brat", "year": 2024},
    {"date": "Tuesday, Dec 10, 2024 6:00 PM", "artist": "The Cars", "album": "The Cars", "year": 1978},
    {"date": "Tuesday, Dec 10, 2024 8:00 PM", "artist": "The Beatles", "album": "Rubber Soul", "year": 1965},
    {"date": "Wednesday, Dec 11, 2024 6:00 PM", "artist": "Thelonious Monk", "album": "Monk's Music", "year": 1957},
    {"date": "Wednesday, Dec 11, 2024 8:00 PM", "artist": "Nick Cave and the Bad Seeds", "album": "Ghosteen", "year": 2020},
    {"date": "Friday, Dec 13, 2024 6:00 PM", "artist": "Billie Holiday", "album": "Body and Soul", "year": 1957},
    {"date": "Friday, Dec 13, 2024 7:30 PM", "artist": "Björk", "album": "Debut", "year": 1993},
    {"date": "Friday, Dec 13, 2024 9:00 PM", "artist": "Tyler, the Creator", "album": "Chromokopia", "year": 2024},
    {"date": "Saturday, Dec 14, 2024 6:00 PM", "artist": "Talking Heads", "album": "Speaking In Tongues", "year": 1983},
    {"date": "Saturday, Dec 14, 2024 7:30 PM", "artist": "Solange", "album": "A Seat At The Table", "year": 2016},
    {"date": "Tuesday, Dec 17, 2024 6:00 PM", "artist": "Bob Dylan", "album": "Blonde on Blonde", "year": 1966},
    {"date": "Tuesday, Dec 17, 2024 8:00 PM", "artist": "Oasis", "album": "What's The Story Morning Glory?", "year": 1995},
    {"date": "Wednesday, Dec 18, 2024 6:00 PM", "artist": "Dawn Upshaw, London Sinfonietta, David Zinman", "album": "Henryk Górecki, Symphony No. 3", "year": 1992},
    {"date": "Wednesday, Dec 18, 2024 8:00 PM", "artist": "Mark Lanegan", "album": "Blues Funeral", "year": 2012},
    {"date": "Thursday, Dec 19, 2024 6:00 PM", "artist": "Nina Simone", "album": "High Priestess of Soul", "year": 1967},
    {"date": "Thursday, Dec 19, 2024 7:30 PM", "artist": "So...How's Your Girl?", "album": "Handsome Boy Modeling School", "year": 1999},
    {"date": "Thursday, Dec 19, 2024 9:00 PM", "artist": "Beyoncé", "album": "Lemonade", "year": 2016},
    {"date": "Friday, Dec 20, 2024 6:00 PM", "artist": "The National", "album": "Sleep Well Beast", "year": 2017},
    {"date": "Friday, Dec 20, 2024 7:30 PM", "artist": "Usher", "album": "My Way", "year": 1997},
    {"date": "Saturday, Dec 21, 2024 6:00 PM", "artist": "Cannonball Adderley", "album": "Something Else", "year": 1958},
    {"date": "Saturday, Dec 21, 2024 7:30 PM", "artist": "Lauryn Hill", "album": "The Miseducation of Lauryn Hill", "year": 1998},
    {"date": "Saturday, Dec 21, 2024 9:00 PM", "artist": "Queen", "album": "A Night At the Opera", "year": 1975},
    {"date": "Sunday, Dec 22, 2024 5:00 PM", "artist": "Vince Guaraldi", "album": "A Charlie Brown Christmas", "year": 1965},
    {"date": "Sunday, Dec 22, 2024 6:00 PM", "artist": "Frank Ocean", "album": "Blonde", "year": 2016},
    {"date": "Sunday, Dec 22, 2024 7:30 PM", "artist": "Herbie Hancock", "album": "Headhunters", "year": 1973},
    {"date": "Monday, Dec 23, 2024 6:00 PM", "artist": "Count Basie and Frank Sinatra", "album": "It Might As Well Swing", "year": 1964},
    {"date": "Monday, Dec 23, 2024 7:30 PM", "artist": "Radiohead", "album": "In Rainbows", "year": 2007},
    {"date": "Thursday, Dec 26, 2024 6:00 PM", "artist": "Taylor Swift", "album": "Fearless (Taylor's Version)", "year": 2021},
    {"date": "Thursday, Dec 26, 2024 7:30 PM", "artist": "Led Zeppelin", "album": "IV", "year": 1970},
    {"date": "Thursday, Dec 26, 2024 9:00 PM", "artist": "Kendrick Lamar", "album": "DAMN", "year": 2017},
    {"date": "Friday, Dec 27, 2024 6:00 PM", "artist": "Willie Nelson", "album": "Stardust", "year": 1978},
    {"date": "Friday, Dec 27, 2024 7:30 PM", "artist": "Marvin Gaye", "album": "I Want You", "year": 1976},
    {"date": "Friday, Dec 27, 2024 9:00 PM", "artist": "Flaming Lips", "album": "Yoshimi Battles the Pink Robots", "year": 2002},
    {"date": "Tuesday, Dec 31, 2024 6:00 PM", "artist": "Miles Davis", "album": "Kind of Blue", "year": 1959},
    {"date": "Tuesday, Dec 31, 2024 7:30 PM", "artist": "Pink Floyd", "album": "Dark Side of the Moon", "year": 1973},
    {"date": "Tuesday, Dec 31, 2024 9:00 PM", "artist": "Daft Punk", "album": "Random Access Memories", "year": 2013}
]
if args.dry_run:
    print("=== DRY RUN MODE ===")
    print(f"Would create playlist: 'Shibuya Seattle - December 2024'")

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
    playlist_name = "Shibuya Seattle - December 2024"
    playlist_description = "Shibuya Hifi Room, Seattle - December 2024 playlist"
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
