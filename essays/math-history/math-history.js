(function () {
  'use strict';
  function update() {
    var lang = document.documentElement.dataset.lang;
    var css = lang === 'zh-hant' ? 'hant' : lang;
    var h = document.querySelector('main h1.lang-' + css);
    if (h) document.title = h.textContent.trim() + ' — Non Dubito';
    var url = new URL(location.href);
    if (url.searchParams.has('lang') && url.searchParams.get('lang') !== lang) {
      url.searchParams.set('lang', lang);
      history.replaceState(history.state, '', url);
    }
    // An in-article anchor must target the visible edition after switching.
    var section = location.hash.match(/^#(?:en|zh|hant)-section-(\d+)$/);
    if (section && location.hash !== '#' + css + '-section-' + section[1]) {
      url = new URL(location.href);
      url.hash = css + '-section-' + section[1];
      history.replaceState(history.state, '', url);
      var target = document.getElementById(css + '-section-' + section[1]);
      // Let the edition's display/font layout settle before anchoring it.
      if (target) requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          target.scrollIntoView({behavior:'instant',block:'start'});
        });
      });
    }
    document.querySelectorAll('[data-set-language]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.setLanguage === lang));
    });
    var menu = document.querySelector('[data-site-shell-menu]');
    if (menu) menu.setAttribute('aria-label', {en:'Menu',zh:'菜单','zh-hant':'選單'}[lang] || 'Menu');
    [
      ['.math-breadcrumbs',{en:'Breadcrumb',zh:'当前位置','zh-hant':'目前位置'}],
      ['.math-topics',{en:'Reading routes',zh:'阅读路线','zh-hant':'閱讀路線'}],
      ['.math-series-nav',{en:'Series navigation',zh:'系列导航','zh-hant':'系列導覽'}]
    ].forEach(function (entry) {
      var node = document.querySelector(entry[0]);
      if (node) node.setAttribute('aria-label', entry[1][lang] || entry[1].en);
    });
  }
  document.addEventListener('DOMContentLoaded', update);
  document.addEventListener('nondubito:languagechange', update);
})();
