const loadScript = async (id, src, root) => {
    const res = await fetch(src);
    document.getElementById(id).innerHTML = (await res.text()).replace('{ROOT}', root);
};

window.onload = () => {
    const root = document.getElementById('web-root').textContent;
    loadScript('header', `${root}/sdsc/header.html`, root);
    loadScript('footer', `${root}/sdsc/footer.html`, root);
};
