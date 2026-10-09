const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8787';
const batch=process.env.ANIME_BATCH||'01';
assert(['01','02','03','04'].includes(batch));
const series=JSON.parse(fs.readFileSync(path.join(__dirname,`../data/anime-full/batch${batch}-received.json`))).series;
const langs=['de','fr','es','ja','ko'];
(async()=>{const browser=await chromium.launch({headless:true,channel:'chrome'});try{
 const context=await browser.newContext();
 await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));let count=0;
 for(const width of [375,768,1440]){
  await page.setViewportSize({width,height:900});
  for(const f of series)for(const lang of langs)for(const name of ['index',...f.chapters]){
   const url=`${base}/${f.route}/${lang}/${name}.html`;await page.goto(url);
   assert.equal(await page.locator('h1:visible').count(),1,url);
   assert.equal(await page.locator('.lang-select option').count(),8,url);
   assert(await page.locator('.lang-select').isVisible(),url);
   assert(await page.locator('.lang-select-menu').evaluate(el=>{const s=el.querySelector('select').getBoundingClientRect(),c=el.querySelector('.lang-select-chevron').getBoundingClientRect();return c.left>=s.left&&c.right<=s.right;}),url);
   assert(await page.locator('.lang-select').evaluate(el=>getComputedStyle(el).color!==getComputedStyle(document.body).backgroundColor),url);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),url);
   if(name!=='index'){
    assert((await page.locator('.essay-body').innerText()).length>1500,url);
    await page.locator('.series-nav').scrollIntoViewIfNeeded();
   }
   count++;
  }
 }
 for(const f of series){
  await page.goto(`${base}/${f.route}/de/${f.chapters[0]}.html`);
  await page.selectOption('.lang-select',{label:'日本語'});await page.waitForURL(`**/${f.slug}/ja/${f.chapters[0]}.html`);
  await page.selectOption('.lang-select',{label:'繁體'});await page.waitForURL(`**/${f.slug}/${f.chapters[0]}.html`);
  assert.equal(await page.locator('html').getAttribute('data-lang'),'zh-hant');
  if(['02','03','04'].includes(batch)){
   await page.selectOption('.lang-select',{label:'Français'});await page.waitForURL(`**/${f.slug}/fr/${f.chapters[0]}.html`);
  }
 }
 await page.setViewportSize({width:1440,height:1000});await page.goto(`${base}/${series[4].route}/fr/${series[4].chapters[2]}.html`);
 await page.screenshot({path:'/tmp/anime-full-desktop.png'});
 await page.setViewportSize({width:375,height:844});await page.goto(`${base}/${series[1].route}/ko/${series[1].chapters[3]}.html`);
 await page.screenshot({path:'/tmp/anime-full-mobile.png'});
 const plain=await browser.newContext({javaScriptEnabled:false});const p=await plain.newPage();
 await p.goto(`${base}/${series[0].route}/ja/${series[0].chapters[0]}.html`);
 assert(await p.locator('.essay-body p').count()>20);
 await p.getByRole('link',{name:'Français',exact:true}).click();await p.waitForURL(`**/${series[0].slug}/fr/${series[0].chapters[0]}.html`);
 assert.deepEqual(errors,[]);console.log(`PASS: ${count} responsive checks, all five series language routes, full text and no-JS reading.`);
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
