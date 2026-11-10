/* War full-edition acceptance. Run only in an authorized isolated headless environment.
 * python3 -B scripts/prepare_war_browser_fixtures.py --output /tmp/war-expected.json
 * node scripts/test_war_full_browser.cjs --base http://127.0.0.1:8791 \
 *   --fixture /tmp/war-expected.json --out data/war-full/qa/browser-NEW --final
 * Optional: --channel chrome, --executable-path /path/to/chromium, --repo-root /checkout.
 * --validate-fixture FILE performs shape/hash checks only and NEVER starts a browser.
 * No user profile, external requests, public-file writes or publication. Screenshot
 * capture is evidence collection, not human visual review or a release approval.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const argv = process.argv.slice(2);
function option(name, fallback) {
  const i = argv.indexOf(name);
  if (i < 0) return fallback;
  assert.ok(argv[i + 1] && !argv[i + 1].startsWith('--'), `Missing argument for ${name}`);
  return argv[i + 1];
}
const root = path.resolve(option('--repo-root', path.join(__dirname, '..')));
const langs = ['zh', 'zh-hant', 'en', 'ja', 'fr', 'de', 'es', 'ko'];
const foreign = ['ja', 'fr', 'de', 'es', 'ko'];
const labels = { zh: '中文', 'zh-hant': '繁體', en: 'EN', ja: '日本語', fr: 'Français', de: 'Deutsch', es: 'Español', ko: '한국어' };
const slugs = [...Array.from({ length: 7 }, (_, i) => `ep0${i + 1}`), ...Array.from({ length: 8 }, (_, i) => `if0${i + 1}`), 'if-conclusion'];
const widths = [320, 375, 1440];
const primary = l => !foreign.includes(l);
const actual = l => ({ zh: 'zh-Hans', 'zh-hant': 'zh-Hant' }[l] || l);
const shaBytes = raw => crypto.createHash('sha256').update(raw).digest('hex');
const shaFile = file => shaBytes(fs.readFileSync(file));
const shaValue = value => shaBytes(JSON.stringify(value));
const readJSON = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const norm = s => s.replace(/\s+/g, ' ').trim();
// The frozen ep05 head legitimately omits the ASCII quotes used by its card.
// Ignore only those quotes for the Chinese fragment of that one essay. English
// wording, Chinese script, and every other title remain strict.
function headContainsPart(title, part, slug, partIndex) {
  const ignoreQuotes = slug === 'ep05' && partIndex === 0;
  const value = norm(title);
  return (ignoreQuotes ? value.replace(/"/g, '') : value)
    .includes(ignoreQuotes ? part.replace(/"/g, '') : part);
}
function validateFixture(f, requireFinal = true) {
  assert.equal(f.schema_version, 1);
  if (requireFinal) assert.equal(f.status, 'final_effective_expectations', 'A shape-only draft is not a final fixture');
  assert.deepEqual(f.languages, langs); assert.deepEqual(f.slugs, slugs); assert.deepEqual(f.widths, widths);
  assert.equal(Object.keys(f.pages).length, 136);
  for (const l of langs) {
    let units = 0, tables = 0;
    for (const s of slugs) {
      const e = f.pages[`${l}/${s}`]; assert.ok(e.title && e.deck);
      assert.equal(e.units.length, e.unit_tags.length); assert.ok(e.units.every(x => typeof x === 'string' && x.length));
      units += e.units.length; tables += e.tables.length;
      for (const t of e.tables) {
        assert.ok(t.body_index >= 0 && t.body_index < e.units.length);
        assert.ok(t.rows.length && t.rows.every(row => row.length));
        for (const row of t.rows) for (const c of row) assert.ok(typeof c.text === 'string' && ['th', 'td'].includes(c.tag) && c.colspan >= 1 && c.rowspan >= 1);
      }
    }
    assert.equal(units, 1121, `${l} total units`); assert.equal(tables, 12, `${l} total tables`);
    if (primary(l)) for (const s of ['index', ...slugs]) { assert.equal(f.pages[`${l}/${s}`].head_title_parts.length, 2); assert.ok(f.pages[`${l}/${s}`].head_title_parts.every(Boolean)); }
    const ix = f.pages[`${l}/index`]; assert.equal(ix.intro.length, 5); assert.equal(ix.groups.length, 2);
    assert.deepEqual(Object.keys(ix.cards).sort(), [...slugs].sort());
    assert.equal(ix.source_notes.length, primary(l) ? 2 : 1);
  }
  assert.equal(f.author_changed_units.length, 8);
  assert.ok(Object.keys(f.input_hashes).length > 100, 'Missing supporting inputs');
  return { pages: 136, viewportCombinations: 408, unitsPerLanguage: 1121, tablesPerLanguage: 12 };
}
function verifyFixtureInputs(f) {
  for (const [relative, digest] of Object.entries(f.input_hashes)) {
    const file = path.resolve(root, relative);
    assert.ok(file.startsWith(root + path.sep), `Input escapes repository: ${relative}`);
    assert.equal(shaFile(file), digest, `Input changed after fixture generation: ${relative}`);
  }
}
module.exports = { headContainsPart };
if (require.main === module) {
  if (argv.includes('--validate-fixture')) {
    const f = readJSON(path.resolve(option('--validate-fixture')));
    const shape = validateFixture(f); verifyFixtureInputs(f);
    console.log(JSON.stringify({ status: 'fixture_shape_and_hashes_valid', browserStarted: false, ...shape }));
  } else {
    main().catch(error => { console.error(error.stack || String(error)); process.exitCode = 1; });
  }
}

async function main() {
  const base = option('--base', 'http://127.0.0.1:8791').replace(/\/$/, '');
  const parsed = new URL(base);
  assert.ok(['127.0.0.1', 'localhost', '[::1]'].includes(parsed.hostname), 'Loopback-only browser acceptance');
  assert.ok(['http:', 'https:'].includes(parsed.protocol));
  assert.ok(!parsed.username && !parsed.password && parsed.pathname === '/' && !parsed.search && !parsed.hash);
  assert.notEqual(argv.includes('--final'), argv.includes('--preview'), 'Choose exactly one of --final or --preview');
  const mode = argv.includes('--final') ? 'final-local-public-pages' : 'isolated-local-preview';
  const fixturePath = path.resolve(option('--fixture', 'data/war-full/qa/expected.json'));
  const out = path.resolve(option('--out', path.join(root, 'data/war-full/qa', `browser-${Date.now()}`)));
  assert.ok(!fs.existsSync(out), 'Protect previous QA evidence: choose a NEW output directory');
  fs.mkdirSync(path.join(out, 'screenshots'), { recursive: true });
  const reportPath = path.join(out, 'run.json');
  let browser, fixture, activeCase = null;
  const pendingResponses = new Set();
  const served = new Map();
  const expectedCoverage = {
    viewportViews: 408, languageSelections: 128, navigationChains: 16,
    searchResultClicks: 16, invalidStorageFallbacks: 6, queryOverrides: 9,
    blockedStoragePages: 24, noJSForeignPages: 85, mobileTables: 96,
    paragraphScreenshots: 240,
  };
  const report = {
    schemaVersion: 1, series: 'war', status: 'running', mode, base,
    startedAt: new Date().toISOString(), finishedAt: null,
    independentVisualReview: 'pending_not_performed_by_this_script',
    browserVersion: null, fixture: { path: fixturePath },
    inputHashes: {}, runtimeFileHashes: {}, servedArtifacts: [],
    expectedCoverage, coverage: {}, cases: [], failures: [], pageErrors: [],
    blockedExternalRequests: [], screenshots: [], searchEntrypoints: [],
    inputsUnchanged: null, screenshotsHumanReviewed: false,
  };
  const writeReport = () => fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
  function failure(check, message, details = {}) {
    const item = { caseId: activeCase, check, message, ...details };
    report.failures.push(item); return false;
  }
  function expect(condition, check, details = {}) {
    return condition || failure(check, check, details);
  }
  function equal(got, wanted, check, details = {}) {
    return expect(JSON.stringify(got) === JSON.stringify(wanted), check, { actual: got, expected: wanted, ...details });
  }
  async function runCase(category, identity, fn) {
    activeCase = `${category}:${identity}`;
    const record = { id: activeCase, category, startedAt: new Date().toISOString() };
    const before = report.failures.length;
    const bucket = report.coverage[category] ||= { attempted: 0, passed: 0, failed: 0 };
    bucket.attempted++;
    try { record.result = await fn(); }
    catch (error) { failure('exception', String(error), { stack: error.stack }); }
    record.passed = report.failures.length === before;
    bucket[record.passed ? 'passed' : 'failed']++;
    record.failureIndexes = Array.from({ length: report.failures.length - before }, (_, i) => before + i);
    record.finishedAt = new Date().toISOString(); report.cases.push(record);
    activeCase = null; writeReport();
  }
  const relativeURL = (l, s) => `/essays/war/${primary(l) ? '' : l + '/'}${s}.html`;
  const url = (l, s, query = true) => base + relativeURL(l, s) + (primary(l) && query ? '?lang=' + l : '');
  async function navigate(p, target) {
    const response = await p.goto(target, { waitUntil: 'load' });
    expect(response && response.status() === 200, 'page HTTP 200', { target, status: response?.status() });
  }
  async function context(options = {}) {
    const c = await browser.newContext({ viewport: { width: 320, height: 900 }, serviceWorkers: 'block', ...options });
    c.setDefaultTimeout(10000); c.setDefaultNavigationTimeout(20000);
    await c.route('**/*', route => {
      let local = false;
      try { local = new URL(route.request().url()).origin === parsed.origin; } catch (_) {}
      if (local) return route.continue();
      report.blockedExternalRequests.push({ url: route.request().url(), resourceType: route.request().resourceType() });
      return route.abort('blockedbyclient');
    });
    c.on('page', p => {
      p.on('pageerror', e => {
        report.pageErrors.push({ caseId: activeCase, url: p.url(), message: e.message });
        failure('pageerror', e.message, { url: p.url() });
      });
      p.on('response', response => {
        if (new URL(response.url()).origin !== parsed.origin) return;
        const caseId = activeCase;
        const task = (async () => {
          if (response.status() >= 400) failure('local resource HTTP error', response.url(), { status: response.status(), caseId });
          if (response.status() !== 200) return;
          const body = await response.body();
          const key = response.url(), digest = shaBytes(body), existing = served.get(key);
          if (existing && existing.sha256 !== digest) failure('served artifact changed during run', key, { before: existing.sha256, after: digest, caseId });
          served.set(key, { url: key, sha256: digest, bytes: body.length, contentType: response.headers()['content-type'] || '' });
        })().catch(error => failure('response hash unavailable', response.url(), { error: String(error), caseId }));
        pendingResponses.add(task); task.finally(() => pendingResponses.delete(task));
      });
    });
    return c;
  }
  async function checkPage(p, l, s) {
    await p.waitForFunction(wanted => document.documentElement.lang === wanted, actual(l));
    await p.evaluate(async () => { await document.fonts.ready; });
    const e = fixture.pages[`${l}/${s}`];
    // This reads actual computed-visible text. Hidden language copies are never
    // allowed to satisfy an expectation for the selected reading language.
    const got = await p.evaluate(() => {
      const visible = n => {
        if (!n || !n.getClientRects().length) return false;
        for (let e = n; e; e = e.parentElement) {
          const c = getComputedStyle(e);
          if (c.display === 'none' || c.visibility === 'hidden' || c.visibility === 'collapse' || Number(c.opacity) === 0) return false;
        }
        return true;
      };
      const txt = n => {
        if (!n) return null;
        const walker = document.createTreeWalker(n, NodeFilter.SHOW_TEXT); let x, out = '';
        while ((x = walker.nextNode())) if (visible(x.parentElement)) out += x.nodeValue;
        return out.replace(/\s+/g, ' ').trim();
      };
      const all = (root, selector) => [...root.querySelectorAll(selector)].filter(visible);
      const selectText = (root, selector) => all(root, selector).map(txt);
      const headings = selectText(document, 'h1');
      const bodies = all(document, '.essay-body');
      const descriptions = all(document, '.series-desc');
      return {
        htmlLang: document.documentElement.lang, dataLang: document.documentElement.getAttribute('data-lang'),
        innerWidth, scrollWidth: document.documentElement.scrollWidth, documentTitle: document.title,
        headings, toggles: selectText(document, '.lang-toggle .lang-btn'),
        activeToggles: selectText(document, '.lang-toggle .lang-btn.active'), bodyCount: bodies.length,
        units: bodies.length === 1 ? [...bodies[0].children].map(n => ({ tag: n.tagName.toLowerCase(), visible: visible(n), text: txt(n) })) : [],
        intro: descriptions.length === 1 ? [...descriptions[0].children].filter(visible).map(txt) : [],
        groups: all(document, '.group-head').map(g => ({
          eyebrow: selectText(g, '.group-eyebrow,.entry-num'), title: selectText(g, 'h2'), note: selectText(g, '.group-note,p'),
        })),
        cards: all(document, '.entry-row').map(c => ({
          href: c.href, title: selectText(c, '.entry-title,.entry-title-zh,.entry-title-en'), deck: selectText(c, '.entry-desc'),
        })),
        sourceNotes: selectText(document, '.source-note > span,.source-note > p:not(.war-source-links)'),
      };
    });
    equal(got.htmlLang, actual(l), 'html lang', { l, s });
    equal(new URL(p.url()).pathname, relativeURL(l, s), 'selected language route', { l, s });
    equal(got.innerWidth, p.viewportSize().width, 'true viewport width', { l, s });
    expect(got.scrollWidth <= got.innerWidth + 1, 'no full-page horizontal overflow', { l, s, width: got.innerWidth, scrollWidth: got.scrollWidth });
    equal(got.headings, [e.title], 'full visible title', { l, s });
    equal([...got.toggles].sort(), Object.values(labels).sort(), 'eight visible language controls', { l, s });
    equal(got.activeToggles, [labels[l]], 'one selected language control', { l, s });
    expect(Boolean(got.documentTitle) && got.documentTitle.includes('Non Dubito'), 'document title present', { l, s, title: got.documentTitle });
    if (!primary(l)) equal(got.documentTitle, e.title + ' — Non Dubito', 'foreign document title', { l, s });
    else for (const [partIndex, part] of e.head_title_parts.entries()) expect(headContainsPart(got.documentTitle, part, s, partIndex), 'reviewed bilingual document title fragment', { l, s, title: got.documentTitle, requiredFragment: part, ignoredAsciiQuotes: s === 'ep05' && partIndex === 0 });
    if (s !== 'index') {
      equal(got.bodyCount, 1, 'one visible full body', { l, s });
      equal(got.units.length, e.units.length, 'full unit count', { l, s });
      for (let i = 0; i < Math.max(got.units.length, e.units.length); i++) {
        const unit = got.units[i];
        equal(unit?.text, e.units[i], 'unit full visible text', { l, s, bodyIndex: i });
        equal(unit?.tag, e.unit_tags[i], 'unit element tag', { l, s, bodyIndex: i });
        expect(unit?.visible, 'unit not hidden', { l, s, bodyIndex: i });
      }
    } else {
      equal(got.intro, e.intro, 'all five complete index paragraphs', { l });
      equal(got.groups.length, 2, 'two complete index groups', { l });
      for (let i = 0; i < 2; i++) for (const k of ['eyebrow', 'title', 'note']) equal(got.groups[i]?.[k], [e.groups[i][k]], 'index group full text', { l, group: i, field: k });
      equal(got.cards.length, 16, 'all sixteen index cards', { l });
      for (let i = 0; i < slugs.length; i++) {
        const card = got.cards[i], slug = slugs[i];
        equal(card?.title, [e.cards[slug].title], 'index card complete title', { l, slug });
        equal(card?.deck, [e.cards[slug].deck], 'index card complete deck', { l, slug });
        equal(card ? new URL(card.href).pathname : null, relativeURL(l, slug), 'index card target', { l, slug });
      }
      equal(got.sourceNotes, e.source_notes, 'index complete source notes', { l });
    }
    return { language: l, slug: s, width: got.innerWidth, units: got.units.length,
      renderedUnitsSHA256: shaValue(got.units.map(u => u.text)), expectedUnitsSHA256: shaValue(e.units || []),
      fullTextCompared: true, title: got.headings, landedURL: p.url(), htmlLang: got.htmlLang };
  }
  async function linkTo(p, selector, l, s) {
    const candidates = p.locator(selector);
    for (let i = 0; i < await candidates.count(); i++) {
      const candidate = candidates.nth(i);
      if (!await candidate.isVisible()) continue;
      const href = await candidate.getAttribute('href'); if (!href) continue;
      const target = new URL(href, p.url());
      if (target.origin === parsed.origin && target.pathname === relativeURL(l, s)) return candidate;
    }
    throw new Error(`Missing visible internal route ${l}/${s} in ${selector}`);
  }
  async function stablePosition(p, locator, horizontal = null) {
    await p.evaluate(() => { document.documentElement.style.setProperty('scroll-behavior', 'auto', 'important'); });
    const desired = await locator.evaluate((n, x) => {
      n.style.setProperty('scroll-behavior', 'auto', 'important');
      const y = Math.max(0, Math.min(document.documentElement.scrollHeight - innerHeight, n.getBoundingClientRect().top + scrollY - 80));
      window.scrollTo({ top: y, left: 0, behavior: 'instant' });
      if (x !== null) n.scrollTo({ left: x === 'right' ? Math.max(0, n.scrollWidth - n.clientWidth) : 0, behavior: 'instant' });
      return { y, x: n.scrollLeft };
    }, horizontal);
    await p.waitForFunction(({ y }) => Math.abs(scrollY - y) <= 1, desired);
    const stability = await locator.evaluate(async n => {
      const position = () => ({ top: n.getBoundingClientRect().top, left: n.getBoundingClientRect().left, x: n.scrollLeft, y: scrollY });
      const before = position();
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      const after = position(); return { before, after };
    });
    for (const k of ['top', 'left', 'x', 'y']) assert.ok(Math.abs(stability.before[k] - stability.after[k]) <= 1, `Screenshot moved: ${k}`);
    const rect = await locator.evaluate(n => {
      const r = n.getBoundingClientRect();
      return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, width: r.width, height: r.height, scrollY, scrollLeft: n.scrollLeft };
    });
    assert.ok(rect.top >= -1 && rect.top < p.viewportSize().height - 100, 'Target start is not visible below navigation');
    assert.ok(rect.left >= -1 && rect.right <= p.viewportSize().width + 1, 'Screenshot target exceeds viewport');
    return { rect, twoFramesStable: true, instantScroll: true };
  }
  async function screenshot(p, locator, name, details = {}, side = null) {
    const position = await stablePosition(p, locator, side);
    const file = path.join(out, 'screenshots', name + '.png');
    assert.ok(!fs.existsSync(file), 'Protect existing screenshot');
    await p.screenshot({ path: file, fullPage: false, animations: 'disabled' });
    report.screenshots.push({ file: path.relative(out, file), sha256: shaFile(file), ...details,
      width: p.viewportSize().width, height: p.viewportSize().height, ...position,
      focus: 'Visible start of target; long units or tables can continue below frame', humanVisuallyReviewed: false });
  }
  try {
    fixture = readJSON(fixturePath); report.fixture.sha256 = shaFile(fixturePath);
    report.fixture.shape = validateFixture(fixture); verifyFixtureInputs(fixture); report.inputHashes = fixture.input_hashes;
    report.runtimeFileHashes[path.relative(root, __filename)] = shaFile(__filename);
    for (const name of ['style.css', 'classic-reading.js', 'search.html', 'search.js', 'search.css', 'data/search-index.json']) {
      const file = path.join(root, name); assert.ok(fs.existsSync(file), `Missing runtime input ${name}`);
      report.runtimeFileHashes[name] = shaFile(file);
    }
    for (const l of ['', ...foreign]) for (const s of ['index', ...slugs]) {
      const name = `essays/war/${l ? l + '/' : ''}${s}.html`;
      report.runtimeFileHashes[name] = shaFile(path.join(root, name));
    }
    const searchDir = path.join(root, 'data/search');
    for (const file of fs.readdirSync(searchDir).filter(f => f.endsWith('.json'))) report.runtimeFileHashes['data/search/' + file] = shaFile(path.join(searchDir, file));
    // Requiring Playwright is deliberately below the validation-only branch.
    const { chromium } = require('playwright');
    const launch = { headless: true };
    if (option('--channel')) launch.channel = option('--channel');
    if (option('--executable-path')) launch.executablePath = option('--executable-path');
    browser = await chromium.launch(launch); report.browserVersion = browser.version();
    const c = await context(), p = await c.newPage();
    for (const width of widths) {
      await p.setViewportSize({ width, height: 900 });
      for (const l of langs) for (const s of ['index', ...slugs]) await runCase('viewportViews', `${width}/${l}/${s}`, async () => {
        await navigate(p, url(l, s)); return checkPage(p, l, s);
      });
      console.log(`Attempted full view matrix at ${width}px`);
    }
    await p.setViewportSize({ width: 375, height: 900 });
    for (const s of ['ep01', 'if01']) for (const from of langs) for (const target of langs) await runCase('languageSelections', `${s}/${from}->${target}`, async () => {
      await navigate(p, url(from, s)); await checkPage(p, from, s);
      const controls = p.locator('.lang-toggle .lang-btn');
      let control;
      for (let i = 0; i < await controls.count(); i++) if (norm(await controls.nth(i).innerText()) === labels[target]) control = controls.nth(i);
      assert.ok(control, `Missing ${target} control`);
      const tag = await control.evaluate(n => n.tagName);
      if (tag === 'SPAN') assert.equal(from, target, 'Only the already-selected foreign language can be a passive span');
      else await control.click();
      const landed = await checkPage(p, target, s);
      if (primary(target)) equal(new URL(p.url()).searchParams.get('lang'), target, 'explicit cross-language query route', { from, target, s });
      return { from, target, controller: s, controlTag: tag, ...landed };
    });
    const navSelector = '.xiyou-nav a,.series-nav a,.war-nav a';
    for (const l of langs) for (const [first, next] of [['ep01', 'ep02'], ['if01', 'if02']]) await runCase('navigationChains', `${l}/${first}`, async () => {
      const steps = [];
      await navigate(p, url(l, 'index')); await checkPage(p, l, 'index');
      await (await linkTo(p, '.entry-row', l, first)).click(); steps.push(await checkPage(p, l, first));
      await (await linkTo(p, navSelector, l, next)).click(); steps.push(await checkPage(p, l, next));
      await (await linkTo(p, navSelector, l, first)).click(); steps.push(await checkPage(p, l, first));
      await (await linkTo(p, '.back-link,.war-nav a,.series-nav a,.xiyou-nav a', l, 'index')).click(); steps.push(await checkPage(p, l, 'index'));
      return { language: l, group: first === 'ep01' ? 'main' : 'interfaces', steps, actualLinkClicks: 4 };
    });
    for (const l of langs) for (const s of ['ep01', 'if-conclusion']) await runCase('searchResultClicks', `${l}/${s}`, async () => {
      const title = fixture.pages[`${l}/${s}`].title;
      const searchURL = `${base}/search.html?in=${actual(l)}&q=${encodeURIComponent(title)}`;
      await navigate(p, searchURL);
      await p.locator('[data-search-results] h2 a').first().waitFor();
      const result = await linkTo(p, '[data-search-results] h2 a', l, s);
      const resultHref = await result.getAttribute('href');
      await result.click(); const landed = await checkPage(p, l, s);
      const record = { language: l, slug: s, title, searchURL, resultHref, landedURL: p.url(), htmlLang: landed.htmlLang };
      report.searchEntrypoints.push(record); return record;
    });
    for (const value of ['garbage', 'ja']) for (const s of ['index', 'ep01', 'if01']) await runCase('invalidStorageFallbacks', `${value}/${s}`, async () => {
      await p.evaluate(v => { localStorage.setItem('nd_lang', v); localStorage.setItem('nondubito-lang', v); }, value);
      await navigate(p, url('zh', s, false) + '?lang=invalid'); const record = await checkPage(p, 'zh', s);
      equal(await p.evaluate(() => [localStorage.getItem('nd_lang'), localStorage.getItem('nondubito-lang')]), ['zh', 'zh'], 'invalid storage repaired');
      return { invalidValue: value, ...record };
    });
    for (const l of ['zh', 'zh-hant', 'en']) for (const s of ['index', 'ep01', 'if01']) await runCase('queryOverrides', `${l}/${s}`, async () => {
      await p.evaluate(() => { localStorage.setItem('nd_lang', 'garbage'); localStorage.setItem('nondubito-lang', 'ko'); });
      await navigate(p, url(l, s)); const record = await checkPage(p, l, s);
      equal(await p.evaluate(() => [localStorage.getItem('nd_lang'), localStorage.getItem('nondubito-lang')]), [l, l], 'query overrides bad storage'); return record;
    });
    const bc = await context();
    await bc.addInitScript(() => Object.defineProperty(window, 'localStorage', { configurable: true, get() { throw new Error('Storage blocked for acceptance test'); } }));
    const bp = await bc.newPage();
    for (const l of langs) for (const s of ['index', 'ep01', 'if01']) await runCase('blockedStoragePages', `${l}/${s}`, async () => {
      await navigate(bp, url(l, s)); return checkPage(bp, l, s);
    });
    const nc = await context({ javaScriptEnabled: false }), np = await nc.newPage();
    for (const l of foreign) for (const s of ['index', ...slugs]) await runCase('noJSForeignPages', `${l}/${s}`, async () => {
      await navigate(np, url(l, s)); return checkPage(np, l, s);
    });
    await p.setViewportSize({ width: 320, height: 900 });
    for (const l of langs) for (const s of slugs) {
      const tables = fixture.pages[`${l}/${s}`].tables;
      if (!tables.length) continue;
      for (const t of tables) await runCase('mobileTables', `${l}/${s}/${t.table_index}`, async () => {
        await navigate(p, url(l, s)); await checkPage(p, l, s);
        equal(await p.locator('.essay-body:visible .table-scroll').count(), tables.length, 'all table wrappers present', { l, s });
        const wrapper = p.locator('.essay-body:visible .table-scroll').nth(t.table_index);
        assert.equal(await wrapper.count(), 1, 'Every table needs a contained scroll wrapper');
        const table = wrapper.locator('table'); assert.equal(await table.count(), 1);
        const matrix = await table.evaluate(t => [...t.rows].map(r => [...r.cells].map(c => ({ text: c.textContent.replace(/\s+/g, ' ').trim(), tag: c.tagName.toLowerCase(), colspan: c.colSpan, rowspan: c.rowSpan }))));
        equal(matrix, t.rows, 'complete table row/column/cell text', { l, s, tableIndex: t.table_index });
        const stem = `${l}-${s}-table${t.table_index + 1}-320`;
        await screenshot(p, wrapper, stem + '-left', { language: l, slug: s, tableIndex: t.table_index, side: 'left' }, 'left');
        const left = await wrapper.evaluate(n => ({ left: n.scrollLeft, max: Math.max(0, n.scrollWidth - n.clientWidth) }));
        expect(Math.abs(left.left) <= 1, 'table starts at left edge', { l, s, ...left });
        await screenshot(p, wrapper, stem + '-right', { language: l, slug: s, tableIndex: t.table_index, side: 'right' }, 'right');
        const end = await wrapper.evaluate(n => ({ left: n.scrollLeft, max: Math.max(0, n.scrollWidth - n.clientWidth),
          right: n.getBoundingClientRect().right,
          lastCellsRight: [...n.querySelectorAll('tr')].map(r => r.lastElementChild?.getBoundingClientRect().right),
          scrollWidth: document.documentElement.scrollWidth }));
        expect(Math.abs(end.left - end.max) <= 1, 'table reaches right edge, including naturally fitting tables', { l, s, ...end });
        expect(end.lastCellsRight.every(x => x <= end.right + 2), 'every final table column is reachable', { l, s, ...end });
        expect(end.scrollWidth <= 321, 'table never creates whole-page overflow', { l, s, ...end });
        return { language: l, slug: s, tableIndex: t.table_index, bodyIndex: t.body_index, rowCount: matrix.length,
          columnsPerRow: matrix.map(r => r.length), allCellsCompared: true, overflowRequired: false, didOverflow: end.max > 1, end };
      });
    }
    // Capture changed paragraphs in all three widths, and ordinary main/interface
    // prose in narrow/desktop layouts. Capture is NOT an independent visual pass.
    for (const width of widths) {
      await p.setViewportSize({ width, height: 900 });
      for (const l of langs) {
        const targets = [...fixture.author_changed_units];
        if (width !== 375) targets.push({ slug: 'ep01', body_index: 1 }, { slug: 'if01', body_index: 1 }, { slug: 'ep05', body_index: 1 });
        for (const t of targets) await runCase('paragraphScreenshots', `${width}/${l}/${t.slug}/${t.body_index}`, async () => {
          await navigate(p, url(l, t.slug)); await checkPage(p, l, t.slug);
          const unit = p.locator('.essay-body:visible').locator(':scope > *').nth(t.body_index);
          await screenshot(p, unit, `${l}-${t.slug}-${width}-u${t.body_index + 1}`, { language: l, slug: t.slug, bodyIndex: t.body_index });
          return { language: l, slug: t.slug, width, bodyIndex: t.body_index, capturedNotVisuallyReviewed: true };
        });
      }
    }
    await Promise.all([...pendingResponses]);
    for (const [category, count] of Object.entries(expectedCoverage)) equal(report.coverage[category]?.attempted, count, 'required coverage attempted', { category });
    equal(report.pageErrors.length, 0, 'zero page errors across all contexts');
    report.inputsUnchanged = false;
    verifyFixtureInputs(fixture);
    let unchanged = equal(shaFile(fixturePath), report.fixture.sha256, 'fixture unchanged during run');
    for (const [name, digest] of Object.entries(report.runtimeFileHashes)) unchanged = equal(shaFile(path.join(root, name)), digest, 'runtime input unchanged during run', { name }) && unchanged;
    report.inputsUnchanged = unchanged;
    report.status = report.failures.length ? 'failed' : 'automated_checks_passed_visual_review_pending';
  } catch (error) {
    failure('fatal', String(error), { stack: error.stack }); report.status = 'failed';
  } finally {
    await Promise.all([...pendingResponses]);
    if (browser) await browser.close();
    await Promise.all([...pendingResponses]);
    report.servedArtifacts = [...served.values()].sort((a, b) => a.url.localeCompare(b.url));
    if (report.failures.length) report.status = 'failed';
    report.finishedAt = new Date().toISOString();
    report.coverage.totalScreenshots = report.screenshots.length;
    writeReport();
    console.log(JSON.stringify({ status: report.status, report: reportPath, failures: report.failures.length,
      coverage: report.coverage, visualReview: report.independentVisualReview }));
    if (report.failures.length) process.exitCode = 1;
  }
}
