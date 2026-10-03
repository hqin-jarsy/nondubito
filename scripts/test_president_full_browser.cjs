/* Local rendered smoke tests: run a localhost server, then NODE_PATH=... node this-file. */
const {chromium}=require('playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const origin=process.env.PRESIDENT_PREVIEW_ORIGIN||'http://127.0.0.1:8786';
const langs=['zh','en','zh-hant','ja','fr','de','es','ko'];
(async()=>{
  const browser=await chromium.launch({channel:'chrome',headless:true});
  const context=await browser.newContext();
  await context.route('**/*',route=>route.request().url().startsWith(origin)?route.continue():route.abort());
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  const results=[];
  try{
    for(const width of [390,768,1440]){
      await page.setViewportSize({width,height:900});
      for(let n=1;n<=5;n++)for(const lang of langs){
        const ep=`ep${String(n).padStart(2,'0')}`;
        const inline=['zh','en','zh-hant'].includes(lang);
        const path=inline?`essays/president/${ep}.html?lang=${lang}`:`essays/president/${lang}/${ep}.html`;
        const response=await page.goto(`${origin}/${path}`,{waitUntil:'load'});assert.equal(response.status(),200,path);
        const metrics=await page.evaluate(()=>{
          const visible=e=>!!(e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden');
          const h=[...document.querySelectorAll('h1')].filter(visible);
          const bodies=[...document.querySelectorAll('.essay-body')].filter(visible);
          const header=document.querySelector('.essay-header');
          const paragraph=bodies[0]?.querySelector('p');
          return {overflow:document.documentElement.scrollWidth-innerWidth,h1:h.length,bodies:bodies.length,
            characters:bodies[0]?.innerText.length,title:h[0]?.innerText,language:document.documentElement.lang,
            choices:document.querySelectorAll('.lang-select option').length,
            overlap:paragraph?.getBoundingClientRect().top<header?.getBoundingClientRect().bottom,
            headerPosition:getComputedStyle(header).position,selected:document.querySelector('.lang-select')?.selectedOptions[0]?.textContent};
        });
        assert(metrics.overflow<=1,`${path} width${width} horizontal overflow ${metrics.overflow}`);
        assert.equal(metrics.h1,1,path);assert.equal(metrics.bodies,1,path);assert.equal(metrics.choices,8,path);
        assert.equal(metrics.overlap,false,path);assert.equal(metrics.headerPosition,'static',path);
        assert(await page.locator('.lang-select').isVisible(),path+' hidden language menu');
        const menu=await page.locator('.lang-select').evaluate(e=>({color:getComputedStyle(e).color,background:getComputedStyle(e).backgroundColor,rect:e.getBoundingClientRect().toJSON()}));
        assert.notEqual(menu.color,'rgb(245, 240, 232)',path+' cream-on-cream menu');
        assert(menu.rect.left>=0&&menu.rect.right<=width&&menu.rect.top>=0&&menu.rect.bottom<=900,path+' menu offscreen');
        assert(metrics.characters>5000,path+' truncated body');
        if(lang==='zh-hant'){assert.equal(metrics.language,'zh-Hant');assert(metrics.title.includes('篇'));}
        if(!inline){
          await page.locator('.president-toc summary').click();
          await page.locator('.president-toc a').last().click();
          assert(/#section-[78]$/.test(page.url()),path+' TOC');
        }
        results.push({path,width,...metrics});
      }
    }
    // Actual select navigation in both directions, plus text restoration.
    await page.goto(`${origin}/essays/president/ep01.html?lang=zh`);
    const chinese=await page.locator('.essay-body.lang-zh').innerText();
    await page.selectOption('.lang-select',{label:'繁體中文'});
    await page.waitForFunction(()=>document.documentElement.lang==='zh-Hant');
    const traditional=await page.locator('.essay-body.lang-zh').innerText();assert.notEqual(chinese,traditional);
    await page.selectOption('.lang-select',{label:'简体中文'});
    await page.waitForFunction(()=>document.documentElement.lang==='zh-Hans');
    assert.equal(await page.locator('.essay-body.lang-zh').innerText(),chinese);
    for(const [code,label] of [['de','Deutsch'],['fr','Français'],['es','Español'],['ja','日本語'],['ko','한국어']]){
      await Promise.all([page.waitForURL(`**/${code}/ep01.html`),page.selectOption('.lang-select',{label})]);
      assert.equal(await page.locator('.lang-select option').count(),8);
    }
    await Promise.all([page.waitForURL('**/ep01.html?lang=en'),page.selectOption('.lang-select',{label:'English'})]);
    assert.equal(await page.locator('.essay-body.lang-en').isVisible(),true);
    for(const lang of ['ja','fr','de','es','ko']){
      await page.goto(`${origin}/essays/president/${lang}/index.html`);
      assert.equal(await page.locator('.lang-select option').count(),7);
      assert(await page.locator('.lang-select').isVisible());
      assert.equal(await page.locator('a[href^="ep"][href$=".html"]').count(),26);
    }
    await page.goto(`${origin}/essays/president/ep05.html?lang=zh-hant`);
    await page.locator('a[href="ep06.html"]').click();
    assert.equal(await page.locator('.essay-body.lang-zh').isVisible(),true);
    assert.equal(await page.locator('.essay-body.lang-en').isVisible(),false);
    await page.setViewportSize({width:390,height:900});
    await page.goto(`${origin}/essays/president/fr/ep01.html`);
    await page.screenshot({path:'/private/tmp/president-batch01-mobile.png',fullPage:false});
    await page.setViewportSize({width:1440,height:900});
    await page.goto(`${origin}/essays/president/ep03.html?lang=zh-hant`);
    await page.screenshot({path:'/private/tmp/president-batch01-desktop.png',fullPage:false});
    assert.deepEqual(errors,[]);
    fs.writeFileSync('/private/tmp/president-batch01-browser.json',JSON.stringify({tested:results.length,errors,results},null,2)+'\n');
    console.log(`OK: ${results.length} viewport/language pages; five-language roundtrip; ZH/Hant restoration; no page errors`);
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
