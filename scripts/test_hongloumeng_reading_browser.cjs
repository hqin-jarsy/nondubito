// Standalone public-reading browser QA. Never opens a user's browser profile.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const mode=process.env.HLM_READING_MODE||'draft';
assert.ok(['draft','release'].includes(mode),'HLM_READING_MODE must be draft or release');
const language=process.env.HLM_READING_LANGUAGE||'zh-Hans';
assert.ok(['zh-Hans','zh-Hant'].includes(language));
const traditional=language==='zh-Hant';
const bilingual=traditional||process.env.HLM_READING_BILINGUAL==='1';
const canonicalRoot='https://nondubito.net/classics/hongloumeng/'+(traditional?'zh-hant/':'');
const beaconURL='https://static.cloudflareinsights.com/beacon.min.js';
const beaconToken='1c920752456e42b5b5469641245a07c2';
function assertPublicationMetadata(metadata,file,selectedMode){
  assert.ok(['draft','release'].includes(selectedMode));
  assert.equal(metadata.privateCount,0,'Private editorial attributes must never appear');
  const allowed=['data-font','data-chapter','data-title'];
  if(selectedMode==='draft'){
    assert.deepEqual(metadata.robots,['noindex,nofollow']);
    assert.deepEqual(metadata.canonicals,[]);
    assert.deepEqual(metadata.externalScripts,[]);
  }else{
    assert.deepEqual(metadata.robots,[],'Release must not retain draft robots');
    assert.deepEqual(metadata.canonicals,[canonicalRoot+(file==='index.html'?'':file)]);
    assert.equal(metadata.externalScripts.length,1,'Release has exactly the site analytics beacon');
    const beacon=metadata.externalScripts[0];
    assert.equal(beacon.src,beaconURL);
    assert.equal(beacon.type,'module');
    assert.deepEqual(JSON.parse(beacon.config),{token:beaconToken});
    allowed.push('data-cf-beacon');
  }
  assert.ok(metadata.dataAttributes.every(k=>allowed.includes(k)),'Only public data attributes');
}
const root=path.resolve(__dirname,'..');
const input=path.join(root,'data/hongloumeng/first80-public');
const reading=JSON.parse(fs.readFileSync(path.join(input,traditional?'reading.zh-hant.json':'reading.zh.json')));
const manifest=JSON.parse(fs.readFileSync(path.join(input,traditional?'manifest.zh-hant.json':'manifest.json')));
if(mode==='release')assert.equal(manifest.status,'finalized','Release QA requires finalized inputs');
const base=process.env.HLM_READING_BASE||'http://127.0.0.1:8793';
assert.ok(['127.0.0.1','localhost'].includes(new URL(base).hostname),'Local previews only');
const out=process.env.HLM_READING_QA||path.join(root,'data/hongloumeng/first80/qa/public-preview');
const digest=s=>crypto.createHash('sha256').update(s).digest('hex');
const pages=['index.html','edition.html',...reading.chapters.map(c=>`ch${String(c.number).padStart(3,'0')}.html`)];
const body=c=>c.blocks.map(b=>b.text).join('');
const classes=b=>[b.kind,...[['first','layout-first'],['last','layout-last'],['heading','diagram-heading'],['group_start','diagram-group-start']].filter(([k])=>b[k]).map(([,v])=>v)];
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  const browser=await chromium.launch({headless:true,channel:'chrome'});
  const report={status:'running',mode,language,browser_version:browser.version(),reading_sha256:manifest.reading_sha256,body_sha256:manifest.body_sha256,assets_sha256:manifest.build.assets_sha256,checks:[],screenshots:[],errors:[],blocked_requests:[],stubbed_analytics_requests:0,scope:'Automated DOM, controls, navigation, privacy attributes and responsive geometry. Screenshot inspection is recorded separately; not a full human proofread.'};
  const contexts=[];
  async function context(options={}){
    const ctx=await browser.newContext({reducedMotion:'reduce',...options});contexts.push(ctx);
    await ctx.route('**/*',route=>{
      const url=route.request().url();
      if(new URL(url).origin===new URL(base).origin)return route.continue();
      // Verify the beacon markup, but never contact analytics during local QA.
      if(mode==='release'&&url===beaconURL&&route.request().resourceType()==='script'){
        report.stubbed_analytics_requests++;
        return route.fulfill({status:200,contentType:'application/javascript',body:''});
      }
      report.blocked_requests.push(url);return route.abort();
    });
    return ctx;
  }
  try{
    const ctx=await context();const page=await ctx.newPage();
    page.on('pageerror',e=>report.errors.push(e.message));
    const go=async file=>{const response=await page.goto(base+'/'+file);await page.evaluate(()=>document.fonts.ready);return response;};
    for(const width of [1440,768,390,320]){
      await page.setViewportSize({width,height:900});
      for(const file of pages){
        assert.equal((await go(file)).status(),200);
        assert.equal(await page.locator('h1').count(),1);
        assert.equal(await page.locator('html').getAttribute('lang'),language);
        if(bilingual){
          assert.equal(await page.locator('.language-switch a').count(),2);
          assert.equal(await page.locator('.language-switch [aria-current=page]').getAttribute('lang'),language);
          if(mode==='release')assert.deepEqual(await page.locator('link[rel=alternate]').evaluateAll(nodes=>nodes.map(n=>n.hreflang)),['zh-Hans','zh-Hant','x-default']);
        }
        const metadata=await page.evaluate(()=>({
          robots:[...document.querySelectorAll('meta[name="robots"],meta[name="googlebot"]')].map(n=>n.content),
          canonicals:[...document.querySelectorAll('link[rel="canonical"]')].map(n=>n.getAttribute('href')),
          externalScripts:[...document.querySelectorAll('script[src]')].filter(n=>new URL(n.src).origin!==location.origin).map(n=>({src:n.src,type:n.type,config:n.getAttribute('data-cf-beacon')})),
          privateCount:document.querySelectorAll('.reading-notes,[data-source-start],[data-author-change-ids]').length,
          dataAttributes:[...document.querySelectorAll('*')].flatMap(n=>[...n.attributes].map(a=>a.name)).filter(k=>k.startsWith('data-'))
        }));
        assertPublicationMetadata(metadata,file,mode);
        assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),file+' overflow '+width);
        if(file.startsWith('ch')){
          const c=reading.chapters[Number(file.slice(2,5))-1];
          const blocks=await page.locator('.novel-text p').evaluateAll(nodes=>nodes.map(n=>({text:n.textContent,classes:[...n.classList]})));
          assert.equal(blocks.map(b=>b.text).join(''),body(c));
          assert.equal(Array.from(blocks.map(b=>b.text).join('')).length,manifest.chapters[c.number-1].character_count,'Unicode code-point count, not UTF-16 length');
          assert.equal(digest(blocks.map(b=>b.text).join('')),manifest.chapters[c.number-1].body_sha256);
          assert.deepEqual(blocks,c.blocks.map(b=>({text:b.text,classes:classes(b)})));
          if(c.number===41)assert.ok(await page.evaluate(()=>document.fonts.check('21px "ND HLM Rare"','𤫫')),'Embedded U+24AEB font loaded');
          await page.locator('#chapter-nav').scrollIntoViewIfNeeded();assert.ok(await page.locator('#chapter-nav').isVisible());
        }
        report.checks.push({file,width,status:'passed'});
      }
    }
    await page.setViewportSize({width:390,height:900});
    await go('index.html');
    const search=page.locator('#chapter-search');
    for(const [query,count] of [['第六回',1],['80',1],['不存在的回目',0],['',80]]){
      await search.fill(query);assert.equal(await page.locator('[data-chapter]:visible').count(),count);
    }
    await search.fill(traditional?'寶玉':'宝玉');assert.ok(await page.locator('[data-chapter]:visible').count()>1);
    await search.fill('');
    await page.reload();await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.className),'skip');
    await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>document.activeElement.id),'main');
    await go('ch001.html');
    if(bilingual){
      const opposite=traditional?'zh-Hans':'zh-Hant';
      await page.locator('.language-switch a[lang="'+opposite+'"]').click();
      await page.waitForLoadState();
      assert.equal(await page.locator('html').getAttribute('lang'),opposite);
      await page.locator('.language-switch a[lang="'+language+'"]').click();
      await page.waitForURL(base+'/ch001.html');
      assert.equal(await page.locator('html').getAttribute('lang'),language);
      await page.goBack();await page.waitForLoadState();
      assert.equal(await page.locator('html').getAttribute('lang'),opposite);
      await page.goForward();await page.waitForURL(base+'/ch001.html');
    }
    const size=()=>page.locator('.novel-text').evaluate(n=>parseFloat(getComputedStyle(n).fontSize));
    const defaultSize=await size();assert.equal(defaultSize,19);
    await page.locator('[data-font=plus]').focus();await page.keyboard.press('Enter');assert.equal(await size(),20);
    await page.locator('a[rel=next]').click();await page.waitForURL('**/ch002.html');assert.equal(await size(),20);
    await page.goBack();await page.waitForURL('**/ch001.html');assert.equal(await size(),20);
    for(let i=0;i<20;i++)await page.locator('[data-font=plus]').click();assert.equal(await size(),28);
    for(let i=0;i<20;i++)await page.locator('[data-font=minus]').click();assert.equal(await size(),17);
    await page.locator('[data-font=reset]').click();assert.equal(await size(),19);
    await page.setViewportSize({width:1440,height:900});assert.equal(await size(),21);
    await page.evaluate(()=>localStorage.setItem('hlm_reading_font','corrupt'));await page.reload();assert.equal(await size(),21);
    await page.evaluate(()=>localStorage.setItem('hlm_reading_font','999'));await page.reload();assert.equal(await size(),21);
    await page.locator('[data-font=reset]').click();assert.equal(await page.evaluate(()=>localStorage.getItem('hlm_reading_font')),null);
    const disabled=await context();await disabled.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage denied')}}));
    const blockedPage=await disabled.newPage();await blockedPage.goto(base+'/ch001.html');
    await blockedPage.locator('[data-font=plus]').click();assert.equal(await blockedPage.locator('.novel-text').evaluate(n=>parseFloat(getComputedStyle(n).fontSize)),22);
    await blockedPage.locator('[data-font=reset]').click();assert.equal(await blockedPage.locator('.novel-text').evaluate(n=>parseFloat(getComputedStyle(n).fontSize)),21);
    const nojs=await context({javaScriptEnabled:false,viewport:{width:390,height:900}});const staticPage=await nojs.newPage();
    await staticPage.goto(base+'/index.html');assert.equal(await staticPage.locator('[data-chapter]:visible').count(),80);
    await staticPage.goto(base+'/ch008.html');assert.equal(await staticPage.locator('.novel-text').textContent(),body(reading.chapters[7]));assert.equal(await staticPage.locator('.diagram').count(),8);
    await staticPage.locator('a[rel=next]').click();await staticPage.waitForURL('**/ch009.html');assert.equal(await staticPage.locator('.novel-text').textContent(),body(reading.chapters[8]));
    const combined=reading.chapters.map(body).join('');
    report.unicode={codepoint_count:Array.from(combined).length,utf16_units:combined.length,non_bmp_characters:Array.from(combined).filter(c=>c.codePointAt(0)>0xffff).map(c=>({text:c,codepoint:'U+'+c.codePointAt(0).toString(16).toUpperCase()}))};
    assert.equal(report.unicode.codepoint_count,manifest.character_count);
    report.interactions=['Chinese and numeric search; empty search and no matches','Keyboard skip link and font controls','Font persistence across navigation and Back; min/max bounds; reset; responsive default','Invalid and unavailable localStorage','No-JS full catalog, exact body, diagram and chapter navigation'];
    const samples=[
      {"file": "ch004.html", "name": "removed-tail-04", "selector": "#chapter-nav"},
      {"file": "ch009.html", "name": "removed-tail-09", "selector": "#chapter-nav"},
      {"file": "ch024.html", "name": "hair-glyph-24", "text": "挽着个䰖", "anchorText": "挽着个䰖"},
      {"file": "ch029.html", "name": "rare-name-29", "text": "贾璜、贾㻞、贾琼", "anchorText": "贾璜、贾㻞、贾琼"},
      {"file": "ch058.html", "name": "repair-bamboo-58", "text": "也有修竹的", "anchorText": "也有修竹的"},
      {"file": "ch062.html", "name": "beijing-word-62", "text": "满嘴里汗巴的胡说了", "anchorText": "满嘴里汗巴的胡说了"},
      {file:'index.html',name:'index-top'},
      {file:'index.html',name:'index-catalog',selector:'#batch01'},
      {file:'edition.html',name:'edition'},
      {file:'ch001.html',name:'chapter-one-top'},
      {file:'ch001.html',name:'haole-ge',text:'世人都晓神仙好，惟有功名忘不了！'},
      {file:'ch008.html',name:'jade-diagram',selector:'.diagram'},
      {file:'ch013.html',name:'rare-name',text:'贾㻞'},
      {file:'ch027.html',name:'zanghua-yin',text:'花谢花飞'},
      {file:'ch080.html',name:'chapter-eighty-boundary',selector:'#chapter-nav'},
      {file:'ch063.html',name:'hair-glyph-63',text:'随便挽着䰖儿'},
      {file:'ch071.html',name:'rare-name-71',text:'因贾㻞之母'},
      {file:'ch064.html',name:'luzhu-updated-poem',exactText:'绿珠'},
      {file:'ch001.html',name:'reading-transition-01',text:'可巧这日，拄了拐杖'},
      {file:'ch019.html',name:'reading-transitions-19',text:'这里素日有个小书房'},
      {file:'ch075.html',name:'reading-transition-75-baoyu',text:'向纸上写了，呈与贾政看'},
      {file:'ch075.html',name:'reading-transition-75-jialan',text:'当下贾兰见奖励宝玉'},
      {file:'ch079.html',name:'reading-transition-79',text:'倒替你耽心虑后呢'},
      {file:'ch041.html',name:'tea-vessel-astral-41',text:'𤫫瓟斝',anchorText:'𤫫瓟斝'},
      {file:'ch041.html',name:'tea-vessel-qiao-41',text:'杏犀䀉',anchorText:'杏犀䀉'},
      {file:'ch001.html',name:'opening-selfstatement-tail',text:'阅者切记之。',anchorText:'阅者切记之。'},
      {file:'ch001.html',name:'opening-eight-lines',text:'浮生着甚苦奔忙，'},
      {file:'ch019.html',name:'ending-couplet-19',text:'戏谑主人调笑仆，'},
      {file:'ch019.html',name:'quote-knowledge-19',text:'灰还有形有迹，还有知识。',anchorText:'灰还有形有迹，还有知识。'},
      {file:'ch019.html',name:'quote-mouse-19',text:'这个不难，等我变来。',anchorText:'这个不难，等我变来。'},
      {file:'ch033.html',name:'quote-mother-33',text:'倘或老太太一时不自在了，岂不事大！',anchorText:'倘或老太太一时不自在了，岂不事大！'}
    ];
    if(traditional){
      const original=JSON.parse(fs.readFileSync(path.join(input,'reading.zh.json')));
      for(const sample of samples){
        if(!sample.text&&!sample.exactText)continue;
        const index=Number(sample.file.slice(2,5))-1;
        const position=original.chapters[index].blocks.findIndex(b=>sample.exactText?b.text===sample.exactText:b.text.includes(sample.text));
        assert.ok(position>=0,'Screenshot source position: '+sample.name);
        const source=original.chapters[index].blocks[position].text;
        const target=reading.chapters[index].blocks[position].text;
        const needle=sample.anchorText||sample.exactText||sample.text;
        const offset=source.indexOf(needle);
        assert.ok(offset>=0);
        const start=Array.from(source.slice(0,offset)).length;
        const length=Array.from(needle).length;
        assert.equal(Array.from(source).length,Array.from(target).length,'Script conversion preserves character positions');
        sample.text=target;
        sample.anchorText=Array.from(target).slice(start,start+length).join('');
        delete sample.exactText;
      }
    }
    for(const width of [1440,390]){
      await page.setViewportSize({width,height:1000});
      for(const sample of samples){
        await go(sample.file);
        const target=sample.exactText?page.getByText(sample.exactText,{exact:true}).first():sample.selector?page.locator(sample.selector).first():sample.text?page.locator('.novel-text p').filter({hasText:sample.text}).first():null;
        if(target){
          await target.scrollIntoViewIfNeeded();
          await target.evaluate((n,needle)=>{
            let top=n.getBoundingClientRect().top;
            if(needle){
              const text=n.firstChild;
              const assertText=text && text.nodeType===Node.TEXT_NODE;
              if(!assertText)throw new Error('Expected plain paragraph text');
              const start=text.textContent.indexOf(needle);
              if(start<0)throw new Error('Missing screenshot text');
              const range=document.createRange();
              // DOM Range offsets are UTF-16 positions; counts above use Unicode code points.
              range.setStart(text,start);range.setEnd(text,start+needle.length);
              top=range.getBoundingClientRect().top;
            }
            scrollTo(0,Math.max(0,top+scrollY-100));
          },sample.anchorText||null);
        }
        const filename=sample.name+'-'+width+'.png';
        await page.screenshot({path:path.join(out,filename)});
        report.screenshots.push({file:filename,page:sample.file,width,region:sample.name,sha256:digest(fs.readFileSync(path.join(out,filename)))});
      }
    }
    assert.deepEqual(report.errors,[]);assert.deepEqual(report.blocked_requests,[]);
    report.status='passed';
    console.log('PASS browser ('+mode+'): '+report.checks.length+' responsive page checks, interactions, no-JS, '+report.screenshots.length+' screenshots');
  }catch(error){report.status='failed';report.errors.push(error.stack);throw error;}
  finally{fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify(report,null,2)+'\n');for(const ctx of contexts)await ctx.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
