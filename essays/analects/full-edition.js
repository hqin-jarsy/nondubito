// Keep a deliberate primary-language switch stable across reloads and links
// arriving from a fixed-language edition. The shared shell owns rendering.
(function () {
  'use strict';
  document.addEventListener('nondubito:languagechange', function (event) {
    var language = event.detail && event.detail.language;
    if (['en', 'zh', 'zh-hant'].indexOf(language) === -1) return;
    var url = new URL(window.location.href);
    url.searchParams.set('lang', language);
    window.history.replaceState(window.history.state, '', url.href);
  });
})();
