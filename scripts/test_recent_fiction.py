#!/usr/bin/env python3
"""Focused regression checks for the Recent Fiction publishing flow."""

from __future__ import annotations

import json
import re
import unittest
from html.parser import HTMLParser
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

import build_recent_fiction as build
import build_search_index as search


VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.ids, self.links, self.articles = [], [], [], [], []
        self.schemas, self.schema_text = [], None
        self.feed(source)
        self.close()
        if self.stack:
            self.errors.append('Unclosed tags: ' + repr(self.stack))

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag not in VOID:
            self.stack.append(tag)
        if attr.get('id'):
            self.ids.append(attr['id'])
        if tag == 'a' and attr.get('href'):
            self.links.append(attr['href'])
        if tag == 'article' and 'rf-prose' in attr.get('class', '').split():
            self.articles.append(attr.get('lang'))
        if tag == 'script' and attr.get('type') == 'application/ld+json':
            self.schema_text = ''

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append('Unexpected closing tag: ' + tag)
        else:
            self.stack.pop()
        if tag == 'script' and self.schema_text is not None:
            self.schemas.append(json.loads(self.schema_text))
            self.schema_text = None

    def handle_data(self, value):
        if self.schema_text is not None:
            self.schema_text += value


class RecentFictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = build.load_books()
        cls.pages = {
            path: Page(path.read_text(encoding='utf-8'))
            for path in build.TARGET.glob('*.html')
        }

    def test_inventory_and_editions(self):
        self.assertEqual(len(build.ORDER), len(set(build.ORDER)))
        self.assertEqual(len(self.pages), len(self.books) + 1)
        for book in self.books:
            with self.subTest(book=book['slug']):
                page = self.pages[build.TARGET / (book['slug'] + '.html')]
                self.assertEqual(page.articles, ['en', 'zh-Hans', 'zh-Hant'])
                self.assertGreater(len(book['en_body'].split()), 1000)
                self.assertGreater(len(re.findall(r'[\u4e00-\u9fff]', book['zh_body'])), 1800)

    def test_sources_and_inline_links(self):
        for book in self.books:
            with self.subTest(book=book['slug']):
                sources = {item['url'] for item in book['sources']}
                kinds = {item['kind'] for item in book['sources']}
                self.assertIn('excerpt', kinds)
                self.assertIn('interview', kinds)
                for body in (book['en_body'], book['zh_body']):
                    links = re.findall(r'\]\((https://[^\s]+?)\)', body)
                    self.assertTrue(links)
                    self.assertFalse(set(links) - sources, set(links) - sources)
                    self.assertNotIn('](', re.sub(r'<a\b.*?</a>', '', build.prose(body)))

    def test_structure_and_local_links(self):
        for path, page in self.pages.items():
            with self.subTest(page=path.name):
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

    def test_dates_are_per_guide(self):
        for book in self.books:
            schema = self.pages[build.TARGET / (book['slug'] + '.html')].schemas[0]
            self.assertEqual(schema['datePublished'], book['guide_date'])
            self.assertEqual(schema['about']['datePublished'], book['book_date'])
            self.assertEqual(schema['dateModified'], book.get('updated_date', book['guide_date']))
        fixture = dict(self.books[0], guide_date='2026-10-01', updated_date='2026-10-03')
        schema = Page(build.head('Test', 'Test', 'test.html', fixture)).schemas[0]
        self.assertEqual(schema['datePublished'], '2026-10-01')
        self.assertEqual(schema['dateModified'], '2026-10-03')

    def test_library_cards_are_current(self):
        converter = build.TraditionalConverter()
        try:
            expected = build.library_section(self.books, converter)
        finally:
            converter.close()
        source = (build.ROOT / 'library.html').read_text(encoding='utf-8')
        self.assertIn(expected, source)
        self.assertEqual(expected.count('class="series-card"'), len(self.books))

    def test_original_languages_and_title_aliases(self):
        expected = {
            'jacaranda': 'fr', 'hey-good-morning': 'de', 'the-brittle-age': 'it',
            'bad-habit': 'es', 'naruse': 'ja', 'oposicion': 'es',
            'clara-y-confusa': 'es', 'madelaine-before-the-dawn': 'fr',
            'le-bastion-des-larmes': 'fr', 'the-cafe-with-no-name': 'de',
            'one-of-these-is-a-lie': 'ko', 'sympathy-tower-tokyo': 'ja',
            'bari-sanko': 'ja',
        }
        for book in self.books:
            with self.subTest(book=book['slug']):
                schema = self.pages[build.TARGET / (book['slug'] + '.html')].schemas[0]['about']
                self.assertEqual(schema['inLanguage'], expected.get(book['slug'], 'en'))
                self.assertEqual(schema['name'], book['book'])
                self.assertEqual(schema.get('alternateName', []), build.book_aliases(book))
                if book['slug'] in expected:
                    source = (build.TARGET / (book['slug'] + '.html')).read_text(encoding='utf-8')
                    search_text = search.extract_search_text(source)
                    for alias in [book['book'], *build.book_aliases(book), *book.get('search_aliases', [])]:
                        self.assertIn(alias, search_text)

    def test_inline_escapes_text_and_attributes(self):
        rendered = build.inline('A < B & [the source](https://example.com/?x=1&y=2)')
        self.assertIn('A &lt; B &amp;', rendered)
        self.assertIn('href="https://example.com/?x=1&amp;y=2"', rendered)

    def test_hubs_sitemap_and_latest_include_the_world_voices_batch(self):
        new_slugs = {
            'oposicion', 'clara-y-confusa', 'the-coin', 'madelaine-before-the-dawn',
            'le-bastion-des-larmes', 'the-cafe-with-no-name', 'one-of-these-is-a-lie',
            'the-south', 'sympathy-tower-tokyo', 'bari-sanko',
        }
        self.assertTrue(new_slugs <= set(build.ORDER))
        shelf = (build.TARGET / 'index.html').read_text(encoding='utf-8')
        sitemap = (build.ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        for book in self.books:
            if book['slug'] not in new_slugs:
                continue
            with self.subTest(book=book['slug']):
                self.assertEqual(book['guide_date'], '2026-09-11')
                self.assertIn(f'href="{book["slug"]}.html"', shelf)
                self.assertIn(f'<loc>https://nondubito.net/essays/recent-fiction/{book["slug"]}.html</loc>', sitemap)
                record = search.scan_page(build.ROOT, build.TARGET / (book['slug'] + '.html'))
                # An original-language title does not advertise a nonexistent guide translation.
                self.assertEqual(set(record['languages']), {'en', 'zh-Hans', 'zh-Hant'})
        ledger = json.loads((build.ROOT / 'data/site-updates.json').read_text(encoding='utf-8'))
        update = next(item for item in ledger['updates'] if item['id'] == '2026-09-11-recent-fiction-world-voices')
        self.assertEqual(update['languages'], ['en', 'zh', 'zh-hant'])
        self.assertIn(update['id'], (build.ROOT / 'latest.html').read_text(encoding='utf-8'))

    def test_search_descriptions_follow_each_published_language(self):
        with patch.object(search, 'collect_pages', return_value=sorted(self.pages)):
            _, chunks = search.build()
        records = {
            language: {record['u']: record for record in chunks[language]}
            for language in ('en', 'zh-Hans', 'zh-Hant')
        }
        converter = build.TraditionalConverter()
        try:
            for book in self.books:
                expected = {
                    'en': book['en_deck'],
                    'zh-Hans': book['zh_deck'],
                    'zh-Hant': converter.convert(book['zh_deck']),
                }
                url = f"essays/recent-fiction/{book['slug']}.html"
                for language, description in expected.items():
                    with self.subTest(book=book['slug'], language=language):
                        self.assertEqual(records[language][url]['x'], description)
            shelf = {
                'en': 'A life you have not met yet.',
                'zh-Hans': '还有一些人，等你翻开书才会遇见。',
                'zh-Hant': converter.convert('还有一些人，等你翻开书才会遇见。'),
            }
            for language, description in shelf.items():
                with self.subTest(book='index', language=language):
                    self.assertEqual(records[language]['essays/recent-fiction/index.html']['x'], description)
        finally:
            converter.close()

    def test_search_deck_extraction_ignores_cards_and_preserves_text(self):
        source = '''<p class="lang-en rf-card-deck">Not the page description</p>
<p data-label="deck" class='rf-article-deck lang-en'>Care &amp; <em>memory</em> together.</p>
<p class="lang-zh rf-article-deck">  记忆与照护。  </p>
<p class="rf-article-deck lang-hant">記憶與照護。</p>'''
        self.assertEqual(search.extract_recent_fiction_descriptions(source), {
            'en': 'Care & memory together.',
            'zh-Hans': '记忆与照护。',
            'zh-Hant': '記憶與照護。',
        })
        self.assertEqual(search.extract_recent_fiction_descriptions('<p class="lang-zh">正文</p>'), {})

    def test_search_keeps_other_shelves_on_the_existing_description(self):
        path = build.ROOT / 'essays' / 'literature' / 'index.html'
        expected = search.scan_page(search.ROOT, path)['description'] or ''
        with patch.object(search, 'collect_pages', return_value=[path]), patch.object(
            search, 'extract_recent_fiction_descriptions', side_effect=AssertionError('Other shelf was changed')
        ):
            _, chunks = search.build()
        for language in ('en', 'zh-Hans', 'zh-Hant'):
            with self.subTest(language=language):
                self.assertEqual(chunks[language][0]['x'], expected)


if __name__ == '__main__':
    unittest.main()
