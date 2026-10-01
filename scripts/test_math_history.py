#!/usr/bin/env python3
"""Read-only content, provenance, routing and indexing checks for mathematics."""
import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch
from urllib.parse import urlsplit,unquote
import build_math_history as build
import build_search_index as search
from test_recent_fiction import Page
from test_daodejing_sources import Page as TextPage

RELEASE = '--release' in sys.argv
if RELEASE:
    sys.argv.remove('--release')


class MathematicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items=build.load_items()
        cls.expected=build.outputs()
        cls.c=build.Converter()

    @classmethod
    def tearDownClass(cls):
        cls.c.close()

    def test_inventory_and_full_sections(self):
        ids=[i['id'] for i in self.items]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(sorted(n for g in build.GROUPS for n in g[3]),list(range(1,26)))
        self.assertEqual(len(build.KEYWORDS),25)
        self.assertEqual(len(list(build.TARGET.glob('ep*.html'))),len(ids))
        for item in self.items:
            for lang in ('en','zh'):
                self.assertEqual(len(re.findall(r'^## ',item['body_'+lang],re.M)),8)
            self.assertGreaterEqual(len(item['body_en'].split()),len(item['source']['original'])*.35)
            self.assertEqual(len(item['section_coverage']),8)
            self.assertFalse(re.search(r'<\s*(?:script|iframe|style)\b',item['body_en'],re.I))
            paragraphs=[p.strip() for p in item['body_en'].split('\n\n') if len(p.strip())>150]
            self.assertEqual(len(paragraphs),len(set(paragraphs)),f'Duplicated English paragraphs: {item["id"]}')

    def test_source_edit_provenance_and_no_missing_chinese_paragraphs(self):
        for item in self.items:
            raw=item['source']['original']
            self.assertEqual(build.digest(raw.encode()),item['source']['sha256'])
            edited=raw
            for change in item['edits']:
                self.assertTrue(change['reason'])
                self.assertEqual(edited.count(change['before']),1)
                edited=edited.replace(change['before'],change['after'],1)
            self.assertEqual(build.normalize_zh(edited),item['body_zh'])
            # EP25 adds an explicitly reviewed, dated status note. No original
            # paragraph is removed; this is the sole new Chinese paragraph.
            expected_count=len(re.split(r'\n\s*\n',raw.strip()))+(1 if item['id']==25 else 0)
            self.assertEqual(expected_count,len(re.split(r'\n\s*\n',edited.strip())))

    def test_reproducible_exact_three_editions(self):
        for path,expected in self.expected.items():
            self.assertEqual(path.read_text(),expected,str(path))
        for item in self.items:
            source=(build.TARGET/f'ep{item["id"]:02d}.html').read_text()
            page=TextPage(source)
            for lang,body in [('en',item['body_en']),('zh',item['body_zh']),('hant',self.c.convert(item['body_zh']))]:
                actual=next(n for n in page.nodes if n.has_class('math-prose') and n.has_class('lang-'+lang))
                rendered=TextPage(build.body_html(body,lang))
                self.assertEqual([n.text() for n in actual.descendants('p')],[n.text() for n in rendered.nodes if n.tag=='p'])
                self.assertEqual(len(list(actual.descendants('h2'))),8)

    def test_structure_metadata_and_local_links(self):
        for path,source in self.expected.items():
            page=Page(source)
            self.assertEqual(page.errors,[],str(path))
            self.assertEqual(len(page.ids),len(set(page.ids)),str(path))
            self.assertEqual(source.count('<header'),1,'Only the site header may inherit fixed positioning')
            canonical=build.BASE+('' if path.name=='index.html' else path.name)
            self.assertIn(f'<link rel="canonical" href="{canonical}">',source)
            self.assertEqual(page.schemas[0]['url'],canonical)
            self.assertEqual(page.schemas[0]['inLanguage'],['en','zh-Hans','zh-Hant'])
            for href in page.links:
                link=urlsplit(href)
                if link.scheme or link.netloc:continue
                target=(path.parent/unquote(link.path)).resolve() if link.path else path
                self.assertTrue(target.is_file(),(path,href))
                if link.fragment:self.assertIn(unquote(link.fragment),Page(target.read_text()).ids,(path,href))

    def test_routes_and_only_ready_links(self):
        source=self.expected[build.TARGET/'index.html']
        self.assertEqual(source.count('class="math-card"'),len(self.items))
        self.assertEqual(source.count('class="math-card pending"'),25-len(self.items))
        for pos,item in enumerate(self.items):
            self.assertEqual(source.count(f'href="ep{item["id"]:02d}.html"'),1)
            html=self.expected[build.TARGET/f'ep{item["id"]:02d}.html']
            nav=re.search(r'<nav class="math-series-nav".*?</nav>',html).group()
            links=re.findall(r'href="([^"]+)"',nav)
            expected=[f'ep{self.items[pos-1]["id"]:02d}.html' if pos else 'index.html',f'ep{self.items[pos+1]["id"]:02d}.html' if pos+1<len(self.items) else 'index.html']
            self.assertEqual(links,expected)

    def test_localized_search_metadata(self):
        with patch.object(search,'collect_pages',return_value=list(self.expected)):
            _,chunks=search.build()
        for item in self.items:
            url=f'essays/math-history/ep{item["id"]:02d}.html'
            for lang,title,deck in [('en',item['title_en'],item['deck_en']),('zh-Hans',item['title_zh'],item['deck_zh']),('zh-Hant',self.c.convert(item['title_zh']),self.c.convert(item['deck_zh']))]:
                record=next(r for r in chunks[lang] if r['u']==url)
                self.assertEqual(record['t'],title)
                self.assertEqual(record['x'],deck)
                self.assertEqual(record['d'],'history')
                self.assertEqual(record['n'],item['id'])
                self.assertIn(build.KEYWORDS[item['id']-1].split()[0].lower(),record['q'].lower())

    def test_traditional_names_and_mathematical_vocabulary(self):
        text=self.c.convert('这里的居里与黎曼，余数与余项，周期。')
        self.assertIn('這裡',text)
        self.assertIn('居里',text)
        self.assertIn('餘數',text)
        self.assertIn('餘項',text)
        self.assertIn('週期',text)
        text=self.c.convert('欧几里得在故事里。傅里叶在论文里证明了，居里在教室里写明了。公里与里程。')
        for phrase in ('歐幾里得','傅里葉','居里','故事裡','論文裡','教室裡','證明了','寫明了','公里','里程'):
            self.assertIn(phrase,text)

    def test_first_essay_evidence_boundaries(self):
        item=next(i for i in self.items if i['id']==1)
        for phrase in ['示意场景','再回到莱因德数学纸草','第二十六或二十七年','手掌宽和手指宽']:
            self.assertIn(phrase,item['body_zh'])
        for phrase in ['illustrative comparison','regnal year 26 or 27','Papyrus Lansing','Returning to the Rhind']:
            self.assertIn(phrase,item['body_en'])

    def test_reader_entry_points(self):
        for filename in ('library.html','explore.html','latest.html'):
            page=Page((build.ROOT/filename).read_text())
            self.assertIn('essays/math-history/index.html',page.links,filename)
        page=Page((build.ROOT/'library.html').read_text())
        self.assertIn('cycles',page.ids)
        ledger=json.loads((build.ROOT/'data/site-updates.json').read_text())
        entry=next(x for x in ledger['updates'] if x['id']=='2026-10-01-mathematics-history')
        self.assertEqual(entry['languages'],['en','zh','zh-hant'])
        self.assertEqual(entry['domain'],'history')

    @unittest.skipUnless(RELEASE,'Use --release after rebuilding all publication artifacts')
    def test_complete_release_indexes(self):
        self.assertEqual([i['id'] for i in self.items],list(range(1,26)))
        expected={'essays/math-history/index.html'}|{f'essays/math-history/ep{i:02d}.html' for i in range(1,26)}
        for lang in ('en','zh-hans','zh-hant','ja','fr','de','es','ko'):
            data=json.loads((build.ROOT/f'data/search/{lang}.json').read_text())
            actual={r['u'] for r in data['records'] if r['u'].startswith('essays/math-history/')}
            self.assertEqual(actual,expected if lang in ('en','zh-hans','zh-hant') else set(),lang)
        urls={n.text for n in ET.parse(build.ROOT/'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        actual={u for u in urls if u.startswith(build.BASE)}
        self.assertEqual(actual,{build.BASE}|{build.BASE+f'ep{i:02d}.html' for i in range(1,26)})
        source=(build.TARGET/'index.html').read_text()
        self.assertNotIn('class="math-card pending"',source)
        self.assertIn('25 complete essays',source)


if __name__=='__main__':unittest.main()
