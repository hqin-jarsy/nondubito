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
            self.assertEqual(papers,[f'https://self-as-an-end.net/papers/sae-hongloumeng-{i}.html' for i in range(3)])
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
            self.assertNotIn('<a ',section)
            self.assertIn('Not yet released' if lang=='en' else ('尚未公開' if lang=='zh-hant' else '尚未公开'),section)


if __name__=='__main__': unittest.main()
