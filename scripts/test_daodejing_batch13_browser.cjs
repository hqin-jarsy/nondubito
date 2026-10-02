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
const receipt = JSON.parse(fs.readFileSync(path.join(root, 'data/daodejing-full/batch13-review.json')));
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
      for (const number of [61, 62, 63, 64, 65, 66, 67, 68, 69, 70]) {
        const chapter = `ch${number}`;
        const dictionary = fs.readFileSync(path.join(root, `essays/daodejing/zh-hant-data/${chapter}.js`), 'utf8');
        const variants = JSON.parse(dictionary.match(/var variants = (\{.*\});/)[1]);
        let simplifiedNodes;
        await page.goto(`${base}/essays/daodejing/${chapter}.html`, {waitUntil:'load'});
        for (const language of ['zh', 'zh-hant', 'en', 'zh']) {
          await page.locator(`.lang-btn[data-lang="${language}"]`).click();
          await page.waitForFunction(lang => document.documentElement.getAttribute('data-lang') === lang && document.documentElement.lang === ({zh:'zh-Hans', 'zh-hant':'zh-Hant', en:'en'}[lang]), language);
          await check(page, width, number, language);
          assert.equal(await page.locator('.essay-body:visible').count(), 1);
          const manuscriptLanguage = language === 'zh-hant' ? 'zh' : language;
          assert.equal(await page.locator('.essay-body:visible h2').count(), receipt.manuscripts[`${chapter}.${manuscriptLanguage}`].sections);
          if (language !== 'zh-hant') {
            assert.equal(await page.locator('h1:visible').innerText(), receipt.manuscripts[`${chapter}.${language}`].title);
            if (language === 'zh') {
              simplifiedNodes = await page.locator('.essay-body.lang-zh').evaluate(body => {
                const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT);
                const values = [];
                let node;
                while ((node = walker.nextNode())) values.push(node.nodeValue);
                return values;
              });
            }
          } else {
            assert.ok((await page.locator('.essay-body:visible').getAttribute('class')).includes('lang-zh'));
            assert.ok(simplifiedNodes.some(value => variants[value] && variants[value] !== value));
            assert.equal(await page.locator('.essay-body:visible').textContent(),
              simplifiedNodes.map(value => variants[value] || value).join(''));
            const title = receipt.manuscripts[`${chapter}.zh`].title;
            assert.equal(await page.locator('h1:visible').innerText(), variants[title] || title);
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
        if (process.env.DDJ_SCREENSHOTS && ((number === 61 && width === 1440) || (number === 70 && width === 390))) {
          await page.screenshot({path:path.join(process.env.DDJ_SCREENSHOTS, `${chapter}-zh-${width}.png`)});
        }
        for (const language of ['ja','ko','de','fr','es']) {
          await page.goto(`${base}/essays/daodejing/${language}/${chapter}.html`, {waitUntil:'load'});
          await check(page, width, number, language);
          assert.equal(await page.locator('h1').innerText(), receipt.manuscripts[`${chapter}.${language}`].title);
          assert.equal(await page.locator('.essay-body h2').count(), receipt.manuscripts[`${chapter}.${language}`].sections);
          assert.equal(await page.locator('.lang-btn.active').count(), 1);
          if (process.env.DDJ_SCREENSHOTS && width === 390 && number === 69 && language === 'fr') {
            await page.screenshot({path:path.join(process.env.DDJ_SCREENSHOTS, 'ch69-fr-mobile.png')});
          }
          checks++;
        }
      }
    }
    const staticContext = await browser.newContext({javaScriptEnabled:false});
    await staticContext.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin ? route.continue() : route.abort());
    const staticPage = await staticContext.newPage();
    await staticPage.goto(`${base}/essays/daodejing/ch70.html`, {waitUntil:'load'});
    assert.ok((await staticPage.locator('.essay-body:visible').innerText()).length > 1000);
    assert.deepEqual(await staticPage.locator('.ddj-source-text p').allTextContents(), data.chapters[69].paragraphs);
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
