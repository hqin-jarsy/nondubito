const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
// Offline smoke test using a fresh browser profile. External fonts are blocked.
// Geometry checks do not substitute for editorial or visual review.
const R=path.resolve(__dirname,'..');
const dirs=process.argv.slice(2);
const profile=fs.mkdtempSync('/tmp/nd-review-profile-');
const chrome=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',['--headless','--disable-gpu','--no-first-run','--disable-background-networking','--disable-sync','--host-resolver-rules=MAP * ~NOTFOUND','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{let ws;try{
let portfile=path.join(profile,'DevToolsActivePort');for(let i=0;i<100&&!fs.existsSync(portfile);i++)await sleep(100);let port=fs.readFileSync(portfile,'utf8').split('\n')[0];let list=await(await fetch(`http://127.0.0.1:${port}/json/list`)).json();ws=new WebSocket(list.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let serial=0,pending=new Map(),onload=null;ws.onmessage=e=>{let m=JSON.parse(e.data);if(m.id){let q=pending.get(m.id);if(q){pending.delete(m.id);m.error?q.reject(m.error):q.resolve(m.result)}}else if(m.method==='Page.loadEventFired'&&onload){onload();onload=null}};
function call(method,params={}){return new Promise((resolve,reject)=>{let id=++serial;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))})}
await call('Page.enable');let count=0,failures=[];
for(let width of [390,1440]){
await call('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:width===390});
for(let dir of dirs)for(let lang of ['ja','fr','de','es','ko']){
let folder=path.join(R,dir,lang);if(!fs.existsSync(folder))continue;
for(let filename of fs.readdirSync(folder).filter(x=>x.endsWith('.html'))){
let loaded=new Promise((resolve,reject)=>{let t=setTimeout(()=>reject(new Error('load timeout '+filename)),10000);onload=()=>{clearTimeout(t);resolve()}});await call('Page.navigate',{url:'file://'+path.join(folder,filename)});await loaded;
let result=await call('Runtime.evaluate',{expression:`JSON.stringify({width:innerWidth,scroll:document.documentElement.scrollWidth,lang:document.documentElement.lang,h1:document.querySelectorAll('h1').length,body:document.querySelector('.essay-body')?.innerText.length,links:document.querySelectorAll('.site-shell-language-options a').length||document.querySelectorAll('.lang-toggle a').length})`,returnByValue:true});let s=JSON.parse(result.result.value);count++;if(s.scroll>s.width+1||s.lang!==lang||s.h1!==1||s.body<100||s.links!==8)failures.push({dir,lang,filename,width,...s});
if(width===390&&lang==='ja'&&filename!=='index.html'&&filename===fs.readdirSync(folder).filter(x=>x.endsWith('.html')&&x!=='index.html').sort()[0]){let shot=await call('Page.captureScreenshot',{format:'png'});fs.writeFileSync('/tmp/nd-'+path.basename(dir)+'-mobile.png',Buffer.from(shot.data,'base64'))}
}}}
for(let width of [390,1440]){await call('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:width===390});for(let dir of dirs){for(let filename of fs.readdirSync(path.join(R,dir)).filter(x=>x.endsWith('.html'))){for(let lang of ['en','zh','zh-hant']){let loaded=new Promise((resolve,reject)=>{let t=setTimeout(()=>reject(new Error('load timeout')),10000);onload=()=>{clearTimeout(t);resolve()}});await call('Page.navigate',{url:'file://'+path.join(R,dir,filename)+'?lang='+lang});await loaded;let result=await call('Runtime.evaluate',{expression:`JSON.stringify({width:innerWidth,scroll:document.documentElement.scrollWidth,lang:document.documentElement.dataset.lang})`,returnByValue:true});let st=JSON.parse(result.result.value);count++;if(st.scroll>st.width+1||st.lang!==lang)failures.push({dir,filename,width,expected:lang,...st});}}}}
console.log(JSON.stringify({count,failures}));if(failures.length)process.exitCode=1;
}finally{if(ws)ws.close();chrome.kill();}})().catch(e=>{console.error(e);chrome.kill();process.exitCode=1});
