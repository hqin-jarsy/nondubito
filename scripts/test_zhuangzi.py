#!/usr/bin/env python3
"""Structural/editorial regression guards; not a substitute for reading review."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit, unquote
import build_zhuangzi as b
from build_content_registry import scan_page

class Page(HTMLParser):
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self,text):
        super().__init__();self.stack=[];self.ids=set();self.links=[];self.headers=0;self.articles=[]
        self.feed(text); self.close()
        assert not self.stack, self.stack
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:
            assert d['id'] not in self.ids, d['id']
            self.ids.add(d['id'])
        if 'href' in d:self.links.append(d['href'])
        if tag=='header':self.headers+=1
        if tag=='article':self.articles.append(d)
        if tag not in self.VOID:self.stack.append(tag)
    def handle_endtag(self,tag):
        assert self.stack and self.stack[-1]==tag,(self.stack[-5:],tag)
        self.stack.pop()
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in self.VOID:self.handle_endtag(tag)

class ZhuangziTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((b.DATA/'manifest.json').read_text())
        cls.pages={p.name:p.read_text() for p in b.TARGET.glob('*.html')}
    def test_inventory(self):
        self.assertEqual([x['number'] for x in self.m['items']],list(range(68)))
        self.assertEqual(len({x['source_file'] for x in self.m['items']}),68)
        for x in self.m['items']:
            self.assertRegex(x['source_sha256'],r'^[0-9a-f]{64}$')
            for k in ('en_title','zh_title','hant_title'):self.assertTrue(x[k])
    def test_groups(self):
        self.assertEqual({x['number'] for x in self.m['items'] if x['group']=='inner'},set(range(11,30)))
        self.assertEqual({x['number'] for x in self.m['items'] if x['group']=='discernment'},set(range(30,42))|set(range(59,66)))
        self.assertEqual({x['number'] for x in self.m['items'] if x['group']=='outer'},set(range(42,59)))
    def test_only_edited_pages(self):
        self.assertEqual(self.m['published'],list(range(26)))
        self.assertEqual(set(self.pages),{'index.html','guide.html'}|{f'{n:02d}.html' for n in range(1,26)})
    def test_all_reading_editions_exist(self):
        for n in self.m['published']:
            for lang in b.LANGS:
                raw=(b.DATA/lang/f'{n:02d}.md').read_text()
                self.assertGreater(len(raw),1000 if n==0 else 2500)
                self.assertNotIn('见置顶',raw)
                self.assertNotIn('TODO',raw)
                self.assertNotIn('**',raw)
            en=(b.DATA/'en'/f'{n:02d}.md').read_text()
            self.assertGreater(len(en.split()),700 if n==0 else 1200)
    def test_traditional_complete_sections(self):
        for n in self.m['published']:
            zh=(b.DATA/'zh'/f'{n:02d}.md').read_text()
            tc=(b.DATA/'zh-hant'/f'{n:02d}.md').read_text()
            self.assertEqual(zh.count('\n## '),tc.count('\n## '))
            self.assertEqual(len(zh.split('\n\n')),len(tc.split('\n\n')))
    def test_traditional_context(self):
        tc='\n'.join((b.DATA/'zh-hant'/f'{n:02d}.md').read_text() for n in self.m['published'])
        for error in ('余項','捨者','客捨','九萬裡','瞭望洋','這麼乾','找准','拿不准','瞄准','稱贊','需要松開'):
            self.assertNotIn(error,tc)
        self.assertIn('舍者與之爭席',tc)
    def test_markup_and_language_bodies(self):
        for name,text in self.pages.items():
            page=Page(text)
            self.assertEqual(page.headers,1) # No content <header> inheriting the global fixed header.
            if name!='index.html':
                self.assertEqual({x['lang'] for x in page.articles},{'en','zh-Hans','zh-Hant'})
            self.assertIn('site-shell-language',text)
            self.assertIn('explicit-hant',text)
            self.assertNotIn('<p>---</p>',text)
    def test_local_links_and_fragments(self):
        for name,text in self.pages.items():
            for href in Page(text).links:
                u=urlsplit(href)
                if u.scheme or u.netloc:continue
                target=(b.TARGET/name).parent/unquote(u.path) if u.path else b.TARGET/name
                if target.is_dir():target=target/'index.html'
                self.assertTrue(target.is_file(),(name,href))
                if u.fragment and target.suffix=='.html':
                    self.assertIn(u.fragment,Page(target.read_text()).ids,(name,href))
    def test_pending_not_empty_links(self):
        links=Page(self.pages['index.html']).links
        for n in range(26,68):self.assertNotIn(f'{n:02d}.html',links)
        self.assertEqual(self.pages['index.html'].count('class="zz-pending"'),84)
        self.assertIn('25/67',self.pages['index.html'])
    def test_first_group_complete_and_navigation(self):
        self.assertEqual({x['number'] for x in self.m['items'] if x['group']=='encounters'},set(range(1,11)))
        for n in range(26):
            links=Page(self.pages[b.filename(n)]).links
            if n: self.assertIn(b.filename(n-1),links)
            if n<25: self.assertIn(b.filename(n+1),links)
            else: self.assertIn('index.html#contents',links)
    def test_publication_dates(self):
        for name,text in self.pages.items():
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
            new=name in {f'{n:02d}.html' for n in range(6,26)}
            self.assertEqual(schema['datePublished'],'2026-09-21' if new else '2026-09-20')
            self.assertEqual(schema['dateModified'],'2026-09-21' if new or name=='index.html' else '2026-09-20')
    def test_second_batch_editorial_boundaries(self):
        for n,zh_marker,en_marker in (
            (6,'不是一份实验报告','should not turn this into a controlled experiment'),
            (7,'任何沉默都能直接判为共谋','Not every silence is complicity'),
            (8,'不能证明他内心毫无怀疑','cannot prove he had no doubts'),
            (9,'优先招待','preferential service'),
            (10,'不是已经核实的病榻记录','not a verified transcript'),
        ):
            self.assertIn(zh_marker,(b.DATA/'zh'/f'{n:02d}.md').read_text())
            self.assertIn(en_marker,(b.DATA/'en'/f'{n:02d}.md').read_text())
        for n in range(1,11):self.assertIn(n,b.CHAPTERS)
    def test_third_batch_editorial_boundaries(self):
        for n,zh_marker,en_marker in (
            (11,'不是已经证实的古代课程表','not an established ancient syllabus'),
            (12,'准备与闲着从外面绝对分不出来','Grain can be counted'),
            (13,'这段原文没有写八百','does not give that number'),
            (14,'能不龟手，一也','preparation that prevents hands from cracking'),
            (15,'夫言非吹也，言者有言','Sincerity does not guarantee accuracy'),
        ):
            self.assertIn(zh_marker,(b.DATA/'zh'/f'{n:02d}.md').read_text())
            self.assertIn(en_marker,(b.DATA/'en'/f'{n:02d}.md').read_text())
        for n in range(11,16):
            self.assertIn(n,b.CHAPTERS)
            tc=(b.DATA/'zh-hant'/f'{n:02d}.md').read_text()
            for error in ('逍遙游','千裡','百裡','幾案','贊嘆','這周','賬單'):
                self.assertNotIn(error,tc)
        self.assertIn('古代课程安排',self.pages['11.html'])
        self.assertIn('essays 11–25 available',self.pages['index.html'])
        self.assertIn('href="11.html"',self.pages['index.html'])
    def test_fourth_batch_editorial_boundaries(self):
        for n,zh_marker,en_marker in (
            (16,'是以圣人和之以是非而休乎天均','timing, risk, or distribution'),
            (17,'这段文学没有给出那样的证明','no reserved seat outside the problem'),
            (18,'郭象把它读作野外之雉自得','Guo Xiang reads the closing words'),
            (19,'三声不是新定额','Three cries are not a new quota'),
            (20,'上司不是君王','A manager is not a sovereign'),
        ):
            self.assertIn(zh_marker,(b.DATA/'zh'/f'{n:02d}.md').read_text())
            self.assertIn(en_marker,(b.DATA/'en'/f'{n:02d}.md').read_text())
            self.assertIn(n,b.CHAPTERS)
            tc=(b.DATA/'zh-hant'/f'{n:02d}.md').read_text()
            for error in ('賬','松一口氣','松開','寬松','松下來','證明瞭','身份','下周','回復'):
                self.assertNotIn(error,tc)
        self.assertIn('保身、全生、尽年',(b.DATA/'zh/19.md').read_text())
        self.assertIn('无迁令，无劝成',(b.DATA/'zh/20.md').read_text())
        self.assertIn('does not report that the mission succeeds',(b.DATA/'en/20.md').read_text())
        for name in ('18.html','19.html'):
            self.assertIn('www.chineseclassic.com/content/445',self.pages[name])
    def test_fifth_batch_editorial_boundaries(self):
        for n,zh_marker,en_marker in (
            (21,'并不是三轮献策','three elements in this second proposal'),
            (22,'不能做事也不意味着一个人失去作为人的资格','Being unable to work does not remove'),
            (23,'他明确说过自己怒','Jia explicitly acknowledges anger'),
            (24,'吾与孔丘，非君臣也，德友而已矣','not as ruler and subject'),
            (25,'不是一套经过检验、对谁都适用的训练周期','numbers are not a validated curriculum'),
        ):
            self.assertIn(zh_marker,(b.DATA/'zh'/f'{n:02d}.md').read_text())
            self.assertIn(en_marker,(b.DATA/'en'/f'{n:02d}.md').read_text())
            self.assertIn(n,b.CHAPTERS)
            tc=(b.DATA/'zh-hant'/f'{n:02d}.md').read_text()
            for error in ('賬','松下來','階梯松','身份','會沈','繇役','贊嘆','贊美','竪起','咨詢','扎實'):
                self.assertNotIn(error,tc)
        self.assertIn('子产回击了',(b.DATA/'zh/23.md').read_text())
        self.assertIn('子無乃稱',(b.DATA/'zh-hant/23.md').read_text())
        self.assertIn('和而不唱',(b.DATA/'zh/24.md').read_text())
        self.assertIn('We are not told why Ai Taituo goes',(b.DATA/'en/24.md').read_text())
        self.assertIn('www.chineseclassic.com/content/446',self.pages['22.html'])
        self.assertNotIn('三套方案',self.m['items'][21]['zh_title'])
        self.assertNotIn('也不说话',self.m['items'][24]['zh_title'])
    def test_canonicals_and_schema(self):
        for name,text in self.pages.items():
            url='https://nondubito.net/essays/zhuangzi/'+('' if name=='index.html' else name)
            self.assertEqual(re.findall(r'<link rel="canonical" href="([^"]+)"',text),[url])
            schemas=re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)
            self.assertEqual(len(schemas),1)
            self.assertEqual(json.loads(schemas[0])['url'],url)
    def test_critical_editorial_distinctions(self):
        allzh='\n'.join((b.DATA/'zh'/f'{n:02d}.md').read_text() for n in self.m['published'])
        for old in ('第一窍凿完，浑沌能看见了','规格越高，死得越快','难堪是入场券','一个留了半分力的人','仿不到的是话到嘴边收住'):
            self.assertNotIn(old,allzh)
        self.assertIn('不是作者身份的印章',allzh)
        self.assertIn('不是在要求无条件受训',allzh)
        self.assertIn('不是现实中可以照做的安全保证',allzh)
    def test_search_metadata(self):
        for name in self.pages:
            record=scan_page(b.ROOT,b.TARGET/name)
            self.assertEqual(record['domain'],'stories')
            self.assertEqual(set(record['languages']),{'en','zh-Hans','zh-Hant'})
            self.assertTrue(record['titles']['en'])
            self.assertTrue(record['titles']['zh-Hans'])
            self.assertTrue(record['titles']['zh-Hant'])
    def test_source_originals_unchanged_if_available(self):
        folder=Path('/Users/hanqin/Documents/大知解庄子')
        if not folder.exists():self.skipTest('Original private folder not present')
        for x in self.m['items']:
            self.assertEqual(hashlib.sha256((folder/x['source_file']).read_bytes()).hexdigest(),x['source_sha256'])
    def test_reader_entrypoints(self):
        for name in ('library.html','explore.html','latest.html'):
            self.assertIn('essays/zhuangzi/index.html',(b.ROOT/name).read_text())

if __name__=='__main__':unittest.main()
