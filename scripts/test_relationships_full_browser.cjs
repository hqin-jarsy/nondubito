/* Local reader QA only. Can test in-memory drafts with serve_relationships_preview.py. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const {chromium}=require('playwright');
const base=process.argv[2]||'http://127.0.0.1:8786';
const folder=path.join(__dirname,'../data/relationships-full');
const series='everyday/relationships';
const langs=['zh','zh-hant','en','ja','fr','de','es','ko'];
const primary=l=>['zh','zh-hant','en'].includes(l);
const actual=l=>({'zh':'zh-Hans','zh-hant':'zh-Hant'}[l]||l);
const source=s=>JSON.parse(fs.readFileSync(path.join(folder,'sources',s+'.json')));
const requested=process.env.RELATIONSHIPS_EPISODES?.split(',').map(Number);
const slugs=fs.readdirSync(path.join(folder,'sources')).filter(s=>/^\d/.test(s)&&s.endsWith('.json')).map(s=>s.slice(0,-5)).filter(s=>!requested||requested.includes(Number(s.slice(0,2)))).sort();
const pageURL=(l,s)=>base+'/essays/'+series+'/'+(primary(l)?'':l+'/')+s+'.html';
async function setLanguage(page,l){
 await page.goto(base+'/index.html');
 await page.evaluate(l=>{localStorage.setItem('nd_lang',l);localStorage.setItem('nondubito-lang',l)},l);
}
async function check(page,l,slug){
 await page.waitForFunction(l=>document.documentElement.lang===l,actual(l));
 assert.equal(await page.locator('h1:visible').count(),1,l+'/'+slug+' title');
 assert.equal(await page.locator('h1:visible').evaluate(el=>getComputedStyle(el).hyphens),'auto',l+'/'+slug+' title hyphenation');
 if(slug!=='index'){
  const body=page.locator('.article-body:visible');
  assert.equal(await body.count(),1);
  assert.equal(await body.locator(':scope > p').count(),source(slug).body.length,l+'/'+slug+' full paragraphs');
  const title=primary(l)&&l!=='en'?source(slug).languages[l==='zh-hant'?'hant':'zh'].title:JSON.parse(fs.readFileSync(path.join(folder,'translations',l,slug+'.json'))).title;
  assert.equal((await page.locator('h1:visible').innerText()).trim(),title);
 }
 assert.equal(await page.locator('.lang-toggle .lang-btn').count(),8);
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth)<=page.viewportSize().width+1,l+'/'+slug+' overflow');
}
(async()=>{
 assert.ok(slugs.length,'No episodes selected');
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const out=process.env.RELATIONSHIPS_SCREENSHOTS||fs.mkdtempSync(path.join(os.tmpdir(),'relationships-reader-qa-'));
 fs.mkdirSync(out,{recursive:true});let views=0,searchClicks=0;const errors=[];
 const localOnly=r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort();
 try{
  const ctx=await browser.newContext();await ctx.route('**/*',localOnly);
  const page=await ctx.newPage();page.on('pageerror',e=>errors.push(e.message));
  for(const width of [320,1440]){
   await page.setViewportSize({width,height:900});
   for(const l of langs){
    await setLanguage(page,l);
    for(const slug of ['index',...slugs]){
     await page.goto(pageURL(l,slug));await check(page,l,slug);views++;
     if(slug===slugs[0]&&['zh','en','de','ja'].includes(l))await page.screenshot({path:path.join(out,l+'-'+width+'.png')});
    }
   }
  }
  await page.setViewportSize({width:375,height:900});
  for(const from of langs)for(const target of langs){
   await setLanguage(page,from);await page.goto(pageURL(from,slugs[0]));
   const label=({zh:'中文','zh-hant':'繁體',en:'EN',ja:'日本語',fr:'Français',de:'Deutsch',es:'Español',ko:'한국어'})[target];
   const control=page.locator('.lang-toggle .lang-btn').filter({hasText:new RegExp('^'+label+'$')});
   if(await control.evaluate(el=>el.tagName!=='SPAN'))await control.click();
   await check(page,target,slugs[0]);assert.ok(page.url().includes(slugs[0]+'.html'));
  }
  for(const l of langs){
   await setLanguage(page,l);await page.goto(pageURL(l,'index'));
   await page.locator('.essay-card[href="'+slugs[0]+'.html"]:visible').click();await check(page,l,slugs[0]);
   if(slugs.length>1&&Number(slugs[1].slice(0,2))===Number(slugs[0].slice(0,2))+1){
    await page.locator('.series-nav a[href="'+slugs[1]+'.html"]:visible').click();await check(page,l,slugs[1]);
    await page.goBack();await check(page,l,slugs[0]);
   }
   await page.goBack();await check(page,l,'index');
  }
  for(const l of ['en','zh','zh-hant']){
   await setLanguage(page,l==='en'?'zh':'en');await page.goto(pageURL(l,slugs[0])+'?lang='+l);
   await check(page,l,slugs[0]);await page.reload();await check(page,l,slugs[0]);
  }
  await page.goto(pageURL('en',slugs[0])+'?lang=en');
  for(const l of ['zh-hant','zh','en','zh-hant','en']){
   await page.locator('.lang-btn[data-lang-button="'+l+'"]').click();await check(page,l,slugs[0]);await page.reload();await check(page,l,slugs[0]);
  }
  const blocked=await browser.newContext({viewport:{width:375,height:900}});await blocked.route('**/*',localOnly);
  await blocked.addInitScript(()=>{Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage blocked')}})});
  const q=await blocked.newPage(),blockedErrors=[];q.on('pageerror',e=>blockedErrors.push(e.message));
  for(const l of ['en','zh','zh-hant']){await q.goto(pageURL(l,slugs[0])+'?lang='+l);await check(q,l,slugs[0])}
  await q.goto(pageURL('de',slugs[0]));await q.locator('.lang-toggle a').filter({hasText:/^EN$/}).click();await check(q,'en',slugs[0]);
  assert.deepEqual(blockedErrors,[]);
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:900}});await nojs.route('**/*',localOnly);const n=await nojs.newPage();
  for(const l of langs.filter(l=>!primary(l))){await n.goto(pageURL(l,slugs[0]));await check(n,l,slugs[0])}
  if(process.env.RELATIONSHIPS_SEARCH==='1')for(const l of langs)for(const slug of [slugs[0],slugs.at(-1)]){
   await setLanguage(page,l);await page.goto(pageURL(l,slug));const title=(await page.locator('h1:visible').innerText()).trim();
   await page.goto(base+'/search.html?in='+actual(l)+'&q='+encodeURIComponent(title));
   const suffix='essays/'+series+'/'+(primary(l)?'':l+'/')+slug+'.html';
   const result=page.locator('[data-search-results] h2 a[href*="'+suffix+'"]');await result.waitFor({state:'visible'});await result.click();await check(page,l,slug);searchClicks++;
  }
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({views,episodes:slugs.length,directedLanguageTransitions:64,searchResultClicks:searchClicks,blockedStorage:true,noJavaScriptForeign:true,errors,screenshots:out}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
