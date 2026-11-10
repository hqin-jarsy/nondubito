/* Local preview or final-site QA. External resources are blocked. */
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {chromium}=require('playwright');
const base=process.argv[2]||'http://127.0.0.1:8788';
assert.ok(!(process.argv.includes('--preview')&&process.argv.includes('--final')),'Choose preview or final mode');
const mode=process.argv.includes('--preview')?'isolated-preview':process.argv.includes('--final')?'final-local-public-pages':'unspecified';
const slugs=['prequel','ep01','ep02','ep03','ep04','ep05','ep06','prospect'];
const langs=['en','zh','zh-hant','ja','fr','de','es','ko'];
const labels=['EN','中文','繁體','日本語','Français','Deutsch','Español','한국어'];
const primary=l=>['en','zh','zh-hant'].includes(l);
const actual=l=>({'zh':'zh-Hans','zh-hant':'zh-Hant'}[l]||l);
const url=(l,s)=>`${base}/essays/sae-value/${primary(l)?'':l+'/'}${s}.html${primary(l)?'?lang='+l:''}`;
const dataRoot=path.join(__dirname,'../data/sae-value-full');
const readJSON=p=>JSON.parse(fs.readFileSync(p));
const sources=Object.fromEntries(slugs.map(s=>[s,readJSON(path.join(dataRoot,'sources',s+'.json'))]));
const counts=Object.fromEntries(slugs.map(s=>[s,sources[s].body_zh.length]));
const expected={},expectedTitles={},inputHashes={};
for(const l of langs.filter(l=>!primary(l)))for(const s of slugs){
 const file=path.join(dataRoot,'translations',l,s+'.json'),raw=fs.readFileSync(file);
 const item=JSON.parse(raw);assert.equal(item.body.length,counts[s],`${l}/${s}: incomplete manuscript`);
 expected[l+'/'+s]=item.body;expectedTitles[l+'/'+s]=item.title;inputHashes[l+'/'+s]=crypto.createHash('sha256').update(raw).digest('hex');
}
for(const s of slugs){
 expected['zh/'+s]=sources[s].body_zh;
 expected['en/'+s]=[...sources[s].body_en];
 const receipt=readJSON(path.join(dataRoot,'reviews','en-'+s+'.json'));
 for(const change of receipt.changes||[])expected['en/'+s][change.unit-1]=change.after;
}
const root=path.join(__dirname,'..');
const fileHash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const hashFiles=files=>Object.fromEntries(files.map(file=>[path.relative(root,file),fileHash(file)]));
const articleRoot=path.join(root,'essays','sae-value');
const publicFiles=['',...langs.filter(l=>!primary(l))].flatMap(l=>['index',...slugs].map(s=>path.join(articleRoot,l,s+'.html')));
const sourceFiles=slugs.map(s=>path.join(dataRoot,'sources',s+'.json'));
const manuscriptFiles=langs.filter(l=>!primary(l)).flatMap(l=>slugs.map(s=>path.join(dataRoot,'translations',l,s+'.json')));
const indexFiles=langs.filter(l=>!primary(l)).map(l=>path.join(dataRoot,'translations',l,'index.json'));
const englishFiles=slugs.map(s=>path.join(dataRoot,'reviews','en-'+s+'.json'));
const supportFiles=['style.css','classic-reading.js','search.html','search.js','search.css','data/search-index.json',...fs.readdirSync(path.join(root,'data/search')).filter(f=>f.endsWith('.json')).map(f=>'data/search/'+f)].map(f=>path.join(root,f));
const artifactHashes={testScript:hashFiles([__filename]),publicPages:hashFiles(publicFiles),manuscripts:hashFiles(manuscriptFiles),sourceSnapshots:hashFiles(sourceFiles),indexManuscripts:hashFiles(indexFiles),englishCorrections:hashFiles(englishFiles),supportFiles:hashFiles(supportFiles)};
const verifyStableInputs=()=>{for(const group of Object.values(artifactHashes))for(const [file,hash] of Object.entries(group))assert.equal(fileHash(path.join(root,file)),hash,`Input changed during QA: ${file}`)};
const searchEntrypoints=[];
const coverage={views:0,languageTransitions:0,navigationLanguages:0,invalidStorageFallbacks:0,blockedStoragePages:0,noJSForeignPages:0,mobileTables:0,searchResultClicks:0};
async function check(p,l,s){
 await p.waitForFunction(l=>document.documentElement.lang===l,actual(l));
 assert.equal(await p.locator('h1:visible').count(),1,`${l}/${s} heading`);
 assert.equal(await p.locator('.lang-toggle .lang-btn').count(),8);
 if(expectedTitles[l+'/'+s])assert.equal((await p.locator('h1:visible').innerText()).trim(),expectedTitles[l+'/'+s],`${l}/${s}: manuscript title`);
 if(s!=='index'){
  const body=p.locator('.essay-body:visible');assert.equal(await body.count(),1);
  const units=body.locator(':scope > p,:scope > h2,:scope > div');
  assert.equal(await units.count(),counts[s],`${l}/${s}: unit count`);
  // Verify all rendered text, not only a count that an old summary might match.
  if(expected[l+'/'+s]){
   const rendered=await units.evaluateAll(nodes=>nodes.map(n=>n.textContent.replace(/\s+/g,' ').trim()));
   const wanted=await p.evaluate(units=>units.map(html=>{const div=document.createElement('div');div.innerHTML=html;return div.textContent.replace(/\s+/g,' ').trim()}),expected[l+'/'+s]);
   assert.deepEqual(rendered,wanted,`${l}/${s}: rendered manuscript text`);
  }
 }
 assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth)<=p.viewportSize().width+1,`${l}/${s}: overflow`);
}
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});const errors=[];const screenshots=fs.mkdtempSync('/tmp/value-reader-qa-');const startedAt=new Date().toISOString();
 try{
  const ctx=await browser.newContext();
  await ctx.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const p=await ctx.newPage();p.on('pageerror',e=>errors.push(e.message));
  for(const width of [320,375,1440]){
   await p.setViewportSize({width,height:900});
   for(const l of langs)for(const s of ['index',...slugs]){await p.goto(url(l,s));await check(p,l,s);coverage.views++;if(s===slugs[1]&&['de','zh-hant'].includes(l)&&width!==375)await p.screenshot({path:path.join(screenshots,`${l}-${width}.png`)});}
   console.log('Checked viewport',width);
  }
  for(const from of langs)for(const target of langs){
   await p.goto(url(from,slugs[1]));
   const control=p.locator('.lang-toggle .lang-btn').filter({hasText:new RegExp('^'+labels[langs.indexOf(target)]+'$')});
   if(await control.evaluate(e=>e.tagName!=='SPAN'))await control.click();
   await check(p,target,slugs[1]);assert.ok(p.url().includes(slugs[1]+'.html'));coverage.languageTransitions++;
  }
  for(const l of langs){
   await p.goto(url(l,'index'));
   await p.locator(`.essay-card[href^="${slugs[0]}.html"]:visible,.entry-row[href="${slugs[0]}.html"]:visible`).click();await check(p,l,slugs[0]);
   await p.locator(`a[data-primary-route][href*="${slugs[1]}.html"]:visible,.series-nav a[href="${slugs[1]}.html"]:visible`).first().click();await check(p,l,slugs[1]);
   await p.goBack();await check(p,l,slugs[0]);coverage.navigationLanguages++;
  }
  for(const l of ['en','zh','zh-hant']){
   await p.evaluate(()=>localStorage.setItem('nd_lang','garbage'));
   await p.goto(url(l,slugs[2]));await check(p,l,slugs[2]);
   assert.equal(await p.evaluate(()=>localStorage.getItem('nd_lang')),l);
   await p.goto(url('en',slugs[3]).split('?')[0]);await check(p,l,slugs[3]);
  }
  for(const value of ['garbage','ja']){
   await p.evaluate(value=>{localStorage.setItem('nd_lang',value);localStorage.setItem('nondubito-lang',value)},value);
   await p.goto(url('zh',slugs[2]).split('?')[0]);await check(p,'zh',slugs[2]);
   assert.equal(await p.evaluate(()=>localStorage.getItem('nd_lang')),'zh');coverage.invalidStorageFallbacks++;
  }
  if(process.argv.includes('--search'))for(const l of langs)for(const s of [slugs[0],slugs[7]]){
   await p.goto(url(l,s));const title=(await p.locator('h1:visible').innerText()).trim();
   await p.goto(`${base}/search.html?in=${actual(l)}&q=${encodeURIComponent(title)}`);
   const result=p.locator(`[data-search-results] h2 a[href*="essays/sae-value/${primary(l)?'':l+'/'}${s}.html"]`);
   const searchURL=p.url(),resultHref=await result.first().getAttribute('href');
   await result.first().click();await check(p,l,s);coverage.searchResultClicks++;
   searchEntrypoints.push({language:l,slug:s,title,searchURL,resultHref,landedURL:p.url(),landedLanguage:await p.evaluate(()=>document.documentElement.lang)});
  }
  const blocked=await browser.newContext({viewport:{width:320,height:900}});
  await blocked.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  await blocked.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage blocked')}}));
  const q=await blocked.newPage();q.on('pageerror',e=>errors.push(e.message));
  for(const l of ['en','zh','zh-hant']){await q.goto(url(l,slugs[0]));await check(q,l,slugs[0]);coverage.blockedStoragePages++;}
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:320,height:900}});
  await nojs.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  const n=await nojs.newPage();for(const l of langs.filter(l=>!primary(l))){await n.goto(url(l,slugs[0]));await check(n,l,slugs[0]);coverage.noJSForeignPages++;}
  // Verify contained table overflow without losing the right-hand cells.
  await p.setViewportSize({width:320,height:900});
  for(const l of langs){
   await p.goto(url(l,'prequel'));await check(p,l,'prequel');
   const table=p.locator('.essay-body:visible .table-scroll').first();await table.scrollIntoViewIfNeeded();
   if(mode==='final-local-public-pages')assert.equal(await table.locator('table').evaluate(e=>getComputedStyle(e).overflowWrap),'normal',`${l}: table word wrapping`);
   assert.equal(await table.locator('thead th').count(),4);assert.equal(await table.locator('tbody tr').count(),3);
   await p.screenshot({path:path.join(screenshots,`${l}-table-left-320.png`)});
   await table.evaluate(e=>e.scrollLeft=e.scrollWidth);
   const scroll=await table.evaluate(e=>({left:e.scrollLeft,max:e.scrollWidth-e.clientWidth,right:e.getBoundingClientRect().right,last:e.querySelector('tbody tr:last-child td:last-child').getBoundingClientRect().right}));
   assert.ok(scroll.max>0,`${l}: mobile table has a scrollable width`);
   assert.ok(Math.abs(scroll.left-scroll.max)<=1,`${l}: mobile table reaches the end`);
   assert.ok(scroll.last<=scroll.right+1,`${l}: last table column is reachable`);
   assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth)<=321);
   await p.screenshot({path:path.join(screenshots,`${l}-table-320.png`)});coverage.mobileTables++;
   await p.goto(url(l,'ep01'));await check(p,l,'ep01');
   await p.locator('.essay-body:visible > p').nth(3).scrollIntoViewIfNeeded();
   await p.screenshot({path:path.join(screenshots,`${l}-body-320.png`)});
  }
  assert.deepEqual(errors,[]);verifyStableInputs();
  console.log(JSON.stringify({status:'passed',mode,base,startedAt,finishedAt:new Date().toISOString(),...coverage,screenshots,inputHashes,artifactHashes,searchEntrypoints,browserVersion:browser.version(),inputsUnchanged:true,errors}));
 }catch(error){
  console.error(JSON.stringify({status:'failed',mode,base,startedAt,finishedAt:new Date().toISOString(),...coverage,screenshots,inputHashes,artifactHashes,searchEntrypoints,browserVersion:browser.version(),errors,failure:String(error)}));throw error;
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
