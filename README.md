# Shibuya Hi-Fi Uploader

Scrapes the [Shibuya Hi-Fi schedule](https://www.shibuyahifi.com/hifi-schedule), parses it with Claude AI to extract album data, and creates a Spotify playlist of the scheduled albums.

## Quick Start

```bash
# Full pipeline: download schedule → parse with LLM → upload to Spotify
./create_new_playlist.sh --month June --year 2026

# Or just upload from an existing CSV file
./create_new_playlist.sh --csv-file data/shibuya-schedule-June-2026-2026-05-20.csv

# Dry run: see what would be added without creating the playlist
poetry run python ./src/shibuyahifi-uploader.py --input-file data.csv --dry-run
```

## Setup

### 1. Install Dependencies

```bash
# System dependencies
brew install html2text
brew install llm
llm install llm-anthropic

# Python dependencies
poetry install

# JavaScript dependencies (optional, but recommended for reliable page fetching)
npm install
```

**Note on Playwright:** The `npm install` step is optional but highly recommended. Playwright automatically handles the JavaScript-heavy Shibuya Hi-Fi schedule page and clicks "Load More" until all albums are loaded. Without it, the script falls back to `curl`, which may miss dynamically-loaded content.

### 2. Configure Spotify Credentials

Create a Spotify app at [developer.spotify.com/dashboard/create](https://developer.spotify.com/dashboard/create):

1. Fill in the form:
   - **App name:** `shibuyahifi-uploader`
   - **App description:** `Upload the monthly Shibuya hifi lounge playlist`
   - **Redirect URIs:** `http://127.0.0.1:8888/callback`
   - **Which API/SDKs are you planning to use?** Check "Web API"
3. Accept the terms and create
4. Go to Settings and copy the **Client ID** and **Client Secret**

Add credentials to `.env`:
```env
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
```

**Note:** Development Mode apps have stricter rate limits (~3-5 requests/30 seconds). For production use with more frequent uploads, request Spotify to upgrade your app to Production Mode.

### 3. Claude API Key

Your Anthropic key is already configured with the `llm` tool and will be used automatically. No additional setup needed.

## Usage

### Full Pipeline

```bash
# Process current month
./create_new_playlist.sh

# Process specific month and year
./create_new_playlist.sh --month July --year 2025

# Use a local HTML file instead of downloading
./create_new_playlist.sh --html-file schedule.html --month June --year 2026
```

### Direct Python (Spotify Upload Only)

```bash
# Dry run: validate what will be added
poetry run python ./src/shibuyahifi-uploader.py --input-file data.csv --dry-run

# Create playlist and add albums
poetry run python ./src/shibuyahifi-uploader.py --input-file data.csv

# Clear search cache and force re-search
poetry run python ./src/shibuyahifi-uploader.py --input-file data.csv --clear-cache

# Custom playlist name
poetry run python ./src/shibuyahifi-uploader.py --input-file data.csv --playlist-name "My Playlist"
```

## How It Works

### 1. Download & Convert

The Shibuya Hi-Fi schedule page is JavaScript-heavy and requires clicking "Load More" multiple times to load all albums. The script handles this automatically:

**With Playwright (recommended):**
- Loads the page in a headless browser
- Automatically clicks "Load More" until all content loads
- Saves the fully-rendered HTML for parsing
- Fast and reliable

**Without Playwright (fallback):**
- Uses `curl` to download the page
- May miss dynamically-loaded albums
- Requires manual "Load More" clicks first

Once downloaded, `html2text` converts the HTML to plain text for LLM parsing.

### 2. Parse with LLM
Claude AI (claude-4-opus) parses the text and extracts albums as CSV:
```
date,artist,album,year
"Wednesday Jun 1, 2026 12:30 AM","Miles Davis","Kind of Blue",1959
"Wednesday Jun 1, 2026 3:30 AM","Pink Floyd","Dark Side of the Moon",1973
```

### 3. Search & Upload
The Python script:
- **Searches** for each album on Spotify (with intelligent fallbacks)
- **Caches** results locally to avoid re-searching
- **Adds** all found albums to a new playlist
- **Reports** what failed (if anything)

## Features

### Smart Search
Handles album name variations automatically:
- "Volume I" → "Vol.1"
- "Raconteurs" → "The Raconteurs"
- Falls back to simplified search if exact match fails

### Rate Limiting
- Respects Spotify's 30-second rolling window rate limit
- Uses only 1 request/second (safe for Development Mode)
- Caches searches to minimize API calls
- Future runs are much faster

### Search Cache
- `.search_cache.pkl` stores successful searches
- Dramatically speeds up re-running the same schedule
- Clear with `--clear-cache` flag if needed

### Detailed Reporting
Shows progress during upload and lists any albums that couldn't be found:
```
Complete: 67/69 albums added

Failed to find:
  • Some Album by Some Artist (not found)
```

## Troubleshooting

### "Rate limit" or "429" errors

Development Mode has strict rate limits. Solutions:
1. **Wait and retry** — The script handles retries automatically with exponential backoff
2. **Clear cache** — If cache has many failed searches: `--clear-cache`
3. **Request Production Mode** — Contact Spotify support to upgrade your app (requires justification of use)

### Album not found

Some albums may not be in Spotify's catalog or may have different titles:
- Check [Spotify](https://open.spotify.com) manually to verify the album exists
- If it exists with a different name, update the CSV
- Re-run with `--clear-cache` to force re-search

### Authentication fails

- Verify `CLIENT_ID` and `CLIENT_SECRET` are in `.env`
- Check that your Spotify app is still active (not deleted/suspended)
- Re-authenticate: delete `.cache` directory and run again

## Files

- `create_new_playlist.sh` — Main orchestration script
- `src/shibuyahifi-uploader.py` — Spotify playlist creation
- `data/` — CSV files with album schedules
- `logs/` — Execution logs and LLM debug scripts
- `.search_cache.pkl` — Local search result cache (auto-generated)

## Spotify API Notes

This tool uses Spotify's Web API with Development Mode access. Key constraints:
- **Rate limit:** ~3-5 requests per 30-second window
- **Max users:** 5 authorized users per app
- **Requires Premium:** Account owner must have Spotify Premium

See Spotify's [Feb 2026 migration guide](https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide) for current API requirements.

## Development

Run tests:
```bash
python -m pytest
```

Check syntax:
```bash
python -m py_compile src/shibuyahifi-uploader.py
```
