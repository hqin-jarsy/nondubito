#!/usr/bin/env python3
"""Regression checks for the staged Great Lives full-text upgrade.

These checks catch dropped sections, stale source revisions, incomplete
Traditional Chinese and accidental synopsis replacement. They cannot assess
literary quality; that still requires reading every edition against its map.
"""
from __future__ import annotations

import copy
import unittest

import build_great_lives_languages as builder


class FullEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = builder.load_copy()
        cls.weil = cls.entries['weil']

    def test_weil_is_reviewed_full_text_in_six_languages(self):
        self.assertEqual(self.weil['edition']['status'], 'full')
        self.assertEqual(set(self.weil['copy']), set(builder.LANGS))
        for lang in builder.LANGS:
            self.assertEqual(len(self.weil['copy'][lang]['sections']), 8)
        builder.validate_full_edition(self.weil)

    def test_synopsis_cannot_replace_reviewed_edition(self):
        broken = copy.deepcopy(self.weil)
        for section in broken['copy']['fr']['sections']:
            section['paragraphs'] = ['Une courte phrase.']
        with self.assertRaisesRegex(ValueError, 'abridgement'):
            builder.validate_full_edition(broken)

    def test_missing_content_topic_is_rejected(self):
        broken = copy.deepcopy(self.weil)
        broken['copy']['de']['sections'][-1]['covers'] = []
        with self.assertRaisesRegex(ValueError, 'content map'):
            builder.validate_full_edition(broken)

    def test_source_change_requires_review(self):
        broken = copy.deepcopy(self.weil)
        broken['edition']['source_sha256']['zh'] = 'stale'
        with self.assertRaisesRegex(ValueError, 'source changed'):
            builder.validate_full_edition(broken)

    def test_traditional_keeps_every_paragraph(self):
        broken = copy.deepcopy(self.weil)
        broken['copy']['zh-hant']['sections'][0]['paragraphs'].pop()
        with self.assertRaisesRegex(ValueError, 'every source section and paragraph'):
            builder.validate_full_edition(broken)

    def test_traditional_keeps_each_sections_paragraphs(self):
        broken = copy.deepcopy(self.weil)
        sections = broken['copy']['zh-hant']['sections']
        sections[1]['paragraphs'].append(sections[0]['paragraphs'].pop())
        with self.assertRaisesRegex(ValueError, 'every source section and paragraph'):
            builder.validate_full_edition(broken)

    def test_legacy_copies_stay_buildable_without_full_claim(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            page = outputs[builder.SERIES / lang / 'weil.html']
            self.assertIn('great-edition-note', page)
            self.assertIn('https://plato.stanford.edu/entries/simone-weil/', page)
        self.assertNotIn('Édition complète', outputs[builder.SERIES / 'fr' / 'index.html'])

    def test_legacy_source_paths_are_preserved(self):
        self.assertEqual(builder.source_path_for('confucius'), builder.ROOT / 'essays/confucius.html')
        self.assertEqual(builder.source_path_for('weil'), builder.SERIES / 'weil.html')
        self.assertIn('href="../../confucius.html"', builder.language_switcher('fr', 'confucius'))
        self.assertIn('href="../weil.html"', builder.language_switcher('fr', 'weil'))


if __name__ == '__main__':
    unittest.main()
