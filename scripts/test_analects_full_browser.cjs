// Run against a local static server. No external network requests are allowed.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8795';
const root=path.resolve(__dirname,'..');
const receipt=JSON.parse(fs.readFileSync(path.join(root,'data/analects-full/manifest.json')));
const langs=['en','zh','zh-hant','de','fr','es','ja','ko'];
const primary=['en','zh','zh-hant'];
const suffix={'en':'en','zh':'zh','zh-hant':'hant'};
const url=(file,lang)=>base+'/essays/analects/'+(primary.includes(lang)?file+'?lang='+lang:lang+'/'+file);
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});let views=0,clicks=0;const errors=[];
 try{
  const context=await browser.newContext();
  await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  for(const width of [1440,390]){
   await page.setViewportSize({width,height:900});
   for(const item of receipt.essays){
    for(const lang of langs){
     const response=await page.goto(url(item.file,lang),{waitUntil:'domcontentloaded'});assert.equal(response.status(),200);
     const article=primary.includes(lang)?page.locator('.lang-'+suffix[lang]+'.local'):page.locator('.analects-article');
     const returnBox=await page.locator('.article-top a').boundingBox();
     const headerBox=await page.locator('.site-shell-header').boundingBox();
     assert(returnBox.y>=headerBox.y+headerBox.height,`${item.file} ${lang} ${width} return link under header`);
     assert(await article.isVisible());assert((await article.locator('.article-body').innerText()).length>1000);
     assert((await article.locator('h1').innerText()).trim());assert.equal(await article.locator('.source-note').count(),1);
     assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),true,`${item.file} ${lang} ${width} overflow`);
     assert.equal(await page.locator('.series-nav a').count(),['01','50'].includes(item.number)?1:2);
     views++;
    }
   }
   for(const lang of langs){
    await page.goto(url('index.html',lang));
    const section=primary.includes(lang)?page.locator('.lang-'+suffix[lang]+'.local'):page.locator('main');
    assert(await section.isVisible());assert.equal(await section.locator('.essay-card').count(),50);
    await section.locator('.essay-card').first().click();assert(page.url().includes(receipt.essays[0].file));clicks++;
   }
  }
  // Round-trip every language from the same primary article, then previous/next and history.
  await page.setViewportSize({width:1440,height:900});
  for(const lang of ['de','fr','es','ja','ko']){
   await page.goto(url(receipt.essays[24].file,'en'));
   await page.locator('.site-shell-language summary').click();
   await page.locator('.site-shell-language-options a').filter({hasText:{de:'Deutsch',fr:'Français',es:'Español',ja:'日本語',ko:'한국어'}[lang]}).click();clicks++;
   assert(page.url().includes('/'+lang+'/'));await page.locator('.series-nav a.next').click();clicks++;
   assert(page.url().includes(receipt.essays[25].file));await page.goBack();assert(page.url().includes(receipt.essays[24].file));
   await page.locator('.site-shell-language summary').click();await page.locator('.site-shell-language-options a').filter({hasText:'繁體中文'}).click();clicks++;
   assert.equal(await page.locator('html').getAttribute('lang'),'zh-Hant');
   await page.locator('.series-nav a.next').click();clicks++;assert.equal(await page.locator('html').getAttribute('lang'),'zh-Hant');
  }
  // A switch after arriving with an explicit query survives reload.
  await page.goto(url(receipt.essays[24].file,'zh-hant'));
  for(const lang of ['en','zh','zh-hant','en']){
   await page.locator('.site-shell-language summary').click();
   await page.locator('.site-shell-language-options [data-set-language="'+lang+'"]').click();clicks++;
   assert.equal(new URL(page.url()).searchParams.get('lang'),lang);
   await page.reload();assert.equal(await page.locator('html').getAttribute('data-lang'),lang);
  }
  // Repeated mobile menu toggles and Escape must leave the navigation usable.
  await page.setViewportSize({width:390,height:900});
  await page.goto(url(receipt.essays[0].file,'fr'));
  const menu=page.locator('[data-site-shell-menu]');
  for(let i=0;i<2;i++){await menu.click();assert.equal(await menu.getAttribute('aria-expanded'),'true');await page.keyboard.press('Escape');assert.equal(await menu.getAttribute('aria-expanded'),'false');}
  await menu.click();await page.locator('.site-shell-mobile-languages a').filter({hasText:'EN'}).click();clicks++;assert.equal(await page.locator('html').getAttribute('lang'),'en');
  // Search-result language, not previously saved UI language, controls primary editions.
  await page.setViewportSize({width:1440,height:900});
  for(const lang of langs){
   await page.goto(url(receipt.essays[0].file,lang));
   const title=await (primary.includes(lang)?page.locator('.lang-'+suffix[lang]+'.local h1'):page.locator('.analects-article h1')).innerText();
   const searchCode={zh:'zh-Hans','zh-hant':'zh-Hant'}[lang]||lang;
   await page.goto(base+'/search.html?lang=en&ui='+lang+'&in='+encodeURIComponent(searchCode)+'&q='+encodeURIComponent(title));
   const target='/essays/analects/'+(primary.includes(lang)?'':lang+'/')+receipt.essays[0].file;
   const result=page.locator('[data-search-results] a').filter({hasText:title}).first();
   await result.waitFor({state:'visible'});await result.click();clicks++;
   assert(new URL(page.url()).pathname===target);
   assert.equal(await page.locator('html').getAttribute('lang'),{zh:'zh-Hans','zh-hant':'zh-Hant'}[lang]||lang);
  }
  await page.goto(url(receipt.essays[0].file,'en'));
  await page.screenshot({path:'/tmp/analects-full-desktop.png'});
  await page.setViewportSize({width:390,height:900});await page.goto(url(receipt.essays[36].file,'ja'));
  await page.screenshot({path:'/tmp/analects-full-mobile.png'});
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({views,clicks,errors,viewports:[1440,390],network:'localhost only'}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
