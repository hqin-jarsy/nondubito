#!/usr/bin/env python3
"""Check complete editions, evidence boundaries and durable discovery routes."""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

from build_political_economy import ROOT, DATA, BASE, DATE, load_items, render
from connect_political_economy import render as entrances
from build_content_registry import scan_page
from test_language_writing import Tags
from web_analytics import TOKEN


class PoliticalEconomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_items()
        cls.pages = render()
        cls.receipt = json.loads((DATA/'publication-batch01.json').read_text())

    def test_reproducible_pages_and_entrances(self):
        self.assertEqual(len(self.pages), 4)
        for p, text in {**self.pages, **entrances()}.items():
            self.assertEqual(p.read_text(), text)
            self.assertNotIn('TODO', text)

    def test_complete_three_reading_modes(self):
        for d in self.items:
            self.assertEqual(self.receipt['counts'][d['slug']]['zh_han'], len(re.findall(r'[\u3400-\u9fff]', ''.join(d['body_zh']))))
            self.assertEqual(self.receipt['counts'][d['slug']]['en_words'], len(' '.join(d['body_en']).split()))
            text = self.pages[ROOT / ('essays/political-economy/' + d['slug'] + '.html')]
            bodies = dict(re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>', text, re.S))
            self.assertEqual(set(bodies), {'en', 'zh', 'hant'})
            self.assertEqual(bodies['zh'].count('<p>'), bodies['hant'].count('<p>'))
            for body in bodies.values():
                self.assertGreaterEqual(body.count('<p>'), 16 if d['id'] == 1 else 22)
                self.assertEqual(body.count('<h2>'), 2 if d['id'] == 1 else 3)
                self.assertNotRegex(body, r'\b\d{2}DD\b|\b[EFGZ]\d+\b||turn\d+(?:view|search)')
            self.assertNotRegex(bodies['en'], r'[\u3400-\u9fff]')
            self.assertNotRegex(bodies['hant'], r'覈實|覈對|復核|標簽|髮款|被系在|余項|籤償還|籤下|籤了和解')

    def test_intro_stays_short_and_distinguishes_voice_from_exit(self):
        d = self.items[0]
        self.assertLess(len(re.findall(r'[\u3400-\u9fff]', ''.join(d['body_zh']))), 1800)
        self.assertLess(len(' '.join(d['body_en']).split()), 1100)
        self.assertIn('不只问能不能走', ''.join(d['body_zh']))
        self.assertIn('stay and challenge', ''.join(d['body_en']))
        self.assertNotIn('青窑', ''.join(d['body_zh']))
        self.assertNotIn('Crossways', ''.join(d['body_en']))

    def test_numbered_original_sources(self):
        self.assertEqual([len(d['sources']) for d in self.items], [5, 3, 6])
        for d in self.items:
            for lang in ('en', 'zh'):
                self.assertEqual(set(map(int, re.findall(r'\[(\d+)\]', '\n'.join(d['body_' + lang])))), {s['id'] for s in d['sources']})
            page = self.pages[ROOT/('essays/political-economy/' + d['slug'] + '.html')]
            for s in d['sources']:
                self.assertIn(s['url'].replace('&', '&amp;'), page)

    def test_petsmart_dates_amounts_and_evidence_status(self):
        d = self.items[1]
        zh, en = ''.join(d['body_zh']), ' '.join(d['body_en'])
        for phrase in ('五千五百', '两千七百五十', '培训开始', '三十天', '被公司解雇', '州方的调查主张', '生效前数年', '2026年2月17日', '否认不当行为'):
            self.assertIn(phrase, zh)
        for phrase in ('$5,500', '$2,750', 'Dismissal', 'within thirty days', 'years before', '17 February 2026', 'not findings after a trial'):
            self.assertIn(phrase, en)
        self.assertIn('not independent proof of the date of judicial entry', d['sources'][1]['note_en'])

    def test_amazon_distinguishes_services_and_proceedings(self):
        d = self.items[2]
        zh, en = ''.join(d['body_zh']), ' '.join(d['body_en'])
        for phrase in ('三者相关，却不是同一个东西', '原告提出的机制', '2026年11月1日', '2026年10月30日', '不作违反欧盟竞争规则的认定', 'Amazon 的答辩'):
            self.assertIn(phrase, zh)
        for phrase in ('not the same thing', 'alleged mechanism', 'must not be presented as an adjudication of liability', 'separate European proceeding', 'Those explanations should not be treated merely as camouflage'):
            self.assertIn(phrase, en)
        self.assertIn('redacted numbers are not reconstructed', d['sources'][0]['note_en'])

    def test_metadata_and_analytics(self):
        for p, text in self.pages.items():
            tags = Tags(text).items
            url = BASE + ('' if p.name == 'index.html' else p.name)
            self.assertEqual([a['href'] for t,a in tags if t == 'link' and a.get('rel') == 'canonical'], [url])
            self.assertEqual(len([a for t,a in tags if t == 'header']), 1)
            self.assertEqual({a['class'] for t,a in tags if t == 'h1'}, {'lang-en', 'lang-zh', 'lang-hant'})
            beacons = [a for t,a in tags if t == 'script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
            self.assertEqual(len(beacons), 1)
            self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'], TOKEN)
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
            self.assertEqual(schema['inLanguage'], ['en', 'zh-Hans', 'zh-Hant'])
            self.assertEqual(schema['datePublished'], DATE)
            self.assertEqual(schema['dateModified'], DATE)
            if p.name == 'index.html':
                self.assertEqual(len(schema['hasPart']), 3)
            else:
                d = next(d for d in self.items if d['slug'] == p.stem)
                self.assertEqual(schema['citation'], [s['url'] for s in d['sources']])
                self.assertEqual(schema['isPartOf']['url'], BASE)

    def test_local_links_and_unique_ids(self):
        for p, text in self.pages.items():
            tags = Tags(text).items
            ids = [a['id'] for t,a in tags if 'id' in a]
            self.assertEqual(len(ids), len(set(ids)))
            for tag, attrs in tags:
                raw = attrs.get('href' if tag in ('a','link') else 'src', '')
                u = urlsplit(raw)
                if not raw or u.scheme or u.netloc:
                    continue
                target = ROOT/unquote(u.path.lstrip('/')) if u.path.startswith('/') else p.parent/unquote(u.path)
                if u.path:
                    self.assertTrue(target.is_file(), str(p) + ': ' + raw)
                if u.fragment:
                    self.assertRegex(target.read_text() if u.path else text, r'\bid=["\']' + re.escape(u.fragment) + r'["\']')

    def test_open_ended_landing_and_navigation(self):
        text = self.pages[ROOT/'essays/political-economy/index.html']
        self.assertEqual(text.count('class="lw-card"'), 2)
        self.assertIn('href="introduction.html"', text)
        self.assertIn('An ongoing series', text)
        for name in ('library.html','explore.html','index.html','latest.html','essays/sae/index.html'):
            self.assertIn('essays/political-economy/index.html', (ROOT/name).read_text())
        groups = json.loads((ROOT/'data/sae-reading-map.json').read_text())['groups']
        self.assertEqual(len(groups), 6)
        shared = next(g for g in groups if g['id'] == 'shared-life')
        self.assertEqual(sum(x[0] == 'essays/political-economy/index.html' for x in shared['items']), 1)

    def test_search_taxonomy_and_localized_descriptions(self):
        for lang in ('en','zh-hans','zh-hant'):
            records = {r['u']:r for r in json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']}
            for p in self.pages:
                rel = p.relative_to(ROOT).as_posix()
                self.assertEqual(records[rel]['d'], 'sae-philosophy')
                self.assertEqual(scan_page(ROOT, p)['domain'], 'sae-philosophy')
                if lang != 'en':
                    self.assertRegex(records[rel]['x'], r'[\u3400-\u9fff]')
            case = records['essays/political-economy/petsmart-training.html']
            self.assertIn('PetSmart', case['q'])
            self.assertIn('PetSmart', case['x']) if lang == 'en' else self.assertIn('培训' if lang == 'zh-hans' else '培訓', case['x'])

    def test_sitemap_and_update_ledger(self):
        root = ET.fromstring((ROOT/'sitemap.xml').read_text())
        urls = {x.find('{*}loc').text:x.find('{*}lastmod').text for x in root.findall('{*}url')}
        for p in self.pages:
            self.assertEqual(urls[BASE + ('' if p.name == 'index.html' else p.name)], DATE)
        updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        u = next(u for u in updates if u['id'] == '2026-11-01-political-economy-batch01')
        self.assertEqual(set(u['languages']), {'en','zh','zh-hant'})
        self.assertEqual(u['kind'], 'new')


if __name__ == '__main__':
    unittest.main()
