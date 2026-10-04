const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8786';
const items=fs.readdirSync(path.join(__dirname,'../data/hongloumeng/readings')).filter(n=>/^\d\d\.json$/.test(n)).map(n=>JSON.parse(fs.readFileSync(path.join(__dirname,'../data/hongloumeng/readings',n))));
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
  const context=await browser.newContext({reducedMotion:'reduce'});
  await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  let checks=0;
  for(const width of [1440,768,390,320]){
   await page.setViewportSize({width,height:900});
   for(const [dir,lang,htmlLang] of [['','zh','zh-Hans'],['en/','en','en'],['zh-hant/','zh-hant','zh-Hant']]){
    for(const item of items){
     const response=await page.goto(`${base}/essays/literature/hlm/${dir}${item.slug}.html`);
     assert.equal(response.status(),200);
     assert.equal(await page.locator('html').getAttribute('lang'),htmlLang);
     assert.equal(await page.locator('h1:visible').count(),1);
     assert.equal(await page.locator('.reading-prose p').count(),item[lang==='en'?'en':'zh'].sections.reduce((n,s)=>n+s.paragraphs.length,0));
     assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${item.slug}/${lang}/${width}`);
     assert.equal(await page.locator('.reading-sources[open]').count(),0);
     await page.locator('.reading-sources summary').click();
     assert.equal(await page.locator('.reading-sources[open]').count(),1);
     assert.equal(await page.locator('.reading-sources a:visible').count(),item.papers.length);
     assert.equal(await page.locator('.reading-next a').count(),2);
     checks++;
    }
   }
  }
  await page.setViewportSize({width:390,height:900});
  await page.goto(`${base}/essays/literature/hlm/reading-01.html?lang=zh#section-2`);
  await page.locator('.language-menu summary').click();
  await page.locator('[data-edition="en"]').click();
  await page.waitForURL('**/en/reading-01.html?lang=en#section-2');
  assert.equal(await page.locator('html').getAttribute('lang'),'en');
  await page.locator('.reading-next a').last().click();
  await page.waitForURL('**/en/reading-02.html');
  assert.equal(await page.locator('html').getAttribute('lang'),'en');
  await page.evaluate(()=>localStorage.setItem('nd_lang','zh'));
  await page.goto(`${base}/essays/literature/hlm/en/reading-06.html`);
  assert.equal(await page.locator('html').getAttribute('lang'),'en');
  await page.locator('.reading-next a').last().click();
  await page.waitForURL('**/en/index.html?lang=en#readings');
  assert.equal(await page.locator('.reading-card').count(),items.length);
  await page.goto(`${base}/essays/literature/hlm/reading-01.html?lang=zh`);
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:'/private/tmp/hlm-readings-mobile-zh.png'});
  await page.goto(`${base}/essays/literature/hlm/en/reading-06.html`);
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:'/private/tmp/hlm-readings-mobile-en.png'});
  await page.setViewportSize({width:1440,height:1000});
  await page.goto(`${base}/essays/literature/hlm/index.html?lang=zh#readings`);
  await page.locator('#readings').scrollIntoViewIfNeeded();
  await page.screenshot({path:'/private/tmp/hlm-readings-hub.png'});
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:850}});
  await nojs.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const p=await nojs.newPage();await p.goto(`${base}/essays/literature/hlm/reading-01.html`);
  await p.locator('.language-menu summary').click();await p.locator('[data-edition="zh-hant"]').click();
  assert.equal(await p.locator('html').getAttribute('lang'),'zh-Hant');
  await p.locator('.reading-next a').last().click();
  assert.ok(p.url().includes('/zh-hant/reading-02.html'));
  assert.deepEqual(errors,[]);
  console.log(`OK: ${checks} essay/edition/viewport checks; same-essay language switching, anchors, next/back navigation, explicit language URLs, source notes and no-JS reading.`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
