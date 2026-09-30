/* All five complete editions at desktop/mobile widths; no external requests. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const receipt = JSON.parse(fs.readFileSync(path.join(root, 'data/economy-full/review.json')));
const base = process.argv[2] || 'http://127.0.0.1:8774';
(async () => {
  const browser = await chromium.launch({headless:true, channel:'chrome'});
  try {
    const context = await browser.newContext();
    await context.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin ? route.continue() : route.abort());
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    let checks = 0;
    for (const width of [1440, 390, 320]) {
      await page.setViewportSize({width,height:950});
      for (const [key, record] of Object.entries(receipt.manuscripts)) {
        const [ep,lang] = key.split('.');
        if (width === 320 && !['ep01','ep16','ep23'].includes(ep)) continue;
        await page.goto(`${base}/essays/economy/${lang}/${ep}.html`, {waitUntil:'load'});
        assert.equal(await page.locator('h1').innerText(),record.title);
        assert.equal(await page.locator('.economy-full h2').count(),8);
        assert.equal(await page.locator('.economy-full p').count(),record.paragraphs_by_section.reduce((a,b)=>a+b,0));
        assert.equal(await page.locator('.lang-select option:checked').innerText(),{de:'Deutsch',fr:'Français',es:'Español',ja:'日本語',ko:'한국어'}[lang]);
        const layout = await page.evaluate(() => ({scroll:document.documentElement.scrollWidth, header:document.querySelector('.essay-header').getBoundingClientRect().bottom, toc:document.querySelector('.economy-toc').getBoundingClientRect().top}));
        assert.ok(layout.scroll <= width+1, `${key} at ${width}: overflow ${layout.scroll}`);
        assert.ok(layout.toc >= layout.header-1, `${key}: header overlaps contents`);
        if (['ep01','ep16','ep23'].includes(ep)) {
          await page.locator('.economy-toc summary').focus();
          await page.keyboard.press('Enter');
          assert.equal(await page.locator('.economy-toc').getAttribute('open'),'');
          await page.locator('.economy-toc a').last().click();
          assert.ok(page.url().endsWith('#section-8'));
          await page.locator('h1').scrollIntoViewIfNeeded();
          if (process.env.ECONOMY_SCREENSHOTS && ((ep==='ep01' && lang==='fr' && width===1440) || (ep==='ep16' && lang==='ja' && width===390))) {
            await page.screenshot({path:path.join(process.env.ECONOMY_SCREENSHOTS,`${ep}-${lang}-${width}.png`)});
          }
        }
        checks++;
      }
    }
    await page.goto(`${base}/essays/economy/de/ep17.html`);
    await page.locator('.lang-select').selectOption({label:'한국어'});
    await page.waitForURL('**/ko/ep17.html');
    await page.locator('.series-nav .next').click();
    await page.waitForURL('**/ko/ep18.html');
    await page.locator('.lang-select').selectOption({label:'中文'});
    await page.waitForURL('**/economy/ep18.html');
    assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
    const staticContext = await browser.newContext({javaScriptEnabled:false});
    await staticContext.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
    const staticPage = await staticContext.newPage();
    for (const lang of ['de','fr','es','ja','ko']) {
      await staticPage.goto(`${base}/essays/economy/${lang}/ep23.html`);
      assert.equal(await staticPage.locator('.economy-full h2').count(),8);
      assert.ok((await staticPage.locator('.economy-full').innerText()).length>15000);
      assert.equal(await staticPage.locator('.lang-toggle .lang-btn').count(),7);
    }
    assert.deepEqual(errors,[]);
    console.log(`OK: ${checks} article/viewport checks; contents, language switching, next article and five no-JS editions`);
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
