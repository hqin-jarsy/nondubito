/* Real edition URLs and native details work without JavaScript. */
(function () {
  'use strict';
  var current = document.documentElement.dataset.lang;
  var requested = new URLSearchParams(location.search).get('lang');
  var saved;
  try { saved = localStorage.getItem('nd_lang'); } catch (_) {}
  var desired = requested || (current === 'zh' ? saved : current);
  var alternate = Array.from(document.querySelectorAll('[data-edition]')).find(function (a) { return a.dataset.edition === desired; });
  if (alternate && desired !== current) {
    var url = new URL(alternate.href); url.hash = location.hash; location.replace(url.href); return;
  }
  function remember(lang) {
    try { localStorage.setItem('nd_lang', lang); localStorage.setItem('nondubito-lang', lang); } catch (_) {}
  }
  remember(current);
  document.querySelectorAll('[data-edition]').forEach(function (a) {
    a.addEventListener('click', function () { remember(a.dataset.edition); if (location.hash) a.hash = location.hash; });
  });
  document.querySelectorAll('[data-legacy-language]').forEach(function (a) {
    ['click', 'auxclick'].forEach(function (event) { a.addEventListener(event, function () { remember(a.dataset.legacyLanguage); }); });
  });
}());
