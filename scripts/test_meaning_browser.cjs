/* Start a local static server, then run with Playwright available via NODE_PATH.
 * node scripts/test_meaning_browser.cjs http://127.0.0.1:8768
 * MEANING_BROWSER_CHANNEL=chrome uses installed Chrome.
 * MEANING_SCREENSHOTS=/absolute/existing/directory saves representative views.
 */
const assert = require('node:assert/strict');
const path = require('node:path');
const {chromium} = require('playwright');
const base = process.argv[2] || 'http://127.0.0.1:8768';
const pages = ['index', ...Array.from({length: 8}, (_, i) => `ep${String(i + 1).padStart(2, '0')}`)];

(async () => {
  const browser = await chromium.launch({headless: true, ...(process.env.MEANING_BROWSER_CHANNEL ? {channel: process.env.MEANING_BROWSER_CHANNEL} : {})});
  try {
    const context = await browser.newContext();
    await context.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin ? route.continue() : route.abort());
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    let checks = 0;
    for (const width of [1440, 390, 320]) {
      await page.setViewportSize({width, height: 950});
      for (const name of pages) {
        await page.goto(`${base}/essays/meaning/${name}.html?lang=zh`, {waitUntil: 'load'});
        const original = await page.locator('main').innerText();
        for (const lang of ['en', 'zh-hant', 'zh']) {
          await page.locator(`.lang-btn[data-lang="${lang}"]`).click();
          await page.waitForFunction(language => document.documentElement.lang === {en: 'en', zh: 'zh-Hans', 'zh-hant': 'zh-Hant'}[language], lang);
          assert.equal(await page.locator('h1:visible').count(), 1);
          assert.equal(await page.locator(`.lang-btn[data-lang="${lang}"]`).getAttribute('aria-pressed'), 'true');
          assert.equal(new URL(page.url()).searchParams.get('lang'), lang);
          const layout = await page.evaluate(() => ({page: document.documentElement.scrollWidth, width: innerWidth}));
          assert.ok(layout.page <= layout.width + 1, `${name}, ${width}, ${lang}: overflow ${layout.page}`);
          if (lang === 'en') assert.equal(await page.locator('main .lang-zh:visible').count(), 0);
          if (lang === 'zh-hant') {
            const label = await page.locator(name === 'index' ? '.lang-zh .series-label' : '.essay-series.lang-zh').innerText();
            assert.ok(label.includes('意義論'), `${name}: Traditional heading`);
            if (name !== 'index') {
              const content = await page.locator('.essay-body.lang-zh').innerText();
              assert.ok(content.length > 1200, `${name}: complete prose remains present`);
              assert.ok(!/[这们会为]/.test(content), `${name}: stale Traditional text`);
            }
          }
          if (process.env.MEANING_SCREENSHOTS && ((width === 1440 && name === 'ep01' && lang === 'en') || (width === 390 && name === 'ep06' && lang === 'zh-hant'))) {
            await page.screenshot({path: path.join(process.env.MEANING_SCREENSHOTS, `meaning-${name}-${width}-${lang}.png`)});
          }
          checks++;
        }
        assert.equal(await page.locator('main').innerText(), original, `${name}: Simplified round trip`);
        if (process.env.MEANING_SCREENSHOTS && ((width === 1440 && ['index', 'ep01'].includes(name)) || (width === 390 && ['index', 'ep06'].includes(name)))) {
          await page.screenshot({path: path.join(process.env.MEANING_SCREENSHOTS, `meaning-${name}-${width}.png`)});
        }
      }
    }
    // Explicit search-result language must override a saved language.
    for (const lang of ['en', 'zh-hant']) {
      await page.goto(`${base}/essays/meaning/ep01.html?lang=${lang}`);
      assert.equal(await page.locator('html').getAttribute('data-lang'), lang);
    }
    await page.locator('.series-nav a').last().click();
    assert.ok(page.url().includes('ep02.html'));
    assert.equal(await page.locator('html').getAttribute('data-lang'), 'zh-hant');
    // All nine pages are discoverable by series name in the matching subject.
    // The selected result language must win over the English search UI.
    for (const [indexLang, mode, query] of [['en', 'en', 'meaning theory'], ['zh-Hans', 'zh', '意义论'], ['zh-Hant', 'zh-hant', '意義論']]) {
      const params = new URLSearchParams({lang: 'en', in: indexLang, q: query, domain: 'sae-philosophy'});
      await page.goto(`${base}/search.html?${params}`);
      await page.waitForFunction(() => document.querySelectorAll('[data-search-results] a[href*="essays/meaning/"]').length === 9);
      const link = page.locator('[data-search-results] a[href*="essays/meaning/ep02.html"]');
      assert.equal(new URL(await link.getAttribute('href'), base).searchParams.get('lang'), mode);
      await link.click();
      assert.equal(await page.locator('html').getAttribute('data-lang'), mode);
    }
    await page.goto(`${base}/library.html?lang=zh-hant`);
    const card = page.locator('a.series-card[href="essays/meaning/index.html"]');
    assert.ok((await card.innerText()).includes('錯選的專業'));
    // No storage access is required to read or switch language.
    const restricted = await context.newPage();
    await restricted.addInitScript(() => Object.defineProperty(window, 'localStorage', {get() {throw new Error('Storage unavailable');}}));
    restricted.on('pageerror', error => errors.push(error.message));
    await restricted.goto(`${base}/essays/meaning/index.html?lang=en`);
    assert.equal(await restricted.locator('html').getAttribute('data-lang'), 'en');
    await restricted.locator('.lang-btn[data-lang="zh-hant"]').click();
    await restricted.waitForFunction(() => document.documentElement.lang === 'zh-Hant');
    assert.deepEqual(errors, []);
    console.log(`OK: ${checks} page/width/language checks, 3 search-to-reading journeys, Traditional Library card, query priority, persistence, and storage-disabled reading`);
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exitCode = 1;});
