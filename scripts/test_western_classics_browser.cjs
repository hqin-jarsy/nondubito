/* Real-browser publication checks, with remote assets disabled. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname,'..');
const origin = process.env.ND_TEST_ORIGIN || 'http://127.0.0.1:8786';
const series = ['sae-descartes','sae-spinoza'];
const pages = [];
for (const slug of series) {
  pages.push({url:`essays/${slug}/index.html`});
  for (const name of fs.readdirSync(path.join(root,'data',slug)).filter(n=>/^\d\d\.json$/.test(n))) {
    const item=JSON.parse(fs.readFileSync(path.join(root,'data',slug,name)));
    pages.push({url:`essays/${slug}/${item.slug}.html`,item});
  }
}
(async()=>{
  const browser=await chromium.launch({channel:'chrome',headless:true});
  try {
    const context=await browser.newContext();
    await context.route('**/*', route=>route.request().url().startsWith(origin+'/')?route.continue():route.abort());
    await context.addInitScript(()=>{
      Object.defineProperty(window,'localStorage',{get(){throw new Error('storage disabled for test');}});
    });
    const page=await context.newPage();
    const errors=[];
    page.on('pageerror',error=>errors.push(String(error)));
    let checks=0;
    for (const width of [390,768,1440]) {
      await page.setViewportSize({width,height:900});
      for (const entry of pages) for (const lang of ['en','zh','zh-hant']) {
        const response=await page.goto(`${origin}/${entry.url}?lang=${lang}`,{waitUntil:'load'});
        assert.equal(response.status(),200);
        assert.equal(await page.locator('main h1:visible').count(),1);
        assert.equal(await page.locator('.western-prose:visible').count(),entry.item?1:0);
        const actual=await page.evaluate(()=>({lang:document.documentElement.dataset.lang,
          overflow:document.documentElement.scrollWidth-innerWidth,
          main:document.querySelector('main').getBoundingClientRect().top,
          header:document.querySelector('header').getBoundingClientRect().bottom}));
        assert.equal(actual.lang,lang);
        assert.ok(actual.overflow<=1,JSON.stringify({entry:entry.url,width,lang,...actual}));
        assert.ok(actual.main>=actual.header-1,JSON.stringify({entry:entry.url,width,lang,...actual}));
        if (entry.item) {
          const copy=entry.item[lang==='en'?'en':'zh'];
          assert.equal(await page.locator('.western-prose:visible p').count(),copy.sections.reduce((n,s)=>n+s.paragraphs.length,0));
          assert.equal(await page.locator('details.western-sources[open]').count(),0);
          await page.locator('details.western-sources summary').click();
          assert.equal(await page.locator('details.western-sources[open]').count(),1);
          assert.ok((await page.locator('.western-series-nav a').first().getAttribute('href')).includes(`lang=${lang}`));
        } else {
          const boxes=await page.locator('.western-entry').evaluateAll(es=>es.map(e=>({n:e.querySelector('.western-number').getBoundingClientRect().right,t:e.querySelector('div').getBoundingClientRect().left})));
          assert.ok(boxes.every(b=>b.n<=b.t),JSON.stringify(boxes));
        }
        checks++;
      }
    }
    await page.setViewportSize({width:390,height:900});
    await page.goto(`${origin}/essays/sae-descartes/ep05.html?lang=zh`);
    await page.locator('[data-site-shell-menu]').click();
    await page.locator('.site-shell-mobile-languages [data-set-language="en"]').click();
    assert.equal(await page.locator('html').getAttribute('data-lang'),'en');
    await page.screenshot({path:'/private/tmp/western-classics-mobile.png'});
    await page.locator('.western-series-nav a').last().click();
    assert.ok(page.url().includes('ep06.html?lang=en'));
    await page.locator('[data-site-shell-menu]').click();
    assert.equal(await page.locator('[data-site-shell-menu]').getAttribute('aria-expanded'),'true');
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('[data-site-shell-menu]').getAttribute('aria-expanded'),'false');
    await page.setViewportSize({width:1440,height:1000});
    await page.goto(`${origin}/essays/sae-spinoza/ep01.html?lang=zh-hant`);
    await page.screenshot({path:'/private/tmp/western-classics-desktop.png'});
    await page.locator('.site-shell-language-summary').click();
    await page.locator('.site-shell-language [data-set-language="en"]').click();
    assert.equal(await page.locator('html').getAttribute('data-lang'),'en');
    assert.deepEqual(errors,[]);
    console.log(`OK: ${checks} page/language/viewport combinations; language switching, storage-free navigation, notes and mobile menu`);
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
