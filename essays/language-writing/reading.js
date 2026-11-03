(function () {
  'use strict';
  if (document.documentElement.hasAttribute('data-foreign-edition')) {
    // A single-language URL must never be overridden by a saved Chinese/English
    // reading mode. Only the local navigation controls need JavaScript here.
    document.addEventListener('DOMContentLoaded', function () {
      var drawer = document.querySelector('[data-site-shell-drawer]');
      var button = document.querySelector('[data-site-shell-menu]');
      var languages = document.querySelector('.site-shell-language');
      function close() {
        drawer.classList.remove('open');
        button.setAttribute('aria-expanded', 'false');
        languages.open = false;
      }
      button.addEventListener('click', function () {
        var open = drawer.classList.toggle('open');
        button.setAttribute('aria-expanded', String(open));
        if (open) languages.open = false;
      });
      document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') close();
      });
      document.addEventListener('click', function (event) {
        if (!languages.contains(event.target)) languages.open = false;
      });
    });
    return;
  }
  function update() {
    var language = document.documentElement.dataset.lang;
    var css = language === 'zh-hant' ? 'hant' : language;
    var heading = document.querySelector('main h1.lang-' + css);
    if (heading) document.title = heading.textContent.trim() + ' — Non Dubito';
    var url = new URL(window.location.href);
    if (url.searchParams.has('lang') && url.searchParams.get('lang') !== language) {
      url.searchParams.set('lang', language);
      window.history.replaceState(window.history.state, '', url);
    }
    var menu = document.querySelector('[data-site-shell-menu]');
    if (menu) menu.setAttribute('aria-label', { en:'Menu', zh:'菜单', 'zh-hant':'選單' }[language] || 'Menu');
    document.querySelectorAll('[data-set-language]').forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.setLanguage === language));
    });
  }
  document.addEventListener('DOMContentLoaded', update);
  document.addEventListener('nondubito:languagechange', update);
})();
