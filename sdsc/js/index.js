const loadScript = async (id, src) => {
    const res = await fetch(src);
    document.getElementById(id).innerHTML = await res.text();
};

window.onload = () => {
    loadScript('header', 'https://www.sdsc.edu/_include/header.html');
    loadScript('footer', 'https://www.sdsc.edu/_include/footer.html');
};
