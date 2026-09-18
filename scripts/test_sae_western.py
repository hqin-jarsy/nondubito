#!/usr/bin/env python3
"""Publication and navigation regressions for SAE Western Philosophy."""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit, unquote

import build_sae_western as build
from build_content_registry import scan_page
from build_search_index import extract_recent_fiction_descriptions
from test_recent_fiction import Page


class WesternTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = build.load_copy()
        cls.outputs = build.build()

    def test_inventory_and_reproducibility(self):
        self.assertEqual([x['number'] for x in self.items], list(range(6)))
        self.assertEqual(len(self.outputs), 8)
        for path, source in self.outputs.items():
            self.assertEqual(path.read_text(encoding='utf-8'), source, path.name)

    def test_complete_bodies_and_traditional_parity(self):
        for item in self.items:
            source = self.outputs[build.SERIES / (item['slug'] + '.html')]
            bodies = re.findall(r'<div class="western-prose lang-([^\"]+)" lang="[^\"]+">(.*?)</div>', source, re.S)
            self.assertEqual([lang for lang, _ in bodies], ['en', 'zh', 'hant'])
            counts = dict((lang, body.count('<p>')) for lang, body in bodies)
            self.assertEqual(counts['zh'], counts['hant'])
            for lang in ('en', 'zh'):
                self.assertEqual(counts[lang], sum(len(s['paragraphs']) for s in item[lang]['sections']))
            self.assertNotIn('[VERIFY', source)

    def test_structure_metadata_and_links(self):
        for path, source in self.outputs.items():
            with self.subTest(page=str(path)):
                page = Page(source)
                self.assertEqual(page.errors, [])
                self.assertEqual(len(page.ids), len(set(page.ids)))
                self.assertEqual(source.count('<header'), 1)
                self.assertEqual(len(page.schemas), 1)
                schema = page.schemas[0]
                self.assertEqual(schema['inLanguage'], ['en', 'zh-Hans', 'zh-Hant'])
                canonical = 'https://nondubito.net/' + path.relative_to(build.ROOT).as_posix()
                if path.name == 'index.html': canonical = canonical.removesuffix('index.html')
                self.assertEqual(schema['url'], canonical)
                self.assertIn(f'<link rel="canonical" href="{canonical}">', source)
                for href in page.links:
                    link = urlsplit(href)
                    if link.scheme or link.netloc: continue
                    target = (path.parent / unquote(link.path)).resolve() if link.path else path
                    if target.is_dir(): target /= 'index.html'
                    self.assertTrue(target.is_file(), href)
                    if link.fragment:
                        self.assertIn(unquote(link.fragment), Page(target.read_text(encoding='utf-8')).ids, href)

    def test_optional_notes_follow_complete_prose(self):
        for item in self.items:
            source = self.outputs[build.SERIES / (item['slug'] + '.html')]
            if item['number']:
                self.assertIn('<details class="western-aside">', source)
                self.assertNotIn('<details class="western-aside" open', source)
                self.assertGreater(source.index('<details class="western-aside">'), source.index('class="western-prose lang-hant"'))
            else:
                self.assertNotIn('class="western-aside"', source)
            for key in build.SOURCE_KEYS[item['number']]:
                self.assertIn(build.SOURCES[key][2].replace('&', '&amp;'), source)

    def test_editorial_corrections_and_no_unverified_statistics(self):
        text = json.dumps(self.items, ensure_ascii=False)
        for old in ('两百六十', '两百八十', '八千多', '谁也驳不倒它', '真正跟那句话对着干的，是成段拿掉和成段添上'):
            self.assertNotIn(old, text)
        for word in ('Que sais', 'nous', '1580'):
            self.assertIn(word, text)

    def test_shelf_and_series_links(self):
        shelf = self.outputs[build.SHELF/'index.html']
        self.assertEqual(shelf.count('class="western-book"'), 4)
        for slug in ('sae-republic', 'sae-nicomachean', 'sae-consolation', 'sae-montaigne'):
            self.assertIn(f'href="../{slug}/index.html"', shelf)
        index = self.outputs[build.SERIES/'index.html']
        self.assertEqual(index.count('class="western-entry"'), 6)
        for item in self.items:
            self.assertIn('href="' + item['slug'] + '.html"', index)

    def test_traditional_editorial_corrections(self):
        source = '\n'.join(m.group(2) for value in self.outputs.values() for m in re.finditer(
            r'<(\w+)\b[^>]*class="[^"]*\blang-hant\b[^"]*"[^>]*>(.*?)</\1>', value, re.S))
        for wrong in ('拿不准', '乾完活', '它乾的事', '外頭髮話', '證明瞭蒙田', '數得再准', '看准了'):
            self.assertFalse(wrong in source, wrong)
        for correct in ('幹完活', '它幹的事', '外頭發話', '證明了蒙田', '數得再準', '看準了', '劃掉'):
            self.assertTrue(correct in source, correct)

    def test_previous_next_links(self):
        for i, item in enumerate(self.items):
            source = self.outputs[build.SERIES/(item['slug']+'.html')]
            nav = re.search(r'<nav class="western-series-nav".*?</nav>', source, re.S).group()
            for target in (self.items[i-1]['slug']+'.html' if i else 'index.html', self.items[i+1]['slug']+'.html' if i<5 else 'index.html'):
                self.assertIn('href="' + target + '"', nav)

    def test_search_localization_and_taxonomy(self):
        for path, source in self.outputs.items():
            page = scan_page(build.ROOT, path)
            self.assertEqual(set(page['languages']), {'en','zh-Hans','zh-Hant'})
            self.assertEqual(page['domain'], 'sae-philosophy')
            self.assertEqual(page['category'], 'sae-western')
            self.assertEqual(set(extract_recent_fiction_descriptions(source)), {'en','zh-Hans','zh-Hant'})
            for language in ('en','zh-Hans','zh-Hant'):
                self.assertTrue(page['titles'].get(language))
            self.assertEqual(page['record_type'], 'collection-index' if path.name == 'index.html' else 'essay')

    def test_latest_record_and_sitemap(self):
        ledger = json.loads((build.ROOT/'data/site-updates.json').read_text())
        entry = next(x for x in ledger['updates'] if x['id']=='2026-09-17-montaigne-western-philosophy')
        self.assertEqual(entry['languages'], ['en','zh','zh-hant'])
        self.assertIn(entry['id'], (build.ROOT/'latest.html').read_text())
        sitemap = ET.parse(build.ROOT/'sitemap.xml')
        locations = {el.text for el in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        for path, source in self.outputs.items():
            canonical = Page(source).schemas[0]['url']
            self.assertTrue(canonical in locations, canonical)


if __name__ == '__main__':
    unittest.main()
