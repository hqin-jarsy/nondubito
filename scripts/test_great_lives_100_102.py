"""100–102 completeness, source receipts, boundaries, and rendering guards.

Length checks prevent truncation; they do not certify literary quality.
"""
import re
import unittest
import build_great_lives_languages as b

COUNTS = {
    'levinas': [20, 18, 30, 51, 18, 15, 25, 41],
    'buber': [15, 21, 28, 16, 25, 36, 27, 29],
    'caozhi': [25, 23, 16, 47, 38, 24, 27, 41],
}


class Batch100102Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = b.load_copy()

    def test_complete_sections_and_receipts(self):
        for slug in COUNTS:
            e = self.entries[slug]
            self.assertEqual(e['edition']['status'], 'full')
            self.assertEqual(e['edition']['pending_source_review'], [])
            b.validate_full_edition(e)
            for lang in b.LANGS:
                with self.subTest(slug=slug, lang=lang):
                    c = e['copy'][lang]
                    self.assertEqual(len(c['sections']), 8)
                    self.assertEqual(len(c['notes']), 3)
                    if lang == 'zh-hant':
                        self.assertEqual([len(s['paragraphs']) for s in c['sections']], COUNTS[slug])
                    self.assertEqual(e['edition']['translation_source_sha256'][lang], e['edition']['source_sha256'])
                    body = ' '.join(p for s in c['sections'] for p in s['paragraphs'])
                    if lang in ('fr', 'de', 'es'):
                        self.assertGreater(len(body.split()), 3300)
                    else:
                        self.assertGreater(len(re.sub(r'\s+', '', body)), 7500)

    def test_bilingual_structure_and_boundaries(self):
        markers = {
            'levinas': ['第三者', '照护者需要休息', '一九八二年', '不是他的第一本书'],
            'buber': ['阳台', 'Vergegnung', '一九四二年', '早于十一月的水晶之夜'],
            'caozhi': ['神女', '曹丕二二六年去世', '又活了六年', '二一九年'],
        }
        for slug in COUNTS:
            page = b.source_path_for(slug).read_text()
            for marker in markers[slug]:
                self.assertIn(marker, page)
            for lang in ('zh', 'en'):
                body = b.source_body(slug, lang)
                self.assertNotRegex(body, r'<ol\b|<li\b')
                ss = re.split(r'<h2\b[^>]*>.*?</h2>', body)[1:]
                self.assertEqual([len(re.findall(r'<p\b', s)) for s in ss], COUNTS[slug])

    def test_source_links_and_final_scene_anchors(self):
        for slug in COUNTS:
            e = self.entries[slug]
            self.assertGreaterEqual(len(e['sources']), 5)
            for lang in b.LANGS:
                last = e['copy'][lang]['sections'][-1]
                self.assertGreaterEqual(len(last['paragraphs']), 20)
                self.assertIn('bridge', last['covers'][0])
        for lang in ('ja', 'fr', 'de', 'es', 'ko'):
            body = ' '.join(self.entries['buber']['copy'][lang]['sections'][5]['paragraphs'])
            for year, kanji in [('1938', '一九三八'), ('1942', '一九四二'), ('1948', '一九四八')]:
                self.assertTrue(year in body or kanji in body, (lang, year))
            body = ' '.join(self.entries['levinas']['copy'][lang]['sections'][5]['paragraphs'])
            self.assertTrue('1982' in body or '一九八二' in body, lang)

    def test_traditional_cleanup(self):
        for slug in COUNTS:
            body = ' '.join(p for s in self.entries[slug]['copy']['zh-hant']['sections'] for p in s['paragraphs'])
            for bad in ['髮現', '髮明', '髮展', '重復', '沈默', '何乾', '萬裡']:
                self.assertNotIn(bad, body)
        self.assertNotIn('왕후', self.entries['caozhi']['copy']['ko']['deck'])
        korean = ' '.join(p for s in self.entries['caozhi']['copy']['ko']['sections'] for p in [s['heading']] + s['paragraphs'])
        for bad in ['왕후', '서울', '콩깍지', '갑작스러운 봄']:
            self.assertNotIn(bad, korean)

    def test_rendered_paragraphs_and_navigation(self):
        order = b.canonical_order()
        available = {e['slug'] for e in order}
        neighbors = {'levinas': ('bergson', 'buber'), 'buber': ('levinas', 'caozhi'), 'caozhi': ('buber', 'girard')}
        for slug in COUNTS:
            for lang in b.LANGS:
                e = self.entries[slug]
                page = b.article_html(lang, e, order, available, self.entries)
                self.assertEqual(page, (b.SERIES / lang / (slug + '.html')).read_text())
                for section in e['copy'][lang]['sections']:
                    for paragraph in section['paragraphs']:
                        self.assertIn(b.paragraph_html(paragraph), page)
                for neighbor in neighbors[slug]:
                    self.assertIn(f'href="{neighbor}.html"', page)


if __name__ == '__main__':
    unittest.main()
