const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8786';
const chapter=process.argv[3]||'ch083';
const chapters=['ch081','ch082','ch083'];
const editions=['','zh-hant/','en/','de/','fr/','es/','ja/','ko/'];
assert.ok(chapters.includes(chapter));
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
  const ctx=await browser.newContext({reducedMotion:'reduce'});
  await ctx.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const originalLines=fs.readFileSync(path.join(__dirname,`../data/originals/hongloumeng/${chapter}.zh.txt`),'utf8').split('\n');
  let checks=0;
  for(const width of [1440,768,390,320]){
   await page.setViewportSize({width,height:900});
   for(const dir of editions)for(const filename of ['index.html',...chapters.map(c=>c+'.html')]){
    await page.goto(`${base}/originals/hongloumeng/${dir}${filename}`);
    assert.equal(await page.locator('h1:visible').count(),1);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    assert.equal(await page.locator('a[href*="ch084"]').count(),0);
    assert.equal(await page.locator('.language-menu a').count(),8);
    if(filename!=='index.html'){
     const lines=fs.readFileSync(path.join(__dirname,`../data/originals/hongloumeng/${filename.replace('.html','.zh.txt')}`),'utf8').split('\n');
     if(!dir||dir==='zh-hant/'){
      assert.equal(await page.locator('.verse p').count(),{'ch081.html':8,'ch082.html':2,'ch083.html':1}[filename]);
      assert.equal(await page.locator('.novel-text p').count(),lines.slice(1).filter(Boolean).length);
      if(!dir)assert.deepEqual(await page.locator('.novel-text p').allTextContents(),lines.slice(1).filter(Boolean));
     }else{
      assert.equal(await page.locator('.novel-text [data-source-unit]').count(),{'ch081.html':101,'ch082.html':67,'ch083.html':32}[filename]);
     }
     await page.locator('.novel-text p').last().scrollIntoViewIfNeeded();
     if(!dir||dir==='zh-hant/')assert.ok((await page.locator('.novel-text').textContent()).includes('下回分解'));
    }
    checks++;
   }
  }
  await page.goto(`${base}/originals/hongloumeng/${chapter}.html`);
  await page.locator('.language-menu summary').click();
  await page.getByRole('link',{name:'繁體中文',exact:true}).click();
  await page.waitForURL(`**/zh-hant/${chapter}.html`);
  await page.locator('.language-menu summary').click();
  await page.getByRole('link',{name:'简体中文',exact:true}).click();
  await page.waitForURL(`**/hongloumeng/${chapter}.html`);
  await page.setViewportSize({width:1440,height:1000});
  await page.screenshot({path:`/tmp/hongloumeng-${chapter}-desktop.png`});
  await page.setViewportSize({width:390,height:844});
  await page.goto(`${base}/originals/hongloumeng/${chapter}.html`);
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:`/tmp/hongloumeng-${chapter}-mobile.png`});
  await page.locator('.verse').scrollIntoViewIfNeeded();
  await page.screenshot({path:`/tmp/hongloumeng-${chapter}-verse.png`});
  const plain=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:900}});
  const p=await plain.newPage();await p.goto(`${base}/originals/hongloumeng/${chapter}.html`);
  assert.equal(await p.locator('.novel-text p').count(),originalLines.slice(1).filter(Boolean).length);
  assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  assert.deepEqual(errors,[]);
  console.log(`PASS: ${checks} responsive page checks, full manuscript parity, poem, language switches and no-JS reading.`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
