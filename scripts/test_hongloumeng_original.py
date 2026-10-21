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
                    for good in ('腰繫青絲','繫一條淡','帕子鬆了','拿不準','參鬚','如何作得準'):self.assertIn(good,s)

    def test_navigation_and_metadata(self):
        for p,s in build.render().items():
            for href in re.findall(r'href="([^"]+)"',s):
                u=urlsplit(html.unescape(href))
                if u.scheme or not u.path:continue
                self.assertTrue((p.parent/unquote(u.path)).resolve().exists(),href)
            self.assertNotIn('ch083.html',s)
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
                self.assertEqual(schema['datePublished'],DATE if foreign else build.CHAPTERS[p.stem]['published'])
                self.assertEqual(schema['dateModified'], DATE if foreign else build.CHAPTERS[p.stem].get('modified', build.DATE))
                if foreign:self.assertEqual(schema['translationOfWork']['url'],build.ORIGIN+p.stem+'.html')
                nav=s.split('<nav class="chapter-nav"')[1].split('</nav>')[0]
                self.assertIn('ch082.html' if p.stem=='ch081' else 'ch081.html',nav)
            else:
                self.assertEqual(len(schema['hasPart']),2)
                self.assertEqual(schema['dateModified'],DATE if foreign else max(ch.get('modified',ch['published']) for ch in build.CHAPTERS.values()))

    def test_discovery(self):
        for lang,d in [('zh-hans',''),('zh-hant','zh-hant/'),*((lang,lang+'/') for lang in FOREIGN)]:
            records=json.loads((search.CHUNKS_DIR/f'{lang}.json').read_text())['records']
            for name in ('index.html','ch081.html','ch082.html'):
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
                self.assertEqual([n for n,_ in actual],list(range(1,102 if stem=='ch081' else 68)))
                self.assertEqual([(n,normalize(v)) for n,v in actual],[(n,normalize(v)) for n,v in units])
                self.assertEqual(len(re.findall(r'data-source-unit="\d+" class="verse"',page)),8 if stem=='ch081' else 2)
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

if __name__=='__main__':unittest.main()
