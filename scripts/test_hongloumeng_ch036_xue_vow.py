"""Verify the Aunt Xue’s vow in all eight published chapter files."""

import unittest

import build_hongloumeng_reading as simplified
import build_hongloumeng_reading_traditional as traditional
from hongloumeng_ch036_xue_vow import PHRASES, apply
from test_hongloumeng_first80_copyedits import READER, body


class Chapter36XueVowTest(unittest.TestCase):
    def test_all_reader_versions(self):
        for lang, (old, new) in PHRASES.items():
            with self.subTest(language=lang):
                directory = '' if lang == 'zh-Hans' else lang.lower()
                page = (READER / directory / 'ch036.html').read_text(encoding='utf-8')
                self.assertEqual(page.count(new), 1)
                self.assertNotIn(old, page)
                self.assertEqual(apply(page, lang), page)
                self.assertEqual(apply(old, lang), new)
                with self.assertRaises(ValueError):
                    apply(old + old, lang)

    def test_chinese_release_regeneration(self):
        for builder, lang, directory in (
            (simplified, 'zh-Hans', ''),
            (traditional, 'zh-Hant', 'zh-hant'),
        ):
            with self.subTest(language=lang):
                reading, manifest = builder.load()
                pages = builder.render(reading, manifest, mode='release', assets={}, bilingual=False)
                page = (READER / directory / 'ch036.html').read_text(encoding='utf-8')
                self.assertEqual(body(pages['ch036.html']), body(page))


if __name__ == '__main__':
    unittest.main()
