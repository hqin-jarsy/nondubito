const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base=process.argv[2]||'http://127.0.0.1:8776';
const langs=['zh','zh-hant','en','ja','fr','de','es','ko'];
const article='western-painting/vermeer-woman-holding-a-balance.html';
const url=(lang,file)=>`${base}/essays/art/${lang==='zh'?'':lang+'/'}${file}?lang=${lang}`;
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try {
  const context=await browser.newContext();
  await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  let checks=0;
  for(const width of [1440,768,390,320]) for(const lang of langs) for(const file of ['index.html',article]){
   await page.setViewportSize({width,height:950});await page.goto(url(lang,file));
   assert.equal(await page.locator('h1:visible').count(),1);
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${lang} ${file} ${width}`);
   await page.locator('.language-menu summary').focus();await page.keyboard.press('Enter');
   assert.equal(await page.locator('[data-edition]:visible').count(),8);
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await page.keyboard.press('Escape');assert.equal(await page.locator('.language-menu[open]').count(),0);
   if(file===article){
    assert.equal(await page.locator('figure').count(),4);
    for(const img of await page.locator('figure img').all()){
     await img.scrollIntoViewIfNeeded();await img.evaluate(i=>i.decode());assert.ok(await img.evaluate(i=>i.naturalWidth>0));
    }
    await page.locator('.optional-reading summary').click();assert.ok(await page.locator('.optional-reading .source-note').isVisible());
   }
   checks++;
  }
  await page.goto(url('zh',article)+'#section-4');await page.locator('.language-menu summary').click();await page.locator('[data-edition="fr"]').click();
  await page.waitForURL('**/fr/'+article+'?lang=fr#section-4');
  await page.goto(url('ko',article)+'#section-6');assert.equal(await page.locator('.optional-reading[open]').count(),1);
  for(const [lang,width,name] of [['zh',1440,'desktop'],['ko',390,'mobile'],['en',390,'english']]){
   await page.setViewportSize({width,height:1000});await page.goto(url(lang,article));
   await page.screenshot({path:`/tmp/art-${name}.png`});
  }
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:850}});
  await nojs.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const p=await nojs.newPage();await p.goto(url('zh',article));await p.locator('.language-menu summary').click();await p.locator('[data-edition="ja"]').click();
  assert.equal(await p.locator('html').getAttribute('lang'),'ja');await p.locator('.optional-reading summary').click();assert.ok(await p.locator('.optional-reading .source-note').isVisible());
  assert.deepEqual(errors,[]);console.log(`OK: ${checks} viewport/edition/page checks; images, dropdown, Escape, anchors and no-JS reading`);
 } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exit(1)});
