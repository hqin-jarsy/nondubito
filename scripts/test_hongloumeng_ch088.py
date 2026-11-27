"""Exercise publication, verse, and discovery on Chapter 88's eight reader routes."""
import functools
import hashlib
import html
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import re
import threading
import unittest
from urllib.parse import urljoin
from urllib.request import urlopen
import xml.etree.ElementTree as ET

import build_hongloumeng_original as build
from hongloumeng_translations import DATA, edition

PREFIX = 'originals/hongloumeng/'


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class Chapter88Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0),
                                        functools.partial(QuietHandler, directory=build.ROOT))
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}/'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.worker.join()
        cls.server.server_close()

    def get(self, path):
        with urlopen(urljoin(self.base, path), timeout=5) as response:
            self.assertEqual(response.status, 200)
            return response.read().decode()

    def test_readers_and_switching(self):
        expected = {code: PREFIX + directory + 'ch088.html'
                    for directory, code, _ in build.EDITIONS.values()}
        for lang, (directory, code, _) in build.EDITIONS.items():
            with self.subTest(lang=lang):
                url = expected[code]
                prior = PREFIX + directory + 'ch087.html'
                index = PREFIX + directory + 'index.html'
                for incoming in (self.get(prior), self.get(index)):
                    self.assertIn('href="ch088.html"', incoming)
                page = self.get(url)
                self.assertIn(f'<html lang="{code}"', page)
                self.assertIn(f'<link rel="canonical" href="https://nondubito.net/{url}">', page)
                alternates = dict(re.findall(r'rel="alternate" hreflang="([^"]+)" href="https://nondubito.net/([^"]+)"',page))
                self.assertEqual(alternates, {**expected, 'x-default':expected['zh-Hans']})
                menu = page.split('<details class="language-menu">',1)[1].split('</details>',1)[0]
                targets = dict((target_lang, href) for href,target_lang in re.findall(r'href="([^"]+)" lang="([^"]+)"',menu))
                self.assertEqual({l:urljoin(url,h) for l,h in targets.items()}, expected)
                nav = page.split('<nav class="chapter-nav"',1)[1]
                self.assertIn('href="ch087.html"', nav)
                self.assertIn('href="index.html"', nav)
                self.assertIn('href="ch089.html"', nav)
                self.assertIn(PREFIX, url)
                self.check_exact_body(lang, page)

    def check_exact_body(self, lang, page):
        source = build.PUBLICATION['chapter_sources']['ch088']
        body = page.split('<div class="novel-text">',1)[1].split('</article>',1)[0]
        verse = re.findall(r'data-source-unit="(\d+)" class="verse"',body)
        if lang in ('zh','zh-hant'):
            file, digest = ((source['source'],source['source_sha256']) if lang=='zh' else
                            (source['traditional_source'],source['traditional_sha256']))
            raw=(DATA.parent/file).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),digest)
            lines=[v for v in raw.decode().splitlines() if v]
            self.assertEqual(len(lines),78)
            self.assertEqual([html.unescape(v) for v in re.findall(r'<p data-source-line="\d+">(.*?)</p>',body)],lines[1:])
            group=re.search(r'<div class="verse">(.*?)</div>',body,re.S)[1]
            self.assertEqual([html.unescape(v) for v in re.findall(r'<p data-source-line="\d+">(.*?)</p>',group)],lines[65:69])
            self.assertIn('凤姐' if lang=='zh' else '鳳姐',lines[32])
        else:
            title, units, notes = edition('ch088',lang)
            self.assertEqual(len(units),77)
            self.assertEqual(verse,['65','66','67','68'])
            self.assertFalse(notes)
            vals=re.findall(r'<div data-source-unit="(\d+)"(?: class="verse")?><p>(.*?)</p></div>',body)
            decode=lambda v: html.unescape(re.sub(r'</?em>', '',v.replace('<br>','\n')))
            self.assertEqual([(int(i),decode(v)) for i,v in vals],
                             [(i,re.sub(r'\*([^*]+)\*',r'\1',v)) for i,v in units])
            if lang=='en':
                self.assertEqual(title.splitlines()[0],'Chapter 88')
                self.assertTrue(all('<br>' in v for i,v in vals if i in verse))

    def test_entrypoints_and_discovery(self):
        for directory, code in (('', 'zh-Hans'), ('zh-hant/', 'zh-Hant'), ('en/', 'en')):
            hub_path = 'essays/literature/hlm/'+directory+'index.html'
            hub = self.get(hub_path)
            below = hub.split('<section id="continuation">',1)[1].split('</section>',1)[0]
            link, = re.findall(r'href="([^"]*ch088.html)" hreflang="'+code+'"',below)
            self.assertEqual(urljoin(hub_path, link), PREFIX+directory+'ch088.html')
            self.assertIn('81–89' if code=='en' else '第八十一至八十九回', below)
        ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
        sitemap=ET.fromstring(self.get('sitemap.xml'))
        all88=[x.text for x in sitemap.iter(ns+'loc') if x.text.endswith('/ch088.html')]
        paths=[]
        for directory, code, _ in build.EDITIONS.values():
            url=PREFIX+directory+'ch088.html'
            paths.append('https://nondubito.net/'+url)
            rows=json.loads(self.get('data/search/'+code.lower()+'.json'))['records']
            self.assertEqual([r['u'] for r in rows if r['u'].endswith('/ch088.html')],[url])
        self.assertCountEqual(all88,paths)
        self.assertIn('2026-11-24-red-chamber-ch088-eight-languages', self.get('latest.html'))


if __name__ == '__main__':
    unittest.main()
