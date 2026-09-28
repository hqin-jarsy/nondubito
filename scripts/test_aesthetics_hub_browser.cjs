const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8776';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
  const ctx=await browser.newContext();
  await ctx.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await ctx.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  let count=0;
  for(const width of [1440,768,390,320]){
   await page.setViewportSize({width,height:900});
   for(const [dir,lang] of [['','zh'],['en/','en'],['zh-hant/','zh-hant']]){
    for(const file of ['index.html','seeing-beauty.html']){
     await page.goto(`${base}/essays/aesthetics/${dir}${file}?lang=${lang}`);
     assert.equal(await page.locator('h1:visible').count(),1);
     assert.equal(await page.locator('.aesthetics-header').count(),1);
     assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${width} ${dir}${file}`);
     await page.locator('.language-menu summary').focus();await page.keyboard.press('Enter');
     assert.equal(await page.locator('[data-edition]:visible').count(),3);
     await page.locator('.language-menu summary').click();
     if(file==='index.html'){
      assert.equal(await page.locator('.recent-list>a').count(),6);
      assert.equal(await page.locator('.paper-map[open]').count(),0);
      await page.locator('.paper-map summary').click();assert.equal(await page.locator('.ray-list a:visible').count(),13);
      await page.locator('#archive>summary').click();await page.locator('.month>summary').first().click();
      assert.ok(await page.locator('.archive-list a:visible').count()>0);
     }else{
      assert.equal(await page.locator('.prose h2').count(),6);
      await page.locator('.contents summary').click();await page.locator('.contents nav a').last().click();
      assert.ok(page.url().endsWith('#section-6'));
     }
     count++;
    }
   }
  }
  await page.goto(`${base}/essays/aesthetics/seeing-beauty.html?lang=zh#section-3`);
  await page.locator('.language-menu summary').click();await page.locator('[data-edition="en"]').click();
  await page.waitForURL('**/en/seeing-beauty.html?lang=en#section-3');
  await page.goto(`${base}/essays/aesthetics/index.html?lang=zh-hant`);
  await page.waitForURL('**/zh-hant/index.html?lang=zh-hant');
  await page.locator('.recent-list a').first().click();
  assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
  if(process.env.AESTHETICS_SCREENSHOTS){
   for(const [name,width,url] of [['desktop',1440,'index.html?lang=zh'],['mobile',390,'en/index.html?lang=en'],['guide',390,'zh-hant/seeing-beauty.html?lang=zh-hant']]){
    await page.setViewportSize({width,height:950});await page.goto(`${base}/essays/aesthetics/${url}`);
    await page.screenshot({path:path.join(process.env.AESTHETICS_SCREENSHOTS,name+'.png'),fullPage:name==='desktop'});
   }
  }
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:850}});
  await nojs.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const p=await nojs.newPage();await p.goto(`${base}/essays/aesthetics/index.html`);
  await p.locator('.language-menu summary').click();await p.locator('[data-edition="en"]').click();
  assert.equal(await p.locator('html').getAttribute('lang'),'en');
  await p.locator('#archive>summary').click();await p.locator('.month>summary').first().click();
  assert.ok(await p.locator('.archive-list a:visible').count()>0);
  await p.locator('#begin .button').click();assert.equal(await p.locator('.prose h2').count(),6);
  assert.deepEqual(errors,[]);console.log(`OK: ${count} viewport/edition/page checks; dropdown, archive, source map, language anchors, legacy fallback and no-JS reading`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
