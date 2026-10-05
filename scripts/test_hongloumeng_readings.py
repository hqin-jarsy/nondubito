#!/usr/bin/env python3
"""Publication checks for the open-ended Red Chamber reader essays."""
import html
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit,unquote
import build_hongloumeng_readings as build
from test_recent_fiction import Page
from build_content_registry import scan_page

class ReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items=build.load_readings();cls.outputs=build.build()

    def test_current_and_full_text(self):
        self.assertEqual(len(self.items),6)
        self.assertEqual(len(self.outputs),18)
        c=build.Converter()
        try:
            for lang,(directory,code,_) in build.EDITIONS.items():
                for item in self.items:
                    path=build.TARGET/directory/(item['slug']+'.html');source=self.outputs[path]
                    self.assertEqual(path.read_text(),source)
                    body=source.split('<div class="reading-prose">')[1].split('<details class="reading-sources">')[0]
                    sections=item['en' if lang=='en' else 'zh']['sections']
                    paragraphs=[p for s in sections for p in s['paragraphs']]
                    self.assertEqual(body.count('<p>'),len(paragraphs))
                    for p in paragraphs:
                        if lang=='zh-hant':p=c.convert(p)
                        self.assertIn(html.escape(p,quote=True),body)
                    self.assertEqual(body.count('<section '),len(sections))
            for item in self.items:
                self.assertEqual(len(item['en']['sections']),len(item['zh']['sections']))
                self.assertGreater(sum(len(p.split()) for s in item['en']['sections'] for p in s['paragraphs']),600)
        finally:c.close()

    def test_html_links_and_metadata(self):
        for path,source in self.outputs.items():
            with self.subTest(page=str(path)):
                page=Page(source);self.assertEqual(page.errors,[])
                self.assertEqual(len(page.ids),len(set(page.ids)))
                self.assertEqual(source.count('<h1>'),1)
                self.assertEqual(len(page.schemas),1)
                schema=page.schemas[0]
                self.assertEqual(schema['@type'],'Article')
                canonical='https://nondubito.net/'+str(path.relative_to(build.ROOT))
                self.assertEqual(schema['url'],canonical)
                self.assertIn(f'rel="canonical" href="{canonical}"',source)
                self.assertTrue(schema['citation'])
                for code in ('en','zh-Hans','zh-Hant','x-default'):
                    self.assertIn(f'hreflang="{code}"',source)
                for href in page.links:
                    u=urlsplit(href)
                    if u.scheme or u.netloc:continue
                    target=(path.parent/unquote(u.path)).resolve() if u.path else path
                    if target.is_dir():target/='index.html'
                    self.assertTrue(target.is_file(),str(target))
                    if u.fragment:self.assertIn(u.fragment,Page(target.read_text()).ids,href)

    def test_sources_spoilers_and_open_sequence(self):
        for lang,(directory,code,_) in build.EDITIONS.items():
            for item in self.items:
                source=self.outputs[build.TARGET/directory/(item['slug']+'.html')]
                self.assertIn('<details class="reading-sources">',source)
                self.assertNotIn('class="reading-sources" open',source)
                self.assertIn('class="reading-scope"',source)
                self.assertIn('class="reading-open"',source)
                for n in item['papers']:self.assertIn(f'sae-hongloumeng-{n}.html',source)
                self.assertNotIn('reading-07.html',source)
                self.assertNotIn('reading-00.html',source)
            last=self.outputs[build.TARGET/directory/'reading-06.html']
            self.assertIn('index.html?lang='+lang+'#readings',last)
            hub=(build.TARGET/directory/'index.html').read_text()
            self.assertEqual(hub.count('class="reading-card"'),len(self.items))
            self.assertIn('id="readings"',hub)
            self.assertIn('sae-hongloumeng-3.html',hub)

    def test_discovery(self):
        ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
        urls={e.text for e in ET.parse(build.ROOT/'sitemap.xml').findall('.//'+ns+'loc')}
        chunks={lang:json.loads((build.ROOT/'data/search'/f'{lang.lower()}.json').read_text())['records'] for lang in ('en','zh-Hans','zh-Hant')}
        for path,source in self.outputs.items():
            page=scan_page(build.ROOT,path)
            self.assertEqual(page['record_type'],'essay')
            self.assertEqual((page['domain'],page['category'],page['series']),('stories','literature','hlm'))
            self.assertEqual(len(page['languages']),1)
            lang=page['languages'][0];url=str(path.relative_to(build.ROOT))
            for key,records in chunks.items():
                self.assertEqual(sum(r['u']==url for r in records),int(key==lang))
            self.assertIn(Page(source).schemas[0]['url'],urls)

    def test_traditional_context_and_continuation_boundary(self):
        c=build.Converter()
        try:
            for s,expected in [('赞美','讚美'),('赞叹','讚嘆'),('赞成','贊成'),('沉默','沉默'),('准许','準許')]:self.assertEqual(c.convert(s),expected)
        finally:c.close()
        # Only the finalized chapter is available; later chapters remain unlinked.
        for directory,_,_ in build.EDITIONS.values():
            source=(build.TARGET/directory/'index.html').read_text()
            fiction=source.split('<section id="continuation">')[1].split('</section>')[0]
            self.assertIn('ch081.html',fiction)
            self.assertNotIn('ch082.html',fiction)

if __name__=='__main__':unittest.main()
