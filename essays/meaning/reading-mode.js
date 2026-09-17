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
      button.setAttribute(button.tagName === 'A' ? 'aria-current' : 'aria-pressed', String(active));
    });
    // Keep the reading mode in ordinary navigation, including when storage is
    // blocked. Only these nine same-directory pages share inline editions.
    var directory = window.location.pathname.replace(/[^/]*$/, '');
    document.querySelectorAll('a[href]:not(.lang-btn)').forEach(function (link) {
      var target = new URL(link.getAttribute('href'), window.location.href);
      if (target.origin !== window.location.origin || target.pathname.replace(/[^/]*$/, '') !== directory) return;
      var name = target.pathname.split('/').pop();
      if (!/^(index|ep0[1-8])\.html$/.test(name)) return;
      target.searchParams.set('lang', language);
      link.setAttribute('href', name + target.search + target.hash);
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
      button.addEventListener('click', function (event) {
        event.preventDefault();
        mode = button.getAttribute('data-lang');
        setMode(mode);
        var url = new URL(window.location.href);
        url.searchParams.set('lang', mode);
        try { window.history.replaceState(null, '', url); } catch (_) { /* File previews may restrict history. */ }
      });
    });
  });
})();
