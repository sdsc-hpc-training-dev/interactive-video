# Interactive Video Refactored Template

Refactored old interactive video project into a modular & easy to use template

## Directories and Files

-   `assets`: assets used by _this_ project (not to be confused with `sdsc` which includes sdsc header & footer templates)
-   `php`: legacy php used to keep track of user events
-   `sdsc`: header & footer files
-   `template`: template files
-   `.gitignore`: configured to ignore everything else so we can create other folders and put stuff in them without worrying about changes to the repo
-   `.prettierrc`: good format tool rc file for my VSCode extension

## How to Use

1. Make a new directory and copy the files (`index.html` and `config.json`) from `template` folder to it
2. Modify `config.json` and test the site
3. Done! (no need to modify `index.html`)

## Config Format

Here's annotated `config.json` in `template` directory:

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

## Notes and TODO

All the magic happens in `assets/js/loader.js` and it's well-commented. Current setup will not work with more than 1 level of sub-directory since it breaks all the links in header & footer files and possibly try to load video and transcript files from unexpected places
