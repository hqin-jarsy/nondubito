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
        self.assertEqual(len(issues), 15)
        self.assertEqual([len(x['jokes']) for x in issues], [6] * 15)
        jokes = [j for issue in issues for j in issue['jokes']]
        self.assertEqual(len({j['id'] for j in jokes}), 90)
        self.assertEqual(len({j['origin'] for j in jokes}), 90)
        self.assertEqual([j['id'] for j in jokes], [f'h{i:03}' for i in range(1, 91)])
        self.assertEqual(len({i['slug'] for i in issues}), 15)
        for joke in jokes:
            self.assertIn(joke['source'], self.data['sources'])
            self.assertTrue(joke['locator'])
            self.assertTrue(joke['note'])
            self.assertGreaterEqual(len(joke['paragraphs']), 2)
            self.assertNotRegex(''.join(joke['paragraphs']), r'SAE|\d+DD|殖民|主体性|结构读法')

    def test_generated_files_and_language(self):
        self.assertEqual(len(self.outputs), 32)
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
                    for mistake in ('輕輕鬆松', '包扎', '鬥篷', '准是'):
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
            self.assertIn('90', index)
            self.assertIn(f'class="humor-start" href="{issues[10]["slug"]}.html"', index)
            for first, last in [(1, 5), (6, 10), (11, 15)]:
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
        for filename in ['index.html', 'library.html', 'explore.html', 'latest.html']:
            self.assertIn('essays/humor/index.html', (build.ROOT / filename).read_text())
        stories = build.ROOT / 'essays/everyday/stories/index.html'
        for tag, attrs in Page(stories.read_text()).tags:
            if 'humor/' in attrs.get('href', ''):
                self.assertTrue((stories.parent / attrs['href']).resolve().is_file())
        item = json.loads((build.ROOT / 'data/site-updates.json').read_text())['updates'][0]
        self.assertEqual(item['languages'], ['zh', 'zh-hant'])

    def test_search_and_sitemap(self):
        for lang in ('zh-hans', 'zh-hant'):
            records = json.loads((build.ROOT / f'data/search/{lang}.json').read_text())['records']
            humor = [r for r in records if r['u'].startswith('essays/humor/')]
            self.assertEqual(len(humor), 16)
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
