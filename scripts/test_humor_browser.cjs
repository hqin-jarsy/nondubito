/* node scripts/test_humor_browser.cjs http://127.0.0.1:8776
 * Uses isolated headless Chrome, never the user's browser profile.
 */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const dataDir = path.join(__dirname, '../data/humor');
const data = {issues: fs.readdirSync(dataDir).filter(f => /^selection-.*\.json$/.test(f)).sort()
  .flatMap(f => JSON.parse(fs.readFileSync(path.join(dataDir, f), 'utf8')).issues)};
const base = process.argv[2] || 'http://127.0.0.1:8776';
(async () => {
  const browser = await chromium.launch({headless: true, channel: 'chrome'});
  try {
    const context = await browser.newContext();
    await context.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin ? route.continue() : route.abort());
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    let checks = 0;
    for (const width of [1440, 768, 390, 320]) {
      await page.setViewportSize({width, height: 920});
      for (const lang of ['zh', 'zh-hant']) {
        for (const slug of ['index', ...data.issues.map(i => i.slug)]) {
          const dir = lang === 'zh-hant' ? 'zh-hant/' : '';
          await page.goto(`${base}/essays/humor/${dir}${slug}.html?lang=${lang}`);
          assert.equal(await page.locator('h1:visible').count(), 1);
          assert.equal(await page.locator('.humor-header').count(), 1);
          assert.equal(await page.locator('.humor-main-nav a:visible').count(), 4);
          const geometry = await page.evaluate(() => ({
            width: innerWidth, page: document.documentElement.scrollWidth,
            header: document.querySelector('header').getBoundingClientRect().bottom,
            main: document.querySelector('main').getBoundingClientRect().top,
          }));
          assert.ok(geometry.page <= geometry.width + 1, `overflow ${width} ${lang} ${slug}`);
          assert.equal(await page.locator('.humor-footer').evaluate(el => getComputedStyle(el).backgroundColor), 'rgba(0, 0, 0, 0)');
          if (slug === 'index') {
            assert.equal(await page.locator('.humor-group').count(), 3);
            assert.equal(await page.locator('.humor-issue').count(), 15);
            await page.locator('.humor-jump a').last().click();
            await page.locator('#issues-11-15').scrollIntoViewIfNeeded();
            assert.ok(page.url().endsWith('#issues-11-15'));
            assert.equal(await page.locator('#issues-11-15 .humor-issue').count(), 5);
          }
          if (slug !== 'index') {
            assert.equal(await page.locator('.humor-source[open]').count(), 0);
            const summary = page.locator('.humor-source summary').first();
            await summary.focus();
            await page.keyboard.press('Enter');
            assert.equal(await page.locator('.humor-source[open]').count(), 1);
            assert.ok(await page.locator('.humor-source[open] a').first().isVisible());
          }
          checks++;
        }
      }
    }
    await page.goto(`${base}/essays/humor/01-children-have-a-point.html?lang=zh#h003`);
    await page.locator('[data-humor-language="zh-hant"]').click();
    await page.waitForURL('**/zh-hant/01-children-have-a-point.html#h003');
    assert.equal(await page.locator('html').getAttribute('lang'), 'zh-Hant');
    await page.locator('[data-humor-language="zh"]').click();
    await page.waitForURL('**/01-children-have-a-point.html?lang=zh#h003');
    assert.equal(await page.locator('html').getAttribute('lang'), 'zh-Hans');
    await page.evaluate(() => localStorage.setItem('nd_lang', 'zh-hant'));
    await page.goto(`${base}/essays/humor/index.html`);
    await page.waitForURL('**/humor/zh-hant/index.html');
    await page.goto(`${base}/essays/humor/01-children-have-a-point.html?lang=zh`);
    await page.locator('a[rel="next"]').click();
    assert.equal(await page.locator('html').getAttribute('lang'), 'zh-Hans');
    if (process.env.HUMOR_SCREENSHOTS) {
      for (const [name, width, file] of [['desktop', 1440, 'index'], ['mobile', 390, data.issues[10].slug]]) {
        await page.setViewportSize({width, height: 920});
        await page.goto(`${base}/essays/humor/${file}.html?lang=zh`);
        await page.screenshot({path: path.join(process.env.HUMOR_SCREENSHOTS, name+'.png'), fullPage: true});
      }
    }
    const nojs = await browser.newContext({javaScriptEnabled: false, viewport: {width: 390, height: 850}});
    const plain = await nojs.newPage();
    await plain.goto(`${base}/essays/humor/11-hear-me-out.html`);
    assert.equal(await plain.locator('article').count(), 6);
    await plain.locator('.humor-source summary').first().click();
    assert.equal(await plain.locator('.humor-source[open]').count(), 1);
    await plain.locator('[data-humor-language="zh-hant"]').click();
    assert.equal(await plain.locator('html').getAttribute('lang'), 'zh-Hant');
    assert.deepEqual(errors, []);
    console.log(`OK: ${checks} page/language/viewport combinations; keyboard disclosure, language links, anchors, stored preference and no-JS reading`);
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exit(1); });
