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
    {"date": "Wednesday Jan 1, 2025 12:30 AM", "artist": "Miles Davis", "album": "Kind of Blue", "year": 1959},
    {"date": "Wednesday Jan 1, 2025 3:30 AM", "artist": "Pink Floyd", "album": "Dark Side of the Moon", "year": 1973},
    {"date": "Wednesday Jan 1, 2025 5:00 AM", "artist": "Daft Punk", "album": "Random Access Memories", "year": 2013},
    {"date": "Friday Jan 3, 2025 2:00 AM", "artist": "Nina Simone", "album": "I Put A Spell On You", "year": 1965},
    {"date": "Friday Jan 3, 2025 3:30 AM", "artist": "Coldplay", "album": "A Rush of Blood to the Head", "year": 2001},
    {"date": "Friday Jan 3, 2025 5:00 AM", "artist": "Beyoncé", "album": "Lemonade", "year": 2016},
    {"date": "Saturday Jan 4, 2025 2:00 AM", "artist": "Steely Dan", "album": "Aja", "year": 1977},
    {"date": "Saturday Jan 4, 2025 3:30 AM", "artist": "Chappell Roan",
     "album": "The Rise and Fall of a Midwest Princess", "year": 2023},
    {"date": "Saturday Jan 4, 2025 5:00 AM", "artist": "Tame Impala", "album": "Currents", "year": 2015},
    {"date": "Sunday Jan 5, 2025 12:30 AM", "artist": "Vangelis", "album": "Blade Runner (Original Motion Picture Soundtrack)", "year": 1994},
    {"date": "Sunday Jan 5, 2025 2:00 AM", "artist": "SOHN", "album": "Tremors", "year": 2014},
    {"date": "Sunday Jan 5, 2025 3:30 AM", "artist": "David Bowie", "album": "The Rise and Fall of Ziggy Stardust and the Spiders From Mars", "year": 1972},
    {"date": "Sunday Jan 5, 2025 5:00 AM", "artist": "Erykah Badu", "album": "Worldwide Underground", "year": 2003},
    {"date": "Wednesday Jan 8, 2025 2:00 AM", "artist": "Rush", "album": "Moving Pictures", "year": 1981},
    {"date": "Wednesday Jan 8, 2025 4:00 AM", "artist": "Oasis", "album": "Definitely, Maybe", "year": 1994},
    {"date": "Thursday Jan 9, 2025 2:00 AM", "artist": "Claudio Abbado, London Symphony Orchestra", "album": "Igor Stravinsky, The Rite of Spring", "year": 1976},
    {"date": "Thursday Jan 9, 2025 4:00 AM", "artist": "Aphex Twin", "album": "Selected Ambient Works", "year": 1992},
    {"date": "Friday Jan 10, 2025 2:00 AM", "artist": "Jimi Hendrix", "album": "Band of Gypsys", "year": 1970},
    {"date": "Friday Jan 10, 2025 3:30 AM", "artist": "Fiona Apple", "album": "Tidal", "year": 1996},
    {"date": "Friday Jan 10, 2025 5:00 AM", "artist": "Lauryn Hill", "album": "The Miseducation of Lauryn Hill", "year": 1998},
    {"date": "Saturday Jan 11, 2025 2:00 AM", "artist": "Eric Dolphy", "album": "Out To Lunch!", "year": 1964},
    {"date": "Saturday Jan 11, 2025 3:30 AM", "artist": "Soundgarden", "album": "Superunknown", "year": 1994},
    {"date": "Saturday Jan 11, 2025 5:00 AM", "artist": "Odesza", "album": "A Moment Apart", "year": 2017},
    {"date": "Saturday Jan 11, 2025 11:30 PM", "artist": "John Williams", "album": "Star Wars: A New Hope", "year": 1977},
    {"date": "Sunday Jan 12, 2025 1:00 AM", "artist": "Grant Green", "album": "Feelin' The Spirit", "year": 1963},
    {"date": "Sunday Jan 12, 2025 2:00 AM", "artist": "James Blake", "album": "Friends That Break Your Heart", "year": 2014},
    {"date": "Sunday Jan 12, 2025 5:00 AM", "artist": "Nilüfar Yanya", "album": "Painless", "year": 2022},
    {"date": "Wednesday Jan 15, 2025 2:00 AM", "artist": "Dead Can Dance", "album": "Dionysus", "year": 2018},
    {"date": "Wednesday Jan 15, 2025 4:00 AM", "artist": "Kyuss", "album": "Blues For The Hot Red Sun", "year": 1992},
    {"date": "Thursday Jan 16, 2025 2:00 AM", "artist": "Isaac Hayes", "album": "Black Moses", "year": 1971},
    {"date": "Thursday Jan 16, 2025 4:00 AM", "artist": "Bruce Springsteen", "album": "Darkness on the Edge of Town", "year": 1978},
    {"date": "Friday Jan 17, 2025 2:00 AM", "artist": "Sam Cooke", "album": "One Night Stand: Live at the Harlem Square Club, 1963", "year": 1963},
    {"date": "Friday Jan 17, 2025 3:30 AM", "artist": "D'Angelo", "album": "Voodoo", "year": 2000},
    {"date": "Friday Jan 17, 2025 3:30 AM", "artist": "The Who", "album": "Quadrophenia", "year": 1973},
    {"date": "Friday Jan 17, 2025 5:00 AM", "artist": "Jesus and Mary Chain", "album": "Psychocandy", "year": 1985},
    {"date": "Friday Jan 17, 2025 5:00 AM", "artist": "Tyler, The Creator", "album": "IGOR", "year": 2019},
    {"date": "Saturday Jan 18, 2025 2:00 AM", "artist": "Leon Thomas", "album": "Electric Dusk", "year": 2023},
    {"date": "Saturday Jan 18, 2025 8:30 PM", "artist": "Led Zeppelin", "album": "Led Zeppelin", "year": 1969},
    {"date": "Saturday Jan 18, 2025 10:00 PM", "artist": "Led Zeppelin", "album": "II", "year": 1969},
    {"date": "Saturday Jan 18, 2025 11:30 PM", "artist": "Led Zeppelin", "album": "III", "year": 1970},
    {"date": "Sunday Jan 19, 2025 1:00 AM", "artist": "Led Zeppelin", "album": "IV", "year": 1971},
    {"date": "Sunday Jan 19, 2025 2:30 AM", "artist": "Led Zeppelin", "album": "Houses of the Holy", "year": 1973},
    {"date": "Sunday Jan 19, 2025 3:30 AM", "artist": "Led Zeppelin", "album": "Physical Graffiti", "year": 1975},
    {"date": "Sunday Jan 19, 2025 5:00 AM", "artist": "Taylor Swift", "album": "1989", "year": 2014},
    {"date": "Wednesday Jan 22, 2025 2:00 AM", "artist": "Elvis Costello", "album": "My Aim Is True", "year": 1977},
    {"date": "Wednesday Jan 22, 2025 4:00 AM", "artist": "Stevie Ray Vaughn", "album": "Texas Flood", "year": 1983},
    {"date": "Thursday Jan 23, 2025 2:00 AM", "artist": "The Beatles", "album": "Abbey Road", "year": 1969},
    {"date": "Thursday Jan 23, 2025 4:00 AM", "artist": "Miles Davis", "album": "In A Silent Way", "year": 1969},
    {"date": "Friday Jan 24, 2025 2:00 AM", "artist": "Iggy and The Stooges", "album": "Raw Power", "year": 1973},
    {"date": "Friday Jan 24, 2025 3:30 AM", "artist": "Frank Ocean", "album": "Blonde", "year": 2016},
    {"date": "Friday Jan 24, 2025 5:00 AM", "artist": "Herbie Hancock", "album": "Headhunters", "year": 1973},
    {"date": "Saturday Jan 25, 2025 2:00 AM", "artist": "Omar Apollo", "album": "God Said No", "year": 2023},
    {"date": "Saturday Jan 25, 2025 3:30 AM", "artist": "Sampha", "album": "Lahai", "year": 2023},
    {"date": "Saturday Jan 25, 2025 5:00 AM", "artist": "Daft Punk", "album": "Discovery", "year": 2001},
    {"date": "Saturday Jan 25, 2025 11:30 PM", "artist": "Tan Dun and Yo Yo Ma", "album": "Crouching Tiger, Hidden Dragon", "year": 2000},
    {"date": "Sunday Jan 26, 2025 1:00 AM", "artist": "Ben E. King, Otis Redding, Doris Troy, Rufus Thomas, The Facons, The Coasters", "album": "Apollo Saturday Night!", "year": 1964},
    {"date": "Sunday Jan 26, 2025 2:00 AM", "artist": "Paul Simon", "album": "Graceland", "year": 1986},
    {"date": "Sunday Jan 26, 2025 3:30 AM", "artist": "Kendrick Lamar", "album": "Good Kid m.A.A.d city", "year": 2012},
    {"date": "Sunday Jan 26, 2025 5:00 AM", "artist": "Kendrick Lamar", "album": "To Pimp A Butterfly", "year": 2015},
    {"date": "Wednesday Jan 29, 2025 2:00 AM", "artist": "Cowboy Junkies", "album": "The Trinity Session", "year": 1988},
    {"date": "Wednesday Jan 29, 2025 4:00 AM", "artist": "Marvin Gaye", "album": "What's Going On", "year": 1971},
    {"date": "Thursday Jan 30, 2025 2:00 AM", "artist": "Tom Waits", "album": "Mule Variations", "year": 1999},
    {"date": "Thursday Jan 30, 2025 4:00 AM", "artist": "The National", "album": "Trouble Will Find Me", "year": 2013},
    {"date": "Friday Jan 31, 2025 2:00 AM", "artist": "Can", "album": "Ege Bamyasi", "year": 1972},
    {"date": "Friday Jan 31, 2025 3:30 AM", "artist": "Talk Talk", "album": "Laughing Stock", "year": 1991},
    {"date": "Saturday Feb 1, 2025 2:00 AM", "artist": "Raveena", "album": "Lucid", "year": 2021},
    {"date": "Saturday Feb 1, 2025 3:30 AM", "artist": "Khruangbin and Leon Bridges", "album": "Texas Sun", "year": "2020"},
    {"date": "Saturday Feb 1, 2025 5:00 AM", "artist": "Khruangbin and Leon Bridges", "album": "Texas Moon", "year": "2022"}
]


if args.dry_run:
    print("=== DRY RUN MODE ===")
    print(f"Would create playlist: 'Shibuya Seattle - January 2025'")

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
    playlist_name = "Shibuya Seattle - January 2025"
    playlist_description = "Shibuya Hifi Room, Seattle - January 2025 playlist"
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
