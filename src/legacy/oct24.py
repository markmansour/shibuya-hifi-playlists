import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

# Spotify Developer Credentials
CLIENT_ID = 'bd22311518324fe58bb6be430781b9af'
# CLIENT_SECRET is in .env
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
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
    {"artist": "U2", "album": "The Unforgettable Fire"},
    {"artist": "Beach Boys", "album": "Pet Sounds"},
    {"artist": "Isaac Hayes", "album": "Hot Buttered Soul"},
    {"artist": "A Tribe Called Quest", "album": "The Low End Theory"},
    {"artist": "Funkadelic", "album": "Standing On The Verge Of Getting It On"},
    {"artist": "Tito Puente", "album": "El Rey Bravo"},
    {"artist": "DJ Hermigervill", "album": "The Dark Ages of Icelandic Music: Before BjörkMedley)"},  # not on spotify
    {"artist": "Bon Iver", "album": "Bon Iver, Bon Iver"},  # double names in spotify
    {"artist": "The Weeknd", "album": "House of Balloons"},
    {"artist": "Janes Addiction", "album": "Nothing's Shocking"},
    {"artist": "Janes Addiction", "album": "Ritual de lo Habitual"},
    {"artist": "Herbie Hancock", "album": "Head Hunters"},
    {"artist": "The National", "album": "Trouble Will Find Me"},
    {"artist": "Massive Attack", "album": "Mezzanine"},
    {"artist": "The Killers", "album": "Hot Fuss"},
    {"artist": "Kendrick Lamar", "album": "DAMN"},
    {"artist": "Stevie Nicks", "album": "Bella Donna"},
    {"artist": "Usher", "album": "My Way"},
    {"artist": "Patti Smith", "album": "Horses"},
    {"artist": "The Beatles", "album": "Revolver"},
    {"artist": "Laserbeans", "album": "Pure Paradise"},
    {"artist": "Radiohead", "album": "OK Computer"},
    {"artist": "Khruangbin", "album": "Texas Sun"},
    {"artist": "Khruangbin", "album": "Texas Moon"},
    {"artist": "Etta James", "album": "Tell Mama"},
    {"artist": "David Bowie", "album": "The Rise and Fall of Ziggy Stardust and the Spiders From Mars"},
    {"artist": "Nina Simone", "album": "Nina Simone Sings the Blues"},
    {"artist": "Portishead", "album": "Dummy"},
    {"artist": "Pink Floyd", "album": "Dark Side of the Moon"},
    {"artist": "Art Blakey and the Jazz Messengers", "album": "Moanin'"},
    {"artist": "LCD Soundsystem", "album": "Sound of Silver"},
    {"artist": "Led Zeppelin", "album": "Physical Graffiti"},
    {"artist": "Alicia Keys", "album": "The Diary of Alicia Keys"},
    {"artist": "Frank Ocean", "album": "Blonde"},
    {"artist": "Pearl Jam", "album": "Ten"},
    {"artist": "Black Crowes", "album": "The Southern Harmony and Musical Companion"},
    {"artist": "Wilco", "album": "Sky Blue Sky"},
    {"artist": "Hozier", "album": "Unreal Unearth"},
#    {"artist": "Michael Jackson", "album": "Thriller (1982)"}
]


# Create a new playlist
user_id = sp.current_user()['id']
playlist_name = "Shibuya Seattle - October 2024"
playlist_description = "Shibuya Hifi Room, Seattle - October 2024 playlist"
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=playlist_description)

# Search for each album and add the tracks to the playlist
for album in albums:
    query = f"album:\"{album['album']}\" artist:\"{album['artist']}\""
    results = sp.search(q=query, type='album', limit=1)
    albums_found = results['albums']['items']
    if albums_found:
        album_id = albums_found[0]['id']
        album_tracks = sp.album_tracks(album_id)
        track_uris = [track['uri'] for track in album_tracks['items']]
        sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
        print(f"Added album '{album['album']}' by {album['artist']}")
    else:
        print(f"Album '{album['album']}' by '{album['artist']}' not found on Spotify.")

print(f"Playlist '{playlist_name}' created successfully!")


query = f"album:\"Nothing's Shocking\" artist:\"Jane's Addiction\""
results = sp.search(q=query, type='album', limit=1)
albums_found = results['albums']['items']

query = f"album:\"Nothing's Shocking\" artist:\"Jane's Addiction\""
sp.search(q= f"album:\"Nothing's Shocking\" artist:\"Jane's Addiction\"", type='album', limit=1)['albums']['items']
