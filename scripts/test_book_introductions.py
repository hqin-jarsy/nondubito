#!/usr/bin/env python3
"""Regression coverage for the fiction/nonfiction discovery split."""
from __future__ import annotations

import copy
import hashlib
import json
import re
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

import build_book_introductions as build
import build_recent_fiction as fiction
import build_search_index as search
from test_recent_fiction import Page


# Approved 2026-09-28 manuscripts, excluding their title and bibliographic line.
# Keep these fixed: tests must not depend on the author's external manuscript folder.
APPROVED_CHINESE_SHA256 = {
    'small-is-beautiful': '2a74e113f31e75bc0e82c9a6354e5527267b60edcaff26f7264e45e0ce5daf74',
    'how-to-do-nothing': '979b1156e41dd54555233eba325d7be7bdf9b1d259a10de72c2d2a2dfdb15390',
    'seeing-like-a-state': '978814a12bbda981c07165ee16e87649c91c274ca8e6765cece6df9ee3ce8efa',
    'being-mortal': 'b735de02ca685a6a0ab04fd15193e4685c291ba17c53edb1f452699662581917',
}


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
        build.validate_book(book, book['slug'])
        # An interview can enrich nonfiction research, but must not be compulsory.
        without_interviews = copy.deepcopy(book)
        without_interviews['sources'] = [
            item for item in book['sources'] if item['kind'] != 'interview'
        ]
        self.assertLess(len(without_interviews['sources']), len(book['sources']))
        build.validate_book(without_interviews, book['slug'])
        page = (build.TARGET / 'small-is-beautiful.html').read_text(encoding='utf-8')
        self.assertTrue('Sources &amp; further reading' in page, 'Missing sources heading')
        self.assertNotIn('Author conversations &amp; sources', page)
        self.assertNotIn('may discuss more of the story', page)
        self.assertTrue('Research &amp; discussion' in page, 'Missing research source label')

    def test_small_is_beautiful_revised_chinese_body(self):
        book = next(book for book in self.books if book['slug'] == 'small-is-beautiful')
        body = book['zh_body']
        self.assertTrue(body.startswith('舒马赫在英国国家煤炭局做了二十年经济学家'))
        self.assertEqual(re.findall(r'^## (.+)$', body, re.MULTILINE), [
            '多出来的收成',
            '这一年的收入，下一代的本钱',
            '公司是谁的',
            '小，也不能替人作主',
        ])
        self.assertNotRegex(body, r'(?i)porritt')

    def test_september_batch_preserves_approved_manuscripts(self):
        books = {book['slug']: book for book in self.books}
        self.assertTrue(set(APPROVED_CHINESE_SHA256).issubset(books))
        for slug, approved_hash in APPROVED_CHINESE_SHA256.items():
            with self.subTest(slug=slug):
                book = books[slug]
                body = book['zh_body']
                self.assertEqual(hashlib.sha256(body.encode('utf-8')).hexdigest(), approved_hash)
                self.assertEqual(len(re.findall(r'^## ', body, re.MULTILINE)), 4)
                self.assertEqual(len(re.findall(r'^## ', book['en_body'], re.MULTILINE)), 4)
                self.assertNotRegex(body + book['en_body'], r'https?://')

    def test_generated_bodies_use_independent_editions(self):
        converter = build.TraditionalConverter()
        try:
            for book in self.books:
                source = (build.TARGET / (book['slug'] + '.html')).read_text(encoding='utf-8')
                articles = dict(re.findall(
                    r'<article class="rf-prose [^"]+" lang="([^"]+)">(.*?)</article>',
                    source, re.DOTALL,
                ))
                # Chinese and English are independent prose, not sentence-aligned text.
                expected = {
                    'en': build.prose(book['en_body']),
                    'zh-Hans': build.prose(book['zh_body']),
                    'zh-Hant': build.prose(converter.convert(book['zh_body'])),
                }
                self.assertEqual(set(articles), set(expected))
                for language, body in expected.items():
                    with self.subTest(slug=book['slug'], language=language):
                        self.assertEqual(articles[language], body)
        finally:
            converter.close()

    def test_small_is_beautiful_retains_registered_sources(self):
        book = next(book for book in self.books if book['slug'] == 'small-is-beautiful')
        self.assertEqual({item['url'] for item in book['sources']}, {
            'https://centerforneweconomics.org/publications/buddhist-economics/',
            'https://centerforneweconomics.org/publications/writings-on-issues-of-scale-by-e-f-schumacher/',
            'https://centerforneweconomics.org/wp-content/uploads/2024/01/small-is-beautiful-revisited-study-guide.pdf',
            'https://www.cambridge.org/core/journals/contemporary-european-history/article/between-the-handloom-and-the-samson-stripper-fritz-schumachers-struggle-for-intermediate-technology/83903115DCDA6312E69C6314CAE15AC5',
            'https://www.manasjournal.org/pdf_library/VolumeXXIX_1976/XXIX-20.pdf',
            'https://centerforneweconomics.org/publications/how-to-help-them-help-themselves/',
            'https://qfp.quaker.org.uk/passage/23-57/',
            'https://aei.pitt.edu/33684/1/A218.pdf',
            'https://journals.sagepub.com/doi/10.1177/13684310241244492',
        })
        build.validate_book(book, book['slug'])

    def test_september_batch_publication_and_revision_dates(self):
        books = {book['slug']: book for book in self.books}
        self.assertEqual(books['small-is-beautiful']['guide_date'], '2026-09-13')
        self.assertEqual(books['small-is-beautiful']['updated_date'], '2026-09-28')
        self.assertEqual(books['raising-hare']['guide_date'], '2026-09-13')
        self.assertEqual(books['raising-hare']['book_date'], '2024-09-26')
        self.assertNotIn('updated_date', books['raising-hare'])
        for slug in ('how-to-do-nothing', 'seeing-like-a-state', 'being-mortal'):
            with self.subTest(slug=slug):
                self.assertEqual(books[slug]['guide_date'], '2026-09-28')
        source = (build.TARGET / 'small-is-beautiful.html').read_text(encoding='utf-8')
        self.assertIn('Revised', source)
        self.assertIn('修订', source)

    def test_publication_precision_and_collection_metadata(self):
        for book in self.books:
            page = self.pages[build.TARGET / (book['slug'] + '.html')]
            schema = page.schemas[0]
            self.assertEqual(schema['datePublished'], book['guide_date'])
            self.assertEqual(schema['dateModified'], book.get('updated_date', book['guide_date']))
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
        self.assertEqual(re.findall(r'Category (\d\d)', source), [f'{i:02}' for i in range(1, 18)])
        self.assertIn('Category 09', expected)

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
        latest = (build.ROOT / 'latest.html').read_text(encoding='utf-8')
        self.assertIn(update['id'], latest)
        updates = {item['id']: item for item in ledger['updates']}
        for identifier, kind, url in (
            ('2026-09-28-nonfiction-three-guides', 'new', 'essays/nonfiction/index.html'),
            ('2026-09-28-small-is-beautiful-rewritten', 'revised', 'essays/nonfiction/small-is-beautiful.html'),
        ):
            with self.subTest(update=identifier):
                item = updates[identifier]
                self.assertEqual(item['date'], '2026-09-28')
                self.assertEqual(item['kind'], kind)
                self.assertEqual(item['url'], url)
                self.assertEqual(item['languages'], ['en', 'zh', 'zh-hant'])
                self.assertIn(identifier, latest)


if __name__ == '__main__':
    unittest.main()
