/* Run against a local static server. Uses Playwright and installed Chrome.
 * DDJ_SCREENSHOTS=/existing/directory optionally saves desktop/mobile samples.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'data/daodejing-chapter-texts.json')));
const ui = JSON.parse(fs.readFileSync(path.join(root, 'data/daodejing-source-ui.json')));
const receipt = JSON.parse(fs.readFileSync(path.join(root, 'data/daodejing-full/batch11-review.json')));
const base = process.argv[2] || 'http://127.0.0.1:8767';

(async () => {
  const browser = await chromium.launch({headless:true, channel:process.env.DDJ_BROWSER_CHANNEL || 'chrome'});
  try {
    const context = await browser.newContext();
    await context.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin ? route.continue() : route.abort());
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    let checks = 0;
    for (const width of [1440, 390, 320]) {
      await page.setViewportSize({width, height:950});
      for (const number of [51, 52, 53, 54, 55]) {
        const chapter = `ch${number}`;
        await page.goto(`${base}/essays/daodejing/${chapter}.html`, {waitUntil:'load'});
        for (const language of ['zh', 'zh-hant', 'en', 'zh']) {
          await page.locator(`.lang-btn[data-lang="${language}"]`).click();
          await page.waitForFunction(lang => document.documentElement.getAttribute('data-lang') === lang && document.documentElement.lang === ({zh:'zh-Hans', 'zh-hant':'zh-Hant', en:'en'}[lang]), language);
          await check(page, width, number, language);
          if (language !== 'zh-hant') {
            assert.equal(await page.locator('h1:visible').innerText(), receipt.manuscripts[`${chapter}.${language}`].title);
          } else {
            assert.ok(!(await page.locator('.essay-body:visible').innerText()).includes('这'));
          }
          checks++;
        }
        const details = page.locator('.ddj-source-details');
        await details.locator('summary').focus();
        await page.keyboard.press('Enter');
        assert.equal(await details.getAttribute('open'), '');
        assert.ok(await details.locator('a').last().isVisible());
        await page.keyboard.press('Enter');
        assert.equal(await details.getAttribute('open'), null);
        if (process.env.DDJ_SCREENSHOTS && ((number === 51 && width === 1440) || (number === 55 && width === 390))) {
          await page.screenshot({path:path.join(process.env.DDJ_SCREENSHOTS, `${chapter}-zh-${width}.png`)});
        }
        for (const language of ['ja','ko','de','fr','es']) {
          await page.goto(`${base}/essays/daodejing/${language}/${chapter}.html`, {waitUntil:'load'});
          await check(page, width, number, language);
          assert.equal(await page.locator('h1').innerText(), receipt.manuscripts[`${chapter}.${language}`].title);
          assert.equal(await page.locator('.essay-body h2').count(), receipt.manuscripts[`${chapter}.${language}`].sections);
          assert.equal(await page.locator('.lang-btn.active').count(), 1);
          if (process.env.DDJ_SCREENSHOTS && width === 390 && number === 54 && language === 'fr') {
            await page.screenshot({path:path.join(process.env.DDJ_SCREENSHOTS, 'ch54-fr-mobile.png')});
          }
          checks++;
        }
      }
    }
    const staticContext = await browser.newContext({javaScriptEnabled:false});
    await staticContext.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin ? route.continue() : route.abort());
    const staticPage = await staticContext.newPage();
    await staticPage.goto(`${base}/essays/daodejing/ch55.html`, {waitUntil:'load'});
    assert.ok((await staticPage.locator('.essay-body:visible').innerText()).length > 1000);
    assert.deepEqual(await staticPage.locator('.ddj-source-text p').allTextContents(), data.chapters[54].paragraphs);
    assert.deepEqual(errors, []);
    console.log(`OK: ${checks} language/viewport checks across every chapter, source text, keyboard details, no-JS reading`);
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode=1;});

async function check(page, width, number, language) {
  assert.equal(await page.locator('#ddj-source-title').innerText(), ui[language].title);
  assert.deepEqual(await page.locator('.ddj-source-text p').allTextContents(), data.chapters[number-1].paragraphs);
  const bounds = await page.evaluate(() => {
    const box = selector => {
      const b = document.querySelector(selector).getBoundingClientRect();
      return {top:b.top,bottom:b.bottom,left:b.left,right:b.right};
    };
    const body = [...document.querySelectorAll('.essay-body')].find(el => getComputedStyle(el).display !== 'none');
    return {header:box('.essay-header'), source:box('.ddj-source'), text:box('.ddj-source-text'), bodyTop:body.getBoundingClientRect().top, scrollWidth:document.documentElement.scrollWidth};
  });
  assert.ok(bounds.source.top >= bounds.header.bottom-1);
  assert.ok(bounds.bodyTop >= bounds.source.bottom-1);
  assert.ok(bounds.text.left >= 0 && bounds.text.right <= width+1);
  assert.ok(bounds.scrollWidth <= width+1, `${number}/${language}: horizontal overflow`);
}
