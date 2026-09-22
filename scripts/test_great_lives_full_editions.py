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

    def test_homer_threshold_title_is_synchronized(self):
        source = builder.source_path_for('homer').read_text(encoding='utf-8')
        self.assertIn('荷马，声音进入文字的门槛', source)
        self.assertIn('Homer, at the Threshold of Voice and Text', source)
        self.assertNotIn('Homer, the Moment Sound Became Text', source)
        index = (builder.SERIES / 'index.html').read_text(encoding='utf-8')
        self.assertIn('Homer, at the Threshold of Voice and Text', index)


if __name__ == '__main__':
    unittest.main()
