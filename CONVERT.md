
# Converting Interactive Videos to New Format (YouTube)
This file includes steps on how to transition videos from different formats to the new format.
## Formats
- **Old Format** - This uses PHP and a separate file structure from the others.
-  **Current Format** - This one is using locally hosted content. This includes the `mp4` file and the `vtt` file.
- **New Format** - This one utilizes YouTube. Has the same file structure as `Current Format`.
## Current Format (local) to New Format (YouTube)
1.  Download the `mp4` file from Newton. You can do this using a feature rich client like MobaXterm or you can use the command line. An example of how to use the command line is below. Keep in mind that you will be doing this in your local terminal and *you will not* SSH into Newton.
```bash
# Format
scp <user>@newton.sdsc.edu:<filepath/to/mp4> <local/filepath>

# Example of downloading an mp4 to intvids directory on my local machine
scp \
jolo@newton.sdsc.edu:/misc/www/projects/education/training/interactive/202301_parallel_computing_concepts/'2023-01 Parallel Computer Concepts -Bob Sinkovits.mp4' \
~/intvids
```
2. Go to YouTube and upload the video. Ideally this should be under the [SDSC YouTube Channel](https://www.youtube.com/@SanDiegoSupercomputerCenter). Instructions on how to do so can be found [here](https://support.google.com/youtube/answer/57407?hl=en&co=GENIE.Platform%3DDesktop). Once the video is uploaded, get the video ID from the URL.
```
# Sample of a video URL inside a playlist
https://www.youtube.com/watch?v=qj7wG4ukzgs&list=PLyckeMIsNe-_bE8I5eay961dfGBsBwcBy&index=5

# Video ID is after the "v" parameter and before the "&" parameter.
qj7wG4ukzgs
```
3. SSH into Newton and go to the interactive videos directory. Activate your python virtual environment while you are at it. 
```bash
# Format
ssh <user>@newton.sdsc.edu
source filepath/yourpythonenv/bin/activate
cd /misc/www/projects/education/training/interactive

# Example
ssh jolo@newton.sdsc.edu
source myenv/bin/activate
cd /misc/www/projects/education/training/interactive
```
4. Use the `iv.py` python script to create the YouTube directory format.
```bash
# Format
python3 iv.py --youtube <targetdirectory> --video-id <youtubevideoid>

# Example
python3 iv.py --youtube 202301_youtube --video-id qj7wG4ukzgs
```
5. Like `Current Format`, you will need to edit a `config.json` to edit how the page is rendered. Under links, if you have a key with the name of "SDSC" or "GitHub", it will render an image badge. Otherwise, it will just render the key name.


# Converting `IntVid1` to `IntVid2`
This README will explain how to convert from `IntVid1` format to the current `IntVid2` format. The conversion process requires a Python 3.8 environment.

1. Activate your python virtual environment
```bash
# Shorthand
. ~/my_env/bin/activate

# Alt Method
source ~/my_env/bin/activate.fish
```
2. Navigate to the interactive videos directory and create a new interactive video folder for the targeted IntVid.
```bash
cd /misc/www/projects/education/training/interactive
python3 iv.py --webinar 201904_target_intvid
```
3. Navigate to the old format directory and look for the `.mp4` file and the `.vtt` file. If you have `tree` then this task should be pretty easy. Otherwise, just index via `ls`.
**Note: the `.mp4` and `.vtt`* file are usually under an `assets/` directory.
**Note: If you find other assets like slides or pdfs, also take note of those locations.*
```bash
# With tree
cd filepath/to/intvid/dir
tree .

# Using ls
ls .
ls dir/
```
4. Move the `.mp4` and `.vtt` to the target directory.
**Note: Also move any other files you have found.*
```bash
# Core video files
mv sample_vid.mp4 /misc/www/projects/education/training/interactive/201904_target_intvid/sample_vid.mp4 
mv sample_vid.vtt /misc/www/projects/education/training/interactive/201904_target_intvid/sample_vid.vtt

# If you have other files
mv sample_slides.pdf /misc/www/projects/education/training/interactive/201904_target_intvid/sample_slides.pdf
```
6. Fill out the `config.json` inside the target directory to include those new files
```json
{
    "title": "Target Int Vid",
    "subtitle": "Presented on March xth, 2019 by Person Y, SDSC",
    "description": "lorem ipsum",
    "toc": {
        "Overview": "3:17",
        "File Systems": "10:37"
    },
    "links": {
        "Slides": "sample_slides.pdf"
    },
    "mp4_path": "sample_vid.mp4",
    "vtt_path": "sample_vid.vtt",
    "date": "3/x/2019",
    "flag": true
}
```

## Old Format (PHP) to New Format (YouTube)
**TBD**
