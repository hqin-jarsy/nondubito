#!/usr/bin/env python3
"""Chapter-86 immutable source, language completeness and narrow-change checks."""
import hashlib
import html
import json
import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import urlsplit, unquote
import build_hongloumeng_original as build
from hongloumeng_translations import edition, FOREIGN, DATA, received_path

BASELINE = '419f917'

class Chapter86Tests(unittest.TestCase):
    def test_source_exact(self):
        raw=(DATA.parent/'ch086.zh.txt').read_bytes()
        self.assertEqual(len(raw),28785)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'3503d15bbcb2b3b6e109ed385b182e33aaa3788f26b8fe255f97a3c0534b0fcc')
        self.assertEqual(raw,received_path('ch086','zh-Hans').read_bytes())
        lines=raw.decode().splitlines()
        self.assertEqual(len([v for v in lines[1:] if v]),88)
        page=(build.TARGET/'ch086.html').read_text()
        actual=[html.unescape(v) for v in re.findall(r'<p data-source-line="\d+">(.*?)</p>',page)]
        self.assertEqual(actual,[v for v in lines[1:] if v])
        title=html.unescape(re.sub('<[^>]+>','',re.search('<h1>(.*?)</h1>',page)[1]))
        self.assertEqual(title,lines[0][2:])

    def test_complete_editions_and_continuity(self):
        registry=json.loads((DATA/'continuity.json').read_text())['languages']
        for lang in FOREIGN:
            title,units,notes=edition('ch086',lang)
            self.assertEqual([n for n,_ in units],list(range(1,89)),lang)
            self.assertTrue(all(v.strip() for _,v in units),lang)
            self.assertEqual(notes,[])
            text=title+'\n'+'\n'.join(v for _,v in units)
            self.assertNotIn('#',title)
            for marker in ('translation-placeholder','TODO','TBD','待翻译'):
                self.assertNotIn(marker,text,lang)
            for rule in registry.get(lang,[]):
                # P19 refers to elderly ladies in other households, not Jia's grandmother.
                scope=text.replace(dict(units)[19],'') if lang == 'de' and rule['identity'] == '贾母' else text
                check=scope.replace(rule['preferred'],'') if rule['retired'] in rule['preferred'] else scope
                self.assertNotIn(rule['retired'],check,(lang,rule['identity']))
            page=(build.TARGET/lang/'ch086.html').read_text()
            self.assertEqual(len(re.findall('data-source-unit=',page)),88,lang)
            self.assertIn('data-source-unit="88" class="verse"',page)

    def test_previous_narratives_and_sources_unchanged(self):
        for stem in ('ch081','ch082','ch083','ch084','ch085'):
            path=DATA.parent/(stem+'.zh.txt')
            self.assertEqual(path.read_bytes(),subprocess.check_output(['git','show',BASELINE+':'+str(path.relative_to(build.ROOT))],cwd=build.ROOT))
            for directory,_,_ in build.EDITIONS.values():
                page=build.TARGET/directory/(stem+'.html')
                before=subprocess.check_output(['git','show',BASELINE+':'+str(page.relative_to(build.ROOT))],cwd=build.ROOT,text=True)
                body=lambda s:s.split('<div class="novel-text">')[1].split('</article>')[0]
                self.assertEqual(body(page.read_text()),body(before),str(page))

    def test_traditional_orthography(self):
        text=(build.TARGET/'zh-hant/ch086.html').read_text()
        for phrase in ('插進髮內','那隻紫檀棋匣','兩隻鞋','託人','紙紮','沉在','餘下','查明了','綠玉斗','準折'):
            self.assertIn(phrase,text)
        for phrase in ('插進發內','綠玉鬥','查明瞭','沈在','那只'):
            self.assertNotIn(phrase,text)

    def test_all_links_and_mutual_navigation(self):
        for directory,code,_ in build.EDITIONS.values():
            path=build.TARGET/directory/'ch086.html';s=path.read_text()
            self.assertIn('href="ch085.html"',s)
            self.assertIn('ch086.html',(path.parent/'ch085.html').read_text())
            self.assertIn('ch086.html',(path.parent/'index.html').read_text())
            (self.assertIn if code.startswith('zh-') else self.assertNotIn)('ch087.html',s)
            self.assertEqual(s.count('rel="alternate" hreflang='),9)
            for href in re.findall(r'href="([^"]+)"',s):
                u=urlsplit(html.unescape(href))
                if u.scheme or not u.path:continue
                target=build.ROOT/unquote(u.path.lstrip('/')) if u.path.startswith('/') else path.parent/unquote(u.path)
                self.assertTrue(target.resolve().exists(),str(target))
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s)[1])
            self.assertEqual(schema['position'],86)
            self.assertEqual(schema['datePublished'],'2026-11-14')
            self.assertEqual(schema['inLanguage'],code)

if __name__=='__main__':unittest.main()
