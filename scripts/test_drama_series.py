#!/usr/bin/env python3
"""Regression checks for the twenty-three play readings and their entry points."""

import json
import re
import unittest
from urllib.parse import unquote, urlsplit
from unittest.mock import patch

import build_drama_series as build
import build_search_index as search
from test_recent_fiction import Page


class DramaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = build.load_items()
        cls.sources = {path: path.read_text(encoding='utf-8') for path in build.TARGET.glob('*.html')}
        cls.pages = {path: Page(source) for path, source in cls.sources.items()}

    def test_complete_collection_and_eight_full_editions(self):
        self.assertEqual(len(self.pages), 24)
        self.assertEqual([item['id'] for item in self.items], list(range(1, 24)))
        self.assertEqual(sorted(n for group in build.GROUPS for n in group[3]), list(range(1, 24)))
        for item in self.items:
            with self.subTest(essay=item['id']):
                source = self.sources[build.TARGET / build.filename(item)]
                self.assertEqual(re.findall(r'class="drama-prose lang-\w+" lang="([^"]+)"', source), ['en', 'zh-Hans', 'zh-Hant', 'de', 'fr', 'es', 'ja', 'ko'])
                self.assertGreater(len(item['body_en']), 10)
                self.assertGreater(len(' '.join(item['body_en']).split()), 1000)
                self.assertGreater(len(re.findall(r'[\u4e00-\u9fff]', ''.join(item['body_zh']))), 1800)
                self.assertNotIn('[^', source)
                self.assertNotIn('正在制作', source)

    def test_translations_are_complete_and_source_is_unchanged(self):
        import hashlib
        manifest=json.loads((build.TRANSLATIONS/'source-manifest.json').read_text())
        for relative,expected in manifest['source_files'].items():
            self.assertEqual(hashlib.sha256((build.ROOT/relative).read_bytes()).hexdigest(),expected)
        for name, languages in manifest['published_body_sha256'].items():
            for lang,expected in languages.items():
                source=self.sources[build.TARGET/name]
                original_body=re.search(r'<div class="drama-prose lang-'+lang+r'"[^>]*>(.*?)</div>',source,re.S)[1]
                self.assertEqual(hashlib.sha256(original_body.encode()).hexdigest(),expected,(name,lang))
        for item in self.items:
            for lang,translation in item['editions'].items():
                with self.subTest(essay=item['id'],language=lang):
                    self.assertEqual(len(translation['body']),len(item['body_zh']))
                    self.assertEqual(len(translation['source_labels']),len(item['sources']))
                    source=self.sources[build.TARGET/build.filename(item)]
                    for paragraph in translation['body']:
                        self.assertIn('<p>'+build.inline(paragraph)+'</p>',source)
                    self.assertGreater(len(''.join(translation['body'])),len(''.join(item['body_zh']))*.65)
        self.assertEqual(sum(len(list((build.TRANSLATIONS/lang).glob('*.json'))) for lang in build.FOREIGN),115)

    def test_build_does_not_require_mac_conversion_framework(self):
        with patch('ctypes.CDLL', side_effect=AssertionError('Normal build must not load CoreFoundation')):
            outputs = build.render()
        self.assertEqual(outputs, self.sources)

    def test_language_links_and_shell(self):
        for path,source in self.sources.items():
            with self.subTest(page=path.name):
                self.assertIn('data-editions="'+' '.join(build.LANGS)+'"',source)
                for lang in build.LANGS:
                    self.assertEqual(source.count('data-set-language="'+lang+'"'),2)
                    self.assertIn('hreflang="'+build.NATIVE[lang]+'"',source)
                self.assertIn('drama.js?v=20261108',source)
                self.assertNotIn('src="../../../../site-shell.js',source)
                self.assertEqual(source.count('static.cloudflareinsights.com/beacon.min.js'),1)

    def test_structure_canonicals_and_local_links(self):
        for path, page in self.pages.items():
            with self.subTest(page=path.name):
                self.assertEqual(page.errors, [])
                self.assertEqual(len(page.ids), len(set(page.ids)))
                source = self.sources[path]
                canonical = build.BASE + ('' if path.name == 'index.html' else path.name)
                self.assertIn(f'<link rel="canonical" href="{canonical}">', source)
                self.assertEqual(page.schemas[0]['url'], canonical)
                self.assertEqual(page.schemas[0]['inLanguage'], ['en', 'zh-Hans', 'zh-Hant', 'de', 'fr', 'es', 'ja', 'ko'])
                self.assertEqual(source.count('<header'), 1, 'Content headings must not inherit the fixed site header')
                for href in page.links:
                    link = urlsplit(href)
                    if link.scheme or link.netloc:
                        continue
                    target = (path.parent / unquote(link.path)).resolve() if link.path else path
                    if target.is_dir():
                        target /= 'index.html'
                    self.assertTrue(target.is_file(), str(target))
                    if link.fragment:
                        target_page = self.pages.get(target) or Page(target.read_text(encoding='utf-8'))
                        self.assertIn(unquote(link.fragment), target_page.ids, href)

    def test_navigation_and_themed_index(self):
        index = self.sources[build.TARGET / 'index.html']
        self.assertEqual(index.count('class="drama-card"'), 23)
        for i, item in enumerate(self.items):
            with self.subTest(essay=item['id']):
                source = self.sources[build.TARGET / build.filename(item)]
                nav = re.search(r'<nav class="drama-series-nav".*?</nav>', source).group()
                expected = [build.filename(self.items[i - 1]) if i else 'index.html', build.filename(self.items[i + 1]) if i < 22 else 'index.html']
                self.assertEqual(re.findall(r'href="([^"]+)"', nav), expected)
                self.assertEqual(index.count(f'href="{build.filename(item)}"'), 1)

    def test_search_titles_descriptions_and_work_names(self):
        with patch.object(search, 'collect_pages', return_value=sorted(self.pages)):
            _, chunks = search.build()
        records = {lang: {record['u']: record for record in chunks[lang]} for lang in ('en', 'zh-Hans', 'zh-Hant', 'de', 'fr', 'es', 'ja', 'ko')}
        converter = build.DramaTraditionalConverter()
        try:
            for item in self.items:
                url = 'essays/everyday/stories/drama/' + build.filename(item)
                for language, title, deck in (
                    ('en', item['title_en'], item['deck_en']),
                    ('zh-Hans', item['title_zh'], item['deck_zh']),
                    ('zh-Hant', converter.convert(item['title_zh']), converter.convert(item['deck_zh'])),
                    *((lang,item['editions'][lang]['title'],item['editions'][lang]['deck']) for lang in build.FOREIGN),
                ):
                    with self.subTest(essay=item['id'], language=language):
                        record = records[language][url]
                        self.assertEqual(record['t'], title)
                        self.assertEqual(record['x'], deck)
                        self.assertEqual(record['d'], 'stories')
                search_text = search.extract_search_text(self.sources[build.TARGET / build.filename(item)])
                self.assertIn(item['work_en'], search_text)
                self.assertIn(item['work_zh'], search_text)
                for lang in build.FOREIGN:self.assertIn(item['editions'][lang]['work'],search_text)
            self.assertIn('馬里沃', converter.convert('皮埃尔·德·马里沃'))
            self.assertIn('普里斯特利', converter.convert('普里斯特利'))
        finally:
            converter.close()

    def test_hubs_latest_and_sitemap(self):
        shelf = (build.TARGET.parent / 'index.html').read_text(encoding='utf-8')
        self.assertEqual(shelf.count('href="drama/index.html"'), 3)
        for count in ('5 collections · 115 essays', '5 个系列 · 115 篇', '5 個系列 · 115 篇'):
            self.assertIn(count, shelf)
            self.assertIn(count, (build.ROOT / 'library.html').read_text(encoding='utf-8'))
        ledger = json.loads((build.ROOT / 'data/site-updates.json').read_text(encoding='utf-8'))
        update = next(item for item in ledger['updates'] if item['id'] == '2026-09-11-drama-structures')
        self.assertEqual(update['languages'], ['en', 'zh', 'zh-hant'])
        expanded=next(item for item in ledger['updates'] if item['id']=='2026-11-08-drama-eight-languages')
        self.assertEqual(expanded['languages'],list(build.LANGS))
        self.assertIn(update['id'], (build.ROOT / 'latest.html').read_text(encoding='utf-8'))
        sitemap = (build.ROOT / 'sitemap.xml').read_text(encoding='utf-8')
        self.assertIn('<loc>' + build.BASE + '</loc>', sitemap)
        for item in self.items:
            self.assertIn('<loc>' + build.BASE + build.filename(item) + '</loc>', sitemap)


if __name__ == '__main__':
    unittest.main()
