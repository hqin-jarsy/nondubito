#!/usr/bin/env python3
"""Regression checks for the staged Great Lives full-text upgrade.

These checks catch dropped sections, stale source revisions, incomplete
Traditional Chinese and accidental synopsis replacement. They cannot assess
literary quality; that still requires reading every edition against its map.
"""
from __future__ import annotations

import copy
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


if __name__ == '__main__':
    unittest.main()
