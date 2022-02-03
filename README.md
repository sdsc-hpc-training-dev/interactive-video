# Interactive Video Tools & Documentation


## System Requirement
**Python > 3.8** (currenly installed to user home with [pyenv](https://github.com/pyenv/pyenv))

## Creating Interactive Video (Webinar)

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
  
  ### TODO
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

## Creating Interactive Video (Series)
TODO

## Experimental Scripts

-   `split.js` - splits a VTT file and FFMPEG command to split a video
-   `combine.js` - combines multiple VTT files and FFMPEG command to combine videos
-   `download.py` - uses google api to download files from drives
-   `stats.py` - generate site statistics from Apache log files

## Files (For Backup)
-   `assets`: assets (js/css/image, sdsc footer & header)
-   `scripts`: experimental scripts to process the videos/transcripts or download them from google drive

