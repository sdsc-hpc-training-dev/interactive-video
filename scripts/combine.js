/*
FFMPEG commands for combining 2 videos (SAME CODEC):

$ cat mylist.txt
file '/path/to/file1'
file '/path/to/file2'
file '/path/to/file3'
    
$ ffmpeg -f concat -safe 0 -i mylist.txt -c copy output.mp4
*/

const webvtt = require('node-webvtt');
const fs = require('fs');

const duration1 = 1432.416;

const input1 = fs.readFileSync('../recordings/day3-1.vtt', 'utf-8');
const data1 = webvtt.parse(input1);

const input2 = fs.readFileSync('../recordings/day3-2.vtt', 'utf-8');
const data2 = webvtt.parse(input2);

data2.cues.forEach(cue => ((cue.start += duration1), (cue.end += duration1)));
data1.cues = data1.cues.concat(data2.cues);
data1.cues.forEach((cue, i) => (cue.identifier = i.toString()));

const output = webvtt.compile(data1);
fs.writeFileSync('../recordings/day3.vtt', output);
