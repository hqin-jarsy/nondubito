/* Shared by the three same-page editions of SAE Meaning Theory. */
(function () {
  'use strict';
  var supported = ['en', 'zh', 'zh-hant'];
  var mode = new URLSearchParams(window.location.search).get('lang');
  if (supported.indexOf(mode) === -1) {
    try {
      mode = localStorage.getItem('nd_lang') || localStorage.getItem('nondubito-lang');
    } catch (_) { mode = null; }
  }
  if (supported.indexOf(mode) === -1) mode = 'zh';
  function setMode(language) {
    document.documentElement.setAttribute('data-lang', language);
    document.documentElement.lang = {en: 'en', zh: 'zh-Hans', 'zh-hant': 'zh-Hant'}[language];
    document.querySelectorAll('.lang-btn[data-lang]').forEach(function (button) {
      var active = button.getAttribute('data-lang') === language;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    try {
      localStorage.setItem('nd_lang', language);
      localStorage.setItem('nondubito-lang', language);
    } catch (_) { /* Reading remains available when storage is disabled. */ }
  }
  setMode(mode);
  document.addEventListener('DOMContentLoaded', function () {
    setMode(mode);
    document.querySelectorAll('.lang-btn[data-lang]').forEach(function (button) {
      button.addEventListener('click', function () {
        mode = button.getAttribute('data-lang');
        setMode(mode);
        var url = new URL(window.location.href);
        url.searchParams.set('lang', mode);
        try { window.history.replaceState(null, '', url); } catch (_) { /* File previews may restrict history. */ }
      });
    });
  });
})();
