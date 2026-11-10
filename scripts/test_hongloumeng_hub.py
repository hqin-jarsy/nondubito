#!/usr/bin/env python3
"""Read-only structural and preservation checks for the Red Chamber entrance."""
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import unittest
from urllib.parse import urlsplit, unquote
from build_hongloumeng_hub import ROOT, TARGET, CATALOG, EDITIONS, render


class Nodes(HTMLParser):
    def __init__(self, source):
        super().__init__(); self.nodes=[]; self.feed(source)
    def handle_starttag(self,tag,attrs): self.nodes.append((tag,dict(attrs)))


class HubTests(unittest.TestCase):
    def test_first80_preview_keeps_original_and_continuation_separate(self):
        pages = render(include_first80=True, first80_date='2026-11-10', include_traditional=False)
        for lang, (directory, _, _) in EDITIONS.items():
            source = pages[TARGET/directory/'index.html']
            section = source.split('<section id="first80">')[1].split('</section>')[0]
            links = [attrs['href'] for tag, attrs in Nodes(section).nodes if tag == 'a']
            self.assertEqual(len(links), 3)
            self.assertEqual([Path(href).name for href in links], ['index.html', 'ch001.html', 'edition.html'])
            self.assertTrue(all('classics/hongloumeng/' in href for href in links))
            self.assertNotIn('/en/', ''.join(links))
            self.assertNotIn('/zh-hant/', ''.join(links))
            self.assertIn('Simplified Chinese only' if lang == 'en' else ('僅提供簡體中文正文' if lang == 'zh-hant' else '仅提供简体中文正文'), section)
            self.assertIn('Translations are not yet published' if lang == 'en' else ('外語翻譯尚未發佈' if lang == 'zh-hant' else '外语翻译尚未发布'), section)
            self.assertIn('edited by Han Qin' if lang == 'en' else ('由秦漢校正整理' if lang == 'zh-hant' else '由秦汉校正整理'), section)
            continuation = source.split('<section id="continuation">')[1].split('</section>')[0]
            self.assertEqual(continuation.count('<a '), 6)
            self.assertNotIn('classics/hongloumeng/', continuation)

    def test_bilingual_preview_routes_and_continuation_stay_separate(self):
        pages = render(include_first80=True, first80_date='2026-11-10', include_traditional=True)
        for lang, (directory, _, _) in EDITIONS.items():
            source = pages[TARGET/directory/'index.html']
            section = source.split('<section id="first80">')[1].split('</section>')[0]
            links = [attrs['href'] for tag, attrs in Nodes(section).nodes if tag == 'a']
            self.assertEqual(len(links), 5)
            self.assertEqual('/zh-hant/' in links[0], lang == 'zh-hant')
            self.assertTrue(links[-2].endswith('classics/hongloumeng/index.html'))
            self.assertTrue(links[-1].endswith('classics/hongloumeng/zh-hant/index.html'))
            self.assertNotIn('Simplified Chinese only', section)
            self.assertNotIn('classics/hongloumeng/en/', source)
            continuation = source.split('<section id="continuation">')[1].split('</section>')[0]
            self.assertEqual(continuation.count('<a '), 6)
            self.assertNotIn('classics/hongloumeng/', continuation)

    def test_explicit_first80_preview_requires_date(self):
        with self.assertRaises(ValueError):
            render(include_first80=True)

    def test_generated_current(self):
        for path,source in render().items(): self.assertEqual(source,path.read_text())

    def test_catalog_and_original_articles(self):
        groups=json.loads(CATALOG.read_text())
        cards=[e for g in groups for e in g['essays']]
        self.assertEqual(len(groups),10)
        self.assertEqual(len(cards),48)
        self.assertEqual(len({e['url'] for e in cards}),48)
        # Baseline before the entrance redesign, not a mutable HEAD comparison.
        previous=subprocess.check_output(['git','show','bda67f8:essays/literature/hlm/index.html'],cwd=ROOT,text=True)
        self.assertEqual([e['url'] for e in cards],re.findall(r'<a href="([^"]+)" class="essay-card">',previous))
        for e in cards:
            file=TARGET/e['url']
            original=subprocess.check_output(['git','show','bda67f8:'+str(file.relative_to(ROOT))],cwd=ROOT)
            self.assertEqual(file.read_bytes(),original,e['url'])

    def test_links_metadata_and_scope(self):
        for lang,(directory,code,_) in EDITIONS.items():
            path=TARGET/directory/'index.html';source=path.read_text();nodes=Nodes(source).nodes
            ids=[a['id'] for _,a in nodes if 'id' in a]
            self.assertEqual(len(ids),len(set(ids)))
            self.assertEqual(sum(tag=='h1' for tag,_ in nodes),1)
            self.assertIn(('html',{'lang':code,'data-lang':lang,'data-editions':code}),nodes)
            self.assertEqual(sum(tag=='details' and a.get('class')=='character-group' for tag,a in nodes),10)
            legacy=[a for tag,a in nodes if tag=='a' and 'data-legacy-language' in a]
            self.assertEqual(len(legacy),51)
            self.assertEqual({a['data-legacy-language'] for a in legacy},{'en' if lang=='en' else 'zh'})
            papers=[a['href'] for tag,a in nodes if tag=='a' and a.get('href','').startswith('https://self-as-an-end.net/papers/')]
            self.assertEqual(papers,[f'https://self-as-an-end.net/papers/sae-hongloumeng-{i}.html' for i in range(4)])
            for tag,a in nodes:
                url=a.get('href',a.get('src',''))
                if not url or urlsplit(url).scheme: continue
                parsed=urlsplit(html.unescape(url))
                target=(path.parent/unquote(parsed.path)).resolve() if parsed.path else path
                self.assertTrue(target.exists(),str(target))
                if parsed.fragment and target==path: self.assertIn(parsed.fragment,ids)
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',source,re.S)[1])
            self.assertEqual(schema['@type'],'CollectionPage')
            self.assertEqual(schema['inLanguage'],code)
            self.assertNotIn('恢复曹雪芹原稿',source)
            section=source.split('<section id="continuation">')[1].split('</section>')[0]
            self.assertEqual(section.count('<a '),6)
            self.assertIn('ch081.html',section)
            self.assertIn('ch082.html',section)
            self.assertIn('ch083.html',section)
            self.assertIn('ch084.html',section)
            self.assertIn('ch085.html',section)
            self.assertIn('original fiction by Han Qin' if lang=='en' else ('秦漢的原創小說' if lang=='zh-hant' else '秦汉的原创小说'),section)
            self.assertIn('Chapters 81–85 published' if lang=='en' else ('第八十一至八十五回定稿已發佈' if lang=='zh-hant' else '第八十一至八十五回定稿已发布'),section)


if __name__=='__main__': unittest.main()
