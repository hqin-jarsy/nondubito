#!/usr/bin/env python3
"""Regression checks for the staged Great Lives full-text upgrade.

These checks catch dropped sections, stale source revisions, incomplete
Traditional Chinese and accidental synopsis replacement. They cannot assess
literary quality; that still requires reading every edition against its map.
"""
from __future__ import annotations

import copy
import unittest
from unittest.mock import Mock, patch

import build_great_lives_languages as builder


class FullEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = builder.load_copy()
        cls.weil = cls.entries['weil']

    def test_intentional_line_breaks_survive_without_allowing_html(self):
        self.assertEqual(builder.paragraph_html('一行\n<另一行>'), '<p>一行<br>&lt;另一行&gt;</p>')

    def test_weil_is_reviewed_full_text_in_six_languages(self):
        self.assertEqual(self.weil['edition']['status'], 'full')
        self.assertEqual(set(self.weil['copy']), set(builder.LANGS))
        for lang in builder.LANGS:
            self.assertEqual(len(self.weil['copy'][lang]['sections']), 8)
        builder.validate_full_edition(self.weil)

    def test_first_batch_has_complete_editions(self):
        for slug, number, sections in (('laozi', 1, 9), ('confucius', 2, 8), ('socrates', 3, 8)):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], 1)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), sections)
                builder.validate_full_edition(entry)

    def test_first_batch_navigation_uses_existing_source_urls(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug, source in (('laozi', '../laozi.html'), ('confucius', '../../confucius.html'), ('socrates', '../../socrates.html')):
                page = outputs[builder.SERIES / lang / (slug + '.html')]
                self.assertIn(f'<a href="{source}">EN / 中文</a>', page)
                self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
            laozi = outputs[builder.SERIES / lang / 'laozi.html']
            self.assertNotIn('href="king.html"', laozi)
            self.assertIn('href="confucius.html"', laozi)
            socrates = outputs[builder.SERIES / lang / 'socrates.html']
            self.assertIn('href="confucius.html"', socrates)
            self.assertIn('href="wangyangming.html"', socrates)

    def test_classical_chong_is_not_converted_to_collision(self):
        traditional = self.entries['laozi']['copy']['zh-hant']
        body = '\n'.join(p for s in traditional['sections'] for p in s['paragraphs'])
        self.assertIn('萬物負陰而抱陽，沖氣以為和', body)
        self.assertNotIn('衝氣', body)

    def test_traditional_context_sensitive_spellings_are_preserved(self):
        for slug in ('laozi', 'confucius', 'socrates'):
            traditional = self.entries[slug]['copy']['zh-hant']
            body = '\n'.join(p for s in traditional['sections'] for p in s['paragraphs'])
            self.assertNotIn('尼採', body)
            self.assertNotIn('從頭髮明', body)
            if slug == 'confucius':
                self.assertIn('從頭發明', body)
                self.assertIn('郁郁乎文哉', body)
                self.assertNotIn('鬱鬱乎', body)

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

    def test_early_narratives_exclude_signatures_and_notes(self):
        for slug, expected_sections in (('laozi', 9), ('confucius', 8), ('socrates', 8)):
            for lang in ('zh', 'en'):
                with self.subTest(slug=slug, lang=lang):
                    body = builder.source_body(slug, lang)
                    self.assertTrue(body.startswith('<h2'))
                    self.assertEqual(body.count('<h2'), expected_sections)
                    self.assertNotIn('<h2>Notes</h2>', body)
                    self.assertNotIn('<h2>注释</h2>', body)
                    self.assertNotIn('essay-body', body)

    def test_nested_divs_do_not_end_body_early(self):
        text = ('<div class="lang-zh essay-body"><p>Signature</p>'
                '<h2>一</h2><div><p>A</p></div><p>B</p>'
                '<h2>注释</h2><p>Notes</p></div>'
                '<div class="essay-body lang-en"><h2>One</h2>'
                '<p>Not Chinese</p><h2>Notes</h2></div>')
        path = Mock()
        path.read_text.return_value = text
        with patch.object(builder, 'source_path_for', return_value=path):
            self.assertEqual(builder.source_body('test', 'zh'), '<h2>一</h2><div><p>A</p></div><p>B</p>')

    def test_missing_note_boundary_cannot_consume_next_language(self):
        text = ('<div class="essay-body lang-zh"><h2>一</h2><p>A</p></div>'
                '<div class="essay-body lang-en"><h2>One</h2>'
                '<p>B</p><h2>Notes</h2></div>')
        path = Mock()
        path.read_text.return_value = text
        with patch.object(builder, 'source_path_for', return_value=path):
            with self.assertRaisesRegex(ValueError, 'source-note boundary'):
                builder.source_body('test', 'zh')


if __name__ == '__main__':
    unittest.main()
