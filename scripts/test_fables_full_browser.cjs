// Uses existing local Playwright and Chrome. All non-local requests are blocked.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8796';
const root=path.resolve(__dirname,'..');
const prefix='/essays/everyday/stories/fables/';
const receipt=JSON.parse(fs.readFileSync(path.join(root,'data/fables-full/manifest.json')));
const langs=['en','zh-Hans','zh-Hant','ja','fr','de','es','ko'];
const query={'en':'en','zh-Hans':'zh','zh-Hant':'zh-hant'};
const cls={'en':'en','zh-Hans':'zh','zh-Hant':'hant'};
const url=(slug,lang)=>base+prefix+(query[lang]?slug+'.html?lang='+query[lang]:lang+'/'+slug+'.html');
const read=(p)=>JSON.parse(fs.readFileSync(path.join(root,p)));
const plain=(s)=>s.replaceAll('**','').replaceAll('*','');
// Normal-sized hero subtitles need WCAG AA contrast on their solid card.
async function assertHeroDeckContrast(page,label){
 const decks=await page.locator('.article-head:visible .story-deck').evaluateAll(nodes=>nodes.map(el=>{
  const foreground=getComputedStyle(el).color;
  const background=getComputedStyle(el.closest('.article-head')).backgroundColor;
  const rgb=s=>s.match(/[\d.]+/g).map(Number);
  const fg=rgb(foreground),bg=rgb(background),alpha=fg[3]??1;
  const luminance=channels=>{
   const linear=channels.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4});
   return .2126*linear[0]+.7152*linear[1]+.0722*linear[2];
  };
  const text=luminance(fg.slice(0,3).map((v,i)=>v*alpha+bg[i]*(1-alpha)));
  const card=luminance(bg);
  return {foreground,background,opaqueBackground:(bg[3]??1)===1,ratio:(Math.max(text,card)+.05)/(Math.min(text,card)+.05)};
 }));
 for(const deck of decks){
  assert.ok(deck.opaqueBackground,`${label}: hero contrast requires the actual opaque card background`);
  assert.ok(deck.ratio>=4.5,`${label}: hero subtitle contrast ${deck.ratio.toFixed(2)}:1 is below 4.5:1 (${deck.foreground} on ${deck.background})`);
 }
 return decks;
}
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const errors=[];let views=0,clicks=0,heroDeckChecks=0;
 try{
  const context=await browser.newContext();
  await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  for(const width of [1440,390]){
   await page.setViewportSize({width,height:900});
   for(const {slug,episode} of receipt.essays){
    const num=String(episode).padStart(2,'0');
    const source=read(`data/fables-full/source/${num}.json`);
    for(const lang of langs){
     const response=await page.goto(url(slug,lang),{waitUntil:'domcontentloaded'});assert.equal(response.status(),200);
     const heading=page.locator('h1:visible');assert.equal(await heading.count(),1);
     heroDeckChecks+=(await assertHeroDeckContrast(page,`${width} ${slug} ${lang}`)).length;
     const body=page.locator(query[lang]?`.lang-${cls[lang]} .article-body`:'.article-body');
     assert.equal(await body.locator('p').count(),source.texts.length-1);
     assert.equal(await body.locator('hr').count(),source.blocks.filter(x=>x.tag==='hr').length);
     assert.equal(await body.locator('blockquote').count(),source.blocks.filter(x=>x.tag==='quote-start').length);
     if(lang!=='zh-Hant'){
      const texts=lang==='zh-Hans'?source.texts:read(`data/fables-full/translations/${lang}/${num}.json`);
      assert.equal(await heading.textContent(),plain(texts[0]),`${slug} ${lang} title`);
      assert.deepEqual(await body.locator('p').allTextContents(),texts.slice(1).map(plain),`${slug} ${lang} all paragraphs`);
     }
     assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`${width} ${slug} ${lang}`);
     if(query[lang])assert.equal(await page.locator('html').getAttribute('data-lang'),query[lang]);
     else assert.equal(await page.locator('html').getAttribute('lang'),lang);
     views++;
    }
   }
   for(const lang of langs){
    await page.goto(url('index',lang),{waitUntil:'domcontentloaded'});
    const cards=page.locator(query[lang]?`.lang-${cls[lang]} a.essay-card`:'a.essay-card');
    assert.equal(await cards.count(),23);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`index ${lang} ${width}`);
    views++;
   }
  }
  // A query-entry language choice must survive links without a query.
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
   await page.locator('a.back-link').click();await page.waitForURL('**/fables/index.html');
   assert.equal(await page.locator('html').getAttribute('lang'),htmlLang);
   await page.locator(container+'a.essay-card').first().click();await page.waitForURL('**/'+receipt.essays[0].slug+'.html');
   assert.equal(await page.locator('html').getAttribute('lang'),htmlLang);
  }
  await page.goto(url(receipt.essays[0].slug,'zh-Hant')+'&from=qa#language-check');
  for(const code of ['en','zh','zh-hant']){
   await page.locator(`button[data-lang-button="${code}"]`).click();
   const selected=new URL(page.url());
   assert.equal(selected.searchParams.get('lang'),code);
   assert.equal(selected.searchParams.get('from'),'qa');assert.equal(selected.hash,'#language-check');
   await page.reload();assert.equal(await page.locator('html').getAttribute('data-lang'),code);
  }
  await page.setViewportSize({width:320,height:860});
  for(const {slug} of receipt.essays){
   for(const lang of langs){
    await page.goto(url(slug,lang),{waitUntil:'domcontentloaded'});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`320 ${slug} ${lang}`);
    heroDeckChecks+=(await assertHeroDeckContrast(page,`320 ${slug} ${lang}`)).length;
    views++;
   }
  }
  const slug=receipt.essays[13].slug;
  await page.goto(url(slug,'en'));
  for(const code of ['zh','zh-hant','en','zh','en']){
   await page.locator(`button[data-lang-button="${code}"]`).click();clicks++;
   assert.equal(await page.locator('html').getAttribute('data-lang'),code);
   assert.equal(await page.locator('h1:visible').count(),1);
  }
  for(const lang of ['ja','fr','de','es','ko']){
   const link=page.locator(`a.lang-btn[href$="/${lang}/${slug}.html"],a.lang-btn[href="${lang}/${slug}.html"]`);
   const href=await link.getAttribute('href');const wanted=new URL(href,page.url()).href;
   await link.click();await page.waitForURL(wanted);clicks++;
   assert.equal(await page.locator('html').getAttribute('lang'),lang);
  }
  await page.locator('a.lang-btn[href$="?lang=zh"]').click();await page.waitForURL('**?lang=zh');clicks++;
  assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
  await page.goBack();assert.equal(await page.locator('html').getAttribute('lang'),'ko');
  await page.goForward();assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
  await page.evaluate(()=>{localStorage.setItem('nd_lang','invalid');localStorage.setItem('nondubito-lang','invalid')});
  await page.goto(base+prefix+slug+'.html');assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
  // Follow actual navigation and an index card, not just their href strings.
  await page.goto(url(receipt.essays[0].slug,'de'));
  await page.locator('a.series-nav-btn.next').click();await page.waitForURL('**/'+receipt.essays[1].slug+'.html');
  await page.locator('a.series-nav-btn:not(.next)').click();await page.waitForURL('**/'+receipt.essays[0].slug+'.html');
  await page.goto(url('index','fr'));
  await page.locator('a.back-link').click();await page.waitForURL('**/essays/everyday/stories/index.html');
  await page.goBack();assert.equal(await page.locator('html').getAttribute('lang'),'fr');
  await page.goto(url('index','ko'));
  await page.locator('a.essay-card').last().click();await page.waitForURL('**/'+receipt.essays[22].slug+'.html');
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({passed:true,readingViews:views,languageClicks:clicks,heroDeckChecks,widths:[1440,390,320],pageErrors:errors}));
  for(const lang of ['de','ja','ko']){
   await page.goto(url(receipt.essays[0].slug,lang));
   await page.screenshot({path:`/tmp/fables-full-${lang}-mobile.png`,fullPage:false});
   await page.locator('.article-body').scrollIntoViewIfNeeded();
   await page.screenshot({path:`/tmp/fables-full-${lang}-body.png`,fullPage:false});
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
