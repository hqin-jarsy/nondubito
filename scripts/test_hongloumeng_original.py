#!/usr/bin/env python3
import hashlib
import html
import json
import re
import unittest
from urllib.parse import urlsplit,unquote
import build_hongloumeng_original as build
import build_search_index as search

class OriginalTests(unittest.TestCase):
    def test_final_manuscript_and_generated_pages(self):
        self.assertEqual(hashlib.sha256(build.SOURCE.read_bytes()).hexdigest(),build.SHA256)
        lines=build.SOURCE.read_text().splitlines()
        for p,s in build.render().items():
            self.assertEqual(p.read_text(),s)
            if p.name=='ch081.html':
                actual=[(int(n),html.unescape(v)) for n,v in re.findall(r'<p data-source-line="(\d+)">(.*?)</p>',s)]
                self.assertEqual([n for n,v in actual],[i for i,v in enumerate(lines,1) if i>1 and v])
                self.assertEqual(len(re.findall('data-source-line=',s.split('<div class="verse">')[1].split('</div>')[0])),8)
                if p.parent==build.TARGET:
                    self.assertEqual(actual,[(i,v) for i,v in enumerate(lines,1) if i>1 and v])
                    self.assertEqual(html.unescape(re.sub('<[^>]+>','',re.search('<h1>(.*?)</h1>',s)[1])),lines[0])
                else:
                    for good in ('城東二十里','一干人','對不準針眼','我繫了送給'):self.assertIn(good,s)
                    for bad in ('城東二十裡','一乾人','對不准針眼'):self.assertNotIn(bad,s)

    def test_navigation_and_metadata(self):
        for p,s in build.render().items():
            for href in re.findall(r'href="([^"]+)"',s):
                u=urlsplit(html.unescape(href))
                if u.scheme or not u.path:continue
                self.assertTrue((p.parent/unquote(u.path)).resolve().exists(),href)
            self.assertNotIn('ch082.html',s)
            self.assertNotIn('hreflang="en"',s)
            self.assertIn('不是曹雪芹',s)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s)[1])
            self.assertEqual(schema['@type'],'Chapter' if p.name=='ch081.html' else 'CollectionPage')
            self.assertEqual(schema['inLanguage'],'zh-Hant' if p.parent.name=='zh-hant' else 'zh-Hans')

    def test_discovery(self):
        for lang,d in [('zh-hans',''),('zh-hant','zh-hant/')]:
            records=json.loads((search.CHUNKS_DIR/f'{lang}.json').read_text())['records']
            for name in ('index.html','ch081.html'):
                url=f'originals/hongloumeng/{d}{name}'
                self.assertEqual(sum(r['u']==url for r in records),1,url)
        en=json.loads((search.CHUNKS_DIR/'en.json').read_text())['records']
        self.assertFalse(any(r['u'].startswith('originals/hongloumeng/') for r in en))

if __name__=='__main__':unittest.main()
