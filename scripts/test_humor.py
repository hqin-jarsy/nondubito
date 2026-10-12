#!/usr/bin/env python3
"""Inventory, attribution, language/SEO and navigation checks for Humor."""
import json
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from pathlib import Path

import build_humor as build
from build_content_registry import scan_page


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class HumorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.load_data()
        cls.outputs = build.render_pages()

    def test_curated_inventory(self):
        issues = self.data['issues']
        self.assertEqual(len(issues), 71)
        self.assertEqual([len(x['jokes']) for x in issues], [6] * 71)
        jokes = [j for issue in issues for j in issue['jokes']]
        self.assertEqual(len({j['id'] for j in jokes}), 426)
        self.assertEqual(len({j['origin'] for j in jokes}), 426)
        self.assertEqual([j['id'] for j in jokes], [f'h{i:03}' for i in range(1, 427)])
        self.assertEqual(len({i['slug'] for i in issues}), 71)
        for joke in jokes:
            self.assertIn(joke['source'], self.data['sources'])
            self.assertTrue(joke['locator'])
            self.assertTrue(joke['note'])
            self.assertGreaterEqual(len(joke['paragraphs']), 2)
            if joke['locator'].startswith('A Hundred Mery Talys'):
                self.assertIn('A Hundred Mery Talys', self.data['sources'][joke['source']]['label'])
            self.assertNotRegex(''.join(joke['paragraphs']), r'SAE|\d+DD|殖民|主体性|结构读法')

    def test_generated_files_and_language(self):
        self.assertEqual(len(self.outputs), 144)
        for path, text in self.outputs.items():
            with self.subTest(path=path):
                self.assertEqual(path.read_text(), text)
                page = Page(text)
                tags = page.tags
                self.assertEqual(sum(t == 'h1' for t, a in tags), 1)
                self.assertEqual(sum(t == 'header' for t, a in tags), 1)
                ids = [a['id'] for t, a in tags if 'id' in a]
                self.assertEqual(len(ids), len(set(ids)))
                language = 'zh-Hant' if path.parent.name == 'zh-hant' else 'zh-Hans'
                record = scan_page(build.ROOT, path)
                self.assertEqual(record['languages'], [language])
                self.assertEqual(record['domain'], 'stories')
                canonicals = [a['href'] for t, a in tags if t == 'link' and a.get('rel') == 'canonical']
                canonical_path = path.relative_to(build.ROOT).as_posix()
                if path.name == 'index.html':
                    canonical_path = canonical_path.removesuffix('index.html')
                self.assertEqual(canonicals, [build.ORIGIN + canonical_path])
                self.assertEqual({a.get('hreflang') for t, a in tags if t == 'link' and a.get('rel') == 'alternate'}, {'zh-Hans', 'zh-Hant'})
                schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
                self.assertEqual(schema['@type'], 'CollectionPage')
                self.assertNotIn('author', schema)  # Compiler is not author of collected jokes.
                if path.name != 'index.html':
                    self.assertEqual(len(schema['hasPart']), 6)
                    self.assertEqual(sum(t == 'article' for t, a in tags), 6)
                    sources = [a for t, a in tags if t == 'details' and a.get('class') == 'humor-source']
                    self.assertEqual(len(sources), 6)
                    self.assertTrue(all('open' not in a for a in sources))
                if language == 'zh-Hant':
                    body = re.search(r'<main.*?</main>', text, re.S)[0]
                    self.assertNotIn('“', body)
                    self.assertNotIn('”', body)
                    self.assertNotIn('乾活', body)
                    self.assertNotIn('復述', body)
                    for mistake in ('譯者表示贊賞', '十分贊賞', '行善稱贊', '重復口令', '發聲重復', '我和我的表', '不補贈表情節'):
                        self.assertNotIn(mistake, body)
                    for mistake in ('有一個准的', '叫得不准', '倒是准的', '准能考中', '咸魚', '咸死他', '乾過這種事', '雞捨', '試題一髮下來', 'Fingers』 Ends'):
                        self.assertNotIn(mistake, body)
                    for mistake in ('才兩英裡', '穆裡亞利', '余下這一路', '野乾', '這只鳥真好看'):
                        self.assertNotIn(mistake, body)
                    for mistake in ('佔吉凶', '裡程碑', '旅人不乾了', '兩只手', '竪起來', '有只老虎'):
                        self.assertNotIn(mistake, body)
                    for mistake in ('只蝨子', '大家認准', '兩只野雞', '三個人合伙做事', '托朋友去廟裡', '改迴路德宗', '乾這麼多活', '線索則輓著'):
                        self.assertNotIn(mistake, body)
                    for mistake in ('道格伯裡', '謝裡丹', '彈得不准', '彈准', '瞄准', '捨下一個粗月亮', '邊挨打邊贊嘆', '客人抬頭贊嘆'):
                        self.assertNotIn(mistake, body)
                    for mistake in ('德米特裡', '土整松', '把松土', '兩只腳', '這只生狗', '一整只狗', '這幾只吃'):
                        self.assertNotIn(mistake, body)
                    for mistake in ('輕輕鬆松', '包扎', '鬥篷', '准是', '乾完活', '該乾的事', '乾得疲憊', '阿裡斯提卜', '望瞭望', '系著紅帶子', '沈下臉'):
                        self.assertNotIn(mistake, body)

    def test_all_local_links_and_anchors(self):
        for path, text in self.outputs.items():
            for tag, attrs in Page(text).tags:
                raw = attrs.get('href') or attrs.get('src')
                if not raw:
                    continue
                url = urlsplit(raw)
                if url.scheme or url.netloc:
                    continue
                target = (path.parent / unquote(url.path)).resolve() if url.path else path
                self.assertTrue(target.is_file(), (path, raw))
                if url.fragment and target.suffix == '.html':
                    ids = {a['id'] for t, a in Page(target.read_text()).tags if 'id' in a}
                    self.assertIn(unquote(url.fragment), ids, (path, raw))

    def test_navigation_across_selections(self):
        issues = self.data['issues']
        for directory in (build.TARGET, build.TARGET / 'zh-hant'):
            index = self.outputs[directory / 'index.html']
            self.assertIn('426', index)
            self.assertIn(f'class="humor-start" href="{issues[65]["slug"]}.html"', index)
            for first, last in [(1, 5), (6, 10), (11, 15), (16, 23), (24, 29), (30, 35), (36, 41), (42, 47), (48, 53), (54, 59), (60, 65), (66, 71)]:
                self.assertIn(f'href="#issues-{first:02}-{last:02}"', index)
            for n, issue in enumerate(issues):
                text = self.outputs[directory / (issue['slug'] + '.html')]
                links = {a.get('rel'): a.get('href') for t, a in Page(text).tags if t == 'a' and a.get('rel')}
                self.assertEqual(links.get('prev'), issues[n - 1]['slug'] + '.html' if n else None)
                self.assertEqual(links.get('next'), issues[n + 1]['slug'] + '.html' if n + 1 < len(issues) else None)
                schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
                self.assertEqual(schema['datePublished'], issue['date'])
        hant = self.outputs[build.TARGET / 'zh-hant/07-things-at-home.html']
        self.assertIn('不鹹', hant)
        self.assertNotIn('不咸', hant)

    def test_discovery_entries(self):
        # The redesigned home page leads to the full Library, not every series.
        self.assertIn('href="library.html"', (build.ROOT / 'index.html').read_text())
        for filename in ['library.html', 'explore.html', 'latest.html']:
            self.assertIn('essays/humor/index.html', (build.ROOT / filename).read_text())
        stories = build.ROOT / 'essays/everyday/stories/index.html'
        self.assertIn('71 个短辑，426 则', stories.read_text())
        self.assertIn('71 個短輯，426 則', stories.read_text())
        for filename in ('library.html', 'explore.html'):
            shelf = (build.ROOT / filename).read_text()
            self.assertIn('71 short collections', shelf)
            self.assertIn('71 个短辑', shelf)
            self.assertIn('71 個短輯', shelf)
            self.assertIn('426', shelf)
        for tag, attrs in Page(stories.read_text()).tags:
            if 'humor/' in attrs.get('href', ''):
                self.assertTrue((stories.parent / attrs['href']).resolve().is_file())
        item = next(x for x in json.loads((build.ROOT / 'data/site-updates.json').read_text())['updates']
                    if x['id'] == '2026-10-12-humor-twelfth-selection')
        self.assertEqual(item['languages'], ['zh', 'zh-hant'])

    def test_optional_philosophy_links(self):
        for path, text in self.outputs.items():
            with self.subTest(path=path):
                self.assertEqual(text.count('<aside class="humor-afterword">'), 1)
                hant = path.parent.name == 'zh-hant'
                lang = 'zh-hant' if hant else 'zh'
                base = '../../../' if hant else '../../'
                self.assertIn(f'href="{base}essays/laughter/index.html?lang={lang}"', text)
                if path.name == 'index.html':
                    self.assertLess(text.index('class="humor-afterword"'), text.index('class="humor-jump"'))
                else:
                    self.assertGreater(text.index('class="humor-afterword"'), text.rindex('</article>'))
        for path in (build.ROOT / 'essays/laughter').glob('*.html'):
            text = path.read_text()
            self.assertEqual(text.count('<aside class="laughter-relax">'), 1)
            self.assertIn('先不想那么多，去读几则笑话。', text)
            self.assertIn('先不想那麼多，去讀幾則笑話。', text)
            self.assertIn('Browse the joke collection (in Chinese)', text)
            self.assertIn('href="../humor/index.html?lang=zh"', text)
            self.assertIn('href="../humor/zh-hant/index.html"', text)
            self.assertIn('new URLSearchParams(location.search)', text)

    def test_search_and_sitemap(self):
        for lang in ('zh-hans', 'zh-hant'):
            records = json.loads((build.ROOT / f'data/search/{lang}.json').read_text())['records']
            humor = [r for r in records if r['u'].startswith('essays/humor/')]
            self.assertEqual(len(humor), 72)
            self.assertTrue(all(r['d'] == 'stories' for r in humor))
        english = json.loads((build.ROOT / 'data/search/en.json').read_text())['records']
        self.assertFalse(any(r['u'].startswith('essays/humor/') for r in english))
        sitemap = (build.ROOT / 'sitemap.xml').read_text()
        for path in self.outputs:
            relative = path.relative_to(build.ROOT).as_posix()
            if path.name == 'index.html':
                relative = relative.removesuffix('index.html')
            self.assertTrue(build.ORIGIN + relative in sitemap, f'Missing sitemap entry: {relative}')


if __name__ == '__main__':
    unittest.main()
