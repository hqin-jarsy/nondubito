const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.argv[2]||'http://127.0.0.1:8786';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
  const ctx=await browser.newContext({reducedMotion:'reduce'});
  await ctx.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const lines=fs.readFileSync(path.join(__dirname,'../data/originals/hongloumeng/ch081.zh.txt'),'utf8').split('\n');
  let checks=0;
  for(const width of [1440,768,390,320]){
   await page.setViewportSize({width,height:900});
   for(const dir of ['','zh-hant/'])for(const filename of ['index.html','ch081.html']){
    await page.goto(`${base}/originals/hongloumeng/${dir}${filename}`);
    assert.equal(await page.locator('h1:visible').count(),1);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    assert.equal(await page.locator('a[href*="ch082"]').count(),0);
    if(filename==='ch081.html'){
     assert.equal(await page.locator('.verse p').count(),8);
     assert.equal(await page.locator('.novel-text p').count(),lines.slice(1).filter(Boolean).length);
     if(!dir)assert.deepEqual(await page.locator('.novel-text p').allTextContents(),lines.slice(1).filter(Boolean));
     await page.locator('.novel-text p').last().scrollIntoViewIfNeeded();
     assert.ok((await page.locator('.novel-text p').last().textContent()).includes('下回分解'));
    }
    checks++;
   }
  }
  await page.goto(`${base}/originals/hongloumeng/ch081.html`);
  await page.getByRole('link',{name:'繁體中文',exact:true}).click();
  await page.waitForURL('**/zh-hant/ch081.html');
  await page.getByRole('link',{name:'简体中文',exact:true}).click();
  await page.waitForURL('**/hongloumeng/ch081.html');
  await page.setViewportSize({width:1440,height:1000});
  await page.screenshot({path:'/tmp/hongloumeng-ch081-desktop.png'});
  await page.setViewportSize({width:390,height:844});
  await page.goto(`${base}/originals/hongloumeng/ch081.html`);
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:'/tmp/hongloumeng-ch081-mobile.png'});
  await page.locator('.verse').scrollIntoViewIfNeeded();
  await page.screenshot({path:'/tmp/hongloumeng-ch081-verse.png'});
  const plain=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:900}});
  const p=await plain.newPage();await p.goto(`${base}/originals/hongloumeng/ch081.html`);
  assert.equal(await p.locator('.novel-text p').count(),lines.slice(1).filter(Boolean).length);
  assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  assert.deepEqual(errors,[]);
  console.log(`PASS: ${checks} responsive page checks, full manuscript parity, poem, language switches and no-JS reading.`);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
