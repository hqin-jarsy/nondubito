#!/usr/bin/env python3
"""Publication checks for real histories distinct from the fictional Interstate essays."""
import json
import hashlib
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

from build_cooperation_histories import ROOT, DATA, BASE, DATE, load_items, render
from connect_cooperation_histories import render as entrances
from build_content_registry import scan_page
from test_language_writing import Tags
from web_analytics import TOKEN


class CooperationHistories(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_items()
        cls.pages = render()
        cls.receipt = json.loads((DATA/'publication.json').read_text())
        cls.batch2 = json.loads((DATA/'publication-batch02.json').read_text())
        cls.counts = {**cls.receipt['counts'], **cls.batch2['counts']}

    def test_complete_rebuild(self):
        self.assertEqual(len(self.pages), 5)
        for path, text in {**self.pages, **entrances()}.items():
            self.assertEqual(path.read_text(), text)
            self.assertNotIn('TODO', text)

    def test_complete_three_reading_modes(self):
        for d in self.items:
            text = self.pages[ROOT/('essays/cooperation-histories/' + d['slug'] + '.html')]
            bodies = dict(re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>', text, re.S))
            self.assertEqual(set(bodies), {'en', 'zh', 'hant'})
            for body in bodies.values():
                self.assertGreaterEqual(body.count('<p>'), 25)
                self.assertEqual(body.count('<h2>'), 3)
                self.assertNotRegex(body, r'\b\d{2}DD\b|\bXZ\d+\b|\b[NGZ]\d+\b||turn\d+(?:view|search)')
            self.assertEqual(bodies['zh'].count('<p>'), bodies['hant'].count('<p>'))
            self.assertNotRegex(bodies['en'], r'[\u3400-\u9fff]')
            self.assertNotRegex(bodies['hant'], r'覈實|覈對|余項|復核|限製|划定|開啓|寫准|稱贊|啓用|阿裡')
            self.assertEqual(self.counts[d['slug']]['zh_han'], len(re.findall(r'[\u3400-\u9fff]', ''.join(d['body_zh']))))
            self.assertEqual(self.counts[d['slug']]['en_words'], len(' '.join(d['body_en']).split()))

    def test_numbered_sources_in_both_editions(self):
        self.assertEqual([len(d['sources']) for d in self.items], [6, 8, 7, 7])
        for d in self.items:
            numbers = {s['id'] for s in d['sources']}
            text = self.pages[ROOT/('essays/cooperation-histories/' + d['slug'] + '.html')]
            for lang in ('en', 'zh'):
                self.assertEqual(set(map(int, re.findall(r'\[(\d+)\]', '\n'.join(d['body_' + lang])))), numbers)
            for source in d['sources']:
                self.assertIn('Source ' + str(source['id']), text)
                self.assertIn(source['url'].replace('&', '&amp;'), text)
                self.assertTrue(all(source[k].strip() for k in ('title_en', 'title_zh', 'note_en', 'note_zh')))

    def test_metadata_and_beacon(self):
        for path, text in self.pages.items():
            tags = Tags(text).items
            url = BASE + ('' if path.name == 'index.html' else path.name)
            self.assertEqual([a['href'] for t,a in tags if t == 'link' and a.get('rel') == 'canonical'], [url])
            self.assertEqual(len([a for t,a in tags if t == 'header']), 1)
            self.assertEqual({a['class'] for t,a in tags if t == 'h1'}, {'lang-en', 'lang-zh', 'lang-hant'})
            beacons = [a for t,a in tags if t == 'script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
            self.assertEqual(len(beacons), 1)
            self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'], TOKEN)
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
            self.assertEqual(schema['datePublished'], DATE)
            self.assertEqual(schema['inLanguage'], ['en', 'zh-Hans', 'zh-Hant'])
            if path.name == 'index.html':
                self.assertEqual(len(schema['hasPart']), 4)
            else:
                d = next(d for d in self.items if d['slug'] == path.stem)
                self.assertEqual(schema['citation'], [s['url'] for s in d['sources']])
                self.assertEqual(schema['isPartOf']['url'], BASE)
                self.assertEqual(schema['temporalCoverage'], d['coverage'])

    def test_local_links_and_unique_ids(self):
        for path, text in self.pages.items():
            tags = Tags(text).items
            ids = [a['id'] for t,a in tags if 'id' in a]
            self.assertEqual(len(ids), len(set(ids)))
            for tag, attrs in tags:
                raw = attrs.get('href' if tag in ('a','link') else 'src', '')
                parts = urlsplit(raw)
                if not raw or parts.scheme or parts.netloc:
                    continue
                target = ROOT/unquote(parts.path.lstrip('/')) if parts.path.startswith('/') else path.parent/unquote(parts.path)
                if parts.path:
                    self.assertTrue(target.is_file(), str(path) + ': ' + raw)
                if parts.fragment:
                    self.assertRegex(target.read_text() if parts.path else text, r'\bid=["\']' + re.escape(parts.fragment) + r'["\']')

    def test_rhine_historical_and_legal_boundaries(self):
        d = self.items[0]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for phrase in ('不是一个国际组织制造的事故', '1963年', '1985至2000年', '多数', '点源排放', '第十一条', '1986年已经全部如此运作', '一条河的改善，不能替每一份个人请求写出结局'):
            self.assertIn(phrase, zh)
        self.assertIn('not a single percentage measuring every kind of pollution', en)
        self.assertIn('Article 11', en)
        self.assertIn('not a description to project backward', en)
        self.assertIn('Article 9 concerns plenary sessions', d['sources'][5]['note_en'])

    def test_haiti_distinctions_and_cutoff(self):
        d = self.items[1]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for phrase in ('2011年11月3日', '2013年2月', '2016年8月18日', '先决条件', '不是联合国在事实与实体责任上已经胜诉', '不是一份法院确定损害赔偿责任的判决', '调查可能揭示事实', '2016年底'):
            self.assertIn(phrase, zh)
        self.assertIn('not a judgment clearing the organization on the merits', en)
        self.assertIn('does not claim that every form of criticism', en)
        self.assertIn('later implementation needs later records', en)
        self.assertIn('not assert that this court found a Section 29 breach', d['sources'][5]['note_en'])

    def test_discovery_and_open_ended_shelf(self):
        for name in ('library.html','explore.html','index.html','latest.html','essays/sae/index.html'):
            self.assertIn('essays/cooperation-histories/index.html', (ROOT/name).read_text())
        fictional = (ROOT/'essays/interstate/index.html').read_text()
        self.assertIn('../cooperation-histories/index.html', fictional)
        self.assertEqual(fictional.count('class="lw-card"'), 3)
        landing = self.pages[ROOT/'essays/cooperation-histories/index.html']
        self.assertEqual(landing.count('class="lw-card"'), 4)
        self.assertIn('An ongoing series', landing)
        self.assertIn('责任来源不同，不是两个相反的评分', landing)
        self.assertIn('制裁、名字与复审', landing)
        self.assertIn('水流、损害与请求', landing)
        self.assertNotIn('First two essays', landing)
        self.assertEqual(landing.count('<h3 class="lang-en">'), 4)
        library = (ROOT/'library.html').read_text()
        self.assertGreater(library.index('<!-- COOPERATION HISTORIES LIBRARY START -->'), library.index('Category 06'))
        self.assertLess(library.index('<!-- COOPERATION HISTORIES LIBRARY START -->'), library.index('Category 07'))

    def test_search_and_sitemap(self):
        for lang in ('en','zh-hans','zh-hant'):
            records = {r['u']:r for r in json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']}
            for path in self.pages:
                relative = path.relative_to(ROOT).as_posix()
                self.assertIn(relative, records)
                self.assertEqual(records[relative]['d'], 'history')
                self.assertEqual(scan_page(ROOT,path)['domain'], 'history')
            if lang != 'en':
                self.assertIn('道歉', records['essays/cooperation-histories/haiti-cholera.html']['x'])
        urls = {e.text for e in ET.fromstring((ROOT/'sitemap.xml').read_text()).findall('{*}url/{*}loc')}
        for path in self.pages:
            self.assertIn(BASE + ('' if path.name == 'index.html' else path.name), urls)
        updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        selected = [u for u in updates if u['id'] == '2026-10-30-cooperation-histories']
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]['domain'], 'history')
        new_update = [u for u in updates if u['id'] == '2026-10-30-cooperation-histories-batch02']
        self.assertEqual(len(new_update), 1)
        self.assertEqual(new_update[0]['kind'], 'expanded')

    def test_iraq_causation_implementation_and_access(self):
        d = self.items[2]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for phrase in ('伊拉克入侵科威特', '保留严格医疗用途物资的例外', '伊拉克政府没有接受', '2002年新程序', '2017年', '不是把外部捐来的粮食', '没有因此成为', '并非宣布世界上不存在其他声音'):
            self.assertIn(phrase, zh)
        self.assertNotRegex(zh, r'五十万|五十萬|50万|500,?000')
        self.assertIn('principally financed by the sale of Iraqi oil', en)
        self.assertIn('not a judicial finding', en)
        self.assertIn('not a collection of named entries', en)
        self.assertIn('repetition of 1999 mortality estimates is not adopted', d['sources'][3]['note_en'])

    def test_kadi_review_is_not_a_world_court_or_acquittal(self):
        d = self.items[3]
        zh, en = '\n'.join(d['body_zh']), '\n'.join(d['body_en'])
        for phrase in ('不是一份已经由刑事法庭定罪', '2008年9月3日', '最多维持三个月', '2013年7月18日', '并未接受普通法院的全部分析', '保密的理由本身需要接受检查', '2012年10月5日', '这发生在2013年欧洲法院判决之前', '早在当年6月通过'):
            self.assertIn(phrase, zh)
        for phrase in ('not a criminal conviction', 'one sufficiently specific, substantiated ground', 'sixty days after the committee', 'A focal-point route had existed before', 'not a judge’s final order', 'preceded the 2013 European judgment'):
            self.assertIn(phrase, en)
        self.assertTrue(d['sources'][1]['url'].startswith('https://eur-lex.europa.eu/'))

    def test_first_pair_is_byte_preserved(self):
        self.assertEqual(self.receipt['published_essays'], 2)
        self.assertEqual(self.batch2['published_essays'], 4)
        self.assertEqual(self.batch2['new_essays'], ['iraq-sanctions', 'kadi-listing'])
        hashes = json.loads((ROOT/'reports/cooperation-histories-batch02-20261030.json').read_text())['preserved_first_pair_sha256']
        for slug, expected in hashes.items():
            self.assertEqual(hashlib.sha256((ROOT/'essays/cooperation-histories'/f'{slug}.html').read_bytes()).hexdigest(), expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
