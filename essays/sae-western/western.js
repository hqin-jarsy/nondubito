(function () {
  'use strict';
  var allowed = ['en', 'zh', 'zh-hant'];
  var labels = {en: 'EN', zh: '中文', 'zh-hant': '繁體'};
  var language = new URLSearchParams(location.search).get('lang');
  if (allowed.indexOf(language) === -1) {
    try { language = localStorage.getItem('nd_lang') || localStorage.getItem('nondubito-lang'); } catch (_) {}
  }
  if (allowed.indexOf(language) === -1) language = 'en';

  function apply(next) {
    if (allowed.indexOf(next) === -1) return;
    language = next;
    document.documentElement.dataset.lang = next;
    document.documentElement.lang = {en: 'en', zh: 'zh-Hans', 'zh-hant': 'zh-Hant'}[next];
    try {
      localStorage.setItem('nd_lang', next);
      localStorage.setItem('nondubito-lang', next);
    } catch (_) {}
  }
  apply(language);

  document.addEventListener('DOMContentLoaded', function () {
    var menu = document.querySelector('[data-site-shell-menu]');
    var drawer = document.querySelector('[data-site-shell-drawer]');
    var languageMenu = document.querySelector('.site-shell-language');
    function update(next) {
      apply(next);
      document.querySelectorAll('[data-current-language]').forEach(function (el) { el.textContent = labels[language]; });
      document.querySelectorAll('[data-set-language]').forEach(function (el) { el.setAttribute('aria-pressed', String(el.dataset.setLanguage === language)); });
      var title = document.querySelector('main h1.lang-' + (language === 'zh-hant' ? 'hant' : language));
      if (title) document.title = title.textContent.trim() + ' — Non Dubito';
      if (menu) menu.setAttribute('aria-label', {en: 'Menu', zh: '菜单', 'zh-hant': '選單'}[language]);
      var url = new URL(location.href);
      if (url.searchParams.has('lang')) {
        url.searchParams.set('lang', language);
        try { history.replaceState(history.state, '', url); } catch (_) {}
      }
      // Keep the chosen language even when browser storage is unavailable.
      document.querySelectorAll('main a[href]').forEach(function (link) {
        var target = new URL(link.getAttribute('href'), location.href);
        if (target.origin === location.origin && /\/essays\/(sae-western|sae-montaigne)\//.test(target.pathname)) {
          target.searchParams.set('lang', language);
          link.href = target.href;
        }
      });
    }
    document.querySelectorAll('[data-set-language]').forEach(function (el) {
      el.addEventListener('click', function () {
        update(el.dataset.setLanguage);
        if (languageMenu) languageMenu.open = false;
        if (drawer) drawer.classList.remove('open');
        if (menu) menu.setAttribute('aria-expanded', 'false');
      });
    });
    if (menu && drawer) {
      menu.addEventListener('click', function () { menu.setAttribute('aria-expanded', String(drawer.classList.toggle('open'))); });
      drawer.querySelectorAll('a').forEach(function (link) { link.addEventListener('click', function () { drawer.classList.remove('open'); menu.setAttribute('aria-expanded', 'false'); }); });
    }
    document.addEventListener('click', function (event) { if (languageMenu && !languageMenu.contains(event.target)) languageMenu.open = false; });
    document.addEventListener('keydown', function (event) {
      if (event.key !== 'Escape') return;
      if (languageMenu) languageMenu.open = false;
      if (drawer) drawer.classList.remove('open');
      if (menu) menu.setAttribute('aria-expanded', 'false');
    });
    update(language);
  });
})();
