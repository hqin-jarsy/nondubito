#!/usr/bin/env python3
"""Check the Accountability companion without altering the original Rights route."""
import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit,unquote

from build_accountability import ROOT,TARGET,DATA,BASE,SOURCE,load_items,render,AccountabilityTraditionalConverter
from build_content_registry import scan_page,parse_library_categories
from build_search_index import extract_recent_fiction_descriptions
from web_analytics import TOKEN
from test_language_writing import Tags


class AccountabilityPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items=load_items()
        cls.pages=render()
        cls.new_pages={p:s for p,s in cls.pages.items() if p.parent==TARGET}
        cls.report=json.loads((DATA/'publication.json').read_text())

    def test_rebuild_and_complete_manuscripts(self):
        self.assertEqual(len(self.new_pages),4)
        self.assertEqual(len(self.pages),5)
        for path,text in self.pages.items():self.assertEqual(path.read_text(),text)
        for item in self.items:
            for lang in ('en','zh'):
                self.assertEqual(sum(p.startswith('## ') for p in item['body_'+lang]),3)
                self.assertNotRegex(' '.join(item['body_'+lang]),r'\b\d{2}DD\b|\b[FT]\d+\b|TODO')

    def test_metadata_analytics_and_classification(self):
        for path,text in self.new_pages.items():
            with self.subTest(page=path.name):
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
                record=scan_page(ROOT,path)
                self.assertEqual(record['domain'],'sae-philosophy')
                self.assertEqual(set(record['languages']),{'en','zh-Hans','zh-Hant'})
                self.assertEqual(set(extract_recent_fiction_descriptions(text)),{'en','zh-Hans','zh-Hant'})

    def test_reading_modes_and_contextual_traditional(self):
        for path,text in self.new_pages.items():
            self.assertEqual({a.get('class') for t,a in Tags(text).items if t=='h1'},{'lang-en','lang-zh','lang-hant'})
            if path.name=='index.html':continue
            bodies=dict(re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>',text,re.S))
            self.assertEqual(set(bodies),{'en','zh','hant'})
            for body in bodies.values():
                self.assertGreaterEqual(body.count('<p>'),18)
                self.assertEqual(body.count('<h2>'),3)
                self.assertNotIn('<h3',body)
            self.assertNotRegex(bodies['en'],r'[\u3400-\u9fff]')
            self.assertNotRegex(bodies['hant'],r'覈實|沈重|舊賬|調用的本領|余項')

    def test_original_seven_and_dictionary_retained(self):
        preserved=self.report['preservation']
        for name,digest in preserved['old_seven_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/'essays/rights'/name).read_bytes()).hexdigest(),digest)
        index=self.pages[ROOT/'essays/rights/index.html']
        old_list=re.search(r'<ul class="entry-list">.*?</ul>',index,re.S)[0]
        self.assertEqual(old_list.count('class="entry-row"'),7)
        self.assertEqual(hashlib.sha256(old_list.encode()).hexdigest(),preserved['old_rights_entry_list_sha256'])
        dictionary=(ROOT/'essays/rights/zh-hant-data/index.js').read_text()
        variants=re.search(r'var variants = (.*?);\n',dictionary)[1]
        self.assertEqual(hashlib.sha256(variants.encode()).hexdigest(),preserved['old_hant_variants_sha256'])
        self.assertIn('.accountability-entry, script, style',dictionary)
        block=re.search(r'<!-- ACCOUNTABILITY COMPANION START -->(.*?)<!-- ACCOUNTABILITY COMPANION END -->',index,re.S)[1]
        self.assertEqual(block.count('<section'),3)
        for language in ('en','zh','zh-hant'):
            self.assertIn('../accountability/index.html?lang='+language+'"',block)

    def test_local_targets(self):
        for path,text in self.new_pages.items():
            for tag,attrs in Tags(text).items:
                raw=attrs.get('href' if tag in ('a','link') else 'src','')
                parts=urlsplit(raw)
                if not raw or parts.scheme or parts.netloc:continue
                target=(ROOT/unquote(parts.path.lstrip('/'))) if parts.path.startswith('/') else path.parent/unquote(parts.path)
                if parts.path:self.assertTrue(target.is_file(),f'{path}: {raw}')
                if parts.fragment:
                    source=target.read_text() if parts.path else text
                    self.assertRegex(source,r'\bid=["\']'+re.escape(parts.fragment)+r'["\']')

    def test_discovery_and_existing_card_copy(self):
        for name in ('index.html','library.html','latest.html','essays/sae/index.html','essays/rights/index.html'):
            self.assertIn('accountability/index.html',(ROOT/name).read_text())
        categories=parse_library_categories(ROOT/'library.html')
        sae=next(c for c in categories if c['number']==2)
        self.assertGreaterEqual(sae['series_count'],31)
        self.assertEqual(sae['series_hrefs'].count('essays/accountability/index.html'),1)
        self.assertLess(sae['series_hrefs'].index('essays/rights/index.html'),sae['series_hrefs'].index('essays/accountability/index.html'))
        # The preceding batch's tests independently retain all 29 original
        # cards. Keep its added Language & Writing card exact too.
        library=(ROOT/'library.html').read_text()
        card=re.search(r'<a href="essays/language-writing/index.html" class="series-card">.*?</a>',library,re.S)[0]
        self.assertEqual(hashlib.sha256(card.encode()).hexdigest(),'1335298812e2785ad31b1332f93a3f2262f222bfa3c24a25d7c2219b47ad1384')

    def test_search_sitemap_and_receipt(self):
        for language in ('en','zh-hans','zh-hant'):
            records=json.loads((ROOT/f'data/search/{language}.json').read_text())['records']
            urls={r['u'] for r in records}
            for p in self.new_pages:self.assertIn(p.relative_to(ROOT).as_posix(),urls)
        urls={e.text for e in ET.fromstring((ROOT/'sitemap.xml').read_text()).findall('{*}url/{*}loc')}
        for p in self.new_pages:self.assertIn(BASE+('' if p.name=='index.html' else p.name),urls)
        self.assertEqual(self.report['source']['url'],SOURCE)
        self.assertTrue(self.report['source']['matches_author_local'])
        self.assertRegex(self.report['source']['sha256'],r'^[0-9a-f]{64}$')
        updates=json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        matching=[u for u in updates if u['id']=='2026-10-26-accountability']
        self.assertEqual(len(matching),1)
        self.assertEqual(set(matching[0]['languages']),{'en','zh','zh-hant'})


if __name__=='__main__':unittest.main(verbosity=2)
