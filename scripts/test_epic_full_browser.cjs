// Local server and Playwright required. No external requests are permitted.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8795';
const prefix='/essays/everyday/stories/epic-traditions/';
const root=path.resolve(__dirname,'..');
const receipt=JSON.parse(fs.readFileSync(path.join(root,'data/epic-full/received.json')));
const reviewDirectory=path.join(root,'data/epic-full/reviews');
const edits=fs.readdirSync(reviewDirectory).filter(n=>n.endsWith('.json')).flatMap(n=>JSON.parse(fs.readFileSync(path.join(reviewDirectory,n))).edits||[]);
edits.push(...JSON.parse(fs.readFileSync(path.join(root,'data/epic-full/author-corrections-20261108.json'))).edits);
const langs=['en','zh-Hans','zh-Hant','ja','fr','de','es','ko'];
const query={'en':'en','zh-Hans':'zh','zh-Hant':'zh-hant'};
const cls={'en':'en','zh-Hans':'zh','zh-Hant':'hant'};
const url=(slug,lang)=>base+prefix+(query[lang]?slug+'.html?lang='+query[lang]:lang+'/'+slug+'.html');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const errors=[];let views=0,clicks=0;
 try{
  const context=await browser.newContext();
  await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  for(const width of [1440,390]){
   await page.setViewportSize({width,height:900});
   for(const {slug,episode} of receipt.essays){
    for(const lang of langs){
     const response=await page.goto(url(slug,lang),{waitUntil:'domcontentloaded'});assert.equal(response.status(),200);
     const blocks=JSON.parse(fs.readFileSync(path.join(root,`data/epic-full/received/alignment/${String(episode).padStart(2,'0')}.${lang}.json`)));
     for(const edit of edits.filter(e=>e.episode===episode&&e.lang===lang)){
      assert.equal(blocks[edit.block].text,edit.before);
      blocks[edit.block].text=edit.after;
     }
     const heading=page.locator('h1:visible');assert.equal(await heading.count(),1);
     assert.equal(await heading.textContent(),blocks[0].text.replace(/\*\*/g,'').replace(/\*/g,''));
     const body=page.locator(query[lang]?`.lang-${cls[lang]} .article-body`:'.collection-body');
     assert.equal(await body.locator(':scope > p').count(),blocks.filter(b=>b.tag==='p').length);
     assert.equal(await body.locator(':scope > hr').count(),blocks.filter(b=>b.tag==='hr').length);
     for(const edit of edits.filter(e=>e.episode===episode&&e.lang===lang&&e.block>0)){
      const index=blocks.slice(1,edit.block+1).filter(b=>b.tag==='p').length-1;
      assert.equal(await body.locator(':scope > p').nth(index).textContent(),edit.after.replace(/\*\*/g,'').replace(/\*/g,''));
     }
     assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`${width} ${slug} ${lang}`);
     if(query[lang])assert.equal(await page.locator('html').getAttribute('data-lang'),query[lang]);
     else assert.equal(await page.locator('html').getAttribute('lang'),lang);
     views++;
    }
   }
   for(const lang of langs){
    await page.goto(url('index',lang),{waitUntil:'domcontentloaded'});
    const cards=page.locator(query[lang]?`.lang-${cls[lang]} a.essay-card`:'a.collection-card');
    assert.equal(await cards.count(),20);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
    views++;
   }
  }
  await page.setViewportSize({width:320,height:860});
  const slug=receipt.essays[13].slug;
  await page.goto(url(slug,'en'));
  for(const code of ['zh','zh-hant','en','zh','en']){
   await page.locator(`button[data-lang-button="${code}"]`).click();clicks++;
   assert.equal(await page.locator('html').getAttribute('data-lang'),code);
   assert.equal(await page.locator('h1:visible').count(),1);
  }
  for(const lang of ['ja','fr','de','es','ko']){
   const href=await page.locator(`a.lang-btn[href$="/${lang}/${slug}.html"],a.lang-btn[href="${lang}/${slug}.html"]`).getAttribute('href');
   const wanted=new URL(href,page.url()).href;
   await page.locator(`a.lang-btn[href="${href}"]`).click();await page.waitForURL(wanted);clicks++;
   assert.equal(await page.locator('html').getAttribute('lang'),lang);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
  }
  const chinese=page.locator('a.lang-btn[href$="?lang=zh"]');
  await chinese.click();await page.waitForURL('**?lang=zh');clicks++;
  assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
  await page.goBack();assert.equal(await page.locator('html').getAttribute('lang'),'ko');
  await page.goForward();assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
  await page.evaluate(()=>{localStorage.setItem('nd_lang','invalid');localStorage.setItem('nondubito-lang','invalid')});
  await page.goto(base+prefix+slug+'.html');assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({passed:true,readingViews:views,languageClicks:clicks,widths:[1440,390,320],pageErrors:errors}));
  await page.goto(url(receipt.essays[0].slug,'de'));
  await page.screenshot({path:'/tmp/epic-full-de-mobile.png',fullPage:false});
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
