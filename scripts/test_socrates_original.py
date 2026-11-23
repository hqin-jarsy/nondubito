#!/usr/bin/env python3
"""Protect an author's literary text and the narrow publication change."""
import hashlib
import json
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import build_socrates_original as build
from build_content_registry import scan_page
from build_sitemap import parse_page
from web_analytics import Document, issue
from refresh_socrates_original import render as discovery


class Tags(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True);self.items=[];self.paragraphs=[];self.active=False;self.capture=None;self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);self.items.append((tag,a))
        if tag=='article' and 'data-original-manuscript' in a:self.active=True
        if tag=='p' and self.active:self.capture=[]
    def handle_data(self,text):
        if self.capture is not None:self.capture.append(text)
    def handle_endtag(self,tag):
        if tag=='p' and self.capture is not None:self.paragraphs.append(''.join(self.capture));self.capture=None
        if tag=='article':self.active=False


def old(path):
    return subprocess.check_output(['git','show','HEAD:'+path],cwd=build.ROOT)


class OriginalSocrates(unittest.TestCase):
    def test_verbatim_manuscript_and_rendered_paragraphs(self):
        self.assertEqual(hashlib.sha256((build.DATA/'zh.txt').read_bytes()).hexdigest(),build.SOURCE_SHA)
        for lang,(directory,code,_) in build.EDITION.items():
            text=(build.TARGET/directory/'socrates.html').read_text()
            body=Tags(text).paragraphs
            self.assertEqual(body,build.manuscript(lang));self.assertEqual(len(body),66)
            repeated='店内外充满了快活的空气。' if lang=='zh' else '店內外充滿了快活的空氣。'
            self.assertEqual(body.count(repeated),2)
            self.assertEqual(body[-1],'此后便没有人再问了——大约他们的确都知道了。' if lang=='zh' else '此後便沒有人再問了——大約他們的確都知道了。')
            self.assertEqual(len([t for t,a in Tags(text).items if t=='article']),1)

    def test_only_real_editions_and_creative_work_metadata(self):
        for path,text in build.render().items():
            p=Tags(text);is_hant='zh-hant' in path.parts;code='zh-Hant' if is_hant else 'zh-Hans'
            page=scan_page(build.ROOT,path)
            self.assertEqual(page['languages'],[code]);self.assertEqual(page['domain'],'stories')
            self.assertEqual(page['record_type'],'story' if path.name=='socrates.html' else 'series-index')
            self.assertEqual(page['titles'].get(code),'蘇格拉底' if is_hant and path.name=='socrates.html' else '苏格拉底' if path.name=='socrates.html' else '短篇小說' if is_hant else '短篇小说')
            self.assertEqual(issue(Document(text)),None)
            self.assertEqual(len([t for t,a in p.items if t=='header' and a.get('class')=='site-shell-header']),1)
            editions=[a['hreflang'] for t,a in p.items if t=='link' and a.get('rel')=='alternate']
            self.assertEqual(set(editions),{'zh-Hans','zh-Hant'})
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
            self.assertEqual(schema['inLanguage'],code)
            if path.name=='socrates.html':self.assertEqual(schema['@type'],'CreativeWork');self.assertEqual(schema['genre'],'Short fiction')

    def test_links_and_language_pairs(self):
        for path,text in build.render().items():
            self.assertEqual(parse_page(path).canonical,'https://nondubito.net/'+path.relative_to(build.ROOT).as_posix().removesuffix('index.html'))
            for t,a in Tags(text).items:
                raw=a.get('href' if t in ('a','link') else 'src','');u=urlsplit(raw)
                if not raw or u.scheme or u.netloc:continue
                target=build.ROOT/unquote(u.path.lstrip('/')) if u.path.startswith('/') else path.parent/unquote(u.path)
                self.assertTrue(target.is_file(),f'{path}: {raw}')
                if u.fragment:self.assertIn('id="'+u.fragment+'"',target.read_text())

    def test_reproducible_pages_and_discovery(self):
        for path,text in {**build.render(),**build.supporting_pages(),**discovery()}.items():self.assertEqual(path.read_text(),text,str(path))
        for lang in ('zh-hans','zh-hant'):
            records=json.loads((build.ROOT/f'data/search/{lang}.json').read_text())['records']
            for filename in ('index.html','socrates.html'):
                rel='originals/short-stories/'+('zh-hant/' if lang=='zh-hant' else '')+filename
                r=next(x for x in records if x['u']==rel)
                self.assertEqual(r['d'],'stories');self.assertIn('蘇格拉底' if lang=='zh-hant' else '苏格拉底',r['q'])
        english=json.loads((build.ROOT/'data/search/en.json').read_text())['records']
        self.assertFalse(any(r['u'].startswith('originals/short-stories/') for r in english))
        entries={u.find('{*}loc').text:u.find('{*}lastmod').text for u in ET.parse(build.ROOT/'sitemap.xml').getroot()}
        for path in build.render():self.assertEqual(entries[parse_page(path).canonical],build.DATE)

    def test_publication_entrances_and_no_duplicate_cards(self):
        ledger=json.loads((build.ROOT/'data/site-updates.json').read_text())['updates']
        entry=[v for v in ledger if v['id']==build.UPDATE_ID];self.assertEqual(len(entry),1)
        self.assertEqual(entry[0]['languages'],['zh','zh-hant'])
        for name in ('originals/index.html','library.html','latest.html','index.html'):
            needle='short-stories/' if name=='originals/index.html' else 'originals/short-stories/'
            self.assertIn(needle,(build.ROOT/name).read_text())
        hub=(build.ROOT/'originals/index.html').read_text()
        self.assertEqual(hub.count('data-search="Socrates 苏格拉底 蘇格拉底 short fiction"'),3)
        library=(build.ROOT/'library.html').read_text()
        self.assertEqual(library.count('<!-- SHORT FICTION LIBRARY START -->'),1)
        self.assertEqual(library.count('href="originals/short-stories/index.html"'),1)

    def test_unrelated_books_search_and_dates_preserved(self):
        changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=build.ROOT,text=True).splitlines()
        self.assertFalse(any(p.startswith(('originals/short-science-fiction/','originals/hongloumeng/')) for p in changed))
        scope={'originals/index.html','library.html','index.html',*(p.relative_to(build.ROOT).as_posix() for p in build.render())}
        for path in (build.ROOT/'data/search').glob('*.json'):
            before=json.loads(old(path.relative_to(build.ROOT).as_posix()))['records'];after=json.loads(path.read_text())['records']
            self.assertEqual({v['u']:v for v in before if v['u'] not in scope},{v['u']:v for v in after if v['u'] not in scope})
        def dates(text):return {v.find('{*}loc').text:v.find('{*}lastmod').text for v in ET.fromstring(text)}
        before=dates(old('sitemap.xml'));after=dates((build.ROOT/'sitemap.xml').read_text())
        allowed={parse_page(p).canonical for p in build.render()}|{'https://nondubito.net/','https://nondubito.net/originals/','https://nondubito.net/library.html','https://nondubito.net/latest.html'}
        self.assertTrue(before.keys()<=after.keys())
        self.assertTrue(all(after[u]==d for u,d in before.items() if u not in allowed))

if __name__=='__main__':unittest.main(verbosity=2)
