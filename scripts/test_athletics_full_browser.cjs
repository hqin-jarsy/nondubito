const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
const receipt=JSON.parse(fs.readFileSync(path.join(root,'data/athletics-full/review.json')));
const base=process.argv[2]||'http://127.0.0.1:8774';
const labels={de:'Deutsch',fr:'Français',es:'Español',ja:'日本語',ko:'한국어'};
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try {
  const ctx=await browser.newContext();
  await ctx.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await ctx.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));let checks=0;
  for(const width of [1440,390,320]){
   await page.setViewportSize({width,height:950});
   for(const [key,r] of Object.entries(receipt.manuscripts)){
    const [ep,lang]=key.split('.');await page.goto(`${base}/essays/athletics/${lang}/${ep}.html`);
    assert.equal(await page.locator('h1').innerText(),r.title);
    assert.equal(await page.locator('.athletics-full p').count(),r.paragraphs_by_section.reduce((a,b)=>a+b,0));
    assert.equal(await page.locator('.athletics-full h2').count(),r.paragraphs_by_section.length);
    assert.equal(await page.locator('.lang-select option:checked').innerText(),labels[lang]);
    assert.equal(await page.locator('.lang-select option').count(),8);
    const box=await page.evaluate(()=>({width:document.documentElement.scrollWidth,header:document.querySelector('.essay-header').getBoundingClientRect().bottom,toc:document.querySelector('.athletics-toc').getBoundingClientRect().top,body:document.querySelector('.athletics-full').getBoundingClientRect().width}));
    assert.ok(box.width<=width+1,`${key} ${width}: overflow ${box.width}`);
    assert.ok(box.toc>=box.header-1,`${key}: header overlap`);
    assert.ok(box.body>width*.55||width===1440,`${key}: cramped body ${box.body}`);
    if(width===390){await page.locator('.athletics-toc summary').focus();await page.keyboard.press('Enter');await page.locator('.athletics-toc a').last().click();assert.ok(page.url().endsWith('#section-'+r.paragraphs_by_section.length));}
    if(process.env.ATHLETICS_SCREENSHOTS&&((ep==='ep01'&&lang==='fr'&&width===1440)||(ep==='ep23'&&['ja','ko'].includes(lang)&&width===390))){await page.locator('h1').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(process.env.ATHLETICS_SCREENSHOTS,`${ep}-${lang}-${width}.png`)});}
    checks++;
   }
   for(const lang of Object.keys(labels)){await page.goto(`${base}/essays/athletics/${lang}/index.html`);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth)<=width+1);assert.equal(await page.locator('.entry-row').count(),23);}
  }
  await page.goto(`${base}/essays/athletics/de/ep01.html`);
  await page.locator('.lang-select').selectOption({label:'한국어'});await page.waitForURL('**/ko/ep01.html');
  await page.locator('.series-nav a[href="ep02.html"]').click();await page.waitForURL('**/ko/ep02.html');
  await page.locator('.lang-select').selectOption({label:'中文'});await page.waitForURL('**/athletics/ep02.html');
  assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
  for(const c of receipt.source_corrections.filter(c=>c.edits&&!c.path.endsWith('/index.html'))){
   await page.goto(`${base}/${c.path}`);
   for(const lang of ['zh','en']){
    if(await page.locator('.lang-select').count())await page.locator('.lang-select').selectOption({label:lang==='zh'?'中文':'EN'});
    else await page.locator(`.lang-btn[data-lang="${lang}"]`).click();
    const body=await page.locator('.essay-body.lang-'+lang).innerText();
    for(const e of c.edits.filter(e=>e.lang===lang&&e.scope!=='metadata'))assert.ok(body.includes(e.after.replaceAll('&amp;','&')),[c.path,lang,e.section,e.paragraph].join(' '));
   }
   if(await page.locator('.lang-select').count())await page.locator('.lang-select').selectOption({label:'繁體'});
   else await page.locator('.lang-btn[data-lang="zh-hant"]').click();
   const t=receipt.source_corrections.find(t=>t.path.endsWith('/'+path.basename(c.path,'.html')+'.js'));
   if(t)for(const [,original,traditional]of t.traditional_pairs){assert.ok((await page.locator('.essay-body.lang-zh').innerText()).includes(traditional));}
  }
  const nojs=await browser.newContext({javaScriptEnabled:false});await nojs.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const stat=await nojs.newPage();
  for(const lang of Object.keys(labels)){await stat.goto(`${base}/essays/athletics/${lang}/ep01.html`);assert.ok(await stat.locator('.athletics-full p').count()>50);assert.equal(await stat.locator('.lang-toggle .lang-btn').count(),8);}
  assert.deepEqual(errors,[]);console.log(`OK: ${checks} article/viewport checks, 15 indexes, keyboard TOCs, language/next links, source/Hant corrections, five no-JS editions`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
