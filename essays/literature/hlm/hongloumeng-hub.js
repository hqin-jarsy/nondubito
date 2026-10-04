(() => {
  const current = document.documentElement.dataset.lang;
  const links = [...document.querySelectorAll('[data-edition]')];
  let saved;
  try { saved = localStorage.getItem('nd_lang'); } catch (_) {}
  const requested = new URLSearchParams(location.search).get('lang');
  // Explicit language URLs take precedence over a stored preference.
  const choice = requested || (document.documentElement.dataset.explicitEdition || /\/(en|zh-hant)\/index\.html$|\/(en|zh-hant)\/$/.test(location.pathname) ? current : saved);
  const target = links.find(a => a.dataset.edition === choice);
  if (target && choice !== current) {
    location.replace(target.href + location.hash);
    return;
  }
  links.forEach(a => {
    a.addEventListener('click', () => {
      a.hash = location.hash;
      try { localStorage.setItem('nd_lang', a.dataset.edition); } catch (_) {}
    });
  });
  document.querySelectorAll('[data-legacy-language]').forEach(a => {
    a.addEventListener('click', () => {
      try { localStorage.setItem('nd_lang', a.dataset.legacyLanguage); } catch (_) {}
    });
  });
  function revealAnchor() {
    const node = document.getElementById(location.hash.slice(1));
    if (node && node.matches('details')) {
      node.open = true;
      node.scrollIntoView();
    }
  }
  revealAnchor();
  window.addEventListener('hashchange', revealAnchor);
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      const menu = document.querySelector('.language-menu');
      if (menu.open) { menu.open = false; menu.querySelector('summary').focus(); }
    }
  });
})();
