#!/usr/bin/env python3
"""Check archival notices without changing historical Negativa prose."""
import hashlib
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/method-negativa-version-note.json').read_text())
class Meta(HTMLParser):
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'meta' and d.get('name') == 'description': self.description = d.get('content')
class VersionNoticeTests(unittest.TestCase):
    def test_historical_bodies_byte_identical(self):
        for path, hashes in DATA['original_body_sha256'].items():
            s = (ROOT / path).read_text()
            bodies = re.findall(r'<div class="essay-body\b[^>]*>.*?</div>', s, re.S)
            self.assertEqual(hashes, [hashlib.sha256(x.encode()).hexdigest() for x in bodies], path)
    def test_notice_and_index_link(self):
        for path in DATA['original_body_sha256']:
            for f in [ROOT / path, (ROOT / path).with_name('index.html')]:
                s = f.read_text()
                self.assertIn('negativa-version-note', s)
                self.assertIn('href="' + DATA['current_paper'] + '"', s)
                self.assertIn('V2', s)
                self.assertNotRegex(s, r'<a\b[^>]*>(?:(?!</a>).)*<a\b')
    def test_metadata(self):
        for path in DATA['original_body_sha256']:
            p=Meta();p.feed((ROOT/path).read_text())
            self.assertIn('V2', p.description)
            self.assertGreater(len(p.description), 20)
    def test_traditional_mapping(self):
        for name in ['0', 'index']:
            s=(ROOT/'essays/method/zh-hant-data'/f'{name}.js').read_text()
            d=json.loads(re.search(r'var variants = (\{.*?\});',s,re.S)[1])
            self.assertEqual(d[DATA['notes']['zh'][0]+' '], DATA['notes']['zh-Hant'][0]+' ')
            self.assertEqual(d[DATA['notes']['zh'][1]], DATA['notes']['zh-Hant'][1])
    def test_search_records(self):
        self.assertEqual(len(DATA['search_records_updated']),8)
        for file,path in DATA['search_records_updated']:
            records=json.loads((ROOT/file).read_text())['records']
            matches=[r for r in records if r['u']==path]
            self.assertEqual(len(matches),1)
            self.assertIn('V2',matches[0]['x'])
if __name__ == '__main__': unittest.main()
