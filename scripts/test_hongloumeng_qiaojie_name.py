"""Verify the one-child name sequence in the published chapter editions."""

import re
import unittest

import build_hongloumeng_reading as simplified
import build_hongloumeng_reading_traditional as traditional
from hongloumeng_qiaojie_name import EDITS, apply
from test_hongloumeng_first80_copyedits import READER, body


class QiaojieNameTest(unittest.TestCase):
    def test_approved_edits_are_installed(self):
        for n, editions in EDITS.items():
            for lang in editions:
                with self.subTest(chapter=n, language=lang):
                    directory = '' if lang == 'zh-Hans' else lang.lower()
                    page = (READER / directory / f'ch{n:03d}.html').read_text(encoding='utf-8')
                    self.assertEqual(apply(page, n, lang), page)

    def test_chinese_regeneration_keeps_the_reviewed_paragraphs(self):
        for builder, lang, directory, naming in (
            (simplified, 'zh-Hans', '', '就叫他是巧哥儿'),
            (traditional, 'zh-Hant', 'zh-hant', '就叫他是巧哥兒'),
        ):
            reading, manifest = builder.load()
            pages = builder.render(reading, manifest, mode='release', assets={}, bilingual=False)
            for n, editions in EDITS.items():
                with self.subTest(chapter=n, language=lang):
                    name = f'ch{n:03d}.html'
                    generated = body(pages[name])
                    installed = body((READER / directory / name).read_text(encoding='utf-8'))
                    for _, new in editions[lang]:
                        self.assertEqual(generated.count(new), 1)
                        passage = next(p for p in re.findall(r'<p\b.*?</p>', generated) if new in p)
                        self.assertIn(passage, installed)
                    if n == 42:
                        self.assertLess(generated.index(naming), generated.index(editions[lang][0][1]))
                    else:
                        self.assertNotIn('巧姐', generated)


if __name__ == '__main__':
    unittest.main()
