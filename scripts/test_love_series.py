#!/usr/bin/env python3
"""Publication checks for the love essays and their discovery routes."""
from __future__ import annotations

import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

from build_love_series import ROOT, BASE, DATE, LoveTraditionalConverter, load_items, render
from build_content_registry import scan_page
from build_search_index import extract_recent_fiction_descriptions
from web_analytics import TOKEN


class Tags(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.items = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.items.append((tag, dict(attrs)))


class LovePublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_items()
        cls.pages = render()

    def test_complete_rebuild(self):
        self.assertEqual(len(self.items), 8)
        self.assertEqual(len(self.pages), 9)
        for path, text in self.pages.items():
            with self.subTest(page=path.name):
                self.assertEqual(path.read_text(), text)
                self.assertNotIn('TODO', text)

    def test_head_and_analytics(self):
        for path, text in self.pages.items():
            with self.subTest(page=path.name):
                tags = Tags(text).items
                # Global header styling is fixed navigation, not article layout.
                headers = [a for tag,a in tags if tag == 'header']
                self.assertEqual(len(headers), 1)
                self.assertTrue(all('site-shell-header' in a.get('class','').split() for a in headers))
                canonicals = [a['href'] for tag,a in tags if tag == 'link' and a.get('rel') == 'canonical']
                self.assertEqual(canonicals, [BASE + ('' if path.name == 'index.html' else path.name)])
                beacons = [a for tag,a in tags if tag == 'script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
                self.assertEqual(len(beacons), 1)
                self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'], TOKEN)
                schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
                self.assertEqual(schema['datePublished'], DATE)
                self.assertEqual(schema['inLanguage'], ['en','zh-Hans','zh-Hant'])
                if path.name != 'index.html':
                    self.assertIn(schema['citation'], {item['source_url'] for item in self.items})

    def test_local_targets_and_fragments(self):
        for path, text in self.pages.items():
            for tag, attrs in Tags(text).items:
                url = attrs.get('href' if tag in ('a','link') else 'src', '')
                parts = urlsplit(url)
                if not url or parts.scheme or parts.netloc:
                    continue
                target = ROOT / unquote(parts.path.lstrip('/')) if parts.path.startswith('/') else path.parent / unquote(parts.path)
                if parts.path:
                    self.assertTrue(target.is_file(), f'{path.name}: {url}')
                if parts.fragment:
                    source = target.read_text() if parts.path else text
                    self.assertRegex(source, r'\bid=["\']' + re.escape(parts.fragment) + r'["\']')

    def test_languages_and_complete_prose(self):
        for path, text in self.pages.items():
            with self.subTest(page=path.name):
                tags = Tags(text).items
                self.assertEqual({a['class'] for tag,a in tags if tag == 'h1'}, {'lang-en','lang-zh','lang-hant'})
                self.assertEqual({a.get('data-set-language') for tag,a in tags if 'data-set-language' in a}, {'en','zh','zh-hant'})
                record = scan_page(ROOT,path)
                self.assertEqual(set(record['languages']), {'en','zh-Hans','zh-Hant'})
                self.assertEqual(record['domain'], 'sae-philosophy')
                self.assertEqual(set(extract_recent_fiction_descriptions(text)), {'en','zh-Hans','zh-Hant'})
                if path.name != 'index.html':
                    bodies = re.findall(r'<div class="essay-body love-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>', text, re.S)
                    self.assertEqual(len(bodies), 3)
                    self.assertTrue(all('<h3' not in body for lang,body in bodies))
                    self.assertIsNone(re.search(r'[\u3400-\u9fff]', dict(bodies)['en']))
                    self.assertNotRegex(text, r'<(?:input|select)\b')

    def test_routes_and_distinct_everyday_shelf(self):
        for name in ('index.html','essays/sae/index.html','library.html','latest.html'):
            self.assertIn('essays/love/index.html', (ROOT/name).read_text())
        landing = self.pages[ROOT/'essays/love/index.html']
        self.assertEqual(len(re.findall(r'class="love-card"', landing)),6)
        self.assertIn('class="love-guide love-stories" href="ep07.html"', landing)
        self.assertIn('class="love-guide" href="overview.html"', landing)
        for text in self.pages.values():
            self.assertIn('../everyday/relationships/index.html', text)
        for i,item in enumerate(self.items):
            text = self.pages[ROOT/'essays/love'/f'{item["slug"]}.html']
            neighbors = re.search(r'<nav class="love-series-nav".*?</nav>',text,re.S)[0]
            if i:
                self.assertIn(f'href="{self.items[i-1]["slug"]}.html"',neighbors)
            if i < 7:
                self.assertIn(f'href="{self.items[i+1]["slug"]}.html"',neighbors)

    def test_updates_and_source_receipts(self):
        updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        matching = [u for u in updates if u['id'] == '2026-10-25-love-series']
        self.assertEqual(len(matching),1)
        self.assertEqual(set(matching[0]['languages']), {'en','zh','zh-hant'})
        receipts = json.loads((ROOT/'data/love/publication.json').read_text())['papers']
        self.assertEqual({p['url'] for p in receipts}, {p['source_url'] for p in self.items})
        for p in receipts:
            self.assertRegex(p['sha256'], r'^[0-9a-f]{64}$')

    def test_traditional_lexical_context(self):
        converter = LoveTraditionalConverter()
        try:
            self.assertEqual(converter.convert('沉默是默认，老沈没有回复；一份文件。'),
                             '沉默是默認，老沈沒有回覆；一份文件。')
            self.assertEqual(converter.convert('来往的沉积'), '來往的沉積')
            self.assertEqual(converter.convert('一发现；复述；愿意多干，认真干活，干净。'),
                             '一發現；複述；願意多幹，認真幹活，乾淨。')
            self.assertEqual(converter.convert('那只手'), '那隻手')
            self.assertEqual(converter.convert('亚里士多德、舍勒、里克；发色；反复追问，日复一日。'),
                             '亞里士多德、舍勒、里克；髮色；反覆追問，日復一日。')
        finally:
            converter.close()

    def test_search_and_sitemap_membership(self):
        expected = {'essays/love/' + name for name in ('index.html','overview.html', *(f'ep{i:02d}.html' for i in range(1,8)))}
        for language in ('en', 'zh-hans', 'zh-hant'):
            records = json.loads((ROOT/'data/search'/f'{language}.json').read_text())['records']
            rows = [r for r in records if r['u'].startswith('essays/love/')]
            self.assertEqual({r['u'] for r in rows}, expected)
            self.assertEqual(len(rows),9)
            self.assertTrue(all(r['d'] == 'sae-philosophy' for r in rows))
        tree = ET.parse(ROOT/'sitemap.xml')
        urls = {node.text for node in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        self.assertTrue({BASE} | {BASE + name for name in ('overview.html', *(f'ep{i:02d}.html' for i in range(1,8)))} <= urls)


if __name__ == '__main__':
    unittest.main(verbosity=2)
