#!/usr/bin/env python3
"""Guard complete editions, staged publication, scope and discoverability."""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

from build_interstate import BASE, DATA, DATE, ROOT, load_items, render
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

    def test_reproducible_pages_and_updates(self):
        self.assertEqual(len(self.pages), 4)
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
            counts = self.receipt['counts'][item['slug']]
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
        self.assertEqual(index.count('class="lw-card"'), 3)
        self.assertIn('九篇散文计划 · 已发布首批三篇', index)
        future = index.split('<ol class="is-roadmap" start="4">')[1].split('</ol>')[0]
        self.assertEqual(future.count('<li>'), 6)
        self.assertNotIn('<a ', future)
        for n in range(4, 10):
            self.assertNotIn(f'ep{n:02d}.html', index)
            self.assertFalse((ROOT/f'essays/interstate/ep{n:02d}.html').exists())

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
            self.assertEqual(schema['datePublished'], DATE)
            if path.name == 'index.html':
                self.assertEqual([p['url'] for p in schema['hasPart']], [BASE + d['slug'] + '.html' for d in self.items])
            else:
                d = next(d for d in self.items if d['slug'] == path.stem)
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
        one, two, three = ['\n'.join(d['body_zh']) for d in self.items]
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
        self.assertEqual({p['url'] for p in self.receipt['papers']}, {d['source_url'] for d in self.items})
        for paper in self.receipt['papers']:
            self.assertEqual(paper['http'], 200)
            self.assertTrue(paper['matches_author_local'])
            self.assertRegex(paper['sha256'], r'^[0-9a-f]{64}$')

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
