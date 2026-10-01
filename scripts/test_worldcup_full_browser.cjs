/* Full-edition reading, navigation and layout; no external requests. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const receipt = JSON.parse(fs.readFileSync(path.join(root, 'data/worldcup-full/review.json')));
const records = receipt.manuscripts;
const latestEpisodes = receipt.batches.at(-1).episodes;
const base = process.argv[2] || 'http://127.0.0.1:8774';
const labels = {de:'Deutsch',fr:'Français',es:'Español',ja:'日本語',ko:'한국어'};
(async () => {
  const browser = await chromium.launch({headless:true, channel:'chrome'});
  try {
    const context = await browser.newContext();
    await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
    const page = await context.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    let checks=0;
    for (const width of [1440,390,320]) {
      await page.setViewportSize({width,height:950});
      for (const [key,record] of Object.entries(records)) {
        const [ep,lang]=key.split('.');
        await page.goto(`${base}/essays/worldcup/${lang}/${ep}.html`);
        assert.equal(await page.locator('h1').innerText(),record.title);
        assert.equal(await page.locator('.worldcup-full p').count(),record.paragraphs_by_section.reduce((a,b)=>a+b,0));
        assert.equal(await page.locator('.worldcup-full h2').count(),record.paragraphs_by_section.length);
        assert.equal(await page.locator('.lang-select option:checked').innerText(),labels[lang]);
        const layout=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,
          header:document.querySelector('.essay-header').getBoundingClientRect().bottom,
          toc:document.querySelector('.worldcup-toc').getBoundingClientRect().top}));
        assert.ok(layout.scroll<=width+1,`${key} ${width}: overflow ${layout.scroll}`);
        assert.ok(layout.toc>=layout.header-1,`${key}: overlapping header`);
        if (width===390) {
          await page.locator('.worldcup-toc summary').focus();
          await page.keyboard.press('Enter');
          await page.locator('.worldcup-toc a').last().click();
          assert.ok(page.url().endsWith('#section-'+record.paragraphs_by_section.length));
        }
        if (process.env.WORLDCUP_SCREENSHOTS && ((ep===latestEpisodes[0]&&lang==='es'&&width===1440)||(ep===latestEpisodes.at(-1)&&lang==='ja'&&width===390))) {
          await page.locator('h1').scrollIntoViewIfNeeded();
          await page.screenshot({path:path.join(process.env.WORLDCUP_SCREENSHOTS,`${ep}-${lang}-${width}.png`)});
        }
        checks++;
      }
      for(const lang of Object.keys(labels)) {
        await page.goto(`${base}/essays/worldcup/${lang}/index.html`);
        assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth)<=width+1,`${lang} index ${width}`);
        assert.equal(await page.locator('.lang-select option:checked').innerText(),labels[lang]);
      }
    }
    await page.goto(`${base}/essays/worldcup/de/ep01.html`);
    await page.locator('.lang-select').selectOption({label:'한국어'});
    await page.waitForURL('**/ko/ep01.html');
    await page.locator('.worldcup-nav-next').click();
    await page.waitForURL('**/ko/ep02.html');
    await page.locator('.lang-select').selectOption({label:'中文'});
    await page.waitForURL('**/worldcup/ep02.html');
    assert.equal(await page.locator('html').getAttribute('data-lang'),'zh');
    for (const correction of receipt.source_corrections || []) {
      await page.goto(`${base}/${correction.path}`);
      for (const edit of correction.edits) {
        const lang=/[\u4e00-\u9fff]/.test(edit.after)?'zh':'en';
        await page.locator(`.lang-btn[data-lang="${lang}"]`).click();
        const body=page.locator(`.essay-body.lang-${lang}`);
        assert.ok(await body.isVisible());
        const text=await body.innerText();
        assert.ok(text.includes(edit.after),`${correction.path}: missing corrected ${lang} text`);
        assert.ok(!text.includes(edit.before),`${correction.path}: obsolete ${lang} text`);
      }
    }
    const staticContext=await browser.newContext({javaScriptEnabled:false});
    await staticContext.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
    const staticPage=await staticContext.newPage();
    for(const lang of Object.keys(labels)) {
      const ep=latestEpisodes[0];
      await staticPage.goto(`${base}/essays/worldcup/${lang}/${ep}.html`);
      assert.equal(await staticPage.locator('.worldcup-full p').count(),records[`${ep}.${lang}`].paragraphs_by_section.reduce((a,b)=>a+b,0));
      assert.equal(await staticPage.locator('.lang-toggle .lang-btn').count(),7);
    }
    assert.deepEqual(errors,[]);
    console.log(`OK: ${checks} article/viewport checks, 15 index checks, keyboard contents, language switching, neighbors, authorized source corrections and five no-JS editions`);
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
