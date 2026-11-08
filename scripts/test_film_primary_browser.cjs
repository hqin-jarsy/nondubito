// Primary editions only: independent of paused foreign manuscripts.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('fs');const path=require('path');
const root=path.resolve(__dirname,'..'),base=process.argv[2]||'http://127.0.0.1:8796';
const films=['raise-the-red-lantern','dead-poets-society','parasite'].map(slug=>({slug,chapters:fs.readdirSync(path.join(root,'essays/film',slug)).filter(n=>/^[123]-.*\.html$/.test(n)).sort().map(n=>n.slice(0,-5))}));
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
const changes=Object.fromEntries(films.map(f=>[f.slug,read(`data/film-full/review/${f.slug}-approved-changes.json`).changes]));
const traditional=read('data/film-full/review/approved-traditional.json').files;
const clean=s=>s.replaceAll('**','').replaceAll('*','').replace(/\s+/g,' ').trim();
const url=(f,ep,l)=>`${base}/essays/film/${f.slug}/${ep}.html?lang=${l}`;
async function choose(p,l){if(await p.locator('.lang-select').count())await p.selectOption('.lang-select',{label:{en:'English',zh:'简体中文','zh-hant':'繁體中文'}[l]});else await p.locator(`button[data-lang="${l}"]`).click();}
(async()=>{const browser=await chromium.launch({channel:'chrome',headless:true});let views=0,actions=0,correctionChecks=0;const errors=[];
 try{const context=await browser.newContext();await context.route('**/*',r=>new URL(r.request().url()).origin===base?r.continue():r.abort());const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 for(const width of [375,768,1440]){await page.setViewportSize({width,height:900});for(const f of films)for(const [i,ep] of f.chapters.entries())for(const lang of ['en','zh','zh-hant']){
  await page.goto(url(f,ep,lang));assert.equal(await page.locator('html').getAttribute('data-lang'),lang);assert.equal(await page.locator('h1:visible').count(),1);const body=page.locator(`.essay-body.lang-${lang==='en'?'en':'zh'}`);assert.equal(await body.locator('h2').count(),8);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2));const text=clean(await body.innerText());
  if(lang!=='zh-hant')for(const change of changes[f.slug].filter(c=>c.episode===i+1)){assert(text.includes(clean(change[(lang==='en'?'en':'zh')+'_after'])),`${f.slug} ${ep} ${lang} approved copy missing`);correctionChecks++;}
  else{const delta=traditional[`essays/film/${f.slug}/zh-hant-data/${ep}.js`];if(delta)for(const value of Object.values(delta.added)){assert(text.includes(clean(value)),`${f.slug} ${ep} Traditional copy missing`);correctionChecks++;}}
  views++;
 }}
 for(const f of films){await page.goto(url(f,f.chapters[0],'en'));for(const l of ['zh-hant','zh','en']){await choose(page,l);assert.equal(new URL(page.url()).searchParams.get('lang'),l);assert.equal(await page.locator('html').getAttribute('data-lang'),l);actions++;}await page.getByRole('link',{name:/Next/}).last().click();await page.waitForURL(url(f,f.chapters[1],'en'));await page.waitForLoadState('domcontentloaded');assert.equal(new URL(page.url()).searchParams.get('lang'),'en');await page.goBack();await page.waitForURL(url(f,f.chapters[0],'en'));assert.equal(new URL(page.url()).pathname,new URL(url(f,f.chapters[0],'en')).pathname);actions++;}
 const noStore=await browser.newContext();await noStore.route('**/*',r=>new URL(r.request().url()).origin===base?r.continue():r.abort());await noStore.addInitScript(()=>{Storage.prototype.getItem=function(){throw Error('denied')};Storage.prototype.setItem=function(){throw Error('denied')};});const p=await noStore.newPage();p.on('pageerror',e=>errors.push(e.message));await p.goto(url(films[0],films[0].chapters[0],'en'));await choose(p,'zh-hant');await p.getByRole('link',{name:/Next/}).last().click();await p.waitForURL(url(films[0],films[0].chapters[1],'zh-hant'));assert.equal(await p.locator('html').getAttribute('data-lang'),'zh-hant');actions++;
 await page.setViewportSize({width:1440,height:1000});await page.goto(url(films[0],films[0].chapters[1],'zh-hant'));await page.locator('.essay-body.lang-zh h2').nth(4).scrollIntoViewIfNeeded();await page.screenshot({path:'/tmp/film-primary-approved-desktop.png'});await page.setViewportSize({width:375,height:844});await page.goto(url(films[2],films[2].chapters[0],'en'));await page.locator('.essay-body.lang-en h2').nth(2).scrollIntoViewIfNeeded();await page.screenshot({path:'/tmp/film-primary-approved-mobile.png'});
 assert.deepEqual(errors,[]);console.log(JSON.stringify({views,actions,correctionChecks,errors,scope:'Chinese, Traditional Chinese and English only'}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
