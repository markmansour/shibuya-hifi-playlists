import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import time

load_dotenv()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_uri='https://localhost:8888/callback',
    scope='playlist-modify-public'
), retries=0)

print("Testing simple search (no field filters)...")
time.sleep(5)
try:
    result = sp.search(q="Miles Davis Kind of Blue", type='album', limit=1)
    print(f"✓ Success: {len(result['albums']['items'])} results")
except Exception as e:
    print(f"✗ Failed: {e}")
