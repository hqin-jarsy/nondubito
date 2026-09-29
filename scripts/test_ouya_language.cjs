// Unit-test the actual page/controller scripts against a minimal DOM fixture.
// This deliberately makes no browser, network, layout, or screenshot claims.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const controller = fs.readFileSync(path.join(root, 'language-select.js'), 'utf8');

class Element {
  constructor(tag, attrs = {}, text = '') {
    this.tag = tag; this.attrs = attrs; this.textContent = text;
    this.dataset = {}; this.children = []; this.handlers = {};
    for (const [k, v] of Object.entries(attrs)) {
      if (k.startsWith('data-')) this.dataset[k.slice(5)] = v;
    }
    this.classes = new Set((attrs.class || '').split(' '));
    this.classList = {
      contains: k => this.classes.has(k),
      add: k => this.classes.add(k),
      toggle: (k, on) => on ? this.classes.add(k) : this.classes.delete(k),
    };
  }
  getAttribute(k) { return this.attrs[k] || null; }
  setAttribute(k, v) { this.attrs[k] = v; }
  appendChild(child) { this.children.push(child); }
  addEventListener(name, fn) { this.handlers[name] = fn; }
  get options() { return this.children; }
}

function fixture(relative, query, saved, denied = false) {
  const html = fs.readFileSync(path.join(root, relative), 'utf8');
  const choices = [...html.match(/<div class="lang-toggle">([\s\S]*?)<\/div>/)[1]
    .matchAll(/<(button|a|span) ([^>]*class="lang-btn[^>]*)>([^<]+)<\/(?:button|a|span)>/g)]
    .map(([, tag, raw, text]) => new Element(tag,
      Object.fromEntries([...raw.matchAll(/([\w-]+)="([^"]*)"/g)].map(m => [m[1], m[2]])), text));
  const toggle = new Element('div');
  toggle.querySelectorAll = () => choices;
  const documentElement = new Element('html', {
    'data-lang': html.match(/<html[^>]*data-lang="([^"]+)"/)?.[1] || '',
  });
  documentElement.lang = html.match(/<html lang="([^"]+)"/)[1];
  const ready = [];
  let stored = saved, destination = '';
  const document = {
    documentElement, readyState: 'loading',
    addEventListener: (name, fn) => ready.push(fn),
    querySelectorAll: selector => selector === '.lang-toggle' ? [toggle] : choices.filter(c => c.dataset.lang),
    createElement: tag => new Element(tag),
  };
  const context = {
    document, URLSearchParams, location: { search: query },
    window: { location: { assign: href => { destination = href; } } },
    localStorage: {
      getItem() { if (denied) throw Error('denied'); return stored; },
      setItem(k, value) { if (denied) throw Error('denied'); stored = value; },
    },
  };
  const inline = html.match(/<script id="ouya-inline-language">([\s\S]*?)<\/script>/)?.[1];
  if (inline) vm.runInNewContext(inline, context);
  vm.runInNewContext(controller, context);
  ready.forEach(fn => fn());
  return { select: toggle.children[0], documentElement, destination: () => destination, stored: () => stored };
}

let checks = 0;
for (const episode of ['ep01', 'ep02', 'ep03', 'ep04']) {
for (const saved of [null, 'en', 'zh', 'zh-hant', 'fr']) {
  for (const query of ['', '?lang=en', '?lang=zh', '?lang=ko']) {
    const f = fixture(`essays/ouya/${episode}.html`, query, saved);
    const expected = query === '?lang=en' ? 'en' : query === '?lang=zh' ? 'zh' : saved === 'en' ? 'en' : 'zh';
    assert.equal(f.select.options.length, 8);
    assert.equal(f.select.options[f.select.selectedIndex].dataset.inlineLanguage, expected);
    assert.equal(f.documentElement.getAttribute('data-lang'), expected);
    for (const [index, language] of [[0, 'en'], [1, 'zh']]) {
      f.select.selectedIndex = index; f.select.handlers.change();
      assert.equal(f.documentElement.getAttribute('data-lang'), language);
      assert.equal(f.stored(), language);
    }
    checks++;
  }
}
for (const language of ['zh-hant', 'ja', 'fr', 'de', 'es', 'ko']) {
  const f = fixture(`essays/ouya/${language}/${episode}.html`, '', 'en');
  assert.equal(f.select.options.length, 8);
  assert.equal(f.select.options[f.select.selectedIndex].dataset.href, undefined);
  for (const [index, lang] of [[0, 'en'], [1, 'zh']]) {
    f.select.selectedIndex = index; f.select.handlers.change();
    assert.equal(f.destination(), `../${episode}.html?lang=${lang}`);
  }
  checks++;
}
const denied = fixture(`essays/ouya/${episode}.html`, '?lang=en', null, true);
assert.equal(denied.documentElement.getAttribute('data-lang'), 'en');
checks++;
}
console.log(`OK: ${checks} language-state/menu unit scenarios (no visual browser test)`);
