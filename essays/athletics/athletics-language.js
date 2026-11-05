(function () {
  'use strict';
  var accepted = ['en', 'zh', 'zh-hant'];
  var query = new URLSearchParams(location.search).get('lang');
  if (accepted.indexOf(query) !== -1) {
    document.documentElement.dataset.lang = query;
    document.documentElement.lang = query === 'zh' ? 'zh-Hans' : (query === 'zh-hant' ? 'zh-Hant' : 'en');
    localStorage.setItem('nd_lang', query);
    localStorage.setItem('nondubito-lang', query);
  }
  document.addEventListener('change', function (event) {
    if (!event.target.matches('.lang-toggle .lang-select')) return;
    var option = event.target.selectedOptions[0];
    var language = option && option.dataset.inlineLanguage;
    if (accepted.indexOf(language) === -1) return;
    localStorage.setItem('nondubito-lang', language);
    var url = new URL(location.href);
    url.searchParams.set('lang', language);
    history.replaceState(null, '', url);
  });
})();
