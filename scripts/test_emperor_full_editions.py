#!/usr/bin/env python3
"""Structural regression checks for reviewed Chinese Emperors editions.

These checks detect lost prose, broken notes, and compact-generator overwrites;
they are not a substitute for editorial or browser review.
"""
import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

import build_emperor_full_editions as full
from build_collection_languages import load_specs, render as collection_render


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = []
        self.links = []
        self.canonicals = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for attribute in ('href', 'src'):
            if attrs.get(attribute):
                self.links.append(attrs[attribute])
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs['href'])


class EmperorFullEditionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.editions = full.editions()
        cls.outputs = full.render()

    def test_first_batch_is_complete(self):
        for number, sections in enumerate((6, 7, 7, 9, 8), 1):
            slug = f'ep{number:02}'
            self.assertEqual(set(self.editions[slug]), set(full.LANGS))
            for lang in ('zh', 'en'):
                source = (full.DATA / f'{slug}.{lang}.md').read_text()
                self.assertEqual(len(re.findall(r'^## ', source, re.M)), sections + 1)

    def test_full_sources_and_notes_render(self):
        for slug, copies in self.editions.items():
            for lang, copy in copies.items():
                with self.subTest(slug=slug, lang=lang):
                    page = Page(copy['body'])
                    self.assertTrue(page.ids)
                    self.assertIn('class="full-sources"', copy['body'])
                    self.assertEqual(re.findall(r'\[\^?\d+\]', copy['body']), [])
                    for link in page.links:
                        if link.startswith('#'):
                            self.assertIn(link[1:], page.ids)
                        self.assertFalse(urlsplit(link).path.endswith('.md'))

    def test_render_is_current_and_idempotent(self):
        for path, expected in self.outputs.items():
            with self.subTest(page=path):
                self.assertEqual(path.read_text(), expected)

    def test_complete_body_survives_old_collection_builder(self):
        specs = load_specs({'chinese-emperors'})
        self.assertEqual(len(specs), 1)
        for path, content in collection_render(specs[0]).items():
            if path.stem in self.editions and path.parent.name in full.LANGS:
                body = self.editions[path.stem][path.parent.name]['body']
                self.assertIn(body, content)
                self.assertEqual(content, path.read_text())

    def test_page_ids_canonicals_and_local_targets(self):
        for path, content in self.outputs.items():
            if path.stem not in self.editions and path.stem != 'index':
                continue
            with self.subTest(page=path):
                page = Page(content)
                duplicates = [key for key, count in Counter(page.ids).items() if count > 1]
                self.assertEqual(duplicates, [])
                expected = 'https://nondubito.net/' + path.relative_to(full.ROOT).as_posix()
                if path.name == 'index.html':
                    expected = expected.removesuffix('index.html')
                self.assertEqual(page.canonicals, [expected])
                for link in page.links:
                    url = urlsplit(link)
                    if url.scheme or url.netloc:
                        continue
                    target = (full.ROOT / url.path.lstrip('/') if url.path.startswith('/')
                              else path.parent / unquote(url.path)) if url.path else path
                    if target.is_dir():
                        target = target / 'index.html'
                    self.assertTrue(target.is_file(), f'{path}: {link}')
                    if url.fragment and url.fragment.startswith('note-'):
                        self.assertIn(url.fragment, Page(target.read_text()).ids)

    def test_japanese_directory_stays_in_japanese(self):
        content = (full.SERIES / 'ja/index.html').read_text()
        links = re.findall(r'href="([^"]+)" class="essay-card"', content)
        self.assertEqual(len(links), 25)
        self.assertTrue(all(re.fullmatch(r'ep\d{2}\.html', link) for link in links))


if __name__ == '__main__':
    unittest.main()
