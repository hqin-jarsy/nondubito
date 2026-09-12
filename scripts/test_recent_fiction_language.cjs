// Exercise the shelf-local enhancement without changing the shared language controller.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const script = fs.readFileSync(path.join(__dirname, '../essays/recent-fiction/recent-fiction.js'), 'utf8');

function fixture(href, language) {
  const handlers = {};
  const menu = { setAttribute(k, v) { this[k] = v; } };
  const buttons = ['en', 'zh', 'zh-hant'].map(lang => ({
    dataset: { setLanguage: lang }, setAttribute(k, v) { this[k] = v; },
  }));
  const location = { href };
  const titles = { en: 'A new novel', zh: '一本新小说', hant: '一本新小說' };
  let replacements = 0;
  const document = {
    title: 'Original title', documentElement: { dataset: { lang: language } },
    addEventListener(name, handler) { handlers[name] = handler; },
    querySelector(selector) {
      if (selector === '[data-site-shell-menu]') return menu;
      const title = titles[selector.replace('main h1.lang-', '')];
      return title ? { textContent: title } : null;
    },
    querySelectorAll() { return buttons; },
  };
  const history = { state: { preserved: true }, replaceState(state, unused, url) {
    assert.deepEqual(state, { preserved: true }); location.href = String(url); replacements++;
  } };
  vm.runInNewContext(script, { document, window: { location, history }, URL });
  return { document, handlers, menu, buttons, location, replacements: () => replacements };
}

const entered = fixture('https://nondubito.net/essays/recent-fiction/index.html?lang=zh&ref=search#year-2024', 'zh');
entered.handlers.DOMContentLoaded();
assert.equal(entered.document.title, '一本新小说 — Non Dubito');
assert.equal(entered.menu['aria-label'], '菜单');
assert.equal(entered.replacements(), 0);
entered.document.documentElement.dataset.lang = 'en';
entered.handlers['nondubito:languagechange']();
assert.equal(entered.document.title, 'A new novel — Non Dubito');
assert.equal(entered.location.href, 'https://nondubito.net/essays/recent-fiction/index.html?lang=en&ref=search#year-2024');
assert.deepEqual(entered.buttons.map(b => b['aria-pressed']), ['true', 'false', 'false']);
entered.document.documentElement.dataset.lang = 'zh-hant';
entered.handlers['nondubito:languagechange']();
assert.equal(entered.document.title, '一本新小說 — Non Dubito');
assert.equal(entered.menu['aria-label'], '選單');
assert.equal(new URL(entered.location.href).searchParams.get('lang'), 'zh-hant');

const plain = fixture('https://nondubito.net/essays/recent-fiction/index.html#year-2023', 'zh-hant');
plain.handlers.DOMContentLoaded();
assert.equal(plain.replacements(), 0);
assert.equal(plain.location.href, 'https://nondubito.net/essays/recent-fiction/index.html#year-2023');
plain.document.documentElement.dataset.lang = 'ja';
plain.handlers['nondubito:languagechange']();
assert.equal(plain.document.title, '一本新小說 — Non Dubito');
console.log('OK: Recent Fiction language, title, URL, and accessibility state');
