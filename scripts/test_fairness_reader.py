#!/usr/bin/env python3
"""Checks for the read and edited Fairness essays; not a substitute for reading."""
import copy
import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from build_reader_series import ROOT, registry, load_items, render, landing, ReaderTraditionalConverter
from build_content_registry import scan_page
from prepare_action_sources import Document, one, Node
from refresh_reader_discovery import render as discovery


def body_sha(body):
    return hashlib.sha256(json.dumps(body, ensure_ascii=False).encode()).hexdigest()


class FairnessPublication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.series = next(s for s in registry() if s['slug'] == 'fairness')
        cls.items = load_items(cls.series)
        cls.receipt = json.loads((ROOT/'data/fairness/publication.json').read_text())
        cls.pages = render('fairness')

    def test_sources_and_reviewed_bodies(self):
        stems = ['prequel', *map(str, range(1, 11)), '0']
        self.assertEqual(len(self.items), 12)
        for item, stem, source in zip(self.items, stems, self.receipt['sources']):
            self.assertEqual(item['source_url'], f'https://self-as-an-end.net/papers/sae-fairness-theory-{stem}.html')
            self.assertEqual(source['sha256'], item['editorial']['source_sha256'])
            self.assertEqual(item['editorial']['source_read_ranges'], [[0, source['read_blocks']]])
            # This remains portable when the author's separate checkout is absent.
            original = Path(item['editorial']['source_path'])
            if original.is_file():
                self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(), source['sha256'])
            self.assertEqual(item['review']['status'], 'approved')
            for language in ('zh', 'hant', 'en'):
                digest = body_sha(item['body_'+language])
                self.assertEqual(digest, item['review']['edition_sha256'][language])
                self.assertEqual(digest, self.receipt['editorial_review']['edition_sha256'][item['slug']][language])
            self.assertEqual(len(item['body_zh']), len(item['body_hant']))

    def test_complete_rendered_text_and_language_controls(self):
        self.assertEqual(len(self.pages), 13)
        for path, text in self.pages.items():
            self.assertEqual(path.read_text(), text)
            document = Document(text)
            controls = {n.attrs['data-set-language'] for n in document.root.walk() if 'data-set-language' in n.attrs}
            self.assertEqual(controls, {'en', 'zh', 'zh-hant'})
            if path.stem == 'index':
                continue
            item = self.items[int(path.stem[2:])-1]
            for language, native in (('en', 'en'), ('zh', 'zh-Hans'), ('hant', 'zh-Hant')):
                body = one(document.root.walk(), lambda n:n.has('essay-body', 'lw-prose', 'lang-'+language), path.name)
                self.assertEqual(body.attrs['lang'], native)
                blocks = [n for n in body.children if isinstance(n, Node)]
                actual = [('## ' if n.tag=='h2' else '')+n.text() for n in blocks]
                self.assertEqual(actual, item['body_'+language])
                self.assertTrue(all(n.tag in ('p','h2') for n in blocks))
                self.assertNotRegex(body.text(), r'\b\d{2}DD\b|\b[FTVH]\d+\b|ψ|ρ|TODO')

    def test_six_five_one_route_and_optional_finish(self):
        document = Document((ROOT/'essays/fairness/index.html').read_text())
        nav = one(document.root.walk(), lambda n:n.tag=='nav' and n.has('sae-jump'), 'Three reading stages')
        self.assertEqual([n.attrs['href'] for n in nav.walk() if n.tag=='a'],
                         ['#learn-to-see', '#use-the-tools', '#further-reading'])
        for group, count in zip(self.series['reading_groups'], (6,5,1)):
            section = one(document.root.walk(), lambda n:n.tag=='section' and n.attrs.get('id')==group['id'], group['id'])
            cards = [n for n in section.walk() if n.tag=='a' and n.has('lw-card')]
            self.assertEqual(len(cards), count)
            self.assertEqual([n.attrs['href'] for n in cards], [f'ep{i:02d}.html' for i in group['episodes']])
            for card in cards:
                self.assertEqual(sum(n.tag=='h3' for n in card.walk()), 3)
                self.assertFalse(any(n.tag=='h2' for n in card.walk()))
        self.assertIn('可选', self.items[-1]['deck_zh'])
        self.assertIn('optional', '\n'.join(self.items[-2]['body_en']))
        self.assertIn('普通阅读', '\n'.join(self.items[-2]['body_zh']))

    def test_invalid_grouping_fails_instead_of_hiding_essays(self):
        converter = ReaderTraditionalConverter()
        try:
            broken = copy.deepcopy(self.series)
            broken['reading_groups'][0]['episodes'].append(6)
            with self.assertRaises(AssertionError):
                landing(broken, self.items, converter)
            broken = copy.deepcopy(self.series)
            broken['reading_groups'][2]['episodes'] = []
            with self.assertRaises(AssertionError):
                landing(broken, self.items, converter)
        finally:
            converter.close()

    def test_editorial_boundary_regressions(self):
        # Protect reviewed wording from accidental future compression or drift.
        opening = '\n'.join(self.items[0]['body_en'])
        self.assertIn('Does not count as fair is not automatically the verdict is unfair.', opening)
        self.assertIn('Establishing neither is already an answer.', opening)
        disability = '\n'.join(self.items[6]['body_en'])
        self.assertIn('reasonable accommodation in individual circumstances', disability)
        algorithms = '\n'.join(self.items[9]['body_en'])
        self.assertIn('calibration within groups', algorithms)
        self.assertIn('Threshold-level results concern different quantities', algorithms)
        self.assertIn('not interchangeable', algorithms)
        closing = '\n'.join(self.items[10]['body_en'])
        self.assertIn('something must count as unfair', closing)
        self.assertNotIn('unfairness cannot be excluded', closing)
        self.assertIn('Unanswered is not neither, and not permission.', closing)
        tradition = '\n'.join(self.items[11]['body_en'])
        self.assertIn('comparisons below remain provisional', tradition)
        self.assertIn('not a quotation from its author', tradition)
        self.assertIn('He does not demand equal final results', tradition)

    def test_scoped_discovery_is_reproducible_and_localized(self):
        for path, expected in discovery('fairness').items():
            self.assertEqual(path.read_text(), expected, str(path))
        for language, key in (('en','en'), ('zh-hans','zh'), ('zh-hant','hant')):
            records = json.loads((ROOT/f'data/search/{language}.json').read_text())['records']
            by_url = {r['u']:r for r in records}
            for path in self.pages:
                record = by_url[path.relative_to(ROOT).as_posix()]
                self.assertEqual(record['d'], 'sae-philosophy')
                if path.stem != 'index':
                    item = self.items[int(path.stem[2:])-1]
                    self.assertEqual(record['x'], item['deck_'+key] if key in ('en','zh') else converted_hant(item['deck_zh']))
                self.assertEqual(scan_page(ROOT,path)['domain'], 'sae-philosophy')
        sitemap = {u.find('{*}loc').text:u.find('{*}lastmod').text for u in ET.parse(ROOT/'sitemap.xml').getroot()}
        for path in self.pages:
            self.assertEqual(sitemap['https://nondubito.net/'+path.relative_to(ROOT).as_posix().removesuffix('index.html')], '2026-11-23')


def converted_hant(text):
    converter = ReaderTraditionalConverter()
    try:
        return converter.convert(text)
    finally:
        converter.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
