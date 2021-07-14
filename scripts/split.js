const webvtt = require('node-webvtt');
const fs = require('fs');

const input = fs.readFileSync('../recordings/week6.vtt', 'utf-8');
const data = webvtt.parse(input);

let offset = -99; // seconds
const oldCount = data.cues.length;
data.cues = data.cues.filter(cue => {
    cue.start += offset;
    cue.end += offset;
    cue.start = Math.max(0, cue.start);
    if (cue.end < 0) return false;
    return true;
});

const delta = data.cues.length - oldCount;
console.log(`Delta = ${delta}`);
data.cues.forEach(cue => (cue.identifier = (~~cue.identifier + delta).toString()));
console.log(data.cues.slice(0, 5));

const output = webvtt.compile(data);
fs.writeFileSync('../recordings/web6_out.vtt', output);
