#!/usr/bin/env python3
"""Test Spotify API credentials without cache"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import sys

def test_credentials(env_file=None, scope='playlist-modify-public'):
    """Test if Spotify credentials in .env are valid"""

    # Default to .env in the project root
    if env_file is None or env_file == '.':
        import pathlib
        env_file = pathlib.Path(__file__).parent.parent.parent / '.env'

    load_dotenv(env_file)

    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI", "http://127.0.0.1:8888/callback")

    if not CLIENT_ID or not CLIENT_SECRET:
        print("✗ CLIENT_ID or CLIENT_SECRET not found in .env")
        return False

    print(f"Testing CLIENT_ID: {CLIENT_ID[:10]}...")
    print(f"Testing CLIENT_SECRET: {CLIENT_SECRET[:10]}...")
    print(f"Testing REDIRECT_URI: {REDIRECT_URI}")
    print(f"Testing SCOPE: {scope}\n")

    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=scope,
            cache_path=None  # Disable cache for this test
        ), retries=0)

        user = sp.current_user()
        print(f"✓ Authentication successful: {user.get('display_name')}")
        return True
    except spotipy.exceptions.SpotifyOauthError as e:
        print(f"\n✗ OAuth Error:")
        print(f"  Error: {e.error}")
        print(f"  Description: {e.error_description}")
        print(f"  Full message: {str(e)}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {type(e).__name__}")
        print(f"  Message: {str(e)}")
        import traceback
        print(f"\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    scope = 'playlist-modify-public'

    # Parse arguments
    if len(sys.argv) > 1:
        scope = sys.argv[1]

    success = test_credentials(None, scope)  # None uses default path resolution
    sys.exit(0 if success else 1)
