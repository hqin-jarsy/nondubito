#!/usr/bin/env python3
"""Integrity, source-correction and navigation checks for Daodejing batch 03."""
import json
import re
import unittest
from urllib.parse import urlsplit, unquote

import build_daodejing_batch03 as build
from test_daodejing_sources import Page
from build_emperor_traditional import TextCollector, TraditionalConverter


class Batch03(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((build.DATA / 'batch03-review.json').read_text())

    def test_received_manuscripts_recoverable(self):
        for key, record in self.receipt['manuscripts'].items():
            with self.subTest(key=key):
                text = (build.DATA / f'{key}.md').read_text()
                self.assertEqual(build.digest(text.encode()), record['published_sha256'])
                published_size = len(text)
                for edit in reversed(record['edits']):
                    offset, before, after = edit['offset'], edit['before'], edit['after']
                    self.assertEqual(text[offset:offset + len(after)], after)
                    text = text[:offset] + before + text[offset + len(after):]
                self.assertEqual(build.digest(text.encode()), record['received_sha256'])
                self.assertGreater(published_size / len(text), 0.80)

    def test_page_checksums(self):
        for path, record in self.receipt['page_edits'].items():
            with self.subTest(path=path):
                self.assertEqual(build.digest((build.ROOT / path).read_bytes()), record['after_sha256'])

    def test_complete_pages_and_links(self):
        pages = build.updates()
        self.assertEqual(len(pages), 25)
        counts = dict(zip(build.CHAPTERS, (5, 6, 7, 7, 7)))
        for path, old, new in pages:
            with self.subTest(path=path):
                self.assertEqual(old, new)
                page = Page(old)
                self.assertEqual(len(page.stack), 1)
                ids = [n.attrs['id'] for n in page.nodes if 'id' in n.attrs]
                self.assertEqual(len(ids), len(set(ids)))
                canonical = [n.attrs.get('href') for n in page.nodes
                             if n.tag == 'link' and n.attrs.get('rel') == 'canonical']
                self.assertEqual(canonical, ['https://nondubito.net/' + path.relative_to(build.ROOT).as_posix()])
                bodies = [n for n in page.nodes if n.has_class('essay-body')]
                self.assertEqual(len(bodies), 1)
                self.assertEqual(len(list(bodies[0].descendants('h2'))), counts[path.stem])
                self.assertNotIn('**', bodies[0].text())
                self.assertEqual(len([n for n in page.nodes if n.has_class('ddj-source')]), 1)
                self.assertEqual(len([n for n in page.nodes if n.has_class('ddj-nav')]), 1)
                toggles = [n for n in page.nodes if n.has_class('lang-btn')]
                self.assertEqual(len(toggles), 8)
                self.assertEqual(len([n for n in toggles if n.has_class('active')]), 1)
                title = (build.DATA / f'{path.stem}.{path.parent.name}.md').read_text().splitlines()[0][2:]
                self.assertEqual([n.text() for n in page.nodes if n.tag == 'h1'], [title])
                self.assertTrue(next(n.text() for n in page.nodes if n.tag == 'title').startswith(title))
                for n in page.nodes:
                    href = n.attrs.get('href') or n.attrs.get('src')
                    if not href:
                        continue
                    url = urlsplit(href)
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (build.ROOT / unquote(url.path).lstrip('/') if url.path.startswith('/')
                              else path.parent / unquote(url.path))
                    self.assertTrue(target.exists(), str(target))
                    if n.tag == 'a' and n.has_class('ddj-nav-btn'):
                        labels = [x.text() for x in n.descendants() if x.has_class('ddj-nav-title')]
                        headings = [x.text() for x in Page(target.read_text()).nodes if x.tag == 'h1']
                        self.assertEqual(labels, headings)

    def test_index_titles_and_neighbor_navigation(self):
        for lang in build.LANGS:
            folder = build.ROOT / 'essays/daodejing' / lang
            index = Page((folder / 'index.html').read_text())
            for chapter in build.CHAPTERS:
                card = next(n for n in index.nodes if n.tag == 'a' and n.attrs.get('href') == chapter + '.html')
                title = (build.DATA / f'{chapter}.{lang}.md').read_text().splitlines()[0][2:]
                self.assertIn(title, card.text())
            for chapter in ('ch10', 'ch16'):
                page = Page((folder / f'{chapter}.html').read_text())
                for n in page.nodes:
                    if n.has_class('ddj-nav-btn'):
                        dest = folder / n.attrs['href']
                        heading = next(x.text() for x in Page(dest.read_text()).nodes if x.tag == 'h1')
                        labels = [x.text() for x in n.descendants() if x.has_class('ddj-nav-title')]
                        self.assertEqual(labels, [heading])

    def test_classical_glyphs_visible_in_western_languages(self):
        for lang in ('de', 'fr', 'es'):
            for chapter, glyphs in [('ch11', ('利', '用', '利用')),
                                    ('ch12', ('之治也', '五色')),
                                    ('ch13', ('身', '吾', '我', '汝', '若')),
                                    ('ch14', ('今', '古', '呵', '兮')),
                                    ('ch15', ('道', '士', '蔽', '敝', '不成', '新成'))]:
                text = (build.DATA / f'{chapter}.{lang}.md').read_text()
                for glyph in glyphs:
                    self.assertIn(glyph, text)

    def test_english_missing_passages_remain_complete(self):
        for ch in (12, 13):
            page = Page((build.ROOT / f'essays/daodejing/ch{ch}.html').read_text())
            body = next(n for n in page.nodes if n.has_class('essay-body') and n.has_class('lang-en'))
            self.assertTrue(any('sae-daodejing-2.html' in n.attrs.get('href', '') for n in body.descendants('a')))
            if ch == 12:
                self.assertIn('Wang Bi', body.text())
                self.assertIn('not establish that Wang Bi himself removed', body.text())
            else:
                self.assertIn('Concrete teaching becomes abstract description.', body.text())
                self.assertIn('The world may be entrusted to you.', body.text())

    def test_no_mathematical_existence_pseudoproof(self):
        for lang in (*build.LANGS, 'zh', 'en'):
            if lang in ('zh', 'en'):
                p = Page((build.ROOT / 'essays/daodejing/ch14.html').read_text())
                text = next(n.text() for n in p.nodes if n.has_class('essay-body') and n.has_class('lang-'+lang))
            else:
                text = (build.DATA / f'ch14.{lang}.md').read_text()
            self.assertNotRegex(text, r'→\s*0')

    def test_seven_opening_images_in_bilingual_source(self):
        page = Page((build.ROOT / 'essays/daodejing/ch15.html').read_text())
        for lang,needle in [('zh','留心四邻的人'),('en','Someone alert to the neighbors')]:
            body = next(n for n in page.nodes if n.has_class('essay-body') and n.has_class('lang-'+lang))
            paragraph = next(n for n in body.descendants('p') if needle in n.text())
            self.assertEqual(len(list(paragraph.descendants('br'))), 6)

    def test_search_index_uses_reviewed_titles(self):
        for lang in build.LANGS:
            records = json.loads((build.ROOT / f'data/search/{lang}.json').read_text())['records']
            records = {r['u']:r for r in records}
            for chapter in build.CHAPTERS:
                title = (build.DATA / f'{chapter}.{lang}.md').read_text().splitlines()[0][2:]
                indexed = records[f'essays/daodejing/{lang}/{chapter}.html']['t']
                self.assertIn(' '.join(title.split()), ' '.join(indexed.split()))

    def test_traditional_mapping_covers_edited_source(self):
        converter = TraditionalConverter()
        try:
            for ch in range(11, 16):
                page = (build.ROOT / f'essays/daodejing/ch{ch}.html').read_text()
                raw = (build.ROOT / f'essays/daodejing/zh-hant-data/ch{ch}.js').read_text()
                variants = json.loads(re.search(r'var variants = (\{.*\});', raw)[1])
                collector = TextCollector(); collector.feed(page)
                for text in collector.text:
                    if converter.convert(text) != text:
                        self.assertIn(text, variants)
        finally:
            converter.close()


if __name__ == '__main__':
    unittest.main()
