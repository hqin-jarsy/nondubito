(function () {
  'use strict';
  function update() {
    var language = document.documentElement.dataset.lang;
    var heading = document.querySelector('main h1.lang-' + (language === 'zh-hant' ? 'hant' : language));
    if (heading) document.title = heading.textContent.trim() + ' — Non Dubito';
    var url = new URL(window.location.href);
    if (url.searchParams.has('lang') && url.searchParams.get('lang') !== language) {
      url.searchParams.set('lang', language);
      window.history.replaceState(window.history.state, '', url);
    }
    var menu = document.querySelector('[data-site-shell-menu]');
    if (menu) menu.setAttribute('aria-label', {en:'Menu', zh:'菜单', 'zh-hant':'選單'}[language] || 'Menu');
    document.querySelectorAll('[data-set-language]').forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.setLanguage === language));
    });
  }
  document.addEventListener('DOMContentLoaded', update);
  document.addEventListener('nondubito:languagechange', update);
})();
