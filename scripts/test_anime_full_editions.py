#!/usr/bin/env python3
import hashlib
import html
import json
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import build_anime_full_editions as b

class Nodes(HTMLParser):
    def __init__(self): super().__init__(); self.nodes=[]
    def handle_starttag(self,t,a): self.nodes.append((t,dict(a)))

class Anime(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.pages=b.outputs()
    def test_preserved_sources_and_original_editions(self):
        for name,digest in b.RECEIPT['files'].items():
            self.assertEqual(hashlib.sha256((b.DATA/name).read_bytes()).hexdigest(),digest,name)
        for name,digest in b.RECEIPT['protected'].items():
            p=b.ROOT/name
            if b.BATCH=='02' and p in self.pages:
                series=next(f for f in b.SERIES if name.startswith(f['route']+'/'))
                old=(b.DATA/'templates'/series['slug']/p.name).read_text()
                self.assertEqual(hashlib.sha256(old.encode()).hexdigest(),digest,name)
                def normalize(s):
                    s=re.sub(r'<!-- anime-full-head -->.*?<!-- /anime-full-head -->','',s,flags=re.S)
                    return re.sub(r'<div class="lang-toggle"[^>]*>.*?</div>','',s,count=1,flags=re.S)
                self.assertEqual(normalize(old),normalize(p.read_text()),name)
            else:self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),digest,name)
    def test_generated_pages_and_links(self):
        self.assertEqual(len(self.pages),180 if b.BATCH=='02' else 145)
        for p,s in self.pages.items():
            self.assertEqual(p.read_text(),s,p)
            parser=Nodes();parser.feed(s)
            for tag,a in parser.nodes:
                if tag not in ('a','link','script'): continue
                value=a.get('href',a.get('src',''));u=urlsplit(html.unescape(value))
                if not value or u.scheme or not u.path: continue
                target=(p.parent/unquote(u.path)).resolve()
                self.assertTrue(target.exists(),(p,value))
            if p.parent.name not in b.LANGS:continue
            self.assertEqual(len(re.findall('<h1[ >]',s)),1,p)
            self.assertEqual(s.count('hreflang='),6,p)
            self.assertNotRegex(s,r'href="[^"]+\.md(?:["#])',p)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)[1])
            self.assertEqual(schema['inLanguage'],p.parent.name)
    def test_complete_bodies_and_navigation(self):
        for series in b.SERIES:
            for lang in b.LANGS:
                index=self.pages[b.ROOT/series['route']/lang/'index.html']
                for ep,name in enumerate(series['chapters'],1):
                    source=b.source(series,lang,ep).read_text()
                    copy=b.copy(series,lang,ep)
                    self.assertEqual(copy['body'].count('<h2'),len(re.findall(r'^## ',source,re.M)))
                    self.assertGreater(len(b.plain(copy['body'])),len(b.plain(source))*.80,(series['slug'],lang,ep))
                    self.assertIn('href="'+name+'.html"',index)
                    self.assertIn(b.E(copy['title']),index)
    def test_editorial_changes(self):
        changes=json.loads((b.DATA/f'batch{b.BATCH}-corrections.json').read_text())['changes']
        for c in changes:
            s=(b.ROOT/c['path']).read_text()
            self.assertIn(c['after'],s,c['path']);self.assertNotIn(c['before'],s,c['path'])
    def test_discovery(self):
        import xml.etree.ElementTree as ET
        ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
        urls=[u.find(ns+'loc').text for u in ET.parse(b.ROOT/'sitemap.xml').getroot()]
        self.assertEqual(len(urls),len(set(urls)))
        for lang in b.LANGS:
            records=json.loads((b.ROOT/'data/search'/f'{lang}.json').read_text())['records']
            routes=[r['u'] for r in records]
            self.assertEqual(len(routes),len(set(routes)))
            for series in b.SERIES:
                for name in ['index',*series['chapters']]:
                    route=f'{series["route"]}/{lang}/{name}.html'
                    self.assertIn(route,routes)
                    canonical='https://nondubito.net/'+(route[:-10] if name=='index' else route)
                    self.assertIn(canonical,urls)

if __name__=='__main__': unittest.main()
