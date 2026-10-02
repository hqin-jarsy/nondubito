const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const receipt = JSON.parse(fs.readFileSync(path.join(root, 'data/emperor-full/new-edition-review.json')));
const base = process.argv[2] || 'http://127.0.0.1:8774';
const labels = {de:'Deutsch',fr:'Français',es:'Español',ja:'日本語',ko:'한국어'};
(async () => {
  const browser = await chromium.launch({headless:true,channel:'chrome'});
  try {
    const context = await browser.newContext();
    await context.route('**/*',r => new URL(r.request().url()).origin === new URL(base).origin ? r.continue() : r.abort());
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror',e => errors.push(e.message));
    let checked = 0;
    for (const width of [1440,390,320]) {
      await page.setViewportSize({width,height:950});
      for (const [key,record] of Object.entries(receipt.manuscripts)) {
        const [ep,lang] = key.split('.');
        await page.goto(`${base}/essays/emperor/${lang}/${ep}.html`);
        assert.equal(await page.locator('h1').innerText(),record.title);
        assert.equal(await page.locator('.full-edition > h2').count(),record.blocks_by_section.length-1);
        assert.equal(await page.locator('.full-edition > p, .full-edition > ul > li, .full-edition > ol > li').count(),record.blocks_by_section.reduce((a,b)=>a+b,0),key);
        assert.equal(await page.locator('.lang-btn').count(),8,key);
        assert.equal((await page.locator('.lang-btn.active').textContent()).trim(),labels[lang],key);
        const layout = await page.evaluate(() => ({width:document.documentElement.scrollWidth,
          title:document.querySelector('h1').getBoundingClientRect().bottom,
          body:document.querySelector('.full-edition').getBoundingClientRect().top,
          bodyWidth:document.querySelector('.full-edition').getBoundingClientRect().width}));
        assert.ok(layout.width<=width+1,`${key} ${width}: overflow ${layout.width}`);
        assert.ok(layout.body>=layout.title,`${key}: title/body overlap`);
        assert.ok(layout.bodyWidth>width*.55||width===1440,`${key}: cramped body`);
        if(process.env.EMPEROR_SCREENSHOTS && ((width===1440&&ep==='ep01'&&lang==='fr') || (width===390&&ep==='ep25'&&lang==='ja') || (width===320&&ep==='ep12'&&lang==='ko'))) {
          await page.screenshot({path:path.join(process.env.EMPEROR_SCREENSHOTS,`${key}-${width}.png`)});
        }
        checked++;
      }
      for(const lang of Object.keys(labels)) {
        await page.goto(`${base}/essays/emperor/${lang}/index.html`);
        assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth)<=width+1,`${lang} index overflow`);
        assert.equal(await page.locator('a.collection-card, a.essay-card').count(),25);
      }
    }
    console.log(`Layout complete: ${checked} article/viewport checks and 15 indexes`);
    await page.goto(`${base}/essays/emperor/fr/ep01.html`);
    await page.locator('a.lang-btn').filter({hasText:'한국어'}).click();
    await page.waitForURL('**/ko/ep01.html');
    await page.locator('nav a[href="ep02.html"]').click();
    await page.waitForURL('**/ko/ep02.html');
    await page.locator('a.lang-btn').filter({hasText:'中文'}).click();
    await page.waitForURL(/\/emperor\/ep02\.html\?lang=zh$/);
    assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
    await page.goto(`${base}/essays/emperor/ep12.html?lang=zh`);
    await page.locator('button.lang-btn[data-lang="zh-hant"]').click();
    assert.ok((await page.locator('.essay-body.lang-zh').innerText()).includes('諸葛亮就來自官宦之家'));
    await page.locator('button.lang-btn[data-lang="en"]').click();
    assert.ok((await page.locator('.essay-body.lang-en').innerText()).includes('belonged to an official family'));
    const nojs = await browser.newContext({javaScriptEnabled:false});
    await nojs.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
    const staticPage=await nojs.newPage();
    for(const lang of Object.keys(labels)) {
      await staticPage.goto(`${base}/essays/emperor/${lang}/ep01.html`);
      assert.ok(await staticPage.locator('.full-edition p').count()>50);
      assert.equal(await staticPage.locator('.lang-btn').count(),8);
    }
    assert.deepEqual(errors,[]);
    console.log(`OK: ${checked} article/viewport checks, 15 indexes, language/next links, corrected EN/Hant, five no-JS editions`);
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});
