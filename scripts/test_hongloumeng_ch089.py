"""Verify the eight Chapter 89 editions stay aligned and publish atomically."""
import copy
import hashlib
import html
import json
import re
import unittest
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

import build_hongloumeng_original as build
from hongloumeng_translations import DATA, ch089_multilingual, edition

PREFIX = 'originals/hongloumeng/'
UPDATE = '2026-11-27-red-chamber-ch089-eight-languages'


class Chapter89Tests(unittest.TestCase):
    def test_release_is_atomic(self):
        self.assertTrue(ch089_multilingual(build.PUBLICATION))
        partial = copy.deepcopy(build.PUBLICATION)
        partial['chapter_publications']['ch089']['languages'].remove('ko')
        with self.assertRaises(ValueError):
            ch089_multilingual(partial)

    def test_readers_navigation_and_fidelity(self):
        expected = {code: PREFIX+directory+'ch089.html'
                    for directory, code, _ in build.EDITIONS.values()}
        source = build.PUBLICATION['chapter_sources']['ch089']
        for lang, (directory, code, _) in build.EDITIONS.items():
            with self.subTest(lang=lang):
                folder = build.ROOT / PREFIX / directory
                page = (folder/'ch089.html').read_text()
                self.assertIn(f'<html lang="{code}"', page)
                self.assertIn(f'<link rel="canonical" href="https://nondubito.net/{expected[code]}">', page)
                alternatives = dict(re.findall(r'rel="alternate" hreflang="([^"]+)" href="https://nondubito.net/([^"]+)"', page))
                self.assertEqual(alternatives, {**expected, 'x-default':expected['zh-Hans']})
                menu = page.split('<details class="language-menu">', 1)[1].split('</details>', 1)[0]
                targets = {lg:urljoin(expected[code], href) for href,lg in re.findall(r'href="([^"]+)" lang="([^"]+)"',menu)}
                self.assertEqual(targets, expected)
                self.assertIn('href="ch088.html"', page)
                self.assertNotIn('href="ch090.html"', page)
                self.assertIn('href="ch089.html"', (folder/'ch088.html').read_text())
                self.assertIn('href="ch089.html"', (folder/'index.html').read_text())
                body = page.split('<div class="novel-text">', 1)[1].split('</article>', 1)[0]
                if lang in ('zh', 'zh-hant'):
                    key, digest = ('source','source_sha256') if lang=='zh' else ('traditional_source','traditional_sha256')
                    raw = (DATA.parent/source[key]).read_bytes()
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), source[digest])
                    self.assertEqual([html.unescape(v) for v in re.findall(r'<p data-source-line="\d+">(.*?)</p>', body)], [l for l in raw.decode().splitlines() if l][1:])
                else:
                    _, units, notes = edition('ch089', lang)
                    self.assertEqual([i for i, _ in units], list(range(1, 126)))
                    actual = re.findall(r'<div data-source-unit="(\d+)"><p>(.*?)</p></div>',body)
                    self.assertEqual([(int(i), html.unescape(v.replace('<br>', '\n'))) for i,v in actual],units)
                    self.assertFalse(notes)

    def test_discovery(self):
        sitemap=ET.parse(build.ROOT/'sitemap.xml')
        urls={n.text for n in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        for directory, code, _ in build.EDITIONS.values():
            url = PREFIX+directory+'ch089.html'
            self.assertIn('https://nondubito.net/'+url, urls)
            records=json.loads((build.ROOT/f'data/search/{code.lower()}.json').read_text())['records']
            self.assertEqual([r['u'] for r in records if r['u']==url], [url])
        for directory in ('', 'en/', 'zh-hant/'):
            hub_path='essays/literature/hlm/'+directory+'index.html'
            hub=(build.ROOT/hub_path).read_text()
            link, = re.findall(r'href="([^"]*ch089.html)"', hub)
            self.assertEqual(urljoin(hub_path, link), PREFIX+directory+'ch089.html')
        for f in ('latest.html', 'index.html'):
            self.assertIn(UPDATE, (build.ROOT/f).read_text())


if __name__ == '__main__':
    unittest.main()
