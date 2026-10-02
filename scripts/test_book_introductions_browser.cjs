/* Start a local static server and finish the search-index build before running.
 * NODE_PATH=/path/to/node_modules node scripts/test_book_introductions_browser.cjs http://127.0.0.1:8788
 * Uses isolated headless Chrome, never the user's browser profile.
 * BOOKS_SCREENSHOTS=/absolute/existing/directory optionally saves three views.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');

const root = path.resolve(__dirname, '..');
const base = new URL(process.argv[2] || 'http://127.0.0.1:8788');
const languages = {en: 'en', zh: 'zh-Hans', 'zh-hant': 'zh-Hant'};
const languageClasses = {en: 'lang-en', zh: 'lang-zh', 'zh-hant': 'lang-hant'};
const slugs = fs.readdirSync(path.join(root, 'data/nonfiction')).filter(name => name.endsWith('.json')).map(name => name.slice(0, -5)).sort();
const newSlugs = slugs.filter(slug => !['raising-hare', 'small-is-beautiful'].includes(slug));
const revisedSlugs = new Set(slugs.filter(slug => slug !== 'raising-hare'));
const books = Object.fromEntries(slugs.map(slug => [slug,
  JSON.parse(fs.readFileSync(path.join(root, 'data/nonfiction', slug + '.json'), 'utf8'))]));
const routes = [
  {name: 'books hub', url: '/essays/books/index.html'},
  {name: 'nonfiction shelf', url: '/essays/nonfiction/index.html'},
  ...slugs.map(slug => ({name: slug, slug, url: `/essays/nonfiction/${slug}.html`}))
];
const failures = [];
let checks = 0;

async function check(label, action) {
  try {
    await action();
    checks++;
  } catch (error) {
    failures.push(`${label}: ${error.message}`);
    console.error(`FAIL ${label}: ${error.message}`);
  }
}

async function visit(page, pathname, lang, hash = '') {
  const url = new URL(pathname, base);
  url.searchParams.set('lang', lang);
  url.hash = hash;
  const response = await page.goto(url.href, {waitUntil: 'load'});
  assert.ok(response && response.ok(), `HTTP failure at ${url.href}`);
  await assertLanguage(page, lang);
}

async function assertLanguage(page, lang) {
  await page.waitForFunction(({mode, code}) =>
    document.documentElement.dataset.lang === mode && document.documentElement.lang === code,
  {mode: lang, code: languages[lang]});
  assert.equal(await page.locator('main h1:visible').count(), 1, 'one visible page title');
  for (const [other, className] of Object.entries(languageClasses)) {
    if (other !== lang) {
      assert.equal(await page.locator(`main .${className}:visible`).count(), 0,
        `unexpected visible ${other} content in ${lang}`);
    }
  }
}

async function assertLayout(page, label) {
  const layout = await page.evaluate(() => {
    const width = document.documentElement.clientWidth;
    const overflow = [...document.querySelectorAll('main *, header *, [data-site-shell-drawer] *')]
      .filter(el => el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden')
      .map(el => ({el, box: el.getBoundingClientRect()}))
      .filter(({box}) => box.width && (box.left < -1 || box.right > width + 1))
      .slice(0, 8).map(({el, box}) => `${el.tagName}.${el.className}: ${box.left.toFixed(1)}..${box.right.toFixed(1)}`);
    return {width, page: document.documentElement.scrollWidth, body: document.body.scrollWidth, overflow};
  });
  assert.ok(layout.page <= layout.width + 1 && layout.body <= layout.width + 1,
    `${label}: horizontal overflow ${JSON.stringify(layout)}`);
  assert.deepEqual(layout.overflow, [], `${label}: content exceeds the viewport`);
}

async function switchLanguage(page, lang) {
  const dropdown = page.locator('.site-shell-language');
  let choice;
  if (await dropdown.isVisible()) {
    await dropdown.locator('summary').click();
    choice = dropdown.locator(`[data-set-language="${lang}"]`);
  } else {
    const menu = page.locator('[data-site-shell-menu]');
    if (await menu.getAttribute('aria-expanded') !== 'true') await menu.click();
    choice = page.locator(`.site-shell-mobile-languages [data-set-language="${lang}"]`);
  }
  await choice.click();
  await assertLanguage(page, lang);
  assert.equal(new URL(page.url()).searchParams.get('lang'), lang, 'language query is updated');
  assert.equal(await choice.getAttribute('aria-pressed'), 'true');
  await page.keyboard.press('Escape');
}

async function assertMobileMenu(page) {
  const button = page.locator('[data-site-shell-menu]');
  const drawer = page.locator('[data-site-shell-drawer]');
  assert.ok(await button.isVisible(), 'mobile menu button is visible');
  assert.equal(await button.getAttribute('aria-expanded'), 'false');
  assert.equal(await drawer.isVisible(), false);
  await button.click();
  assert.equal(await button.getAttribute('aria-expanded'), 'true');
  assert.ok(await drawer.isVisible());
  assert.equal(await drawer.locator('nav a:visible').count(), 5);
  assert.equal(await drawer.locator('[data-set-language]:visible').count(), 3);
  await assertLayout(page, 'open mobile menu');
  await page.keyboard.press('Escape');
  assert.equal(await button.getAttribute('aria-expanded'), 'false');
  assert.equal(await drawer.isVisible(), false);
}

(async () => {
  const browser = await chromium.launch({headless: true, channel: process.env.BOOKS_BROWSER_CHANNEL || 'chrome'});
  try {
    const context = await browser.newContext({viewport: {width: 1440, height: 950}, reducedMotion: 'reduce'});
    context.setDefaultTimeout(10000);
    // Local pages only: do not depend on third-party fonts or make review-site requests.
    await context.route('**/*', route => new URL(route.request().url()).origin === base.origin
      ? route.continue() : route.abort());
    const page = await context.newPage();
    const runtimeErrors = [];
    const httpErrors = [];
    page.on('pageerror', error => runtimeErrors.push(`${page.url()}: ${error.message}`));
    page.on('response', response => {
      if (new URL(response.url()).origin === base.origin && response.status() >= 400) {
        httpErrors.push(`${response.status()} ${response.url()}`);
      }
    });

    for (const width of [1440, 390, 320]) {
      await page.setViewportSize({width, height: 950});
      for (const route of routes) {
        for (const lang of Object.keys(languages)) {
          await check(`${route.name} ${lang} ${width}`, async () => {
            await visit(page, route.url, lang);
            await assertLayout(page, route.name);
            const title = page.locator('main h1:visible');
            assert.equal(await page.title(), `${(await title.innerText()).trim()} — Non Dubito`);
            const titleBox = await title.boundingBox();
            const headerBox = await page.locator('header.site-shell-header').boundingBox();
            assert.ok(titleBox.y >= headerBox.y + headerBox.height - 1, 'title is below the header');
            if (route.slug) {
              const article = page.locator('article.rf-prose:visible');
              assert.equal(await article.count(), 1, 'one visible language body');
              assert.equal(await article.getAttribute('lang'), languages[lang]);
              assert.ok((await article.innerText()).length > 1800, 'complete visible prose');
              if (revisedSlugs.has(route.slug)) {
                const sectionCount = (books[route.slug].zh_body.match(/^## /gm) || []).length;
                assert.equal(await article.locator('h2').count(), sectionCount, 'all manuscript sections remain');
                assert.equal(await article.locator('a[href^="https://"]').count(), 0, 'sources stay outside the prose');
              }
              if (route.slug === 'small-is-beautiful') {
                const revised = page.locator('.rf-guide-meta time[datetime="2026-09-28"]');
                assert.equal(await revised.count(), 1, 'Small revision date exists');
                assert.ok(await revised.isVisible(), 'Small revision date is visible');
                const label = {en: 'Revised', zh: '修订', 'zh-hant': '修訂'}[lang];
                assert.ok((await page.locator('.rf-guide-meta').innerText()).includes(label));
              }
              assert.equal(await page.locator('.rf-source-card').count(), books[route.slug].sources.length);
              await page.locator('.rf-actions a[href="#sources"]').click();
              assert.equal(new URL(page.url()).hash, '#sources', 'source anchor is reached');
              await page.waitForFunction(() => {
                const box = document.querySelector('#source-heading').getBoundingClientRect();
                return box.top >= 0 && box.top < innerHeight;
              });
              const sourceBox = await page.locator('#source-heading').boundingBox();
              assert.ok(sourceBox.y >= 0 && sourceBox.y < 950, 'source heading is in view');
              await assertLayout(page, `${route.slug} sources`);
            } else {
              assert.equal(await page.locator('article.rf-prose:visible').count(), 0);
              if (route.name === 'nonfiction shelf') {
                assert.equal(await page.locator('.rf-book-card').count(), slugs.length);
                for (const slug of slugs) assert.equal(await page.locator(`.rf-book-card[href="${slug}.html"]`).count(), 1);
              } else {
                assert.ok(await page.locator('main a[href="../nonfiction/index.html"]').first().isVisible());
                assert.equal(await page.locator('.rf-book-card[href*="../nonfiction/"]').count(), 2);
              }
            }
            if (width < 768) await assertMobileMenu(page);
          });
        }
      }
      console.log(`Completed viewport ${width}px`);
    }

    await page.setViewportSize({width: 390, height: 950});
    for (const route of routes) {
      await check(`${route.name}: switch, reload, retain anchor`, async () => {
        const hash = route.slug ? '#sources' : '';
        await visit(page, route.url, 'en', hash);
        for (const lang of ['zh', 'zh-hant', 'en']) {
          await switchLanguage(page, lang);
          assert.equal(new URL(page.url()).hash, hash);
          await page.reload({waitUntil: 'load'});
          await assertLanguage(page, lang);
          assert.equal(new URL(page.url()).searchParams.get('lang'), lang);
          assert.equal(new URL(page.url()).hash, hash);
        }
      });
    }

    for (const lang of Object.keys(languages)) {
      await check(`hub-to-shelf-to-article navigation ${lang}`, async () => {
        await visit(page, '/essays/books/index.html', lang);
        await page.locator('main a[href="../nonfiction/index.html"]').first().click();
        await assertLanguage(page, lang);
        await page.locator('.rf-book-card[href="being-mortal.html"]').click();
        await assertLanguage(page, lang);
        await page.locator('.rf-next a[href="seeing-like-a-state.html"]').click();
        await assertLanguage(page, lang);
        await page.locator('.rf-return').click();
        await assertLanguage(page, lang);
        assert.equal(new URL(page.url()).pathname, '/essays/nonfiction/index.html');
      });
    }

    const localizedTitles = {
      'the-book-of-delights': {zh: '欢喜之书', 'zh-hant': '歡喜之書'},
      'a-lifes-work': {zh: '成为母亲', 'zh-hant': '成為母親'},
      'wintering': {zh: '过冬', 'zh-hant': '過冬'},
      'youre-not-listening': {zh: '你都没在听', 'zh-hant': '你都沒在聽'},
      'yowai-robotto': {zh: '弱机器人', 'zh-hant': '弱機器人'},
      'educated': {zh: '你当像鸟飞往你的山', 'zh-hant': '你當像鳥飛往你的山'},
      'because-internet': {zh: 'Because Internet', 'zh-hant': 'Because Internet'},
      'ways-of-seeing': {zh: '观看之道', 'zh-hant': '觀看之道'},
      'the-personality-brokers': {zh: 'MBTI的前世今生', 'zh-hant': 'MBTI的前世今生'},
      'the-living-mountain': {zh: '活山', 'zh-hant': '活山'},
      'how-to-do-nothing': {zh: '如何无所事事', 'zh-hant': '如何無所事事'},
      'seeing-like-a-state': {zh: '国家的视角', 'zh-hant': '國家的視角'},
      'being-mortal': {zh: '最好的告别', 'zh-hant': '最好的告別'},
      'the-art-of-gathering': {zh: '聚会', 'zh-hant': '聚會'},
      'four-thousand-weeks': {zh: '四千周', 'zh-hant': '四千周'},
      'the-craftsman': {zh: '匠人', 'zh-hant': '匠人'},
      'the-serviceberry': {zh: '礼物经济', 'zh-hant': '禮物經濟'},
      'the-sound-of-a-wild-snail-eating': {zh: '蜗牛教我慢慢活', 'zh-hant': '蝸牛教我慢慢活'},
      'palaces-for-the-people': {zh: '没有人是一座孤岛', 'zh-hant': '沒有人是一座孤島'},
      'the-other-significant-others': {zh: 'The Other Significant Others', 'zh-hant': 'The Other Significant Others'}
    };
    for (const slug of newSlugs) {
      for (const lang of Object.keys(languages)) {
        const title = lang === 'en' ? books[slug].book_en : localizedTitles[slug][lang];
        for (const query of [title, books[slug].author]) {
          await check(`search ${lang}: ${query}`, async () => {
            const params = new URLSearchParams({lang: 'en', in: languages[lang], domain: 'stories'});
            await page.goto(new URL(`/search.html?${params}`, base).href, {waitUntil: 'load'});
            await page.locator('[data-search-input]').fill(query);
            const result = page.locator(`[data-search-results] a[href*="essays/nonfiction/${slug}.html"]`);
            await result.waitFor({state: 'visible'});
            assert.equal(new URL(await result.getAttribute('href'), base).searchParams.get('lang'), lang,
              'search result carries the selected reading language');
            await assertLayout(page, `search ${query}`);
            await result.click();
            await assertLanguage(page, lang);
            assert.equal(new URL(page.url()).pathname, `/essays/nonfiction/${slug}.html`);
            assert.equal(await page.locator('article.rf-prose:visible').getAttribute('lang'), languages[lang]);
          });
        }
      }
    }

    if (process.env.BOOKS_SCREENSHOTS) {
      const output = path.resolve(process.env.BOOKS_SCREENSHOTS);
      assert.ok(fs.statSync(output).isDirectory(), 'screenshot directory must exist');
      await page.setViewportSize({width: 1440, height: 1000});
      await visit(page, '/essays/books/index.html', 'zh');
      await page.screenshot({path: path.join(output, 'books-hub-desktop-zh.png')});
      await page.setViewportSize({width: 390, height: 1100});
      await visit(page, '/essays/nonfiction/the-other-significant-others.html', 'zh-hant');
      await page.screenshot({path: path.join(output, 'friendship-mobile-zh-hant.png')});
      await page.locator('article.rf-prose:visible h2').first().scrollIntoViewIfNeeded();
      await page.screenshot({path: path.join(output, 'friendship-mobile-prose-zh-hant.png')});
      console.log(`Screenshots: ${output}`);
    }
    await check('no JavaScript errors', () => assert.deepEqual(runtimeErrors, []));
    await check('no failed local resources', () => assert.deepEqual([...new Set(httpErrors)], []));
    assert.equal(failures.length, 0, `${failures.length} browser checks failed:\n${failures.join('\n')}`);
    console.log(`OK: ${checks} checks; ${routes.length * 9} page/language/viewport combinations, language reloads and anchors, shelf navigation, ${newSlugs.length * 6} title/author searches, and mobile menus`);
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
