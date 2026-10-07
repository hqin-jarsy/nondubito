#!/usr/bin/env python3
import html
import json
import re
import unittest
from urllib.parse import urlsplit,unquote
import build_hongloumeng_original as build
import build_search_index as search

class OriginalTests(unittest.TestCase):
    def test_final_manuscript_and_generated_pages(self):
        for p,s in build.render().items():
            self.assertEqual(p.read_text(),s)
            if p.stem in build.CHAPTERS:
                lines=build.manuscript(p.stem)
                actual=[(int(n),html.unescape(v)) for n,v in re.findall(r'<p data-source-line="(\d+)">(.*?)</p>',s)]
                self.assertEqual([n for n,v in actual],[i for i,v in enumerate(lines,1) if i>1 and v])
                self.assertEqual(len(re.findall('data-source-line=',s.split('<div class="verse">')[1].split('</div>')[0])),8 if p.stem=='ch081' else 2)
                if p.parent==build.TARGET:
                    self.assertEqual(actual,[(i,v) for i,v in enumerate(lines,1) if i>1 and v])
                    self.assertEqual(html.unescape(re.sub('<[^>]+>','',re.search('<h1>(.*?)</h1>',s)[1])),lines[0])
                elif p.stem=='ch081':
                    for good in ('城東二十里','一干人','對不準針眼','我繫了送給'):self.assertIn(good,s)
                    for bad in ('城東二十裡','一乾人','對不准針眼'):self.assertNotIn(bad,s)
                else:
                    for good in ('腰繫青絲','繫一條淡','帕子鬆了','拿不準','參鬚'):self.assertIn(good,s)

    def test_navigation_and_metadata(self):
        for p,s in build.render().items():
            for href in re.findall(r'href="([^"]+)"',s):
                u=urlsplit(html.unescape(href))
                if u.scheme or not u.path:continue
                self.assertTrue((p.parent/unquote(u.path)).resolve().exists(),href)
            self.assertNotIn('ch083.html',s)
            self.assertNotIn('hreflang="en"',s)
            self.assertIn('不是曹雪芹',s)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s)[1])
            self.assertEqual(schema['@type'],'Chapter' if p.stem in build.CHAPTERS else 'CollectionPage')
            self.assertEqual(schema['inLanguage'],'zh-Hant' if p.parent.name=='zh-hant' else 'zh-Hans')
            if p.stem in build.CHAPTERS:
                self.assertEqual(schema['datePublished'],build.CHAPTERS[p.stem]['published'])
                nav=s.split('<nav class="chapter-nav"')[1].split('</nav>')[0]
                self.assertIn('ch082.html' if p.stem=='ch081' else 'ch081.html',nav)
            else:
                self.assertEqual(len(schema['hasPart']),2)

    def test_discovery(self):
        for lang,d in [('zh-hans',''),('zh-hant','zh-hant/')]:
            records=json.loads((search.CHUNKS_DIR/f'{lang}.json').read_text())['records']
            for name in ('index.html','ch081.html','ch082.html'):
                url=f'originals/hongloumeng/{d}{name}'
                self.assertEqual(sum(r['u']==url for r in records),1,url)
        en=json.loads((search.CHUNKS_DIR/'en.json').read_text())['records']
        self.assertFalse(any(r['u'].startswith('originals/hongloumeng/') for r in en))

if __name__=='__main__':unittest.main()
