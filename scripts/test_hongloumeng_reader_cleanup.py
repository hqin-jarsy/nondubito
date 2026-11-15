"""Focused regressions for the November reader cleanup, without frozen text hashes."""
import re
import unittest
from pathlib import Path
from refresh_hongloumeng_korean_reader import normalize_reader_chrome

ROOT = Path(__file__).resolve().parents[1] / 'classics/hongloumeng'
LANGS = ('', 'zh-hant', 'en', 'ja', 'fr', 'de', 'es', 'ko')


class ReaderCleanupTests(unittest.TestCase):
    def test_song_layout_in_all_languages(self):
        for lang in LANGS:
            with self.subTest(lang=lang):
                text = (ROOT / lang / 'ch005.html').read_text()
                labels = dict(zip(LANGS, ['［分骨肉］', '［分骨肉］', '[Kin Torn Apart]', '［肉親との別れ］', '[Les siens séparés]', '[Trennung von Fleisch und Blut]', '[Separación de la propia sangre]', '［골육의 이별］']))
                paragraphs = re.findall(r'<p\b[^>]*>.*?</p>', text, re.S)
                i = next(i for i, p in enumerate(paragraphs) if labels[lang] in p)
                self.assertIn('class="verse layout-first"', paragraphs[i])
                self.assertIn('class="verse layout-last"', paragraphs[i + 1])
                text = (ROOT / lang / 'ch078.html').read_text()
                songs = re.findall(r'<span class="[^"]*invocation-verse[^"]*">(.*?)</span>', text, re.S)
                self.assertEqual(len(songs), 4)
                self.assertEqual([len(s.strip().splitlines()) for s in songs], [3, 4, 4, 8])
                self.assertEqual(text.count('id="invocation-song-layout"'), 1)

    def test_english_layout_is_idempotent(self):
        from hongloumeng_english_verse_layout import apply
        for name in ('ch005.html', 'ch078.html'):
            text = (ROOT / 'en' / name).read_text()
            self.assertEqual(apply(text, name), text)

    def test_korean_controls_and_navigation(self):
        for path in sorted((ROOT / 'ko').glob('ch*.html')):
            with self.subTest(page=path.name):
                text = path.read_text()
                self.assertEqual(text.count('class="chapter-nav"'), 1)
                self.assertEqual(text.count('id="chapter-nav"'), 1)
                self.assertEqual(text.count('data-size='), 3)
                self.assertNotIn('data-font=', text)
                nav = re.search(r'<nav class="chapter-nav".*?</nav>', text, re.S)[0]
                nav = nav.replace(' id="chapter-nav"', '')
                self.assertEqual(normalize_reader_chrome(text, nav), text)

    def test_targeted_chinese_typos(self):
        for lang, typo in [('', '时侯'), ('zh-hant', '時侯')]:
            self.assertNotIn(typo, (ROOT / lang / 'ch027.html').read_text())
            text = (ROOT / lang / 'ch005.html').read_text()
            self.assertIn('‘好色不淫’', text)
            self.assertIn('‘情而不淫’', text)
        self.assertNotIn('饭後', (ROOT / 'ch037.html').read_text())

    def test_begonia_is_not_the_courtyard_tree(self):
        for file in ['ch037.html', 'ch070.html', 'index.html']:
            self.assertIn('Begoniengesellschaft', (ROOT / 'de' / file).read_text())
            self.assertNotIn('Zierapfelgesellschaft', (ROOT / 'de' / file).read_text())
        self.assertNotIn('Zierapfel', (ROOT / 'de/ch037.html').read_text())
        self.assertIn('manzano de flor', (ROOT / 'es/ch078.html').read_text())


if __name__ == '__main__':
    unittest.main()
