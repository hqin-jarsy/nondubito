/* Run against the local preview: NODE_PATH=<runtime modules> node this-file. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');

(async () => {
  const base = process.env.PALEO_PREVIEW_URL || 'http://127.0.0.1:8786';
  const browser = await chromium.launch({channel:'chrome', headless:true});
  try {
    const context = await browser.newContext();
    await context.route('**/*', route => route.request().url().startsWith(base) ? route.continue() : route.abort());
    const page = await context.newPage();
    const errors = []; page.on('pageerror', e => errors.push(e.message));
    let checks = 0;
    for (const width of [375, 768, 1440]) {
      await page.setViewportSize({width, height:900});
      for (const lang of ['', 'en/', 'zh-hant/', 'de/', 'fr/', 'es/', 'ja/', 'ko/']) {
        for (const filename of ['index.html', ...Array.from({length:8}, (_, i) => `ep${String(i + 1).padStart(2,'0')}.html`)]) {
          const response = await page.goto(`${base}/essays/paleontology/${lang}${filename}`);
          assert.equal(response.status(), 200);
          assert.equal(await page.locator('h1').count(), 1);
          assert.equal(await page.locator('h1').isVisible(), true);
          assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, `${lang}${filename} ${width}`);
          await page.locator('.language-menu summary').click();
          assert.equal(await page.locator('.language-menu nav a:visible').count(), 8);
          assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true);
          const active = page.locator('.language-menu a[aria-current="page"]');
          assert.equal(await active.count(), 1);
          assert((await active.getAttribute('href')).endsWith(filename));
          await page.locator('.language-menu summary').click();
          if (filename !== 'index.html') {
            assert.equal(await page.locator('article.prose > h2').count(), 8);
            await page.locator('.contents summary').click();
            await page.locator('.contents a[href="#section-8"]').click();
            assert(page.url().endsWith('#section-8'));
          }
          checks++;
        }
      }
    }
    for (const target of ['library.html', 'latest.html']) {
      await page.goto(`${base}/${target}?lang=en`);
      const link = page.locator('a[data-edition-en="essays/paleontology/en/index.html"]').first();
      assert.equal(await link.getAttribute('href'), 'essays/paleontology/en/index.html');
      await page.locator('.site-shell-language summary').click();
      await page.locator('.site-shell-language [data-set-language="zh-hant"]').click();
      assert.equal(await link.getAttribute('href'), 'essays/paleontology/zh-hant/index.html');
      await page.locator('.site-shell-language summary').click();
      await page.locator('.site-shell-language [data-set-language="zh"]').click();
      assert.equal(await link.getAttribute('href'), 'essays/paleontology/index.html');
    }
    const noJS = await browser.newContext({javaScriptEnabled:false, viewport:{width:390,height:844}});
    const plain = await noJS.newPage();
    await plain.goto(`${base}/essays/paleontology/en/ep05.html`);
    assert.equal(await plain.locator('article.prose > h2').count(), 8);
    await plain.locator('.language-menu summary').click();
    await plain.locator('.language-menu a[lang="ja"]').click();
    assert(plain.url().endsWith('/ja/ep05.html'));
    assert.equal(await plain.locator('article.prose > h2').count(), 8);
    await page.setViewportSize({width:1440,height:1000});
    await page.goto(`${base}/essays/paleontology/index.html`);
    await page.screenshot({path:'/tmp/paleontology-hub-desktop.png', fullPage:true});
    await page.goto(`${base}/essays/paleontology/en/ep05.html`);
    await page.screenshot({path:'/tmp/paleontology-essay-desktop.png'});
    await page.setViewportSize({width:390,height:844});
    await page.goto(`${base}/essays/paleontology/zh-hant/ep08.html`);
    await page.screenshot({path:'/tmp/paleontology-essay-mobile.png'});
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({viewportChecks:checks, menuLinks:'8 per page', libraryAndLatestLanguageLinks:'passed', withoutJavaScript:'passed', pageErrors:errors}));
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode=1; });
