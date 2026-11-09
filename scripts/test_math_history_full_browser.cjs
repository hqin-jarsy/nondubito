/* Local-only regression: accepted output or an explicitly mocked temporary preview. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {chromium}=require('playwright');
const base=process.argv[2]||'http://127.0.0.1:8774';
const langs=['en','zh','zh-hant','de','fr','es','ja','ko'];
const actualLang=l=>({'zh':'zh-Hans','zh-hant':'zh-Hant'}[l]||l);
const cssLang=l=>l==='zh-hant'?'hant':l;
const primary=l=>langs.indexOf(l)<3;
function url(l,n){return `${base}/essays/math-history/${primary(l)?n+'?lang='+l:l+'/'+n}`;}
function episode(i){return 'ep'+String(i).padStart(2,'0')+'.html';}
async function offline(context){
 await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
}
async function language(page,l,article=true){
 await page.waitForFunction(expected=>document.documentElement.lang===expected,actualLang(l));
 assert.equal(await page.locator('html').getAttribute('data-lang'),l);
 assert.equal(await page.locator('main h1:visible').count(),1);
 if(primary(l))assert.ok(await page.locator('main h1.lang-'+cssLang(l)).isVisible());
 if(article){
  const prose=page.locator('.math-prose:visible');
  assert.equal(await prose.count(),1);
  assert.equal(await prose.getAttribute('lang'),actualLang(l));
  if(primary(l))assert.ok(await prose.evaluate((node,css)=>node.classList.contains('lang-'+css),cssLang(l)));
  assert.equal(await prose.locator('h2').count(),primary(l)?8:9);
 }
}
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});let checks=0;
 const screenshots=process.env.MATH_SCREENSHOTS||fs.mkdtempSync(path.join(os.tmpdir(),'math-browser-qa-'));
 fs.mkdirSync(screenshots,{recursive:true});
 try{
  const ctx=await browser.newContext();await offline(ctx);
  const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const width of [320,375,768,1440]){
   await page.setViewportSize({width,height:900});
   for(const l of langs)for(let i=0;i<=25;i++){
    const n=i?episode(i):'index.html';await page.goto(url(l,n));await language(page,l,!!i);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth)<=width+1,`${l} ${n} ${width}`);
    assert.equal(await page.locator('[data-math-language]').count(),8);
    const spacing=await page.evaluate(()=>{const nav=document.querySelector('.math-languages'),main=document.querySelector('main');return {nav:nav.getBoundingClientRect().bottom,main:main.getBoundingClientRect().top};});
    assert.ok(spacing.main>=spacing.nav,`${l} ${n} ${width}: language navigation overlaps content`);
    if(i===1 && ['en','de'].includes(l) && [1440,375].includes(width)){
     await page.screenshot({path:path.join(screenshots,`math-ep01-${l}-${width}.png`)});
     await page.locator('.math-prose:visible h2').nth(1).scrollIntoViewIfNeeded();
     await page.screenshot({path:path.join(screenshots,`math-prose-${l}-${width}.png`)});
    }
    checks++;
   }
  }
  // Check every directed language transition, not just a repeated eight-link cycle.
  for(const from of langs)for(const target of langs){
   await page.goto(url(from,'ep13.html'));await language(page,from);
   await page.locator(`[data-math-language="${target}"]`).click();
   assert.ok(page.url().includes('ep13.html'));await language(page,target);
  }
  // Real hub card, first/last cards, neighbors, contents, then browser Back to hub.
  for(const l of langs){
   const hub=primary(l)?`${base}/library.html?lang=${l}`:`${base}/essays/${l}/index.html`;
   for(const i of [1,25]){
    await page.goto(hub);
    await page.locator(`a[href="${primary(l)?'essays/math-history/index.html':'../math-history/'+l+'/index.html'}"]`).click();
    await language(page,l,false);
    await page.locator(`a.math-card[href*="${episode(i)}"]`).click();await language(page,l);
    await page.locator('.math-series-nav a').nth(i===1?1:0).click();
    assert.ok(page.url().includes(episode(i===1?2:24)));await language(page,l);
    await page.locator('.math-series-nav a').nth(i===1?0:1).click();
    assert.ok(page.url().includes(episode(i)));await language(page,l);
    await page.locator('.math-series-nav a').nth(i===1?0:1).click();await language(page,l,false);
    // Back through contents -> boundary -> neighbor -> boundary -> index -> hub.
    for(let back=0;back<5;back++)await page.goBack();
    assert.equal(new URL(page.url()).pathname,new URL(hub).pathname);
   }
  }
  // Query the real search UI and click an actual first/last result in all eight languages.
  for(const l of langs)for(const i of [1,25]){
   await page.goto(url(l,episode(i)));await language(page,l);
   const title=(await page.locator('main h1:visible').innerText()).trim();
   await page.goto(`${base}/search.html?in=${actualLang(l)}&q=${encodeURIComponent(title)}`);
   const suffix=primary(l)?`essays/math-history/${episode(i)}`:`essays/math-history/${l}/${episode(i)}`;
   const result=page.locator(`[data-search-results] h2 a[href*="${suffix}"]`);
   await result.waitFor({state:'visible'});await result.click();
   await language(page,l);assert.ok(page.url().includes(episode(i)));
   if(primary(l))assert.equal(new URL(page.url()).searchParams.get('lang'),l);
  }
  const nojs=await browser.newContext({javaScriptEnabled:false});await offline(nojs);const p=await nojs.newPage();
  for(const l of langs.slice(3))for(const i of [1,25]){await p.goto(url(l,episode(i)));await language(p,l);}
  const blocked=await browser.newContext();await offline(blocked);
  await blocked.addInitScript(()=>{Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage blocked');}});});
  const q=await blocked.newPage(),blockedErrors=[];q.on('pageerror',e=>blockedErrors.push(e.message));
  for(const l of langs){await q.goto(url(l,'ep01.html'));await language(q,l);}
  assert.deepEqual(errors,[]);assert.deepEqual(blockedErrors,[]);
  console.log(`Passed ${checks} responsive views, 64 directed switches, 16 hub/neighbor/back routes, 16 real search result clicks, no-JS and blocked-storage checks. All contexts block external requests. Screenshots: ${screenshots}`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
