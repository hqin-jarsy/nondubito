/* KOE is English-only; retain the visitor's site-wide language preference. */
(function () {
  'use strict';
  var button = document.querySelector('[data-site-shell-menu]');
  var drawer = document.querySelector('[data-site-shell-drawer]');
  if (!button || !drawer) return;
  function closeMenu() {
    drawer.classList.remove('open');
    button.setAttribute('aria-expanded', 'false');
  }
  button.addEventListener('click', function () {
    var open = drawer.classList.toggle('open');
    button.setAttribute('aria-expanded', String(open));
  });
  drawer.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', closeMenu);
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') closeMenu();
  });
})();
