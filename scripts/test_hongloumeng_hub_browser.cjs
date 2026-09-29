const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8776';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
  const ctx=await browser.newContext();
  await ctx.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  let checks=0;
  for(const width of [1440,768,390,320]){
   await page.setViewportSize({width,height:900});
   for(const [dir,lang] of [['','zh'],['en/','en'],['zh-hant/','zh-hant']]){
    await page.goto(`${base}/essays/literature/hlm/${dir}index.html?lang=${lang}`);
    assert.equal(await page.locator('h1:visible').count(),1);
    assert.equal(await page.locator('.paper').count(),3);
    assert.equal(await page.locator('.catalog a').count(),48);
    assert.equal(await page.locator('#continuation a').count(),0);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    await page.locator('.language-menu summary').focus();await page.keyboard.press('Enter');
    assert.equal(await page.locator('[data-edition]:visible').count(),3);
    await page.keyboard.press('Escape');assert.equal(await page.locator('.language-menu[open]').count(),0);
    await page.locator('#zhengce summary').click();
    assert.equal(await page.locator('#zhengce a:visible').count(),10);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    checks++;
   }
  }
  await page.goto(`${base}/essays/literature/hlm/index.html?lang=zh#zhengce`);
  assert.equal(await page.locator('#zhengce[open]').count(),1);
  await page.locator('.language-menu summary').click();await page.locator('[data-edition="en"]').click();
  await page.waitForURL('**/en/index.html?lang=en#zhengce');
  assert.equal(await page.locator('#zhengce[open]').count(),1);
  await page.locator('#zhengce a').first().click();
  assert.equal(await page.locator('html').getAttribute('data-lang'),'en');
  await page.goto(`${base}/essays/literature/hlm/index.html?lang=zh-hant#characters`);
  await page.waitForURL('**/zh-hant/index.html?lang=zh-hant#characters');
  await page.locator('.featured a').first().click();
  assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
  if(process.env.HLM_SCREENSHOTS){
   for(const [name,width,dir,lang] of [['desktop',1440,'','zh'],['english',390,'en/','en'],['traditional',390,'zh-hant/','zh-hant']]){
    await page.setViewportSize({width,height:900});
    await page.goto(`${base}/essays/literature/hlm/${dir}index.html?lang=${lang}`);
    await page.screenshot({path:path.join(process.env.HLM_SCREENSHOTS,name+'.png'),fullPage:true});
   }
  }
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:850}});
  await nojs.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const p=await nojs.newPage();await p.goto(`${base}/essays/literature/hlm/index.html`);
  await p.locator('.language-menu summary').click();await p.locator('[data-edition="en"]').click();
  assert.equal(await p.locator('html').getAttribute('lang'),'en');
  await p.locator('#zhengce summary').click();assert.equal(await p.locator('#zhengce a:visible').count(),10);
  assert.deepEqual(errors,[]);
  console.log(`OK: ${checks} viewport/edition checks; language menu, original anchors, article language, 48 links, unreleased manuscript and no-JS hub.`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
