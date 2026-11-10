/* Independent audit fixture. It does not modify public pages or source text.
   Run only from an execution context authorized to use an isolated headless browser.
   NODE_PATH=<installed dependencies> node browser-check.cjs http://127.0.0.1:8794 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'../../..');
const tmp='/tmp/value-author-review-20261110';
const base=process.argv[2]||'http://127.0.0.1:8794';
assert.equal(new URL(base).hostname,'127.0.0.1','Loopback-only QA');
const out=path.join(__dirname,'browser-qa');
assert.ok(!fs.existsSync(path.join(out,'run.json')),'Protect an existing browser run; choose a new evidence directory before rerunning');
fs.mkdirSync(path.join(out,'screenshots'),{recursive:true});
const langs=['zh','zh-hant','en','ja','de','fr','es','ko'],slugs=['ep01','prospect'],widths=[320,375,1440];
const expectedPath=path.join(tmp,'expected.json');
const expected=JSON.parse(fs.readFileSync(expectedPath,'utf8'));
const initial=JSON.parse(fs.readFileSync(path.join(tmp,'input-hashes.json'),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
for(const [p,h] of Object.entries(initial))assert.equal(sha(path.join(root,p)),h,'Input changed since expected text was derived: '+p);
const inputFiles=new Set([...Object.keys(initial).map(p=>path.join(root,p)),expectedPath,__filename,path.join(__dirname,'semantic-review.json')]);
for(const s of slugs){
 inputFiles.add(path.join(root,'data/sae-value-full/sources',s+'.json'));
 inputFiles.add(path.join(root,'data/sae-value-full/reviews','en-'+s+'.json'));
 for(const l of langs.filter(l=>!['zh','zh-hant','en'].includes(l)))inputFiles.add(path.join(root,'data/sae-value-full/translations',l,s+'.json'));
}
const inputHashes=Object.fromEntries([...inputFiles].sort().map(p=>[p,sha(p)]));
const primary=l=>['zh','zh-hant','en'].includes(l);
const actual=l=>({'zh':'zh-Hans','zh-hant':'zh-Hant'}[l]||l);
const url=(l,s)=>base+'/essays/sae-value/'+(primary(l)?'':l+'/')+s+'.html'+(primary(l)?'?lang='+l:'');
let browser;const pageErrors=[],views=[],transitions=[],screenshots=[];let version=null;
const report={status:'running',independent_visual_review:'pending',started_at:new Date().toISOString(),base,mode:'isolated-headless-chrome-final-local-pages',inputHashes,views,transitions,screenshots,pageErrors};
async function check(page,l,s,width,kind){
 await page.waitForFunction(wanted=>document.documentElement.lang===wanted,actual(l));
 await page.evaluate(()=>document.fonts.ready);
 const b=page.locator('.essay-body:visible');assert.equal(await b.count(),1,l+'/'+s+' visible body');
 const got=await b.evaluate(n=>Array.from(n.children,x=>x.textContent.replace(/\s+/g,' ').trim()));
 assert.deepEqual(got,expected[l+'/'+s],l+'/'+s+' complete rendered text');
 assert.equal(await page.locator('h1:visible').count(),1,l+'/'+s+' title');
 assert.equal(await page.locator('.lang-toggle .lang-btn').count(),8,l+'/'+s+' toggles');
 const metrics=await page.evaluate(()=>({innerWidth,scrollWidth:document.documentElement.scrollWidth,htmlLang:document.documentElement.lang}));
 assert.equal(metrics.innerWidth,width);assert.ok(metrics.scrollWidth<=width+1,l+'/'+s+' overflow '+metrics.scrollWidth);
 return {kind,language:l,slug:s,width,height:900,units:got.length,all_rendered_units_match:true,...metrics};
}
async function shot(page,l,s,width,unit){
 const n=page.locator('.essay-body:visible').locator(':scope > *').nth(unit-1);
 const rect=await n.evaluate(n=>{const r=n.getBoundingClientRect();window.scrollTo(0,r.top+scrollY-80);return {width:r.width,height:r.height};});
 const name=l+'-'+s+'-'+width+'-u'+unit+'.png',file=path.join(out,'screenshots',name);
 await page.screenshot({path:file,fullPage:false});
 screenshots.push({file:path.relative(root,file),language:l,slug:s,width,height:900,unit,paragraph_rect:rect,focus:'start of changed unit, with 80px clearance for sticky navigation',sha256:sha(file),visually_reviewed:false});
}
(async()=>{
 try{
  browser=await chromium.launch({headless:true,channel:'chrome'});version=browser.version();report.browserVersion=version;
  const context=await browser.newContext({viewport:{width:320,height:900}});
  await context.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
  const page=await context.newPage();page.on('pageerror',e=>pageErrors.push(e.message));
  for(const width of widths){
   await page.setViewportSize({width,height:900});
   for(const l of langs)for(const s of slugs){
    await page.goto(url(l,s),{waitUntil:'load'});views.push(await check(page,l,s,width,'view'));
    for(const unit of s==='ep01'?[200]:[114,137,145])await shot(page,l,s,width,unit);
   }
   for(const s of slugs){
    await page.goto(url('zh',s),{waitUntil:'load'});
    for(const l of ['zh','zh-hant','en','zh-hant','zh']){
     await page.locator('.lang-btn[data-lang="'+l+'"]').click();
     transitions.push(await check(page,l,s,width,'language_transition'));
     assert.equal(new URL(page.url()).searchParams.get('lang'),l,'language route');
    }
   }
   console.log('Passed viewport',width);
  }
  assert.equal(views.length,48);assert.equal(transitions.length,30);assert.equal(screenshots.length,96);assert.deepEqual(pageErrors,[]);
  for(const [p,h] of Object.entries(inputHashes))assert.equal(sha(p),h,'Input changed during run: '+p);
  report.inputsUnchanged=true;report.status='passed';
 }catch(e){report.status='failed';report.failure=String(e);report.stack=e.stack;process.exitCode=1;}
 finally{
  report.finished_at=new Date().toISOString();report.coverage={views:views.length,language_transitions:transitions.length,screenshots:screenshots.length};
  fs.writeFileSync(path.join(out,'run.json'),JSON.stringify(report,null,2)+'\n');
  if(browser)await browser.close();console.log(JSON.stringify({status:report.status,browserVersion:version,...report.coverage,report:path.join(out,'run.json'),failure:report.failure}));
 }
})();
