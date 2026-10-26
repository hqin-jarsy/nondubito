#!/usr/bin/env python3
"""Publication and navigation-preservation checks for Language & Writing."""
import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit

from build_language_writing import ROOT,render,load_items,WritingTraditionalConverter
from update_sae_navigation import CARD,library_block,render_library,render_explore
from build_content_registry import scan_page,parse_library_categories
from build_search_index import extract_recent_fiction_descriptions
from web_analytics import TOKEN


class Tags(HTMLParser):
    def __init__(self,text):
        super().__init__()
        self.items=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        self.items.append((tag,dict(attrs)))


class LanguageWritingPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items=load_items()
        cls.pages=render()
        cls.report=json.loads((ROOT/'data/language-writing/publication.json').read_text())
        cls.groups=json.loads((ROOT/'data/sae-reading-map.json').read_text())['groups']

    def test_complete_rebuild(self):
        self.assertEqual(len(self.items),3)
        self.assertEqual(len(self.pages),5)
        for path,text in self.pages.items():
            self.assertEqual(path.read_text(),text)
            self.assertNotIn('TODO',text)

    def test_page_metadata_and_beacon(self):
        for path,text in self.pages.items():
            with self.subTest(page=str(path)):
                tags=Tags(text).items
                headers=[a for t,a in tags if t=='header']
                self.assertEqual(len(headers),1)
                self.assertIn('site-shell-header',headers[0]['class'])
                canonical='https://nondubito.net/'+path.relative_to(ROOT).as_posix().removesuffix('index.html')
                self.assertEqual([a['href'] for t,a in tags if t=='link' and a.get('rel')=='canonical'],[canonical])
                beacons=[a for t,a in tags if t=='script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
                self.assertEqual(len(beacons),1)
                self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'],TOKEN)
                schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
                self.assertEqual(schema['inLanguage'],['en','zh-Hans','zh-Hant'])
                if path.name!='index.html':
                    self.assertEqual(schema['datePublished'],'2026-10-26')
                    self.assertIn(schema['citation'],[i['source_url'] for i in self.items])

    def test_three_complete_reading_modes(self):
        for path,text in self.pages.items():
            with self.subTest(page=path.name):
                self.assertEqual({a['class'] for t,a in Tags(text).items if t=='h1'},{'lang-en','lang-zh','lang-hant'})
                record=scan_page(ROOT,path)
                self.assertEqual(set(record['languages']),{'en','zh-Hans','zh-Hant'})
                self.assertEqual(record['domain'],'sae-philosophy')
                self.assertEqual(set(extract_recent_fiction_descriptions(text)),{'en','zh-Hans','zh-Hant'})
                if path.name=='index.html':continue
                bodies=re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="([^"]+)">(.*?)</div>',text,re.S)
                self.assertEqual(len(bodies),3)
                for language,native,body in bodies:
                    self.assertEqual(body.count('<h2>'),3)
                    self.assertNotIn('<h3',body)
                    self.assertGreater(body.count('<p>'),18)
                    if language=='en':self.assertNotRegex(body,r'[\u3400-\u9fff]')
                hant=next(b for l,n,b in bodies if l=='hant')
                self.assertNotRegex(hant,r'余項|一髮過去|鄰裡|松了|說明瞭|深沈|贊美|兩只|調用的本領')

    def test_contextual_traditional_conversion(self):
        converter=WritingTraditionalConverter()
        try:
            self.assertEqual(converter.convert('默认这句成立，文件说明；余项、沉默、邻里互助，一发过去，松了口气，赞美父亲。'),'默認這句成立，文件說明；餘項、沉默、鄰里互助，一發過去，鬆了口氣，讚美父親。')
        finally:converter.close()

    def test_local_urls_and_fragments(self):
        for path,text in self.pages.items():
            for tag,attrs in Tags(text).items:
                url=attrs.get('href' if tag in ('a','link') else 'src','')
                parts=urlsplit(url)
                if not url or parts.scheme or parts.netloc:continue
                target=(ROOT/unquote(parts.path.lstrip('/'))) if parts.path.startswith('/') else path.parent/unquote(parts.path)
                if parts.path:self.assertTrue(target.is_file(),f'{path}: {url}')
                if parts.fragment:
                    source=target.read_text() if parts.path else text
                    self.assertRegex(source,r'\bid=["\']'+re.escape(parts.fragment)+r'["\']')

    def test_card_copy_preserved_and_groups_reproducible(self):
        source=(ROOT/'library.html').read_text()
        _,_,block=library_block(source)
        cards={re.search(r'href="([^"]+)"',m[0])[1]:m[0] for m in CARD.finditer(block)}
        self.assertGreaterEqual(len(cards),30)
        for url,digest in self.report['navigation']['old_category02_card_sha256'].items():
            self.assertEqual(hashlib.sha256(cards[url].encode()).hexdigest(),digest,url)
        self.assertEqual(len(self.groups),6)
        self.assertEqual(block.count('class="sae-library-group"'),6)
        categories=parse_library_categories(ROOT/'library.html')
        self.assertEqual(len(categories),18)
        self.assertEqual(next(c for c in categories if c['number']==2)['series_count'],len(cards))
        conv=WritingTraditionalConverter()
        try:
            self.assertEqual(render_library(source,self.groups,conv),source)
            explore=(ROOT/'explore.html').read_text()
            self.assertEqual(render_explore(explore,self.groups,conv),explore)
        finally:conv.close()

    def test_six_explore_routes_and_full_hub(self):
        explore=(ROOT/'explore.html').read_text()
        block=re.search(r'<section class="domain-section" id="sae">(.*?)</section>',explore,re.S)[1]
        self.assertEqual(block.count('class="shelf-link"'),6)
        hub=self.pages[ROOT/'essays/sae/index.html']
        self.assertEqual(hub.count('class="sae-group"'),6)
        self.assertLess(hub.index('class="sae-jump"'),hub.index('class="lw-opening"'))
        for group in self.groups:
            self.assertIn('href="essays/sae/index.html#'+group['id']+'"',block)
            for url,zh,en in group['items']:
                self.assertIn('href="../../'+url+'"',hub)
        self.assertIn('href="essays/sae/index.html"',(ROOT/'index.html').read_text())

    def test_search_sitemap_and_publication_receipts(self):
        for language in ('en','zh-hans','zh-hant'):
            records=json.loads((ROOT/f'data/search/{language}.json').read_text())['records']
            urls={r['u'] for r in records}
            self.assertTrue(all(p.relative_to(ROOT).as_posix() in urls for p in self.pages))
        root=ET.fromstring((ROOT/'sitemap.xml').read_text())
        urls={x.text for x in root.findall('{*}url/{*}loc')}
        for path in self.pages:
            self.assertIn('https://nondubito.net/'+path.relative_to(ROOT).as_posix().removesuffix('index.html'),urls)
        self.assertEqual({p['url'] for p in self.report['papers']},{i['source_url'] for i in self.items})
        for paper in self.report['papers']:
            self.assertTrue(paper['matches_author_local'])
            self.assertRegex(paper['sha256'],r'^[0-9a-f]{64}$')
        for name in ('index.html','library.html','latest.html'):
            self.assertIn('essays/language-writing/index.html',(ROOT/name).read_text())
        updates=json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        self.assertEqual(len([u for u in updates if u['id']=='2026-10-26-language-writing']),1)


if __name__=='__main__':
    unittest.main(verbosity=2)
