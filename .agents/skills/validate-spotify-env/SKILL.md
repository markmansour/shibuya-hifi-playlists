---
name: validate-spotify-env
description: Validate Spotify credentials in .env before running the uploader
disable-model-invocation: true
---

# Validate Spotify Environment

Checks that your Spotify app credentials are valid and your authentication works. Catches credential errors before you spend time running the uploader.

## What it does

1. Verifies `.env` has `CLIENT_ID`, `CLIENT_SECRET`, and `REDIRECT_URI`
2. Tests authentication with Spotify (may open browser for OAuth if token expired)
3. Reports your authenticated username
4. Shows you the exact config being used

## When to use

- **Before running** `/create-playlist.sh` for the first time
- **When authentication fails** during a playlist creation
- **After updating credentials** in your Spotify dashboard
- **When adding to a new machine** (initial setup)

## Usage

```bash
/validate-spotify-env
```

## What it checks

| Item | Example |
|------|---------|
| `CLIENT_ID` | Present and non-empty |
| `CLIENT_SECRET` | Present and non-empty |
| `REDIRECT_URI` | Matches your Spotify app settings |
| **Authentication** | Can successfully connect to Spotify API |
| **User** | Shows your authenticated Spotify username |

## Common Issues

### Missing credentials
```
✗ CLIENT_ID or CLIENT_SECRET not found in .env
```
→ Create `.env` with your credentials from [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)

### Wrong REDIRECT_URI
```
✗ OAuth Error: redirect_uri_mismatch
```
→ Check that `REDIRECT_URI` in `.env` exactly matches what you registered in Spotify app settings (including protocol, domain, port, and path)

### Authentication window doesn't appear
→ If running on a headless machine, you may need to copy the OAuth URL manually. The script will print it to the console.

## Implementation

Run the existing `test_spotify_credentials.py` to validate:

```bash
poetry run python src/utils/test_spotify_credentials.py
```

This will:
- Load your `.env`
- Test authentication
- Print your username if successful
- Show detailed errors if authentication fails
