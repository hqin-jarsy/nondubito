"""094–096 coverage and editorial-boundary guards, not literary scores."""
import re
import unittest
import build_great_lives_languages as b

COUNTS = {
    'strawson': [9, 7, 10, 5, 6, 6, 5, 15],
    'merleauponty': [5, 5, 7, 6, 6, 5, 6, 14],
    'polanyi': [6, 8, 6, 20, 14, 9, 7, 22],
}


class Batch094096Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = b.load_copy()

    def test_full_editions_and_source_receipts(self):
        for slug, counts in COUNTS.items():
            e = self.entries[slug]
            self.assertEqual(e['edition']['status'], 'full')
            self.assertEqual(e['edition']['pending_source_review'], [])
            b.validate_full_edition(e)
            for lang in b.LANGS:
                with self.subTest(slug=slug, lang=lang):
                    self.assertEqual([len(s['paragraphs']) for s in e['copy'][lang]['sections']], counts)
                    self.assertEqual(len(e['copy'][lang]['notes']), 3)
                    self.assertEqual(e['edition']['translation_source_sha256'][lang],
                                     e['edition']['source_sha256'])

    def test_source_boundaries_and_structures(self):
        markers = {
            'strawson': ['原文举的是踩到手', '不是宣布每次愤怒都正当', '这种拆分有争议'],
            'merleauponty': ['不能冒充他的逐字名言', '神经系统仍在', '交织保留着差异', '1964年'],
            'polanyi': ['1962年', '辅助意识不等于', '不是把下面的整套循环冒充他的原文', '科学直觉仍须检验'],
        }
        for slug, counts in COUNTS.items():
            page = b.source_path_for(slug).read_text()
            for marker in markers[slug]:
                self.assertIn(marker, page)
            self.assertNotRegex(page, r'<p class="essay-footnote">.*?<p>')
            for lang in ['zh', 'en']:
                body = b.source_body(slug, lang)
                self.assertNotRegex(body, r'<ol\b|<li\b')
                ss = re.split(r'<h2\b[^>]*>.*?</h2>', body)[1:]
                self.assertEqual([len(re.findall(r'<p\b', s)) for s in ss], counts)
        self.assertIn('1959. Oxford.', b.source_body('strawson', 'en'))
        self.assertIn('1945. Merleau-Ponty', b.source_body('merleauponty', 'en'))
        self.assertNotIn('They are the same thing', b.source_body('polanyi', 'en'))

    def test_polanyi_keeps_all_seventeen_comparisons(self):
        names = {
            'zh-hant': ['孔德', '波普爾', '狄拉克', '屈原', '費希特', '麥克林托克', '薇依', '柴契爾', '龍樹', '吳爾芙', '湯川', '鄂蘭', '梅鐸', '赫勒敦', '維果茨基', '史特勞森', '梅洛'],
            'ja': ['コント', 'ポパー', 'ディラック', '屈原', 'フィヒテ', 'マクリントック', 'ヴェイユ', 'サッチャー', 'ナーガールジュナ', 'ウルフ', '湯川', 'アーレント', 'マードック', 'ハルドゥーン', 'ヴィゴツキー', 'ストローソン', 'メルロ'],
            'fr': ['Comte', 'Popper', 'Dirac', 'Qu Yuan', 'Fichte', 'McClintock', 'Weil', 'Thatcher', 'Nāgārjuna', 'Woolf', 'Yukawa', 'Arendt', 'Murdoch', 'Khaldoun', 'Vygotski', 'Strawson', 'Merleau'],
            'de': ['Comte', 'Popper', 'Dirac', 'Qu Yuan', 'Fichte', 'McClintock', 'Weil', 'Thatcher', 'Nāgārjuna', 'Woolf', 'Yukawa', 'Arendt', 'Murdoch', 'Khaldun', 'Wygotski', 'Strawson', 'Merleau'],
            'es': ['Comte', 'Popper', 'Dirac', 'Qu Yuan', 'Fichte', 'McClintock', 'Weil', 'Thatcher', 'Nāgārjuna', 'Woolf', 'Yukawa', 'Arendt', 'Murdoch', 'Jaldún', 'Vygotsky', 'Strawson', 'Merleau'],
            'ko': ['콩트', '포퍼', '디랙', '굴원', '피히테', '매클린톡', '베유', '대처', '나가르주나', '울프', '유카와', '아렌트', '머독', '할둔', '비고츠키', '스트로슨', '메를로퐁티'],
        }
        for lang, figures in names.items():
            ps = self.entries['polanyi']['copy'][lang]['sections'][3]['paragraphs']
            self.assertEqual(len(ps), 20)
            # p1 introduces the arc; p3 is Polanyi's reply to Comte.
            positions = [1] + list(range(3, 19))
            for figure, pos in zip(figures, positions):
                with self.subTest(lang=lang, figure=figure):
                    self.assertIn(figure, ps[pos])

    def test_traditional_glyphs_and_dated_anchors(self):
        for slug in COUNTS:
            for lang in b.LANGS:
                c = self.entries[slug]['copy'][lang]
                body = ' '.join(p for s in c['sections'] for p in s['paragraphs'])
                for year in {'strawson': ['1959', '1962', '1966'],
                             'merleauponty': ['1945', '1961', '1964'],
                             'polanyi': ['1962', '1966', '1958']}[slug]:
                    self.assertIn(year, body)
                if lang == 'zh-hant':
                    for bad in ['髮現', '髮明', '髮展', '重復', '阿倫特', '斯特勞森']:
                        self.assertNotIn(bad, body)

    def test_rendered_paragraphs_and_series_navigation(self):
        order = b.canonical_order()
        available = {e['slug'] for e in order}
        neighbors = {'strawson': ('vygotsky', 'merleauponty'),
                     'merleauponty': ('strawson', 'polanyi'),
                     'polanyi': ('merleauponty', 'hypatia')}
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
