const loadScript = async (id, src) => {
    const res = await fetch(src);
    document.getElementById(id).innerHTML = await res.text();
};

window.onload = () => {
    loadScript('header', '../sdsc/header.html');
    loadScript('footer', '../sdsc/footer.html');
};
