#!/usr/bin/env python3
"""Completeness, reproducibility, discovery and local-link regression checks."""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import markdown
import build_paleontology as p
from build_content_registry import scan_page

class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(); self.tags = []; self.ids = []; self.links = []
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs); self.tags.append((tag, attrs))
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag in ('a', 'link') and 'href' in attrs: self.links.append((tag, attrs))

class Publication(unittest.TestCase):
    def test_hub_groups_match_published_episodes(self):
        for lang in p.LANGS:
            source = p.destination(lang).read_text()
            seen = []
            for first, last in ((1, 8), (9, 13), (14, 18), (19, 23)):
                expected = [n for n in p.PUBLISHED if first <= n <= last]
                section = re.search(r'<section class="published" id="group-' + f'{first:02d}' + r'">(.*?)</section>', source, re.S)
                if not expected:
                    self.assertIsNone(section)
                    continue
                self.assertIsNotNone(section)
                actual = [int(n) for n in re.findall(r'class="essay-card" href="ep(\d+)\.html"', section[1])]
                self.assertEqual(actual, expected)
                seen.extend(actual)
            self.assertEqual(seen, list(p.PUBLISHED))

    def test_optional_afterword(self):
        for lang in p.LANGS:
            hub = p.destination(lang).read_text()
            self.assertIn('id="afterword"', hub)
            self.assertIn('href="afterword.html"', hub)
            self.assertIn('href="afterword.html"', p.destination(lang, 23).read_text())
            final = p.destination(lang, p.AFTERWORD).read_text()
            self.assertIn('href="ep23.html"', final)
            self.assertNotIn('EP24', final)
            self.assertNotIn('ep24.html', hub + final)
            self.assertEqual(len(p.parts(p.AFTERWORD, lang)[1]), 7)

    def test_full_text_and_immutable_sources(self):
        for lang in p.LANGS:
            for ep in p.ARTICLES:
                original = p.original(ep, lang); edited = p.reviewed(ep, lang)
                self.assertEqual(len(re.findall(r'^### ', original, re.M)), 7 if ep == p.AFTERWORD else 8)
                # Ignore trailing blank lines in supplied files, not real paragraphs.
                self.assertEqual(len(re.split(r'\n\s*\n', original.strip())),
                                 len(re.split(r'\n\s*\n', edited.strip())))
                self.assertGreater(len(edited) / len(original), .97)
                # All source paragraphs survive; exact reviewed HTML is embedded intact.
                body = p.parts(ep, lang)[2]
                self.assertIn(body, p.destination(lang, ep).read_text())
                self.assertEqual(body.count('<p>'), markdown.markdown(original).count('<p>'))

    def test_generated_documents_and_links(self):
        paths = list(p.TARGET.rglob('*.html')); self.assertEqual(len(paths), len(p.LANGS) * (len(p.ARTICLES) + 1))
        for lang in p.LANGS:
            for ep in (None, *p.ARTICLES):
                path = p.destination(lang, ep); source = path.read_text(); doc = Document(source)
                self.assertEqual(source, p.hub(lang) if ep is None else p.essay(lang, ep))
                self.assertEqual(sum(t == 'h1' for t,a in doc.tags), 1)
                self.assertEqual(len(doc.ids), len(set(doc.ids)))
                self.assertIn(('html', {'lang':lang, 'data-editions':lang}), doc.tags)
                canonical = [a['href'] for t,a in doc.links if a.get('rel') == 'canonical']
                self.assertEqual(canonical, [p.url(path)])
                alternates = {a['hreflang']:a['href'] for t,a in doc.links if a.get('rel') == 'alternate'}
                self.assertEqual(len(alternates), 9)
                for l in p.LANGS: self.assertEqual(alternates[l], p.url(p.destination(l, ep)))
                schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)[1])
                self.assertEqual(schema['inLanguage'], lang)
                self.assertEqual(schema['datePublished'], p.publication_date(ep))
                self.assertEqual(schema['dateModified'], p.publication_date(ep) if ep else p.DATE)
                if ep:
                    self.assertIn(f'<time datetime="{p.publication_date(ep)}">', source)
                for tag, attrs in doc.links:
                    parsed = urlsplit(attrs['href'])
                    if parsed.scheme or parsed.netloc: continue
                    target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
                    self.assertTrue(target.exists(), (path, attrs))
                    if parsed.fragment and target.suffix == '.html':
                        self.assertIn(parsed.fragment, Document(target.read_text()).ids)
                record = scan_page(p.ROOT, path)
                self.assertEqual(record['languages'], [lang])
                self.assertEqual(record['series'], 'paleontology')
                self.assertEqual(record['domain'], 'history')

    def test_discovery(self):
        manifest = json.loads((p.ROOT/'data/search-index.json').read_text())
        total = 0
        for lang in p.LANGS:
            chunk = json.loads((p.ROOT/f'data/search/{lang.lower()}.json').read_text())
            records = [r for r in chunk['records'] if r['u'].startswith('essays/paleontology/')]
            self.assertEqual(len(records), len(p.ARTICLES) + 1)
            self.assertEqual({r['u'] for r in records}, {str(p.destination(lang,n).relative_to(p.ROOT)) for n in (None,*p.ARTICLES)})
            self.assertTrue(all(r['s'] == 'paleontology' and r['d'] == 'history' for r in records))
            self.assertEqual(manifest['languages'][lang]['count'], len(chunk['records']))
            total += len(chunk['records'])
        # Existing manifest counts unique source records, not all language copies.
        self.assertGreaterEqual(total, manifest['record_count'])
        entries = [u.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text for u in ET.parse(p.ROOT/'sitemap.xml').getroot()]
        self.assertEqual(len(entries), len(set(entries)))
        self.assertEqual(sum('/essays/paleontology/' in u for u in entries), len(p.LANGS) * (len(p.ARTICLES) + 1))

if __name__ == '__main__':
    unittest.main()
