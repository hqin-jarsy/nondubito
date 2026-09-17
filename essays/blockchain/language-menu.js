/* Enhance real links without relying on the inline-language switching system. */
(function () {
  'use strict';

  function enhanceLanguageMenus() {
    document.querySelectorAll('.blockchain-language-menu').forEach(function (menu) {
      if (menu.querySelector('select')) return;
      var links = Array.from(menu.querySelectorAll('a[data-language]'));
      if (!links.length) return;

      var select = document.createElement('select');
      select.setAttribute('aria-label', menu.getAttribute('aria-label') || 'Language');
      links.forEach(function (link) {
        var option = document.createElement('option');
        option.value = link.getAttribute('data-language');
        option.textContent = link.textContent.trim();
        option.selected = link.getAttribute('aria-current') === 'page';
        select.appendChild(option);
      });
      select.addEventListener('change', function () {
        var destination = links.find(function (link) {
          return link.getAttribute('data-language') === select.value;
        });
        if (destination) window.location.assign(destination.href);
      });
      menu.appendChild(select);
      links.forEach(function (link) { link.hidden = true; });
      menu.classList.add('is-enhanced');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceLanguageMenus);
  } else {
    enhanceLanguageMenus();
  }
}());
