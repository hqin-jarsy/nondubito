#!/usr/bin/env python3
"""Check editions, archive completeness, honest status labels and local links."""
import json
import html
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
    def setUpClass(cls):
        cls.pages=build.render_pages()
        cls.rays=json.loads((build.DATA/'rays.json').read_text())

    def test_generated_and_metadata(self):
        self.assertEqual(len(self.pages),3*(2+len(self.rays)))
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
                if path.stem.startswith('ray'):
                    n=int(path.stem[3:])
                    self.assertEqual(schema['citation'],build.PAPERS+f'sae-aesthetics-ray-{n}.html')
                    self.assertEqual(schema['datePublished'],self.rays[n-1]['date'])
                if lang=='zh-Hant':
                    for wrong in ['“','”','那只已經','這只杯子','贊美','沈默','松口氣','余一']:self.assertNotIn(wrong,s)
                    for wrong in ['公裡','算不准','證明瞭','生命奇跡','冷冰冰的重復']:self.assertNotIn(wrong,s)

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
            count=len(self.rays)
            self.assertTrue(f'{count} of 13' in s or f'{count} / 13' in s)
            if count<13:self.assertTrue(any(f'{prefix} {13-count}' in s for prefix in ['remaining','其余','其餘']))
            self.assertEqual(sum(a.get('class')=='ray-card' for t,a in tags),count)
            for n in range(count+1,14):self.assertNotRegex(s,rf'href="[^"]*ray{n:02d}\.html')
            self.assertIn('artist_dead.html',s)

    def test_discovery(self):
        for name in ['index.html','library.html','explore.html','latest.html']:
            self.assertIn('essays/aesthetics/index.html',(build.ROOT/name).read_text())
        updates=json.loads((build.ROOT/'data/site-updates.json').read_text())['updates']
        item=next(x for x in updates if x['id']=='2026-09-28-aesthetics-hub')
        self.assertEqual(set(item['languages']),{'en','zh','zh-hant'})
        self.assertEqual(updates[0]['id'],'2026-09-28-aesthetics-rays-04-07')

    def test_search_sitemap(self):
        for lang,sub in [('zh-hans',''),('en','en/'),('zh-hant','zh-hant/')]:
            records=json.loads((build.ROOT/f'data/search/{lang}.json').read_text())['records']
            urls={r['u'] for r in records}
            for f in ['index.html','seeing-beauty.html']+[r['slug']+'.html' for r in self.rays]:
                self.assertIn('essays/aesthetics/'+sub+f,urls)
        sitemap=(build.ROOT/'sitemap.xml').read_text()
        for p in self.pages:
            self.assertIn(build.ORIGIN+p.relative_to(build.ROOT).as_posix().removesuffix('index.html'),sitemap)

    def test_complete_manuscripts_and_navigation(self):
        for path,s in self.pages.items():
            if not path.stem.startswith('ray'):continue
            n=int(path.stem[3:]);lang='en' if path.parent.name=='en' else 'zh'
            source=(build.DATA/f'{path.stem}-{lang}.md').read_text().strip()
            article=re.search(r'<article class="prose">(.*?)</article>',s,re.S)[1]
            rendered=re.findall(r'<(?:p|h2)[^>]*>(.*?)</(?:p|h2)>',article,re.S)
            blocks=source.split('\n\n')
            self.assertEqual(len(blocks),len(rendered))
            if path.parent.name!='zh-hant':
                self.assertEqual([html.unescape(x) for x in rendered],[x.removeprefix('## ') for x in blocks])
            self.assertEqual(len(re.findall(r'<h2 ',article)),source.count('## '))
            if lang=='en':self.assertGreater(len(source.split()),1100)
            else:self.assertGreater(len(re.findall(r'[\u3400-\u9fff]',source)),1700)
            current='zh-hant' if path.parent.name=='zh-hant' else lang
            chapter=re.search(r'<nav class="chapter-links"[^>]*>(.*?)</nav>',s,re.S)[1]
            expected_prev=f'ray{n-1:02d}.html' if n>1 else 'seeing-beauty.html'
            expected_next=f'ray{n+1:02d}.html?lang={current}' if n<len(self.rays) else f'index.html?lang={current}#rays'
            self.assertIn(f'href="{expected_prev}?lang={current}"',chapter)
            self.assertIn(f'href="{expected_next}"',chapter)
            self.assertNotRegex(article,r'\b(?:13|14|15|16)DD\b')
            for ref in self.rays[n-1].get('references',[]):self.assertIn(html.escape(ref['url'],quote=True),s)

    def test_arithmetic_and_traditional_fixes(self):
        self.assertEqual(sum(range(1,101)),50*101)
        self.assertEqual(sum(range(1,10)),9*10//2)
        self.assertEqual(2*3*5*7*11*13+1,59*509)
        self.assertIn('都會餘一',self.pages[build.TARGET/'zh-hant/ray03.html'])
        self.assertIn('沉默',self.pages[build.TARGET/'zh-hant/ray02.html'])
        self.assertIn('鬆口氣',self.pages[build.TARGET/'zh-hant/ray02.html'])

if __name__=='__main__':unittest.main()
