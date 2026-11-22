/* Isolated local browser only; run after building theatre and discovery data. */
const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const works = JSON.parse(fs.readFileSync(path.join(__dirname,'../data/theatre/catalog.json'),'utf8')).works;
const sharedLanguages = ['en','zh','zh-hant'];
const foreignLanguages = ['ja','fr','de','es','ko'];
const expanded = works.filter(w => w.editions_added === '2026-11-22').map(w => w.slug);
assert.equal(expanded.length, 3);
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
      await page.route('https://static.cloudflareinsights.com/**', route => route.abort());
      for (const route of ['index.html',...works.map(w=>`${w.slug}.html`)]) {
        const work = works.find(w => `${w.slug}.html` === route);
        for (const lang of (work?.languages || sharedLanguages).filter(lang => sharedLanguages.includes(lang))) {
          const response = await page.goto(`${base}/essays/theatre/${route}?lang=${lang}`);
          assert.ok(response.ok());
          await page.waitForFunction(l => document.documentElement.dataset.lang === l, lang);
          assert.equal(await page.locator('main h1:visible').count(),1);
          for (const [key, cls] of [['en','en'],['zh','zh'],['zh-hant','hant']]) {
            if (key !== lang) assert.equal(await page.locator(`main .lang-${cls}:visible`).count(),0);
          }
          assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
          if (route !== 'index.html') {
            assert.equal(await page.locator('.rf-article-hero').evaluate(el => getComputedStyle(el).position), 'static');
            assert.ok(await page.locator('article.rf-prose:visible h2').count() >= 3);
            assert.ok((await page.locator('article.rf-prose:visible').innerText()).length > 3000);
          } else {
            assert.equal(await page.locator('.rf-book-card').count(),works.length);
          }
          if (shots && lang === 'zh' && ['index.html','a-man-of-no-importance.html','once-on-this-island.html','the-secret-garden.html'].includes(route)) await page.screenshot({path:`${shots}/${width}-${route}.png`,fullPage:false});
          if (shots && lang === 'zh' && route === 'index.html') {
            await page.locator('.rf-book-card[href="the-last-five-years.html"]').scrollIntoViewIfNeeded();
            await page.screenshot({path:`${shots}/${width}-new-chinese-cards.png`,fullPage:false});
          }
          checks++;
        }
      }
      for (const lang of foreignLanguages) {
        const response = await page.goto(`${base}/essays/theatre/${lang}/index.html`);
        assert.ok(response.ok());
        assert.equal(await page.locator('.essay-card').count(),23);
        for (const slug of expanded) {
          await page.locator(`.essay-card[href="${slug}.html"]`).click();
          await page.waitForURL(`**/theatre/${lang}/${slug}.html`);
          assert.equal(await page.locator('html').getAttribute('lang'),lang);
          assert.equal(await page.locator('.lang-toggle a').count(),8);
          assert.ok(await page.locator('.essay-body h2').count() >= 5);
          assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1));
          await page.locator('.lang-toggle a[lang="zh-Hant"]').click();
          await page.waitForFunction(() => document.documentElement.dataset.lang === 'zh-hant');
          assert.equal(await page.locator('article.rf-prose.lang-hant:visible').count(),1);
          if (width < 600) {
            await page.locator('[data-site-shell-menu]').click();
            await page.locator(`.site-shell-mobile-languages a[lang="${lang}"]`).click();
          } else {
            await page.locator('.site-shell-language summary').click();
            await page.locator(`.site-shell-language a[lang="${lang}"]`).click();
          }
          await page.waitForURL(`**/theatre/${lang}/${slug}.html`);
          await page.locator('.back-link').click();
          await page.waitForURL(`**/theatre/${lang}/index.html`);
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
      // An English reader follows a Chinese-only card. Do not hide its body,
      // advertise nonexistent editions, or silently replace the site preference.
      await page.evaluate(() => localStorage.setItem('nd_lang','en'));
      await page.goto(`${base}/essays/theatre/a-man-of-no-importance.html?lang=en`);
      await page.waitForFunction(() => document.documentElement.dataset.lang === 'zh');
      assert.equal(await page.locator('article.rf-prose:visible').count(),1);
      assert.equal(await page.locator('article.lang-en').count(),0);
      assert.equal(await page.evaluate(() => localStorage.getItem('nd_lang')),'en');
      assert.equal(await page.locator('nav[aria-label="Other editions"]').count(),0);
      await page.reload();
      assert.equal(await page.evaluate(() => localStorage.getItem('nd_lang')),'en');
      assert.equal(await page.locator('article.lang-zh:visible').count(),1);
      if (width < 600) {
        await page.locator('[data-site-shell-menu]').click();
        assert.equal(await page.locator('.site-shell-mobile-languages [data-set-language="en"]:visible').count(),0);
        await page.locator('.site-shell-mobile-languages [data-set-language="zh-hant"]').click();
      } else {
        await page.locator('.site-shell-language summary').click();
        assert.equal(await page.locator('.site-shell-language [data-set-language="en"]:visible').count(),0);
        await page.locator('.site-shell-language [data-set-language="zh-hant"]').click();
      }
      await page.waitForFunction(() => document.documentElement.dataset.lang === 'zh-hant');
      await page.reload();
      assert.equal(await page.locator('article.lang-hant:visible').count(),1);
      assert.equal(await page.evaluate(() => localStorage.getItem('nd_lang')),'zh-hant');
      await page.goto(`${base}/essays/theatre/hamilton.html?lang=en`);
      assert.equal(await page.locator('article.lang-en:visible').count(),1);
      checks++;
      for (const route of ['index.html','explore.html','library.html','latest.html']) {
        await page.goto(`${base}/${route}?lang=zh`);
        assert.ok(await page.locator('a[href="essays/theatre/index.html"]:visible').count() > 0, route);
      }
      for (const [query,slug,lang] of [['Hamilton','hamilton','en'],['西区故事','west-side-story','zh'],['樂隊來訪','the-bands-visit','zh-hant'],['Falsettos','falsettos','en'],['他们天天见面','a-man-of-no-importance','zh'],['牆倒了','once-on-this-island','zh-hant'],['舞动人生','billy-elliot','zh']]) {
        await page.goto(`${base}/search.html?q=${encodeURIComponent(query)}&lang=${lang}`);
        await page.waitForSelector(`a[href*="essays/theatre/${slug}.html"]`);
        checks++;
      }
      await context.close();
    }
    assert.deepEqual(errors,[]);
    console.log(`OK: ${checks} theatre browser scenarios, eight languages, mobile/desktop, navigation and search`);
  } finally { await browser.close(); }
})().catch(e => {console.error(e); process.exit(1);});
