#!/usr/bin/env python3
"""Guard the adversity special study without altering the original main route."""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

from build_action_adversity import ROOT, TARGET, URL, AdversityTraditionalConverter, load_item, render
from build_content_registry import scan_page
from build_search_index import extract_recent_fiction_descriptions
from web_analytics import TOKEN


class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.items = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.items.append((tag, dict(attrs)))


class AdversityPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.item = load_item()
        cls.pages = render()
        cls.article = cls.pages[TARGET/'adversity.html']

    def test_idempotent_outputs(self):
        self.assertEqual(len(self.pages), 3)
        for path,text in self.pages.items():
            self.assertEqual(path.read_text(),text, str(path))

    def test_three_complete_bodies(self):
        text = self.article
        bodies = re.findall(r'<div class="essay-body adversity-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>',text,re.S)
        self.assertEqual({lang for lang,body in bodies},{'en','zh','hant'})
        for lang,body in bodies:
            self.assertEqual(body.count('<h2>'),3)
            self.assertNotIn('<h3',body)
            self.assertEqual(body.count('<p>'),35)
            self.assertNotRegex(body,r'\bD\d{1,3}\b|\b\d{2}DD\b')
        self.assertNotRegex(dict(bodies)['en'],r'[\u3400-\u9fff]')
        self.assertIn('那條路走不通以後',text)
        self.assertEqual(set(extract_recent_fiction_descriptions(text)),{'en','zh-Hans','zh-Hant'})

    def test_head_schema_and_tracking(self):
        tags = Tags(self.article).items
        headers = [a for t,a in tags if t=='header']
        self.assertEqual(len(headers),1)
        self.assertIn('site-shell-header',headers[0]['class'])
        self.assertEqual([a['href'] for t,a in tags if t=='link' and a.get('rel')=='canonical'],[URL])
        self.assertEqual({a['data-set-language'] for t,a in tags if 'data-set-language' in a},{'en','zh','zh-hant'})
        beacons = [a for t,a in tags if t=='script' and 'cloudflareinsights.com/beacon.min.js' in a.get('src','')]
        self.assertEqual(len(beacons),1)
        self.assertEqual(json.loads(beacons[0]['data-cf-beacon'])['token'],TOKEN)
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',self.article,re.S)[1])
        self.assertEqual(schema['citation'],self.item['source_url'])
        self.assertEqual(schema['datePublished'],'2026-10-26')
        self.assertEqual(schema['inLanguage'],['en','zh-Hans','zh-Hant'])

    def test_targets(self):
        for tag,attrs in Tags(self.article).items:
            url = attrs.get('href' if tag in ('a','link') else 'src','')
            parts = urlsplit(url)
            if not parts.path or parts.scheme or parts.netloc:
                continue
            path = ROOT/unquote(parts.path.lstrip('/')) if parts.path.startswith('/') else TARGET/unquote(parts.path)
            self.assertTrue(path.is_file(),url)
            if parts.fragment:
                self.assertRegex(path.read_text(),r'\bid=["\']'+re.escape(parts.fragment)+r'["\']')

    def test_separate_entry_and_traditional_map(self):
        index = self.pages[TARGET/'index.html']
        self.assertEqual(index.count('<!-- ACTION ADVERSITY EN START -->'),1)
        self.assertEqual(index.count('<!-- ACTION ADVERSITY ZH START -->'),1)
        self.assertEqual(index.count('href="adversity.html"'),2)
        self.assertLess(index.index('<h1'),index.index('<!-- ACTION ADVERSITY EN START -->'))
        self.assertNotIn('ep10.html',index)
        for name in ['prequel','interface',*(f'ep{i:02d}' for i in range(1,10))]:
            self.assertEqual(index.count(f'href="{name}.html"'),2)
        js = self.pages[TARGET/'zh-hant-data/index.js']
        variants = json.loads(re.search(r'  var variants = (\{.*?\});',js)[1])
        self.assertEqual(variants[self.item['title_zh']],'那條路走不通以後')
        self.assertIn(self.item['deck_zh'],variants)
        c=AdversityTraditionalConverter()
        try:
            self.assertEqual(c.convert('克里米亚；合伙；核实；一周；一份文件。'),'克里米亞；合夥；核實；一週；一份文件。')
        finally:
            c.close()

    def test_discovery(self):
        for name in ['index.html','latest.html']:
            self.assertIn('essays/action/adversity.html',(ROOT/name).read_text())
        self.assertIn('11 essays + 1 special study',(ROOT/'library.html').read_text())
        for language in ['en','zh-hans','zh-hant']:
            records=json.loads((ROOT/'data/search'/f'{language}.json').read_text())['records']
            rows=[r for r in records if r['u']=='essays/action/adversity.html']
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]['d'],'sae-philosophy')
        self.assertEqual(scan_page(ROOT,TARGET/'adversity.html')['domain'],'sae-philosophy')
        urls={e.text for e in ET.parse(ROOT/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        self.assertIn(URL,urls)
        updates=json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        rows=[u for u in updates if u['id']=='2026-10-26-action-adversity']
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['url'],'essays/action/adversity.html')


if __name__ == '__main__':
    unittest.main(verbosity=2)
