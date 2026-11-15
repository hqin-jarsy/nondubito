"""Published reader chrome, language clusters and original/continuation boundary."""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit
from hongloumeng_language_metadata import LANGUAGES
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'classics/hongloumeng'
class ReaderLinks(unittest.TestCase):
    def test_all_eight_language_clusters_and_sitemap(self):
        ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls=[x.text for x in ET.parse(ROOT/'sitemap.xml').findall('s:url/s:loc',ns)]
        for name in ['index.html','edition.html']+[f'ch{n:03d}.html' for n in range(1,81)]:
            expected={code:'https://nondubito.net/classics/hongloumeng/'+directory+('' if name=='index.html' else name) for code,directory in LANGUAGES}
            expected['x-default']=expected['zh-Hans']
            for code,directory in LANGUAGES:
                with self.subTest(name=name,language=code):
                    text=(BASE/directory/name).read_text()
                    links=dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">',text))
                    self.assertEqual(links,expected)
                    canonical=re.search(r'<link rel="canonical" href="([^"]+)">',text)[1]
                    self.assertEqual(canonical,expected[code])
                    self.assertEqual(urls.count(canonical),1)
                    for url in links.values():
                        path=ROOT/urlsplit(url).path.lstrip('/')
                        if url.endswith('/'):path/='index.html'
                        self.assertTrue(path.is_file())
    def test_eighty_eightyone_roundtrip(self):
        for code,directory in LANGUAGES:
            last=(BASE/directory/'ch080.html').read_text()
            first=(ROOT/'originals/hongloumeng'/directory/'ch081.html').read_text()
            self.assertIn('/originals/hongloumeng/'+directory+'ch081.html',last)
            self.assertIn('/classics/hongloumeng/'+directory+'ch080.html',first)
    def test_stale_labels_and_publication_notices(self):
        self.assertNotIn('未訳箇所あり',(BASE/'ja/index.html').read_text())
        self.assertNotIn('Elle est en cours',(BASE/'fr/edition.html').read_text())
        self.assertNotIn('jia Yingchun',(BASE/'es/index.html').read_text())
        self.assertNotIn('jia Yingchun',(BASE/'es/ch079.html').read_text())
        for name in ['edition.html','ch080.html','index.html']:
            self.assertNotIn('Chapters 86–110 remain unpublished',(BASE/'en'/name).read_text())
            self.assertNotIn('第八十六〜百十回は未公開',(BASE/'ja'/name).read_text())
        for directory in ['', 'zh-hant/']:
            self.assertIn('class="brand" href="/"',(BASE/directory/'index.html').read_text())
    def test_catalog_formatting(self):
        ja=(BASE/'ja/index.html').read_text();ko=(BASE/'ko/index.html').read_text()
        for n in range(1,81):
            text=re.search(fr'<a href="ch{n:03d}.html">(.*?)</a>',ko)[1]
            self.assertRegex(text,fr'^제{n}회 · ')
        for n in list(range(66,71))+[72,73,74,76]:
            text=re.search(fr'<a href="ch{n:03d}.html">(.*?)</a>',ja)[1]
            self.assertRegex(text,r'^\d+\. 第.+回　')
if __name__=='__main__':unittest.main()
