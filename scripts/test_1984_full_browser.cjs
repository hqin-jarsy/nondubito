/* Local-only reader QA. No public navigation, deployment, or saved-profile access. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const {chromium}=require('playwright');
const base=process.argv[2]||'http://127.0.0.1:8776';
const series='literature/nineteen-eighty-four';
const dataDir=path.join(__dirname,'../data/nineteen-eighty-four-full');
const receipt=JSON.parse(fs.readFileSync(path.join(dataDir,'preservation.json')));
const slugs=Object.keys(receipt.source_bodies);
const langs=['zh','zh-hant','en','ja','de','fr','es','ko'];
const primary=l=>['zh','zh-hant','en'].includes(l);
const pageURL=(l,s)=>`${base}/essays/${series}/${primary(l)?'':l+'/'}${s}.html`;
const actual=l=>({'zh':'zh-Hans','zh-hant':'zh-Hant'}[l]||l);
async function setLanguage(page,l){
 await page.goto(base+'/index.html');
 await page.evaluate(l=>{localStorage.setItem('nd_lang',l);localStorage.setItem('nondubito-lang',l);},l);
}
async function check(page,l,slug){
 await page.waitForFunction(l=>document.documentElement.lang===l,actual(l));
 assert.equal(await page.locator('h1:visible').count(),1,`${l}/${slug} title`);
 if(slug!=='index'){
  const body=page.locator('.essay-body:visible');assert.equal(await body.count(),1);
  const expected=receipt.source_bodies[slug].units;
  assert.equal(await body.locator(':scope > p, :scope > h2').count(),expected,`${l}/${slug} full body`);
 }
 assert.equal(await page.locator('.lang-toggle .lang-btn').count(),8);
 const width=page.viewportSize().width;
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth)<=width+1,`${l}/${slug} overflow at ${width}`);
}
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const out=process.env.ORWELL_SCREENSHOTS||fs.mkdtempSync(path.join(os.tmpdir(),'orwell-reader-qa-'));
 fs.mkdirSync(out,{recursive:true});let views=0;const errors=[];
 try{
  const ctx=await browser.newContext();
  await ctx.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await ctx.newPage();page.on('pageerror',e=>errors.push(e.message));
  for(const width of [320,1440]){
   await page.setViewportSize({width,height:900});
   for(const lang of langs){
    await setLanguage(page,lang);
    for(const [n,slug] of ['index',...slugs].entries()){
     await page.goto(pageURL(lang,slug));await check(page,lang,slug);views++;
     if(n===1&&['zh','en','de','ja'].includes(lang))await page.screenshot({path:path.join(out,`${lang}-${width}.png`)});
    }
   }
  }
  // Every directed language transition preserves the same essay; controls are
  // buttons for primary languages and same-episode links for foreign editions.
  await page.setViewportSize({width:375,height:900});
  for(const from of langs)for(const target of langs){
   await setLanguage(page,from);await page.goto(pageURL(from,slugs[1]));
   const label=({zh:'中文','zh-hant':'繁體',en:'EN',ja:'日本語',de:'Deutsch',fr:'Français',es:'Español',ko:'한국어'})[target];
   const control=page.locator('.lang-toggle .lang-btn').filter({hasText:new RegExp('^'+label+'$')});
   if(await control.evaluate(el=>el.tagName!=='SPAN'))await control.click();
   await check(page,target,slugs[1]);assert.ok(page.url().includes(slugs[1]+'.html'));
  }
  // Index -> first/last essay -> neighbor -> Back, and repeated primary toggles.
  for(const l of langs){
   for(const n of [1,4]){
    await setLanguage(page,l);await page.goto(pageURL(l,'index'));
    const slug=slugs[n-1];
    await page.locator(`.entry-row[href="${slug}.html"]:visible, .essay-card[href="${slug}.html"]:visible`).click();await check(page,l,slug);
    const neighbor=slugs[n===1?1:2];
    await page.locator(`.series-nav a[href="${neighbor}.html"]:visible, .essay-nav a[href="${neighbor}.html"]:visible`).first().click();await check(page,l,neighbor);
    await page.goBack();await check(page,l,slug);
   }
  }
  await setLanguage(page,'en');await page.goto(pageURL('en',slugs[0]));
  for(const l of ['zh-hant','zh','en','zh-hant','en']){
   await page.locator(`.lang-btn[data-lang="${l}"]`).click();await check(page,l,slugs[0]);
  }
  // Actual first/last search results in every language.
  for(const l of langs)for(const n of [1,4]){
   const slug=slugs[n-1];
   await setLanguage(page,l);await page.goto(pageURL(l,slug));await check(page,l,slug);
   const title=(await page.locator('h1:visible').innerText()).trim();
   await page.goto(`${base}/search.html?in=${actual(l)}&q=${encodeURIComponent(title)}`);
   const suffix=`essays/${series}/${primary(l)?'':l+'/'}${slug}.html`;
   const result=page.locator(`[data-search-results] h2 a[href*="${suffix}"]`);
   await result.waitFor({state:'visible'});await result.click();await check(page,l,slug);
  }
  // Explicit URL language wins over conflicting storage, and survives reload.
  for(const l of ['en','zh','zh-hant']){
   await setLanguage(page,l==='en'?'zh':'en');await page.goto(pageURL(l,slugs[3])+'?lang='+l);
   await check(page,l,slugs[3]);await page.reload();await check(page,l,slugs[3]);
   if(l==='zh-hant')assert.ok((await page.title()).includes('附錄'));
  }
  const blocked=await browser.newContext({viewport:{width:375,height:900}});
  await blocked.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  await blocked.addInitScript(()=>{Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage blocked');}});});
  const q=await blocked.newPage(),blockedErrors=[];q.on('pageerror',e=>blockedErrors.push(e.message));
  for(const l of ['en','zh','zh-hant']){
   await q.goto(pageURL(l,slugs[0])+'?lang='+l);await check(q,l,slugs[0]);
  }
  await q.goto(pageURL('de',slugs[0]));await q.locator('.lang-toggle a').filter({hasText:/^EN$/}).click();await check(q,'en',slugs[0]);
  assert.deepEqual(blockedErrors,[]);
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:900}});
  await nojs.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const nojsPage=await nojs.newPage();
  for(const l of langs.filter(l=>!primary(l))){await nojsPage.goto(pageURL(l,slugs[0]));await check(nojsPage,l,slugs[0]);}
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({views,directedLanguageTransitions:64,searchResultClicks:16,blockedStorage:true,noJavaScriptForeign:true,errors,screenshots:out}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
