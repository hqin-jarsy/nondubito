#!/usr/bin/env python3
"""Read-only integrity, selective-merge and navigation guards for batch 02."""
import json
import re
import unittest
from urllib.parse import urlsplit, unquote

import build_daodejing_batch02 as build
from daodejing_review_checks import after_batch07
from test_daodejing_sources import Page


class Batch02(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((build.DATA / 'batch02-review.json').read_text())

    def test_received_manuscripts_recoverable(self):
        for group in ('manuscripts', 'merged_previous'):
            for key, record in self.receipt[group].items():
                with self.subTest(key=key):
                    text = (build.DATA / f'{key}.md').read_text()
                    self.assertEqual(build.digest(text.encode()), record['published_sha256'])
                    for edit in reversed(record['edits']):
                        offset, before, after = edit['offset'], edit['before'], edit['after']
                        self.assertEqual(text[offset:offset + len(after)], after)
                        text = text[:offset] + before + text[offset + len(after):]
                    self.assertEqual(build.digest(text.encode()), record['received_sha256'])

    def test_page_checksums(self):
        for path, record in self.receipt['page_edits'].items():
            with self.subTest(path=path):
                self.assertEqual(build.digest((build.ROOT / path).read_bytes()), after_batch07(build.DATA, path, record['after_sha256']))

    def test_complete_pages_and_links(self):
        pages = build.updates()
        self.assertEqual(len(pages), 25)
        counts = dict(zip(build.CHAPTERS, (6, 6, 7, 8, 6)))
        for path, old, new in pages:
            with self.subTest(path=path):
                self.assertEqual(old, new)
                page = Page(old)
                ids = [n.attrs['id'] for n in page.nodes if 'id' in n.attrs]
                self.assertEqual(len(ids), len(set(ids)))
                canonical = [n.attrs.get('href') for n in page.nodes
                             if n.tag == 'link' and n.attrs.get('rel') == 'canonical']
                self.assertEqual(canonical, ['https://nondubito.net/' + path.relative_to(build.ROOT).as_posix()])
                body = [n for n in page.nodes if n.has_class('essay-body')]
                self.assertEqual(len(body), 1)
                self.assertEqual(len(list(body[0].descendants('h2'))), counts[path.stem])
                self.assertNotIn('**', body[0].text())
                self.assertEqual(len([n for n in page.nodes if n.has_class('ddj-source')]), 1)
                self.assertEqual(len([n for n in page.nodes if n.has_class('ddj-nav')]), 1)
                toggles = [n for n in page.nodes if n.has_class('lang-btn')]
                self.assertEqual(len(toggles), 8)
                self.assertEqual(len([n for n in toggles if n.has_class('active')]), 1)
                title = (build.DATA / f'{path.stem}.{path.parent.name}.md').read_text().splitlines()[0][2:]
                self.assertEqual([n.text() for n in page.nodes if n.tag == 'h1'], [title])
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

    def test_previous_corrections_retained(self):
        intro = (build.DATA / 'daoyan.ko.md').read_text()
        self.assertIn('zxyj.cbpt.cnki.net', intro)
        self.assertNotIn('장 구분이 아예 없다', intro)
        for lang in ('ko', 'de', 'fr'):
            text = (build.DATA / f'ch05.{lang}.md').read_text()
            self.assertIn('zh.wikisource.org/wiki/莊子/天運', text)
        for lang in ('fr', 'de'):
            text = (build.DATA / f'ch05.{lang}.md').read_text()
            self.assertIn('WhatsApp', text)
            self.assertIn('TikTok', text)

    def test_source_corrections(self):
        ch08 = (build.ROOT / 'essays/daodejing/ch08.html').read_text()
        self.assertIn('第六十七章"慈故能勇"', ch08)
        self.assertNotIn('Chapter Sixty-Nine', ch08)
        for lang in build.LANGS:
            ch06 = (build.DATA / f'ch06.{lang}.md').read_text()
            ch09 = (build.DATA / f'ch09.{lang}.md').read_text()
            self.assertIn('dict.variants.moe.edu.tw', ch06)
            self.assertIn('zh.wikisource.org/wiki/史記/卷063', ch09)
        bad = ('Sein benennt die Mutter', 'L’être nomme la mère', 'el ser nombra la madre',
               '유(有)는 만물의 어머니를 이름한다', '有は、万物の母に名づくるなり')
        for lang in build.LANGS:
            text = (build.DATA / f'ch06.{lang}.md').read_text()
            for phrase in bad:
                self.assertNotIn(phrase, text)
        for lang in ('de', 'fr', 'es'):
            for chapter, glyphs in [('ch06', ('浴', '谷', '堇', '勤')),
                                    ('ch08', ('有静', '不争', '予善天', '与善仁')),
                                    ('ch09', ('遂', '成', '盈', '满')),
                                    ('ch10', ('营', '魄', '为而不恃'))]:
                text = (build.DATA / f'{chapter}.{lang}.md').read_text()
                for glyph in glyphs:
                    self.assertIn(glyph, text)


if __name__ == '__main__':
    unittest.main()
