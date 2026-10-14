/* Isolated local browser only; run after building theatre and discovery data. */
const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const base = process.argv[2] || 'http://127.0.0.1:8788';
const shots = process.env.THEATRE_SCREENSHOTS;
(async () => {
  const browser = await chromium.launch({channel:'chrome', headless:true});
  const errors = [];
  let checks = 0;
  try {
    for (const width of [390, 1440]) {
      const context = await browser.newContext({viewport:{width,height:900}});
      const page = await context.newPage();
      page.on('pageerror', e => errors.push(e.message));
      await page.route('https://fonts.googleapis.com/**', route => route.abort());
      await page.route('https://fonts.gstatic.com/**', route => route.abort());
      for (const route of ['index.html','hamilton.html']) {
        for (const lang of ['en','zh','zh-hant']) {
          const response = await page.goto(`${base}/essays/theatre/${route}?lang=${lang}`);
          assert.ok(response.ok());
          await page.waitForFunction(l => document.documentElement.dataset.lang === l, lang);
          assert.equal(await page.locator('main h1:visible').count(),1);
          for (const [key, cls] of [['en','en'],['zh','zh'],['zh-hant','hant']]) {
            if (key !== lang) assert.equal(await page.locator(`main .lang-${cls}:visible`).count(),0);
          }
          assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
          if (route === 'hamilton.html') {
            assert.equal(await page.locator('.rf-article-hero').evaluate(el => getComputedStyle(el).position), 'static');
            assert.equal(await page.locator('article.rf-prose:visible h2').count(),4);
            assert.ok((await page.locator('article.rf-prose:visible').innerText()).length > 3000);
          }
          if (shots && lang === 'zh') await page.screenshot({path:`${shots}/${width}-${route}.png`,fullPage:false});
          checks++;
        }
      }
      await page.goto(`${base}/essays/theatre/hamilton.html?lang=zh`);
      if (width < 600) {
        await page.locator('[data-site-shell-menu]').click();
        await page.locator('.site-shell-mobile-languages [data-set-language="en"]').click();
      } else {
        await page.locator('.site-shell-language summary').click();
        await page.locator('.site-shell-language [data-set-language="en"]').click();
      }
      await page.waitForFunction(() => document.documentElement.dataset.lang === 'en');
      assert.equal(new URL(page.url()).searchParams.get('lang'),'en');
      await page.reload();
      assert.equal(await page.locator('article.lang-en:visible').count(),1);
      checks++;
      for (const route of ['index.html','explore.html','library.html','latest.html']) {
        await page.goto(`${base}/${route}?lang=zh`);
        assert.ok(await page.locator('a[href="essays/theatre/index.html"]:visible').count() > 0, route);
      }
      await page.goto(`${base}/search.html?q=Hamilton&lang=zh`);
      await page.waitForSelector('a[href*="essays/theatre/hamilton.html"]');
      checks++;
      await context.close();
    }
    assert.deepEqual(errors,[]);
    console.log(`OK: ${checks} theatre browser scenarios, EN/Hans/Hant, mobile/desktop, navigation and search`);
  } finally { await browser.close(); }
})().catch(e => {console.error(e); process.exit(1);});
