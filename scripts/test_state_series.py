#!/usr/bin/env python3
"""Publication checks for the complete, three-mode Theory of the State series."""
from __future__ import annotations

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from build_state_series import ROOT, TARGET, BASE, DATE, load_items, render
from build_content_registry import scan_page
from build_search_index import extract_recent_fiction_descriptions
from web_analytics import TOKEN


class Page(HTMLParser):
    def __init__(self, source: str):
        super().__init__()
        self.tags = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class StatePublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_items()
        cls.outputs = render()

    def test_complete_reproducible_collection(self):
        self.assertEqual(len(self.items), 8)
        self.assertEqual(len(self.outputs), 9)
        for path, source in self.outputs.items():
            with self.subTest(page=path.name):
                self.assertEqual(path.read_text(), source)
                self.assertNotIn('TODO', source)

    def test_metadata_tracking_and_local_links(self):
        for path, source in self.outputs.items():
            with self.subTest(page=path.name):
                tags = Page(source).tags
                canonical = [a['href'] for t, a in tags if t == 'link' and a.get('rel') == 'canonical']
                self.assertEqual(canonical, [BASE + ('' if path.name == 'index.html' else path.name)])
                beacons = [a for t, a in tags if t == 'script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src', '')]
                self.assertEqual(len(beacons), 1)
                self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'], TOKEN)
                schema = re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)
                self.assertEqual(len(schema), 1)
                record = json.loads(schema[0])
                self.assertEqual(record['datePublished'], DATE)
                self.assertEqual(record['inLanguage'], ['en', 'zh-Hans', 'zh-Hant'])
                for tag, attrs in tags:
                    attr = 'href' if tag in ('a', 'link') else 'src'
                    url = attrs.get(attr, '')
                    parts = urlsplit(url)
                    if not url or parts.scheme or parts.netloc:
                        continue
                    target = (ROOT / unquote(parts.path.lstrip('/'))) if parts.path.startswith('/') else (path.parent / unquote(parts.path))
                    if parts.path:
                        self.assertTrue(target.is_file(), f'{path.name}: missing {url}')
                    if parts.fragment:
                        content = target.read_text() if parts.path else source
                        self.assertRegex(content, r'\bid=["\']' + re.escape(parts.fragment) + r'["\']')

    def test_modes_search_and_article_hierarchy(self):
        for path, source in self.outputs.items():
            with self.subTest(page=path.name):
                tags = Page(source).tags
                headings = [a for t, a in tags if t == 'h1']
                self.assertEqual({a['class'] for a in headings}, {'lang-en', 'lang-zh', 'lang-hant'})
                self.assertEqual(len(headings), 3)
                controls = [a.get('data-set-language') for t, a in tags if 'data-set-language' in a]
                self.assertEqual(set(controls), {'en', 'zh', 'zh-hant'})
                self.assertEqual(set(extract_recent_fiction_descriptions(source)), {'en', 'zh-Hans', 'zh-Hant'})
                record = scan_page(ROOT, path)
                self.assertEqual(set(record['languages']), {'en', 'zh-Hans', 'zh-Hant'})
                if path.name != 'index.html':
                    bodies = re.findall(r'<div class="essay-body state-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>', source, re.S)
                    self.assertEqual(len(bodies), 3)
                    self.assertTrue(all('<h3' not in body for _, body in bodies))
                    en = next(body for lang, body in bodies if lang == 'en')
                    self.assertIsNone(re.search(r'[\u3400-\u9fff]', en))
                    self.assertNotIn('公裡', next(body for lang, body in bodies if lang == 'hant'))

    def test_front_door_entries(self):
        for name in ('index.html', 'essays/sae/index.html', 'library.html', 'latest.html'):
            self.assertIn('essays/state/index.html', (ROOT / name).read_text())
        updates = json.loads((ROOT / 'data/site-updates.json').read_text())['updates']
        entries = [item for item in updates if item['id'] == '2026-10-25-state-series']
        self.assertEqual(len(entries), 1)
        self.assertEqual(set(entries[0]['languages']), {'en', 'zh', 'zh-hant'})

    def test_provenance_receipts(self):
        report = json.loads((ROOT / 'data/state/publication.json').read_text())
        self.assertEqual(len(report['papers']), 8)
        self.assertEqual({p['url'] for p in report['papers']}, {p['source_url'] for p in self.items})
        for source in report['papers']:
            self.assertRegex(source['sha256'], r'^[0-9a-f]{64}$')


if __name__ == '__main__':
    unittest.main(verbosity=2)
