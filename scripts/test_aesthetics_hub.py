#!/usr/bin/env python3
"""Check editions, archive completeness, honest status labels and local links."""
import json
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import re
import unittest
import build_aesthetics_hub as build
from build_content_registry import scan_page

class Page(HTMLParser):
    def __init__(self,s):
        super().__init__();self.tags=[];self.feed(s)
    def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))

class HubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.pages=build.render_pages()

    def test_generated_and_metadata(self):
        self.assertEqual(len(self.pages),6)
        for path,s in self.pages.items():
            with self.subTest(path=path):
                self.assertEqual(path.read_text(),s)
                tags=Page(s).tags
                self.assertEqual(sum(t=='h1' for t,a in tags),1)
                ids=[a['id'] for t,a in tags if 'id' in a]
                self.assertEqual(len(ids),len(set(ids)))
                lang='zh-Hant' if path.parent.name=='zh-hant' else 'en' if path.parent.name=='en' else 'zh-Hans'
                record=scan_page(build.ROOT,path)
                self.assertEqual(record['languages'],[lang])
                self.assertEqual(record['domain'],'sae-philosophy')
                expected=build.ORIGIN+path.relative_to(build.ROOT).as_posix().removesuffix('index.html')
                self.assertEqual([a['href'] for t,a in tags if t=='link' and a.get('rel')=='canonical'],[expected])
                self.assertEqual({a.get('hreflang') for t,a in tags if t=='link' and a.get('rel')=='alternate'},{'en','zh-Hans','zh-Hant'})
                schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)[1])
                self.assertEqual(schema['inLanguage'],lang)
                self.assertEqual(schema['@type'],'CollectionPage' if path.name=='index.html' else 'Article')
                if lang=='zh-Hant':
                    for wrong in ['“','”','那只已經','這只杯子','贊美']:self.assertNotIn(wrong,s)

    def test_links(self):
        for path,s in self.pages.items():
            for tag,a in Page(s).tags:
                raw=a.get('href') or a.get('src')
                if not raw:continue
                url=urlsplit(raw)
                if url.scheme or url.netloc:continue
                target=(path.parent/unquote(url.path)).resolve() if url.path else path
                self.assertTrue(target.is_file(),(path,raw))
                if url.fragment and target.suffix=='.html':
                    ids={a['id'] for t,a in Page(target.read_text()).tags if 'id' in a}
                    self.assertIn(unquote(url.fragment),ids,(path,raw))

    def test_archive_and_status(self):
        entries=json.loads((build.TARGET/'log.json').read_text())['entries']
        for path,s in self.pages.items():
            if path.name!='index.html':continue
            tags=Page(s).tags
            daily=[a['href'] for t,a in tags if t=='a' and re.search(r'\d{4}-\d\d-\d\d.html',a.get('href',''))]
            self.assertEqual(len(daily),len(entries)+6)
            self.assertEqual({urlsplit(x).path.split('/')[-1] for x in daily},{e['slug']+'.html' for e in entries})
            self.assertEqual(sum('sae-aesthetics-ray-' in a.get('href','') for t,a in tags),13)
            self.assertNotIn('它不活',s)
            self.assertNotIn('it is no longer alive',s)
            self.assertTrue('still to come' in s or '本批上线' in s or '本批上線' in s)
            self.assertIn('artist_dead.html',s)

    def test_discovery(self):
        for name in ['index.html','library.html','explore.html','latest.html']:
            self.assertIn('essays/aesthetics/index.html',(build.ROOT/name).read_text())
        updates=json.loads((build.ROOT/'data/site-updates.json').read_text())['updates']
        item=next(x for x in updates if x['id']=='2026-09-28-aesthetics-hub')
        self.assertEqual(set(item['languages']),{'en','zh','zh-hant'})

    def test_search_sitemap(self):
        for lang,sub in [('zh-hans',''),('en','en/'),('zh-hant','zh-hant/')]:
            records=json.loads((build.ROOT/f'data/search/{lang}.json').read_text())['records']
            urls={r['u'] for r in records}
            for f in ['index.html','seeing-beauty.html']:
                self.assertIn('essays/aesthetics/'+sub+f,urls)
        sitemap=(build.ROOT/'sitemap.xml').read_text()
        for p in self.pages:
            self.assertIn(build.ORIGIN+p.relative_to(build.ROOT).as_posix().removesuffix('index.html'),sitemap)

if __name__=='__main__':unittest.main()
