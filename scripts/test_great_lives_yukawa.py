"""Completeness and editorial guardrails for 089, not literary quality scores."""
import re
import unittest
import build_great_lives_languages as b


class YukawaFullEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = b.load_copy()
        cls.entry = cls.entries['yukawa']

    def test_full_narrative_and_current_receipts(self):
        e = self.entry
        self.assertEqual(e['number'], 89)
        self.assertEqual(e['edition']['status'], 'full')
        self.assertEqual(e['edition']['pending_source_review'], [])
        b.validate_full_edition(e)
        for lang in b.LANGS:
            with self.subTest(lang=lang):
                self.assertEqual([len(s['paragraphs']) for s in e['copy'][lang]['sections']],
                                 [12, 7, 9, 9, 6, 5, 6, 11])
                self.assertEqual(len(e['copy'][lang]['notes']), 3)
                self.assertEqual(e['edition']['translation_source_sha256'][lang],
                                 e['edition']['source_sha256'])
        hant = ' '.join(p for s in e['copy']['zh-hant']['sections'] for p in s['paragraphs'])
        self.assertNotIn('髮現', hant)

    def test_retained_narrative_and_distinctions(self):
        markers = {
            'zh-hant': ['1934', '1947', '拉蒂斯', 'μ子', 'π介子', '知魚樂', '西田', '帕格沃什', '蝴蝶不是介子'],
            'ja': ['1934', '1947', 'ラッテス', 'ミュー粒子', 'パイ中間子', '知魚楽', '西田', 'パグウォッシュ', '蝶は中間子ではなく'],
            'fr': ['1934', '1947', 'Lattes', 'muon', 'pion', 'Nishida', 'Pugwash', 'Un papillon n’est pas un méson'],
            'de': ['1934', '1947', 'Lattes', 'Myon', 'Pion', 'Nishida', 'Pugwash', 'Ein Schmetterling ist kein Meson'],
            'es': ['1934', '1947', 'Lattes', 'muon', 'pion', 'Nishida', 'Pugwash', 'Una mariposa no es un mesón'],
            'ko': ['1934', '1947', '라테스', '뮤온', '파이온', '지어락', '니시다', '퍼그워시', '나비는 중간자가 아니고'],
        }
        for lang, words in markers.items():
            text = ' '.join(p for s in self.entry['copy'][lang]['sections'] for p in s['paragraphs'])
            for word in words:
                with self.subTest(lang=lang, word=word):
                    self.assertIn(word, text)

    def test_source_corrections_and_synced_title(self):
        page = b.source_path_for('yukawa').read_text()
        self.assertIn('汤川秀树：看不见的粒子', page)
        self.assertIn('Yukawa: The Unseen Particle', page)
        for old in ['东方从来没封过这道缝', 'The East Never Sealed This Crack',
                    'Analerta', '庄子早就知道了', 'Zhuangzi knew this long ago',
                    'the entire universe would stick together']:
            self.assertNotIn(old, page)
        self.assertNotRegex(page, r'<p class="essay-footnote">.*?<p>')
        self.assertNotRegex(b.source_body('yukawa', 'en'), r'<ol\b|<li\b')
        for lang in ['zh', 'en']:
            sections = re.split(r'<h2\b[^>]*>.*?</h2>', b.source_body('yukawa', lang))[1:]
            self.assertEqual([len(re.findall(r'<p\b', s)) for s in sections],
                             [12, 7, 9, 9, 6, 5, 6, 11])
        for slug in ['woolf', 'arendt']:
            neighbor = b.source_path_for(slug).read_text()
            self.assertIn('Yukawa: The Unseen Particle', neighbor)
            self.assertNotIn('The East Never Sealed This Crack', neighbor)

    def test_every_paragraph_rendered_and_navigation_stable(self):
        order = b.canonical_order()
        available = {e['slug'] for e in order}
        for lang in b.LANGS:
            with self.subTest(lang=lang):
                page = b.article_html(lang, self.entry, order, available, self.entries)
                for s in self.entry['copy'][lang]['sections']:
                    for p in s['paragraphs']:
                        self.assertIn(b.paragraph_html(p), page)
                self.assertIn('href="woolf.html"', page)
                self.assertIn('href="arendt.html"', page)
                self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/yukawa.html', page)
                self.assertEqual(page.count('<h1>'), 1)


if __name__ == '__main__':
    unittest.main()
