#!/usr/bin/env python3
"""Regression checks for the reviewed eight-language thirteenth batch."""
import json
import re
import unittest
from urllib.parse import unquote, urlsplit

import build_daodejing_batch13 as build
from test_daodejing_sources import Page
from build_emperor_traditional import TextCollector, TraditionalConverter
from daodejing_review_checks import after_batch14


class Batch13(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(build.RECEIPT.read_text())

    def test_locally_authored_manuscripts(self):
        self.assertEqual(build.digest((build.DATA / 'batch13-brief.json').read_bytes()),
                         self.receipt['brief_sha256'])
        for key, record in self.receipt['manuscripts'].items():
            with self.subTest(key=key):
                text = (build.DATA / f'{key}.md').read_text()
                self.assertEqual(build.digest(text.encode()), record['published_sha256'])
                self.assertEqual(text.count('\n## '), dict(zip(build.CHAPTERS, [6, 7, 8, 8, 7, 7, 9, 8, 7, 8]))[key.split('.')[0]])
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
            self.assertEqual(build.digest((build.ROOT / path).read_bytes()), after_batch14(build.DATA, path, record['after_sha256']), path)
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
            for adjacent in ('ch60', 'ch71'):
                neighbour = build.page_path(adjacent, lang)
                old = Page(build.baseline(neighbour, self.receipt['baseline_commit']))
                successor = build.DATA / 'batch14-review.json'
                if adjacent == 'ch71' and successor.exists():
                    next_commit = json.loads(successor.read_text())['baseline_commit']
                    new = Page(build.baseline(neighbour, next_commit))
                else:
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
            for number in range(60, 72):
                buttons = [n for n in Page((folder / f'ch{number}.html').read_text()).nodes
                           if n.has_class('ddj-nav-btn')]
                self.assertEqual([n.attrs.get('href') for n in buttons],
                                 [f'ch{number - 1}.html', f'ch{number + 1}.html'])
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
        expected = {'ch61': '人却不是只能随地势而去的水',
                    'ch62': '不能并排当成已经查实的三段履历',
                    'ch63': '责任不因此回到受害者身上',
                    'ch64': '更早的郭店简',
                    'ch65': '不是由同一个“愚”字',
                    'ch66': '不能仅凭“无”“不”两个字',
                    'ch67': '不能说“肖”的字面本义就是雕刻自己',
                    'ch68': '愤怒可以提醒人看见不公',
                    'ch69': '这是小说中的情节',
                    'ch70': '不被理解，不能反过来证明自己正确'}
        for chapter, phrase in expected.items():
            self.assertIn(phrase, (build.DATA / f'{chapter}.zh.md').read_text())
        self.assertNotIn('犹难之', (build.DATA / 'ch63.zh.md').read_text())
        self.assertIn('The opening describes the Dao as', (build.DATA / 'ch62.en.md').read_text())
        for lang in ('en', 'es'):
            self.assertIn('Guodian', (build.DATA / f'ch64.{lang}.md').read_text())
        self.assertIn('ofrecerle una alternativa mejor', (build.DATA / 'ch69.es.md').read_text())
        self.assertNotIn('Wir können unnötige Feindseligkeit nicht herstellen',
                         (build.DATA / 'ch69.de.md').read_text())
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
            paper = 7 if int(chapter[2:]) <= 63 else 8
            self.assertIn(f'https://self-as-an-end.net/papers/sae-daodejing-{paper}.html', text)
            self.assertIn('https://doi.org/10.5281/zenodo.20131989', text)
            if paper == 8:
                self.assertIn('https://doi.org/10.5281/zenodo.20133829', text)

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


if __name__ == '__main__':
    unittest.main()
