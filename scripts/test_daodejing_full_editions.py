#!/usr/bin/env python3
"""Read-only guards for the reviewed Chapter 1 full editions."""
import json
import unittest
from urllib.parse import urlsplit, unquote

import build_daodejing_full_editions as build
from test_daodejing_sources import Page


class FullEditions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((build.DATA / 'ch01-review.json').read_text())

    def test_protected_editions(self):
        for path, expected in self.receipt['protected'].items():
            with self.subTest(path=path):
                self.assertEqual(build.digest((build.ROOT / path).read_bytes()), expected)

    def test_received_text_recoverable(self):
        # Reverse only the explicit editorial ledger: no silent shortening.
        for lang, record in self.receipt['languages'].items():
            with self.subTest(lang=lang):
                text = (build.DATA / f'ch01.{lang}.md').read_text()
                self.assertEqual(build.digest(text.encode()), record['published_sha256'])
                for edit in reversed(record['edits']):
                    offset, before, after = edit['offset'], edit['before'], edit['after']
                    self.assertEqual(text[offset:offset + len(after)], after)
                    text = text[:offset] + before + text[offset + len(after):]
                self.assertEqual(build.digest(text.encode()), record['received_sha256'])

    def test_complete_pages_and_unchanged_shells(self):
        for path, old, new in build.updates():
            lang = path.parent.name
            with self.subTest(lang=lang):
                self.assertEqual(old, new)
                self.assertEqual(build.digest(build.replace_div(old, 'essay-body', '').encode()),
                                 self.receipt['languages'][lang]['page_shell_sha256'])
                page = Page(old)
                ids = [n.attrs['id'] for n in page.nodes if 'id' in n.attrs]
                self.assertEqual(len(ids), len(set(ids)))
                canonicals = [n.attrs.get('href') for n in page.nodes
                              if n.tag == 'link' and n.attrs.get('rel') == 'canonical']
                self.assertEqual(canonicals, ['https://nondubito.net/' + path.relative_to(build.ROOT).as_posix()])
                bodies = [n for n in page.nodes if n.has_class('essay-body')]
                self.assertEqual(len(bodies), 1)
                body = bodies[0]
                for tag, count in [('h2', 8), ('p', 119), ('blockquote', 8), ('hr', 1)]:
                    self.assertEqual(len(list(body.descendants(tag))), count)
                self.assertNotIn('**', body.text())
                self.assertNotIn('*', body.text())
                self.assertEqual(len([n for n in page.nodes if n.has_class('ddj-source')]), 1)
                self.assertEqual(len([n for n in page.nodes if n.has_class('ddj-nav')]), 1)
                toggles = [n for n in page.nodes if n.has_class('lang-btn')]
                self.assertEqual(len(toggles), 8)
                self.assertEqual(len([n for n in toggles if n.has_class('active')]), 1)
                for n in page.nodes:
                    if n.tag != 'a' or not n.attrs.get('href'):
                        continue
                    url = urlsplit(n.attrs['href'])
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = ((build.ROOT / unquote(url.path).lstrip('/')) if url.path.startswith('/')
                              else (path.parent / unquote(url.path)))
                    self.assertTrue(target.exists(), str(target))

    def test_variant_glyphs_and_corrected_reading(self):
        for lang in build.LANGS:
            text = (build.DATA / f'ch01.{lang}.md').read_text()
            with self.subTest(lang=lang):
                for glyph in ('恒', '常', '眇', '妙', '所徼', '徼'):
                    self.assertIn(glyph, text)
                self.assertNotIn('Le non-être nomme', text)
                self.assertNotIn('Nichtsein benennt', text)
                self.assertNotIn('El no-ser nombra', text)
                self.assertNotIn('万物の始めに名づくる', text)
                self.assertNotIn('시작을 이름한다', text)


if __name__ == '__main__':
    unittest.main()
