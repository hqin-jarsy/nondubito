#!/usr/bin/env python3
import html
import json
import re
import unittest
import hashlib
from urllib.parse import urlsplit,unquote
import build_hongloumeng_original as build
import build_search_index as search
from hongloumeng_translations import edition, FOREIGN, DATA, DATE

class OriginalTests(unittest.TestCase):
    def test_author_revision_20261019(self):
        publication=json.loads((build.ROOT/'data/originals/hongloumeng/publication.json').read_text())
        self.assertEqual(publication['author_revision']['date'],'2026-10-19')
        self.assertEqual(publication['author_revision']['chapters'],[81,82])
        for stem in ('ch081','ch082'):
            record=publication['chapter_sources'][stem]
            self.assertEqual(record['source_sha256'],build.CHAPTERS[stem]['sha256'])
            self.assertEqual(record['source_bytes'],(build.ROOT/f'data/originals/hongloumeng/{stem}.zh.txt').stat().st_size)
            self.assertEqual(record['modified'],build.CHAPTERS[stem]['modified'])
            self.assertEqual(record['modified'],'2026-10-19')
        ch81='\n'.join(build.manuscript('ch081'))
        self.assertIn('站了一站，心下想道',ch81)
        self.assertIn('隔了这几年，尚有一缕香气',ch81)
        ch82='\n'.join(build.manuscript('ch082'))
        for phrase in ('下孟还生些', '和尚的话，如何作得准', '拿门闩打过他一回',
                       '他外祖母原是大太太的陪房', '欠了我们铺子里两吊酱钱'):
            self.assertIn(phrase,ch82)
        self.assertEqual(build.CHAPTERS['ch081']['published'],'2026-10-05')
        self.assertEqual(build.CHAPTERS['ch082']['published'],'2026-10-07')

    def test_author_revision_20261012(self):
        source = '\n'.join(build.manuscript('ch081'))
        for phrase in ('他母亲的孝已满了', '竟是鱼眼睛了', '还是我替他说破的', '紫檀堡的房子，还是我当日说出来的', '忘不了灯前替我缝衣袖，', '说不出别样心思大马猴', '两人才笑了一时'):
            self.assertIn(phrase, source)
        self.assertNotIn('抛红豆，滴相思。', source)
        publication = json.loads((build.ROOT / 'data/originals/hongloumeng/publication.json').read_text())
        self.assertEqual(publication['source_sha256'], build.CHAPTERS['ch081']['sha256'])
        self.assertEqual(publication['source_bytes'], (build.ROOT / 'data/originals/hongloumeng/ch081.zh.txt').stat().st_size)

    def test_final_manuscript_and_generated_pages(self):
        for p,s in build.render().items():
            self.assertEqual(p.read_text(),s)
            if p.stem in build.CHAPTERS and p.parent.name not in FOREIGN:
                lines=build.manuscript(p.stem)
                actual=[(int(n),html.unescape(re.sub('<[^>]+>','',v))) for n,v in re.findall(r'<p data-source-line="(\d+)">(.*?)</p>',s)]
                self.assertEqual([n for n,v in actual],[i for i,v in enumerate(lines,1) if i>1 and v])
                self.assertEqual(len(re.findall('data-source-line=',s.split('<div class="verse">')[1].split('</div>')[0])),{'ch081':8,'ch082':2,'ch083':1}[p.stem])
                if p.parent==build.TARGET:
                    self.assertEqual(actual,[(i,v) for i,v in enumerate(lines,1) if i>1 and v])
                    self.assertEqual(html.unescape(re.sub('<[^>]+>','',re.search('<h1>(.*?)</h1>',s)[1])),lines[0])
                elif p.stem=='ch081':
                    for good in ('城東二十里','一干人','對不準針眼','我繫了送給'):self.assertIn(good,s)
                    for bad in ('城東二十裡','一乾人','對不准針眼'):self.assertNotIn(bad,s)
                elif p.stem=='ch082':
                    for good in ('腰繫青絲','繫一條淡','帕子鬆了','拿不準','參鬚','如何作得準'):self.assertIn(good,s)
                else:
                    for good in ('茶飯一發','方鬆開','紙紮','兩隻手','人數估準','桌几裡頭','餘下的銀封','準信'):self.assertIn(good,s)
                    for bad in ('茶飯一髮','桌幾裡頭','准信'):self.assertNotIn(bad,s)

    def test_navigation_and_metadata(self):
        for p,s in build.render().items():
            for href in re.findall(r'href="([^"]+)"',s):
                u=urlsplit(html.unescape(href))
                if u.scheme or not u.path:continue
                self.assertTrue((p.parent/unquote(u.path)).resolve().exists(),href)
            self.assertNotIn('ch084.html',s)
            self.assertEqual(len(re.findall(r'rel="alternate" hreflang=',s)),9)
            for directory,code,_ in build.EDITIONS.values():
                self.assertIn(f'hreflang="{code}" href="{build.ORIGIN+directory+(p.name if p.stem in build.CHAPTERS else "")}"',s)
            self.assertIn('<details class="language-menu">',s)
            self.assertEqual(s.count('aria-current="page"'),1)
            foreign=p.parent.name in FOREIGN
            if foreign:self.assertIn(html.escape(FOREIGN[p.parent.name][2]),s)
            else:self.assertIn('不是曹雪芹',s)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s)[1])
            self.assertEqual(schema['@type'],'Chapter' if p.stem in build.CHAPTERS else 'CollectionPage')
            self.assertEqual(schema['inLanguage'],p.parent.name if foreign else 'zh-Hant' if p.parent.name=='zh-hant' else 'zh-Hans')
            if p.stem in build.CHAPTERS:
                translation_date='2026-10-24' if p.stem=='ch083' else DATE
                self.assertEqual(schema['datePublished'],translation_date if foreign else build.CHAPTERS[p.stem]['published'])
                self.assertEqual(schema['dateModified'], translation_date if foreign else build.CHAPTERS[p.stem].get('modified', build.DATE))
                if foreign:self.assertEqual(schema['translationOfWork']['url'],build.ORIGIN+p.stem+'.html')
                nav=s.split('<nav class="chapter-nav"')[1].split('</nav>')[0]
                keys=list(build.CHAPTERS);position=keys.index(p.stem)
                for step in (-1,1):
                    if 0<=position+step<len(keys):self.assertIn(keys[position+step]+'.html',nav)
            else:
                self.assertEqual(len(schema['hasPart']),len(build.CHAPTERS))
                self.assertEqual(schema['dateModified'],'2026-10-24' if foreign else max(ch.get('modified',ch['published']) for ch in build.CHAPTERS.values()))

    def test_discovery(self):
        for lang,d in [('zh-hans',''),('zh-hant','zh-hant/'),*((lang,lang+'/') for lang in FOREIGN)]:
            records=json.loads((search.CHUNKS_DIR/f'{lang}.json').read_text())['records']
            for name in ('index.html',*(ch+'.html' for ch in build.CHAPTERS)):
                url=f'originals/hongloumeng/{d}{name}'
                self.assertEqual(sum(r['u']==url for r in records),1,url)

    def test_received_manuscripts_and_source_parity(self):
        publication=json.loads((build.ROOT/'data/originals/hongloumeng/publication.json').read_text())
        for path,sha in publication['multilingual_publication']['received_files'].items():
            self.assertEqual(hashlib.sha256((DATA.parent/path).read_bytes()).hexdigest(),sha,path)
        for stem in build.CHAPTERS:
            received=(DATA/'received'/stem/(stem+'_zh-Hans.md')).read_text()
            normalize=lambda value: re.sub(r'\s+','',value.lstrip('# '))
            self.assertEqual(normalize(received),normalize('\n'.join(build.manuscript(stem))))

    def test_complete_foreign_text_and_verse(self):
        normalize=lambda value: re.sub(r'\s+','',value.replace('*',''))
        for lang in FOREIGN:
            for stem in build.CHAPTERS:
                title,units,notes=edition(stem,lang)
                page=(build.TARGET/lang/(stem+'.html')).read_text()
                body=page.split('<div class="novel-text">')[1].split('</article>')[0]
                # Reconstruct all source units, including the eight distinct song lines.
                pieces=re.split(r'<div data-source-unit="(\d+)"[^>]*>',body)[1:]
                actual=[(int(pieces[i]),html.unescape(re.sub('<[^>]*>','',pieces[i+1]))) for i in range(0,len(pieces),2)]
                self.assertEqual([n for n,_ in actual],list(range(1,{'ch081':102,'ch082':68,'ch083':33}[stem])))
                self.assertEqual([(n,normalize(v)) for n,v in actual],[(n,normalize(v)) for n,v in units])
                self.assertEqual(len(re.findall(r'data-source-unit="\d+" class="verse"',page)),{'ch081':8,'ch082':2,'ch083':1}[stem])
                self.assertNotIn('<!-- P',body)
                if lang=='es' and stem=='ch081':
                    self.assertNotIn('Nota 1.',body)
                    self.assertIn('Nota 1.',page)

    def test_local_corrections_and_continuity(self):
        self.assertIn('elle n’était plus là.',edition('ch081','fr')[1][58][1])
        self.assertNotIn('niemand weiß',edition('ch081','de')[1][58][1])
        self.assertIn('einen Satz',edition('ch081','de')[1][86][1])
        self.assertIn('early',edition('ch081','en')[1][91][1])
        french='\n'.join(v for _,v in edition('ch082','fr')[1])
        self.assertNotIn('Ping-er',french)
        self.assertIn('Petite Quiète',french)
        self.assertNotIn('Grande Grande',french)
        japanese='\n'.join(v for _,v in edition('ch082','ja')[1])
        self.assertNotIn('玉釧児児',japanese)

    def test_ch083_immutable_author_text(self):
        source=(DATA.parent/'ch083.zh.txt').read_bytes()
        received=(DATA/'received/ch083/ch083_zh-Hans.md').read_bytes()
        self.assertEqual(source,received[2:])
        self.assertEqual(len([v for v in source.decode().splitlines()[1:] if v]),32)
        for phrase in ('我的女儿没了。他的女儿就是我的心肝儿肉。命根子总要跟心肝儿肉在一处。',
                       '回去替我问你妈好', '百日里头就办', '那盏灯不必吹，留着'):
            self.assertIn(phrase,source.decode())

    def test_ch083_continuity_registry(self):
        registry=json.loads((DATA/'continuity.json').read_text())['languages']
        for lang,rules in registry.items():
            title,units,_=edition('ch083',lang)
            text=title+'\n'+'\n'.join(v for _,v in units)
            for rule in rules:
                # A short name can be a substring of the preferred full title.
                check=text.replace(rule['preferred'],'') if rule['retired'] in rule['preferred'] else text
                self.assertNotIn(rule['retired'],check,(lang,rule['identity']))
        preferred={'en':['Grandmother Jia','Sunshine','Lotus Pavilion'],
                   'de':['Blaujuwel','Phönix','Herr Tschong','Frau Tschong',"Ping'er",'Mingyan'],
                   'fr':['Petite Quiète','Cri de Coucou','Brume de Thé','Grande Sœur Phénix'],
                   'es':['Pinger','Anciana Dama','pabellón del Aroma de Loto'],
                   'ko':['희봉','노마님','왕부인','항서전']}
        for lang,names in preferred.items():
            for name in names:self.assertIn(name,'\n'.join(v for _,v in edition('ch083',lang)[1]))
        japanese='\n'.join(v for _,v in edition('ch083','ja')[1])
        self.assertIn('蒲草の円座',japanese);self.assertNotIn('蒲団',japanese)
        german='\n'.join(v for _,v in edition('ch083','de')[1])
        self.assertNotIn('Phönixs',german);self.assertIn('Phönix’ Hand',german)
        for phrase in ('ließ Herrn Tschong','an Herrn Tschong','zu Herrn Tschong','sah Herrn Tschong an',
                       'Herrn Tschong entglitt','Herrn Tschong blieb nichts anderes übrig'):
            self.assertIn(phrase,german)

    def test_ch083_private_message_and_couplet(self):
        phrases={
            'en':"My daughter is gone. Her daughter is my heart's own flesh. The one who is my very life must always be with my heart's own flesh.",
            'de':'Meine Tochter ist tot. Ihre Tochter ist mein Herzblut. Mein Ein und Alles muss stets mit meinem Herzblut vereint sein.',
            'fr':'Ma fille n’est plus. Sa fille est la chair même de mon cœur. L’être qui est toute ma vie doit toujours demeurer auprès de la chair de mon cœur.',
            'es':'Mi hija ha muerto. Su hija es la carne de mi corazón. Quien es mi vida ha de estar siempre junto a la carne de mi corazón',
            'ja':'わたしの娘はもういない。あの子の娘は、わたしの心肝にも等しいいとし子だ。命とも頼む子は、どうあってもその心肝にも等しいいとし子と一緒にいなくてはならない',
            'ko':'내 딸은 세상을 떠났다. 그 애의 딸이 바로 내 심장 같은 살붙이다. 목숨 같은 아이는 언제나 심장 같은 살붙이와 함께 있어야 한다.'}
        for lang,phrase in phrases.items():
            units=edition('ch083',lang)[1]
            self.assertIn(phrase,units[7][1]);self.assertIn(phrase,units[16][1])
            self.assertEqual('\n'.join(v for _,v in units).count(phrase),2)
            page=(build.TARGET/lang/'ch083.html').read_text()
            verse=page.split('data-source-unit="32" class="verse">')[1].split('</p>')[0]
            self.assertEqual(verse.count('<br>'),2)

if __name__=='__main__':unittest.main()
