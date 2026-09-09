(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var drawer = document.querySelector('[data-site-shell-drawer]');
    var menuButton = document.querySelector('[data-site-shell-menu]');
    var languageDetails = document.querySelector('.site-shell-language');

    if (menuButton && drawer) {
      menuButton.addEventListener('click', function () {
        var open = drawer.classList.toggle('open');
        menuButton.setAttribute('aria-expanded', String(open));
      });
      drawer.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
          drawer.classList.remove('open');
          menuButton.setAttribute('aria-expanded', 'false');
        });
      });
    }

    document.addEventListener('click', function (event) {
      if (languageDetails && languageDetails.open && !languageDetails.contains(event.target)) {
        languageDetails.open = false;
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key !== 'Escape') return;
      if (drawer) drawer.classList.remove('open');
      if (menuButton) menuButton.setAttribute('aria-expanded', 'false');
      if (languageDetails) languageDetails.open = false;
    });
  });
})();
