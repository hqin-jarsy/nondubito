"""Completeness, primary-text preservation and reader-facing edition routes."""
import hashlib
import html
import json
import re
import unittest
from urllib.parse import unquote, urlsplit

from full_series_languages import ROOT, load_language, profile, render
from build_accountability import render as primary_pages
from build_content_registry import scan_page
from web_analytics import TOKEN


class AccountabilityLanguages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = profile('accountability')
        cls.pages = render('accountability')
        cls.receipt = json.loads((ROOT/'data/accountability/multilingual/preservation.json').read_text())

    def test_full_argument_units_and_natural_length(self):
        self.assertEqual(len(self.pages), 20)
        for language in self.spec['languages']:
            _, data = load_language('accountability', language)
            for article, count in zip(data['articles'], (23,24,25)):
                self.assertEqual(len(article['body']), count)
                self.assertEqual(len(article['coverage']), count)
                self.assertEqual(sum(p.startswith('## ') for p in article['body']), 3)
                text = '\n'.join(article['body'])
                if language in ('de','fr','es'):
                    self.assertGreater(len(text.split()), 1000)
                else:
                    self.assertGreater(len(text), 2600)
                self.assertNotRegex(text, r'\b\d{2}DD\b|TODO|PLACEHOLDER|待翻译')
                path = ROOT/self.spec['directory']/language/(article['slug']+'.html')
                rendered = self.pages[path]
                for p in article['body']:
                    self.assertIn(html.escape(p[3:] if p.startswith('## ') else p), rendered)

    def test_primary_bodies_headers_notes_and_source_data_preserved(self):
        pages = primary_pages()
        for slug, expected in self.receipt['primary_prose'].items():
            page = pages[ROOT/'essays/accountability'/(slug+'.html')]
            fragments = {
                'bodies': ''.join(re.findall(r'<div class="essay-body lw-prose[^>]*>.*?</div>', page, re.S)),
                'head': re.search(r'<div class="lw-head">.*?</div>', page, re.S)[0],
                'sources': re.search(r'<details class="lw-sources">.*?</details>', page, re.S)[0],
            }
            for key, fragment in fragments.items():
                self.assertEqual(hashlib.sha256(fragment.encode()).hexdigest(), expected[key])
            data = ROOT/'data/accountability'/(slug+'.json')
            self.assertEqual(hashlib.sha256(data.read_bytes()).hexdigest(), self.receipt['source_data'][slug])

    def test_metadata_analytics_and_same_article_switching(self):
        for path, page in self.pages.items():
            language = path.parent.name
            self.assertEqual(page, path.read_text())
            self.assertIn(f'data-editions="{language}" data-foreign-edition="true"', page)
            self.assertEqual(page.count('<h1>'), 1)
            self.assertEqual(page.count('<header '), 1)
            self.assertEqual(page.count('cloudflareinsights.com/beacon.min.js'), 1)
            self.assertIn(TOKEN, page)
            self.assertNotRegex(page, r'<script[^>]*src="[^"]*site-shell.js')
            canonical = 'https://nondubito.net/'+path.relative_to(ROOT).as_posix().removesuffix('index.html')
            self.assertIn(f'rel="canonical" href="{canonical}"', page)
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page)[1])
            self.assertEqual(schema['inLanguage'], language)
            self.assertEqual(schema['datePublished'], self.spec['date'])
            cluster = re.findall(r'rel="alternate" hreflang="([^"]+)" href="([^"]+)"', page)
            self.assertEqual(len(cluster), 7)
            self.assertFalse(any('?lang=' in url for _, url in cluster))
            menu = re.search(r'<div class="site-shell-language-options">(.*?)</div>', page)[1]
            self.assertEqual(menu.count('<a '), 8)
            self.assertEqual(menu.count('aria-current="page"'), 1)
            for code in self.spec['languages']:
                self.assertIn(f'../{code}/{path.name}', menu)
            for href in re.findall(r'href="([^"]+)"', page):
                url = urlsplit(html.unescape(href))
                if url.scheme or not url.path:
                    continue
                target = (path.parent/unquote(url.path)).resolve()
                self.assertTrue(target in self.pages or target.is_file(), (path, href))
            self.assertEqual(scan_page(ROOT,path)['languages'], [language])

    def test_review_is_separate_from_coverage_claims(self):
        for name, languages in [('cross-review-de-fr.json', ['de','fr']), ('cross-review-ja-ko.json', ['ja','ko']), ('cross-review-es.json', ['es'])]:
            report = json.loads((ROOT/'data/accountability/multilingual'/name).read_text())
            self.assertEqual(report['languages'], languages)
            self.assertEqual(report['remaining'], [])
        publication = json.loads((ROOT/'data/accountability/multilingual/publication.json').read_text())
        self.assertEqual(publication['result'], 'passed')
        self.assertEqual(publication['unresolved'], [])
        for fix in publication['resolved_issues']:
            data = json.loads((ROOT/f'data/accountability/multilingual/{fix["language"]}.json').read_text())
            article = next(a for a in data['articles'] if a['slug'] == fix['slug'])
            self.assertIn(fix['after'], article['body'][fix['paragraph']])

    def test_discovery(self):
        sitemap = (ROOT/'sitemap.xml').read_text()
        for language in self.spec['languages']:
            records = json.loads((ROOT/f'data/search/{language}.json').read_text())['records']
            urls = {r['u'] for r in records}
            for path in self.pages:
                if path.parent.name != language:
                    continue
                self.assertIn(path.relative_to(ROOT).as_posix(), urls)
                self.assertIn('https://nondubito.net/'+path.relative_to(ROOT).as_posix().removesuffix('index.html'), sitemap)
            self.assertIn(f'../accountability/{language}/index.html', (ROOT/f'essays/{language}/index.html').read_text())
        self.assertIn('Eight languages', (ROOT/'essays/accountability/index.html').read_text())


if __name__ == '__main__':
    unittest.main()
