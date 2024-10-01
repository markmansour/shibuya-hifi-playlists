# Getting the list of albumns
1. Select all the text on the HTML page: https://www.shibuyahifi.com/schedule-hifi
2. Use ChatGPT to create a list of albumns
```text
pull out the band name and albums in the below text and display it as a table: <PASTE>

(untested)
create a python array containing dictionaries of "artist" and "album" in the following format:

albums = [
    {"artist": "Tom Petty", "album": "Wildflowers"},
    {"artist": "The National", "album": "High Violet"},
]
```

Copy this result into the code.

Create a python program to create a new playlist with each of these albums.


# Setup
update the following variables:

```python
playlist_name = "Shibuya Hi-fi room, Seattle - September 2024 playlist"
playlist_description = "A playlist containing some favorite albums."
```

# Usage
```bash
poetry shell
source .env
python3 ./sept24.py
```

