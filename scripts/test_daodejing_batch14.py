#!/usr/bin/env python3
"""Regression checks for the reviewed eight-language fourteenth batch."""
import json
import re
import unittest
from urllib.parse import unquote, urlsplit

import build_daodejing_batch14 as build
from test_daodejing_sources import Page
from build_emperor_traditional import TextCollector, TraditionalConverter


class Batch14(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(build.RECEIPT.read_text())

    def test_locally_authored_manuscripts(self):
        self.assertEqual(build.digest((build.DATA / 'batch14-brief.json').read_bytes()),
                         self.receipt['brief_sha256'])
        for key, record in self.receipt['manuscripts'].items():
            with self.subTest(key=key):
                text = (build.DATA / f'{key}.md').read_text()
                self.assertEqual(build.digest(text.encode()), record['published_sha256'])
                self.assertEqual(text.count('\n## '), dict(zip(build.CHAPTERS, [7, 8, 7, 7, 8, 7, 8, 8, 7, 8, 9]))[key.split('.')[0]])
                self.assertNotIn('BODY_PLACEHOLDER', text)
                self.assertNotIn('received_sha256', record)

    def test_generated_pages_are_current(self):
        outputs = build.updates()
        changed = {path.relative_to(build.ROOT).as_posix() for path, content in outputs.items()
                   if content != build.baseline(path, self.receipt['baseline_commit'])}
        self.assertEqual(set(self.receipt['page_edits']), changed)
        for path, content in outputs.items():
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
                        rendered = Page(build.render(f'{chapter}.{code}', record)).root.text()
                        self.assertEqual(body.text().strip(), rendered.strip())
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
            for adjacent in ('ch70',):
                neighbour = build.page_path(adjacent, lang)
                old = Page(build.baseline(neighbour, self.receipt['baseline_commit']))
                new = Page(neighbour.read_text())
                self.assertEqual([n.text() for n in old.nodes if n.has_class('essay-body')],
                                 [n.text() for n in new.nodes if n.has_class('essay-body')])
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
                key = f'{chapter}.{lang}'
                for paragraph in card.descendants('p'):
                    self.assertEqual(paragraph.text(), build.description(key, self.receipt['manuscripts'][key]))
            for number in range(70, 82):
                buttons = [n for n in Page((folder / f'ch{number}.html').read_text()).nodes
                           if n.has_class('ddj-nav-btn')]
                self.assertEqual([n.attrs.get('href') for n in buttons],
                                 [f'ch{number - 1}.html'] + ([f'ch{number + 1}.html'] if number < 81 else []))
                for n in buttons:
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
        expected = {'ch71': '不是听一句发言便能给人贴的标签',
                    'ch72': '这是本文的应用',
                    'ch73': '最后一句说从容而善于谋划',
                    'ch74': '专业资格与正当授权是两回事',
                    'ch75': '两个文本都留下的难题',
                    'ch76': '木质化也不是树木开始死亡的证明',
                    'ch77': '不能证明人间的贫困最后也会由某种规律自动补足',
                    'ch78': '高压水流与磨料',
                    'ch79': '不能凭一个字就宣布传统的契约读法失效',
                    'ch80': '并不足以证明',
                    'ch81': '不把占有当成唯一的安全来源'}
        for chapter, phrase in expected.items():
            self.assertIn(phrase, (build.DATA / f'{chapter}.zh.md').read_text())
        self.assertNotIn('Chapter71', (build.DATA / 'ch71.en.md').read_text())
        self.assertIn('Apology', (build.DATA / 'ch71.en.md').read_text())
        self.assertIn('The fourth does not say “without planning.”', (build.DATA / 'ch73.en.md').read_text())
        self.assertNotIn('Ausbeutung oder Täuschung bleibt verantwortbar',
                         (build.DATA / 'ch77.de.md').read_text())
        self.assertNotIn('居間の調停', (build.DATA / 'ch79.ja.md').read_text())
        self.assertNotIn('열을 입', (build.DATA / 'ch73.ko.md').read_text())
        self.assertEqual(self.receipt['source_mode'], 'locally-authored-independent-editions')
        self.assertNotIn('source_archive', self.receipt)
        for key, record in self.receipt['manuscripts'].items():
            chapter, lang = key.split('.')
            path = build.page_path(chapter, lang)
            self.assertEqual(build.digest(build.baseline(path, self.receipt['baseline_commit']).encode()),
                             record['baseline_page_sha256'])
            text = (build.DATA / f'{key}.md').read_text()
            for doi in ('20131002', '20116124', '20116288', '20117251', '20127345', '20129184'):
                self.assertIn('https://doi.org/10.5281/zenodo.' + doi, text)
            paper = 8 if int(chapter[2:]) <= 72 else 9
            self.assertIn(f'https://self-as-an-end.net/papers/sae-daodejing-{paper}.html', text)
            self.assertIn('https://doi.org/10.5281/zenodo.20131989', text)
            self.assertIn('https://doi.org/10.5281/zenodo.20133829', text)
            if paper == 9:
                self.assertIn('https://doi.org/10.5281/zenodo.20145192', text)

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
                    # Independent native essays need not mirror English word
                    # counts. Coverage is reviewed before the exact hash freeze;
                    # this floor detects accidental summary/truncation only.
                    self.assertGreater(len(text.split()), 1250)
                    self.assertGreater(len(text.split()), len(en.split()) * .75)
                self.assertGreater(text.count('\n\n'), 24)

    def test_search_titles(self):
        for lang in build.LANGS:
            filename = 'zh-hans' if lang == 'zh' else lang
            records = {r['u']: r for r in json.loads((build.ROOT / f'data/search/{filename}.json').read_text())['records']}
            for chapter in build.CHAPTERS:
                path = build.page_path(chapter, lang).relative_to(build.ROOT).as_posix()
                self.assertIn(self.receipt['manuscripts'][f'{chapter}.{lang}']['title'], records[path]['t'])
        records = {r['u']: r for r in json.loads((build.ROOT / 'data/search/zh-hant.json').read_text())['records']}
        for chapter in build.CHAPTERS:
            script = (build.SERIES / 'zh-hant-data' / f'{chapter}.js').read_text()
            variants = json.loads(re.search(r'var variants = (\{.*\});', script)[1])
            title = self.receipt['manuscripts'][f'{chapter}.zh']['title']
            path = build.page_path(chapter, 'zh').relative_to(build.ROOT).as_posix()
            self.assertIn(variants.get(title, title), records[path]['t'])


if __name__ == '__main__':
    unittest.main()
