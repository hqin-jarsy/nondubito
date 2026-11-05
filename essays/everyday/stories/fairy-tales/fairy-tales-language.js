(function () {
  "use strict";
  // Deferred before the shared selector; keep the original inline script intact.
  document.querySelectorAll('[data-lang-button]').forEach(function (button) {
    button.dataset.lang = button.dataset.langButton;
  });
  document.addEventListener('change', function (event) {
    var select = event.target;
    if (!select.matches('.lang-select')) return;
    var option = select.options[select.selectedIndex];
    var language = option && option.dataset.inlineLanguage;
    if (!language) return;
    var url = new URL(location.href);
    url.searchParams.set('lang', language);
    history.replaceState(null, '', url);
    localStorage.setItem('nondubito-lang', language);
  });
})();
