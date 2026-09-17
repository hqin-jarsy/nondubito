/* Progressive enhancement: foreign-edition links remain usable without JS.
 * English/Chinese inline modes use the existing reading-mode script. */
(function () {
  'use strict';
  function enhance() {
    document.querySelectorAll('.meaning-languages').forEach(function (group) {
      var links = Array.from(group.querySelectorAll('a[data-edition]'));
      if (!links.length || group.querySelector('select')) return;
      var select = document.createElement('select');
      select.className = 'lang-select';
      select.setAttribute('aria-label', group.getAttribute('aria-label'));
      links.forEach(function (link) {
        var option = document.createElement('option');
        option.value = link.dataset.edition;
        option.textContent = link.textContent;
        select.appendChild(option);
      });
      function sync() { select.value = document.documentElement.getAttribute('data-lang'); }
      select.addEventListener('change', function () {
        var link = links.find(function (item) { return item.dataset.edition === select.value; });
        // Existing same-page handler owns URL, script conversion and preferences.
        if (link.hasAttribute('data-lang')) link.click();
        else window.location.assign(link.href);
      });
      links.forEach(function (link) { link.hidden = true; });
      group.classList.add('lang-select-menu');
      group.appendChild(select);
      var arrow = document.createElement('span');
      arrow.className = 'lang-select-chevron';
      arrow.textContent = '▾';
      arrow.setAttribute('aria-hidden', 'true');
      group.appendChild(arrow);
      new MutationObserver(sync).observe(document.documentElement, {attributes: true, attributeFilter: ['data-lang']});
      sync();
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', enhance);
  else enhance();
})();
