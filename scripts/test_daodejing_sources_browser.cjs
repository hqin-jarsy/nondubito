/* Start a local static server first. Requires Playwright (via NODE_PATH or npm).
 * node scripts/test_daodejing_sources_browser.cjs http://127.0.0.1:8766
 * DDJ_SCREENSHOTS=/absolute/existing/directory optionally saves visual samples.
 * DDJ_BROWSER_CHANNEL=chrome uses an installed Chrome if Playwright has no bundled browser.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'data/daodejing-chapter-texts.json')));
const ui = JSON.parse(fs.readFileSync(path.join(root, 'data/daodejing-source-ui.json')));
const base = process.argv[2] || 'http://127.0.0.1:8766';

(async () => {
  const browser = await chromium.launch({headless: true, ...(process.env.DDJ_BROWSER_CHANNEL ? {channel:process.env.DDJ_BROWSER_CHANNEL} : {})});
  try {
    const context = await browser.newContext();
    // Test the local site without analytics or third-party font dependencies.
    await context.route('**/*', route => {
      if (new URL(route.request().url()).origin === new URL(base).origin) return route.continue();
      return route.abort();
    });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    let checks = 0;
    for (const width of [1440, 390, 320]) {
      await page.setViewportSize({width, height: 950});
      for (const number of [1, 28, 42, 67, 80, 81]) {
        const name = `ch${String(number).padStart(2, '0')}.html`;
        await page.goto(`${base}/essays/daodejing/${name}`, {waitUntil:'load'});
        for (const language of ['zh', 'zh-hant', 'en', 'zh']) {
          await page.locator(`.lang-btn[data-lang="${language}"]`).click();
          await page.waitForFunction(lang => document.documentElement.getAttribute('data-lang') === lang && document.documentElement.lang === ({zh:'zh-Hans', 'zh-hant':'zh-Hant', en:'en'}[lang]), language);
          assert.equal(await page.locator('#ddj-source-title').innerText(), ui[language].title);
          assert.deepEqual(await page.locator('.ddj-source-text p').allTextContents(), data.chapters[number - 1].paragraphs);
          const visible = await page.locator('.ddj-source-details').evaluate(el => getComputedStyle(el).display !== 'none');
          assert.ok(visible);
          checks++;
        }
        await checkLayout(page, width, name);
        const details = page.locator('.ddj-source-details');
        await details.locator('summary').focus();
        await page.keyboard.press('Enter');
        assert.equal(await details.getAttribute('open'), '');
        assert.ok(await details.locator('a').last().isVisible());
        await page.keyboard.press('Enter');
        assert.equal(await details.getAttribute('open'), null);
        if (process.env.DDJ_SCREENSHOTS && ((width === 1440 && number === 1) || (width === 390 && number === 28))) {
          await page.locator('.ddj-source').scrollIntoViewIfNeeded();
          await page.screenshot({path: path.join(process.env.DDJ_SCREENSHOTS, `ddj-${number}-${width}.png`)});
        }
      }
      for (const language of ['ja', 'fr', 'de', 'es', 'ko']) {
        await page.goto(`${base}/essays/daodejing/${language}/ch42.html`, {waitUntil:'load'});
        assert.equal(await page.locator('#ddj-source-title').innerText(), ui[language].title);
        assert.deepEqual(await page.locator('.ddj-source-text p').allTextContents(), data.chapters[41].paragraphs);
        await checkLayout(page, width, language);
        await page.locator('.ddj-source-details summary').click();
        assert.ok((await page.locator('.ddj-source-details').innerText()).includes(ui[language].chapter_notes['42']));
        checks++;
      }
    }
    // Static content is available even if the language-switching JS is disabled.
    const staticContext = await browser.newContext({javaScriptEnabled:false});
    await staticContext.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin ? route.continue() : route.abort());
    const staticPage = await staticContext.newPage();
    await staticPage.goto(`${base}/essays/daodejing/ch28.html`, {waitUntil:'load'});
    assert.equal(await staticPage.locator('.ddj-source-text p:visible').count(), 4);
    assert.equal(await staticPage.locator('#ddj-source-title').innerText(), ui.zh.title);
    assert.deepEqual(errors, []);
    console.log(`OK: ${checks} language/viewport checks, preserved text, keyboard details, and no-JS reading`);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });

async function checkLayout(page, width, label) {
  const bounds = await page.evaluate(() => {
    const rect = selector => {
      const b = document.querySelector(selector).getBoundingClientRect();
      return {top:b.top, bottom:b.bottom, left:b.left, right:b.right};
    };
    const source = rect('.ddj-source');
    const text = rect('.ddj-source-text');
    const header = rect('.essay-header');
    const body = [...document.querySelectorAll('.essay-body')].find(el => getComputedStyle(el).display !== 'none').getBoundingClientRect();
    return {source, text, header, bodyTop:body.top};
  });
  assert.ok(bounds.source.top >= bounds.header.bottom - 1, `${label}: source overlaps title`);
  assert.ok(bounds.bodyTop >= bounds.source.bottom - 1, `${label}: essay overlaps source`);
  assert.ok(bounds.text.left >= 0 && bounds.text.right <= width + 1, `${label}: quotation overflows viewport`);
}
