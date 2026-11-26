"""Check that approved copyedits survive regeneration of public reader text."""

import html
from pathlib import Path
import re
import unittest

import build_hongloumeng_reading as simplified
import build_hongloumeng_reading_traditional as traditional
from hongloumeng_first80_copyedits import CHAPTERS, TRANSLATIONS, apply

READER = Path(__file__).resolve().parents[1] / 'classics/hongloumeng'


def body(page):
    return page.split('<div class="novel-text">', 1)[1].split('</div></article>', 1)[0]


class CopyeditsTest(unittest.TestCase):
    def test_chinese_release_render_matches_installed_text(self):
        for renderer, directory, lang in ((simplified, '', 'zh-Hans'), (traditional, 'zh-hant', 'zh-Hant')):
            reading, manifest = renderer.load()
            pages = renderer.render(reading, manifest, mode='release', assets={}, bilingual=False)
            for n in CHAPTERS | {3}:
                with self.subTest(language=lang, chapter=n):
                    name = f'ch{n:03d}.html'
                    installed = (READER / directory / name).read_text(encoding='utf-8')
                    self.assertEqual(body(pages[name]), body(installed))
                    self.assertEqual(apply(installed, n, lang), installed)

    def test_no_ascii_dialogue_quotes_remain_in_chinese_reader(self):
        for directory in ('', 'zh-hant'):
            for n in range(1, 81):
                with self.subTest(directory=directory, chapter=n):
                    page = (READER / directory / f'ch{n:03d}.html').read_text(encoding='utf-8')
                    text = html.unescape(re.sub(r'<[^>]+>', '', body(page)))
                    self.assertNotIn('"', text)

    def test_translations_with_duplicate_phrase_are_corrected(self):
        for directory, (old, new) in TRANSLATIONS.items():
            with self.subTest(language=directory):
                page = (READER / directory / 'ch006.html').read_text(encoding='utf-8')
                self.assertNotIn(old, page)
                self.assertEqual(page.count(new), 1)
                self.assertEqual(apply(page, 6, directory), page)


if __name__ == '__main__':
    unittest.main()
