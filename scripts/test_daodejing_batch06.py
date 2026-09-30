#!/usr/bin/env python3
"""Content integrity and publication regressions for the reviewed sixth batch."""
import json
import re
import subprocess
import unittest
from urllib.parse import unquote, urlsplit
import build_daodejing_batch06 as build
from daodejing_review_checks import after_batch07
from test_daodejing_sources import Page
from build_emperor_traditional import TextCollector, TraditionalConverter


class Batch06(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((build.DATA / 'batch06-review.json').read_text())

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
                floor = .37 if key.startswith('ch29.') else .48
                self.assertGreater(size / len(text), floor)

    def test_page_checksums(self):
        for path, record in self.receipt['page_edits'].items():
            with self.subTest(path=path):
                self.assertEqual(build.digest((build.ROOT / path).read_bytes()), after_batch07(build.DATA, path, record['after_sha256']))

    def test_complete_pages_and_navigation(self):
        pages = build.updates()
        self.assertEqual(len(pages), 25)
        counts = dict(zip(build.CHAPTERS, (7, 8, 7, 6, 7)))
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

    def test_shared_corrections(self):
        chinese = {ch: (build.ROOT / f'essays/daodejing/{ch}.html').read_text() for ch in build.CHAPTERS}
        for ch, expected in [('ch26', '日明也'), ('ch27', '哲学重读'), ('ch28', '《论语·为政》'), ('ch29', '不是买一份成功保险'), ('ch30', '不是免于说明的通行证')]:
            self.assertIn(expected, chinese[ch])
        for ch, bad in [('ch26', '复命曰静'), ('ch26', '昭曰明也'), ('ch27', '眯/瞇 = 眇目 = 精微'), ('ch28', '立了招牌就会停下来'), ('ch29', 'Not Grasping the World Means Never Losing It'), ('ch30', '五个“毋”')]:
            self.assertNotIn(bad, chinese[ch])
        for lang in build.LANGS:
            for ch in build.CHAPTERS:
                text = (build.DATA / f'{ch}.{lang}.md').read_text()
                self.assertNotIn('BODY_PLACEHOLDER', text)
                self.assertGreater(len(text), 1800 if lang == 'ja' else 2500)

    def test_index_titles_and_neighbor_navigation(self):
        for lang in build.LANGS:
            folder = build.ROOT / 'essays/daodejing' / lang
            index = Page((folder / 'index.html').read_text())
            for ch in build.CHAPTERS:
                card = next(n for n in index.nodes if n.tag == 'a' and n.attrs.get('href') == ch + '.html')
                title = (build.DATA / f'{ch}.{lang}.md').read_text().splitlines()[0][2:]
                self.assertIn(title, card.text())
            for ch in ('ch25', 'ch31'):
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
