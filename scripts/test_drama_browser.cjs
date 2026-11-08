/* Local-only functional and visual-geometry coverage for all complete editions. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8796';
const root=path.resolve(__dirname,'..');
const dir='/essays/everyday/stories/drama/';
const langs=['en','zh','zh-hant','de','fr','es','ja','ko'];
const native=l=>l==='zh'?'zh-Hans':l==='zh-hant'?'zh-Hant':l;
const css=l=>l==='zh-hant'?'hant':l;
const items=Array.from({length:23},(_,i)=>JSON.parse(fs.readFileSync(path.join(root,'data/drama',String(i+1).padStart(2,'0')+'.json'))));
const file=i=>String(i.id).padStart(2,'0')+'-'+i.slug+'.html';
const url=(f,l)=>base+dir+f+'?lang='+l;
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});let views=0,actions=0;const errors=[];
 try{
  const context=await browser.newContext();
  await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  for(const width of [1440,390]){
   await page.setViewportSize({width,height:900});
   for(const f of ['index.html',...items.map(file)]){
    for(const lang of langs){
     const response=await page.goto(url(f,lang),{waitUntil:'domcontentloaded'});assert.equal(response.status(),200);
     assert.equal(await page.locator('html').getAttribute('lang'),native(lang));
     assert.equal(await page.locator('main h1:visible').count(),1);
     assert((await page.locator('main h1:visible').innerText()).trim());
     for(const other of langs.filter(l=>l!==lang))assert.equal(await page.locator('main .lang-'+css(other)+':visible').count(),0,`${f} ${lang} hidden ${other}`);
     assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),true,`${f} ${lang} ${width} overflow`);
     const bread=await page.locator('.drama-breadcrumbs').boundingBox(),header=await page.locator('.site-shell-header').boundingBox();assert(bread.y>=header.y+header.height,`${f} breadcrumb behind fixed header`);
     if(f==='index.html')assert.equal(await page.locator('.drama-card').count(),23);
     else{
      const item=items.find(i=>file(i)===f);const prose=page.locator('.drama-prose.lang-'+css(lang));assert(await prose.isVisible());
      assert.equal(await prose.locator('p').count(),lang==='en'?item.body_en.length:item.body_zh.length);
      assert((await prose.innerText()).length>1800);assert.equal(await page.locator('.drama-series-nav a').count(),2);
     }
     views++;
    }
   }
  }
  // Query, saved state, navigation, copied link and history are consistent in every language.
  await page.setViewportSize({width:1440,height:900});
  for(const lang of langs){
   await page.goto(url(file(items[10]),'en'));
   await page.locator('.site-shell-language summary').click();await page.locator('.site-shell-language [data-set-language="'+lang+'"]').click();actions++;
   assert.equal(new URL(page.url()).searchParams.get('lang'),lang);assert.equal(await page.locator('html').getAttribute('lang'),native(lang));
   assert.equal(await page.locator('.site-shell-language').getAttribute('open'),null);
   await page.reload();assert.equal(await page.locator('html').getAttribute('lang'),native(lang));
   await page.locator('.drama-series-nav a').nth(1).click();actions++;assert.equal(new URL(page.url()).pathname,dir+file(items[11]));assert.equal(await page.locator('html').getAttribute('lang'),native(lang));
   await page.goBack();assert.equal(new URL(page.url()).pathname,dir+file(items[10]));assert.equal(await page.locator('html').getAttribute('lang'),native(lang));
   await page.locator('.drama-breadcrumbs a').last().click();actions++;assert.equal(await page.locator('.drama-card').count(),23);assert.equal(await page.locator('html').getAttribute('lang'),native(lang));
  }
  // Repeated mobile open/dismiss/language flows, including narrow title wrapping.
  await page.setViewportSize({width:320,height:800});await page.goto(url(file(items[0]),'de'));
  const menu=page.locator('[data-site-shell-menu]');
  for(let i=0;i<3;i++){await menu.click();assert.equal(await menu.getAttribute('aria-expanded'),'true');await page.keyboard.press('Escape');assert.equal(await menu.getAttribute('aria-expanded'),'false');actions++;}
  for(const lang of langs){
   await menu.click();await page.locator('.site-shell-mobile-languages [data-set-language="'+lang+'"]').click();actions++;
   assert.equal(await menu.getAttribute('aria-expanded'),'false');assert.equal(await page.locator('html').getAttribute('lang'),native(lang));
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),true);
  }
  // Follow the real header search entry, preserving interface and retrieval language.
  await page.setViewportSize({width:1440,height:900});
  for(const lang of langs){
   await page.goto(url(file(items[0]),lang));const title=await page.locator('main h1:visible').innerText();
   await page.locator('.site-shell-tool').click();actions++;
   await page.waitForFunction(expected=>document.querySelector('[data-search-language]').value===expected,native(lang));
   assert.equal(await page.locator('html').getAttribute('lang'),native(lang));
   await page.locator('[data-search-input]').fill(title);
   const result=page.locator('[data-search-results] a').filter({hasText:title}).first();await result.waitFor({state:'visible'});await result.click();actions++;
   assert.equal(new URL(page.url()).pathname,dir+file(items[0]));assert.equal(await page.locator('html').getAttribute('lang'),native(lang));
  }
  // Search results must carry the selected result language rather than old saved UI state.
  await page.setViewportSize({width:1440,height:900});
  for(const lang of langs){
   await page.goto(url(file(items[0]),lang));const title=await page.locator('main h1:visible').innerText();
   await page.goto(base+'/search.html?lang=en&ui=en&in='+encodeURIComponent(native(lang))+'&q='+encodeURIComponent(title));
   const result=page.locator('[data-search-results] a').filter({hasText:title}).first();await result.waitFor({state:'visible'});await result.click();actions++;
   assert.equal(new URL(page.url()).pathname,dir+file(items[0]));assert.equal(await page.locator('html').getAttribute('lang'),native(lang));
  }
  // Every language hub has a direct language-carrying entry into the series.
  for(const lang of ['de','fr','es','ja','ko']){
   await page.goto(base+'/essays/'+lang+'/index.html');await page.locator('#drama-eight a').click();actions++;
   assert.equal(await page.locator('html').getAttribute('lang'),lang);assert.equal(await page.locator('.drama-card').count(),23);
  }
  // Storage denial must not break direct query editions or next/previous.
  const noStore=await browser.newContext();await noStore.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  await noStore.addInitScript(()=>{Storage.prototype.getItem=function(){throw new Error('denied')};Storage.prototype.setItem=function(){throw new Error('denied')};});
  const privatePage=await noStore.newPage();privatePage.on('pageerror',e=>errors.push(e.message));await privatePage.goto(url(file(items[0]),'ja'));await privatePage.locator('.drama-series-nav a').nth(1).click();assert.equal(await privatePage.locator('html').getAttribute('lang'),'ja');actions++;await noStore.close();
  await page.goto(url(file(items[0]),'de'));await page.screenshot({path:'/tmp/drama-desktop.png'});
  await page.setViewportSize({width:390,height:900});await page.goto(url(file(items[22]),'ko'));await page.screenshot({path:'/tmp/drama-mobile.png'});
  assert.deepEqual(errors,[]);console.log(JSON.stringify({views,actions,errors,viewports:[1440,390,320],network:'localhost only'}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
