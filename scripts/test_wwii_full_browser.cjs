/* Local preview or final-site QA. External resources are blocked. */
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('playwright');
const base=process.argv[2]||'http://127.0.0.1:8787';
const slugs=['1-weimar','2-institutions','3-four-systems','4-promise','5-cracks'];
const langs=['en','zh','zh-hant','ja','fr','de','es','ko'];
const labels=['EN','简体','繁體','日本語','Français','Deutsch','Español','한국어'];
const primary=l=>['en','zh','zh-hant'].includes(l);
const actual=l=>({'zh':'zh-Hans','zh-hant':'zh-Hant'}[l]||l);
const url=(l,s)=>`${base}/essays/wwii/${primary(l)?'':l+'/'}${s}.html${primary(l)?'?lang='+l:''}`;
const counts=Object.fromEntries(slugs.map(s=>[s,JSON.parse(fs.readFileSync(path.join(__dirname,'../data/wwii-full/sources/'+s+'.json'))).body.length]));
async function check(p,l,s){
 await p.waitForFunction(l=>document.documentElement.lang===l,actual(l));
 assert.equal(await p.locator('h1:visible').count(),1,`${l}/${s} heading`);
 assert.equal(await p.locator('.lang-toggle .lang-btn').count(),8);
 if(s!=='index'){
  const body=p.locator('.essay-body:visible');assert.equal(await body.count(),1);
  assert.equal(await body.locator(':scope > p,:scope > h2').count(),counts[s]);
 }
 assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth)<=p.viewportSize().width+1,`${l}/${s}: overflow`);
}
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});let views=0;const errors=[];const screenshots=fs.mkdtempSync('/tmp/wwii-reader-qa-');
 try{
  const ctx=await browser.newContext();
  await ctx.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const p=await ctx.newPage();p.on('pageerror',e=>errors.push(e.message));
  for(const width of [320,375,1440]){
   await p.setViewportSize({width,height:900});
   for(const l of langs)for(const s of ['index',...slugs]){await p.goto(url(l,s));await check(p,l,s);views++;if(s===slugs[1]&&['de','zh-hant'].includes(l)&&width!==375)await p.screenshot({path:path.join(screenshots,`${l}-${width}.png`)});}
   console.log('Checked viewport',width);
  }
  for(const from of langs)for(const target of langs){
   await p.goto(url(from,slugs[1]));
   const control=p.locator('.lang-toggle .lang-btn').filter({hasText:new RegExp('^'+labels[langs.indexOf(target)]+'$')});
   if(await control.evaluate(e=>e.tagName!=='SPAN'))await control.click();
   await check(p,target,slugs[1]);assert.ok(p.url().includes(slugs[1]+'.html'));
  }
  for(const l of langs){
   await p.goto(url(l,'index'));
   await p.locator(`.essay-card[href^="${slugs[0]}.html"]:visible,.entry-row[href="${slugs[0]}.html"]:visible`).click();await check(p,l,slugs[0]);
   await p.locator(`a[data-primary-route][href*="${slugs[1]}.html"]:visible,.series-nav a[href="${slugs[1]}.html"]:visible`).first().click();await check(p,l,slugs[1]);
   await p.goBack();await check(p,l,slugs[0]);
  }
  for(const l of ['en','zh','zh-hant']){
   await p.evaluate(()=>localStorage.setItem('nd_lang','garbage'));
   await p.goto(url(l,slugs[2]));await check(p,l,slugs[2]);
   assert.equal(await p.evaluate(()=>localStorage.getItem('nd_lang')),l);
   await p.goto(url('en',slugs[3]).split('?')[0]);await check(p,l,slugs[3]);
  }
  if(process.argv.includes('--search'))for(const l of langs)for(const s of [slugs[0],slugs[4]]){
   await p.goto(url(l,s));const title=(await p.locator('h1:visible').innerText()).trim();
   await p.goto(`${base}/search.html?in=${actual(l)}&q=${encodeURIComponent(title)}`);
   const result=p.locator(`[data-search-results] h2 a[href*="essays/wwii/${primary(l)?'':l+'/'}${s}.html"]`);
   await result.first().click();await check(p,l,s);
  }
  const blocked=await browser.newContext({viewport:{width:320,height:900}});
  await blocked.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  await blocked.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage blocked')}}));
  const q=await blocked.newPage();q.on('pageerror',e=>errors.push(e.message));
  for(const l of ['en','zh','zh-hant']){await q.goto(url(l,slugs[0]));await check(q,l,slugs[0]);}
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:900}});
  await nojs.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const n=await nojs.newPage();for(const l of langs.filter(l=>!primary(l))){await n.goto(url(l,slugs[0]));await check(n,l,slugs[0]);}
  assert.deepEqual(errors,[]);console.log(JSON.stringify({views,languageTransitions:64,navigationLanguages:8,blockedStorage:true,noJSForeign:true,searchResultClicks:process.argv.includes('--search')?16:0,screenshots,errors}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
