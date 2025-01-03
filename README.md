# Getting the list of albums
### Grab the listsings (basic)
2. Select all the text on the HTML page: https://www.shibuyahifi.com/schedule-hifi
2. Use Claude.ai to create a list of albums

### Grab the listing (automated)
```bash
brew install html2text
backupfile=shibuya-schedule-$(date -u +"%Y-%m-%d").html
textfile=shibuya-schedule-$(date -u +"%Y-%m-%d").txt
curl https://www.shibuyahifi.com/schedule-hifi -o $backupfile
html2text $backupfile > $textfile
```

###  Convert listing to python datastructure
```text
I want to pull data out of the attachment and put it into the following format.  Sort by the date the albums will be played, and not the year they were released.  Remove any duplicates.  Remove "Deep Listening" from any prefixes.

albums = [
    {"date": "Tuesday, Dec 3, 2024 6:00 PM", "artist": "Herbert von Karajan, Berlin Philharmonic", "album": "Ludwig van Beethoven, Symphony No. 7", "year": 1962},
    {"date": "Tuesday, Dec 3, 2024 8:00 PM", "artist": "Funkadelic", "album": "Maggot Brain", "year": 1971},
    {"date": "Wednesday, Dec 4, 2024 8:00 PM", "artist": "KISS", "album": "Destroyer", "year": 1976},
    {"date": "Thursday, Dec 5, 2024 7:30 PM", "artist": "Chappell Roan", "album": "The Rise and Fall of a Midwest Princess", "year": 2023}
]

<EITHER SELECT THE TABLE AND PASTE IT INTO THE CLAUDE.AI EDITOR>
OR
<UPLOAD THE ATTACHMENT $textfile>
```

### Prepare the new script
1. Duplicate the previous month's python file
2. Copy this result of the alumns in a python data structure into the code.
3. Update the following variables:

```python
playlist_name = "Shibuya Hi-fi room, Seattle - <MONTH> <YEAR> playlist"
playlist_description = "A playlist containing some favorite albums."
```

# Usage
```bash
poetry shell
source .env
python3 ./nov24.py --dry-run  # to see how well it will work without creating the playlist
```
