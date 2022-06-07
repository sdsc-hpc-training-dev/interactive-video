# Interactive Video Tools & Documentation


## System Requirement
**Python > 3.8** (currenly installed to user home with [pyenv](https://github.com/pyenv/pyenv))

## Interactive Video (Webinar)

### Step 1
```bash
cd /misc/www/projects/education/training/interactive
python iv.py --webinar 202202_hello_webinar
```

### Step 2
* Upload video and transcript (.vtt) to the folder created with scp or a ssh agent that provides file transfering function
* Alternatively use `download.py` to download directly from google drive to the server 
<details>
  <summary>download.py usage</summary>
  
  #### Dependencies (pip install)
  `google-api-python-client` `google_auth_oauthlib`
  
  ```
  usage: python download.py [-h] [--verbose] [--hide-pg] [--no-color] [--skip-exist]
                   [--list-only] [--flat] [--ext EXT] --drive DRIVE --dist DIST
                   (--folder-name FOLDER_NAME | --folder-id FOLDER_ID)

optional arguments:
  -h, --help            show this help message and exit
  --verbose             Increase output verbosity
  --hide-pg             Hide progress bar
  --no-color            Hide ANSI colors
  --skip-exist          Skip already downloaded
  --list-only           List the files without downloading them
  --flat                Download files without preserving folder structures
  --ext EXT             File extension to download
  --drive DRIVE         Drive ID (token at the end of the URL at root level in the
                        drive)
  --dist DIST           Dist folder
  --folder-name FOLDER_NAME
                        Folder name. If multiple folder matches, download will not
                        start.
  --folder-id FOLDER_ID
                        Folder ID (token at the end of the URL
  ```
</details>

### Step 3
Edit `config.json` inside the folder created
<details>
  <summary>config.json format</summary>
  
  ```json
{
    "title": "Sample Title", // Window and document title
    "subtitle": "Sample subtitle",
    "description": "Sample description",
    "toc": {
        "TOC1": "01:50",
        "TOC2": "20:30"
    }, // Table of contents, [Text Content: key]: [Timestamp: value]
    "links": {
        "Link1": "https://sdsc.edu",
        "Link2": "https://github.com"
    }, // Links, [Text Content: key]: [Link: value]
    
    // Path can be absolute or relative to where the config.json is
    "mp4_path": "video.mp4", // Path to find the video file
    "vtt_path": "transcript.vtt" // Path to find the transcript file
}
```
</details>

## Interactive Video (Series)

### Creating the folder
```bash
cd /misc/www/projects/education/training/interactive
python iv.py --series 202202_hello_series --init "Series Name To Display On the Web"
```

### Adding Video
```bash
python iv.py --series 202202_hello_series --add video1
```
The command above will create `202202_hello_series/video1/config.json` which can be edited with the same way as a regular webinar. Materials (video and slides) can be downloaded the same way as well.

## Notes
```
iv.py --sync --build
```
`--sync` pulls XML from sdsc.edu and stores the data in `events.json`
`--build` reads events.json and builds `dev.html` from it
Use in order to make changes to dev.

## Experimental Scripts

-   `split.js` - splits a VTT file and FFMPEG command to split a video
-   `combine.js` - combines multiple VTT files and FFMPEG command to combine videos
-   `download.py` - uses google api to download files from drives
-   `stats.py` - generate site statistics from Apache log files

## Files (For Backup)
-   `assets`: assets (js/css/image, sdsc footer & header)
-   `scripts`: experimental scripts to process the videos/transcripts or download them from google drive

