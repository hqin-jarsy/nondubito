#!/usr/bin/env python3
"""Publication checks for the historical series and its separation from fictional cases."""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

from build_state_transitions import ROOT, BASE, DATA, DATE, load_items, render
from connect_state_transitions import render as navigation
from build_content_registry import scan_page
from build_search_index import extract_recent_fiction_descriptions
from test_language_writing import Tags
from web_analytics import TOKEN


class StateHistories(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_items()
        cls.pages = render()

    def test_rebuild_and_navigation_are_current(self):
        self.assertEqual(len(self.pages), 3)
        for path, text in {**self.pages, **navigation()}.items():
            self.assertEqual(path.read_text(), text)
            self.assertNotIn('TODO', text)

    def test_complete_modes_and_recorded_lengths(self):
        receipt = json.loads((DATA/'publication.json').read_text())
        for item in self.items:
            text = self.pages[ROOT/('essays/state-transitions/' + item['slug'] + '.html')]
            bodies = dict(re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>', text, re.S))
            self.assertEqual(set(bodies), {'en', 'zh', 'hant'})
            for body in bodies.values():
                self.assertGreaterEqual(body.count('<p>'), 25)
                self.assertEqual(body.count('<h2>'), 3)
                self.assertNotRegex(body, r'\b\d{2}DD\b|正相变|逆相变|phase transition')
            self.assertNotRegex(bodies['en'], r'[\u3400-\u9fff]')
            self.assertNotRegex(bodies['hant'], r'覈實|覈對|余項|復核|裡貝羅|限製|划定|瞄准')
            self.assertEqual(receipt['counts'][item['slug']]['zh_han'], len(re.findall(r'[\u3400-\u9fff]', ''.join(item['body_zh']))))
            self.assertEqual(receipt['counts'][item['slug']]['en_words'], len(' '.join(item['body_en']).split()))

    def test_sources_are_resolvable_and_not_guessed(self):
        for item in self.items:
            text = self.pages[ROOT/('essays/state-transitions/' + item['slug'] + '.html')]
            refs = {s['id'] for s in item['sources']}
            for lang in ('en', 'zh'):
                self.assertEqual(set(map(int, re.findall(r'\[(\d+)\]', '\n'.join(item['body_' + lang])))), refs)
            self.assertNotIn('act9534.htm', text)
            for source in item['sources']:
                self.assertIn('Source ' + str(source['id']), text)
            if item['id'] == 1:
                self.assertIn('text mirror', text)
                self.assertIn('1979年4月30日', text)
            else:
                self.assertIn('第71', text)
                self.assertIn('第38', text)
                self.assertIn('AZAPO', text)

    def test_schema_and_analytics(self):
        for path, text in self.pages.items():
            tags = Tags(text).items
            self.assertEqual(len([a for t,a in tags if t == 'header' and 'site-shell-header' in a.get('class','')]), 1)
            self.assertEqual({a.get('class') for t,a in tags if t == 'h1'}, {'lang-en', 'lang-zh', 'lang-hant'})
            url = BASE + ('' if path.name == 'index.html' else path.name)
            self.assertEqual([a['href'] for t,a in tags if t == 'link' and a.get('rel') == 'canonical'], [url])
            beacons = [a for t,a in tags if t == 'script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
            self.assertEqual(len(beacons), 1)
            self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'], TOKEN)
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
            self.assertEqual(schema['datePublished'], DATE)
            self.assertEqual(schema['dateModified'], DATE)
            self.assertEqual(schema['inLanguage'], ['en', 'zh-Hans', 'zh-Hant'])
            if path.name == 'index.html':
                self.assertEqual(len(schema['hasPart']), 2)
            else:
                item = next(d for d in self.items if d['slug'] == path.stem)
                self.assertEqual(schema['citation'], [s['url'] for s in item['sources']])
                self.assertEqual(schema['isPartOf']['url'], BASE)

    def test_links_ids_and_search_taxonomy(self):
        for path, text in self.pages.items():
            tags = Tags(text).items
            ids = [a['id'] for t,a in tags if 'id' in a]
            self.assertEqual(len(ids), len(set(ids)))
            for tag, attrs in tags:
                raw = attrs.get('href' if tag in ('a', 'link') else 'src', '')
                parts = urlsplit(raw)
                if not raw or parts.scheme or parts.netloc:
                    continue
                target = ROOT/unquote(parts.path.lstrip('/')) if parts.path.startswith('/') else path.parent/unquote(parts.path)
                if parts.path:
                    self.assertTrue(target.is_file(), str(path) + ': ' + raw)
                if parts.fragment:
                    self.assertRegex(target.read_text() if parts.path else text, r'\bid=["\']' + re.escape(parts.fragment) + r'["\']')
            record = scan_page(ROOT, path)
            self.assertEqual(record['domain'], 'history')
            self.assertEqual(set(record['languages']), {'en', 'zh-Hans', 'zh-Hant'})
            self.assertEqual(set(extract_recent_fiction_descriptions(text)), {'en', 'zh-Hans', 'zh-Hant'})

    def test_discovery_and_separation(self):
        for lang in ('en', 'zh-hans', 'zh-hant'):
            records = {d['u']:d for d in json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']}
            for path in self.pages:
                relative = path.relative_to(ROOT).as_posix()
                self.assertIn(relative, records)
                self.assertEqual(records[relative]['d'], 'history')
        urls = {e.text for e in ET.fromstring((ROOT/'sitemap.xml').read_text()).findall('{*}url/{*}loc')}
        for path in self.pages:
            self.assertIn(BASE + ('' if path.name == 'index.html' else path.name), urls)
        for name in ('library.html', 'explore.html', 'index.html', 'latest.html', 'essays/sae/index.html', 'essays/state/index.html'):
            self.assertIn('state-transitions/index.html', (ROOT/name).read_text())
        library = (ROOT/'library.html').read_text()
        self.assertGreater(library.index('<!-- STATE HISTORIES LIBRARY START -->'), library.index('Category 06'))
        self.assertLess(library.index('<!-- STATE HISTORIES LIBRARY START -->'), library.index('Category 07'))
        self.assertEqual((ROOT/'essays/state/index.html').read_text().count('class="state-card"'), 8)
        self.assertEqual(len(list((ROOT/'data/state-reversal').glob('ep*.json'))), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
