#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Theoretical completeness, nested assets, and distinct bidirectional reading paths."""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import unquote, urlsplit

from build_political_economy_theory import ROOT, BASE, DATE, load_items, render, counts
from build_political_economy import render as render_cases
from political_economy_routes import CASE_TO_THEORY
from test_language_writing import Tags
from web_analytics import TOKEN


class PoliticalEconomyTheoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_items()
        cls.pages = render()

    def test_nine_reproducible_pages(self):
        self.assertEqual(len(self.items), 8)
        self.assertEqual(len(self.pages), 9)
        for path, text in self.pages.items():
            self.assertEqual(path.read_text(), text)
            self.assertNotIn('__PE_THEORY_CONTENT__', text)
            self.assertNotIn('TODO', text)

    def test_three_complete_editions(self):
        receipt = json.loads((ROOT/'data/political-economy/publication-theory.json').read_text())
        for d in self.items:
            n = counts(d)
            self.assertEqual(n, receipt['counts'][d['slug']])
            self.assertGreaterEqual(n['zh_han'], 2300)
            self.assertGreaterEqual(n['en_words'], 1400)
            text = self.pages[ROOT/f'essays/political-economy/theory/{d["slug"]}.html']
            bodies = dict(re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>', text, re.S))
            self.assertEqual(set(bodies), {'zh', 'hant', 'en'})
            self.assertEqual(bodies['zh'].count('<p>'), bodies['hant'].count('<p>'))
            for b in bodies.values():
                self.assertGreaterEqual(b.count('<h2>'), 3)
                self.assertNotRegex(b, r'\b\d{2}DD\b|\b[EFGZ]\d+\b||turn\d+(?:view|search)')
            self.assertNotRegex(bodies['en'], r'[\u3400-\u9fff]')
            self.assertNotRegex(bodies['hant'], r'覈對|覈實|復核|標簽|髮款|余項|被系在|英裡|准入')
            self.assertIn('pe-takeaway', text)

    def test_source_papers_and_schema(self):
        for path, text in self.pages.items():
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
            expected = BASE + ('' if path.name == 'index.html' else path.name)
            self.assertIn('rel="canonical" href="' + expected + '"', text)
            self.assertEqual(schema['url'], expected)
            self.assertEqual(schema['datePublished'], DATE)
            self.assertEqual(schema['dateModified'], DATE)
            self.assertEqual(schema['inLanguage'], ['en','zh-Hans','zh-Hant'])
            if path.name == 'index.html':
                self.assertEqual(len(schema['hasPart']), 8)
            else:
                d = next(d for d in self.items if d['slug'] == path.stem)
                self.assertEqual(schema['citation'], d['source_url'])
                self.assertIn('href="' + d['source_url'] + '"', text)
                self.assertEqual(schema['isPartOf']['url'], BASE)

    def test_nested_assets_links_and_unique_ids(self):
        for path, text in self.pages.items():
            tags = Tags(text).items
            ids = [a['id'] for _,a in tags if 'id' in a]
            self.assertEqual(len(ids), len(set(ids)))
            for tag, a in tags:
                raw = a.get('href' if tag in ('a','link') else 'src', '')
                u = urlsplit(raw)
                if not raw or u.scheme or u.netloc:
                    continue
                target = ROOT/unquote(u.path.lstrip('/')) if u.path.startswith('/') else path.parent/unquote(u.path)
                if u.path:
                    self.assertTrue(target.is_file(), str(path) + ': ' + raw)
                if u.fragment:
                    self.assertRegex(target.read_text() if u.path else text, r'\bid=["\']' + re.escape(u.fragment) + r'["\']')
            self.assertIn('href="../../../style.css"', text)
            self.assertIn('src="../../../site-shell.js', text)
            self.assertIn('href="../../language-writing/reading.css', text)

    def test_primary_route_and_optional_deep_read(self):
        index = self.pages[ROOT/'essays/political-economy/theory/index.html']
        self.assertEqual(index.count('class="lw-card"'), 6)
        self.assertIn('01 · Start here', index)
        self.assertIn('08 · Optional deeper reading', index)
        self.assertIn('href="ep08.html"', index)
        hub = (ROOT/'essays/political-economy/index.html').read_text()
        self.assertIn('href="theory/index.html"', hub)
        self.assertIn('id="cases"', hub)
        self.assertEqual(hub.count('class="lw-card"'), 8)
        self.assertIn('id="group-one-ending"', hub)

    def test_targeted_two_way_companions(self):
        cases = render_cases()
        for d in self.items:
            page = self.pages[ROOT/f'essays/political-economy/theory/{d["slug"]}.html']
            for slug in d['case_slugs']:
                self.assertIn('href="../' + slug + '.html"', page)
                self.assertIn(d['slug'], CASE_TO_THEORY[slug])
                case = cases[ROOT/f'essays/political-economy/{slug}.html']
                self.assertIn('href="theory/' + d['slug'] + '.html"', case)
        for text in cases.values():
            if 'class="lw-article"' in text:
                self.assertIn('pe-theory-companion', text)

    def test_chapter_navigation(self):
        for i, d in enumerate(self.items):
            p = self.pages[ROOT/f'essays/political-economy/theory/{d["slug"]}.html']
            nav = re.search(r'<nav class="lw-series-nav".*?</nav>', p, re.S)[0]
            self.assertEqual(nav.count('<a '), 2)
            for j in (i-1, i+1):
                expected = self.items[j]['slug'] + '.html' if 0 <= j < 8 else 'index.html'
                self.assertIn('href="' + expected + '"', nav)

    def test_analytics_search_and_sitemap(self):
        urls = {x.find('{*}loc').text:x.find('{*}lastmod').text for x in ET.fromstring((ROOT/'sitemap.xml').read_text()).findall('{*}url')}
        expansion_profile = ROOT/'data/political-economy-theory/multilingual/profile.json'
        minimum = max(DATE, json.loads(expansion_profile.read_text())['date']) if expansion_profile.exists() else DATE
        for path, text in self.pages.items():
            self.assertEqual(text.count(TOKEN), 1)
            # A later navigation update changes lastmod, not datePublished.
            modified = urls[BASE + ('' if path.name == 'index.html' else path.name)]
            self.assertGreaterEqual(modified, minimum)
            self.assertLessEqual(modified, datetime.now(timezone.utc).date().isoformat())
        for lang in ('en','zh-hans','zh-hant'):
            records = {r['u']:r for r in json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']}
            for path in self.pages:
                r = records[path.relative_to(ROOT).as_posix()]
                self.assertEqual(r['d'], 'sae-philosophy')
                if lang != 'en':
                    self.assertRegex(r['x'], r'[\u3400-\u9fff]')

    def test_discovery_and_historical_updates(self):
        updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        u = next(u for u in updates if u['id'] == '2026-11-03-political-economy-theory')
        self.assertEqual(u['languages'], ['en','zh','zh-hant'])
        for path in ('latest.html','explore.html','library.html','essays/sae/index.html'):
            self.assertIn('political-economy/', (ROOT/path).read_text())
        for batch in range(1,6):
            self.assertIn(f'POLITICAL ECONOMY BATCH{batch:02d} LATEST START', (ROOT/'latest.html').read_text())

    def test_explicit_boundaries_and_fact_limits(self):
        intro = ''.join(self.items[0]['body_zh'])
        self.assertIn('人是目的', intro)
        self.assertIn('不是对各地现行法律', intro)
        self.assertIn('制衡者也', intro)
        exit_text = ''.join(self.items[2]['body_zh'])
        self.assertIn('签字或补偿', exit_text)
        self.assertIn('三关', exit_text)
        support = ''.join(self.items[6]['body_zh'])
        self.assertIn('单程三小时', support)
        self.assertIn('是否继续', support)
        tradition = ''.join(self.items[7]['body_zh'])
        self.assertIn('明确拒绝', tradition)
        self.assertIn('二手', tradition)
        self.assertIn('资本加等待', tradition)
        self.assertNotIn('内在声誉', tradition)
        accumulation = ' '.join(self.items[1]['body_en'])
        self.assertIn('Within a week', accumulation)
        self.assertIn('pension fund\'s behalf', accumulation)
        self.assertNotIn('overnight', accumulation)
        growth = ' '.join(self.items[5]['body_en'])
        self.assertNotIn('reviews leads to', growth)
        self.assertNotIn('inherited reputation', growth)
        conversion = ' '.join(self.items[4]['body_en'])
        self.assertIn('rated at least 4.5', conversion)
        self.assertNotIn('Reputation leading to opportunity', conversion)


if __name__ == '__main__':
    unittest.main()
