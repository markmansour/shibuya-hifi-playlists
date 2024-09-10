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
albums = [
    {"artist": "Tom Petty", "album": "Wildflowers"},
    {"artist": "The National", "album": "High Violet"},
    {"artist": "Velvet Underground & Nico", "album": "Velvet Underground & Nico"},
    {"artist": "Charles Mingus", "album": "Ah Um"},
    {"artist": "Queens of the Stone Age", "album": "Songs for the Deaf"},
    {"artist": "Tupac Shakur", "album": "All Eyez on Me"},
    {"artist": "Notorious B.I.G.", "album": "Ready to Die"},
    {"artist": "Kehlani", "album": "It Was Good Until It Wasn't"},
    {"artist": "Amy Winehouse", "album": "Back to Black"},
    {"artist": "Tame Impala", "album": "Currents"},
    {"artist": "Santana", "album": "Abraxas"},
    {"artist": "John Coltrane", "album": "A Love Supreme"},
    {"artist": "Daft Punk", "album": "Random Access Memories"},
    {"artist": "Duke Ellington", "album": "Masterpieces"},
    {"artist": "Lana Del Rey", "album": "Ultraviolence"},
    {"artist": "Al Di Meola, John McLaughlin, Paco de Lucía", "album": "Friday Night in San Francisco"},
    {"artist": "Radiohead", "album": "In Rainbows"},
    {"artist": "Metallica", "album": "...And Justice for All"},
    {"artist": "Massive Attack", "album": "Blue Lines"},
    {"artist": "Pink Floyd", "album": "The Wall"},
    {"artist": "Terry Riley", "album": "A Rainbow in Curved Air"},
    {"artist": "Interpol", "album": "Antics"},
    {"artist": "Led Zeppelin", "album": "Houses of the Holy"},
    {"artist": "New Order", "album": "Power, Corruption & Lies"},
    {"artist": "Wilco", "album": "Yankee Hotel Foxtrot"},
    {"artist": "Tame Impala", "album": "Lonerism"},
    {"artist": "Tyler, The Creator", "album": "Goblin"},
    {"artist": "Frank Ocean", "album": "Channel Orange"},
]

# Create a new playlist
user_id = sp.current_user()['id']
playlist_name = "Shibuya Hi-fi room, Seattle - September 2024 playlist"
playlist_description = "A playlist containing some favorite albums."
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=playlist_description)

# Search for each album and add the tracks to the playlist
for album in albums:
    query = f"album:{album['album']} artist:{album['artist']}"
    results = sp.search(q=query, type='album', limit=1)
    albums_found = results['albums']['items']
    if albums_found:
        album_id = albums_found[0]['id']
        album_tracks = sp.album_tracks(album_id)
        track_uris = [track['uri'] for track in album_tracks['items']]
        sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
        print(f"Added album '{album['album']}' by {album['artist']}")
    else:
        print(f"Album '{album['album']}' by {album['artist']}' not found on Spotify.")

print(f"Playlist '{playlist_name}' created successfully!")
