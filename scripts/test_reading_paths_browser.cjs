// Run against a local static server with Playwright available on NODE_PATH.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const base = process.argv[2] || 'http://127.0.0.1:8794';
const routes = [
  ['reading-path-sae', 'Understand SAE without beginning from a system'],
  ['reading-path-care', 'Care without taking over another life'],
  ['reading-path-stories', 'When a work refuses to judge for us'],
];
const languages = ['en', 'zh', 'zh-hant'];

async function verifyTarget(page, id, language = 'en') {
  // Poll from Node so the same check also works with page JavaScript disabled.
  let settled = false;
  const deadline = Date.now() + 10000;
  while (!settled && Date.now() < deadline) {
    settled = await page.evaluate((targetId) => {
      const target = document.getElementById(targetId);
      if (!target) return false;
      const top = target.getBoundingClientRect().top + scrollY;
      const margin = parseFloat(getComputedStyle(target).scrollMarginTop);
      const expected = Math.min(top - margin, document.documentElement.scrollHeight - innerHeight);
      return Math.abs(scrollY - expected) < 2;
    }, id);
    if (!settled) await new Promise(resolve => setTimeout(resolve, 50));
  }
  assert.ok(settled, `Native anchor scroll did not settle: ${id}`);
  const state = await page.evaluate((targetId) => {
    const target = document.getElementById(targetId);
    const style = getComputedStyle(target);
    const rect = target.getBoundingClientRect();
    return {
      hash: location.hash,
      language: document.documentElement.dataset.lang,
      targets: document.querySelectorAll('.route-card:target').length,
      top: rect.top,
      headerBottom: document.querySelector('.site-shell-header').getBoundingClientRect().bottom,
      outlineWidth: style.outlineWidth,
      outlineStyle: style.outlineStyle,
      overflow: document.documentElement.scrollWidth > innerWidth + 1,
    };
  }, id);
  assert.equal(state.hash, `#${id}`);
  assert.equal(state.language, language);
  assert.equal(state.targets, 1);
  assert.equal(state.outlineWidth, '2px');
  assert.equal(state.outlineStyle, 'solid');
  assert.ok(state.top >= state.headerBottom, JSON.stringify(state));
  assert.equal(state.overflow, false);
  assert.equal(await page.locator(`#${id} h3:visible`).count(), 1);
}

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  const errors = [];
  let combinations = 0;
  try {
    const context = await browser.newContext();
    // Keep QA local; do not send analytics or depend on external font loading.
    await context.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin
      ? route.continue() : route.abort());
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));

    for (const width of [1440, 768, 390, 320]) {
      await page.setViewportSize({ width, height: 900 });
      for (const language of languages) {
        for (const [id, heading] of routes) {
          await page.goto(`${base}/index.html?lang=${language}`);
          assert.equal(await page.locator('.home-path[href="essays/ai-work/index.html"]').count(), 1);
          await page.locator(`.home-path[href="explore.html#${id}"]`).click();
          await page.waitForURL(`**/explore.html#${id}`);
          assert.equal(await page.locator(`#${id} h3.lang-en`).textContent(), heading);
          await verifyTarget(page, id, language);
          assert.equal(await page.locator(`#${id}`).getAttribute('tabindex'), '-1');
          await page.keyboard.press('Tab');
          assert.equal(await page.locator(`#${id} .route-list a`).first().evaluate(el => el === document.activeElement), true);
          await page.goBack();
          await page.waitForURL(`**/index.html?lang=${language}`);
          await page.goForward();
          await verifyTarget(page, id, language);
          combinations++;
        }
      }
      console.log(`Passed ${width}px: all three languages and routes, with keyboard and history.`);
    }

    // Direct entry, reload, and repeated clicks all keep native fragment behavior.
    await page.goto(`${base}/explore.html?lang=zh#reading-path-care`);
    await verifyTarget(page, 'reading-path-care', 'zh');
    await page.reload();
    await verifyTarget(page, 'reading-path-care', 'zh');
    await page.goto(`${base}/index.html?lang=zh`);
    for (let repeat = 0; repeat < 2; repeat++) {
      await page.locator('.home-path[href="explore.html#reading-path-care"]').click();
      await verifyTarget(page, 'reading-path-care', 'zh');
      await page.goBack();
    }

    // Switching fragments removes the old highlight; Back/Forward restores it.
    await page.goto(`${base}/explore.html?lang=en#reading-path-sae`);
    await page.evaluate(() => { location.hash = 'reading-path-stories'; });
    await verifyTarget(page, 'reading-path-stories');
    await page.goBack();
    await verifyTarget(page, 'reading-path-sae');
    await page.goForward();
    await verifyTarget(page, 'reading-path-stories');

    // Existing section URLs remain supported, without selecting a route.
    await page.goto(`${base}/explore.html#reading-paths`);
    assert.equal(await page.locator('#reading-paths').count(), 1);
    assert.equal(await page.locator('.route-card:target').count(), 0);

    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto(`${base}/explore.html?lang=zh-hant#reading-path-stories`);
    await verifyTarget(page, 'reading-path-stories', 'zh-hant');
    assert.equal(await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior), 'auto');

    if (process.env.READING_PATH_SCREENSHOTS) {
      fs.mkdirSync(process.env.READING_PATH_SCREENSHOTS, { recursive: true });
      for (const [width, language, id] of [[1440, 'zh', 'reading-path-care'], [390, 'en', 'reading-path-stories'], [320, 'zh-hant', 'reading-path-sae']]) {
        await page.setViewportSize({ width, height: 900 });
        await page.goto(`${base}/explore.html?lang=${language}#${id}`);
        await verifyTarget(page, id, language);
        await page.screenshot({ path: path.join(process.env.READING_PATH_SCREENSHOTS, `${width}-${language}.png`) });
      }
    }

    const nojs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 900 } });
    await nojs.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin
      ? route.continue() : route.abort());
    const nojsPage = await nojs.newPage();
    for (const [id] of routes) {
      await nojsPage.goto(`${base}/index.html`);
      await nojsPage.locator(`.home-path[href="explore.html#${id}"]`).click();
      await verifyTarget(nojsPage, id);
    }
    assert.deepEqual(errors, []);
    console.log(`OK: ${combinations} viewport/language/route combinations; keyboard, Back/Forward, direct entry, reload, repeated clicks, fragment changes, legacy anchor, reduced motion, no-JS, and zero page errors.`);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
