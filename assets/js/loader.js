(async () => {
    const dirs = window.location.href.split('/');
    const last = dirs[dirs.length - 1];

    // Find the right directory to load config.json
    if (!last || last.endsWith('html')) {
        dirs.pop();
    }

    const dir = dirs.join('/');
    let config = {};
    try {
        const res = await fetch(`${dir}/config.json`);
        config = await res.json();
    } catch (_) {
        // Failed to load config.json
        document.getElementById('nav-breadcrumbs').innerHTML = `
        <li><a href="https://www.sdsc.edu/">Home</a> &gt;</li>
        <li><a href="https://www.sdsc.edu/education_and_training/index.html">Education &amp; Training</a> &gt; </li>
        <li><a href="../">HPC User Training 2021</a> &gt;</li>
        <li>404</li>`;
        document.title = document.getElementById('title').textContent =
            '404 (config.json not found for this directory)';
        return;
    }

    const title = config.title || 'Undefined Title';
    const subtitle = config.subtitle || 'Undefined Subtitle';
    const description = config.description || 'Undefined Description';

    document.getElementById('nav-breadcrumbs').innerHTML = `
    <li><a href="https://www.sdsc.edu/">Home</a> &gt;</li>
    <li><a href="https://www.sdsc.edu/education_and_training/index.html">Education &amp; Training</a> &gt; </li>
    <li><a href="../">HPC User Training 2021</a> &gt;</li>
    <li>${title}</li>`;

    document.title = document.getElementById('title').textContent = title;
    document.getElementById('subtitle').textContent = subtitle;
    document.getElementById('description').textContent = description;

    const links = Object.entries(config.links || {});
    document.getElementById('links').innerHTML = links
        .map(([text, link]) => `<a href="${link}" target="new">${text}</a>`)
        .join(' | ');

    /** @type {string[][]} */
    const toc = Object.entries(config.toc || {});
    const tocElem = document.getElementById('toc');

    if (!Object.keys(toc).length) {
        tocElem.innerHTML = `<p style="color: #d31820">To Be Added</p>`;
    } else {
        // Parse time string to number in seconds
        toc.map(([text, time]) => {
            const args = time.split(':');
            if (args.length === 1) {
                return [text, time, ~~args[0]];
            } else if (args.length === 2) {
                return [text, time, ~~args[0] * 60 + ~~args[1]];
            } else if (args.length === 3) {
                return [text, time, ~~args[0] * 60 * 60 + ~~args[1] * 60 + ~~args[2]];
            } else {
                return [text, time, NaN];
            }
            // Map items to html elements
        }).forEach(([text, timeText, time]) => {
            if (isNaN(time)) return;
            const a = document.createElement('a');
            a.onclick = () => (videoElem.currentTime = time);
            a.textContent = `${timeText} - ${text}`;
            tocElem.appendChild(a);
            tocElem.appendChild(document.createElement('br'));
        });
    }

    /** @type {TextTrackCue[]} */
    let cues = [];

    const enterCueManually = () => {
        const index = cues.findIndex(c => c.endTime > videoElem.currentTime);
        cues[Math.max(index, 0)].onenter();
    };

    /** @type {HTMLInputElement} */
    const autoScrollInput = document.getElementById('auto-scroll');
    const hasAutoScroll = () => autoScrollInput.checked;
    // Video might be paused, jump to cue manually
    autoScrollInput.onchange = () => {
        if (hasAutoScroll()) enterCueManually();
    };

    const cueList = document.getElementById('transcript');
    /** @type {HTMLVideoElement} */
    const videoElem = document.getElementById('video');

    // Load video into a <source> element
    const sourceElem = document.createElement('source');
    sourceElem.src = config.mp4_path;
    sourceElem.type = 'video/mp4';

    // Load transcript into a <track> element
    const trackElem = document.createElement('track');
    trackElem.default = true;
    trackElem.kind = 'captions';
    trackElem.srclang = 'en';
    trackElem.src = config.vtt_path;
    videoElem.appendChild(sourceElem);
    videoElem.appendChild(trackElem);

    // User disabled caption which means cue.onenter is not called internally,
    // So cue needs to be updated manually
    videoElem.ontimeupdate = () => {
        if (trackElem.track.mode === 'disabled') enterCueManually();
    };

    // Initilize clicable cue items after track is loaded
    trackElem.onload = () => {
        cues.push(...trackElem.track.cues); // Keep track of the cues

        for (const cue of cues) {
            const item = document.createElement('p');
            item.textContent = cue.text.replace(/^.+: /, ''); // Get rid of names
            item.classList.add('cue');
            cueList.appendChild(item);

            // Item clicked, set video time and call onenter on the cue
            item.onclick = () => {
                videoElem.currentTime = cue.startTime;
                cue.onenter();
            };

            cue.onenter = () => {
                // Scroll to this this item
                if (hasAutoScroll())
                    cueList.scrollTo({ top: item.offsetTop - 350, behavior: 'smooth' });

                // Remove any highlighted item's highlight
                document
                    .querySelectorAll('.highlight')
                    .forEach(i => i.classList.remove('highlight'));
                // Add highlight to this element
                item.classList.add('highlight');
            };
        }
    };
})();
