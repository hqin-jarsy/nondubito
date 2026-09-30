#!/usr/bin/env python3
"""Static integrity guards for the reviewed introduction and chapters 2–5."""
import json
import re
import unittest
from urllib.parse import urlsplit, unquote

import build_daodejing_batch01 as build
from daodejing_review_checks import after_batch07
from test_daodejing_sources import Page


class BatchEditions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((build.DATA / 'batch01-review.json').read_text())

    def test_received_text_recoverable(self):
        for key, record in self.receipt['manuscripts'].items():
            with self.subTest(key=key):
                text = (build.DATA / f'{key}.md').read_text()
                self.assertEqual(build.digest(text.encode()), record['published_sha256'])
                self.assertIsNone(re.search(r'(\([吾我]\)) \1', text))
                for edit in reversed(record['edits']):
                    offset, before, after = edit['offset'], edit['before'], edit['after']
                    self.assertEqual(text[offset:offset + len(after)], after)
                    text = text[:offset] + before + text[offset + len(after):]
                self.assertEqual(build.digest(text.encode()), record['received_sha256'])

    def test_approved_page_checksums(self):
        for path, record in self.receipt['page_edits'].items():
            with self.subTest(path=path):
                self.assertEqual(build.digest((build.ROOT / path).read_bytes()), after_batch07(build.DATA, path, record['after_sha256']))

    def test_complete_pages_and_navigation(self):
        pages = build.updates()
        self.assertEqual(len(pages), 25)
        for path, old, new in pages:
            with self.subTest(path=path):
                self.assertEqual(old, new)
                page = Page(old)
                ids = [n.attrs['id'] for n in page.nodes if 'id' in n.attrs]
                self.assertEqual(len(ids), len(set(ids)))
                canonical = [n.attrs.get('href') for n in page.nodes
                             if n.tag == 'link' and n.attrs.get('rel') == 'canonical']
                self.assertEqual(canonical, ['https://nondubito.net/' + path.relative_to(build.ROOT).as_posix()])
                bodies = [n for n in page.nodes if n.has_class('essay-body')]
                self.assertEqual(len(bodies), 1)
                record = self.receipt['manuscripts'][f'{path.stem}.{path.parent.name}']
                for tag, field in [('h2', 'sections'), ('p', 'paragraphs'), ('blockquote', 'blockquotes')]:
                    self.assertEqual(len(list(bodies[0].descendants(tag))), record[field])
                self.assertNotIn('**', bodies[0].text())
                self.assertEqual(len([n for n in page.nodes if n.has_class('ddj-source')]),
                                 0 if path.stem == 'daoyan' else 1)
                toggles = [n for n in page.nodes if n.has_class('lang-btn')]
                self.assertEqual(len(toggles), 8)
                self.assertEqual(len([n for n in toggles if n.has_class('active')]), 1)
                for node in page.nodes:
                    href = node.attrs.get('href') or node.attrs.get('src')
                    if not href:
                        continue
                    url = urlsplit(href)
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (build.ROOT / unquote(url.path).lstrip('/') if url.path.startswith('/')
                              else path.parent / unquote(url.path))
                    self.assertTrue(target.exists(), str(target))

    def test_correction_sources_and_glyphs(self):
        for lang in build.LANGS:
            intro = (build.DATA / f'daoyan.{lang}.md').read_text()
            ch05 = (build.DATA / f'ch05.{lang}.md').read_text()
            self.assertIn('zxyj.cbpt.cnki.net', intro)
            self.assertIn('zh.wikisource.org/wiki/莊子/天運', ch05)
        for lang in ('fr', 'de', 'es'):
            for chapter, glyphs in [('ch02', ('恒也', '相盈', '相倾')),
                                    ('ch03', ('上', '尚', '弗')),
                                    ('ch04', ('有', '又', '吾', '我')),
                                    ('ch05', ('多闻', '多言'))]:
                text = (build.DATA / f'{chapter}.{lang}.md').read_text()
                for glyph in glyphs:
                    self.assertIn(glyph, text)


if __name__ == '__main__':
    unittest.main()
