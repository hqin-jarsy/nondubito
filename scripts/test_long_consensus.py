#!/usr/bin/env python3
"""Check complete Long Consensus editions and bounded site integration."""
import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit,unquote

from build_long_consensus import ROOT,TARGET,DATA,BASE,SOURCE,load_items,render,ConsensusTraditionalConverter
from build_content_registry import scan_page,parse_library_categories
from build_search_index import extract_recent_fiction_descriptions
from update_sae_navigation import CARD,library_block
from test_language_writing import Tags
from web_analytics import TOKEN


class LongConsensusPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items=load_items()
        cls.pages=render()
        cls.report=json.loads((DATA/'publication.json').read_text())
        cls.qa=json.loads((ROOT/'reports/long-consensus-publication-20261026.json').read_text())

    def test_complete_reproducible_manuscripts(self):
        self.assertEqual(len(self.items),5)
        self.assertEqual(len(self.pages),6)
        for path,text in self.pages.items():
            self.assertEqual(path.read_text(),text)
            self.assertNotIn('TODO',text)
            self.assertNotRegex(text,r'\b\d{2}DD\b|ψ|ZFC')

    def test_metadata_beacon_and_source(self):
        for path,text in self.pages.items():
            tags=Tags(text).items
            headers=[a for t,a in tags if t=='header']
            self.assertEqual(len(headers),1)
            self.assertIn('site-shell-header',headers[0]['class'])
            self.assertEqual([a['href'] for t,a in tags if t=='link' and a.get('rel')=='canonical'],[BASE+('' if path.name=='index.html' else path.name)])
            beacons=[a for t,a in tags if t=='script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
            self.assertEqual(len(beacons),1)
            self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'],TOKEN)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
            self.assertEqual(schema['inLanguage'],['en','zh-Hans','zh-Hant'])
            if path.name!='index.html':
                self.assertEqual(schema['citation'],SOURCE)
                self.assertEqual(schema['isPartOf']['url'],BASE)
                self.assertEqual(schema['datePublished'],'2026-10-26')

    def test_three_complete_reading_modes(self):
        for path,text in self.pages.items():
            self.assertEqual({a.get('class') for t,a in Tags(text).items if t=='h1'},{'lang-en','lang-zh','lang-hant'})
            record=scan_page(ROOT,path)
            self.assertEqual(record['domain'],'sae-philosophy')
            self.assertEqual(set(record['languages']),{'en','zh-Hans','zh-Hant'})
            self.assertEqual(set(extract_recent_fiction_descriptions(text)),{'en','zh-Hans','zh-Hant'})
            if path.name=='index.html':continue
            bodies=dict(re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>',text,re.S))
            self.assertEqual(set(bodies),{'en','zh','hant'})
            for body in bodies.values():
                self.assertGreaterEqual(body.count('<p>'),20)
                self.assertEqual(body.count('<h2>'),3)
                self.assertNotIn('<h3',body)
            self.assertNotRegex(bodies['en'],r'[\u3400-\u9fff]')
            self.assertNotRegex(bodies['hant'],r'覈實|沈到|幾只紙箱|有點松|每周|鏈接|硬盤|文件夾|工作文檔|余項|代碼')

    def test_contextual_traditional(self):
        conv=ConsensusTraditionalConverter()
        try:
            self.assertEqual(conv.convert('每周核实几只纸箱，椅背有点松；链接沉到下面，硬盘里的文件夹，账目与模型设置代码。'),'每週核實幾隻紙箱，椅背有點鬆；連結沉到下面，硬碟裡的資料夾，帳目與模型設定程式碼。')
        finally:conv.close()

    def test_local_targets_and_fragments(self):
        for path,text in self.pages.items():
            for tag,attrs in Tags(text).items:
                raw=attrs.get('href' if tag in ('a','link') else 'src','')
                parts=urlsplit(raw)
                if not raw or parts.scheme or parts.netloc:continue
                target=(ROOT/unquote(parts.path.lstrip('/'))) if parts.path.startswith('/') else path.parent/unquote(parts.path)
                if parts.path:self.assertTrue(target.is_file(),f'{path}: {raw}')
                if parts.fragment:
                    source=target.read_text() if parts.path else text
                    self.assertRegex(source,r'\bid=["\']'+re.escape(parts.fragment)+r'["\']')

    def test_preserve_all_preceding_cards(self):
        library=(ROOT/'library.html').read_text()
        _,_,block=library_block(library)
        cards={re.search(r'href="([^"]+)"',m[0])[1]:m[0] for m in CARD.finditer(block)}
        self.assertEqual(len(self.qa['old_card_sha256']),31)
        for url,digest in self.qa['old_card_sha256'].items():
            self.assertEqual(hashlib.sha256(cards[url].encode()).hexdigest(),digest,url)
        categories=parse_library_categories(ROOT/'library.html')
        sae=next(c for c in categories if c['number']==2)
        self.assertEqual(sae['series_count'],len(cards))
        self.assertGreaterEqual(sae['series_count'],32)
        self.assertEqual(sae['series_hrefs'].count('essays/long-consensus/index.html'),1)
        self.assertLess(sae['series_hrefs'].index('essays/institution/index.html'),sae['series_hrefs'].index('essays/long-consensus/index.html'))
        for name in ('index.html','library.html','latest.html','essays/sae/index.html'):
            self.assertIn('long-consensus/index.html',(ROOT/name).read_text())

    def test_search_sitemap_and_receipt(self):
        for language in ('en','zh-hans','zh-hant'):
            urls={r['u'] for r in json.loads((ROOT/f'data/search/{language}.json').read_text())['records']}
            for p in self.pages:self.assertIn(p.relative_to(ROOT).as_posix(),urls)
        urls={e.text for e in ET.fromstring((ROOT/'sitemap.xml').read_text()).findall('{*}url/{*}loc')}
        for p in self.pages:self.assertIn(BASE+('' if p.name=='index.html' else p.name),urls)
        source=self.report['source']
        self.assertEqual(source['url'],SOURCE)
        self.assertTrue(source['matches_author_local'])
        self.assertEqual(source['status'],200)
        self.assertRegex(source['sha256'],r'^[0-9a-f]{64}$')
        for d in self.items:
            count=self.qa['counts'][d['slug']]
            self.assertEqual(count['zh_han'],len(re.findall(r'[\u3400-\u9fff]',''.join(d['body_zh']))))
            self.assertEqual(count['en_words'],len(' '.join(d['body_en']).split()))
        updates=json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        matching=[u for u in updates if u['id']=='2026-10-26-long-consensus']
        self.assertEqual(len(matching),1)
        self.assertEqual(set(matching[0]['languages']),{'en','zh','zh-hant'})


if __name__=='__main__':unittest.main(verbosity=2)
