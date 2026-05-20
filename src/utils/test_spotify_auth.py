import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

print(f"CLIENT_ID: {CLIENT_ID[:10]}..." if CLIENT_ID else "CLIENT_ID: NOT SET")
print(f"CLIENT_SECRET: {'SET' if CLIENT_SECRET else 'NOT SET'}")

try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri='https://localhost:8888/callback',
        scope='playlist-modify-public'
    ), retries=0)
    
    print("\n✓ Authentication successful")
    user = sp.current_user()
    print(f"✓ Current user: {user.get('display_name', user.get('id'))}")
    
    # Try a simple search
    print("\nAttempting first search...")
    result = sp.search(q="album:Kind of Blue artist:Miles Davis", type='album', limit=1)
    print(f"✓ Search successful: {len(result['albums']['items'])} results")
    
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}")
    print(f"  {str(e)}")
