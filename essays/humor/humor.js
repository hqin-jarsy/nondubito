/* The text, navigation and source disclosures work without JavaScript. */
(function () {
  'use strict';
  var current = document.documentElement.dataset.lang;
  var requested = new URLSearchParams(location.search).get('lang');
  var saved;
  try { saved = localStorage.getItem('nd_lang'); } catch (_) { /* Optional preference. */ }
  if (current === 'zh' && (requested === 'zh-hant' || requested === 'zh-Hant' || (!requested && saved === 'zh-hant'))) {
    var alternate = document.querySelector('[data-humor-language="zh-hant"]');
    if (alternate) { location.replace(alternate.href + location.hash); return; }
  }
  try { localStorage.setItem('nd_lang', current); localStorage.setItem('nondubito-lang', current); } catch (_) {}
  document.querySelectorAll('[data-humor-language]').forEach(function (link) {
    link.addEventListener('click', function () {
      try { localStorage.setItem('nd_lang', link.dataset.humorLanguage); localStorage.setItem('nondubito-lang', link.dataset.humorLanguage); } catch (_) {}
      if (location.hash) link.hash = location.hash;
    });
  });
}());
