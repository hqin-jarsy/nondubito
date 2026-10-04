#!/usr/bin/env python3
"""Source-preservation and publication checks for the two new Western series."""
import copy
import html
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit
import build_western_classics as build
from build_content_registry import scan_page
from test_recent_fiction import Page


class ClassicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build.build()
        cls.received = json.loads((build.ROOT/'data/western-classics-received.json').read_text())
        cls.items = {slug:build.load(slug) for slug in build.SERIES}

    def test_reproducible_inventory(self):
        self.assertEqual(len(self.outputs),20)
        self.assertEqual(sum(map(len,self.items.values())),18)
        for path,source in self.outputs.items():
            self.assertEqual(path.read_text(),source,str(path))

    def test_original_chinese_preserved_except_logged_edits(self):
        count = 0
        for slug,items in self.items.items():
            for item,received in zip(items,self.received[slug]['entries']):
                with self.subTest(series=slug,number=item['number']):
                    original = copy.deepcopy(received['original_zh'])
                    for edit in item['editorial']['zh_edits']:
                        occurrences = sum(p.count(edit['old']) for s in original['sections'] for p in s['paragraphs'])
                        occurrences += original.get('aside','').count(edit['old'])
                        self.assertEqual(occurrences,1,edit['old'])
                        for s in original['sections']:
                            s['paragraphs'] = [p.replace(edit['old'],edit['new']) for p in s['paragraphs']]
                        if 'aside' in original: original['aside'] = original['aside'].replace(edit['old'],edit['new'])
                    for edit in item['editorial'].get('heading_edits',[]):
                        self.assertEqual(sum(s['heading']==edit['old'] for s in original['sections']),1)
                        for s in original['sections']:
                            if s['heading']==edit['old']: s['heading']=edit['new']
                    self.assertEqual(original['title'],item['zh']['title'])
                    self.assertEqual(original['sections'],item['zh']['sections'])
                    self.assertEqual(original.get('aside'),item['zh'].get('aside'))
                    count += sum(len(s['paragraphs']) for s in original['sections'])
        self.assertEqual(count,370)

    def test_full_language_bodies(self):
        for slug,items in self.items.items():
            for item in items:
                source = self.outputs[build.ROOT/'essays'/slug/(item['slug']+'.html')]
                bodies = dict(re.findall(r'<div class="western-prose lang-([^"]+)" lang="[^"]+">(.*?)</div>',source,re.S))
                self.assertEqual(set(bodies),{'en','zh','hant'})
                for lang in ('en','zh'):
                    paragraphs = [p for s in item[lang]['sections'] for p in s['paragraphs']]
                    self.assertEqual(bodies[lang].count('<p>'),len(paragraphs))
                    for p in paragraphs: self.assertIn(html.escape(p,quote=True),bodies[lang])
                self.assertEqual(bodies['zh'].count('<p>'),bodies['hant'].count('<p>'))
                self.assertGreater(sum(len(p.split()) for s in item['en']['sections'] for p in s['paragraphs']),400)
                self.assertEqual(item['editorial']['coverage'],[s['heading'] or 'Opening' for s in item['zh']['sections']])
                self.assertEqual(len(item['en']['sections']),len(item['zh']['sections']))
                self.assertEqual('class="western-aside"' in source,bool(item['zh'].get('aside')))
                self.assertNotIn('class="western-aside" open',source)

    def test_metadata_html_and_local_links(self):
        for path,source in self.outputs.items():
            with self.subTest(page=str(path)):
                page = Page(source)
                self.assertEqual(page.errors,[])
                self.assertEqual(len(page.ids),len(set(page.ids)))
                self.assertEqual(source.count('<header'),1)
                self.assertEqual(len(page.schemas),1)
                schema = page.schemas[0]
                self.assertEqual(schema['inLanguage'],['en','zh-Hans','zh-Hant'])
                canonical = 'https://nondubito.net/'+str(path.relative_to(build.ROOT))
                if path.name=='index.html': canonical=canonical.removesuffix('index.html')
                self.assertEqual(schema['url'],canonical)
                self.assertIn(f'<link rel="canonical" href="{canonical}">',source)
                self.assertEqual(schema['@type'],'CollectionPage' if path.name=='index.html' else 'Article')
                if path.name!='index.html': self.assertTrue(schema['citation'])
                for href in page.links:
                    link = urlsplit(href)
                    if link.scheme or link.netloc: continue
                    target = (path.parent/unquote(link.path)).resolve() if link.path else path
                    if target.is_dir(): target /= 'index.html'
                    self.assertTrue(target.is_file(),href)
                    if link.fragment: self.assertIn(unquote(link.fragment),Page(target.read_text()).ids)

    def test_previous_next_links(self):
        for slug,items in self.items.items():
            for i,item in enumerate(items):
                source=self.outputs[build.ROOT/'essays'/slug/(item['slug']+'.html')]
                nav=re.search(r'<nav class="western-series-nav".*?</nav>',source,re.S).group()
                for n in (i-1,i+1):
                    href=items[n]['slug']+'.html' if 0<=n<len(items) else 'index.html'
                    self.assertIn('href="'+href+'"',nav)

    def test_traditional_context_corrections(self):
        c=build.Converter()
        try:
            self.assertEqual(c.convert('笛卡尔沉思集'),'笛卡爾沉思集')
            for old,new in [('讲明了','講明了'),('说明了一点','說明了一點'),('替自己干活','替自己幹活'),('对不太准','對不太準'),('准下雨','準下雨')]:
                self.assertEqual(c.convert(old),new)
        finally: c.close()

    def test_search_and_sitemap(self):
        ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
        locations={x.text for x in ET.parse(build.ROOT/'sitemap.xml').findall('.//'+ns+'loc')}
        chunks={l:json.loads((build.ROOT/'data/search'/f'{l.lower()}.json').read_text())['records'] for l in ('en','zh-Hans','zh-Hant')}
        for path,source in self.outputs.items():
            page=scan_page(build.ROOT,path)
            self.assertEqual(page['category'],'sae-western')
            self.assertEqual(page['domain'],'sae-philosophy')
            self.assertEqual(set(page['languages']),set(chunks))
            self.assertIn(Page(source).schemas[0]['url'],locations)
            for lang,records in chunks.items():
                matches=[r for r in records if r['u']==str(path.relative_to(build.ROOT))]
                self.assertEqual(len(matches),1)
                self.assertEqual(matches[0]['t'],page['titles'][lang])
                self.assertTrue(matches[0]['x'])

    def test_shelf_library_latest(self):
        shelf=(build.ROOT/'essays/sae-western/index.html').read_text()
        self.assertEqual(shelf.count('class="western-book"'),6)
        for slug in self.items:
            self.assertIn(f'../{slug}/index.html',shelf)
            self.assertIn(f'essays/{slug}/index.html',(build.ROOT/'library.html').read_text())
        ledger=json.loads((build.ROOT/'data/site-updates.json').read_text())
        updates=[e for e in ledger['updates'] if e['id']=='2026-10-03-descartes-spinoza']
        self.assertEqual(len(updates),1)
        self.assertEqual(updates[0]['languages'],['en','zh','zh-hant'])
        self.assertIn(updates[0]['id'],(build.ROOT/'latest.html').read_text())

if __name__=='__main__': unittest.main()
