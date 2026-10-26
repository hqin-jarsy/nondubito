#!/usr/bin/env python3
"""Readiness checks for the judgment-and-play essays and their discovery routes."""
from __future__ import annotations

import json
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

from build_judgment_games_series import ROOT, BASE, DATE, load_items, render
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


class JudgmentGamesPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_items()
        cls.pages = render()

    def test_complete_rebuild(self):
        self.assertEqual(len(self.items), 4)
        self.assertEqual(len(self.pages), 5)
        for path, text in self.pages.items():
            with self.subTest(page=path.name):
                self.assertEqual(path.read_text(), text)
                self.assertNotIn('TODO', text)

    def test_head_and_analytics(self):
        for path, text in self.pages.items():
            with self.subTest(page=path.name):
                tags = Tags(text).items
                # The site's global header selector is fixed-position; article
                # headings must not accidentally acquire the navigation layout.
                self.assertTrue(all('site-shell-header' in a.get('class','').split() for tag,a in tags if tag == 'header'))
                canonicals = [a['href'] for tag, a in tags if tag == 'link' and a.get('rel') == 'canonical']
                self.assertEqual(canonicals, [BASE + ('' if path.name == 'index.html' else path.name)])
                beacons = [a for tag,a in tags if tag == 'script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
                self.assertEqual(len(beacons), 1)
                self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'], TOKEN)
                schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
                self.assertEqual(schema['datePublished'], DATE)
                self.assertEqual(schema['inLanguage'], ['en','zh-Hans','zh-Hant'])

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
                self.assertEqual(set(scan_page(ROOT,path)['languages']), {'en','zh-Hans','zh-Hant'})
                self.assertEqual(set(extract_recent_fiction_descriptions(text)), {'en','zh-Hans','zh-Hant'})
                if path.name != 'index.html':
                    bodies = re.findall(r'<div class="essay-body jg-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>', text, re.S)
                    self.assertEqual(len(bodies), 3)
                    self.assertTrue(all('<h3' not in body for lang,body in bodies))
                    self.assertIsNone(re.search(r'[\u3400-\u9fff]', dict(bodies)['en']))
                    self.assertNotRegex(text, r'<(?:input|select)\b')
                    self.assertIn('The closing invitations are optional', text)

    def test_discovery_and_source_receipts(self):
        for name in ('index.html','explore.html','library.html','latest.html'):
            self.assertIn('essays/judgment-games/index.html', (ROOT/name).read_text())
        updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        matching = [u for u in updates if u['id'] == '2026-10-25-judgment-games']
        self.assertEqual(len(matching),1)
        self.assertEqual(set(matching[0]['languages']), {'en','zh','zh-hant'})
        receipts = json.loads((ROOT/'data/judgment-games/publication.json').read_text())['papers']
        self.assertEqual({p['url'] for p in receipts}, {p['source_url'] for p in self.items})
        for p in receipts:
            self.assertRegex(p['sha256'], r'^[0-9a-f]{64}$')


if __name__ == '__main__':
    unittest.main(verbosity=2)
