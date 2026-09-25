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

    def test_second_batch_has_all_sections_in_seven_source_languages(self):
        for number, sections in enumerate((6, 9, 8, 8, 8), 6):
            slug = f'ep{number:02}'
            self.assertEqual(set(self.editions[slug]), set(full.LANGS))
            for lang in full.LANGS:
                with self.subTest(slug=slug, lang=lang):
                    source = (full.DATA / f'{slug}.{lang}.md').read_text()
                    self.assertEqual(len(re.findall(r'^## ', source, re.M)), sections + 1)
                    self.assertIn(self.editions[slug][lang]['body'],
                                  self.outputs[full.SERIES / (f'{slug}.html' if lang in ('zh','en') else f'{lang}/{slug}.html')])

    def test_second_batch_old_title_commentary_removed(self):
        patterns = r'中国語(?:の)?原題|중국어 원제|título chino|titre chinois|chinesischen Titel|chinesische Überschrift'
        for number in range(6, 11):
            for lang in ('ja', 'ko', 'fr', 'de', 'es'):
                source = (full.DATA / f'ep{number:02}.{lang}.md').read_text()
                self.assertEqual(re.findall(patterns, source), [], (number, lang))

    def test_third_batch_has_complete_sections_and_sources(self):
        for number, sections in enumerate((7, 7, 7, 6, 6), 11):
            slug = f'ep{number:02}'
            self.assertEqual(set(self.editions[slug]), set(full.LANGS))
            for lang in full.LANGS:
                with self.subTest(slug=slug, lang=lang):
                    source = (full.DATA / f'{slug}.{lang}.md').read_text()
                    self.assertEqual(len(re.findall(r'^## ', source, re.M)), sections + 1)
                    path = full.SERIES / (f'{slug}.html' if lang in ('zh', 'en') else f'{lang}/{slug}.html')
                    self.assertIn(self.editions[slug][lang]['body'], self.outputs[path])
                    self.assertNotIn('中国語の原題', source)
                    self.assertNotIn('중국어 원제', source)
                    self.assertNotIn('titre chinois', source)
                    self.assertNotIn('título chino', source)
                    self.assertNotIn('chinesischen Titel', source)

    def test_third_batch_restored_english_topics_and_numeric_links(self):
        topics = {
            'ep11': ('He Hai', 'Lü Qiang', '194', '220'),
            'ep12': ('Jiang Wan', 'Fei Yi', 'Wei Guan', 'households'),
            'ep13': ('Xu Xian', 'Dao’an', 'Daosheng', 'registration'),
            'ep14': ('Empress Dowager Feng', 'Liu Xie', '574', '590'),
            'ep15': ('Yongfeng', '631', 'Wude', 'community-granary'),
        }
        for slug, terms in topics.items():
            source = (full.DATA / f'{slug}.en.md').read_text().replace("'", '’')
            for term in terms:
                self.assertIn(term, source, (slug, term))
        # Numeric source labels are ordinary external links, not note numbers.
        body = self.editions['ep11']['en']['body']
        self.assertIn('href="https://zh.wikisource.org/wiki/後漢書/卷114">114</a>', body)
        self.assertNotIn('href="#note-en-114"', body)

    def test_fourth_batch_complete_in_all_source_languages(self):
        for number, sections in enumerate((6, 8, 6, 7, 6), 16):
            slug = f'ep{number:02}'
            self.assertEqual(set(self.editions[slug]), set(full.LANGS))
            for lang in full.LANGS:
                with self.subTest(slug=slug, lang=lang):
                    source = (full.DATA / f'{slug}.{lang}.md').read_text()
                    self.assertEqual(len(re.findall(r'^## ', source, re.M)), sections + 1)
                    path = full.SERIES / (f'{slug}.html' if lang in ('zh', 'en') else f'{lang}/{slug}.html')
                    self.assertIn(self.editions[slug][lang]['body'], self.outputs[path])
                    self.assertFalse(re.search(r'中国語の原題|중국어 원제|titre chinois|título chino|chinesischen Titel', source))

    def test_fourth_batch_english_preserves_key_discussions(self):
        topics = {
            'ep16': ('Wang Gui', 'Wu Zetian', '737', 'Bian Lingcheng', 'Wu Jing'),
            'ep17': ('Tian Hongzheng', 'Feng Dao', 'Fu Lingguang', '961', 'Chanyuan'),
            'ep18': ('Yuanfeng', 'Bi Sheng', '1089', 'Yingtianfu', '1129'),
            'ep19': ('Ögödei', '1315', 'Cheng Jufu', 'Jia Lu', '1367'),
            'ep20': ('Qian Xing', '1393', 'Qi Jiguang', 'Fish-Scale', 'Shi Lingzhi', '1519'),
        }
        for slug, terms in topics.items():
            source = (full.DATA / f'{slug}.en.md').read_text()
            for term in terms:
                self.assertIn(term, source, (slug, term))

    def test_final_batch_complete_and_submission_markers_removed(self):
        self.assertEqual(set(self.editions), {f'ep{n:02}' for n in range(1, 26)})
        for number, notes in zip(range(21, 26), (29, 26, 31, 31, 30)):
            slug = f'ep{number:02}'
            self.assertEqual(set(self.editions[slug]), set(full.LANGS))
            for lang in full.LANGS:
                with self.subTest(slug=slug, lang=lang):
                    source = (full.DATA / f'{slug}.{lang}.md').read_text()
                    self.assertEqual(len(re.findall(r'^## ', source, re.M)), 7)
                    self.assertNotIn('[^S', source)
                    self.assertNotIn('.md', source)
                    self.assertNotIn('v0.1', source)
                    self.assertNotIn('non validé pour publication', source)
                    self.assertFalse(re.search(r'^<a id=', source, re.M))
                    if lang not in ('zh', 'en'):
                        self.assertEqual(len(re.findall(r'^\[\d+\]', source, re.M)), notes)
                    path = full.SERIES / (f'{slug}.html' if lang in ('zh', 'en') else f'{lang}/{slug}.html')
                    self.assertIn(self.editions[slug][lang]['body'], self.outputs[path])

    def test_final_batch_english_keeps_concrete_questions(self):
        topics = {
            'ep21': ('1617', 'Single Whip', 'Gu Xiancheng', 'Wang Aoyong', '1638'),
            'ep22': ('Liu Mingying', 'forty-two days', 'Jiangyin', 'Jiading', '1683'),
            'ep23': ('Fang Bao', 'Qian Feng', 'Liu Qiyuan', 'Dai Zhen', 'Nerchinsk'),
            'ep24': ('Tongwenguan', '1894', 'Weihai', '1905', 'Sun Yat-sen'),
            'ep25': ('Hu Shi', '1931', '1934', 'Xi’an', 'Chen Sheng'),
        }
        for slug, terms in topics.items():
            source = (full.DATA / f'{slug}.en.md').read_text().replace("'", '’')
            for term in terms:
                self.assertIn(term, source, (slug, term))

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
