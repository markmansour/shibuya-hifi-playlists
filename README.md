# Getting the list of albums
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

date,artist,album,year
"Wednesday Jan 1, 2025 12:30 AM","Miles Davis","Kind of Blue",1959
"Wednesday Jan 1, 2025 3:30 AM","Pink Floyd","Dark Side of the Moon",1973
"Wednesday Jan 1, 2025 5:00 AM","Daft Punk","Random Access Memories",2013

<EITHER SELECT THE TABLE AND PASTE IT INTO THE CLAUDE.AI EDITOR>
OR
<UPLOAD THE ATTACHMENT $textfile>
```

download the playlist to the `./data/` directory. 

# Usage
```bash
poetry run python ./src/shibuyahifi-uploader.py --input-file ./data/playlist-data-20250203.csv 
```
