(function () {
  'use strict';

  function syncReadingLanguage() {
    var language = document.documentElement.dataset.lang;
    var css = { en: 'en', zh: 'zh', 'zh-hant': 'hant' }[language];
    if (!css) return;
    var heading = document.querySelector('main h1.lang-' + css);
    if (heading) document.title = heading.textContent.trim() + ' — Non Dubito';

    // A search-result language must not override the reader's subsequent choice on reload.
    var url = new URL(window.location.href);
    if (url.searchParams.has('lang') && url.searchParams.get('lang') !== language) {
      url.searchParams.set('lang', language);
      window.history.replaceState(window.history.state, '', url);
    }
    var menu = document.querySelector('[data-site-shell-menu]');
    if (menu) menu.setAttribute('aria-label', { en: 'Menu', zh: '菜单', 'zh-hant': '選單' }[language]);
    document.querySelectorAll('[data-set-language]').forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.setLanguage === language));
    });
  }

  document.addEventListener('DOMContentLoaded', syncReadingLanguage);
  document.addEventListener('nondubito:languagechange', syncReadingLanguage);
})();
