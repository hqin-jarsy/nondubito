/* Edition links are ordinary anchors. Explicit URLs work without JavaScript. */
(() => {
  const menu = document.querySelector('.language-menu');
  if (!menu) return;
  document.addEventListener('click', event => { if (!menu.contains(event.target)) menu.open = false; });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.open) { menu.open = false; menu.querySelector('summary').focus(); }
  });
  function revealAnchor() {
    let target;
    try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (_) { return; }
    if (!target) return;
    let parent = target;
    while (parent) { if (parent.tagName === 'DETAILS') parent.open = true; parent = parent.parentElement; }
  }
  revealAnchor(); window.addEventListener('hashchange', revealAnchor);
})();
