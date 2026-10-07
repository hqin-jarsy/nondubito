#!/usr/bin/env python3
import hashlib
import html
import json
import re
import subprocess
import unittest
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import build_film_full_editions as b

class Nodes(HTMLParser):
    def __init__(self):super().__init__();self.nodes=[];self.depth=0;self.body=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);self.nodes.append((tag,a))
        if tag=='div':
            if self.depth:self.depth+=1
            elif 'essay-body' in a.get('class','').split():self.depth=1
    def handle_endtag(self,tag):
        if tag=='div' and self.depth:self.depth-=1
    def handle_data(self,s):
        if self.depth:self.body.append(s)

class Films(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages=b.outputs();cls.receipt=json.loads((b.DATA/'batch01-received.json').read_text())
    def test_reproducible_and_local_links(self):
        for p,s in self.pages.items():
            self.assertEqual(p.read_text(),s,p)
            parser=Nodes();parser.feed(s);ids={a['id'] for _,a in parser.nodes if 'id' in a}
            for tag,a in parser.nodes:
                if tag not in ('a','link','script'):continue
                href=a.get('href',a.get('src',''));u=urlsplit(html.unescape(href))
                if not href or u.scheme:continue
                target=(p.parent/unquote(u.path)).resolve() if u.path else p
                self.assertTrue(target.exists(),(p,href))
                if not u.path and u.fragment:self.assertIn(unquote(u.fragment),ids,(p,href))
    def test_sources_and_legacy_bodies(self):
        for name,r in self.receipt['files'].items():
            self.assertEqual(hashlib.sha256((b.DATA/name).read_bytes()).hexdigest(),r['sha256'],name)
        for name,digest in self.receipt['protected'].items():
            p=b.ROOT/name
            if p.suffix=='.js':self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),digest,name)
            elif p.suffix=='.html':
                old=subprocess.check_output(['git','show',self.receipt['baseline_commit']+':'+name],cwd=b.ROOT).decode()
                x=Nodes();x.feed(old);y=Nodes();y.feed(p.read_text());self.assertEqual(x.body,y.body,name)
    def test_full_editions_and_seo(self):
        fresh=[(p,s) for p,s in self.pages.items() if p.parent.name in b.LANGS]
        self.assertEqual(len(fresh),105)
        for p,s in fresh:
            self.assertEqual(len(re.findall('<h1[ >]',s)),1,p)
            self.assertEqual(len(re.findall('hreflang=',s)),6,p)
            self.assertNotIn('.md)',s,p)
            self.assertNotIn('href="EP',s,p)
            self.assertEqual(s.count('class="lang-btn'),8,p)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)[1])
            self.assertEqual(schema['inLanguage'],p.parent.name)
        for film in b.FILMS:
            for lang in b.LANGS:
                for ep,slug in enumerate(film['chapters'],1):
                    s=(b.DATA/'reviewed'/film['slug']/lang/f'EP{ep:02}.md').read_text()
                    page=self.pages[b.ROOT/'essays/film'/film['slug']/lang/(slug+'.html')]
                    expected=len(re.findall(r'^## ',s,re.M))
                    self.assertEqual(page.count('<h2'),expected,(film['slug'],lang,ep))
                    self.assertGreater(len(b.plain(b.split_copy(film,lang,ep)['body'])),len(b.plain(s))*.85)

if __name__=='__main__':unittest.main()
