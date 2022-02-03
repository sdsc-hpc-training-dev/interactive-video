const loadScript = async (id, src) => {
  const res = await fetch(src);
  document.getElementById(id).innerHTML = await res.text();
};

window.onload = () => {
  loadScript("header", `/training/interactive/assets/header.html`);
  loadScript("footer", `/training/interactive/assets/footer.html`);
};
