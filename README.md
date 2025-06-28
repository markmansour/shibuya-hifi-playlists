# The way
The `create_new_playlist.sh` command will
1. Scrape the album data from the Shibuya Lounge website to a html file
2. Convert the html file into text for easier parsing by `llm`
2. Write out a prospective playlist for a month to a CSV file - either the current month or specify the target month
3. create a Spotify playlist using the newly created CSV as input

e.g.
```./create_new_playlist.sh --month July```

# Requirements
* `html2text`
* `llm`
* Python and Poetry


---

# The old way
# Getting the list of albums
### Grab the listing (automated)
```bash
brew install html2text
backupfile=shibuya-schedule-$(date -u +"%Y-%m-%d").html
textfile=shibuya-schedule-$(date -u +"%Y-%m-%d").txt
csvfile=./data/shibuya-schedule-$(date -u +"%Y-%m-%d").csv
curl https://www.shibuyahifi.com/schedule-hifi -o $backupfile
html2text $backupfile > $textfile
cat $textfile | pbcopy
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
```
pbpaste > $csvfile
```

# Usage
```bash
poetry run python ./src/shibuyahifi-uploader.py --input-file $csvfile
```

# Notes for me
### Automating the downloading of text
Can I use something like `https://pypi.org/project/html2text/` to pull down the data and then work with claude to build a repeatable parser?
