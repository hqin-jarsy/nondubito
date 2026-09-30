#!/usr/bin/env python3
"""Read-only coverage, source-protection and rendering checks for all 115 texts."""
import html
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

import build_economy_full_editions as build
from test_daodejing_sources import Page


class EconomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(build.RECEIPT.read_text())
        cls.copies = build.manuscripts()
        cls.outputs = build.outputs()

    def test_all_115_full_manuscripts(self):
        self.assertEqual(len(self.copies), 115)
        self.assertEqual(len(self.receipt['archives']), 23)
        for key, copy in self.copies.items():
            with self.subTest(key=key):
                text = (build.DATA/f'{key}.md').read_text()
                self.assertGreater(len(text), 15000)
                self.assertEqual(len(copy['headings']), 8)
                self.assertEqual(copy['body'].count('<p>'), sum(copy['paragraphs_by_section']))
                self.assertTrue(text.rstrip().endswith(build.REFRAINS[key.split('.')[1]]))

    def test_protected_source_and_other_language_files(self):
        for rel, expected in self.receipt['protected_files'].items():
            with self.subTest(path=rel):
                self.assertEqual(build.digest((build.ROOT/rel).read_bytes()), expected)

    def test_outputs_are_current(self):
        self.assertEqual(len(self.outputs), 120)
        for path, expected in self.outputs.items():
            with self.subTest(path=path):
                self.assertEqual(path.read_text(), expected)

    def test_exact_rendered_paragraphs_and_sections(self):
        for key, copy in self.copies.items():
            ep, lang = key.split('.')
            page = Page((build.SERIES/lang/f'{ep}.html').read_text())
            expected = Page(copy['body'])
            body = next(n for n in page.nodes if n.has_class('economy-full'))
            with self.subTest(key=key):
                self.assertEqual([n.text() for n in body.descendants('p')], [n.text() for n in expected.nodes if n.tag == 'p'])
                self.assertEqual([n.text() for n in body.descendants('h2')], copy['headings'])
                self.assertEqual([n.text() for n in page.nodes if n.tag == 'h1'], [copy['title']])
                self.assertEqual(sum(n.has_class('economy-full') for n in page.nodes), 1)
                self.assertEqual(sum(n.has_class('source-note') for n in page.nodes), 1)

    def test_links_canonical_and_unique_ids(self):
        for path, source in self.outputs.items():
            page = Page(source)
            ids = [n.attrs['id'] for n in page.nodes if 'id' in n.attrs]
            with self.subTest(path=path):
                self.assertEqual(len(ids), len(set(ids)))
                canonicals = [n.attrs.get('href') for n in page.nodes if n.tag == 'link' and n.attrs.get('rel') == 'canonical']
                canonical_path = path.relative_to(build.ROOT).as_posix()
                if path.name == 'index.html': canonical_path = canonical_path.removesuffix('index.html')
                self.assertEqual(canonicals, ['https://nondubito.net/'+canonical_path])
                for node in page.nodes:
                    if node.tag != 'a': continue
                    href = node.attrs.get('href', '')
                    url = urlsplit(href)
                    if url.scheme or url.netloc: continue
                    target = (build.ROOT/unquote(url.path).lstrip('/') if url.path.startswith('/') else path.parent/unquote(url.path)) if url.path else path
                    self.assertTrue(target.exists(), (path, href))
                    if url.fragment and target == path:
                        self.assertIn(unquote(url.fragment), ids)

    def test_index_and_neighbor_titles(self):
        for lang in build.LANGS:
            for name in ('index', *build.EPISODES):
                page = Page((build.SERIES/lang/f'{name}.html').read_text())
                for anchor in [n for n in page.nodes if n.tag == 'a']:
                    match = re.fullmatch(r'(ep\d{2})\.html', anchor.attrs.get('href', ''))
                    if not match: continue
                    titles = [n.text() for n in anchor.descendants() if n.has_class('nav-title') or n.has_class('entry-title')]
                    if titles:
                        self.assertEqual(titles, [self.copies[f'{match[1]}.{lang}']['title']])

    def test_declared_edits_only(self):
        for key, record in self.receipt['manuscripts'].items():
            text = (build.DATA/f'{key}.md').read_text()
            for edit in record['edits']:
                self.assertIn(edit['after'], text, key)
            if key.startswith('ep17.'):
                self.assertIn('war was still in progress', ' '.join(self.receipt['notes']))

    def test_search_titles(self):
        for lang in build.LANGS:
            records = json.loads((build.ROOT/f'data/search/{lang}.json').read_text())['records']
            by_url = {r['u']: r for r in records}
            for ep in build.EPISODES:
                row = by_url[f'essays/economy/{lang}/{ep}.html']
                self.assertEqual(' '.join(self.copies[f'{ep}.{lang}']['title'].split()), ' '.join(row['t'].split()))


if __name__ == '__main__':
    unittest.main()
