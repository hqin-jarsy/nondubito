(function () {
  'use strict';

  var queryLanguage = new URLSearchParams(window.location.search).get('lang');
  var savedLanguage = queryLanguage || localStorage.getItem('nd_lang') || 'en';
  if (['en', 'zh', 'zh-hant'].indexOf(savedLanguage) === -1) savedLanguage = 'en';

  function applyLanguage(language) {
    document.documentElement.dataset.lang = language;
    document.documentElement.lang = language === 'zh-hant' ? 'zh-Hant' : (language === 'zh' ? 'zh-Hans' : 'en');
    localStorage.setItem('nd_lang', language);
    localStorage.setItem('nondubito-lang', language);
  }

  applyLanguage(savedLanguage);

  document.addEventListener('DOMContentLoaded', function () {
    var drawer = document.querySelector('[data-site-shell-drawer]');
    var menuButton = document.querySelector('[data-site-shell-menu]');
    var languageDetails = document.querySelector('.site-shell-language');
    var currentLabels = document.querySelectorAll('[data-current-language]');

    function languageLabel(language) {
      if (language === 'zh') return '中文';
      if (language === 'zh-hant') return '繁體';
      return 'EN';
    }

    function updateLanguage(language) {
      applyLanguage(language);
      currentLabels.forEach(function (node) {
        node.textContent = languageLabel(language);
      });
      document.dispatchEvent(new CustomEvent('nondubito:languagechange', {
        detail: { language: language }
      }));
    }

    document.querySelectorAll('[data-set-language]').forEach(function (button) {
      button.addEventListener('click', function () {
        updateLanguage(button.dataset.setLanguage);
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

    updateLanguage(savedLanguage);
  });
})();
