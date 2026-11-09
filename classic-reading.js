/* Shared by reviewed classic editions. Query choice wins over saved preference. */
(function () {
  'use strict';
  var valid = ['zh', 'zh-hant', 'en'];
  function readPreference() {
    try { return localStorage.getItem('nd_lang') || localStorage.getItem('nondubito-lang'); }
    catch (error) { return null; }
  }
  function savePreference(language) {
    try {
      localStorage.setItem('nd_lang', language);
      localStorage.setItem('nondubito-lang', language);
    } catch (error) {}
  }
  var requested = new URLSearchParams(location.search).get('lang');
  var language = valid.indexOf(requested) >= 0 ? requested : readPreference();
  if (valid.indexOf(language) < 0) language = 'zh';
  function select(value, updateURL) {
    if (valid.indexOf(value) < 0) return;
    document.documentElement.setAttribute('data-lang', value);
    document.documentElement.lang = value === 'zh' ? 'zh-Hans' : value === 'zh-hant' ? 'zh-Hant' : 'en';
    savePreference(value);
    if (updateURL) {
      var url = new URL(location.href);
      url.searchParams.set('lang', value);
      history.replaceState(null, '', url);
    }
    document.querySelectorAll('.lang-btn[data-lang]').forEach(function (button) {
      var active = button.getAttribute('data-lang') === value;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
  }
  select(language, false);
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.lang-btn[data-lang]').forEach(function (button) {
      button.addEventListener('click', function () { select(button.getAttribute('data-lang'), true); });
    });
    select(document.documentElement.getAttribute('data-lang'), false);
  });
})();
