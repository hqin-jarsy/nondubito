"""Check the birthday correction in all eight readers and in Chinese rebuilds."""

import unittest

import build_hongloumeng_reading as simplified
import build_hongloumeng_reading_traditional as traditional
from hongloumeng_ch062_birthdays import PHRASES, apply
from test_hongloumeng_first80_copyedits import READER, body


class Chapter62BirthdaysTest(unittest.TestCase):
    def test_all_reader_versions(self):
        for lang, (old, new) in PHRASES.items():
            with self.subTest(language=lang):
                directory = '' if lang == 'zh-Hans' else lang.lower()
                page = (READER / directory / 'ch062.html').read_text(encoding='utf-8')
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
                page = (READER / directory / 'ch062.html').read_text(encoding='utf-8')
                self.assertEqual(body(pages['ch062.html']), body(page))

    def test_chinese_correction_is_two_characters(self):
        for lang, expected in (('zh-Hans', '宝姐姐'), ('zh-Hant', '寶姐姐')):
            old, new = PHRASES[lang]
            self.assertEqual(old.replace(f'老太太和{expected}', f'太太和{expected}', 1)
                             .replace('三月初一日是太太', '三月初一日是大太太', 1), new)


if __name__ == '__main__':
    unittest.main()
