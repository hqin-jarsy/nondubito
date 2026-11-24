#!/usr/bin/env python3
"""Verify the exact author attachment and chapter 87's declared release editions."""
import hashlib
import html
import json
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET

import build_hongloumeng_original as build


class Chapter87Tests(unittest.TestCase):
    def test_exact_source_and_rendered_paragraphs(self):
        raw = (build.ROOT / 'data/originals/hongloumeng/ch087.zh.txt').read_bytes()
        self.assertEqual(len(raw), 26362)
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '00da7a7593b913a5c02f578967e1dac05bd36dab771f33c2706498a2d2b33b6e')
        lines = raw.decode().splitlines()
        self.assertEqual(lines[0], '# 第八十七回　凤辣子失势尝世冷　痴公子有问立菱洲')
        units = [(i, v) for i, v in enumerate(lines, 1) if i > 1 and v]
        self.assertEqual(len(units), 148)
        pattern = r'<p data-source-line="(\d+)">(.*?)</p>'
        hans = (build.TARGET / 'ch087.html').read_text()
        hant = (build.TARGET / 'zh-hant/ch087.html').read_text()
        self.assertEqual([(int(i), html.unescape(v)) for i, v in re.findall(pattern, hans)], units)
        self.assertEqual([int(i) for i, _ in re.findall(pattern, hant)], [i for i, _ in units])
        self.assertEqual(html.unescape(re.sub(r'<[^>]+>', '', re.search(r'<h1>(.*?)</h1>', hans)[1])), lines[0][2:])
        self.assertTrue(units[-1][1].endswith('要知端详，且听下回分解。'))
        for form in ('鳳辣子失勢嘗世冷', '沉在外頭', '查明了', '不干奴才', '鞓帶上繫一條紅穗',
                     '沉甸甸', '枯菱葉捲到', '只餘一點', '幾隻封了口'):
            self.assertIn(form, hant)
        for bad in ('沈在外頭', '查明瞭', '不乾奴才', '幾只封了口'):
            self.assertNotIn(bad, hant)

    def test_release_reach_and_exactly_declared_editions_are_indexed(self):
        full = build.ch087_multilingual(build.PUBLICATION)
        locales = build.EDITIONS if full else {k:build.EDITIONS[k] for k in ('zh','zh-hant')}
        expected_paths = {lang:'originals/hongloumeng/'+directory+'ch087.html'
                          for lang,(directory,_,_) in locales.items()}
        expected = set(expected_paths.values())
        urls = {el.text.removeprefix('https://nondubito.net/') for el in
                ET.parse(build.ROOT/'sitemap.xml').getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        self.assertEqual({url for url in urls if url.startswith('originals/hongloumeng/') and url.endswith('/ch087.html')}, expected)
        hits = {}
        for path in (build.ROOT/'data/search').glob('*.json'):
            found = [r['u'] for r in json.loads(path.read_text())['records']
                     if r['u'].startswith('originals/hongloumeng/') and r['u'].endswith('/ch087.html')]
            if found:
                hits[path.stem] = found
        expected_hits = {'zh-hans' if l=='zh' else l:[url] for l,url in expected_paths.items()}
        self.assertEqual(hits, expected_hits)
        for lang, (directory, _, _) in build.EDITIONS.items():
            folder = build.TARGET/directory
            index = (folder/'index.html').read_text()
            if lang in locales:
                page = (folder/'ch087.html').read_text()
                expected_alts = [code for _,code,_ in locales.values()]+['x-default']
                self.assertEqual(re.findall('hreflang="([^"]+)"', page), expected_alts)
                self.assertIn('href="ch085.html"', (folder/'ch086.html').read_text())
                self.assertIn('href="ch087.html"', (folder/'ch086.html').read_text())
                self.assertIn('href="ch086.html"', page)
                self.assertIn('href="ch087.html"', index)
                if lang in ('zh','zh-hant'):
                    self.assertIn('第八十八回', page)
                else:
                    from hongloumeng_translations import CH087_COMPLETED, edition
                    self.assertIn(html.escape(CH087_COMPLETED[lang][1]), page)
                    self.assertNotIn('href="../ch087.html" hreflang="zh-Hans"', index)
                    _, units, notes = edition('ch087',lang)
                    body=page.split('<div class="novel-text">',1)[1].split('</article>',1)[0]
                    self.assertEqual([int(n) for n in re.findall(r'data-source-unit="(\d+)"', body)], list(range(1,149)))
                    self.assertEqual(len(units),148)
                    self.assertFalse(notes)
            else:
                self.assertFalse((folder/'ch087.html').exists())
                self.assertIn('href="../ch087.html" hreflang="zh-Hans"', index)
                self.assertNotIn('href="ch087.html"', index)

    def test_earlier_and_ch087_chinese_narratives_unchanged(self):
        body = lambda s: s.split('<div class="novel-text">', 1)[1].split('</article>', 1)[0]
        for filename in ('ch081', 'ch082', 'ch083', 'ch084', 'ch085', 'ch086', 'ch087'):
            chapter_editions = (build.EDITIONS.values() if filename != 'ch087'
                                else (build.EDITIONS[k] for k in ('zh','zh-hant')))
            for directory, _, _ in chapter_editions:
                page = build.TARGET/directory/(filename+'.html')
                earlier = subprocess.check_output(['git', 'show', 'de27614:'+str(page.relative_to(build.ROOT))],
                                                  cwd=build.ROOT, text=True)
                at_ch087 = subprocess.check_output(['git','show','c0abfe1:'+str(page.relative_to(build.ROOT))],cwd=build.ROOT,text=True)
                self.assertEqual(body(at_ch087), body(earlier), str(page))
                if filename == 'ch087':
                    self.assertEqual(body(page.read_text()), body(earlier), str(page))


if __name__ == '__main__':
    unittest.main()
