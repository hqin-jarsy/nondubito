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
        self.assertEqual(self.m['published'],list(range(51)))
        self.assertEqual(set(self.pages),{'index.html','guide.html'}|{f'{n:02d}.html' for n in range(1,51)})
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
        for n in range(51,68):self.assertNotIn(f'{n:02d}.html',links)
        self.assertEqual(self.pages['index.html'].count('class="zz-pending"'),34)
        self.assertIn('50/67',self.pages['index.html'])
    def test_first_group_complete_and_navigation(self):
        self.assertEqual({x['number'] for x in self.m['items'] if x['group']=='encounters'},set(range(1,11)))
        for n in range(51):
            links=Page(self.pages[b.filename(n)]).links
            if n: self.assertIn(b.filename(n-1),links)
            if n<50: self.assertIn(b.filename(n+1),links)
            else: self.assertIn('index.html#contents',links)
    def test_publication_dates(self):
        for name,text in self.pages.items():
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])
            new=name in {f'{n:02d}.html' for n in range(6,51)}
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
        self.assertIn('essays 11–29 available',self.pages['index.html'])
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
    def test_sixth_batch_editorial_boundaries(self):
        for n,zh_marker,en_marker in (
            (26,'不能规定只有拿尺的一方','Permission to notice that the ruler is too short'),
            (27,'水要真的回来','A change of attitude cannot, by itself'),
            (28,'他不是整场一言不发','The teacher is already explaining'),
            (29,'镜子的比喻不能替别人发出原谅的命令','The mirror cannot issue an order to forgive'),
            (30,'第一步说得漂亮','Smaller scissors do not, by themselves'),
        ):
            self.assertIn(zh_marker,(b.DATA/'zh'/f'{n:02d}.md').read_text())
            self.assertIn(en_marker,(b.DATA/'en'/f'{n:02d}.md').read_text())
            self.assertIn(n,b.CHAPTERS)
            tc=(b.DATA/'zh-hant'/f'{n:02d}.md').read_text()
            for error in ('贊美','贊許','太衝莫勝','無為名屍','拿不准','松開','身份牌','說明瞭','晚回資訊','往吊之'):
                self.assertNotIn(error,tc)
        self.assertIn('太沖莫勝',(b.DATA/'zh-hant/28.md').read_text())
        self.assertIn('無為名尸',(b.DATA/'zh-hant/29.md').read_text())
        self.assertIn('www.chineseclassic.com/content/441',self.pages['30.html'])
        self.assertIn('漢書/卷030',self.pages['30.html'])
        self.assertIn('href="30.html"',self.pages['index.html'])
        self.assertIn('this route is complete',self.pages['index.html'])
        self.assertNotIn('没有骗人',self.m['items'][28]['zh_title'])
        self.assertNotIn('讲的不是感情',self.m['items'][27]['zh_title'])
    def test_seventh_batch_editorial_boundaries(self):
        for n,zh_marker,en_marker in (
            (31,'他在用类比论证','He is reasoning by analogy'),
            (32,'相亲本身不能推出对外必然不仁','Affection for insiders does not logically entail cruelty'),
            (33,'未大”明明在说尚未达到','Its force does not depend on pretending'),
            (34,'文章后来还明说“伯乐之罪”','the text explicitly assigns blame to Bole'),
            (35,'身体不是身外之物','A body is not an external possession'),
        ):
            self.assertIn(zh_marker,(b.DATA/'zh'/f'{n:02d}.md').read_text())
            self.assertIn(en_marker,(b.DATA/'en'/f'{n:02d}.md').read_text())
            self.assertIn(n,b.CHAPTERS)
            tc=(b.DATA/'zh-hant'/f'{n:02d}.md').read_text()
            for error in ('這隻能','乾活','證明瞭','千裡','稱贊','贊譽','松開','松緩','松滑','身份','賬'):
                self.assertNotIn(error,tc)
        self.assertIn('通行本后面还有一大段回答',(b.DATA/'zh/32.md').read_text())
        self.assertIn('通行本还有关于天地与治理的总结',(b.DATA/'zh/33.md').read_text())
        self.assertIn('若所言，顺吾意则生，逆吾心则死',(b.DATA/'zh/35.md').read_text())
        self.assertIn('不是推测“真正的庄子一定会怎样写”',(b.DATA/'zh/35.md').read_text())
        self.assertIn('www.chineseclassic.com/content/477',self.pages['31.html'])
        self.assertIn('www.chinulture.com/ebook/read/341562/514497',self.pages['32.html'])
        self.assertIn('not an ancient passage',self.pages['35.html'])
        self.assertIn('essays 30–41 available',self.pages['index.html'])
        self.assertNotIn('是真的懂马',self.m['items'][34]['zh_title'])
        self.assertNotIn('比一个坏国君干净',self.m['items'][35]['zh_title'])
    def test_eighth_batch_editorial_boundaries(self):
        for n,zh_marker,en_marker in (
            (36,'非故随大王也','He refuses the flattering explanation'),
            (37,'原文没有证明离开贫穷只有这六条路','Wealth does not automatically prove corruption'),
            (38,'死伤六十余人','More than sixty are killed or injured'),
            (39,'感动不是鉴真仪','Being moved is not an authenticity detector'),
            (40,'孩子推辞，黄帝又问','Removing harm is not the same as removing everyone'),
        ):
            self.assertIn(zh_marker,(b.DATA/'zh'/f'{n:02d}.md').read_text())
            self.assertIn(en_marker,(b.DATA/'en'/f'{n:02d}.md').read_text())
            self.assertIn(n,b.CHAPTERS)
            tc=(b.DATA/'zh-hant'/f'{n:02d}.md').read_text()
            for error in ('身份','贊賞','稱贊','贊美','贊嘆','賬','萬鐘','沈迷','沈寂','深沈','千裡','鑒真','復述','復核','答復','計劃','底稿'):
                self.assertNotIn(error,tc)
        self.assertIn('遂不受也',(b.DATA/'zh/36.md').read_text())
        self.assertIn('文字没有说子贡没有听见琴声',(b.DATA/'zh/37.md').read_text())
        self.assertIn('皆服毙其处也',(b.DATA/'zh/38.md').read_text())
        self.assertIn('处丧以哀，无问其礼',(b.DATA/'zh/39.md').read_text())
        self.assertIn('乘日之车',(b.DATA/'zh/40.md').read_text())
        self.assertIn('莊子祠堂記',self.pages['36.html'])
        self.assertNotIn('再悲也不哀',self.m['items'][39]['zh_title'])
        self.assertNotIn('他没有劝人',self.m['items'][38]['zh_title'])
    def test_ninth_batch_editorial_boundaries(self):
        for n,zh_marker,en_marker in (
            (41,'喝药反而添了病','medicine that makes the condition worse'),
            (42,'这本来就在讲心志不分散','Concentration is therefore not a mistaken description'),
            (43,'不是在这里学习下水','The passage is not a guide to surviving rapids'),
            (44,'原文没有告诉我们他最后削了多久','We are not told how long the carving itself takes'),
            (45,'有些黄金，不该要求人看成瓦片','Some gold should not be mentally converted into tiles'),
        ):
            self.assertIn(zh_marker,(b.DATA/'zh'/f'{n:02d}.md').read_text())
            self.assertIn(en_marker,(b.DATA/'en'/f'{n:02d}.md').read_text())
            self.assertIn(n,b.CHAPTERS)
            self.assertIn('www.chineseclassic.com/content/'+('487' if n==41 else '483'),self.pages[f'{n:02d}.html'])
            tc=(b.DATA/'zh-hant'/f'{n:02d}.md').read_text()
            for error in ('乾活','乾得','瞄准','身份','贊美','復述','四十裡','計劃','鈎','底稿'):
                self.assertNotIn(error,tc)
        self.assertIn('非也”“未也',(b.DATA/'zh/41.md').read_text())
        self.assertIn('whether the other person can disagree',(b.DATA/'en/41.md').read_text())
        self.assertIn('旧注解作黏蝉的时节',(b.DATA/'zh/42.md').read_text())
        self.assertIn('两段在原书里并不紧挨着',(b.DATA/'zh/43.md').read_text())
        self.assertIn('不然则已',(b.DATA/'zh/44.md').read_text())
        self.assertNotIn('比花在手上的多',self.m['items'][44]['zh_title'])
        self.assertIn('essays 42–50 available',self.pages['index.html'])
        self.assertIn('href="42.html"',self.pages['index.html'])
    def test_tenth_batch_editorial_boundaries(self):
        for n,zh_marker,en_marker in (
            (46,'疲劳不是“虚张声势”的证据','fatigue does not diagnose bluffing'),
            (47,'这些比喻不是在“否”之后','They precede the River Lord’s question'),
            (48,'是六种观法','gives six approaches'),
            (49,'非谓其薄之也','The text supplies its own qualification'),
            (50,'故事没有说元君此前从未见过他的画','does not say that the ruler has never seen'),
        ):
            self.assertIn(zh_marker,(b.DATA/'zh'/f'{n:02d}.md').read_text())
            self.assertIn(en_marker,(b.DATA/'en'/f'{n:02d}.md').read_text())
            self.assertIn(n,b.CHAPTERS)
            tc=(b.DATA/'zh-hant'/f'{n:02d}.md').read_text()
            for error in ('松下來','回復','提心弔膽','一髮現','因之捨','贊許','計劃','鑒別','底稿'):
                self.assertNotIn(error,tc)
        self.assertIn('三次“未也”，最后一次“几矣”',(b.DATA/'zh/46.md').read_text())
        self.assertIn('真诚不等于双方都对',(b.DATA/'zh/48.md').read_text())
        self.assertIn('不要拿自身所得去殉逐名声',(b.DATA/'zh/49.md').read_text())
        self.assertIn('因之舍',(b.DATA/'zh-hant/50.md').read_text())
        self.assertIn('Covertly watching people',(b.DATA/'en/50.md').read_text())
        for n in (47,48,49):
            self.assertIn('www.chineseclassic.com/content/481',self.pages[f'{n}.html'])
        self.assertIn('www.chineseclassic.com/content/485',self.pages['50.html'])
        self.assertNotIn('一定是自己贵',self.m['items'][48]['zh_title'])
        self.assertNotIn('一笔还没画',self.m['items'][50]['zh_title'])
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
