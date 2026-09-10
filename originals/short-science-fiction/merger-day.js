(function () {
  'use strict';

  var root = document.documentElement;
  var hasLocalEditions = root.hasAttribute('data-editions');

  function label(language) {
    if (language === 'zh') return '中文';
    if (language === 'zh-hant') return '繁體';
    return 'EN';
  }

  function apply(language) {
    if (!hasLocalEditions) return;
    if (['en', 'zh', 'zh-hant'].indexOf(language) === -1) language = 'zh';
    root.dataset.lang = language;
    root.lang = language === 'zh-hant' ? 'zh-Hant' : (language === 'zh' ? 'zh-Hans' : 'en');
    localStorage.setItem('nd_lang', language);
    localStorage.setItem('nondubito-lang', language);
    document.querySelectorAll('[data-current-language]').forEach(function (node) {
      node.textContent = label(language);
    });
  }

  if (hasLocalEditions) {
    var requested = new URLSearchParams(window.location.search).get('lang');
    apply(requested || localStorage.getItem('nd_lang') || localStorage.getItem('nondubito-lang') || 'zh');
  }

  document.addEventListener('DOMContentLoaded', function () {
    var drawer = document.querySelector('[data-site-shell-drawer]');
    var menuButton = document.querySelector('[data-site-shell-menu]');
    var languageDetails = document.querySelector('.site-shell-language');

    document.querySelectorAll('[data-set-language]').forEach(function (button) {
      button.addEventListener('click', function () {
        apply(button.dataset.setLanguage);
        if (languageDetails) languageDetails.open = false;
      });
    });

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
      if (languageDetails && languageDetails.open && !languageDetails.contains(event.target)) languageDetails.open = false;
    });
    document.addEventListener('keydown', function (event) {
      if (event.key !== 'Escape') return;
      if (drawer) drawer.classList.remove('open');
      if (menuButton) menuButton.setAttribute('aria-expanded', 'false');
      if (languageDetails) languageDetails.open = false;
    });
  });
})();
