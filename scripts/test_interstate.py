#!/usr/bin/env python3
"""Guard nine complete editions, source boundaries, preservation and navigation."""
import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

from build_interstate import BASE, DATA, DATE, COMPLETE_DATE, ROOT, load_items, render
from connect_interstate import render as entrances
from build_content_registry import scan_page
from test_language_writing import Tags
from web_analytics import TOKEN


class InterstatePublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load_items()
        cls.pages = render()
        cls.receipt = json.loads((DATA/'publication.json').read_text())
        cls.complete = json.loads((DATA/'publication-complete.json').read_text())

    def test_reproducible_pages_and_updates(self):
        self.assertEqual(len(self.pages), 10)
        for path, text in {**self.pages, **entrances()}.items():
            self.assertEqual(path.read_text(), text)
            self.assertNotIn('TODO', text)

    def test_complete_bodies_and_recorded_lengths(self):
        for item in self.items:
            text = self.pages[ROOT/('essays/interstate/' + item['slug'] + '.html')]
            bodies = dict(re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>', text, re.S))
            self.assertEqual(set(bodies), {'en', 'zh', 'hant'})
            for body in bodies.values():
                self.assertGreaterEqual(body.count('<p>'), 25)
                self.assertEqual(body.count('<h2>'), 3)
                self.assertNotRegex(body, r'\b\d{2}DD\b|\bXZ\d+\b|\b[NGZ]\d+\b|\bF6\b')
            self.assertNotRegex(bodies['en'], r'[\u3400-\u9fff]')
            self.assertNotRegex(bodies['hant'], r'覈實|覈對|余項|復核|限製|划定|一髮|開啓')
            counts = {**self.receipt['counts'], **self.complete['counts']}[item['slug']]
            self.assertEqual(counts['zh_han'], len(re.findall(r'[\u3400-\u9fff]', ''.join(item['body_zh']))))
            self.assertEqual(counts['en_words'], len(' '.join(item['body_en']).split()))
            self.assertEqual(bodies['zh'].count('<p>'), bodies['hant'].count('<p>'))

    def test_visible_fiction_and_domain_note(self):
        for path, text in self.pages.items():
            self.assertIn('class="is-notice"', text)
            self.assertIn('文中国家、事件与票数均为虚构', text)
            self.assertIn('不描述所有现实国际组织', text)
            if path.name != 'index.html':
                self.assertLess(text.index('class="is-notice"'), text.index('class="essay-body'))

    def test_only_published_essays_have_cards_and_schema_parts(self):
        index = self.pages[ROOT/'essays/interstate/index.html']
        self.assertEqual(index.count('class="lw-card"'), 9)
        self.assertIn('九篇完整散文', index)
        self.assertNotIn('尚未发布', index)
        self.assertNotIn('next-readings', index)
        self.assertEqual(index.count('class="is-group"'), 3)
        for n in range(1, 10):
            self.assertEqual(index.count(f'class="lw-card" href="ep{n:02d}.html"'), 1)
            self.assertIn(f'href="ep{n:02d}.html"', index)
            self.assertTrue((ROOT/f'essays/interstate/ep{n:02d}.html').exists())
        last = self.pages[ROOT/'essays/interstate/ep09.html']
        self.assertIn('href="ep08.html"', last)
        self.assertIn('href="index.html#reading-route"', last)
        self.assertNotIn('next-readings', last)

    def test_metadata_and_analytics(self):
        for path, text in self.pages.items():
            tags = Tags(text).items
            self.assertEqual(len([a for t,a in tags if t == 'header']), 1)
            self.assertEqual({a['class'] for t,a in tags if t == 'h1'}, {'lang-en', 'lang-zh', 'lang-hant'})
            url = BASE + ('' if path.name == 'index.html' else path.name)
            self.assertEqual([a['href'] for t,a in tags if t == 'link' and a.get('rel') == 'canonical'], [url])
            beacon = [a for t,a in tags if t == 'script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
            self.assertEqual(len(beacon), 1)
            self.assertEqual(json.loads(beacon[0]['data-cf-beacon'])['token'], TOKEN)
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
            self.assertEqual(schema['inLanguage'], ['en', 'zh-Hans', 'zh-Hant'])
            if path.name == 'index.html':
                self.assertEqual(schema['datePublished'], DATE)
                self.assertEqual(schema['dateModified'], COMPLETE_DATE)
                self.assertEqual([p['url'] for p in schema['hasPart']], [BASE + d['slug'] + '.html' for d in self.items])
            else:
                d = next(d for d in self.items if d['slug'] == path.stem)
                self.assertEqual(schema['datePublished'], d.get('date', DATE))
                self.assertEqual(schema['dateModified'], d.get('date', DATE))
                self.assertEqual(schema['citation'], d['source_url'])
                self.assertEqual(schema['isPartOf']['url'], BASE)

    def test_local_links_and_unique_ids(self):
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

    def test_selected_argument_guards(self):
        one, two, three = ['\n'.join(d['body_zh']) for d in self.items[:3]]
        self.assertIn('不是对现实所有国际组织的统一描述', one)
        self.assertIn('不设共同上级', one)
        self.assertIn('不能保证', one)
        for term in ('五十九张反对票', '四十分钟', '九个小时', '运行数据依然没有提供', '猜测填成内幕'):
            self.assertIn(term, two)
        for term in ('问的一方也不能独自宣布', '义务，是因为', '没有记载', '因果不能替它补', '八户', '三百一十一户', '四十一天', '成员国境内'):
            self.assertIn(term, three)
        en = '\n'.join(self.items[2]['body_en'])
        self.assertIn('does not establish that the inquiry caused them', en)
        self.assertIn('absence of information, not verification', en)
        self.assertIn('opinions rather than judgments', en)

    def test_sources_and_publication_receipt(self):
        self.assertEqual(self.receipt['published_essays'], 3)
        self.assertEqual(self.receipt['planned_essays'], 9)
        self.assertEqual(self.complete['published_essays'], 9)
        self.assertEqual(self.complete['new_essays'], [f'ep{i:02d}' for i in range(4, 10)])
        papers = self.receipt['papers'] + self.complete['papers']
        self.assertEqual({p['url'] for p in papers}, {d['source_url'] for d in self.items})
        for paper in papers:
            self.assertEqual(paper['http'], 200)
            self.assertTrue(paper['matches_author_local'])
            self.assertRegex(paper['sha256'], r'^[0-9a-f]{64}$')

    def test_trust_and_economic_pressure_boundaries(self):
        four, five = ['\n'.join(d['body_zh']) for d in self.items[3:5]]
        for term in ('五点二亿', '第十六年份额的四成', '没有记载', '不是保证', '总分'):
            self.assertIn(term, four)
        for term in ('没收', '赔偿经约或裁决', '复核', '不等于', '四十一天', '十五天', '不能只由'):
            self.assertIn(term, five)
        self.assertIn('The proposal fails and the assets are released', '\n'.join(self.items[4]['body_en']))

    def test_defence_and_reception_boundaries(self):
        six, seven = ['\n'.join(d['body_zh']) for d in self.items[5:7]]
        for term in ('差十七票', '九十天', '邀请不是', '没有第三方认定', '非战援助', '两天失守', '成员证'):
            self.assertIn(term, six)
        for term in ('不是得到一个人', '另外设了一例', '故事没有续写结果', '是否追诉', '任何一个国家', '无边界的对外援助义务', '三十一户', '二万人'):
            self.assertIn(term, seven)
        self.assertIn('No outcome is supplied', '\n'.join(self.items[6]['body_en']))

    def test_exit_and_closing_do_not_erase_gaps(self):
        eight, nine = ['\n'.join(d['body_zh']) for d in self.items[7:9]]
        for term in ('六十一位', '七件', '不能把这七次退回', '新约', '仍未决', '程序可以审结', '监所医院'):
            self.assertIn(term, eight)
        for term in ('九个小时', '没有那份统计', '不能替委员会说已经受理', '涨价', '两个村', '不必', '没有保证', '不是现实中的强制已经'):
            self.assertIn(term, nine)
        self.assertIn('The three-party protocol never came into being', '\n'.join(self.items[8]['body_en']))

    def test_original_bodies_and_real_histories_preserved(self):
        for slug, editions in self.complete['preserved_body_sha256'].items():
            source = self.pages[ROOT/f'essays/interstate/{slug}.html']
            bodies = dict(re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>', source, re.S))
            for lang, expected in editions.items():
                self.assertEqual(hashlib.sha256(bodies[lang].encode()).hexdigest(), expected)
        for name, expected in self.complete['preserved_history_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/'essays/cooperation-histories'/name).read_bytes()).hexdigest(), expected)

    def test_shelves_updates_search_and_sitemap(self):
        for name in ('index.html', 'library.html', 'latest.html', 'essays/sae/index.html'):
            self.assertIn('essays/interstate/index.html', (ROOT/name).read_text())
        state = (ROOT/'essays/state/index.html').read_text()
        self.assertIn('../interstate/index.html', state)
        self.assertEqual(state.count('class="state-card"'), 8)
        groups = json.loads((ROOT/'data/sae-reading-map.json').read_text())['groups']
        self.assertEqual(len(groups), 6)
        shelf = next(g for g in groups if g['id'] == 'shared-life')
        self.assertEqual(sum(i[0] == 'essays/interstate/index.html' for i in shelf['items']), 1)
        updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        self.assertEqual(sum(u['id'] == '2026-10-30-interstate-batch01' for u in updates), 1)
        self.assertEqual(sum(u['id'] == '2026-10-31-interstate-complete' for u in updates), 1)
        latest = (ROOT/'latest.html').read_text()
        self.assertEqual(latest.count('data-update-id="2026-10-31-interstate-complete"'), 1)
        home = (ROOT/'index.html').read_text()
        self.assertLess(home.index('<!-- INTERSTATE HOME START -->'), home.index('<!-- MARRIAGE SERIES HOME START -->'))
        for lang in ('en', 'zh-hans', 'zh-hant'):
            records = {d['u']:d for d in json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']}
            for path in self.pages:
                relative = path.relative_to(ROOT).as_posix()
                self.assertEqual(records[relative]['d'], 'sae-philosophy')
                self.assertEqual(scan_page(ROOT, path)['domain'], 'sae-philosophy')
            if lang != 'en':
                self.assertIn('合作', records['essays/interstate/ep01.html']['x'])
        urls = {e.text for e in ET.fromstring((ROOT/'sitemap.xml').read_text()).findall('{*}url/{*}loc')}
        for path in self.pages:
            self.assertIn(BASE + ('' if path.name == 'index.html' else path.name), urls)


if __name__ == '__main__':
    unittest.main(verbosity=2)
