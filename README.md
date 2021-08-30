# Interactive Video Refactored Template

Refactored old interactive video project into a modular & easy to use template

## Directories and Files

-   `assets`: assets used by _this_ project (not to be confused with `sdsc` which includes sdsc header & footer templates)
-   `sdsc`: header & footer files
-   `scripts`: useful scripts to process the videos/transcripts/download from google drive
-   `.gitignore`: configured to ignore everything else so we can create other folders and put stuff in them without worrying about changes to the repo
-   `.prettierrc`: good format tool rc file for my VSCode extension

## How to Use

1. Make a new directory and copy `config.json` from `sample.json` to it
2. Modify `config.json` and test the site
3. Done!

## Config Format

Here's annotated `sample.json`:

```
{
    "title": "HPC Training Week 4 CUDA w/ Python", // Window and document title
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
    "mp4_path": "../recordings/week4.mp4", // Path to find the video file
    "vtt_path": "../recordings/week4.vtt" // Path to find the transcript file
}
```

## Scripts

-   `split.js` - splits a VTT file and FFMPEG command to split a video
-   `combine.js` - combines multiple VTT files and FFMPEG command to combine videos
-   `list.py` - uses google api to download files from drives
-   `stats.py` - generate site statistics from Apache log files

## Notes and TODO

All the magic happens in `assets/js/loader.js` and it's well-commented. Current setup will not work with more than 1 level of sub-directory since it breaks all the links in header & footer files and possibly try to load video and transcript files from unexpected places
