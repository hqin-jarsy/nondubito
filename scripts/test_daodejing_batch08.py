#!/usr/bin/env python3
"""Regression checks for the reviewed eight-language eighth batch."""
import json
import re
import unittest
from urllib.parse import unquote, urlsplit

import build_daodejing_batch08 as build
from test_daodejing_sources import Page
from build_emperor_traditional import TextCollector, TraditionalConverter


class Batch08(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(build.RECEIPT.read_text())

    def test_manuscripts_and_recoverable_received_editions(self):
        for key, record in self.receipt['manuscripts'].items():
            with self.subTest(key=key):
                text = (build.DATA / f'{key}.md').read_text()
                self.assertEqual(build.digest(text.encode()), record['published_sha256'])
                self.assertEqual(text.count('\n## '), dict(zip(build.CHAPTERS, [8, 7, 9, 7, 7]))[key.split('.')[0]])
                self.assertNotIn('BODY_PLACEHOLDER', text)
                if 'received_sha256' in record:
                    size = len(text)
                    for edit in reversed(record['edits']):
                        offset, before, after = edit['offset'], edit['before'], edit['after']
                        self.assertEqual(text[offset:offset+len(after)], after)
                        text = text[:offset] + before + text[offset+len(after):]
                    self.assertEqual(build.digest(text.encode()), record['received_sha256'])
                    # Approved editorial reconstruction removes repeated false causal chains.
                    # Check scope, section coverage, frozen prose and language parity too.
                    self.assertGreater(size / len(text), .40)

    def test_generated_pages_are_current(self):
        for path, content in build.updates().items():
            self.assertEqual(path.read_text(), content, str(path))
        for path, record in self.receipt['page_edits'].items():
            self.assertEqual(build.digest((build.ROOT / path).read_bytes()), record['after_sha256'], path)
            self.assertEqual(build.digest(build.baseline(build.ROOT / path, self.receipt['baseline_commit']).encode()), record['before_sha256'], path)

    def test_pages_metadata_structure_links(self):
        for chapter in build.CHAPTERS:
            for lang in ('zh', *build.FOREIGN):
                path = build.page_path(chapter, lang)
                page = Page(path.read_text())
                with self.subTest(path=path):
                    self.assertEqual(len(page.stack), 1)
                    ids = [n.attrs['id'] for n in page.nodes if 'id' in n.attrs]
                    self.assertEqual(len(ids), len(set(ids)))
                    bodies = [n for n in page.nodes if n.has_class('essay-body')]
                    self.assertEqual(len(bodies), 2 if lang == 'zh' else 1)
                    for code, body in zip(('zh', 'en') if lang == 'zh' else (lang,), bodies):
                        record = self.receipt['manuscripts'][f'{chapter}.{code}']
                        self.assertEqual(len(list(body.descendants('h2'))), record['sections'])
                        self.assertNotIn('**', body.text())
                        headings = [n.text() for n in page.nodes if n.tag == 'h1' and (lang != 'zh' or n.has_class(f'lang-{code}'))]
                        self.assertEqual(headings, [record['title']])
                    canonical = [n.attrs['href'] for n in page.nodes if n.tag == 'link' and n.attrs.get('rel') == 'canonical']
                    self.assertEqual(canonical, ['https://nondubito.net/' + path.relative_to(build.ROOT).as_posix()])
                    self.assertEqual(len([n for n in page.nodes if n.has_class('ddj-source')]), 1)
                    self.assertEqual(len([n for n in page.nodes if n.has_class('ddj-nav')]), 1)
                    self.assertEqual(len([n for n in page.nodes if n.has_class('lang-btn')]), 8)
                    self.assertTrue(next(n.text() for n in page.nodes if n.tag == 'title').startswith(self.receipt['manuscripts'][f'{chapter}.{lang}']['title']))
                    for n in page.nodes:
                        href = n.attrs.get('href') or n.attrs.get('src')
                        if not href:
                            continue
                        url = urlsplit(href)
                        if url.scheme or url.netloc or not url.path:
                            continue
                        target = build.ROOT / unquote(url.path).lstrip('/') if url.path.startswith('/') else path.parent / unquote(url.path)
                        self.assertTrue(target.exists(), str(target))

    def test_classical_panels_and_intro_not_changed(self):
        for chapter in build.CHAPTERS:
            for lang in ('zh', *build.FOREIGN):
                path = build.page_path(chapter, lang)
                old, new = build.baseline(path, self.receipt['baseline_commit']), path.read_text()
                pattern = r'<!-- daodejing-source:start -->.*?<!-- daodejing-source:end -->'
                self.assertEqual(re.search(pattern, old, re.S)[0], re.search(pattern, new, re.S)[0])
        for lang in ('zh', *build.FOREIGN):
            path = build.page_path('daoyan', lang)
            self.assertEqual(path.read_text(), build.baseline(path, self.receipt['baseline_commit']))
        for lang in build.FOREIGN:
            path = build.DATA / f'daoyan.{lang}.md'
            self.assertEqual(path.read_text(), build.baseline(path, self.receipt['baseline_commit']))
            self.assertIn('7b050bc382277fdfcfa12f36e75a355a', path.read_text())

    def test_titles_in_index_and_neighbor_navigation(self):
        for lang in ('zh', *build.FOREIGN):
            folder = build.page_path('index', lang).parent
            index = Page((folder / 'index.html').read_text())
            for chapter in build.CHAPTERS:
                card = next(n for n in index.nodes if n.tag == 'a' and n.attrs.get('href') == chapter + '.html')
                for code in ('zh', 'en') if lang == 'zh' else (lang,):
                    self.assertIn(self.receipt['manuscripts'][f'{chapter}.{code}']['title'], card.text())
            for number in range(35, 42):
                for n in Page((folder / f'ch{number}.html').read_text()).nodes:
                    if n.has_class('ddj-nav-btn'):
                        target = Page((folder / n.attrs['href']).read_text())
                        labels = [x.text() for x in n.descendants() if x.has_class('ddj-nav-title')]
                        # Existing adjacent chapters use typographic quotes in
                        # headings and straight quotes in navigation labels.
                        quotes = str.maketrans({'“': '"', '”': '"', '‘': "'", '’': "'"})
                        self.assertEqual([s.translate(quotes) for s in labels],
                                         [x.text().translate(quotes) for x in target.nodes if x.tag == 'h1'])

    def test_traditional_source_guard_and_coverage(self):
        converter = TraditionalConverter()
        try:
            for chapter in build.CHAPTERS:
                text = build.page_path(chapter, 'zh').read_text()
                script = (build.SERIES / 'zh-hant-data' / f'{chapter}.js').read_text()
                self.assertIn(', .ddj-source', script)
                variants = json.loads(re.search(r'var variants = (\{.*\});', script)[1])
                collector = TextCollector(); collector.feed(text)
                for value in collector.text:
                    if converter.convert(value) != value:
                        self.assertEqual(variants[value], converter.convert(value))
        finally:
            converter.close()

    def test_editorial_corrections_present(self):
        expected = {'ch36': '现实里，操控者可能得利',
                    'ch37': '自化并不等于自动向好',
                    'ch38': '不是凡有制度就宣布关系已经失败',
                    'ch39': '不是数目本身有罪',
                    'ch40': '成熟的大树仍然生长'}
        for chapter, phrase in expected.items():
            self.assertIn(phrase, (build.DATA / f'{chapter}.zh.md').read_text())
        for lang in build.LANGS:
            for chapter, link in [('ch36', 'https://ctext.org/hanfeizi/yu-lao/zh'),
                                  ('ch39', 'https://www.chineseclassic.com/LauTzu/LaoTzu_hersongkong/ch39.htm'),
                                  ('ch40', 'https://www.nature.com/articles/nature12914'),
                                  ('ch40', 'https://zh.wikisource.org/zh/道德真經取善集/卷七')]:
                self.assertIn(link, (build.DATA / f'{chapter}.{lang}.md').read_text())
        # Guard against the exact contradicted claims found during the final read.
        for key, forbidden in {
            'ch36.en': 'Seeing that frantic inflation must collapse',
            'ch37.ja': 'しかも、よく化していく',
            'ch37.de': 'und zwar gut',
            'ch37.fr': 'pas un seul recoin n’est souillé',
            'ch38.en': 'This line has two valid readings',
            'ch38.zh': '还有第三个',
            'ch39.zh': '会反噬成“致数舆无舆”',
            'ch40.en': 'The earlier analogy',
        }.items():
            self.assertNotIn(forbidden, (build.DATA / f'{key}.md').read_text())

    def test_complete_essays_and_language_parity(self):
        for chapter in build.CHAPTERS:
            zh = (build.DATA / f'{chapter}.zh.md').read_text()
            en = (build.DATA / f'{chapter}.en.md').read_text()
            self.assertGreater(len(zh), 1800)
            self.assertGreater(len(en.split()), 950)
            for lang in build.FOREIGN:
                text = (build.DATA / f'{chapter}.{lang}.md').read_text()
                if lang in ('ja', 'ko'):
                    self.assertGreater(len(text), len(zh) * .95)
                else:
                    self.assertGreater(len(text.split()), len(en.split()) * .80)
                self.assertGreater(text.count('\n\n'), 24)

    def test_search_titles(self):
        for lang in build.LANGS:
            filename = 'zh-hans' if lang == 'zh' else lang
            records = {r['u']: r for r in json.loads((build.ROOT / f'data/search/{filename}.json').read_text())['records']}
            for chapter in build.CHAPTERS:
                path = build.page_path(chapter, lang).relative_to(build.ROOT).as_posix()
                self.assertIn(self.receipt['manuscripts'][f'{chapter}.{lang}']['title'], records[path]['t'])


if __name__ == '__main__':
    unittest.main()
