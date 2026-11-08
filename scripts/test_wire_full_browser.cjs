const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8796';
const root=path.resolve(__dirname,'..');
const slugs=JSON.parse(fs.readFileSync(path.join(root,'data/wire-full/source-manifest.json'))).articles.map(x=>x.slug);
const langs=['en','zh','zh-hant','de','fr','es','ja','ko'];
const primary=l=>['en','zh','zh-hant'].includes(l);
const native=l=>l==='zh'?'zh-Hans':l==='zh-hant'?'zh-Hant':l;
const labels={en:'EN',zh:'中文','zh-hant':'繁體',de:'Deutsch',fr:'Français',es:'Español',ja:'日本語',ko:'한국어'};
const url=(slug,lang)=>base+'/essays/tv/the-wire/'+(primary(lang)?slug+'.html?lang='+lang:lang+'/'+slug+'.html');
(async()=>{const browser=await chromium.launch({headless:true,channel:'chrome'});let views=0,actions=0;const errors=[];
 try{
 const ctx=await browser.newContext();await ctx.route('**/*',r=>new URL(r.request().url()).origin===base?r.continue():r.abort());const page=await ctx.newPage();page.on('pageerror',e=>errors.push(e.message));
 for(const width of [375,768,1440]){await page.setViewportSize({width,height:900});for(const slug of ['index',...slugs])for(const lang of langs){
  const response=await page.goto(url(slug,lang));assert.equal(response.status(),200);assert.equal(await page.locator('html').getAttribute('lang'),native(lang));assert.equal(await page.locator('h1:visible').count(),1,url(slug,lang));assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),url(slug,lang)+' '+width+' overflow');
  if(slug!=='index'){const body=page.locator(primary(lang)?'.essay-body.lang-'+(lang==='en'?'en':'zh'):'.collection-body');assert(await body.isVisible());assert.equal(await body.locator('h2').count(),5);assert((await body.innerText()).length>2500);if(!primary(lang))assert((await body.locator('p').count())>80);}
  else assert.equal(await page.locator(primary(lang)?'.essay-body.lang-'+(lang==='en'?'en':'zh')+' .essay-card':'.collection-card').count(),9);
  views++;
 }}
 // Eight-language switching keeps the same article and requested language.
 await page.goto(url(slugs[0],'en'));
 for(const lang of ['zh','zh-hant','fr','de','ja','ko','es','en']){
  await page.locator('.lang-btn').filter({hasText:new RegExp('^'+labels[lang]+'$')}).click();await page.waitForFunction(l=>document.documentElement.lang===l,native(lang));assert.equal(path.basename(new URL(page.url()).pathname),slugs[0]+'.html');actions++;
 }
 // Query wins over a contradictory saved language; neighbor/index links carry it.
 for(const lang of ['en','zh','zh-hant']){
  await page.goto(url(slugs[0],lang));await page.evaluate(()=>localStorage.setItem('nd_lang','de'));await page.reload();assert.equal(await page.locator('html').getAttribute('lang'),native(lang));await page.locator('.essay-nav a').last().click();await page.waitForURL(url(slugs[1],lang));await page.goBack();await page.waitForURL(url(slugs[0],lang));await page.locator('.back-link').click();await page.waitForURL(url('index',lang));await page.locator('.essay-body.lang-'+(lang==='en'?'en':'zh')+' .essay-card').nth(8).click();await page.waitForURL(url(slugs[8],lang));actions+=3;
 }
 // Every language's first and last page, including search-result language.
 for(const lang of langs)for(const slug of [slugs[0],slugs[8]]){
  await page.goto(url(slug,lang));const title=await page.locator('h1:visible').innerText();await page.goto(base+'/search.html?lang=en&ui=en&in='+native(lang)+'&q='+encodeURIComponent(title));const result=page.locator('[data-search-results] a').filter({hasText:title}).first();await result.waitFor({state:'visible'});await result.click();await page.waitForURL(u=>u.pathname===new URL(url(slug,lang)).pathname);await page.waitForLoadState('domcontentloaded');assert.equal(await page.locator('html').getAttribute('lang'),native(lang));actions++;
 }
 for(const lang of ['de','fr','es','ja','ko']){await page.goto(base+'/essays/'+lang+'/index.html');const link=page.locator('a[href="../tv/the-wire/'+lang+'/index.html"]');assert.equal(await link.count(),1);await link.click();await page.waitForURL(url('index',lang));actions++;}
 const nostore=await browser.newContext();await nostore.route('**/*',r=>new URL(r.request().url()).origin===base?r.continue():r.abort());await nostore.addInitScript(()=>{Storage.prototype.getItem=function(){throw Error('denied')};Storage.prototype.setItem=function(){throw Error('denied')};});const s=await nostore.newPage();s.on('pageerror',e=>errors.push(e.message));await s.goto(url(slugs[0],'en'));await s.locator('button[data-lang="zh-hant"]').click();await s.locator('.essay-nav a').last().click();await s.waitForURL(url(slugs[1],'zh-hant'));assert.equal(await s.locator('html').getAttribute('lang'),'zh-Hant');await nostore.close();actions++;
 const plain=await browser.newContext({javaScriptEnabled:false});await plain.route('**/*',r=>new URL(r.request().url()).origin===base?r.continue():r.abort());const p=await plain.newPage();await p.goto(url(slugs[0],'ja'));assert.equal(await p.locator('.collection-body h2').count(),5);await p.getByRole('link',{name:'Français',exact:true}).click();await p.waitForURL(url(slugs[0],'fr'));assert.equal(await p.locator('.collection-body h2').count(),5);await plain.close();actions++;
 await page.setViewportSize({width:1440,height:1000});await page.goto(url(slugs[0],'en'));await page.screenshot({path:'/tmp/wire-desktop.png'});await page.setViewportSize({width:375,height:844});await page.goto(url(slugs[8],'ko'));await page.screenshot({path:'/tmp/wire-mobile.png'});
 assert.deepEqual(errors,[]);console.log(JSON.stringify({views,actions,errors,viewports:[375,768,1440],network:'localhost only'}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
