(async () => {
    const res = await fetch('./list.php');
    const json = await res.json();

    document.title =
        document.getElementById('title').textContent =
        document.getElementById('nav').textContent =
            json.title;

    document.getElementById('list').innerHTML = json.list
        .sort((p1, p2) => p1.time - p2.time)
        .map(
            post => `
        <div>
            <h2><a href="./${post.path}">${post.title}</a></h2>
            <p><em>${post.subtitle}</em></p>
            <p>${post.description}</p>
        </div>`,
        )
        .join('<hr>');
})();
