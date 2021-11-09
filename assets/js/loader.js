(async () => {
    const dirs = window.location.href.split('/');
    const last = dirs[dirs.length - 1];

    // Find the right directory to load config.json
    if (!last || last.endsWith('html')) {
        dirs.pop();
    }

    let page = {};

    try {
        const res = await fetch(`${dirs.slice(0, -1).join('/')}/page.json`);
        page = await res.json();
    } catch (_) {
        document.title = document.getElementById('title').textContent =
            '404 (page.json not found for parent directory)';
        return;
    }

    let config = {};
    try {
        const res = await fetch(`${dirs.join('/')}/config.json`);
        config = await res.json();
    } catch (_) {
        // Failed to load config.json
        document.getElementById('nav-breadcrumbs').innerHTML = `
        <li><a href="https://www.sdsc.edu/">Home</a> &gt;</li>
        <li><a href="https://www.sdsc.edu/education_and_training/index.html">Education &amp; Training</a> &gt; </li>
        <li><a href="https://education.sdsc.edu/training/interactive/">Interactive Videos</a> &gt; </li>
        <li><a href="../">${page.title || 'Page Title'}</a> &gt;</li>
        <li>404</li>`;
        document.title = document.getElementById('title').textContent =
            '404 (config.json not found for this directory)';
        return;
    }

    const title = config.title || 'Undefined Title';
    const subtitle = config.subtitle || 'Undefined Subtitle';
    const description = config.description;

    document.getElementById('nav-breadcrumbs').innerHTML = `
    <li><a href="https://www.sdsc.edu/">Home</a> &gt;</li>
    <li><a href="https://www.sdsc.edu/education_and_training/index.html">Education &amp; Training</a> &gt; </li>
    <li><a href="https://education.sdsc.edu/training/interactive/">Interactive Videos</a> &gt; </li>
    <li><a href="../">${page.title || 'Page Title'}</a> &gt;</li>
    <li>${title}</li>`;

    document.title = document.getElementById('title').textContent = title;
    document.getElementById('subtitle').textContent = subtitle;
    if (description) document.getElementById('description').textContent = description;
    else document.getElementById('description').remove();

    const links = Object.entries(config.links || {});
    document.getElementById('links').innerHTML = links
        .map(([text, link]) => `<a href="${link}" target="new">${text}</a>`)
        .join(' | ');

    config.toc = config.toc || {};
    const tocElem = document.getElementById('toc');

    /** @type {TextTrackCue[]} */
    let cues = [];
    let fuse;

    const enterCueManually = () => {
        const past = cues.filter(c => videoElem.currentTime >= c.startTime);
        const cue = past[past.length - 1] || cues[0];
        cue && cue.onenter();
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

    document.getElementById('playback-speed').addEventListener('change', function () {
        videoElem.playbackRate = parseFloat(this.value);
    });

    const setSource = (toc, mp4, vtt) => {
        if (!Array.isArray(toc)) {
            tocElem.innerHTML = `<p style="color: #d31820">To Be Added</p>`;
        } else {
            tocElem.innerHTML = '';
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

        // Load video into a <source> element
        const sourceElem = document.createElement('source');
        sourceElem.type = 'video/mp4';

        // Load transcript into a <track> element
        const trackElem = document.createElement('track');
        trackElem.default = true;
        trackElem.kind = 'captions';
        trackElem.srclang = 'en';

        // Initilize clicable cue items after track is loaded
        trackElem.onload = () => {
            cues = [];
            cues.push(...trackElem.track.cues); // Keep track of the cues

            // Search library initialization
            fuse = new Fuse(
                cues.map(c => c.text),
                { includeScore: true },
            );

            cueList.innerHTML = '';
            for (const cue of cues) {
                const item = document.createElement('p');
                item.textContent = cue.text.replace(/^.+: /, '').replace(/^\<v \w+\>/, "").replace(/\<\/\>$/, ""); // Get rid of names
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
                        cueList.scrollTo({
                            top: item.offsetTop - 500,
                            behavior: 'smooth',
                        });

                    // Remove any highlighted item's highlight
                    document
                        .querySelectorAll('.highlight')
                        .forEach(i => i.classList.remove('highlight'));
                    // Add highlight to this element
                    item.classList.add('highlight');
                };
            }

            trackElem.track.mode = 'disabled'; // Disable by default
        };

        videoElem.innerHTML = '';
        videoElem.appendChild(sourceElem);
        videoElem.appendChild(trackElem);
        videoElem.load();

        // User disabled caption which means cue.onenter is not called internally,
        // So cue needs to be updated manually
        videoElem.ontimeupdate = () => {
            if (trackElem.track.mode === 'disabled') enterCueManually();
        };

        sourceElem.src = mp4;
        trackElem.src = vtt;
    };

    document.addEventListener('keydown', e => {
        const k = e.code;
        if (k === 'ArrowLeft') {
            videoElem.currentTime -= 10;
            if (videoElem.currentTime <= 0) {
                videoElem.pause();
                videoElem.currentTime = 0;
            }
            e.preventDefault();
        } else if (k === 'ArrowRight') {
            videoElem.currentTime += 10;
            if (videoElem.currentTime >= videoElem.duration) {
                videoElem.pause();
                videoElem.currentTime = videoElem.duration;
            }
            e.preventDefault();
        } else if (k === 'Space') {
            if (videoElem.paused || videoElem.ended) {
                videoElem.play();
            } else {
                videoElem.pause();
            }
            e.preventDefault();
        }
    });

    /** @type {HTMLInputElement} */
    const searchInput = document.getElementById('transcript-search');
    const result = document.getElementById('search-result');
    const count = document.getElementById('result-count');
    searchInput.onchange = () => {
        const value = searchInput.value.trim();
        if (!fuse) {
            result.innerHTML = 'Transcript not loaded';
            count.innerText = '';
        } else if (value.length < 3) {
            result.innerHTML = 'Search term is too short!';
            count.innerText = '';
        } else {
            /** @type {{ item: string, refIndex: number, score: number  }[]} */
            const arr = fuse.search(value);
            result.innerHTML = '';
            count.innerText = `${arr.length} result${arr.length > 1 ? 's' : ''} ${
                arr.length > 100 ? ` (showing 100 out of ${arr.length})` : ''
            }`;
            for (const match of arr.slice(0, 100)) {
                const p = document.createElement('p');
                p.className = 'result';
                p.onclick = () => {
                    videoElem.currentTime = cues[match.refIndex].startTime;
                    cues[match.refIndex].onenter();
                };
                const seconds = ~~cues[match.refIndex].startTime;
                const str = new Date(seconds * 1000).toISOString().substr(11, 8);
                p.innerText = `${str} ...${match.item.replace(/^.+: /, '')}...`;
                result.appendChild(p);
            }
        }
    };

    if (
        Array.isArray(config.toc) &&
        Array.isArray(config.mp4_path) &&
        Array.isArray(config.vtt_path)
    ) {
        // Multiple parts
        const len = Math.min(config.mp4_path.length, config.vtt_path.length);
        const container = document.createElement('div');
        container.style.display = 'flex';
        container.style.justifyContent = 'center';
        videoElem.parentElement.prepend(container);

        let currPart = 0;

        const update = () => {
            setSource(
                Object.entries(config.toc[currPart] || {}),
                config.mp4_path[currPart],
                config.vtt_path[currPart],
            );
        };

        const buttons = [];
        for (let i = 0; i < len; i++) {
            const button = document.createElement('button');
            button.classList.add('part');
            button.innerText = `Section ${i + 1}`;
            container.appendChild(button);
            button.onclick = () => {
                if (currPart != i) {
                    currPart = i;
                    update();

                    for (const b of buttons) b.style.backgroundColor = '#888';
                    button.style.backgroundColor = '#d31820';
                }
            };
            if (!i) button.style.backgroundColor = '#d31820';
            buttons.push(button);
        }

        update();
    } else {
        const toc = Array.isArray(config.toc) ? config.toc[0] : config.toc;
        const mp4_path = Array.isArray(config.mp4_path)
            ? config.mp4_path[0]
            : config.mp4_path;
        const vtt_path = Array.isArray(config.vtt_path)
            ? config.vtt_path[0]
            : config.vtt_path;
        setSource(Object.entries(toc), mp4_path, vtt_path);
    }
})();
