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
import build_content_registry as registry
from test_recent_fiction import Page


# Approved 2026-09-28 / 2026-09-30 manuscripts, excluding title and bibliography.
# Keep these fixed: tests must not depend on the author's external manuscript folder.
APPROVED_CHINESE_SHA256 = {
    'the-art-of-gathering': '100ac9ddbc2b72198b4acbc0bb1fb1e66432c06e2c4ca22402432ed9c01565f6',
    'four-thousand-weeks': '2282381f50ad33b05558578776905d62bd00036ab3984e7269a1647756ace010',
    'the-craftsman': '9875d78c8deac8903c37228d9ee54d16a62292d0ba0664b29816e4314ddfd40e',
    'the-serviceberry': '982d0f096ba047af6f32a3f9c3d687a5c1c19d1abb269d791a8f674d5f18443d',
    'the-sound-of-a-wild-snail-eating': '18e78793b182d2e518a5d7d69d957df4afabbdf63528720a1be389f945b2be62',
    'palaces-for-the-people': '6997a28ba68a91fd3f94ea015a190613145d48357b5796eb2c557618859b3142',
    'the-other-significant-others': '0bca88cf752e1041c33058c02f121a12b7e8f6194ad24f815dc03d79c68b9ce0',
    'small-is-beautiful': '2a74e113f31e75bc0e82c9a6354e5527267b60edcaff26f7264e45e0ce5daf74',
    'how-to-do-nothing': '979b1156e41dd54555233eba325d7be7bdf9b1d259a10de72c2d2a2dfdb15390',
    'seeing-like-a-state': '978814a12bbda981c07165ee16e87649c91c274ca8e6765cece6df9ee3ce8efa',
    'being-mortal': 'b735de02ca685a6a0ab04fd15193e4685c291ba17c53edb1f452699662581917',
}


OCTOBER_APPROVED_CHINESE_SHA256 = {
    'a-lifes-work': '0e1b110f6b4da504d4eda6e9022fdc1548518ef62d61d1ae710c4c2560e70fd2',
    'because-internet': '637239a6f6abbd8b066f2f9fd5bb32f249c1195533a8712fef0e776cff8e4862',
    'educated': '2628a6c30c19be850dcfcc3d22cb8e5263222381ee87269c7ad9724ba45672e1',
    'the-book-of-delights': 'ed687c623974f2d2da5739de8c2ec7871f3fcd8dfb23a388858131331b13725e',
    'the-living-mountain': 'd28ce48f99592fecb7762f39e0bd018aa1093fa16363058e70576f412c4530f9',
    'the-personality-brokers': 'e0aa4183d57a3e883d976043c2479c5fdfc091532f81272d34267f3342def460',
    'ways-of-seeing': '642bef904b5531888ea754f4efba69d6d717da303f2430c43d6ead11016ba35b',
    'wintering': '0092e5a2724a5c39d1dede6583ddfe806cf4f6c3213af4d320534d228bbd54ba',
    'youre-not-listening': 'd71215fb502aa039b8f33f72333f7486d9d84abe07e839a45a656f4e58134961',
    'yowai-robotto': '0eee31815ba44b08f71a9222a1d792e87c91ccfdcef581586db452d7e60d6bb7',
}


OCTOBER_SEVENTH_APPROVED = {
    'the-year-of-magical-thinking': '87361b8c5df0593c6af91fe5e0a4cd3ae76ecd1699cf8b9fa5c0405cec05fd47',
    'the-library-book': '83d43930b3f16552db203f91eff6150ee417a0f9f3c485329b1fce4af7318c02',
    'working': '36200ebe5f3b2379fa9a7b9ca234ca11e3f71eea65c145ca4c662f690640bd5c',
    'a-field-guide-to-getting-lost': '6f67feaf75e4cf2c643d5e92c1f85bbbb1bb0b11321fee2964b98302ba81173e',
    'the-gift': 'c612c1203a07cf019460bd8c61a1f1900ec7e710b2c4aa28e33457ddefcddf83',
    'seeing-voices': '64d2c6de07c801214a264757ce8b3fdee590fbc1b7a3349248e0a1b6a97deb6b',
    'the-years': 'd1b02c6651ea99b6c3182d22584fca1edab1582078c47caf9f78fc5d9d177d8d',
    'the-shepherds-life': 'f1cb5c9b9eb13c8823a164a77698f301b534acb8e94dede2245c8d08851711d4',
    'beginners': 'bba9c030349e5c18dd784943d3705f004d7430a42d1e6bdd07c91da1da00e8cb',
    'paying-the-land': '6ecaca425f4ab8bff0de348fc7e394592a2448cc1c5544c055ff8a0f2a2cb78a',
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
                expected = 3 if slug in ('the-art-of-gathering', 'four-thousand-weeks', 'the-craftsman') else 4
                self.assertEqual(len(re.findall(r'^## ', body, re.MULTILINE)), expected)
                self.assertEqual(len(re.findall(r'^## ', book['en_body'], re.MULTILINE)), expected)
                self.assertNotRegex(body + book['en_body'], r'https?://')

    def test_interview_basis_does_not_invent_an_excerpt(self):
        book = next(book for book in self.books if book['slug'] == 'palaces-for-the-people')
        self.assertEqual(book['reading_basis'], 'interviews-and-research')
        self.assertNotIn('excerpt', {item['kind'] for item in book['sources']})
        build.validate_book(book, book['slug'])
        for missing in ('interview', 'publisher'):
            candidate = copy.deepcopy(book)
            candidate['sources'] = [item for item in book['sources'] if item['kind'] != missing]
            with self.subTest(missing=missing), self.assertRaises(ValueError):
                build.validate_book(candidate, book['slug'])
        source = (build.TARGET / 'palaces-for-the-people.html').read_text(encoding='utf-8')
        actions = re.search(r'<div class="rf-actions">(.*?)</div>', source, re.S).group(1)
        self.assertIn('About the book', actions)
        self.assertIn('查看原书资料', actions)
        self.assertNotIn('先读一段原作', actions)
        excerpt_book = copy.deepcopy(self.books[0])
        excerpt_book['sources'] = [item for item in excerpt_book['sources'] if item['kind'] != 'excerpt']
        with self.assertRaises(ValueError):
            build.validate_book(excerpt_book, excerpt_book['slug'])

    def test_seven_new_guides_have_publication_and_discovery_records(self):
        new_books = [book for book in self.books if book['guide_date'] == '2026-09-30']
        self.assertEqual(len(new_books), 7)
        ledger = json.loads((build.ROOT / 'data/site-updates.json').read_text(encoding='utf-8'))
        update = next(item for item in ledger['updates'] if item['id'] == '2026-09-30-nonfiction-seven-guides')
        self.assertEqual(update['languages'], ['en', 'zh', 'zh-hant'])
        self.assertEqual(update['kind'], 'new')
        self.assertIn(update['id'], (build.ROOT / 'latest.html').read_text(encoding='utf-8'))
        self.assertEqual(len(self.books), 32)

    def test_october_seventh_preserves_reviewed_texts_and_editions(self):
        books = {book['slug']: book for book in self.books}
        self.assertEqual({b['slug'] for b in self.books if b['guide_date'] == '2026-10-07'},
                         set(OCTOBER_SEVENTH_APPROVED))
        for slug, digest in OCTOBER_SEVENTH_APPROVED.items():
            with self.subTest(slug=slug):
                book = books[slug]
                self.assertEqual(hashlib.sha256(book['zh_body'].encode()).hexdigest(), digest)
                self.assertNotIn('updated_date', book)
                self.assertIn('未通读全书', book['zh_notice'])
                zh_sections = re.findall(r'^## ', book['zh_body'], re.M)
                self.assertEqual(len(zh_sections), len(re.findall(r'^## ', book['en_body'], re.M)))
                self.assertGreater(len(book['en_body'].split()), 1200)
                self.assertNotRegex(book['zh_body'] + book['en_body'], r'https?://|TODO|TBD')
        self.assertEqual(books['the-years']['book_language'], 'fr')
        self.assertEqual(books['the-years']['book_date'], '2008')
        self.assertIn('2010', books['seeing-voices']['zh_body'])
        self.assertIn('1990年的书评', books['seeing-voices']['zh_body'])
        self.assertIn('2006', books['the-gift']['zh_notice'])
        self.assertEqual(books['paying-the-land']['book_date'], '2020')
        self.assertEqual(books['the-shepherds-life']['book_date'], '2015')
        ledger = json.loads((build.ROOT / 'data/site-updates.json').read_text(encoding='utf-8'))
        update = next(x for x in ledger['updates'] if x['id'] == '2026-10-07-nonfiction-ten-guides')
        self.assertEqual(update['kind'], 'new')
        self.assertEqual(update['languages'], ['en', 'zh', 'zh-hant'])
        self.assertIn(update['id'], (build.ROOT / 'latest.html').read_text(encoding='utf-8'))

    def test_october_batch_uses_revised_manuscripts_and_complete_editions(self):
        books = {book['slug']: book for book in self.books}
        self.assertEqual({book['slug'] for book in self.books if book['guide_date'] == '2026-10-02'},
                         set(OCTOBER_APPROVED_CHINESE_SHA256))
        for slug, expected_hash in OCTOBER_APPROVED_CHINESE_SHA256.items():
            with self.subTest(slug=slug):
                book = books[slug]
                self.assertEqual(hashlib.sha256(book['zh_body'].encode('utf-8')).hexdigest(), expected_hash)
                self.assertNotIn('updated_date', book)  # First website publication, not a live revision.
                sections = 5 if slug == 'youre-not-listening' else 4
                for lang in ('zh', 'en'):
                    self.assertEqual(len(re.findall(r'^## ', book[f'{lang}_body'], re.M)), sections)
                    self.assertNotRegex(book[f'{lang}_body'], r'https?://|TODO|TBD')
                self.assertIn('未通读全书', book['zh_notice'])
        self.assertEqual(books['yowai-robotto']['book_language'], 'ja')
        self.assertEqual(books['yowai-robotto']['book_date'], '2012')
        self.assertEqual(books['the-personality-brokers']['book_date'], '2018')
        self.assertEqual(books['the-living-mountain']['book_date'], '1977')
        ledger = json.loads((build.ROOT / 'data/site-updates.json').read_text(encoding='utf-8'))
        update = next(item for item in ledger['updates'] if item['id'] == '2026-10-02-nonfiction-ten-guides')
        self.assertEqual(update['kind'], 'new')
        self.assertEqual(update['languages'], ['en', 'zh', 'zh-hant'])
        self.assertIn(update['id'], (build.ROOT / 'latest.html').read_text(encoding='utf-8'))

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
        # Category 04 has an id on its label; extra attributes must not hide it.
        categories = registry.parse_library_categories(build.ROOT / 'library.html')
        self.assertEqual([category['number'] for category in categories], list(range(1, 18)))

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
