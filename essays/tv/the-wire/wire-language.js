/* Scoped primary-language routing: explicit URL wins, storage is optional. */
(function () {
  'use strict';
  var choices = ['en', 'zh', 'zh-hant'];
  var current = 'zh';
  var url = new URL(location.href);
  var explicit = url.searchParams.get('lang');
  try { current = localStorage.getItem('nd_lang') || localStorage.getItem('nondubito-lang') || current; } catch (_) {}
  if (choices.indexOf(explicit) >= 0) current = explicit;
  if (choices.indexOf(current) < 0) current = 'zh';
  function apply() {
    document.documentElement.dataset.lang = current;
    document.documentElement.lang = current === 'zh-hant' ? 'zh-Hant' : current === 'zh' ? 'zh-Hans' : 'en';
    try { localStorage.setItem('nd_lang', current); localStorage.setItem('nondubito-lang', current); } catch (_) {}
    document.querySelectorAll('.lang-btn[data-lang]').forEach(function (button) {
      var selected = button.dataset.lang === current;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-pressed', String(selected));
    });
    // The frozen Traditional Chinese converter runs on the same attribute change.
    // Update the tab title after its text-node pass, using the visible heading.
    setTimeout(function () {
      var css = current === 'en' ? '.lang-en' : '.lang-zh';
      var heading = document.querySelector('h1' + css);
      var deck = document.querySelector('.essay-page-deck' + css);
      if (heading) document.title = heading.textContent.trim() + (deck ? ': ' + deck.textContent.trim() : '') + ' — Non Dubito';
    }, 0);
    document.querySelectorAll('a[href]').forEach(function (a) {
      var target = new URL(a.getAttribute('href'), location.href);
      if (target.origin === location.origin && target.pathname.slice(0, target.pathname.lastIndexOf('/')) === location.pathname.slice(0, location.pathname.lastIndexOf('/')) && /\.html$/.test(target.pathname)) {
        target.searchParams.set('lang', current);
        a.setAttribute('href', target.pathname.split('/').pop() + target.search + target.hash);
      }
    });
  }
  apply();
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.lang-btn[data-lang]').forEach(function (button) {
      button.addEventListener('click', function () {
        if (choices.indexOf(button.dataset.lang) < 0) return;
        current = button.dataset.lang;
        var next = new URL(location.href); next.searchParams.set('lang', current);
        history.replaceState(history.state, '', next.href); apply();
      });
    });
    apply();
  });
  window.addEventListener('popstate', function () {
    var requested = new URL(location.href).searchParams.get('lang');
    if (choices.indexOf(requested) >= 0) current = requested;
    apply();
  });
})();
