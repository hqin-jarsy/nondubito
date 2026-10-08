const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8786';
const data=path.join(__dirname,'../data/film-full');
const films=fs.readdirSync(data).filter(n=>/^batch\d+-received\.json$/.test(n)).sort().flatMap(n=>JSON.parse(fs.readFileSync(path.join(data,n))).films);
const langs=['de','fr','es','ja','ko'];
(async()=>{const browser=await chromium.launch({headless:true,channel:'chrome'});try{
 const context=await browser.newContext();await context.route('**/*',r=>new URL(r.request().url()).origin===base?r.continue():r.abort());
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));let count=0;
 for(const width of [375,768,1440]){
  await page.setViewportSize({width,height:900});
  for(const f of films)for(const lang of langs)for(const name of ['index',...f.chapters]){
   const url=`${base}/essays/film/${f.slug}/${lang}/${name}.html`;await page.goto(url);
   assert.equal(await page.locator('h1:visible').count(),1,url);
   assert.equal(await page.locator('.lang-select option').count(),8,url);
   assert.equal(await page.locator('.lang-select option:checked').textContent(),{de:'Deutsch',fr:'Français',es:'Español',ja:'日本語',ko:'한국어'}[lang]);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),url);
   count++;
  }
 }
 for(const f of films){
  await page.goto(`${base}/essays/film/${f.slug}/${f.chapters[0]}.html?lang=en`);
  assert.equal(await page.locator('html').getAttribute('data-lang'),'en');
  await page.selectOption('.lang-select',{label:'日本語'});await page.waitForURL(`**/${f.slug}/ja/${f.chapters[0]}.html`);
  await page.selectOption('.lang-select',{label:'繁體中文'});await page.waitForURL(`**/${f.chapters[0]}.html?lang=zh-hant`);
  assert.equal(await page.locator('html').getAttribute('data-lang'),'zh-hant');
 }
 for(const lang of langs){await page.goto(`${base}/essays/film/${lang}/index.html`);assert.equal(await page.locator('.ff-card').count(),films.length);}
 const sample=films[films.length-1];
 await page.setViewportSize({width:1440,height:1000});await page.goto(`${base}/essays/film/${sample.slug}/fr/${sample.chapters[1]}.html`);await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));await page.screenshot({path:'/tmp/film-full-desktop.png'});
 await page.setViewportSize({width:375,height:844});await page.goto(`${base}/essays/film/${sample.slug}/ko/${sample.chapters[2]}.html`);await page.screenshot({path:'/tmp/film-full-mobile.png'});
 const plain=await browser.newContext({javaScriptEnabled:false});const p=await plain.newPage();await p.goto(`${base}/essays/film/leon/ja/${films[4].chapters[0]}.html`);assert(await p.locator('.ff-body p').count()>25);await p.getByRole('link',{name:'Français',exact:true}).click();await p.waitForURL(`**/leon/fr/${films[4].chapters[0]}.html`);
 assert.deepEqual(errors,[]);console.log(`PASS ${count} article/index viewport checks, same-article language routing, five hubs and no-JS reading.`);
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
