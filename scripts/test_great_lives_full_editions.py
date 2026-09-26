#!/usr/bin/env python3
"""Regression checks for the staged Great Lives full-text upgrade.

These checks catch dropped sections, stale source revisions, incomplete
Traditional Chinese and accidental synopsis replacement. They cannot assess
literary quality; that still requires reading every edition against its map.
"""
from __future__ import annotations

import copy
import hashlib
import html
import json
import re
import unittest
from unittest.mock import Mock, patch
from urllib.parse import urlsplit, unquote

import build_great_lives_languages as builder


class FullEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = builder.load_copy()
        cls.weil = cls.entries['weil']

    def test_intentional_line_breaks_survive_without_allowing_html(self):
        self.assertEqual(builder.paragraph_html('一行\n<另一行>'), '<p>一行<br>&lt;另一行&gt;</p>')

    def test_subheadings_preserve_order_without_changing_paragraphs(self):
        section = {'heading': 'One', 'paragraphs': ['A', 'B'],
                   'subheadings': [{'before': 1, 'text': 'Two <three>'}]}
        rendered = builder.section_html(section)
        self.assertEqual(rendered, '<section><h2>One</h2><p>A</p><h3>Two &lt;three&gt;</h3><p>B</p></section>')

    def test_out_of_range_subheadings_are_rejected(self):
        for before in (-1, 1, '0', True):
            with self.subTest(before=before):
                section = {'heading': 'One', 'paragraphs': ['A'],
                           'subheadings': [{'before': before, 'text': 'Two'}]}
                with self.assertRaisesRegex(ValueError, 'subheading'):
                    builder.section_html(section)

    def test_duplicate_or_reversed_subheadings_are_rejected(self):
        for indexes in ((0, 0), (1, 0)):
            with self.subTest(indexes=indexes):
                section = {'heading': 'One', 'paragraphs': ['A', 'B'],
                           'subheadings': [{'before': index, 'text': 'Two'} for index in indexes]}
                with self.assertRaisesRegex(ValueError, 'subheading'):
                    builder.section_html(section)

    def test_source_labels_can_be_localized_with_a_safe_fallback(self):
        entry = copy.deepcopy(self.weil)
        entry['sources'][0]['titles'] = {'fr': 'Une source <annotée>'}
        order = builder.canonical_order()
        available = {item['slug'] for item in order}
        french = builder.article_html('fr', entry, order, available, self.entries)
        german = builder.article_html('de', entry, order, available, self.entries)
        self.assertIn('>Une source &lt;annotée&gt;</a>', french)
        self.assertIn('>' + builder.esc(entry['sources'][0]['title']) + '</a>', german)

    def test_kant_keeps_internal_reading_landmarks(self):
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                sections = self.entries['kant']['copy'][lang]['sections']
                self.assertEqual(sum(len(s.get('subheadings', [])) for s in sections), 11)
                for section in sections:
                    builder.validate_subheadings(section)

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

    def test_second_batch_has_complete_editions(self):
        for slug, number, sections in (('wangyangming', 4, 10), ('kant', 5, 10), ('nietzsche', 6, 8)):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], 1)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), sections)
                builder.validate_full_edition(entry)

    def test_full_editions_have_no_unrendered_markdown_footnotes(self):
        for slug, entry in self.entries.items():
            if entry.get('edition', {}).get('status') != 'full':
                continue
            for lang in builder.LANGS:
                with self.subTest(slug=slug, lang=lang):
                    edition = self.entries[slug]['copy'][lang]
                    text = '\n'.join(
                        paragraph for section in edition['sections']
                        for paragraph in section['paragraphs']
                    ) + '\n' + '\n'.join(edition['notes'])
                    self.assertNotRegex(text, r'\[\^[^\]]+\]')

    def test_second_batch_source_and_neighbour_links(self):
        outputs = builder.build()
        cases = (
            ('wangyangming', '../../wangyangming.html', 'socrates', 'kant'),
            ('kant', '../kant.html', 'wangyangming', 'nietzsche'),
            ('nietzsche', '../../nietzsche.html', 'kant', 'zhuangzi'),
        )
        for lang in builder.LANGS:
            for slug, source, previous, following in cases:
                with self.subTest(slug=slug, lang=lang):
                    page = outputs[builder.SERIES / lang / (slug + '.html')]
                    self.assertIn(f'<a href="{source}">EN / 中文</a>', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
                    self.assertIn(f'href="{previous}.html"', page)
                    self.assertIn(f'href="{following}.html"', page)

    def test_second_batch_local_links_resolve(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug in ('wangyangming', 'kant', 'nietzsche'):
                path = builder.SERIES / lang / (slug + '.html')
                for href in re.findall(r'href="([^"]+)"', outputs[path]):
                    url = urlsplit(html.unescape(href))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (path.parent / unquote(url.path)).resolve()
                    with self.subTest(page=str(path), href=href):
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_zhuangzi_links_back_with_current_nietzsche_title(self):
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                page = (builder.SERIES / lang / 'zhuangzi.html').read_text(encoding='utf-8')
                link = re.search(r'<a href="nietzsche.html">(.*?)</a>', page, re.S)
                self.assertIsNotNone(link)
                self.assertIn(builder.esc(self.entries['nietzsche']['copy'][lang]['title']), link.group(1))

    def test_third_batch_has_complete_editions(self):
        for slug, number, sections in (('zhuangzi', 7, 8), ('buddha', 8, 9), ('jesus', 9, 8)):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], 1)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), sections)
                builder.validate_full_edition(entry)

    def test_third_batch_source_and_neighbour_links(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug, previous, following in (
                ('zhuangzi', 'nietzsche', 'buddha'),
                ('buddha', 'zhuangzi', 'jesus'),
                ('jesus', 'buddha', 'godel'),
            ):
                with self.subTest(slug=slug, lang=lang):
                    page = outputs[builder.SERIES / lang / (slug + '.html')]
                    self.assertIn(f'<a href="../{slug}.html">EN / 中文</a>', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
                    self.assertIn(f'href="{previous}.html"', page)
                    self.assertIn(f'href="{following}.html"', page)

    def test_third_batch_local_links_resolve(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug in ('zhuangzi', 'buddha', 'jesus'):
                path = builder.SERIES / lang / (slug + '.html')
                for href in re.findall(r'href="([^"]+)"', outputs[path]):
                    url = urlsplit(html.unescape(href))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (path.parent / unquote(url.path)).resolve()
                    with self.subTest(page=str(path), href=href):
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_third_batch_narratives_exclude_editorial_notes(self):
        for slug, sections in (('zhuangzi', 8), ('buddha', 9), ('jesus', 8)):
            for lang in ('zh', 'en'):
                with self.subTest(slug=slug, lang=lang):
                    body = builder.source_body(slug, lang)
                    self.assertEqual(body.count('<h2'), sections)
                    self.assertNotIn('<h2>Notes</h2>', body)
                    self.assertNotIn('<h2>注释</h2>', body)

    def test_first_movement_is_fully_upgraded(self):
        first = [item for item in builder.canonical_order() if item['number'] <= 9]
        self.assertEqual(len(first), 9)
        self.assertTrue(all(self.entries[item['slug']]['edition']['status'] == 'full' for item in first))
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full' for e in self.entries.values()), 10)

    def test_fourth_batch_has_complete_editions(self):
        for slug, number, sections in (('godel', 10, 7), ('einstein', 11, 6), ('dufu', 12, 9)):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], 2)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), sections)
                builder.validate_full_edition(entry)

    def test_fourth_batch_source_and_neighbour_links(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug, previous, following in (
                ('godel', 'jesus', 'einstein'),
                ('einstein', 'godel', 'dufu'),
                ('dufu', 'einstein', 'qinshihuang'),
            ):
                with self.subTest(slug=slug, lang=lang):
                    page = outputs[builder.SERIES / lang / (slug + '.html')]
                    self.assertIn(f'<a href="../{slug}.html">EN / 中文</a>', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
                    for neighbour in (previous, following):
                        link = re.search(r'<a href="' + neighbour + r'\.html">(.*?)</a>', page, re.S)
                        self.assertIsNotNone(link)
                        self.assertIn(builder.esc(self.entries[neighbour]['copy'][lang]['title']), link.group(1))

    def test_fourth_batch_local_links_resolve(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug in ('godel', 'einstein', 'dufu'):
                path = builder.SERIES / lang / (slug + '.html')
                for href in re.findall(r'href="([^"]+)"', outputs[path]):
                    url = urlsplit(html.unescape(href))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (path.parent / unquote(url.path)).resolve()
                    with self.subTest(page=str(path), href=href):
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_fourth_batch_narratives_exclude_editorial_notes(self):
        for slug, sections in (('godel', 7), ('einstein', 6), ('dufu', 9)):
            for lang in ('zh', 'en'):
                with self.subTest(slug=slug, lang=lang):
                    body = builder.source_body(slug, lang)
                    self.assertEqual(body.count('<h2'), sections)
                    self.assertNotIn('<h2>Notes</h2>', body)
                    self.assertNotIn('<h2>注释</h2>', body)
                    self.assertNotIn('essay-footer-note', body)

    def test_first_twelve_and_weil_have_full_editions(self):
        required = [item['slug'] for item in builder.canonical_order() if item['number'] <= 12] + ['weil']
        self.assertEqual(len(required), 13)
        self.assertTrue(all(self.entries[slug]['edition']['status'] == 'full' for slug in required))

    def test_fifth_batch_has_complete_editions(self):
        for slug, number in (('qinshihuang', 13), ('washington', 14), ('alexander', 15)):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], 2)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), 8)
                builder.validate_full_edition(entry)

    def test_fifth_batch_source_and_neighbour_links(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug, previous, following in (
                ('qinshihuang', 'dufu', 'washington'),
                ('washington', 'qinshihuang', 'alexander'),
                ('alexander', 'washington', 'darwin'),
            ):
                with self.subTest(slug=slug, lang=lang):
                    page = outputs[builder.SERIES / lang / (slug + '.html')]
                    self.assertIn(f'<a href="../{slug}.html">EN / 中文</a>', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
                    for neighbour in (previous, following):
                        link = re.search(r'<a href="' + neighbour + r'\.html">(.*?)</a>', page, re.S)
                        self.assertIsNotNone(link)
                        self.assertIn(builder.esc(self.entries[neighbour]['copy'][lang]['title']), link.group(1))

    def test_fifth_batch_local_links_resolve(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug in ('qinshihuang', 'washington', 'alexander'):
                path = builder.SERIES / lang / (slug + '.html')
                for href in re.findall(r'href="([^"]+)"', outputs[path]):
                    url = urlsplit(html.unescape(href))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (path.parent / unquote(url.path)).resolve()
                    with self.subTest(page=str(path), href=href):
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_fifth_batch_narratives_exclude_editorial_notes(self):
        for slug in ('qinshihuang', 'washington', 'alexander'):
            for lang in ('zh', 'en'):
                with self.subTest(slug=slug, lang=lang):
                    body = builder.source_body(slug, lang)
                    self.assertEqual(body.count('<h2'), 8)
                    self.assertNotIn('<h2>Notes</h2>', body)
                    self.assertNotIn('<h2>注释</h2>', body)
                    self.assertNotIn('essay-footer-note', body)

    def test_first_fifteen_and_weil_have_full_editions(self):
        required = [item['slug'] for item in builder.canonical_order() if item['number'] <= 15] + ['weil']
        self.assertEqual(len(required), 16)
        self.assertTrue(all(self.entries[slug]['edition']['status'] == 'full' for slug in required))

    def test_alexander_traditional_distinguishes_campaigns_and_names(self):
        edition = self.entries['alexander']['copy']['zh-hant']
        text = '\n'.join(p for s in edition['sections'] for p in s['paragraphs'])
        text += '\n' + '\n'.join(edition['notes'])
        for correct in ('遠征', '東征', '另闢道路', '反覆', '亞里士多德', '阿里安'):
            self.assertIn(correct, text)
        for incorrect in ('遠徵', '東徵', '另辟道路', '反復', '亞裡士多德', '阿裡安', '場景里', '史料里', '史詩里'):
            self.assertNotIn(incorrect, text)

    def test_sixth_batch_has_complete_editions(self):
        for slug, number, sections in (('darwin', 16, 9), ('newton', 17, 8), ('bach', 18, 8)):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], 2)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), sections)
                builder.validate_full_edition(entry)

    def test_sixth_batch_source_and_neighbour_links(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug, previous, following in (
                ('darwin', 'alexander', 'newton'),
                ('newton', 'darwin', 'bach'),
                ('bach', 'newton', 'beethoven'),
            ):
                with self.subTest(slug=slug, lang=lang):
                    page = outputs[builder.SERIES / lang / (slug + '.html')]
                    self.assertIn(f'<a href="../{slug}.html">EN / 中文</a>', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
                    for neighbour in (previous, following):
                        link = re.search(r'<a href="' + neighbour + r'\.html">(.*?)</a>', page, re.S)
                        self.assertIsNotNone(link)
                        self.assertIn(builder.esc(self.entries[neighbour]['copy'][lang]['title']), link.group(1))

    def test_sixth_batch_local_links_resolve(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug in ('darwin', 'newton', 'bach'):
                path = builder.SERIES / lang / (slug + '.html')
                for href in re.findall(r'href="([^"]+)"', outputs[path]):
                    url = urlsplit(html.unescape(href))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (path.parent / unquote(url.path)).resolve()
                    with self.subTest(page=str(path), href=href):
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_sixth_batch_narratives_exclude_editorial_notes(self):
        for slug, sections in (('darwin', 9), ('newton', 8), ('bach', 8)):
            for lang in ('zh', 'en'):
                with self.subTest(slug=slug, lang=lang):
                    body = builder.source_body(slug, lang)
                    self.assertEqual(body.count('<h2'), sections)
                    self.assertNotIn('<h2>Notes</h2>', body)
                    self.assertNotIn('<h2>注释</h2>', body)
                    self.assertNotIn('essay-footer-note', body)

    def test_first_eighteen_and_weil_have_full_editions(self):
        required = [item['slug'] for item in builder.canonical_order() if item['number'] <= 18] + ['weil']
        self.assertEqual(len(required), 19)
        self.assertTrue(all(self.entries[slug]['edition']['status'] == 'full' for slug in required))

    def test_sixth_batch_sources_are_localized_in_every_edition(self):
        for slug in ('darwin', 'newton', 'bach'):
            for source in self.entries[slug]['sources']:
                with self.subTest(slug=slug, source=source['url']):
                    self.assertTrue(source['url'].startswith('https://'))
                    for lang in builder.LANGS:
                        self.assertTrue(source['titles'].get(lang, '').strip())

    def test_seventh_batch_has_complete_editions(self):
        for slug, number, sections in (('beethoven', 19, 8), ('simaqian', 20, 9), ('libai', 21, 8)):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], 2)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), sections)
                builder.validate_full_edition(entry)

    def test_seventh_batch_source_and_neighbour_links(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug, previous, following in (
                ('beethoven', 'bach', 'simaqian'),
                ('simaqian', 'beethoven', 'libai'),
                ('libai', 'simaqian', 'rumi'),
            ):
                with self.subTest(slug=slug, lang=lang):
                    page = outputs[builder.SERIES / lang / (slug + '.html')]
                    self.assertIn(f'<a href="../{slug}.html">EN / 中文</a>', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
                    for neighbour in (previous, following):
                        link = re.search(r'<a href="' + neighbour + r'\.html">(.*?)</a>', page, re.S)
                        self.assertIsNotNone(link)
                        self.assertIn(builder.esc(self.entries[neighbour]['copy'][lang]['title']), link.group(1))

    def test_seventh_batch_local_links_resolve(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug in ('beethoven', 'simaqian', 'libai'):
                path = builder.SERIES / lang / (slug + '.html')
                for href in re.findall(r'href="([^"]+)"', outputs[path]):
                    url = urlsplit(html.unescape(href))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (path.parent / unquote(url.path)).resolve()
                    with self.subTest(page=str(path), href=href):
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_seventh_batch_narratives_exclude_editorial_notes(self):
        for slug, sections in (('beethoven', 8), ('simaqian', 9), ('libai', 8)):
            for lang in ('zh', 'en'):
                with self.subTest(slug=slug, lang=lang):
                    body = builder.source_body(slug, lang)
                    self.assertEqual(body.count('<h2'), sections)
                    self.assertNotIn('<h2>Notes</h2>', body)
                    self.assertNotIn('<h2>注释</h2>', body)
                    self.assertNotIn('essay-footer-note', body)

    def test_first_twenty_one_and_weil_have_full_editions(self):
        required = [item['slug'] for item in builder.canonical_order() if item['number'] <= 21] + ['weil']
        self.assertEqual(len(required), 22)
        self.assertTrue(all(self.entries[slug]['edition']['status'] == 'full' for slug in required))

    def test_seventh_batch_sources_are_localized_in_every_edition(self):
        for slug in ('beethoven', 'simaqian', 'libai'):
            for source in self.entries[slug]['sources']:
                with self.subTest(slug=slug, source=source['url']):
                    self.assertTrue(source['url'].startswith('https://'))
                    for lang in builder.LANGS:
                        self.assertTrue(source['titles'].get(lang, '').strip())

    def test_libai_keeps_bring_in_the_wine_in_verse(self):
        # Twelve long lines in the Chinese edition, with complete banquet,
        # money, horse and coat passages. Other languages may split further.
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                section = self.entries['libai']['copy'][lang]['sections'][3]
                verse_lines = sum(p.count('\n') + 1 for p in section['paragraphs'] if '\n' in p)
                self.assertGreaterEqual(verse_lines, 12)
        traditional = '\n'.join(self.entries['libai']['copy']['zh-hant']['sections'][3]['paragraphs'])
        for phrase in ('陳王昔時宴平樂', '主人何為言少錢', '五花馬', '千金裘', '與爾同銷萬古愁'):
            self.assertIn(phrase, traditional)

    def test_beethoven_keeps_ode_to_joy_as_verse(self):
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                section = self.entries['beethoven']['copy'][lang]['sections'][6]
                self.assertTrue(any(p.count('\n') >= 5 for p in section['paragraphs']))

    def test_libai_traditional_uses_context_sensitive_poem_characters(self):
        body = '\n'.join(p for s in self.entries['libai']['copy']['zh-hant']['sections'] for p in s['paragraphs'])
        for correct in ('悲白髮', '還復來', '不復回', '鐘鼓饌玉'):
            self.assertIn(correct, body)
        for incorrect in ('悲白發', '還複來', '還覆來', '不複回', '不覆回', '鍾鼓饌玉', '楊萬裡'):
            self.assertNotIn(incorrect, body)

    def test_eighth_batch_has_complete_editions(self):
        for slug, number, movement, sections in (
            ('rumi', 22, 2, 9), ('davinci', 23, 2, 8), ('freud', 24, 3, 9),
        ):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], movement)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), sections)
                builder.validate_full_edition(entry)

    def test_eighth_batch_source_and_neighbour_links(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug, previous, following in (
                ('rumi', 'libai', 'davinci'),
                ('davinci', 'rumi', 'freud'),
                ('freud', 'davinci', 'lacan'),
            ):
                with self.subTest(slug=slug, lang=lang):
                    page = outputs[builder.SERIES / lang / (slug + '.html')]
                    self.assertIn(f'<a href="../{slug}.html">EN / 中文</a>', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
                    for neighbour in (previous, following):
                        link = re.search(r'<a href="' + neighbour + r'\.html">(.*?)</a>', page, re.S)
                        self.assertIsNotNone(link)
                        self.assertIn(builder.esc(self.entries[neighbour]['copy'][lang]['title']), link.group(1))

    def test_eighth_batch_local_links_resolve(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug in ('rumi', 'davinci', 'freud'):
                path = builder.SERIES / lang / (slug + '.html')
                for href in re.findall(r'href="([^"]+)"', outputs[path]):
                    url = urlsplit(html.unescape(href))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (path.parent / unquote(url.path)).resolve()
                    with self.subTest(page=str(path), href=href):
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_eighth_batch_narratives_exclude_editorial_notes(self):
        for slug, sections in (('rumi', 9), ('davinci', 8), ('freud', 9)):
            for lang in ('zh', 'en'):
                with self.subTest(slug=slug, lang=lang):
                    body = builder.source_body(slug, lang)
                    self.assertEqual(body.count('<h2'), sections)
                    self.assertNotIn('essay-footer-note', body)
                    self.assertNotIn('<h2>Notes</h2>', body)
                    self.assertNotIn('<h2>注释</h2>', body)

    def test_first_twenty_four_and_weil_have_full_editions(self):
        required = [item['slug'] for item in builder.canonical_order() if item['number'] <= 24] + ['weil']
        self.assertEqual(len(required), 25)
        self.assertTrue(all(self.entries[slug]['edition']['status'] == 'full' for slug in required))

    def test_eighth_batch_sources_are_localized_in_every_edition(self):
        for slug in ('rumi', 'davinci', 'freud'):
            for source in self.entries[slug]['sources']:
                with self.subTest(slug=slug, source=source['url']):
                    self.assertTrue(source['url'].startswith('https://'))
                    for lang in builder.LANGS:
                        self.assertTrue(source['titles'].get(lang, '').strip())

    def test_rumi_keeps_the_four_reed_couplets(self):
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                section = self.entries['rumi']['copy'][lang]['sections'][3]
                verse_lines = sum(len([line for line in p.split('\n') if line.strip()])
                                  for p in section['paragraphs'] if '\n' in p)
                self.assertGreaterEqual(verse_lines, 8)

    def test_freud_no_longer_closes_the_obsolete_first_round(self):
        self.assertNotIn('第一轮的最后一个人', builder.source_body('freud', 'zh'))
        self.assertNotIn('The Last Person in Round One', builder.source_body('freud', 'en'))
        self.assertEqual(self.entries['freud']['movement'], 3)

    def test_davinci_retitled_without_changing_his_url(self):
        index = (builder.SERIES / 'index.html').read_text(encoding='utf-8')
        self.assertIn('达芬奇，还要打开一扇门', index)
        self.assertIn('Da Vinci, One More Door to Open', index)
        self.assertIn('href="davinci.html"', index)
        self.assertNotIn('Da Vinci, Everything Begun, Nothing Finished', index)

    def test_ninth_batch_has_complete_editions(self):
        for slug, number in (('lacan', 25), ('dostoevsky', 26), ('kafka', 27)):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], 3)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), 8)
                builder.validate_full_edition(entry)

    def test_ninth_batch_source_and_neighbour_links(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug, previous, following in (
                ('lacan', 'freud', 'dostoevsky'),
                ('dostoevsky', 'lacan', 'kafka'),
                ('kafka', 'dostoevsky', 'huineng'),
            ):
                with self.subTest(slug=slug, lang=lang):
                    page = outputs[builder.SERIES / lang / (slug + '.html')]
                    self.assertIn(f'<a href="../{slug}.html">EN / 中文</a>', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
                    for neighbour in (previous, following):
                        link = re.search(r'<a href="' + neighbour + r'\.html">(.*?)</a>', page, re.S)
                        self.assertIsNotNone(link)
                        self.assertIn(builder.esc(self.entries[neighbour]['copy'][lang]['title']), link.group(1))

    def test_ninth_batch_local_links_resolve(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug in ('lacan', 'dostoevsky', 'kafka'):
                path = builder.SERIES / lang / (slug + '.html')
                for href in re.findall(r'href="([^"]+)"', outputs[path]):
                    url = urlsplit(html.unescape(href))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (path.parent / unquote(url.path)).resolve()
                    with self.subTest(page=str(path), href=href):
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_ninth_batch_narratives_exclude_editorial_notes(self):
        for slug in ('lacan', 'dostoevsky', 'kafka'):
            for lang in ('zh', 'en'):
                with self.subTest(slug=slug, lang=lang):
                    body = builder.source_body(slug, lang)
                    self.assertEqual(body.count('<h2'), 8)
                    self.assertNotIn('essay-footer-note', body)
                    self.assertNotIn('<h2>Notes</h2>', body)
                    self.assertNotIn('<h2>注释</h2>', body)

    def test_first_twenty_seven_and_weil_have_full_editions(self):
        required = [item['slug'] for item in builder.canonical_order() if item['number'] <= 27] + ['weil']
        self.assertEqual(len(required), 28)
        self.assertTrue(all(self.entries[slug]['edition']['status'] == 'full' for slug in required))

    def test_ninth_batch_sources_are_localized_in_every_edition(self):
        for slug in ('lacan', 'dostoevsky', 'kafka'):
            for source in self.entries[slug]['sources']:
                with self.subTest(slug=slug, source=source['url']):
                    self.assertTrue(source['url'].startswith('https://'))
                    for lang in builder.LANGS:
                        self.assertTrue(source['titles'].get(lang, '').strip())

    def test_tenth_batch_has_complete_editions(self):
        for slug, number, count in (('huineng', 28, 8), ('hegel', 29, 9), ('napoleon', 30, 9)):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], 3)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), count)
                builder.validate_full_edition(entry)

    def test_tenth_batch_source_and_neighbour_links(self):
        outputs = builder.build()
        cases = (('huineng', 'kafka', 'hegel'), ('hegel', 'huineng', 'napoleon'),
                 ('napoleon', 'hegel', 'genghiskhan'))
        for lang in builder.LANGS:
            for slug, previous, following in cases:
                with self.subTest(slug=slug, lang=lang):
                    page = outputs[builder.SERIES / lang / (slug + '.html')]
                    self.assertIn(f'<a href="../{slug}.html">EN / 中文</a>', page)
                    self.assertIn(f'href="{previous}.html"', page)
                    self.assertIn(f'href="{following}.html"', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)

    def test_tenth_batch_local_links_resolve(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug in ('huineng', 'hegel', 'napoleon'):
                path = builder.SERIES / lang / (slug + '.html')
                for href in re.findall(r'href="([^"]+)"', outputs[path]):
                    url = urlsplit(html.unescape(href))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (path.parent / unquote(url.path)).resolve()
                    with self.subTest(page=str(path), href=href):
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_tenth_batch_narratives_exclude_editorial_notes(self):
        for slug, count in (('huineng', 8), ('hegel', 9), ('napoleon', 9)):
            for lang in ('zh', 'en'):
                with self.subTest(slug=slug, lang=lang):
                    body = builder.source_body(slug, lang)
                    self.assertEqual(body.count('<h2'), count)
                    self.assertNotIn('essay-footer-note', body)
                    self.assertNotIn('<h2>Notes</h2>', body)
                    self.assertNotIn('<h2>注释</h2>', body)

    def test_first_thirty_and_weil_have_full_editions(self):
        required = [item['slug'] for item in builder.canonical_order() if item['number'] <= 30] + ['weil']
        self.assertEqual(len(required), 31)
        self.assertTrue(all(self.entries[slug]['edition']['status'] == 'full' for slug in required))

    def test_tenth_batch_sources_are_localized_in_every_edition(self):
        for slug in ('huineng', 'hegel', 'napoleon'):
            for source in self.entries[slug]['sources']:
                with self.subTest(slug=slug, source=source['url']):
                    self.assertTrue(source['url'].startswith('https://'))
                    for lang in builder.LANGS:
                        self.assertTrue(source['titles'].get(lang, '').strip())

    def test_eleventh_batch_has_complete_editions(self):
        for slug, number, count in (('genghiskhan', 31, 9), ('curie', 32, 8), ('michelangelo', 33, 8)):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], 3)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), count)
                builder.validate_full_edition(entry)

    def test_eleventh_batch_source_and_neighbour_links(self):
        outputs = builder.build()
        cases = (('genghiskhan', 'napoleon', 'curie'), ('curie', 'genghiskhan', 'michelangelo'),
                 ('michelangelo', 'curie', 'lincoln'))
        for lang in builder.LANGS:
            for slug, previous, following in cases:
                with self.subTest(slug=slug, lang=lang):
                    page = outputs[builder.SERIES / lang / (slug + '.html')]
                    self.assertIn(f'<a href="../{slug}.html">EN / 中文</a>', page)
                    self.assertIn(f'href="{previous}.html"', page)
                    self.assertIn(f'href="{following}.html"', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)

    def test_eleventh_batch_local_links_resolve(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug in ('genghiskhan', 'curie', 'michelangelo'):
                path = builder.SERIES / lang / (slug + '.html')
                for href in re.findall(r'href="([^"]+)"', outputs[path]):
                    url = urlsplit(html.unescape(href))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (path.parent / unquote(url.path)).resolve()
                    with self.subTest(page=str(path), href=href):
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_eleventh_batch_narratives_exclude_editorial_notes(self):
        for slug, count in (('genghiskhan', 9), ('curie', 8), ('michelangelo', 8)):
            for lang in ('zh', 'en'):
                with self.subTest(slug=slug, lang=lang):
                    body = builder.source_body(slug, lang)
                    self.assertEqual(body.count('<h2'), count)
                    self.assertNotIn('essay-footer-note', body)
                    self.assertNotIn('<h2>Notes</h2>', body)
                    self.assertNotIn('<h2>注释</h2>', body)

    def test_first_thirty_three_and_weil_have_full_editions(self):
        required = [item['slug'] for item in builder.canonical_order() if item['number'] <= 33] + ['weil']
        self.assertEqual(len(required), 34)
        self.assertTrue(all(self.entries[slug]['edition']['status'] == 'full' for slug in required))

    def test_eleventh_batch_sources_are_localized_in_every_edition(self):
        for slug in ('genghiskhan', 'curie', 'michelangelo'):
            self.assertTrue(self.entries[slug]['sources'])
            for source in self.entries[slug]['sources']:
                with self.subTest(slug=slug, source=source['url']):
                    self.assertTrue(source.get('title', '').strip())
                    self.assertTrue(source['url'].startswith('https://'))
                    for lang in builder.LANGS:
                        self.assertTrue(source['titles'].get(lang, '').strip())

    def test_eleventh_batch_revised_titles_match_index_and_sources(self):
        index = (builder.SERIES / 'index.html').read_text()
        for slug, zh, en in (
            ('genghiskhan', '成吉思汗，马蹄之后', 'Genghis Khan, After the Hooves'),
            ('curie', '玛丽·斯克沃多夫斯卡，不止是一个名字', 'Maria Skłodowska, More Than a Name'),
        ):
            with self.subTest(slug=slug):
                source = builder.source_path_for(slug).read_text()
                for title in (zh, en):
                    self.assertIn(title, source)
                    self.assertIn(title, index)
                self.assertIn(f'<h1 class="lang-zh">{zh}</h1>', source)
                self.assertIn(f'<h1 class="lang-en">{en}</h1>', source)

    def test_eleventh_batch_description_attributes_are_not_broken_by_quotes(self):
        from html.parser import HTMLParser

        class Descriptions(HTMLParser):
            def __init__(self):
                super().__init__()
                self.descriptions = []

            def handle_starttag(self, tag, attrs):
                if tag == 'meta' and dict(attrs).get('name') == 'description':
                    self.descriptions.append(attrs)

        for slug in ('genghiskhan', 'curie', 'michelangelo'):
            with self.subTest(slug=slug):
                parser = Descriptions()
                parser.feed(builder.source_path_for(slug).read_text())
                self.assertEqual(len(parser.descriptions), 1)
                attrs = parser.descriptions[0]
                self.assertEqual({key for key, value in attrs}, {'name', 'content'})
                self.assertEqual(len(attrs), 2)
                self.assertGreater(len(dict(attrs)['content']), 25)

    def test_twelfth_batch_has_complete_editions(self):
        for slug, number in (('lincoln', 34), ('galileo', 35), ('wittgenstein', 36)):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], 3)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), 9)
                builder.validate_full_edition(entry)

    def test_first_thirty_six_and_weil_have_full_editions(self):
        required = [item['slug'] for item in builder.canonical_order() if item['number'] <= 36] + ['weil']
        self.assertEqual(len(required), 37)
        self.assertTrue(all(self.entries[slug]['edition']['status'] == 'full' for slug in required))

    def test_twelfth_batch_source_and_neighbour_links(self):
        outputs = builder.build()
        cases = (('lincoln', 'michelangelo', 'galileo'), ('galileo', 'lincoln', 'wittgenstein'),
                 ('wittgenstein', 'galileo', 'augustine'))
        for lang in builder.LANGS:
            for slug, previous, following in cases:
                with self.subTest(slug=slug, lang=lang):
                    page = outputs[builder.SERIES / lang / (slug + '.html')]
                    self.assertIn(f'<a href="../{slug}.html">EN / 中文</a>', page)
                    self.assertIn(f'href="{previous}.html"', page)
                    self.assertIn(f'href="{following}.html"', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)

    def test_twelfth_batch_local_links_resolve(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug in ('lincoln', 'galileo', 'wittgenstein'):
                path = builder.SERIES / lang / (slug + '.html')
                for href in re.findall(r'href="([^"]+)"', outputs[path]):
                    url = urlsplit(html.unescape(href))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (path.parent / unquote(url.path)).resolve()
                    with self.subTest(page=str(path), href=href):
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_twelfth_batch_sources_are_localized(self):
        for slug in ('lincoln', 'galileo', 'wittgenstein'):
            for source in self.entries[slug]['sources']:
                with self.subTest(slug=slug, source=source['url']):
                    self.assertTrue(source.get('title', '').strip())
                    self.assertTrue(source['url'].startswith('https://'))
                    self.assertEqual(set(source['titles']), set(builder.LANGS))
                    self.assertTrue(all(source['titles'][lang].strip() for lang in builder.LANGS))

    def test_twelfth_batch_source_narratives_exclude_notes(self):
        for slug, paragraphs in (('lincoln', 60), ('galileo', 49), ('wittgenstein', 54)):
            for lang in ('zh', 'en'):
                with self.subTest(slug=slug, lang=lang):
                    body = builder.source_body(slug, lang)
                    self.assertEqual(body.count('<h2'), 9)
                    self.assertEqual(len(re.findall(r'<p\b', body)), paragraphs)
                    self.assertNotIn('essay-footer-note', body)
                    self.assertNotIn('source-notes', body)

    def test_twelfth_batch_description_attributes_are_well_formed(self):
        from html.parser import HTMLParser

        class Descriptions(HTMLParser):
            def __init__(self):
                super().__init__()
                self.items = []

            def handle_starttag(self, tag, attrs):
                if tag == 'meta' and dict(attrs).get('name') == 'description':
                    self.items.append(attrs)

        for slug in ('lincoln', 'galileo', 'wittgenstein'):
            parser = Descriptions()
            parser.feed(builder.source_path_for(slug).read_text())
            with self.subTest(slug=slug):
                self.assertEqual(len(parser.items), 1)
                self.assertEqual({key for key, _ in parser.items[0]}, {'name', 'content'})
                self.assertEqual(len(parser.items[0]), 2)
                self.assertGreater(len(dict(parser.items[0])['content']), 25)

    def test_twelfth_batch_traditional_has_every_paragraph(self):
        for slug, expected in (('lincoln', [7, 6, 8, 5, 7, 6, 7, 6, 8]),
                               ('galileo', [5, 6, 5, 5, 6, 5, 5, 6, 6]),
                               ('wittgenstein', [6] * 9)):
            with self.subTest(slug=slug):
                sections = self.entries[slug]['copy']['zh-hant']['sections']
                self.assertEqual([len(s['paragraphs']) for s in sections], expected)

    def test_thirteenth_batch_has_complete_editions(self):
        for slug, number in (('augustine', 37), ('badashanren', 38), ('sushi', 39)):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual(entry['number'], number)
                self.assertEqual(entry['movement'], 3)
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                for lang in builder.LANGS:
                    self.assertEqual(len(entry['copy'][lang]['sections']), 9)
                builder.validate_full_edition(entry)

    def test_first_thirty_nine_and_weil_have_full_editions(self):
        required = [item['slug'] for item in builder.canonical_order() if item['number'] <= 39] + ['weil']
        self.assertEqual(len(required), 40)
        self.assertTrue(all(self.entries[slug]['edition']['status'] == 'full' for slug in required))

    def test_thirteenth_batch_navigation_and_local_links(self):
        outputs = builder.build()
        cases = (('augustine', 'wittgenstein', 'badashanren'),
                 ('badashanren', 'augustine', 'sushi'), ('sushi', 'badashanren', 'nishida'))
        for lang in builder.LANGS:
            for slug, previous, following in cases:
                path = builder.SERIES / lang / (slug + '.html')
                page = outputs[path]
                with self.subTest(slug=slug, lang=lang):
                    self.assertIn(f'<a href="../{slug}.html">EN / 中文</a>', page)
                    self.assertIn(f'href="{previous}.html"', page)
                    self.assertIn(f'href="{following}.html"', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
                    for href in re.findall(r'href="([^"]+)"', page):
                        url = urlsplit(html.unescape(href))
                        if url.scheme or url.netloc or not url.path:
                            continue
                        target = (path.parent / unquote(url.path)).resolve()
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_thirteenth_batch_sources_are_localized(self):
        for slug in ('augustine', 'badashanren', 'sushi'):
            for source in self.entries[slug]['sources']:
                with self.subTest(slug=slug, source=source['url']):
                    self.assertTrue(source.get('title', '').strip())
                    self.assertTrue(source['url'].startswith('https://'))
                    self.assertEqual(set(source['titles']), set(builder.LANGS))
                    self.assertTrue(all(source['titles'][lang].strip() for lang in builder.LANGS))

    def test_thirteenth_batch_source_narratives_and_traditional_paragraphs(self):
        for slug in ('augustine', 'badashanren', 'sushi'):
            for lang in ('zh', 'en'):
                body = builder.source_body(slug, lang)
                with self.subTest(slug=slug, lang=lang):
                    self.assertEqual(body.count('<h2'), 9)
                    self.assertGreaterEqual(len(re.findall(r'<p\b', body)), 40)
                    self.assertNotIn('essay-footer-note', body)
                    self.assertNotIn('source-notes', body)
            sections = re.split(r'<h2\b[^>]*>.*?</h2>', builder.source_body(slug, 'zh'), flags=re.S)[1:]
            source_counts = [len(re.findall(r'<p\b', section)) for section in sections]
            self.assertEqual(source_counts, [len(s['paragraphs']) for s in self.entries[slug]['copy']['zh-hant']['sections']])

    def test_thirteenth_batch_source_descriptions_are_well_formed(self):
        from html.parser import HTMLParser

        class Descriptions(HTMLParser):
            def __init__(self):
                super().__init__()
                self.items = []

            def handle_starttag(self, tag, attrs):
                if tag == 'meta' and dict(attrs).get('name') == 'description':
                    self.items.append(attrs)

        for slug in ('augustine', 'badashanren', 'sushi'):
            parser = Descriptions()
            parser.feed(builder.source_path_for(slug).read_text())
            with self.subTest(slug=slug):
                self.assertEqual(len(parser.items), 1)
                self.assertEqual({key for key, _ in parser.items[0]}, {'name', 'content'})
                self.assertEqual(len(parser.items[0]), 2)
                self.assertGreater(len(dict(parser.items[0])['content']), 25)

    def test_thirteenth_batch_keeps_the_grounding_scenes(self):
        # Scene/attribution guards supplement the coverage map, not literary review.
        augustine = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('augustine', 'zh')))
        for term in ('梨', '伙伴', '记忆', '恩典', '上帝之城', '想象'):
            self.assertIn(term, augustine)
        self.assertNotIn('他已经不想了', augustine)
        bada = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('badashanren', 'zh')))
        for term in ('1699', '七条', '河上花', '阮籍', '慧能', '米开朗基罗', '想象'):
            self.assertIn(term, bada)
        self.assertNotIn('六十一年的沉默', bada)
        sushi = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('sushi', 'zh')))
        for term in ('1100', '柔奴', '寒食雨', '微冷', '夜郎', '想象'):
            self.assertIn(term, sushi)
        self.assertNotIn('你凿不碎一个不把你的凿当回事的人', sushi)

    def test_huineng_preserves_both_gathas_as_verse(self):
        for lang in builder.LANGS:
            verses = [p for p in self.entries['huineng']['copy'][lang]['sections'][1]['paragraphs'] if '\n' in p]
            with self.subTest(lang=lang):
                self.assertGreaterEqual(len(verses), 2)
                self.assertGreaterEqual(sum(p.count('\n') for p in verses), 6)
        for lang in ('zh', 'en'):
            self.assertGreaterEqual(builder.source_body('huineng', lang).count('<br>'), 6)

    def test_dufu_keeps_the_poems_as_verse_in_every_edition(self):
        # Nine stanza blocks across the mountain, patronage, war, cottage,
        # river and late-life sections. Prose summaries cannot replace them.
        minimum_stanzas = (1, 0, 1, 0, 1, 3, 2, 1, 0)
        for lang in builder.LANGS:
            sections = self.entries['dufu']['copy'][lang]['sections']
            for index, minimum in enumerate(minimum_stanzas):
                with self.subTest(lang=lang, section=index + 1):
                    verses = [p for p in sections[index]['paragraphs'] if '\n' in p]
                    self.assertGreaterEqual(len(verses), minimum)
            self.assertGreaterEqual(sum(p.count('\n') for s in sections for p in s['paragraphs']), 25)

    def test_dufu_traditional_resolves_context_sensitive_poem_characters(self):
        body = '\n'.join(p for s in self.entries['dufu']['copy']['zh-hant']['sections'] for p in s['paragraphs'])
        for correct in ('干謁', '造化鍾神秀', '無乾處', '踏裡裂', '楊萬里', '里巷'):
            self.assertIn(correct, body)
        for incorrect in ('乾謁', '造化鐘神秀', '無干處', '踏里裂', '楊萬裡', '裡巷'):
            self.assertNotIn(incorrect, body)

    def test_korean_full_editions_load_word_preserving_heading_styles(self):
        css = (builder.SERIES / 'great-lives-edition.css').read_text(encoding='utf-8')
        self.assertIn('html[lang="ko"] .great-edition-body h2,html[lang="ko"] .great-edition-body h3{word-break:keep-all;overflow-wrap:anywhere}', css)
        outputs = builder.build()
        for slug, entry in self.entries.items():
            if entry.get('edition', {}).get('status') == 'full':
                self.assertIn('great-lives-edition.css?v=20260918', outputs[builder.SERIES / 'ko' / (slug + '.html')])

    def test_full_editions_keep_index_structured_titles_in_sync(self):
        index = (builder.SERIES / 'index.html').read_text(encoding='utf-8')
        block = re.search(r'<script type="application/ld\+json">(.*?)</script>', index, re.S)
        self.assertIsNotNone(block)
        items = json.loads(block.group(1))['mainEntity']['itemListElement']
        names = {item['position']: item['name'] for item in items}
        for slug, entry in self.entries.items():
            if entry.get('edition', {}).get('status') != 'full':
                continue
            with self.subTest(slug=slug):
                source = builder.source_path_for(slug).read_text(encoding='utf-8')
                heading = re.search(r'<h1 class="lang-en">(.*?)</h1>', source, re.S)
                self.assertIsNotNone(heading)
                title = html.unescape(re.sub(r'<[^>]+>', '', heading.group(1)))
                self.assertEqual(names[entry['number']], title)

    def test_jesus_traditional_uses_neighbour_not_relinquishment(self):
        text = '\n'.join(p for section in self.entries['jesus']['copy']['zh-hant']['sections'] for p in section['paragraphs'])
        self.assertIn('鄰舍', text)
        self.assertNotIn('鄰捨', text)
        self.assertNotIn('尼採', text)

    def test_second_batch_narratives_have_explicit_boundaries(self):
        for slug, sections in (('wangyangming', 10), ('kant', 10), ('nietzsche', 8)):
            for lang in ('zh', 'en'):
                with self.subTest(slug=slug, lang=lang):
                    body = builder.source_body(slug, lang)
                    self.assertTrue(body.startswith('<h2'))
                    self.assertEqual(body.count('<h2'), sections)
                    self.assertNotIn('<h2>Abstract</h2>', body)
                    self.assertNotIn('<h2>Notes</h2>', body)
                    self.assertNotIn('<h2>注释</h2>', body)
                    self.assertNotIn('<p>---</p>', body)

    def test_classical_chong_is_not_converted_to_collision(self):
        traditional = self.entries['laozi']['copy']['zh-hant']
        body = '\n'.join(p for s in traditional['sections'] for p in s['paragraphs'])
        self.assertIn('萬物負陰而抱陽，沖氣以為和', body)
        self.assertNotIn('衝氣', body)

    def test_traditional_context_sensitive_spellings_are_preserved(self):
        for slug in ('laozi', 'confucius', 'socrates', 'wangyangming', 'kant', 'nietzsche', 'zhuangzi', 'buddha', 'jesus', 'godel', 'einstein', 'dufu', 'qinshihuang', 'washington', 'alexander', 'darwin', 'newton', 'bach', 'beethoven', 'simaqian', 'libai', 'rumi', 'davinci', 'freud'):
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

    def test_optional_english_abstract_is_not_a_numbered_section(self):
        text = ('<div class="essay-body lang-en"><h1>Title</h1><p>Author</p>'
                '<h2>Abstract</h2><p>Summary only.</p>'
                '<h2>I. First scene</h2><p>Complete narrative.</p>'
                '<h2>II. Second scene</h2><p>Its continuation.</p>'
                '<h2>Notes</h2><p>Sources.</p></div>')
        path = Mock()
        path.read_text.return_value = text
        with patch.object(builder, 'source_path_for', return_value=path):
            body = builder.source_body('test', 'en')
            self.assertTrue(body.startswith('<h2>I. First scene</h2>'))
            self.assertEqual(body.count('<h2'), 2)
            self.assertNotIn('Summary only.', body)

    def test_missing_note_boundary_cannot_consume_next_language(self):
        text = ('<div class="essay-body lang-zh"><h2>一</h2><p>A</p></div>'
                '<div class="essay-body lang-en"><h2>One</h2>'
                '<p>B</p><h2>Notes</h2></div>')
        path = Mock()
        path.read_text.return_value = text
        with patch.object(builder, 'source_path_for', return_value=path):
            with self.assertRaisesRegex(ValueError, 'source-note boundary'):
                builder.source_body('test', 'zh')

    def test_fourteenth_batch_has_complete_editions(self):
        for slug, number, movement, sections in (
            ('nishida', 40, 3, 9),
            ('emperor', 41, 3, 9),
            ('homer', 42, 4, 9),
        ):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual((entry['number'], entry['movement']), (number, movement))
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                self.assertTrue(all(len(entry['copy'][lang]['sections']) == sections for lang in builder.LANGS))
                builder.validate_full_edition(entry)

    def test_fourteenth_batch_source_and_neighbour_links(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug, previous, following in (
                ('nishida', 'sushi', 'emperor'),
                ('emperor', 'nishida', 'homer'),
                ('homer', 'emperor', 'plato'),
            ):
                with self.subTest(slug=slug, lang=lang):
                    page = outputs[builder.SERIES / lang / (slug + '.html')]
                    self.assertIn(f'<a href="../{slug}.html">EN / 中文</a>', page)
                    self.assertIn(f'href="{previous}.html"', page)
                    self.assertIn(f'href="{following}.html"', page)

    def test_fourteenth_batch_does_not_regress_to_the_rejected_synopses(self):
        # User review rejected the previous 20–21-paragraph editions.
        # This catches that regression; length cannot certify literary quality.
        for slug in ('nishida', 'emperor', 'homer'):
            for lang in ('ja', 'fr', 'de', 'es', 'ko'):
                with self.subTest(slug=slug, lang=lang):
                    sections = self.entries[slug]['copy'][lang]['sections']
                    paragraphs = [p for section in sections for p in section['paragraphs']]
                    self.assertGreaterEqual(len(paragraphs), 40)
                    self.assertTrue(all(len(s['paragraphs']) >= 4 for s in sections))
                    body = ' '.join(paragraphs)
                    if lang in ('ja', 'ko'):
                        self.assertGreaterEqual(len(re.sub(r'\s+', '', body)), 3000)
                    else:
                        self.assertGreaterEqual(len(body.split()), 1200)

    def test_fourteenth_batch_removes_conflicting_source_claims(self):
        forbidden = {
            'nishida': ('西田几多郎四十一岁', '都是这个意思', 'Nishida discovered what comes before language.', 'The same logic.'),
            'emperor': ('空的东西不碎', '一千多年的程序', 'all political legitimacy flows from it', 'Postwar democracy used the Emperor'),
            'homer': ('每一次唱都不一样', '声音是混沌', 'Gödel proved it — no system can close.', 'burned the bridge'),
        }
        for slug, fragments in forbidden.items():
            body = '\n'.join(builder.source_body(slug, lang) for lang in ('zh', 'en'))
            for fragment in fragments:
                with self.subTest(slug=slug, fragment=fragment):
                    self.assertNotIn(fragment, body)

    def test_fourteenth_batch_local_links_resolve(self):
        outputs = builder.build()
        for lang in builder.LANGS:
            for slug in ('nishida', 'emperor', 'homer'):
                path = builder.SERIES / lang / (slug + '.html')
                for href in re.findall(r'href="([^"]+)"', outputs[path]):
                    url = urlsplit(html.unescape(href))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (path.parent / unquote(url.path)).resolve()
                    with self.subTest(page=str(path), href=href):
                        self.assertTrue(target in outputs or target.is_file(), f'Missing link: {href}')

    def test_fourteenth_batch_completes_third_movement_and_reaches_43(self):
        full = [entry for entry in self.entries.values() if entry.get('edition', {}).get('status') == 'full']
        self.assertGreaterEqual(len(full), 43)
        third = [item for item in builder.canonical_order() if self.entries[item['slug']]['movement'] == 3]
        self.assertEqual(len(third), 18)
        self.assertTrue(all(self.entries[item['slug']]['edition']['status'] == 'full' for item in third))

    def test_fourteenth_batch_sources_are_localized(self):
        for slug in ('nishida', 'emperor', 'homer'):
            for source in self.entries[slug]['sources']:
                with self.subTest(slug=slug, source=source['url']):
                    self.assertEqual(set(source['titles']), set(builder.LANGS))
                    self.assertTrue(all(source['titles'][lang].strip() for lang in builder.LANGS))

    def test_fourteenth_batch_keeps_factual_boundaries_visible(self):
        nishida = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('nishida', 'zh')))
        self.assertIn('留下被帝国语言利用的暧昧', nishida)
        self.assertNotIn('哲学与政治无关', nishida)
        emperor = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('emperor', 'zh')))
        for term in ('国民主权', '内阁', '国政权能', '神格'):
            self.assertIn(term, emperor)
        homer = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('homer', 'zh')))
        for term in ('并无定论', '仍在争论', '不是学界定论'):
            self.assertIn(term, homer)

    def test_plato_full_edition_reaches_44(self):
        entry = self.entries['plato']
        self.assertEqual((entry['number'], entry['movement']), (43, 4))
        self.assertEqual(entry['edition']['status'], 'full')
        builder.validate_full_edition(entry)
        full = [e for e in self.entries.values() if e.get('edition', {}).get('status') == 'full']
        self.assertGreaterEqual(len(full), 44)
        for lang in builder.LANGS:
            sections = entry['copy'][lang]['sections']
            self.assertEqual(len(sections), 9)
            paragraphs = [p for s in sections for p in s['paragraphs']]
            self.assertGreaterEqual(len(paragraphs), 50)
            self.assertGreaterEqual(len(sections[-1]['paragraphs']), 8)
            for section in sections:
                self.assertGreaterEqual(len(section['paragraphs']), 5)
            body = ' '.join(paragraphs)
            units = len(re.sub(r'\s+', '', body)) if lang in ('zh-hant','ja','ko') else len(body.split())
            self.assertGreaterEqual(units, 3500 if lang in ('zh-hant','ja','ko') else 1600)

    def test_plato_keeps_factual_and_interpretive_boundaries(self):
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('plato', 'zh')))
        for term in ('叙述者斐多', '《法律篇》没有苏格拉底', '第一次旅程', '作者身份也未定', '《巴门尼德篇》', '这是我的文学想象', '他准备听'):
            self.assertIn(term, zh)
        for claim in ('心病也是病', '他错了因为他太痛了', '每一篇里都是主角', '第二次差点被卖成奴隶', '比任何帝国都长'):
            self.assertNotIn(claim, zh)
        tc = ' '.join(p for s in self.entries['plato']['copy']['zh-hant']['sections'] for p in s['paragraphs'])
        for error in ('克裡托','西西裡','亞裡士多德','沈思','那只雞','記得准','證明瞭','覈實'):
            self.assertNotIn(error, tc)
        self.assertIn('那隻雞', tc)
        self.assertIn('亞里斯多德', tc)
        for source in self.entries['plato']['sources']:
            self.assertEqual(set(source['titles']), set(builder.LANGS))


    def test_hume_full_edition_reaches_45(self):
        entry = self.entries['hume']
        self.assertEqual((entry['number'], entry['movement']), (44, 4))
        self.assertEqual(entry['edition']['status'], 'full')
        builder.validate_full_edition(entry)
        full = [e for e in self.entries.values() if e.get('edition', {}).get('status') == 'full']
        self.assertGreaterEqual(len(full), 45)
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                sections = entry['copy'][lang]['sections']
                self.assertEqual(len(sections), 9)
                self.assertEqual([len(s['paragraphs']) for s in sections], [6] * 8 + [8])
                self.assertEqual([s['covers'][0] for s in sections], entry['edition']['required_topics'])
                body = ' '.join(p for s in sections for p in s['paragraphs'])
                units = len(re.sub(r'\s+', '', body)) if lang in ('zh-hant', 'ja', 'ko') else len(body.split())
                self.assertGreaterEqual(units, 3800 if lang in ('zh-hant', 'ja', 'ko') else 1900)
        for source in entry['sources']:
            self.assertEqual(set(source['titles']), set(builder.LANGS))

    def test_hume_keeps_corrected_facts_and_interpretive_boundaries(self):
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('hume', 'zh')))
        for term in ('1739至1740年', '双陆棋，不是台球', '感性直观的形式', '因果性是知性范畴',
                     '还无法给出满意的解释', '种族天生高下的偏见', '不是历史上的相遇'):
            self.assertIn(term, zh)
        self.assertNotIn('1739年，二十八岁', zh)
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('hume', 'en')))
        for term in ('backgammon, not billiards', 'forms of sensible intuition', 'a racist assertion',
                     'not a historical meeting', 'not a readership survey'):
            self.assertIn(term, en)

    def test_hume_traditional_and_game_names(self):
        entry = self.entries['hume']
        tc = ' '.join(p for s in entry['copy']['zh-hant']['sections'] for p in s['paragraphs'])
        for term in ('休謨', '撞球', '雙陸棋', '很準', '想像', '反覆'):
            self.assertIn(term, tc)
        for error in ('很准', '想象', '反復', '台球', '依据'):
            self.assertNotIn(error, tc)
        for lang, game in {'ja': 'バックギャモン', 'fr': 'backgammon', 'de': 'Backgammon',
                           'es': 'backgammon', 'ko': '백개먼'}.items():
            for section_number in (4, 8):
                self.assertIn(game, ' '.join(entry['copy'][lang]['sections'][section_number]['paragraphs']))

    def test_hume_description_is_a_single_valid_attribute(self):
        from html.parser import HTMLParser
        class MetaParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.descriptions = []
            def handle_starttag(self, tag, attrs):
                if tag == 'meta' and dict(attrs).get('name') == 'description':
                    self.descriptions.append(attrs)
        page = MetaParser()
        page.feed(builder.source_path_for('hume').read_text(encoding='utf-8'))
        self.assertEqual(len(page.descriptions), 1)
        self.assertEqual({k for k, v in page.descriptions[0]}, {'name', 'content'})
        self.assertIn('双陆棋', dict(page.descriptions[0])['content'])


    def test_schopenhauer_full_edition_completes_batch_15(self):
        entry = self.entries['schopenhauer']
        self.assertEqual((entry['number'], entry['movement']), (45, 4))
        self.assertEqual(entry['edition']['status'], 'full')
        builder.validate_full_edition(entry)
        full = [e for e in self.entries.values() if e.get('edition', {}).get('status') == 'full']
        self.assertGreaterEqual(len(full), 46)
        for slug in ('plato', 'hume', 'schopenhauer'):
            self.assertEqual(self.entries[slug]['edition']['status'], 'full')
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                sections = entry['copy'][lang]['sections']
                self.assertEqual(len(sections), 9)
                self.assertEqual([len(s['paragraphs']) for s in sections], [6, 6, 6, 6, 8, 6, 6, 7, 9])
                self.assertEqual([s['covers'][0] for s in sections], entry['edition']['required_topics'])
                body = ' '.join(p for s in sections for p in s['paragraphs'])
                units = len(re.sub(r'\s+', '', body)) if lang in ('zh-hant', 'ja', 'ko') else len(body.split())
                self.assertGreaterEqual(units, 4300 if lang in ('zh-hant', 'ja', 'ko') else 2100)
        for source in entry['sources']:
            self.assertEqual(set(source['titles']), set(builder.LANGS))

    def test_schopenhauer_source_keeps_factual_and_philosophical_boundaries(self):
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('schopenhauer', 'zh')))
        for term in ('不是一个人也没来', '同一个行动以不同方式被知道', '形而上学的推展',
                     '还有同情', '不是一张三格流程图', '1925年的自述', '自我报告',
                     '并不能证明谁都做不到', '他六十三岁', '不是史料里的场面', '双陆棋'):
            self.assertIn(term, zh)
        for claim in ('失败本身就是证据', '余项守恒', '他比佛陀更诚实的地方',
                      '第一个把东方思想当作严肃哲学资源', '推下楼梯'):
            self.assertNotIn(claim, zh)
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('schopenhauer', 'en')))
        for term in ('small, not nonexistent', 'one act known in different ways',
                     'compassion', 'not Freud\'s unconscious', 'not a historical record',
                     'sixty-three', 'backgammon'):
            self.assertIn(term, en)

    def test_schopenhauer_all_editions_keep_ethics_and_full_dog_ending(self):
        terms = {
            'zh-hant': ('同情', '雙陸棋', '狗'),
            'ja': ('同情', 'バックギャモン', '犬'),
            'fr': ('compassion', 'backgammon', 'chien'),
            'de': ('Mitleid', 'Backgammon', 'Hund'),
            'es': ('compasión', 'backgammon', 'perro'),
            'ko': ('동정', '백개먼', '개'),
        }
        for lang, (ethics, game, animal) in terms.items():
            sections = self.entries['schopenhauer']['copy'][lang]['sections']
            self.assertIn(ethics, ' '.join(sections[4]['paragraphs']))
            ending = ' '.join(sections[8]['paragraphs'])
            self.assertIn(game, ending)
            self.assertIn(animal, ending)
        tc = ' '.join(p for s in self.entries['schopenhauer']['copy']['zh-hant']['sections'] for p in s['paragraphs'])
        for correct in ('想像', '回覆', '帳', '沉溺', '尼采'):
            self.assertIn(correct, tc)
        for wrong in ('想象', '回復', '賬', '沈溺', '尼採'):
            self.assertNotIn(wrong, tc)

    def test_schopenhauer_source_metadata_is_well_formed(self):
        from html.parser import HTMLParser
        class DescriptionParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.items = []
            def handle_starttag(self, tag, attrs):
                if tag == 'meta' and dict(attrs).get('name') == 'description':
                    self.items.append(attrs)
        parser = DescriptionParser()
        parser.feed(builder.source_path_for('schopenhauer').read_text(encoding='utf-8'))
        self.assertEqual(len(parser.items), 1)
        self.assertEqual({k for k, v in parser.items[0]}, {'name', 'content'})
        self.assertIn('同情', dict(parser.items[0])['content'])

    def test_batch_16_all_three_are_reviewed_full_editions(self):
        for number, slug in enumerate(('kierkegaard', 'turing', 'chekhov'), 46):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual((entry['number'], entry['movement']), (number, 4))
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                builder.validate_full_edition(entry)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full'
                                    for e in self.entries.values()), 49)

    def test_batch_16_retains_nine_sections_and_full_endings(self):
        for slug in ('kierkegaard', 'turing', 'chekhov'):
            entry = self.entries[slug]
            counts = [6] * 8 + [9 if slug == 'chekhov' else 8]
            for lang, copy in entry['copy'].items():
                with self.subTest(slug=slug, lang=lang):
                    sections = copy['sections']
                    self.assertEqual(len(sections), 9)
                    self.assertEqual([len(s['paragraphs']) for s in sections], counts)
                    self.assertEqual([s['covers'][0] for s in sections], entry['edition']['required_topics'])
                    body = ' '.join(p for s in sections for p in s['paragraphs'])
                    cjk = lang in ('zh-hant', 'ja', 'ko')
                    units = len(re.sub(r'\s+', '', body)) if cjk else len(body.split())
                    self.assertGreaterEqual(units, 3700 if cjk else 1800)

    def test_batch_16_has_localized_notes_and_bibliographies(self):
        for slug, count in (('kierkegaard', 4), ('turing', 7), ('chekhov', 7)):
            entry = self.entries[slug]
            self.assertEqual(len(entry['sources']), count)
            for source in entry['sources']:
                self.assertEqual(set(source['titles']), set(builder.LANGS))
                self.assertTrue(source['url'].startswith('https://'))
            for lang in builder.LANGS:
                self.assertEqual(len(entry['copy'][lang]['notes']), 2)

    def test_kierkegaard_keeps_regine_and_pseudonym_boundaries(self):
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('kierkegaard', 'zh')))
        for phrase in ('1840年9月', '到10月', '蕾吉娜不能被缩成', '以撒不是',
                       '后人概括', '虚构编者', '双陆棋'):
            self.assertIn(phrase, zh)
        self.assertIn('regine-separation-and-other-person', self.entries['kierkegaard']['edition']['required_topics'])
        self.assertIn('abraham-faith-and-ethical-danger', self.entries['kierkegaard']['edition']['required_topics'])

    def test_turing_keeps_mathematical_and_historical_distinctions(self):
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('turing', 'zh')))
        for phrase in ('1931年', '1936年', '三十九岁', '一阶逻辑', '苹果没有接受检验',
                       '形态发生研究在定罪前已经开始', '死亡日期记为6月7日'):
            self.assertIn(phrase, zh)
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('turing', 'en')))
        for phrase in ('thirty-nine', 'first-order', 'before the conviction',
                       'inquest returned a verdict of suicide', 'dignity is not a consequence of the halting theorem'):
            self.assertIn(phrase, en)

    def test_chekhov_is_not_reduced_to_inaction_or_neutrality(self):
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('chekhov', 'zh')))
        for phrase in ('1890年', '萨哈林', '两枪，都没打中', '《三姐妹》有四幕',
                       '1888年10月27日', '回忆中的场面', '生蚝'):
            self.assertIn(phrase, zh)
        self.assertIn('restraint-is-not-neutrality', self.entries['chekhov']['edition']['required_topics'])
        self.assertIn('posing-problems-and-artistic-construction', self.entries['chekhov']['edition']['required_topics'])

    def test_batch_16_traditional_context_is_reviewed(self):
        for slug in ('kierkegaard', 'turing', 'chekhov'):
            tc = ' '.join(p for s in self.entries[slug]['copy']['zh-hant']['sections'] for p in s['paragraphs'])
            for wrong in ('區分瞭解決', '住進瞭解釋', '證明瞭一次', '尼採', '賬', '想象', '反復', '沈默'):
                self.assertNotIn(wrong, tc)
        tc = ' '.join(p for s in self.entries['chekhov']['copy']['zh-hant']['sections'] for p in s['paragraphs'])
        self.assertIn('區分了解決', tc)
        self.assertIn('爆發', tc)

    def test_batch_16_description_attributes_and_reading_navigation(self):
        from html.parser import HTMLParser
        class Metadata(HTMLParser):
            def __init__(self, text):
                super().__init__()
                self.descriptions, self.links = [], []
                self.feed(text)
            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                if tag == 'meta' and d.get('name') == 'description':
                    self.descriptions.append(attrs)
                if tag == 'a' and 'href' in d:
                    self.links.append(d['href'])
        chain = ['schopenhauer', 'kierkegaard', 'turing', 'chekhov', 'cantor']
        for i, slug in enumerate(chain[1:-1], 1):
            page = Metadata(builder.source_path_for(slug).read_text(encoding='utf-8'))
            self.assertEqual(len(page.descriptions), 1)
            self.assertEqual({k for k, v in page.descriptions[0]}, {'name', 'content'})
            for lang in builder.LANGS:
                page = Metadata((builder.SERIES / lang / (slug + '.html')).read_text(encoding='utf-8'))
                self.assertIn(chain[i - 1] + '.html', page.links)
                self.assertIn(chain[i + 1] + '.html', page.links)


    def test_batch_17_all_three_are_reviewed_full_editions(self):
        for number, slug in enumerate(('cantor', 'copernicus', 'sartre'), 49):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual((entry['number'], entry['movement']), (number, 4))
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                builder.validate_full_edition(entry)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full'
                                    for e in self.entries.values()), 52)

    def test_batch_17_keeps_all_nine_sections_and_full_endings(self):
        expected = {
            'cantor': [6, 6, 8, 6, 6, 8, 6, 6, 8],
            'copernicus': [6] * 8 + [7],
            'sartre': [6] * 8 + [8],
        }
        for slug, counts in expected.items():
            entry = self.entries[slug]
            for lang, copy in entry['copy'].items():
                with self.subTest(slug=slug, lang=lang):
                    self.assertEqual(len(copy['sections']), 9)
                    self.assertEqual([len(s['paragraphs']) for s in copy['sections']], counts)
                    self.assertEqual([s['covers'][0] for s in copy['sections']],
                                     entry['edition']['required_topics'])
                    body = ' '.join(p for s in copy['sections'] for p in s['paragraphs'])
                    cjk = lang in ('zh-hant', 'ja', 'ko')
                    units = len(re.sub(r'\s+', '', body)) if cjk else len(body.split())
                    floor = 3500 if lang == 'zh-hant' else 4000 if cjk else 1800
                    self.assertGreaterEqual(units, floor)

    def test_batch_17_has_localized_notes_and_sources(self):
        for slug, count in (('cantor', 4), ('copernicus', 7), ('sartre', 7)):
            entry = self.entries[slug]
            self.assertEqual(len(entry['sources']), count)
            for source in entry['sources']:
                self.assertEqual(set(source['titles']), set(builder.LANGS))
                self.assertTrue(source['url'].startswith('https://'))
                self.assertTrue(all(source['titles'].values()))
            for lang in builder.LANGS:
                self.assertEqual(len(entry['copy'][lang]['notes']), 2)

    def test_cantor_keeps_proof_and_acknowledgment_boundaries(self):
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('cantor', 'zh')))
        for phrase in ('1874年', '1891年', '0.4999', '0.5000', '幂集',
                       'ZFC是一致的', '德德金', '1873年11月30日', '不归一个原因管',
                       '双陆棋', '这两件事不该互相冒充'):
            self.assertIn(phrase, zh)
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('cantor', 'en')))
        for phrase in ('power set need not', 'if the usual set-theoretic axioms ZFC are consistent',
                       'adequate public credit', 'not three statements of one theorem',
                       'There can also be a chair here'):
            self.assertIn(phrase, en)
        self.assertIn('dedekind-credit-and-kronecker', self.entries['cantor']['edition']['required_topics'])

    def test_copernicus_differentiates_preface_and_later_evidence(self):
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('copernicus', 'zh')))
        for phrase in ('吉泽写给雷蒂库斯', '而非哥白尼', '1620年', '第谷式模型',
                       '2009年', '2010年', '不能把那一句误作整本书最后一句'):
            self.assertIn(phrase, zh)
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('copernicus', 'en')))
        for phrase in ('Osiander, not written by Copernicus', 'Johannes Petreius',
                       'Tychonic model', 'important source', 'not an astronomical theorem'):
            self.assertIn(phrase, en)
        self.assertIn('osiander-unauthorized-preface', self.entries['copernicus']['edition']['required_topics'])

    def test_sartre_keeps_open_door_situation_and_other_people(self):
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('sartre', 'zh')))
        for phrase in ('门曾经打开', '不是说一切人际关系必然有毒', '自由不是全能',
                       '受害者', '只承认可能、不承认事实', '偶然道具', '她自己有话要说'):
            self.assertIn(phrase, zh)
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('sartre', 'en')))
        for phrase in ('The door opens', 'Freedom is neither omnipotence',
                       'Beauvoir is not an appendix', 'does not give No Exit a happy ending'):
            self.assertIn(phrase, en)
        self.assertIn('situated-freedom-without-victim-blame', self.entries['sartre']['edition']['required_topics'])

    def test_batch_17_traditional_context_is_reviewed(self):
        texts = {
            slug: ' '.join(p for s in self.entries[slug]['copy']['zh-hant']['sections'] for p in s['paragraphs'])
            for slug in ('cantor', 'copernicus', 'sartre')
        }
        for tc in texts.values():
            for wrong in ('反復', '重復', '想象', '煙鬥', '捨恩貝格',
                          '揭明瞭', '賬', '沈重', '咨詢', '里'):
                self.assertNotIn(wrong, tc)
        self.assertIn('煙斗', texts['sartre'])
        self.assertIn('諮詢', texts['sartre'])
        self.assertIn('署名帳', texts['cantor'])
        self.assertIn('舍恩貝格', texts['copernicus'])

    def test_batch_17_navigation_metadata_and_update_card(self):
        from html.parser import HTMLParser
        class Metadata(HTMLParser):
            def __init__(self, text):
                super().__init__()
                self.descriptions, self.links = [], []
                self.feed(text)
            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                if tag == 'meta' and d.get('name') == 'description':
                    self.descriptions.append(attrs)
                if tag == 'a' and 'href' in d:
                    self.links.append(d['href'])
        chain = ['chekhov', 'cantor', 'copernicus', 'sartre', 'beauvoir']
        for i, slug in enumerate(chain[1:-1], 1):
            source = Metadata(builder.source_path_for(slug).read_text(encoding='utf-8'))
            self.assertEqual(len(source.descriptions), 1)
            self.assertEqual({k for k, v in source.descriptions[0]}, {'name', 'content'})
            for lang in builder.LANGS:
                page = Metadata((builder.SERIES / lang / (slug + '.html')).read_text(encoding='utf-8'))
                self.assertIn(chain[i - 1] + '.html', page.links)
                self.assertIn(chain[i + 1] + '.html', page.links)
        latest = (builder.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertEqual(latest.count('data-update-id="2026-09-22-great-lives-batch-17-full"'), 1)
        for slug in chain[1:-1]:
            self.assertIn('essays/mingren/' + slug + '.html', Metadata(latest).links)

    def test_batch_18_all_three_are_reviewed_full_editions(self):
        for number, slug in enumerate(('beauvoir', 'quine', 'tesla'), 52):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual((entry['number'], entry['movement']), (number, 4))
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                builder.validate_full_edition(entry)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full'
                                    for e in self.entries.values()), 55)

    def test_batch_18_preserves_sections_and_full_prose(self):
        for slug, count in (('beauvoir', 9), ('quine', 10), ('tesla', 9)):
            entry = self.entries[slug]
            for lang, copy in entry['copy'].items():
                with self.subTest(slug=slug, lang=lang):
                    self.assertEqual(len(copy['sections']), count)
                    self.assertEqual([s['covers'][0] for s in copy['sections']],
                                     entry['edition']['required_topics'])
                    paragraphs = [p for s in copy['sections'] for p in s['paragraphs']]
                    self.assertGreaterEqual(len(paragraphs), 54)
                    self.assertGreaterEqual(len(copy['sections'][-1]['paragraphs']), 6)
                    body = ' '.join(paragraphs)
                    cjk = lang in ('zh-hant', 'ja', 'ko')
                    units = len(re.sub(r'\s+', '', body)) if cjk else len(body.split())
                    floor = 3500 if lang == 'zh-hant' else 4000 if cjk else 1800
                    self.assertGreaterEqual(units, floor)

    def test_batch_18_has_localized_notes_and_sources(self):
        for slug in ('beauvoir', 'quine', 'tesla'):
            entry = self.entries[slug]
            self.assertGreaterEqual(len(entry['sources']), 3)
            for source in entry['sources']:
                self.assertEqual(set(source['titles']), set(builder.LANGS))
                self.assertTrue(source['url'].startswith('https://'))
                self.assertTrue(all(source['titles'].values()))
            for lang in builder.LANGS:
                self.assertEqual(len(entry['copy'][lang]['notes']), 2)

    def test_beauvoir_keeps_agency_and_author_accountability(self):
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('beauvoir', 'zh')))
        for phrase in ('1944年', '1945年', '1965年', '朗布兰', '师生关系',
                       '受过压迫', '专一', '诺贝尔奖', '第五卷'):
            self.assertIn(phrase, zh)
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('beauvoir', 'en')))
        for phrase in ('Bianca Lamblin', 'certificate of innocence', 'exclusivity',
                       'A human-built wall', 'Book V'):
            self.assertIn(phrase, en)
        self.assertNotIn('Not second-class. The second to be seen.', en)

    def test_quine_keeps_the_dispute_and_distinct_questions(self):
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('quine', 'zh')))
        for phrase in ('先天综合', '红杯子', '卡尔纳普', '格赖斯', '斯特劳森',
                       '双陆棋', '西田', '同意与强迫'):
            self.assertIn(phrase, zh)
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('quine', 'en')))
        for phrase in ('synthetic a priori', 'chipped', 'Grice and Strawson',
                       'explicit stipulations', 'consent and coercion'):
            self.assertIn(phrase.lower(), en.lower())

    def test_tesla_keeps_engineering_and_patent_boundaries(self):
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('tesla', 'zh')))
        for phrase in ('1887', '1888', '1895', '1896', '1917', '1943', 'FBI'):
            self.assertIn(phrase, zh)
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('tesla', 'en')))
        for phrase in ('O\'Neill', 'Office of Alien Property', 'Lodge', 'Stone',
                       'high-voltage DC', 'Westinghouse'):
            self.assertIn(phrase, en)
        self.assertNotIn('Tesla was the sole inventor of radio', en)

    def test_batch_18_traditional_is_complete_and_reviewed(self):
        for slug in ('beauvoir', 'quine', 'tesla'):
            sections = self.entries[slug]['copy']['zh-hant']['sections']
            source = builder.source_body(slug, 'zh')
            self.assertEqual(len(re.findall(r'<h2\b', source)), len(sections))
            self.assertEqual(len(re.findall(r'<p\b', source)),
                             sum(len(s['paragraphs']) for s in sections))
            text = ' '.join(p for s in sections for p in s['paragraphs'])
            for wrong in ('反復', '重復', '想象', '煙鬥', '賬', '咨詢'):
                self.assertNotIn(wrong, text)

    def test_batch_18_navigation_metadata_and_update_card(self):
        from html.parser import HTMLParser
        class Metadata(HTMLParser):
            def __init__(self, text):
                super().__init__()
                self.descriptions, self.links = [], []
                self.feed(text)
            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                if tag == 'meta' and d.get('name') == 'description':
                    self.descriptions.append(attrs)
                if tag == 'a' and 'href' in d:
                    self.links.append(d['href'])
        chain = ['sartre', 'beauvoir', 'quine', 'tesla', 'edison']
        for i, slug in enumerate(chain[1:-1], 1):
            source = Metadata(builder.source_path_for(slug).read_text(encoding='utf-8'))
            self.assertEqual(len(source.descriptions), 1)
            self.assertEqual({k for k, v in source.descriptions[0]}, {'name', 'content'})
            for lang in builder.LANGS:
                page = Metadata((builder.SERIES / lang / (slug + '.html')).read_text(encoding='utf-8'))
                self.assertIn(chain[i - 1] + '.html', page.links)
                self.assertIn(chain[i + 1] + '.html', page.links)
        latest = (builder.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertEqual(latest.count('data-update-id="2026-09-22-great-lives-batch-18-full"'), 1)
        for slug in chain[1:-1]:
            self.assertIn('essays/mingren/' + slug + '.html', Metadata(latest).links)

    def test_batch_19_all_three_are_reviewed_full_editions(self):
        for number, slug in enumerate(('edison', 'heisenberg', 'bohr'), 55):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual((entry['number'], entry['movement']), (number, 4))
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                builder.validate_full_edition(entry)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full'
                                    for e in self.entries.values()), 58)

    def test_batch_19_preserves_nine_sections_and_full_prose(self):
        for slug in ('edison', 'heisenberg', 'bohr'):
            entry = self.entries[slug]
            for lang in ('zh', 'en'):
                source = builder.source_body(slug, lang)
                self.assertEqual(len(re.findall(r'<h2\b', source)), 9)
                self.assertGreaterEqual(len(re.findall(r'<p\b', source)), 54)
                body = html.unescape(re.sub(r'<[^>]+>', ' ', source))
                units = len(re.sub(r'\s+', '', body)) if lang == 'zh' else len(body.split())
                self.assertGreaterEqual(units, 3500 if lang == 'zh' else 1800)
            for lang, copy in entry['copy'].items():
                with self.subTest(slug=slug, lang=lang):
                    self.assertEqual(len(copy['sections']), 9)
                    self.assertEqual([s['covers'][0] for s in copy['sections']],
                                     entry['edition']['required_topics'])
                    paragraphs = [p for s in copy['sections'] for p in s['paragraphs']]
                    self.assertGreaterEqual(len(paragraphs), 54)
                    self.assertGreaterEqual(len(copy['sections'][-1]['paragraphs']), 6)
                    body = ' '.join(paragraphs)
                    cjk = lang in ('zh-hant', 'ja', 'ko')
                    units = len(re.sub(r'\s+', '', body)) if cjk else len(body.split())
                    floor = 3500 if lang == 'zh-hant' else 4000 if cjk else 1800
                    self.assertGreaterEqual(units, floor)

    def test_batch_19_has_localized_notes_and_sources(self):
        for slug in ('edison', 'heisenberg', 'bohr'):
            entry = self.entries[slug]
            self.assertGreaterEqual(len(entry['sources']), 3)
            for source in entry['sources']:
                self.assertEqual(set(source['titles']), set(builder.LANGS))
                self.assertTrue(source['url'].startswith('https://'))
                self.assertTrue(all(source['titles'].values()))
            for lang in builder.LANGS:
                self.assertEqual(len(entry['copy'][lang]['notes']), 2)

    def test_edison_keeps_collaboration_and_a_safe_tribute(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('edison', 'en')))
        for phrase in ('cotton', 'Swan', 'Dickson', 'Brown', 'Hoover', '1892', '1931'):
            self.assertIn(phrase, en)
        self.assertNotIn('No one before or since has come close.', en)
        self.assertNotIn('Tesla invented alternating current. Edison invented how to invent.', en)
        self.assertNotIn('he never built a power station', en)

    def test_heisenberg_keeps_physics_and_history_distinct(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('heisenberg', 'en')))
        for phrase in ('Born', 'Jordan', '1925', '1927', '1941', '1945', '1961', 'Farm Hall'):
            self.assertIn(phrase, en)
        self.assertNotIn('What you cannot observe does not exist.', en)
        self.assertNotIn('He waited thirty-five years.', en)

    def test_bohr_keeps_complementarity_and_responsibility(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('bohr', 'en')))
        for phrase in ('1912', '1913', '1935', '1943', '1950', 'Nishida',
                       'local hidden-variable', 'United Nations'):
            self.assertIn(phrase, en)
        self.assertNotIn('There are no hidden variables.', en)
        self.assertNotIn('Bohr won the debate.', en)

    def test_batch_19_traditional_is_complete_and_reviewed(self):
        for slug in ('edison', 'heisenberg', 'bohr'):
            sections = self.entries[slug]['copy']['zh-hant']['sections']
            source = builder.source_body(slug, 'zh')
            self.assertEqual(len(re.findall(r'<h2\b', source)), len(sections))
            self.assertEqual(len(re.findall(r'<p\b', source)),
                             sum(len(s['paragraphs']) for s in sections))
            text = ' '.join(p for s in sections for p in s['paragraphs'])
            for wrong in ('反復', '重復', '想象', '煙鬥', '賬', '咨詢'):
                self.assertNotIn(wrong, text)

    def test_batch_19_navigation_metadata_and_update_card(self):
        from html.parser import HTMLParser
        class Metadata(HTMLParser):
            def __init__(self, text):
                super().__init__()
                self.descriptions, self.links = [], []
                self.feed(text)
            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                if tag == 'meta' and d.get('name') == 'description':
                    self.descriptions.append(attrs)
                if tag == 'a' and 'href' in d:
                    self.links.append(d['href'])
        chain = ['tesla', 'edison', 'heisenberg', 'bohr', 'tolstoy']
        for i, slug in enumerate(chain[1:-1], 1):
            source = Metadata(builder.source_path_for(slug).read_text(encoding='utf-8'))
            self.assertEqual(len(source.descriptions), 1)
            self.assertEqual({k for k, v in source.descriptions[0]}, {'name', 'content'})
            for lang in builder.LANGS:
                page = Metadata((builder.SERIES / lang / (slug + '.html')).read_text(encoding='utf-8'))
                self.assertIn(chain[i - 1] + '.html', page.links)
                self.assertIn(chain[i + 1] + '.html', page.links)
        latest = (builder.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertEqual(latest.count('data-update-id="2026-09-22-great-lives-batch-19-full"'), 1)
        for slug in chain[1:-1]:
            self.assertIn('essays/mingren/' + slug + '.html', Metadata(latest).links)

    def test_batch_20_all_three_are_reviewed_full_editions(self):
        for number, slug in enumerate(('tolstoy', 'shakespeare', 'spinoza'), 58):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual((entry['number'], entry['movement']), (number, 4))
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                builder.validate_full_edition(entry)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full'
                                    for e in self.entries.values()), 61)

    def test_batch_20_preserves_nine_sections_and_full_prose(self):
        for slug in ('tolstoy', 'shakespeare', 'spinoza'):
            entry = self.entries[slug]
            for lang in ('zh', 'en'):
                source = builder.source_body(slug, lang)
                self.assertEqual(len(re.findall(r'<h2\b', source)), 9)
                self.assertGreaterEqual(len(re.findall(r'<p\b', source)), 54)
                body = html.unescape(re.sub(r'<[^>]+>', ' ', source))
                units = len(re.sub(r'\s+', '', body)) if lang == 'zh' else len(body.split())
                self.assertGreaterEqual(units, 3500 if lang == 'zh' else 1800)
            for lang, copy in entry['copy'].items():
                with self.subTest(slug=slug, lang=lang):
                    self.assertEqual(len(copy['sections']), 9)
                    self.assertEqual([s['covers'][0] for s in copy['sections']],
                                     entry['edition']['required_topics'])
                    paragraphs = [p for s in copy['sections'] for p in s['paragraphs']]
                    self.assertGreaterEqual(len(paragraphs), 54)
                    self.assertGreaterEqual(len(copy['sections'][-1]['paragraphs']), 6)
                    body = ' '.join(paragraphs)
                    cjk = lang in ('zh-hant', 'ja', 'ko')
                    units = len(re.sub(r'\s+', '', body)) if cjk else len(body.split())
                    floor = 3500 if lang == 'zh-hant' else 4000 if cjk else 1800
                    self.assertGreaterEqual(units, floor)

    def test_batch_20_has_localized_notes_and_sources(self):
        for slug in ('tolstoy', 'shakespeare', 'spinoza'):
            entry = self.entries[slug]
            self.assertGreaterEqual(len(entry['sources']), 3)
            for source in entry['sources']:
                self.assertEqual(set(source['titles']), set(builder.LANGS))
                self.assertTrue(source['url'].startswith('https://'))
                self.assertTrue(all(source['titles'].values()))
            for lang in builder.LANGS:
                self.assertEqual(len(entry['copy'][lang]['notes']), 2)

    def test_tolstoy_keeps_family_agency_and_late_fiction(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('tolstoy', 'en')))
        for phrase in ('Sofia', 'Resurrection', 'Hadji Murad', 'Gerasim', 'Gandhi'):
            self.assertIn(phrase.lower(), en.lower())
        self.assertNotIn('he stopped writing fiction', en.lower())
        zh = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('tolstoy', 'zh')))
        for phrase in ('11月10日', '10月28日', '11月20日', '11月7日', '儿子', '空椅子'):
            self.assertIn(phrase, zh)

    def test_shakespeare_keeps_evidence_and_interpretation_distinct(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('shakespeare', 'en')))
        for phrase in ('Quiney', '1598', 'Hand D', 'Fletcher', 'Caliban', 'Ariel', '1623',
                       'whether Shakespeare received it is uncertain', 'eighteen previously unprinted'):
            self.assertIn(phrase, en)
        self.assertNotIn('We know nothing about Shakespeare', en)
        self.assertNotIn('no letters survive at all', en.lower())

    def test_spinoza_keeps_finite_difference_and_supported_independence(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('spinoza', 'en')))
        for phrase in ('1656', '1663', '1670', '1673', '1677', '1678', 'Fabritius',
                       'financial help', 'stronger affect', 'nineteen lives'):
            self.assertIn(phrase, en)
        self.assertNotIn('The continuation prompt notes', en)
        self.assertNotIn('There are no differences', en)
        self.assertNotIn('forgotten for two hundred years', en.lower())

    def test_batch_20_traditional_is_complete_and_reviewed(self):
        for slug in ('tolstoy', 'shakespeare', 'spinoza'):
            sections = self.entries[slug]['copy']['zh-hant']['sections']
            source = builder.source_body(slug, 'zh')
            self.assertEqual(len(re.findall(r'<h2\b', source)), len(sections))
            self.assertEqual(len(re.findall(r'<p\b', source)),
                             sum(len(s['paragraphs']) for s in sections))
            text = ' '.join(p for s in sections for p in s['paragraphs'])
            for wrong in ('反復', '重復', '想象', '煙鬥', '賬', '咨詢'):
                self.assertNotIn(wrong, text)

    def test_batch_20_navigation_metadata_and_update_card(self):
        from html.parser import HTMLParser
        class Metadata(HTMLParser):
            def __init__(self, text):
                super().__init__()
                self.descriptions, self.links = [], []
                self.feed(text)
            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                if tag == 'meta' and d.get('name') == 'description':
                    self.descriptions.append(attrs)
                if tag == 'a' and 'href' in d:
                    self.links.append(d['href'])
        chain = ['bohr', 'tolstoy', 'shakespeare', 'spinoza', 'aristotle']
        for i, slug in enumerate(chain[1:-1], 1):
            source = Metadata(builder.source_path_for(slug).read_text(encoding='utf-8'))
            self.assertEqual(len(source.descriptions), 1)
            self.assertEqual({k for k, v in source.descriptions[0]}, {'name', 'content'})
            for lang in builder.LANGS:
                page = Metadata((builder.SERIES / lang / (slug + '.html')).read_text(encoding='utf-8'))
                self.assertIn(chain[i - 1] + '.html', page.links)
                self.assertIn(chain[i + 1] + '.html', page.links)
        latest = (builder.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertEqual(latest.count('data-update-id="2026-09-22-great-lives-batch-20-full"'), 1)
        for slug in chain[1:-1]:
            self.assertIn('essays/mingren/' + slug + '.html', Metadata(latest).links)

    def test_batch_21_all_three_are_reviewed_full_editions(self):
        for number, slug in enumerate(('aristotle', 'faraday', 'maxwell'), 61):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual((entry['number'], entry['movement']), (number, 5))
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                builder.validate_full_edition(entry)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full'
                                    for e in self.entries.values()), 64)

    def test_batch_21_preserves_nine_sections_and_full_prose(self):
        for slug in ('aristotle', 'faraday', 'maxwell'):
            entry = self.entries[slug]
            for lang in ('zh', 'en'):
                source = builder.source_body(slug, lang)
                self.assertEqual(len(re.findall(r'<h2\b', source)), 9)
                self.assertGreaterEqual(len(re.findall(r'<p\b', source)), 54)
                body = html.unescape(re.sub(r'<[^>]+>', ' ', source))
                units = len(re.sub(r'\s+', '', body)) if lang == 'zh' else len(body.split())
                self.assertGreaterEqual(units, 3500 if lang == 'zh' else 1800)
            for lang, copy in entry['copy'].items():
                with self.subTest(slug=slug, lang=lang):
                    self.assertEqual(len(copy['sections']), 9)
                    self.assertEqual([s['covers'][0] for s in copy['sections']],
                                     entry['edition']['required_topics'])
                    paragraphs = [p for s in copy['sections'] for p in s['paragraphs']]
                    self.assertGreaterEqual(len(paragraphs), 54)
                    self.assertGreaterEqual(len(copy['sections'][-1]['paragraphs']), 8)
                    body = ' '.join(paragraphs)
                    cjk = lang in ('zh-hant', 'ja', 'ko')
                    units = len(re.sub(r'\s+', '', body)) if cjk else len(body.split())
                    floor = 3500 if lang == 'zh-hant' else 4000 if cjk else 1800
                    self.assertGreaterEqual(units, floor)

    def test_batch_21_has_localized_notes_and_sources(self):
        for slug in ('aristotle', 'faraday', 'maxwell'):
            entry = self.entries[slug]
            self.assertGreaterEqual(len(entry['sources']), 3)
            for source in entry['sources']:
                self.assertEqual(set(source['titles']), set(builder.LANGS))
                self.assertTrue(source['url'].startswith('https://'))
                self.assertTrue(all(source['titles'].values()))
            for lang in builder.LANGS:
                self.assertEqual(len(entry['copy'][lang]['notes']), 2)

    def test_aristotle_keeps_inquiry_and_exclusion_visible(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('aristotle', 'en'))).lower()
        for phrase in ('plato', 'lyceum', 'slavery', 'observation', 'alexander'):
            self.assertIn(phrase, en)
        for old_error in ('he classified whales as mammals', 'every why gets an answer',
                          'stopping does (the law of inertia)', 'no one remembered there was anything underneath'):
            self.assertNotIn(old_error, en)

    def test_faraday_keeps_theory_light_and_communication(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('faraday', 'en'))).lower()
        for phrase in ('marcet', 'davy', '1831', '1845', '1857', 'hampton', 'sarah'):
            self.assertIn(phrase, en)
        for old_error in ('he could not write it down', 'only with maxwell did he see the proof',
                          'lived above the royal institution for the rest of his life',
                          "a bookbinder's son, a blacksmith's grandson"):
            self.assertNotIn(old_error, en)

    def test_maxwell_keeps_shared_experiment_and_historical_layers(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('maxwell', 'en'))).lower()
        for phrase in ('1845', '1864', '1865', '1873', '1874', 'heaviside', 'hertz', 'katherine', 'sutton'):
            self.assertIn(phrase, en)
        for old_error in ('faraday never said anything about light', 'maxwell was a mathematician who rarely experimented',
                          'electricity is light. magnetism is light', 'routh, whom almost no one remembers',
                          'he chose maxwell, abandoned newton'):
            self.assertNotIn(old_error, en)

    def test_batch_21_traditional_is_complete_and_reviewed(self):
        for slug in ('aristotle', 'faraday', 'maxwell'):
            sections = self.entries[slug]['copy']['zh-hant']['sections']
            source = builder.source_body(slug, 'zh')
            self.assertEqual(len(re.findall(r'<h2\b', source)), len(sections))
            self.assertEqual(len(re.findall(r'<p\b', source)),
                             sum(len(s['paragraphs']) for s in sections))
            text = ' '.join(p for s in sections for p in s['paragraphs'])
            for wrong in ('反復', '重復', '想象', '煙鬥', '賬', '咨詢'):
                self.assertNotIn(wrong, text)

    def test_batch_21_navigation_metadata_and_update_card(self):
        from html.parser import HTMLParser
        class Metadata(HTMLParser):
            def __init__(self, text):
                super().__init__()
                self.descriptions, self.links = [], []
                self.feed(text)
            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                if tag == 'meta' and d.get('name') == 'description':
                    self.descriptions.append(attrs)
                if tag == 'a' and 'href' in d:
                    self.links.append(d['href'])
        chain = ['spinoza', 'aristotle', 'faraday', 'maxwell', 'joanofarc']
        for i, slug in enumerate(chain[1:-1], 1):
            source = Metadata(builder.source_path_for(slug).read_text(encoding='utf-8'))
            self.assertEqual(len(source.descriptions), 1)
            self.assertEqual({k for k, v in source.descriptions[0]}, {'name', 'content'})
            for lang in builder.LANGS:
                page = Metadata((builder.SERIES / lang / (slug + '.html')).read_text(encoding='utf-8'))
                self.assertIn(chain[i - 1] + '.html', page.links)
                self.assertIn(chain[i + 1] + '.html', page.links)
        latest = (builder.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertEqual(latest.count('data-update-id="2026-09-22-great-lives-batch-21-full"'), 1)
        for slug in chain[1:-1]:
            self.assertIn('essays/mingren/' + slug + '.html', Metadata(latest).links)

    def test_batch_22_all_three_are_reviewed_full_editions(self):
        for number, slug in enumerate(('joanofarc', 'wilde', 'ramanujan'), 64):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual((entry['number'], entry['movement']), (number, 5))
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                builder.validate_full_edition(entry)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full'
                                    for e in self.entries.values()), 67)

    def test_batch_22_preserves_nine_sections_and_full_prose(self):
        for slug in ('joanofarc', 'wilde', 'ramanujan'):
            entry = self.entries[slug]
            for lang in ('zh', 'en'):
                source = builder.source_body(slug, lang)
                self.assertEqual(len(re.findall(r'<h2\b', source)), 9)
                self.assertGreaterEqual(len(re.findall(r'<p\b', source)), 48)
                body = html.unescape(re.sub(r'<[^>]+>', ' ', source))
                units = len(re.sub(r'\s+', '', body)) if lang == 'zh' else len(body.split())
                self.assertGreaterEqual(units, 3500 if lang == 'zh' else 1800)
            for lang, copy in entry['copy'].items():
                with self.subTest(slug=slug, lang=lang):
                    self.assertEqual(len(copy['sections']), 9)
                    self.assertEqual([s['covers'][0] for s in copy['sections']],
                                     entry['edition']['required_topics'])
                    paragraphs = [p for s in copy['sections'] for p in s['paragraphs']]
                    self.assertGreaterEqual(len(paragraphs), 48)
                    self.assertGreaterEqual(len(copy['sections'][-1]['paragraphs']), 6)
                    body = ' '.join(paragraphs)
                    cjk = lang in ('zh-hant', 'ja', 'ko')
                    units = len(re.sub(r'\s+', '', body)) if cjk else len(body.split())
                    floor = 3500 if lang == 'zh-hant' else 4000 if cjk else 1800
                    self.assertGreaterEqual(units, floor)

    def test_batch_22_has_localized_notes_and_sources(self):
        for slug in ('joanofarc', 'wilde', 'ramanujan'):
            entry = self.entries[slug]
            self.assertGreaterEqual(len(entry['sources']), 3)
            for source in entry['sources']:
                self.assertEqual(set(source['titles']), set(builder.LANGS))
                self.assertTrue(source['url'].startswith('https://'))
                self.assertTrue(all(source['titles'].values()))
            for lang in builder.LANGS:
                self.assertEqual(len(entry['copy'][lang]['notes']), 2)

    def test_joan_keeps_agency_trial_and_rehabilitation_distinct(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('joanofarc', 'en'))).lower()
        for phrase in ('1431', '1456', '1920', 'charles', 'fear'):
            self.assertIn(phrase, en)
        self.assertRegex(en, 'orl[eé]ans')
        for old_error in ('she simply did not see them', 'joan built nothing',
                          'both killed by their own city', 'she never once treated anyone as a means',
                          'joan does not know. but she arrives first'):
            self.assertNotIn(old_error, en)

    def test_wilde_keeps_specific_love_without_a_martyrdom_requirement(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('wilde', 'en'))).lower()
        for phrase in ('queensberry', '1895', 'dorian', 'douglas', 'turing', '2013', '2017'):
            self.assertIn(phrase, en)
        for old_error in ('had he run, the sentence would have been empty',
                          'but if she had, she would not have', 'they are all saints',
                          'turing said nothing', 'his only work was the ballad'):
            self.assertNotIn(old_error, en)

    def test_ramanujan_keeps_proof_training_and_other_people_visible(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('ramanujan', 'en'))).lower()
        for phrase in ('1913', 'hardy', 'littlewood', 'proof', '1729', 'positive', 'janaki'):
            self.assertIn(phrase, en)
        for old_error in ('the formulas know they are true', 'proof is the church of mathematics',
                          'both had seen too much', 'he proved the non-closure of constructs',
                          'he had only formulas'):
            self.assertNotIn(old_error, en)

    def test_batch_22_traditional_is_complete_and_reviewed(self):
        for slug in ('joanofarc', 'wilde', 'ramanujan'):
            sections = self.entries[slug]['copy']['zh-hant']['sections']
            source = builder.source_body(slug, 'zh')
            self.assertEqual(len(re.findall(r'<h2\b', source)), len(sections))
            self.assertEqual(len(re.findall(r'<p\b', source)),
                             sum(len(s['paragraphs']) for s in sections))
            text = ' '.join(p for s in sections for p in s['paragraphs'])
            for wrong in ('反復', '重復', '想象', '煙鬥', '賬', '咨詢'):
                self.assertNotIn(wrong, text)

    def test_batch_22_navigation_metadata_and_update_card(self):
        from html.parser import HTMLParser
        class Metadata(HTMLParser):
            def __init__(self, text):
                super().__init__()
                self.descriptions, self.links = [], []
                self.feed(text)
            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                if tag == 'meta' and d.get('name') == 'description':
                    self.descriptions.append(attrs)
                if tag == 'a' and 'href' in d:
                    self.links.append(d['href'])
        chain = ['maxwell', 'joanofarc', 'wilde', 'ramanujan', 'oppenheimer']
        for i, slug in enumerate(chain[1:-1], 1):
            source = Metadata(builder.source_path_for(slug).read_text(encoding='utf-8'))
            self.assertEqual(len(source.descriptions), 1)
            self.assertEqual({k for k, v in source.descriptions[0]}, {'name', 'content'})
            for lang in builder.LANGS:
                page = Metadata((builder.SERIES / lang / (slug + '.html')).read_text(encoding='utf-8'))
                self.assertIn(chain[i - 1] + '.html', page.links)
                self.assertIn(chain[i + 1] + '.html', page.links)
        latest = (builder.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertEqual(latest.count('data-update-id="2026-09-22-great-lives-batch-22-full"'), 1)
        for slug in chain[1:-1]:
            self.assertIn('essays/mingren/' + slug + '.html', Metadata(latest).links)

    def test_batch_23_all_three_are_reviewed_full_editions(self):
        for number, slug in enumerate(('oppenheimer', 'charlottebronte', 'emilybronte'), 67):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual((entry['number'], entry['movement']), (number, 5))
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                builder.validate_full_edition(entry)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full'
                                    for e in self.entries.values()), 70)

    def test_batch_23_preserves_nine_sections_and_full_prose(self):
        for slug in ('oppenheimer', 'charlottebronte', 'emilybronte'):
            entry = self.entries[slug]
            for lang in ('zh', 'en'):
                source = builder.source_body(slug, lang)
                self.assertEqual(len(re.findall(r'<h2\b', source)), 9)
                self.assertGreaterEqual(len(re.findall(r'<p\b', source)), 48)
                body = html.unescape(re.sub(r'<[^>]+>', ' ', source))
                units = len(re.sub(r'\s+', '', body)) if lang == 'zh' else len(body.split())
                self.assertGreaterEqual(units, 3500 if lang == 'zh' else 1800)
            for lang, copy in entry['copy'].items():
                with self.subTest(slug=slug, lang=lang):
                    self.assertEqual(len(copy['sections']), 9)
                    self.assertEqual([s['covers'][0] for s in copy['sections']],
                                     entry['edition']['required_topics'])
                    paragraphs = [p for s in copy['sections'] for p in s['paragraphs']]
                    self.assertGreaterEqual(len(paragraphs), 48)
                    self.assertGreaterEqual(len(copy['sections'][-1]['paragraphs']), 6)
                    body = ' '.join(paragraphs)
                    cjk = lang in ('zh-hant', 'ja', 'ko')
                    units = len(re.sub(r'\s+', '', body)) if cjk else len(body.split())
                    floor = 3500 if lang == 'zh-hant' else 4000 if cjk else 1800
                    self.assertGreaterEqual(units, floor)

    def test_batch_23_has_localized_notes_and_sources(self):
        for slug in ('oppenheimer', 'charlottebronte', 'emilybronte'):
            entry = self.entries[slug]
            self.assertGreaterEqual(len(entry['sources']), 3)
            for source in entry['sources']:
                self.assertEqual(set(source['titles']), set(builder.LANGS))
                self.assertTrue(source['url'].startswith('https://'))
                self.assertTrue(all(source['titles'].values()))
            for lang in builder.LANGS:
                self.assertEqual(len(entry['copy'][lang]['notes']), 2)

    def test_oppenheimer_keeps_responsibility_and_procedure_distinct(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('oppenheimer', 'en'))).lower()
        for phrase in ('1945', '1965', '1949', '1951', '1954', '2022', 'hiroshima', 'nagasaki'):
            self.assertIn(phrase, en)
        for old_error in ('the ash on his hands is not evidence of guilt',
                          'he paid it on behalf of those who come after',
                          'nearly the same as being burned', 'the formulas knew they were true'):
            self.assertNotIn(old_error, en)

    def test_charlotte_keeps_love_without_a_debt_or_entitlement(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('charlottebronte', 'en'))).lower()
        for phrase in ('bertha', 'currer', '1854', '1855', 'rochester', 'villette'):
            self.assertIn(phrase, en)
        for old_error in ('you no longer belong only to yourself',
                          'duty to be worthy of being loved', 'she herself held that right for less than a year',
                          "a woman's name could not get a book published", 'five english words'):
            self.assertNotIn(old_error, en)

    def test_emily_keeps_narrators_and_second_generation_visible(self):
        en = html.unescape(re.sub(r'<[^>]+>', '', builder.source_body('emilybronte', 'en'))).lower()
        for phrase in ('nelly', 'lockwood', 'hareton', 'isabella', '1847', '1848', 'gondal'):
            self.assertIn(phrase, en)
        for old_error in ('no morals. no lessons. no one is good',
                          'two people were always one', 'she needs no instrument',
                          'the boundary between one subject and another has vanished'):
            self.assertNotIn(old_error, en)
        self.assertNotIn('记录这场谈话的是耐莉', builder.source_body('emilybronte', 'zh'))

    def test_batch_23_traditional_is_complete_and_reviewed(self):
        for slug in ('oppenheimer', 'charlottebronte', 'emilybronte'):
            sections = self.entries[slug]['copy']['zh-hant']['sections']
            source = builder.source_body(slug, 'zh')
            self.assertEqual(len(re.findall(r'<h2\b', source)), len(sections))
            self.assertEqual(len(re.findall(r'<p\b', source)),
                             sum(len(s['paragraphs']) for s in sections))
            text = ' '.join(p for s in sections for p in s['paragraphs'])
            for wrong in ('反復', '重復', '想象', '煙鬥', '賬', '咨詢'):
                self.assertNotIn(wrong, text)

    def test_batch_23_navigation_metadata_and_update_card(self):
        from html.parser import HTMLParser
        class Metadata(HTMLParser):
            def __init__(self, text):
                super().__init__()
                self.descriptions, self.links = [], []
                self.feed(text)
            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                if tag == 'meta' and d.get('name') == 'description':
                    self.descriptions.append(attrs)
                if tag == 'a' and 'href' in d:
                    self.links.append(d['href'])
        chain = ['ramanujan', 'oppenheimer', 'charlottebronte', 'emilybronte', 'boltzmann']
        for i, slug in enumerate(chain[1:-1], 1):
            source = Metadata(builder.source_path_for(slug).read_text(encoding='utf-8'))
            self.assertEqual(len(source.descriptions), 1)
            self.assertEqual({k for k, v in source.descriptions[0]}, {'name', 'content'})
            for lang in builder.LANGS:
                page = Metadata((builder.SERIES / lang / (slug + '.html')).read_text(encoding='utf-8'))
                self.assertIn(chain[i - 1] + '.html', page.links)
                self.assertIn(chain[i + 1] + '.html', page.links)
        latest = (builder.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertEqual(latest.count('data-update-id="2026-09-22-great-lives-batch-23-full"'), 1)
        for slug in chain[1:-1]:
            self.assertIn('essays/mingren/' + slug + '.html', Metadata(latest).links)

    def test_batch_24_all_three_are_reviewed_full_editions(self):
        for number, slug in enumerate(('boltzmann', 'vangogh', 'dickens'), 70):
            with self.subTest(slug=slug):
                entry = self.entries[slug]
                self.assertEqual((entry['number'], entry['movement']), (number, 5))
                self.assertEqual(entry['edition']['status'], 'full')
                self.assertEqual(set(entry['copy']), set(builder.LANGS))
                builder.validate_full_edition(entry)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full'
                                    for e in self.entries.values()), 73)

    def test_batch_24_preserves_nine_sections_and_full_prose(self):
        for slug in ('boltzmann', 'vangogh', 'dickens'):
            entry = self.entries[slug]
            for lang in ('zh', 'en'):
                source = builder.source_body(slug, lang)
                self.assertEqual(len(re.findall(r'<h2\b', source)), 9)
                self.assertGreaterEqual(len(re.findall(r'<p\b', source)), 48)
                body = html.unescape(re.sub(r'<[^>]+>', ' ', source))
                units = len(re.sub(r'\s+', '', body)) if lang == 'zh' else len(body.split())
                self.assertGreaterEqual(units, 3500 if lang == 'zh' else 1800)
            for lang, copy in entry['copy'].items():
                with self.subTest(slug=slug, lang=lang):
                    self.assertEqual(len(copy['sections']), 9)
                    self.assertEqual([s['covers'][0] for s in copy['sections']],
                                     entry['edition']['required_topics'])
                    paragraphs = [p for s in copy['sections'] for p in s['paragraphs']]
                    self.assertGreaterEqual(len(paragraphs), 48)
                    self.assertGreaterEqual(len(copy['sections'][-1]['paragraphs']), 6)
                    body = ' '.join(paragraphs)
                    cjk = lang in ('zh-hant', 'ja', 'ko')
                    units = len(re.sub(r'\s+', '', body)) if cjk else len(body.split())
                    floor = 3500 if lang == 'zh-hant' else 4000 if cjk else 1800
                    self.assertGreaterEqual(units, floor)

    def test_batch_24_has_localized_notes_and_sources(self):
        for slug in ('boltzmann', 'vangogh', 'dickens'):
            entry = self.entries[slug]
            self.assertGreaterEqual(len(entry['sources']), 3)
            for source in entry['sources']:
                self.assertEqual(set(source['titles']), set(builder.LANGS))
                self.assertTrue(source['url'].startswith('https://'))
                self.assertTrue(all(source['titles'].values()))
            for lang in builder.LANGS:
                self.assertEqual(len(entry['copy'][lang]['notes']), 4 if slug == 'dickens' else 3)

    def test_batch_24_traditional_is_complete_and_reviewed(self):
        for slug in ('boltzmann', 'vangogh', 'dickens'):
            sections = self.entries[slug]['copy']['zh-hant']['sections']
            source = builder.source_body(slug, 'zh')
            self.assertEqual(len(re.findall(r'<h2\b', source)), len(sections))
            self.assertEqual(len(re.findall(r'<p\b', source)),
                             sum(len(s['paragraphs']) for s in sections))
            text = ' '.join(p for s in sections for p in s['paragraphs'])
            for wrong in ('反復', '重復', '想象', '煙鬥', '賬', '咨詢'):
                self.assertNotIn(wrong, text)

    def test_batch_24_navigation_metadata_and_update_card(self):
        from html.parser import HTMLParser
        class Metadata(HTMLParser):
            def __init__(self, text):
                super().__init__()
                self.descriptions, self.links = [], []
                self.feed(text)
            def handle_starttag(self, tag, attrs):
                d = dict(attrs)
                if tag == 'meta' and d.get('name') == 'description':
                    self.descriptions.append(attrs)
                if tag == 'a' and 'href' in d:
                    self.links.append(d['href'])
        chain = ['emilybronte', 'boltzmann', 'vangogh', 'dickens', 'churchill']
        for i, slug in enumerate(chain[1:-1], 1):
            source = Metadata(builder.source_path_for(slug).read_text(encoding='utf-8'))
            self.assertEqual(len(source.descriptions), 1)
            self.assertEqual({k for k, v in source.descriptions[0]}, {'name', 'content'})
            for lang in builder.LANGS:
                page = Metadata((builder.SERIES / lang / (slug + '.html')).read_text(encoding='utf-8'))
                self.assertIn(chain[i - 1] + '.html', page.links)
                self.assertIn(chain[i + 1] + '.html', page.links)
        latest = (builder.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertEqual(latest.count('data-update-id="2026-09-23-great-lives-batch-24-full"'), 1)
        for slug in chain[1:-1]:
            self.assertIn('essays/mingren/' + slug + '.html', Metadata(latest).links)

    def test_batch_24_exact_paragraph_map_and_no_markdown_leaks(self):
        expected = {'boltzmann': [9,8,12,9,10,8,12,10,18],
                    'vangogh': [9,9,10,11,11,10,12,12,21],
                    'dickens': [8,10,9,9,7,11,9,8,22]}
        hume = {'zh-hant': '雙陸棋', 'ja': 'バックギャモン', 'fr': 'backgammon',
                'de': 'Backgammon', 'es': 'backgammon', 'ko': '백개먼'}
        for slug, counts in expected.items():
            for lang, copy in self.entries[slug]['copy'].items():
                self.assertEqual([len(s['paragraphs']) for s in copy['sections']], counts)
                prose = ' '.join(p for s in copy['sections'] for p in s['paragraphs'])
                self.assertIn(hume[lang], prose)
                self.assertNotRegex(prose, r'\[\^\d+\]|\*\*|ビリヤード|당구|billiards|Billard|billard|billar')
                if lang == 'zh-hant':
                    self.assertNotIn('艾米莉', prose)
                    self.assertNotIn('梵高', prose)
            self.assertIn('双陆棋', builder.source_body(slug, 'zh'))
            self.assertIn('backgammon', builder.source_body(slug, 'en'))

    def test_batch_24_keeps_factual_and_ethical_boundaries(self):
        body = {s: html.unescape(re.sub(r'<[^>]+>', '', builder.source_body(s, 'en'))).lower()
                for s in ('boltzmann', 'vangogh', 'dickens')}
        for phrase in ('isolated', 'translation', 'loschmidt', 'ostwald', '1899', '1904', 'berkeley', 'perrin'):
            self.assertIn(phrase, body['boltzmann'])
        for phrase in ('jo van gogh-bonger', 'fifty francs', '651', '903', 'unsent draft',
                       'not turn being loved into a debt', 'literary imagination'):
            self.assertIn(phrase, body['vangogh'])
        for phrase in ('bob fagin', 'catherine', 'arthur smith', 'cook', '136', '1899',
                       'september', '1860', '1870'):
            self.assertIn(phrase, body['dickens'])

    def test_070_072_local_review_has_current_receipts_for_every_language(self):
        for slug in ('boltzmann', 'vangogh', 'dickens'):
            edition = self.entries[slug]['edition']
            self.assertEqual(set(edition['source_revision']['scope']),
                             {'zh', 'en', *builder.LANGS})
            self.assertEqual(edition['pending_source_review'], [])
            current = {lang: builder.source_digest(slug, lang) for lang in ('zh', 'en')}
            self.assertEqual(edition['source_sha256'], current)
            self.assertEqual(edition['translation_source_sha256'],
                             {lang: current for lang in builder.LANGS})

    def test_070_072_keeps_the_long_bridge_ensemble(self):
        names = {
            'zh-hant': ('蘇格拉底', '休謨', '莎士比亞', '艾蜜莉'),
            'ja': ('ソクラテス', 'ヒューム', 'シェイクスピア', 'エミリー'),
            'fr': ('Socrate', 'Hume', 'Shakespeare', 'Emily'),
            'de': ('Sokrates', 'Hume', 'Shakespeare', 'Emily'),
            'es': ('Sócrates', 'Hume', 'Shakespeare', 'Emily'),
            'ko': ('소크라테스', '흄', '셰익스피어', '에밀리'),
        }
        for slug, start in (('boltzmann', 5), ('vangogh', 8), ('dickens', 8)):
            for lang in builder.LANGS:
                paragraphs = self.entries[slug]['copy'][lang]['sections'][8]['paragraphs']
                ensemble = paragraphs[start:start + 3]
                self.assertEqual(len(ensemble), 3)
                # Character density differs: the shortest intact Chinese block is 82.
                self.assertTrue(all(len(p) > 80 for p in ensemble), (slug, lang))
                for name in names[lang]:
                    self.assertIn(name, ' '.join(ensemble))

    def test_070_072_localized_endings_remain_full_narrative_endings(self):
        markers = {
            'boltzmann': {'zh-hant': '走向秩序', 'ja': '秩序へ向かって歩く',
                         'fr': 'marcher vers lui', 'de': 'der Weg auf sie zu',
                         'es': 'caminar hacia él', 'ko': '그쪽으로 걸어가는'},
            'vangogh': {'zh-hant': '全是顏色', 'ja': '色', 'fr': 'de la couleur',
                       'de': 'überall Farbe', 'es': 'queda color', 'ko': '색'},
            'dickens': {'zh-hant': '信被折疊', 'ja': '手紙を折りたたむ',
                       'fr': 'une lettre qu’on plie', 'de': 'ein Brief gefaltet',
                       'es': 'una carta al doblarse', 'ko': '편지를 접는'},
        }
        for slug, languages in markers.items():
            for lang, marker in languages.items():
                ending = self.entries[slug]['copy'][lang]['sections'][-1]['paragraphs'][-1]
                self.assertIn(marker, ending, (slug, lang))
        for slug in markers:
            hant = ' '.join(p for s in self.entries[slug]['copy']['zh-hant']['sections']
                            for p in s['paragraphs'])
            self.assertNotRegex(hant, r'斯托裡|贊美|“|”')

    def test_073_075_local_review_tracks_current_sources(self):
        for slug in ('churchill', 'roosevelt', 'schrodinger'):
            edition = self.entries[slug]['edition']
            revision = edition['source_revision']
            self.assertEqual(revision['baseline'], '3374a61')
            self.assertEqual(revision['report'], 'reports/great-lives-073-075-local-review.md')
            self.assertTrue((builder.ROOT / revision['report']).is_file())
            self.assertEqual(set(revision['scope']), {'zh', 'en', *builder.LANGS})
            self.assertEqual(edition['pending_source_review'], [])
            current = {lang: builder.source_digest(slug, lang) for lang in ('zh', 'en')}
            self.assertEqual(edition['source_sha256'], current)
            for lang in builder.LANGS:
                self.assertEqual(edition['translation_source_sha256'][lang], current)

    def test_073_075_local_review_preserves_complete_bridge_ensembles(self):
        # Freeze only the three unchanged ensemble paragraphs per edition,
        # not the surrounding scenes being edited. Baseline: 023ca2b.
        expected = {
            'churchill': (6, 'c15063ff14992a40eaadd1eba373719d9e7b9954d42679d7b1b5f24c2b5644e5'),
            'roosevelt': (6, '307190dd896285e1b618adaa42e89404624df243052a423dc3d2c32114222729'),
            'schrodinger': (4, '6b63581ec036652d196b655552d420bf1ec78c6b94ead71d82fda5c40c7e5d02'),
        }
        for slug, (start, digest) in expected.items():
            copies = self.entries[slug]['copy']
            blocks = {lang: copies[lang]['sections'][8]['paragraphs'][start:start + 3]
                      for lang in sorted(copies)}
            encoded = json.dumps(blocks, ensure_ascii=False, sort_keys=True).encode()
            self.assertEqual(hashlib.sha256(encoded).hexdigest(), digest, slug)

    def test_073_075_localized_endings_keep_their_narrative_direction(self):
        markers = {
            'churchill': {'zh-hant': '很沉。但在走', 'ja': 'それでも、歩いている',
                          'fr': 'Mais il avance', 'de': 'Doch er geht',
                          'es': 'sigue andando', 'ko': '그래도 걷는다'},
            'roosevelt': {'zh-hant': '參與建起', 'ja': 'ともに築いた',
                          'fr': 'contribué à bâtir', 'de': 'mit aufgebaut',
                          'es': 'ayudó a construir', 'ko': '함께 지은'},
            'schrodinger': {'zh-hant': '貓睡了', 'ja': '猫は眠った',
                            'fr': 'chat dort', 'de': 'Katze schläft',
                            'es': 'gato duerme', 'ko': '고양이는 잠든다'},
        }
        for slug, languages in markers.items():
            for lang, marker in languages.items():
                ending = self.entries[slug]['copy'][lang]['sections'][-1]['paragraphs'][-1]
                self.assertIn(marker, ending, (slug, lang))

    def test_batch_25_full_editions_and_source_revisions(self):
        for number, slug in enumerate(('churchill', 'roosevelt', 'schrodinger'), 73):
            entry = self.entries[slug]
            self.assertEqual((entry['number'], entry['movement']), (number, 5))
            self.assertEqual(entry['edition']['status'], 'full')
            self.assertEqual(set(entry['copy']), set(builder.LANGS))
            builder.validate_full_edition(entry)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full'
                                    for e in self.entries.values()), 76)

    def test_batch_25_complete_paragraph_maps_and_localized_notes(self):
        maps = {'churchill': [11,9,9,11,11,9,8,9,18],
                'roosevelt': [8,11,10,12,10,10,10,10,18],
                'schrodinger': [10,9,9,9,11,9,10,9,20]}
        for slug, counts in maps.items():
            entry = self.entries[slug]
            self.assertEqual(len(entry['sources']), {'churchill':25,'roosevelt':36,'schrodinger':12}[slug])
            for source in entry['sources']:
                self.assertEqual(set(source['titles']), set(builder.LANGS))
                self.assertTrue(source['url'].startswith('https://'))
            for lang, copy in entry['copy'].items():
                with self.subTest(slug=slug, lang=lang):
                    self.assertEqual([len(s['paragraphs']) for s in copy['sections']], counts)
                    self.assertEqual([s['covers'][0] for s in copy['sections']], entry['edition']['required_topics'])
                    self.assertEqual(len(copy['notes']), 3 if slug == 'churchill' else 4)
                    text = ' '.join(p for s in copy['sections'] for p in s['paragraphs'])
                    self.assertNotRegex(text, r'\[\^\d+\]|\*\*|billiards|ビリヤード|당구')
            for lang in ('zh', 'en'):
                source = builder.source_body(slug, lang)
                sections = re.split(r'<h2\b[^>]*>.*?</h2>', source, flags=re.S)[1:]
                self.assertEqual([len(re.findall(r'<p\b', s)) for s in sections], counts)
                self.assertNotRegex(source, r'\[\^\d+\]|\*\*')

    def test_batch_25_keeps_substantive_boundaries_without_editorial_asides(self):
        text = {s: html.unescape(re.sub(r'<[^>]+>', '', builder.source_body(s, 'en'))).lower()
                for s in ('churchill', 'roosevelt', 'schrodinger')}
        for term in ('1949', 'halifax', 'nanavati', '1944', 'woodford', 'backgammon',
                     'respect for someone', 'more useful afterward'):
            self.assertIn(term, text['churchill'])
        for term in ('perkins', 'korematsu', 'endo', 'sugiyama', 'september 2', 'ramp', 'two inks'):
            self.assertIn(term, text['roosevelt'])
        for term in ('probability amplitudes', 'decoherence', 'franklin', 'gosling',
                     'underage pupil', 'adult has a particular responsibility', 'literary imagination'):
            self.assertIn(term, text['schrodinger'])
        for term in ('zurich sanatorium', 'no imaginary meeting', 'this time both hands are free'):
            self.assertNotIn(term, text['schrodinger'])
        self.assertNotIn('definitive final line of dialogue', text['roosevelt'])
        self.assertIn('puts the papers in his pocket, freeing both hands, then picks up the cat', text['schrodinger'])

    def test_batch_25_navigation_sources_and_latest_card(self):
        chain = ['dickens', 'churchill', 'roosevelt', 'schrodinger', 'feynman']
        for i, slug in enumerate(chain[1:-1], 1):
            for lang in builder.LANGS:
                path = builder.SERIES / lang / (slug + '.html')
                page = path.read_text(encoding='utf-8')
                self.assertIn(f'href="{chain[i-1]}.html"', page)
                self.assertIn(f'href="{chain[i+1]}.html"', page)
                self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
                self.assertNotRegex(page, r'\[\^\d+\]')
                for href in re.findall(r'href="([^"]+)"', page):
                    url = urlsplit(html.unescape(href))
                    if not url.scheme and not url.netloc and url.path:
                        self.assertTrue((path.parent / unquote(url.path)).resolve().is_file(), href)
        latest = (builder.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertEqual(latest.count('data-update-id="2026-09-23-great-lives-batch-25-full"'), 1)
        for slug in chain[1:-1]:
            self.assertIn('href="essays/mingren/' + slug + '.html"', latest)

    def test_batch_26_complete_editions_and_paragraph_maps(self):
        maps = {'feynman': [11,9,12,11,9,11,10,9,17],
                'hawking': [9,8,9,11,10,10,8,10,20],
                'caoxueqin': [14,10,12,8,9,12,10,10,34]}
        for number, (slug, counts) in enumerate(maps.items(), 76):
            entry = self.entries[slug]
            self.assertEqual((entry['number'], entry['movement']), (number, 5))
            self.assertEqual(entry['edition']['status'], 'full')
            builder.validate_full_edition(entry)
            for lang, copy in entry['copy'].items():
                expected = ([6,11,7,18,12,9,9,12,70]
                            if slug == 'caoxueqin' and lang == 'zh-hant' else counts)
                self.assertEqual([len(s['paragraphs']) for s in copy['sections']], expected)
                self.assertEqual([s['covers'][0] for s in copy['sections']], entry['edition']['required_topics'])
                self.assertEqual(len(copy['notes']), 3)
            for lang in ('zh', 'en'):
                sections = re.split(r'<h2\b[^>]*>.*?</h2>', builder.source_body(slug, lang), flags=re.S)[1:]
                expected = ([6,11,7,18,12,9,9,12,70]
                            if slug == 'caoxueqin' else counts)
                self.assertEqual([len(re.findall(r'<p\b', s)) for s in sections], expected)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full'
                                    for e in self.entries.values()), 79)

    def test_batch_26_continuity_and_clean_public_copy(self):
        games = {'zh-hant':'雙陸棋', 'ja':'バックギャモン', 'fr':'backgammon',
                 'de':'Backgammon', 'es':'backgammon', 'ko':'백개먼'}
        for slug in ('feynman','hawking','caoxueqin'):
            for lang, copy in self.entries[slug]['copy'].items():
                text = ' '.join(p for s in copy['sections'] for p in s['paragraphs'])
                self.assertIn(games[lang], text)
                self.assertNotRegex(text, r'\[\^\d+\]|\*\*|billiards|Billard|billard|billar|ビリヤード|당구|台球|撞球')
                self.assertNotIn('v0.1', text)
                for source in self.entries[slug]['sources']:
                    self.assertEqual(set(source['titles']), set(builder.LANGS))
                    self.assertTrue(source['url'].startswith('https://'))
            self.assertIn('双陆棋', builder.source_body(slug, 'zh'))
            self.assertIn('backgammon', builder.source_body(slug, 'en'))

    def test_caoxueqin_restoration_preserves_author_landmarks(self):
        zh = html.unescape(builder.source_body('caoxueqin', 'zh'))
        en = html.unescape(builder.source_body('caoxueqin', 'en'))
        for phrase in ('四、构不可闭合', '构碎了，但人还在。人不是为构活的。人是目的。',
                       '情不是桥。情是桥合不拢的地方长出来的东西。',
                       '他看着你。他的意思是：你也是目的。'):
            self.assertIn(phrase, zh)
        for phrase in ('The Construct Cannot Close', 'The construct is shattered, but the people remain.',
                       'Qing is not the bridge. Qing is what grows where the bridge fails to close.',
                       'you, too, are an end.'):
            self.assertIn(phrase, en)
        for name in ('苏格拉底', '柏拉图', '休谟', '叔本华', '克尔凯郭尔', '图灵',
                     '契诃夫', '康托尔', '托尔斯泰', '莎士比亚', '斯宾诺莎',
                     '亚里士多德', '法拉第', '麦克斯韦', '贞德', '王尔德',
                     '拉马努金', '奥本海默', '夏洛蒂', '艾米莉', '玻尔兹曼',
                     '梵高', '狄更斯', '丘吉尔', '罗斯福', '薛定谔', '费曼',
                     '霍金', '海森堡', '玻尔', '康德'):
            self.assertIn(name, zh.split('<h2>九、情</h2>')[1])
        for wrong in ('遗民不让他改', '时代把他的书拿走了', '曹雪芹用一本未完成的书证明了它',
                      '这是最高的熵', '七十五个人', '一旦你写了结局，人就从目的降格'):
            self.assertNotIn(wrong, zh)

    def test_caoxueqin_pending_translations_keep_old_source_receipts(self):
        entry = self.entries['caoxueqin']
        edition = entry['edition']
        self.assertEqual(edition['source_revision']['scope'], ['zh', 'en', 'zh-hant'])
        self.assertEqual(set(edition['pending_source_review']), {'ja', 'fr', 'de', 'es', 'ko'})
        self.assertEqual(edition['translation_source_sha256']['zh-hant'], edition['source_sha256'])
        old = {'zh': '16745289d9e3d26bb88200c8cd453d6dc5173f185e95eeab80422b3089faee04',
               'en': 'a4b92d6e0afd60b875a23fd0763266f7d3f5253a24389c1d1b37c686c0591aca'}
        for lang in edition['pending_source_review']:
            self.assertEqual(edition['translation_source_sha256'][lang], old)

    def test_translation_receipt_cannot_silently_claim_new_source(self):
        entry = copy.deepcopy(self.entries['caoxueqin'])
        entry['edition']['pending_source_review'].remove('ja')
        with self.assertRaisesRegex(ValueError, 'review status is inconsistent'):
            builder.validate_full_edition(entry)
        entry = copy.deepcopy(self.entries['caoxueqin'])
        entry['edition']['translation_source_sha256']['ja'] = entry['edition']['source_sha256']
        with self.assertRaisesRegex(ValueError, 'review status is inconsistent'):
            builder.validate_full_edition(entry)
        entry = copy.deepcopy(self.entries['caoxueqin'])
        entry['edition']['pending_source_review'].append('zh-hant')
        with self.assertRaisesRegex(ValueError, 'invalid translation review receipts'):
            builder.validate_full_edition(entry)

    def test_batch_26_preserves_substance_without_revision_log(self):
        text = {s: html.unescape(re.sub(r'<[^>]+>', '', builder.source_body(s, 'en'))).lower()
                for s in ('feynman','hawking','caoxueqin')}
        for word in ('amplitude', 'arline', '1946', 'dyson', 'boisjoly', '1981', 'letter'):
            self.assertIn(word, text['feynman'])
        for word in ('1963', 'hand', 'cheek', 'bekenstein', 'hartle', '1983', 'assistance', 'lucasian'):
            self.assertIn(word, text['hawking'])
        for word in ('1791', 'lingguan', 'xiren', 'baochai',
                     '1763', '1764', 'merely', 'final page', 'cat'):
            self.assertIn(word, text['caoxueqin'])
        self.assertIn('he was the water beneath the bridge', text['caoxueqin'])
        for wrong in ('no engine', 'medical inventory', 'not another photograph'):
            self.assertNotIn(wrong, text['hawking'])
        for wrong in ('new proof about infinite sets', 'qing officials and ming loyalists',
                      'grade human freedom', 'quotation from jane eyre'):
            self.assertNotIn(wrong, text['caoxueqin'])

    def test_batch_26_navigation_and_latest_entry(self):
        chain = ['schrodinger','feynman','hawking','caoxueqin','comte']
        for i, slug in enumerate(chain[1:-1], 1):
            for lang in builder.LANGS:
                path = builder.SERIES / lang / (slug + '.html')
                page = path.read_text(encoding='utf-8')
                for neighbour in (chain[i-1], chain[i+1]):
                    self.assertIn(f'href="{neighbour}.html"', page)
                self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
                self.assertNotRegex(page, r'\[\^\d+\]')
        latest = (builder.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertEqual(latest.count('data-update-id="2026-09-24-great-lives-batch-26-full"'), 1)
        for slug in chain[1:-1]:
            self.assertIn('href="essays/mingren/' + slug + '.html"', latest)

    def test_batch_27_complete_editions_and_content_maps(self):
        for number, slug in enumerate(('comte', 'popper', 'dirac'), 79):
            entry = self.entries[slug]
            self.assertEqual((entry['number'], entry['movement']), (number, 6))
            self.assertEqual(entry['edition']['status'], 'full')
            builder.validate_full_edition(entry)
            for lang, copy in entry['copy'].items():
                self.assertEqual(len(copy['sections']), 8)
                self.assertEqual([s['covers'][0] for s in copy['sections']], entry['edition']['required_topics'])
                self.assertEqual(len(copy['notes']), 3)
                body = ' '.join(p for s in copy['sections'] for p in s['paragraphs'])
                self.assertNotRegex(body, r'\[\^\d+\]|\*\*|v0\.1|\\\[|\\frac')
            for lang in ('zh', 'en'):
                self.assertEqual(len(re.findall(r'<h2\b', builder.source_body(slug, lang))), 8)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full'
                                   for e in self.entries.values()), 82)

    def test_batch_27_readable_equations_in_all_editions(self):
        formulas = ('iℏ ∂ψ/∂t = (c α·p + βmc²)ψ', 'E = ±√(|p|²c² + m²c⁴)')
        for copy in self.entries['dirac']['copy'].values():
            paragraphs = [p for s in copy['sections'] for p in s['paragraphs']]
            for formula in formulas:
                self.assertEqual(paragraphs.count(formula), 1)
        for lang in ('zh', 'en'):
            body = builder.source_body('dirac', lang)
            for formula in formulas:
                self.assertEqual(body.count(formula), 1)
            self.assertNotIn('\\(', body)

    def test_batch_27_author_voice_restoration(self):
        landmarks = {
            'comte': ('按得很用力。', 'He presses hard.', '模式匹配不是认知的天花板，是认知的地板。'),
            'popper': ('先让那个人把话说完。', 'First, let the person finish speaking.', '这是本乐章的三步。'),
            'dirac': ('缝隙里有东西。方程知道。', 'There is something in the cracks. The equation knows.', '我把这个姿态叫作听方程说话。'),
        }
        for slug, (zh_end, en_end, phrase) in landmarks.items():
            zh = html.unescape(builder.source_body(slug, 'zh'))
            en = html.unescape(builder.source_body(slug, 'en'))
            self.assertTrue(zh.endswith(zh_end + '</p>'))
            self.assertTrue(en.endswith(en_end + '</p>'))
            self.assertIn(phrase, zh)
            for body in (zh, en):
                self.assertNotRegex(body, r'原稿里|原稿裡|in the original draft|this revision')
        dirac = html.unescape(builder.source_body('dirac', 'zh'))
        self.assertIn('指南针不是目的地', dirac)
        self.assertIn('接受这些前提', dirac)
        for wrong in ('一辈子只哭过一次', '因为他的美学判断一直是对的', '他的证明方式是什么？沉默。'):
            self.assertNotIn(wrong, dirac)

    def test_batch_27_traditional_retains_every_source_paragraph(self):
        for slug in ('comte', 'popper', 'dirac'):
            hant = self.entries[slug]['copy']['zh-hant']['sections']
            for lang in ('zh', 'en'):
                sections = re.split(r'<h2\b[^>]*>.*?</h2>', builder.source_body(slug, lang), flags=re.S)[1:]
                self.assertEqual([len(re.findall(r'<p\b', s)) for s in sections],
                                 [len(s['paragraphs']) for s in hant])

    def test_batch_27_other_languages_remain_pending_not_newly_approved(self):
        originals = {
            'comte': {'zh': '932c9ca318d9b72481b868c218bc8d9cf319020efc4e10222331186a528d2b7b', 'en': '45c2d64da108e5b00509f995a4f3571a31300ccc074d493a1ea4ae57edb68ac3'},
            'popper': {'zh': '6dc36e17055a26205db984fed50a953e1cf2c51961e4c554a66a0182e038aa74', 'en': '44062b7830574fc72555119b4ba5c0a0b69a052a3957ec4ff5da6d74fa2b0f02'},
            'dirac': {'zh': '5fc34703a04a17b28309831b99d8577e344b580e5a7c715069bb900244ec5ada', 'en': '4324d4e91905d2c655da15a9f328b63dfa4329ac14c6f86f2873233d05dc9a95'},
        }
        for slug, old in originals.items():
            edition = self.entries[slug]['edition']
            self.assertEqual(edition['source_revision']['scope'], ['zh', 'en', 'zh-hant'])
            self.assertEqual(edition['source_revision']['baseline'], '3374a61')
            self.assertEqual(edition['pending_source_review'], ['ja', 'fr', 'de', 'es', 'ko'])
            self.assertEqual(edition['translation_source_sha256']['zh-hant'], edition['source_sha256'])
            for lang in edition['pending_source_review']:
                self.assertEqual(edition['translation_source_sha256'][lang], old)

    def test_batch_27_substance_and_bridge_continuity(self):
        bodies = {slug: html.unescape(re.sub(r'<[^>]+>', '', builder.source_body(slug, 'en'))).lower()
                  for slug in ('comte', 'popper', 'dirac')}
        for term in ('clotilde', 'friendship', '1849', 'relative', 'observation', 'water'):
            self.assertIn(term, bodies['comte'])
        self.assertNotIn('shakespeare is on the bridge', bodies['comte'])
        for term in ('black swan', 'criterion of meaning', '1978', 'auxiliary', 'finish speaking'):
            self.assertIn(term, bodies['popper'])
        for term in ('1928', '1931', '1932', '1933', 'weyl', 'anderson', 'vacuum', 'positive-energy'):
            self.assertIn(term, bodies['dirac'])
        self.assertNotIn('before counting tears', bodies['dirac'])
        self.assertNotIn('a mouth the equation', bodies['dirac'])

    def test_batch_27_navigation_and_latest_entry(self):
        chain = ('caoxueqin', 'comte', 'popper', 'dirac', 'quyuan')
        for i, slug in enumerate(chain[1:-1], 1):
            for lang in builder.LANGS:
                page = (builder.SERIES / lang / (slug + '.html')).read_text(encoding='utf-8')
                for neighbour in (chain[i-1], chain[i+1]):
                    self.assertIn(f'href="{neighbour}.html"', page)
                self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
        latest = (builder.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertEqual(latest.count('data-update-id="2026-09-25-great-lives-batch-27-full"'), 1)
        for slug in chain[1:-1]:
            self.assertIn(f'href="essays/mingren/{slug}.html"', latest)

    def test_batch_28_full_editions_and_traditional_coverage(self):
        for number, slug in enumerate(('quyuan', 'fichte', 'mcclintock'), 82):
            entry = self.entries[slug]
            self.assertEqual((entry['number'], entry['movement']), (number, 6))
            self.assertEqual(entry['edition']['status'], 'full')
            builder.validate_full_edition(entry)
            for lang, copy in entry['copy'].items():
                self.assertEqual(len(copy['sections']), 8)
                self.assertEqual(len(copy['notes']), 3)
                expected_topics = (['kant-and-revisions', 'self-positing', 'knowers-position',
                                    'religion-nation-education', 'kant-and-revisions',
                                    'body-and-recognition', 'freedom-and-others', 'bridge']
                                   if slug == 'fichte' and lang == 'zh-hant'
                                   else entry['edition']['required_topics'])
                self.assertEqual([s['covers'][0] for s in copy['sections']], expected_topics)
                body = ' '.join(p for s in copy['sections'] for p in s['paragraphs'])
                self.assertNotRegex(body, r'\[\^\d+\]|\*\*|v0\.2|旧稿|舊稿|旧稿|옛 초고|La versión anterior|L’ancienne version|Die ältere Fassung')
            for lang in ('zh', 'en'):
                self.assertEqual(len(re.findall(r'<h2\b', builder.source_body(slug, lang))), 8)
        self.assertGreaterEqual(sum(e.get('edition', {}).get('status') == 'full' for e in self.entries.values()), 85)

    def test_batch_28_essay_substance_and_editorial_boundaries(self):
        bodies = {slug: html.unescape(re.sub(r'<[^>]+>', '', builder.source_body(slug, 'en')))
                  for slug in ('quyuan', 'fichte', 'mcclintock')}
        for body in bodies.values():
            self.assertNotRegex(body, r'earlier draft|old essay|this revision can sustain|already corrected|Self-as-an-End')
        for term in ('She Jiang', 'Orange Tree', 'Liu Xie', 'fisherman', 'remains on the bank'):
            self.assertIn(term, bodies['quyuan'])
        for term in ('Tathandlung', 'Anstoß', 'Aufforderung', '1799', 'education', 'refuse'):
            self.assertIn(term, bodies['fichte'])
        for term in ('breakage–fusion–bridge', '1953', '1961', 'gender', 'Plant again', 'Evidence still has to follow'):
            self.assertIn(term, bodies['mcclintock'])

    def test_batch_28_navigation_sources_and_latest(self):
        chain = ('dirac', 'quyuan', 'fichte', 'mcclintock', 'weil')
        for i, slug in enumerate(chain[1:-1], 1):
            urls = [s['url'] for s in self.entries[slug]['sources']]
            self.assertEqual(len(urls), len(set(urls)))
            self.assertTrue(all(u.startswith('https://') for u in urls))
            self.assertTrue(all(u.count('https://') == 1 and '[' not in u and ']' not in u for u in urls))
            for lang in builder.LANGS:
                page = (builder.SERIES / lang / (slug + '.html')).read_text(encoding='utf-8')
                for neighbour in (chain[i-1], chain[i+1]):
                    self.assertIn(f'href="{neighbour}.html"', page)
                self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
        latest = (builder.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertEqual(latest.count('data-update-id="2026-09-25-great-lives-batch-28-full"'), 1)
        for slug in chain[1:-1]:
            self.assertIn(f'href="essays/mingren/{slug}.html"', latest)

    def test_batch_28_mcclintock_opens_with_material_not_audit(self):
        for lang in ('zh', 'en'):
            body = builder.source_body('mcclintock', lang)
            paragraphs = re.findall(r'<p>(.*?)</p>', body, re.S)
            self.assertIn('玉米' if lang == 'zh' else 'kernel', paragraphs[0])
            self.assertNotIn('Ds', paragraphs[0])
        for copy in self.entries['mcclintock']['copy'].values():
            self.assertNotIn('Ds', copy['sections'][0]['paragraphs'][0])

    def test_fichte_restoration_keeps_the_knower_and_original_ending(self):
        zh = html.unescape(builder.source_body('fichte', 'zh'))
        en = html.unescape(builder.source_body('fichte', 'en'))
        self.assertEqual(re.findall(r'<h2>(.*?)</h2>', zh), [
            '一、被当成康德的人', '二、我设定我自身', '三、缝隙站在你脚下',
            '四、被指控无神论的人', '五、他和康德', '六、他和本轮其他人',
            '七、自由的第一个系统', '八、桥头'])
        for phrase in ('那个“谁”从哪里来', '认知者就是认知的地基',
                       '本系列反复遇见的“不能不”', '两只脚分别踩住两块板'):
            self.assertIn(phrase, zh)
        for phrase in ('The Crack Is Under Your Feet', 'The knower is the foundation of knowing.',
                       'the cannot-not that keeps appearing in this series', 'one foot on each side'):
            self.assertIn(phrase, en)
        self.assertTrue(zh.endswith('他不害怕。他就是从那里来的。</p>'))
        self.assertTrue(en.endswith('He is not afraid. He came from there.</p>'))
        for wrong in ('把两只脚都放回了木板', '他没有解释“我”本身', '病毒从她传给了他',
                      '被他者的余项杀死', '《离骚》第一句就是“我”'):
            self.assertNotIn(wrong, zh)
        for required in ('康德并没有忘记“我”', 'Anstoß', 'Aufforderung', '早期传记',
                         '不是说他的第一原则已经写出了同一套答案'):
            self.assertIn(required, zh)

    def test_fichte_restoration_three_versions_retain_all_paragraphs(self):
        expected = [10, 12, 13, 14, 12, 13, 15, 15]
        entry = self.entries['fichte']
        traditional = ' '.join(p for s in entry['copy']['zh-hant']['sections'] for p in s['paragraphs'])
        self.assertIn('兩隻腳分別踩住兩塊板', traditional)
        self.assertNotIn('兩只腳', traditional)
        self.assertEqual([len(s['paragraphs']) for s in entry['copy']['zh-hant']['sections']], expected)
        for lang in ('zh', 'en'):
            sections = re.split(r'<h2\b[^>]*>.*?</h2>', builder.source_body('fichte', lang), flags=re.S)[1:]
            self.assertEqual([len(re.findall(r'<p\b', s)) for s in sections], expected)

    def test_fichte_untouched_translations_keep_old_source_receipts(self):
        edition = self.entries['fichte']['edition']
        old = {'zh': '403ef562234756d999192f2f437922934ff11795649426418243a4cc641eac37',
               'en': '062d059531037658695752f989580407af615452d81a421e369c48778b4438cf'}
        self.assertEqual(edition['source_revision']['baseline'], '3374a61')
        self.assertEqual(edition['source_revision']['scope'], ['zh', 'en', 'zh-hant'])
        self.assertEqual(edition['pending_source_review'], ['ja', 'fr', 'de', 'es', 'ko'])
        self.assertEqual(edition['translation_source_sha256']['zh-hant'], edition['source_sha256'])
        for lang in edition['pending_source_review']:
            self.assertEqual(edition['translation_source_sha256'][lang], old)

    def test_mcclintock_restoration_keeps_feeling_and_original_ending(self):
        zh = html.unescape(builder.source_body('mcclintock', 'zh'))
        en = html.unescape(builder.source_body('mcclintock', 'en'))
        self.assertEqual(re.findall(r'<h2>(.*?)</h2>', zh), [
            '一、三十年', '二、对有机体的感觉', '三、她和狄拉克', '四、被否定',
            '五、她停了又没停', '六、tacit knowing', '七、一个人', '八、桥头'])
        for phrase in ('这个“先”，前面已经站着许多年', '用时间凿', '你会骑自行车',
                       '论文想成房子', '泥土和花粉', '下一篇，薇依',
                       '她没有在1953年停止发表', '转座本身在五十年代就得到'):
            self.assertIn(phrase, zh)
        for phrase in ('Years of work stood behind that first', 'Chiseling with time',
                       'You can ride a bicycle', 'papers as a house', 'Earth and pollen',
                       'In the next essay, Weil', 'She Stopped and She Didn’t'):
            self.assertIn(phrase, en)
        self.assertTrue(zh.endswith('她还是蹲着。看着那些玉米粒。微笑着。</p>'))
        self.assertTrue(en.endswith('She is still crouching. Looking at the kernels. Smiling.</p>'))
        for wrong in ('她等了三十年。现在所有人都听到了', '她的数据经得起任何检验',
                      '费希特的“我”没有身体', '被克罗内克迫害', '只卖出一幅画'):
            self.assertNotIn(wrong, zh)

    def test_mcclintock_restoration_three_versions_retain_all_paragraphs(self):
        expected = [12, 13, 11, 11, 13, 13, 12, 22]
        traditional = self.entries['mcclintock']['copy']['zh-hant']['sections']
        self.assertEqual([len(s['paragraphs']) for s in traditional], expected)
        self.assertEqual(traditional[-1]['paragraphs'][-1], '她還是蹲著。看著那些玉米粒。微笑著。')
        text = ' '.join(p for s in traditional for p in s['paragraphs'])
        for wrong in ('證明瞭', '密蘇裡', '輓留', '重復', '划線', '認准'):
            self.assertNotIn(wrong, text)
        for correct in ('證明了', '密蘇里', '挽留', '重複', '劃線', '認準'):
            self.assertIn(correct, text)
        for lang in ('zh', 'en'):
            sections = re.split(r'<h2\b[^>]*>.*?</h2>', builder.source_body('mcclintock', lang), flags=re.S)[1:]
            self.assertEqual([len(re.findall(r'<p\b', s)) for s in sections], expected)

    def test_mcclintock_untouched_translations_keep_old_source_receipts(self):
        edition = self.entries['mcclintock']['edition']
        old = {'zh': '9f690ea3c12876bb0b17ad59e3a14bb68f7891acbb9705ac059859e83981236d',
               'en': '0de013cdacb41574e8cf9cce66e84b3de255b2aab90405230f4c18720d54fad6'}
        self.assertEqual(edition['source_revision']['baseline'], '3374a61')
        self.assertEqual(edition['source_revision']['scope'], ['zh', 'en', 'zh-hant'])
        self.assertEqual(edition['pending_source_review'], ['ja', 'fr', 'de', 'es', 'ko'])
        self.assertEqual(edition['translation_source_sha256']['zh-hant'], edition['source_sha256'])
        for lang in edition['pending_source_review']:
            self.assertEqual(edition['translation_source_sha256'][lang], old)

    def test_homer_threshold_title_is_synchronized(self):
        source = builder.source_path_for('homer').read_text(encoding='utf-8')
        self.assertIn('荷马，声音进入文字的门槛', source)
        self.assertIn('Homer, at the Threshold of Voice and Text', source)
        self.assertNotIn('Homer, the Moment Sound Became Text', source)
        index = (builder.SERIES / 'index.html').read_text(encoding='utf-8')
        self.assertIn('Homer, at the Threshold of Voice and Text', index)


if __name__ == '__main__':
    unittest.main()
