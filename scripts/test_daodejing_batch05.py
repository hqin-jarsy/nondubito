#!/usr/bin/env python3
"""Content integrity and publication regressions for the reviewed fifth batch."""
import json
import re
import subprocess
import unittest
from urllib.parse import unquote, urlsplit
import build_daodejing_batch05 as build
from daodejing_review_checks import after_batch07
from test_daodejing_sources import Page
from build_emperor_traditional import TextCollector, TraditionalConverter


class Batch05(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((build.DATA / 'batch05-review.json').read_text())

    def test_received_manuscripts_recoverable(self):
        for key, record in self.receipt['manuscripts'].items():
            with self.subTest(key=key):
                text = (build.DATA / f'{key}.md').read_text()
                self.assertEqual(build.digest(text.encode()), record['published_sha256'])
                size = len(text)
                for edit in reversed(record['edits']):
                    offset, before, after = edit['offset'], edit['before'], edit['after']
                    self.assertEqual(text[offset:offset + len(after)], after)
                    text = text[:offset] + before + text[offset + len(after):]
                self.assertEqual(build.digest(text.encode()), record['received_sha256'])
                floor = .55 if key.startswith('ch22.') else .60 if key.startswith('ch24.') else .75
                self.assertGreater(size / len(text), floor)

    def test_page_checksums(self):
        for path, record in self.receipt['page_edits'].items():
            with self.subTest(path=path):
                self.assertEqual(build.digest((build.ROOT / path).read_bytes()), after_batch07(build.DATA, path, record['after_sha256']))

    def test_complete_pages_and_navigation(self):
        pages = build.updates()
        self.assertEqual(len(pages), 25)
        counts = dict(zip(build.CHAPTERS, (7, 5, 7, 7, 9)))
        for path, old, new in pages:
            with self.subTest(path=path):
                self.assertEqual(old, new)
                p = Page(old)
                self.assertEqual(len(p.stack), 1)
                ids = [n.attrs['id'] for n in p.nodes if 'id' in n.attrs]
                self.assertEqual(len(ids), len(set(ids)))
                canonical = [n.attrs.get('href') for n in p.nodes if n.tag == 'link' and n.attrs.get('rel') == 'canonical']
                self.assertEqual(canonical, ['https://nondubito.net/' + path.relative_to(build.ROOT).as_posix()])
                body = [n for n in p.nodes if n.has_class('essay-body')]
                self.assertEqual(len(body), 1)
                self.assertEqual(len(list(body[0].descendants('h2'))), counts[path.stem])
                self.assertNotIn('**', body[0].text())
                self.assertNotIn('BODY_PLACEHOLDER', old)
                self.assertEqual(len([n for n in p.nodes if n.has_class('ddj-source')]), 1)
                self.assertEqual(len([n for n in p.nodes if n.has_class('ddj-nav')]), 1)
                toggles = [n for n in p.nodes if n.has_class('lang-btn')]
                self.assertEqual(len(toggles), 8)
                self.assertEqual(len([n for n in toggles if n.has_class('active')]), 1)
                title = (build.DATA / f'{path.stem}.{path.parent.name}.md').read_text().splitlines()[0][2:]
                self.assertEqual([n.text() for n in p.nodes if n.tag == 'h1'], [title])
                self.assertTrue(next(n.text() for n in p.nodes if n.tag == 'title').startswith(title))
                for n in p.nodes:
                    href = n.attrs.get('href') or n.attrs.get('src')
                    if not href:
                        continue
                    url = urlsplit(href)
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = build.ROOT / unquote(url.path).lstrip('/') if url.path.startswith('/') else path.parent / unquote(url.path)
                    self.assertTrue(target.exists(), str(target))
                    if n.has_class('ddj-nav-btn'):
                        label = [x.text() for x in n.descendants() if x.has_class('ddj-nav-title')]
                        self.assertEqual(label, [x.text() for x in Page(target.read_text()).nodes if x.tag == 'h1'])

    def test_classical_source_blocks_unchanged(self):
        for ch in build.CHAPTERS:
            for lang in ('', *build.LANGS):
                rel = 'essays/daodejing/' + (lang + '/' if lang else '') + ch + '.html'
                original = subprocess.check_output(['git', 'show', self.receipt['baseline_commit'] + ':' + rel], cwd=build.ROOT, text=True)
                before = [n.text() for n in Page(original).nodes if n.has_class('ddj-source')]
                after = [n.text() for n in Page((build.ROOT / rel).read_text()).nodes if n.has_class('ddj-source')]
                self.assertEqual(before, after, rel)

    def test_key_corrections_and_glyphs(self):
        for lang in build.LANGS:
            files = {ch: (build.DATA / f'{ch}.{lang}.md').read_text() for ch in build.CHAPTERS}
            for ch, glyphs in [('ch21', ('有', '信', '非')), ('ch22', ('不自', '弗', '无' if lang in ('de','fr','es') else '無')), ('ch23', ('希言',)), ('ch24', ('自',)), ('ch25', ('自然',))]:
                for glyph in glyphs:
                    self.assertIn(glyph, files[ch])
            for bad in ('Mutter (dem Nichtsein)', 'mère (le non-être)', 'madre (el no-ser)', '母（無）', '어머니(무)', 'privilège du Dao, non le but', 'privilegio del Dao, no una meta'):
                self.assertNotIn(bad, '\n'.join(files.values()))
        # Reviewed introductions retain the evidence removed by incoming replacements.
        for lang in build.LANGS:
            intro = (build.DATA / f'daoyan.{lang}.md').read_text()
            self.assertIn('zxyj.cbpt.cnki.net', intro)
        chinese = (build.ROOT / 'essays/daodejing/ch24.html').read_text()
        self.assertIn('并不是这里批评的', chinese)
        self.assertIn('退休', chinese)
        self.assertNotIn('过去的功会被时间稀释', chinese)
        chinese = (build.ROOT / 'essays/daodejing/ch25.html').read_text()
        self.assertIn('不等于向权威交出自己的法', chinese)
        self.assertNotIn('法自然是道的特权', chinese)

    def test_index_titles_and_neighbor_navigation(self):
        for lang in build.LANGS:
            folder = build.ROOT / 'essays/daodejing' / lang
            index = Page((folder / 'index.html').read_text())
            for ch in build.CHAPTERS:
                card = next(n for n in index.nodes if n.tag == 'a' and n.attrs.get('href') == ch + '.html')
                title = (build.DATA / f'{ch}.{lang}.md').read_text().splitlines()[0][2:]
                self.assertIn(title, card.text())
            for ch in ('ch20', 'ch26'):
                for n in Page((folder / f'{ch}.html').read_text()).nodes:
                    if n.has_class('ddj-nav-btn'):
                        target = folder / n.attrs['href']
                        self.assertEqual([x.text() for x in n.descendants() if x.has_class('ddj-nav-title')], [x.text() for x in Page(target.read_text()).nodes if x.tag == 'h1'])

    def test_traditional_mapping_covers_edited_source(self):
        converter = TraditionalConverter()
        try:
            for ch in build.CHAPTERS:
                page = (build.ROOT / f'essays/daodejing/{ch}.html').read_text()
                raw = (build.ROOT / f'essays/daodejing/zh-hant-data/{ch}.js').read_text()
                variants = json.loads(re.search(r'var variants = (\{.*\});', raw)[1])
                collector = TextCollector(); collector.feed(page)
                for text in collector.text:
                    if converter.convert(text) != text:
                        self.assertIn(text, variants)
        finally:
            converter.close()

    def test_search_titles(self):
        for lang in build.LANGS:
            records = json.loads((build.ROOT / f'data/search/{lang}.json').read_text())['records']
            records = {r['u']: r for r in records}
            for ch in build.CHAPTERS:
                title = (build.DATA / f'{ch}.{lang}.md').read_text().splitlines()[0][2:]
                self.assertIn(' '.join(title.split()), ' '.join(records[f'essays/daodejing/{lang}/{ch}.html']['t'].split()))


if __name__ == '__main__':
    unittest.main()
