/* Local-only visual, keyboard, edition and navigation regressions. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
const items=fs.readdirSync(path.join(root,'essays/math-history')).filter(n=>/^ep\d\d\.html$/.test(n)).sort().map(n=>JSON.parse(fs.readFileSync(path.join(root,'data/math-history',n.slice(2,4)+'.json'),'utf8')));
const base=process.argv[2]||'http://127.0.0.1:8774';
const langs=['en','zh','zh-hant'];
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try {
  const context=await browser.newContext();
  await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));let checks=0;
  for(const width of [1440,390,320]) {
   await page.setViewportSize({width,height:950});
   for(const lang of langs) {
    const css=lang==='zh-hant'?'hant':lang;
    await page.goto(`${base}/essays/math-history/index.html?lang=${lang}`);
    assert.equal(await page.locator('main h1:visible').count(),1);
    assert.ok(await page.locator('main h1.lang-'+css).isVisible());
    assert.equal(await page.locator('a.math-card').count(),items.length);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth)<=width+1);
    if(process.env.MATH_SCREENSHOTS && lang==='zh' && [1440,390].includes(width)) {
      await page.screenshot({path:path.join(process.env.MATH_SCREENSHOTS,`math-index-zh-${width}.png`)});
    }
    for(const item of items) {
     const ep='ep'+String(item.id).padStart(2,'0');
     await page.goto(`${base}/essays/math-history/${ep}.html?lang=${lang}`);
     assert.equal(await page.locator('main h1:visible').count(),1);
     assert.equal(await page.locator('.math-prose:visible').count(),1);
     assert.ok(await page.locator('.math-prose.lang-'+css).isVisible());
     assert.equal(await page.locator('.math-prose.lang-'+css+' h2').count(),8);
     assert.ok(await page.locator('.math-prose.lang-'+css+' p').count()>35);
     const layout=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,header:document.querySelector('.math-head').getBoundingClientRect().bottom,toc:document.querySelector('.math-toc').getBoundingClientRect().top}));
     assert.ok(layout.scroll<=width+1,`${ep} ${lang} ${width} overflow`);
     assert.ok(layout.toc>=layout.header,`${ep} overlapping heading`);
     if(item.id===1 && width===390) {
      await page.locator('.math-toc summary').focus();await page.keyboard.press('Enter');
      await page.locator(`.math-toc .lang-${css} a`).last().click();
      assert.ok(page.url().endsWith(`#${css}-section-8`));
     }
     if(process.env.MATH_SCREENSHOTS && item.id===1 && ((lang==='zh'&&width===1440)||(lang==='zh-hant'&&width===390)||(lang==='en'&&width===320))) {
      await page.locator('.math-head').scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(process.env.MATH_SCREENSHOTS,`math-${ep}-${lang}-${width}.png`)});
     }
     checks++;
    }
   }
  }
  await page.setViewportSize({width:1440,height:950});
  await page.goto(`${base}/essays/math-history/ep01.html?lang=en#en-section-3`);
  await page.locator('.site-shell-language > summary').click();
  await page.locator('.site-shell-language [data-set-language="zh-hant"]').click();
  assert.equal(await page.locator('html').getAttribute('data-lang'),'zh-hant');
  assert.ok(page.url().includes('lang=zh-hant'));assert.ok(page.url().endsWith('#hant-section-3'));
  await page.waitForFunction(()=>Math.abs(document.querySelector('#hant-section-3').getBoundingClientRect().top-90)<3,null,{timeout:5000});
  if(items.length>1){await page.locator('.math-series-nav a').last().click();assert.ok(page.url().includes('ep'+String(items[1].id).padStart(2,'0')+'.html'));assert.equal(await page.locator('html').getAttribute('data-lang'),'zh-hant');}
  await page.goto(`${base}/essays/math-history/index.html?lang=en`);await page.locator('.math-topics a').last().click();assert.ok(page.url().endsWith('#purposes'));
  await page.setViewportSize({width:390,height:950});
  await page.goto(`${base}/essays/math-history/ep01.html?lang=en`);
  await page.locator('[data-site-shell-menu]').click();
  await page.locator('.site-shell-mobile-languages [data-set-language="zh"]').click();
  assert.ok(await page.locator('.math-prose.lang-zh').isVisible());
  assert.equal(await page.locator('main h1:visible').textContent(),items[0].title_zh);
  const staticContext=await browser.newContext({javaScriptEnabled:false});
  await staticContext.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const staticPage=await staticContext.newPage();await staticPage.goto(`${base}/essays/math-history/ep01.html`);
  assert.ok(await staticPage.locator('.math-prose.lang-en').isVisible());assert.equal(await staticPage.locator('.math-prose.lang-en h2').count(),8);
  assert.deepEqual(errors,[]);
  console.log(`OK: ${checks} article/language/viewport checks, 9 collection views, keyboard contents, edition persistence, section anchors, neighbors and no-JS English.`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
