# Getting the list of albums
1. Select all the text on the HTML page: https://www.shibuyahifi.com/schedule-hifi
2. Use Claude.ai to create a list of albums

```text
I want to pull data out of the attachment and put it into the following format

albums = [
    {"artist": "U2", "album": "The Unforgettable Fire"},
    {"artist": "Beach Boys", "album": "Pet Sounds"},
    {"artist": "Isaac Hayes", "album": "Hot Buttered Soul"},
    {"artist": "A Tribe Called Quest", "album": "The Low End Theory"},
    {"artist": "Funkadelic", "album": "Standing On The Verge Of Getting It On"},
}

<SELECT THE TABLE AND PASTE IT INTO THE CLAUDE.AI EDITOR>
```

Copy this result into the code.

Create a python program to create a new playlist with each of these albums.

# Setup
update the following variables:

```python
playlist_name = "Shibuya Hi-fi room, Seattle - <MONTH> 2024 playlist"
playlist_description = "A playlist containing some favorite albums."
```

# Usage
```bash
poetry shell
source .env
python3 ./nov24.py --dry-run  # to see how well it will work without creating the playlist
```
