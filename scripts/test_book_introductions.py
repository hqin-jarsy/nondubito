#!/usr/bin/env python3
"""Regression coverage for the fiction/nonfiction discovery split."""
from __future__ import annotations

import copy
import json
import re
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

import build_book_introductions as build
import build_recent_fiction as fiction
import build_search_index as search
from test_recent_fiction import Page


class BookIntroductionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = build.load_books()
        cls.paths = sorted(build.TARGET.glob('*.html')) + [build.HUB]
        cls.pages = {path: Page(path.read_text(encoding='utf-8')) for path in cls.paths}

    def test_inventory_and_reading_editions(self):
        self.assertEqual(len(build.ORDER), len(set(build.ORDER)))
        self.assertEqual(len(self.pages), len(self.books) + 2)
        for book in self.books:
            page = self.pages[build.TARGET / (book['slug'] + '.html')]
            self.assertEqual(page.articles, ['en', 'zh-Hans', 'zh-Hant'])
            self.assertGreater(len(book['en_body'].split()), 1000)
            self.assertGreater(len(re.findall(r'[\u4e00-\u9fff]', book['zh_body'])), 1800)
        for path in self.paths:
            record = search.scan_page(build.ROOT, path)
            self.assertEqual(set(record['languages']), {'en', 'zh-Hans', 'zh-Hant'})
            self.assertEqual(record['domain'], 'stories')

    def test_no_fiction_only_source_requirements(self):
        book = next(book for book in self.books if book['slug'] == 'small-is-beautiful')
        self.assertEqual(book['reading_basis'], 'excerpts-and-research')
        self.assertNotIn('interview', {item['kind'] for item in book['sources']})
        build.validate_book(book, book['slug'])
        page = (build.TARGET / 'small-is-beautiful.html').read_text(encoding='utf-8')
        self.assertTrue('Sources &amp; further reading' in page, 'Missing sources heading')
        self.assertNotIn('Author conversations &amp; sources', page)
        self.assertNotIn('may discuss more of the story', page)
        self.assertTrue('Research &amp; discussion' in page, 'Missing research source label')

    def test_publication_precision_and_collection_metadata(self):
        for book in self.books:
            page = self.pages[build.TARGET / (book['slug'] + '.html')]
            schema = page.schemas[0]
            self.assertEqual(schema['datePublished'], book['guide_date'])
            self.assertEqual(schema['about']['datePublished'], book['book_date'])
            self.assertEqual(schema['about']['genre'], book['genre_en'])
            self.assertEqual(schema['isPartOf']['url'], 'https://nondubito.net/essays/nonfiction/')
        small = self.pages[build.TARGET / 'small-is-beautiful.html'].schemas[0]
        self.assertEqual(small['about']['datePublished'], '1973')
        self.assertNotEqual(small['datePublished'], '1973')
        for path, url in [(build.HUB, 'books'), (build.TARGET / 'index.html', 'nonfiction')]:
            schema = self.pages[path].schemas[0]
            self.assertEqual(schema['@type'], 'CollectionPage')
            self.assertEqual(schema['url'], f'https://nondubito.net/essays/{url}/')

    def test_validation_rejects_inconsistent_sources_and_dates(self):
        book = copy.deepcopy(self.books[0])
        for mutation in ({'book_date': '1973-02-30'}, {'updated_date': '2020-01-01'}, {'slug': '../escape'}):
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                build.validate_book(dict(book, **mutation), book['slug'])
        for sources in ([], [dict(book['sources'][0], url='javascript:alert(1)')], book['sources'] + [book['sources'][0]]):
            with self.subTest(sources=sources), self.assertRaises(ValueError):
                build.validate_book(dict(book, sources=sources), book['slug'])
        with self.assertRaises(ValueError):
            build.validate_book(dict(book, en_body=book['en_body'] + '\n\n[Unlisted](https://example.com/)'), book['slug'])

    def test_safe_source_rendering(self):
        rendered = build.prose('A < B\n\n[Source](https://example.com/?x=1&y=2)')
        self.assertIn('A &lt; B', rendered)
        self.assertIn('x=1&amp;y=2', rendered)

    def test_structure_links_and_assets(self):
        for path, page in self.pages.items():
            with self.subTest(path=path):
                self.assertEqual(page.errors, [])
                self.assertEqual(len(page.ids), len(set(page.ids)))
                for href in page.links:
                    link = urlsplit(href)
                    if link.scheme or link.netloc:
                        continue
                    target = (path.parent / unquote(link.path)).resolve() if link.path else path
                    if target.is_dir():
                        target /= 'index.html'
                    self.assertTrue(target.is_file(), str(target))
                    if link.fragment:
                        target_page = self.pages.get(target) or Page(target.read_text(encoding='utf-8'))
                        self.assertIn(unquote(link.fragment), target_page.ids, href)
                source = path.read_text(encoding='utf-8')
                for value in re.findall(r'(?:href|src)="([^"\s]+\.(?:css|js)(?:\?[^"\s]*)?)"', source):
                    link = urlsplit(value)
                    if not link.scheme:
                        self.assertTrue((path.parent / link.path).is_file(), value)

    def test_hub_counts_and_existing_fiction_destinations(self):
        novels = fiction.load_books()
        hub = build.HUB.read_text(encoding='utf-8')
        self.assertIn(f'{len(novels) + len(self.books)} books', hub)
        self.assertIn(f'{len(novels)} books', hub)
        self.assertIn('../recent-fiction/index.html', hub)
        self.assertIn('../nonfiction/index.html', hub)
        shelf = (fiction.TARGET / 'index.html').read_text(encoding='utf-8')
        self.assertIn('../books/index.html', shelf)
        self.assertIn('../nonfiction/index.html', shelf)
        for novel in novels:
            path = fiction.TARGET / (novel['slug'] + '.html')
            self.assertTrue(path.is_file())
            self.assertEqual(Page(path.read_text(encoding='utf-8')).schemas[0]['url'], f'https://nondubito.net/essays/recent-fiction/{novel["slug"]}.html')

    def test_library_categories_and_generated_cards(self):
        source = (build.ROOT / 'library.html').read_text(encoding='utf-8')
        converter = build.TraditionalConverter()
        try:
            expected = build.library_section(self.books, converter)
        finally:
            converter.close()
        self.assertIn(expected, source)
        self.assertEqual(expected.count('class="series-card"'), len(self.books))
        self.assertEqual(re.findall(r'Category (\d\d)', source), [f'{i:02}' for i in range(1, 17)])

    def test_search_uses_each_languages_deck(self):
        with patch.object(search, 'collect_pages', return_value=self.paths):
            _, chunks = search.build()
        records = {language: {item['u']: item for item in chunks[language]} for language in ('en', 'zh-Hans', 'zh-Hant')}
        converter = build.TraditionalConverter()
        try:
            for book in self.books:
                url = f'essays/nonfiction/{book["slug"]}.html'
                for language, text in [('en', book['en_deck']), ('zh-Hans', book['zh_deck']), ('zh-Hant', converter.convert(book['zh_deck']))]:
                    self.assertEqual(records[language][url]['x'], text)
            for url in ('essays/books/index.html', 'essays/nonfiction/index.html'):
                self.assertNotEqual(records['en'][url]['x'], records['zh-Hans'][url]['x'])
                self.assertTrue(re.search(r'[\u4e00-\u9fff]', records['zh-Hant'][url]['x']))
        finally:
            converter.close()

    def test_sitemap_and_latest_are_integrated(self):
        sitemap = (build.ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        for path in self.paths:
            schema = self.pages[path].schemas[0]
            self.assertTrue(f'<loc>{schema["url"]}</loc>' in sitemap, schema['url'])
        ledger = json.loads((build.ROOT / 'data/site-updates.json').read_text(encoding='utf-8'))
        update = next(item for item in ledger['updates'] if item['id'] == '2026-09-13-nonfiction-shelf')
        self.assertEqual(update['languages'], ['en', 'zh', 'zh-hant'])
        self.assertEqual(update['url'], 'essays/books/index.html')
        self.assertIn(update['id'], (build.ROOT / 'latest.html').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
