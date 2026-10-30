#!/usr/bin/env python3
"""Check the three-mode State companion and preservation of the eight main essays."""
import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit,unquote
from build_state_reversal import ROOT,DATA,TARGET,BASE,STATE_BASE,SOURCE,DATE,load_items,render,ReversalTraditionalConverter
from build_state_series import render as state_render
from build_content_registry import scan_page
from build_search_index import extract_recent_fiction_descriptions
from test_language_writing import Tags
from web_analytics import TOKEN


class StateReversalPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items=load_items()
        cls.pages=render()
        cls.receipt=json.loads((DATA/'publication.json').read_text())
        cls.qa=json.loads((ROOT/'reports/state-reversal-publication-20261029.json').read_text())

    def test_complete_rebuild(self):
        self.assertEqual(len(self.items),3)
        self.assertEqual(len(self.pages),4)
        for path,text in self.pages.items():
            self.assertEqual(path.read_text(),text)
            self.assertNotIn('TODO',text)
            self.assertNotRegex(text,r'\b\d{2}DD\b|\bN\d+\b')

    def test_metadata_dates_and_tracking(self):
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
                self.assertEqual(schema['datePublished'],DATE)
                self.assertEqual(schema['dateModified'],DATE)
                self.assertEqual(schema['citation'],SOURCE)
                self.assertEqual(schema['isPartOf']['url'],STATE_BASE)

    def test_complete_reading_modes(self):
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
            self.assertNotRegex(bodies['hant'],r'覈實|覈對|舊賬|余項|復核')

    def test_local_links(self):
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

    def test_main_route_and_source_files_preserved(self):
        self.assertEqual(len(self.qa['original_article_sha256']),8)
        for name,digest in self.qa['original_article_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/'essays/state'/name).read_bytes()).hexdigest(),digest)
        self.assertEqual(len(self.qa['original_data_sha256']),8)
        for name,digest in self.qa['original_data_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/'data/state'/name).read_bytes()).hexdigest(),digest)
        self.assertFalse((ROOT/'essays/state/ep08.html').exists())
        for path,text in state_render().items():self.assertEqual(path.read_text(),text)
        landing=(ROOT/'essays/state/index.html').read_text()
        self.assertIn('id="reverse-phase-transition"',landing)
        self.assertIn('href="#reverse-phase-transition"',landing)
        self.assertEqual(landing.count('class="state-card"'),8)
        schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',landing,re.S)[1])
        self.assertEqual(schema['datePublished'],'2026-10-25')
        self.assertEqual(schema['dateModified'],DATE)

    def test_discovery_and_receipts(self):
        for lang in ('en','zh-hans','zh-hant'):
            urls={r['u'] for r in json.loads((ROOT/f'data/search/{lang}.json').read_text())['records']}
            for p in self.pages:self.assertTrue(p.relative_to(ROOT).as_posix() in urls,f'{lang}: missing {p.name}')
        urls={e.text for e in ET.fromstring((ROOT/'sitemap.xml').read_text()).findall('{*}url/{*}loc')}
        for p in self.pages:self.assertIn(BASE+('' if p.name=='index.html' else p.name),urls)
        for name in ('index.html','latest.html','essays/state/index.html'):
            self.assertIn('state-reversal/index.html',(ROOT/name).read_text())
        self.assertIn('含逆相变专论',(ROOT/'essays/sae/index.html').read_text())
        source=self.receipt['source']
        self.assertEqual(source['url'],SOURCE)
        self.assertTrue(source['matches_author_local'])
        self.assertEqual(source['status'],200)
        self.assertRegex(source['sha256'],r'^[0-9a-f]{64}$')
        for d in self.items:
            counts=self.qa['counts'][d['slug']]
            self.assertEqual(counts['zh_han'],len(re.findall(r'[\u3400-\u9fff]',''.join(d['body_zh']))))
            self.assertEqual(counts['en_words'],len(' '.join(d['body_en']).split()))
        entries=[u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id']=='2026-10-29-state-reversal']
        self.assertEqual(len(entries),1)
        self.assertEqual(set(entries[0]['languages']),{'en','zh','zh-hant'})


if __name__=='__main__':unittest.main(verbosity=2)
