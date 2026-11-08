/* Scoped eight-language shell; other collections keep their existing shell. */
(function () {
  'use strict';
  var labels = {en: 'EN', zh: '中文', 'zh-hant': '繁體', de: 'DE', fr: 'FR', es: 'ES', ja: '日本語', ko: '한국어'};
  var menuLabels = {en: 'Menu', zh: '菜单', 'zh-hant': '選單', de: 'Menü', fr: 'Menu', es: 'Menú', ja: 'メニュー', ko: '메뉴'};
  var searchLabels = {en: 'Search', zh: '搜索', 'zh-hant': '搜尋', de: 'Suchen', fr: 'Rechercher', es: 'Buscar', ja: '検索', ko: '검색'};
  function stored() {try {return localStorage.getItem('nd_lang');} catch (_) {return null;}}
  function save(lang) {try {localStorage.setItem('nd_lang', lang);localStorage.setItem('nondubito-lang', lang);} catch (_) {}}
  function native(lang) {return lang === 'zh' ? 'zh-Hans' : lang === 'zh-hant' ? 'zh-Hant' : lang;}
  function requested() {
    var query = new URLSearchParams(location.search).get('lang');
    return Object.prototype.hasOwnProperty.call(labels, query) ? query : Object.prototype.hasOwnProperty.call(labels, stored()) ? stored() : 'en';
  }
  function apply(lang, notify) {
    if (!Object.prototype.hasOwnProperty.call(labels, lang)) lang = 'en';
    document.documentElement.dataset.lang = lang;
    document.documentElement.lang = native(lang);
    save(lang);
    var heading = document.querySelector('main h1.lang-' + (lang === 'zh-hant' ? 'hant' : lang));
    if (heading) document.title = heading.textContent.trim() + ' — Non Dubito';
    document.querySelectorAll('[data-current-language]').forEach(function (node) {node.textContent = labels[lang];});
    document.querySelectorAll('[data-set-language]').forEach(function (button) {button.setAttribute('aria-pressed', String(button.dataset.setLanguage === lang));});
    var menu = document.querySelector('[data-site-shell-menu]');
    if (menu) menu.setAttribute('aria-label', menuLabels[lang]);
    var search = document.querySelector('.site-shell-tool');
    if (search) {
      search.setAttribute('aria-label', searchLabels[lang]);
      var searchUrl = new URL(search.href, location.href);
      var sharedLanguage = ['en', 'zh', 'zh-hant'].indexOf(lang) >= 0;
      searchUrl.searchParams.set('lang', sharedLanguage ? lang : 'en');
      searchUrl.searchParams.set('in', native(lang));
      if (sharedLanguage) searchUrl.searchParams.delete('ui');
      else searchUrl.searchParams.set('ui', lang);
      search.href = searchUrl.href;
    }
    // Preserve the selected edition in a copied link and on back/reload.
    if (notify) {
      var url = new URL(location.href);url.searchParams.set('lang', lang);
      history.replaceState(history.state, '', url);
    }
    // Explicit query language survives links even when browser storage is disabled.
    document.querySelectorAll('a[href]').forEach(function (link) {
      var url = new URL(link.href, location.href);
      if (url.origin === location.origin && url.pathname.startsWith('/essays/everyday/stories/drama/')) {
        url.searchParams.set('lang', lang);link.href = url.href;
      }
    });
  }
  apply(requested(), false);
  document.addEventListener('DOMContentLoaded', function () {
    var drawer = document.querySelector('[data-site-shell-drawer]');
    var menu = document.querySelector('[data-site-shell-menu]');
    var details = document.querySelector('.site-shell-language');
    function closeDrawer() {if(drawer)drawer.classList.remove('open');if(menu)menu.setAttribute('aria-expanded','false');}
    function closeAll() {closeDrawer();if(details)details.open=false;}
    document.querySelectorAll('[data-set-language]').forEach(function (button) {
      button.addEventListener('click', function () {apply(button.dataset.setLanguage, true);closeAll();document.dispatchEvent(new CustomEvent('nondubito:languagechange',{detail:{language:button.dataset.setLanguage}}));});
    });
    if (menu && drawer) menu.addEventListener('click',function(){var open=drawer.classList.toggle('open');menu.setAttribute('aria-expanded',String(open));});
    if (drawer) drawer.querySelectorAll('a').forEach(function (link) {link.addEventListener('click', closeDrawer);});
    document.addEventListener('click', function (event) {if(details && details.open && !details.contains(event.target))details.open=false;});
    document.addEventListener('keydown', function (event) {if(event.key==='Escape')closeAll();});
    window.addEventListener('popstate',function(){apply(requested(),false);closeAll();});
    apply(requested(), false);
  });
})();
