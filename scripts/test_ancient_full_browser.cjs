// Existing local Playwright and Chrome; all non-local requests blocked.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8797';
const root=path.resolve(__dirname,'..');
const prefix='/essays/everyday/stories/ancient-stories/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
const receipt=read('data/ancient-full/source-manifest.json');
const langs=['en','zh-Hans','zh-Hant','ja','fr','de','es','ko'];
const query={en:'en','zh-Hans':'zh','zh-Hant':'zh-hant'};
const cls={en:'en','zh-Hans':'zh','zh-Hant':'hant'};
const url=(slug,lang)=>base+prefix+(query[lang]?slug+'.html?lang='+query[lang]:lang+'/'+slug+'.html');
const corrections=[read('data/ancient-full/minor-source-correction.json'),...read('data/ancient-full/approved-source-corrections.json')];
const blocks=(episode,lang)=>{
 const values=read(`data/ancient-full/${lang.startsWith('zh-')?'source':'translations'}/${String(episode).padStart(2,'0')}.${lang}.json`);
 for(const correction of corrections)if(episode===correction.episode&&correction.edits[lang]){
  assert.equal(values[correction.block].text,correction.edits[lang].before);
  values[correction.block].text=correction.edits[lang].after;
 }
 return values;
};
const plain=s=>s.replaceAll('**','').replaceAll('*','');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const errors=[];let views=0,clicks=0,searches=0;
 try{
  const context=await browser.newContext();
  await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  for(const width of [1440,390,320]){
   await page.setViewportSize({width,height:900});
   for(const {slug,episode} of receipt.essays){
    for(const lang of langs){
     const response=await page.goto(url(slug,lang),{waitUntil:'domcontentloaded'});assert.equal(response.status(),200);
     const source=blocks(episode,lang);
     const heading=page.locator('h1:visible');assert.equal(await heading.count(),1);
     assert.equal(await heading.textContent(),plain(source[0].text),`${slug} ${lang} title`);
     const body=page.locator(query[lang]?`.lang-${cls[lang]} .article-body`:'.collection-body');
     assert.equal(await body.locator(':scope > hr').count(),source.filter(b=>b.tag==='hr').length);
     assert.deepEqual(await body.locator(':scope > p').allTextContents(),source.filter(b=>b.tag==='p').map(b=>plain(b.text)),`${slug} ${lang} paragraphs`);
     assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`${width} ${slug} ${lang}`);
     if(query[lang])assert.equal(await page.locator('html').getAttribute('data-lang'),query[lang]);
     else assert.equal(await page.locator('html').getAttribute('lang'),lang);
     if(lang==='ko')assert.equal(await heading.evaluate(e=>getComputedStyle(e).wordBreak),'keep-all');
     if(lang==='de')assert.equal(await heading.evaluate(e=>getComputedStyle(e).hyphens),'auto');
     views++;
    }
   }
   for(const lang of langs){
    await page.goto(url('index',lang),{waitUntil:'domcontentloaded'});
    assert.equal(await page.locator(query[lang]?`.lang-${cls[lang]} a.essay-card`:'a.collection-card').count(),19);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`index ${lang} ${width}`);views++;
   }
  }
  // Cross-language entries retain the selected primary language through navigation.
  for(const [code,htmlLang,stored] of [['en','en','zh'],['zh-hant','zh-Hant','en'],['zh','zh-Hans','en']]){
   await page.goto(url(receipt.essays[0].slug,'de'));
   await page.evaluate(s=>{localStorage.setItem('nd_lang',s);localStorage.setItem('nondubito-lang',s)},stored);
   await page.locator(`a.lang-btn[href$="?lang=${code}"]`).click();await page.waitForURL(`**?lang=${code}`);
   assert.equal(await page.locator('html').getAttribute('lang'),htmlLang);
   assert.deepEqual(await page.evaluate(()=>[localStorage.getItem('nd_lang'),localStorage.getItem('nondubito-lang')]),[code,code]);
   const container=`.lang-${cls[htmlLang]} `;
   await page.locator(container+'a.series-nav-btn.next').click();await page.waitForURL('**/'+receipt.essays[1].slug+'.html');
   assert.equal(await page.locator('html').getAttribute('lang'),htmlLang);
   await page.locator(container+'a.series-nav-btn:not(.next)').click();await page.waitForURL('**/'+receipt.essays[0].slug+'.html');
   assert.equal(await page.locator('html').getAttribute('lang'),htmlLang);
   await page.locator('a.back-link').click();await page.waitForURL('**/ancient-stories/index.html');
   assert.equal(await page.locator('html').getAttribute('lang'),htmlLang);
   await page.locator(container+'a.essay-card').first().click();await page.waitForURL('**/'+receipt.essays[0].slug+'.html');
   assert.equal(await page.locator('html').getAttribute('lang'),htmlLang);
  }
  await page.goto(url(receipt.essays[0].slug,'zh-Hant')+'&from=qa#language-check');
  for(const code of ['en','zh','zh-hant']){
   await page.locator(`button[data-lang-button="${code}"]`).click();
   const selected=new URL(page.url());assert.equal(selected.searchParams.get('lang'),code);
   assert.equal(selected.searchParams.get('from'),'qa');assert.equal(selected.hash,'#language-check');
   await page.reload();assert.equal(await page.locator('html').getAttribute('data-lang'),code);
  }
  const slug=receipt.essays[13].slug;
  await page.goto(url(slug,'en'));
  for(const code of ['zh','zh-hant','en','zh','en']){
   await page.locator(`button[data-lang-button="${code}"]`).click();clicks++;
   assert.equal(await page.locator('html').getAttribute('data-lang'),code);assert.equal(await page.locator('h1:visible').count(),1);
  }
  for(const lang of ['ja','fr','de','es','ko']){
   const link=page.locator(`a.lang-btn[href$="/${lang}/${slug}.html"],a.lang-btn[href="${lang}/${slug}.html"]`);
   const wanted=new URL(await link.getAttribute('href'),page.url()).href;
   await link.click();await page.waitForURL(wanted);clicks++;assert.equal(await page.locator('html').getAttribute('lang'),lang);
  }
  await page.locator('a.lang-btn[href$="?lang=zh"]').click();await page.waitForURL('**?lang=zh');clicks++;
  await page.goBack();assert.equal(await page.locator('html').getAttribute('lang'),'ko');
  await page.goForward();assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
  await page.evaluate(()=>{localStorage.setItem('nd_lang','invalid');localStorage.setItem('nondubito-lang','invalid')});
  await page.goto(base+prefix+slug+'.html');assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
  await page.goto(url(receipt.essays[0].slug,'de'));
  await page.locator('.collection-nav a').last().click();await page.waitForURL('**/'+receipt.essays[1].slug+'.html');
  await page.locator('.collection-nav a').first().click();await page.waitForURL('**/'+receipt.essays[0].slug+'.html');
  await page.goto(url('index','ko'));
  await page.locator('a.collection-card').last().click();await page.waitForURL('**/'+receipt.essays[18].slug+'.html');
  // Search reaches the exact edition instead of merely finding a title string.
  for(const lang of langs){
   const first=receipt.essays[0];const term=plain(blocks(first.episode,lang)[0].text);
   await page.goto(base+'/search.html?q='+encodeURIComponent(term)+'&in='+encodeURIComponent(lang));
   const route=prefix.slice(1)+(query[lang]?'':lang+'/')+first.slug+'.html';
   const result=page.locator(`[data-search-results] a[href*="${route}"]`).first();
   await result.waitFor({state:'visible'});await result.click();await page.waitForURL('**/'+first.slug+'.html*');
   assert.equal(await page.locator('h1:visible').textContent(),term);searches++;
  }
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({passed:true,readingViews:views,languageClicks:clicks,searches,widths:[1440,390,320],pageErrors:errors}));
  for(const lang of ['de','ja','ko']){
   await page.goto(url(receipt.essays[0].slug,lang));
   await page.screenshot({path:`/tmp/ancient-full-${lang}-mobile.png`,fullPage:false});
   await page.locator('.collection-body').scrollIntoViewIfNeeded();
   await page.screenshot({path:`/tmp/ancient-full-${lang}-body.png`,fullPage:false});
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
