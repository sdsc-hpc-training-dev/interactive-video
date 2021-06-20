const loadScript = async (id, src) => {
    const res = await fetch(src);
    document.getElementById(id).innerHTML = await res.text();
};

window.onload = () => {
    const root = document.getElementById('web-root').textContent;
    loadScript('header', `${root}/sdsc/header.html`);
    loadScript('footer', `${root}/sdsc/footer.html`);
};
