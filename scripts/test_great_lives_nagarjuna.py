"""Regression guards for 087; counts and markers do not certify prose quality."""
import re
import unittest

import build_great_lives_languages as builder


class NagarjunaFullEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = builder.load_copy()
        cls.entry = cls.entries['nagarjuna']

    def test_complete_eight_sections_and_current_source_receipts(self):
        entry = self.entry
        self.assertEqual(entry['number'], 87)
        self.assertEqual(entry['edition']['status'], 'full')
        self.assertEqual(entry['edition']['pending_source_review'], [])
        builder.validate_full_edition(entry)
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                self.assertEqual([len(s['paragraphs']) for s in entry['copy'][lang]['sections']],
                                 [8, 7, 12, 8, 6, 7, 7, 15])
                self.assertEqual(entry['edition']['translation_source_sha256'][lang],
                                 entry['edition']['source_sha256'])
                self.assertEqual(len(entry['copy'][lang]['notes']), 3)
                self.assertEqual(len(entry['copy'][lang]['sections'][2]['paragraphs'][2].splitlines()), 4)

    def test_preceding_figures_chair_and_walkers_survive(self):
        names = {
            'zh-hant': ('孔德', '波普爾', '狄拉克', '屈原', '費希特', '麥克林托克', '薇依', '柴契爾'),
            'ja': ('コント', 'ポパー', 'ディラック', '屈原', 'フィヒテ', 'マクリントック', 'ヴェイユ', 'サッチャー'),
            'fr': ('Comte', 'Popper', 'Dirac', 'Qu Yuan', 'Fichte', 'McClintock', 'Weil', 'Thatcher'),
            'de': ('Comte', 'Popper', 'Dirac', 'Qu Yuan', 'Fichte', 'McClintock', 'Weil', 'Thatcher'),
            'es': ('Comte', 'Popper', 'Dirac', 'Qu Yuan', 'Fichte', 'McClintock', 'Weil', 'Thatcher'),
            'ko': ('콩트', '포퍼', '디랙', '굴원', '피히테', '매클린톡', '베유', '대처'),
        }
        chair = {'zh-hant': '椅子', 'ja': '椅子', 'fr': 'chaise', 'de': 'Stuhl', 'es': 'silla', 'ko': '의자'}
        endings = {'zh-hant': '人們在走。這就夠了。', 'ja': '人が歩いている。それでいい。',
                   'fr': 'Des gens marchent. Cela suffit.', 'de': 'Menschen gehen. Das genügt.',
                   'es': 'La gente camina. Eso basta.', 'ko': '사람들이 걷는다. 그걸로 충분하다.'}
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                sections = self.entry['copy'][lang]['sections']
                for name in names[lang]:
                    self.assertIn(name, sections[0]['paragraphs'][5])
                self.assertIn(chair[lang], sections[5]['paragraphs'][3])
                self.assertIn('008', sections[7]['paragraphs'][10])
                self.assertEqual(sections[7]['paragraphs'][-1], endings[lang])

    def test_corrections_do_not_return_as_nihilism_or_equivalence(self):
        boundaries = {
            'zh-hant': ('不是四個邏輯真值', '不等於已經解脫', '不是不能獲得知識', '不是龍樹的“空”', '不會讓一句話自動免於質疑'),
            'ja': ('四つの論理的な真理値ではない', '自体も、解脱ではない', '知識が不可能になるのではない', '神は龍樹の空ではない', '批判を免れるわけではない'),
            'fr': ('non quatre valeurs logiques', 'pas non plus la délivrance', 'ne rend pas le savoir impossible', 'Son Dieu n’est pas la vacuité', 'à l’abri de la critique'),
            'de': ('nicht um vier logische Wahrheitswerte', 'noch nicht Befreiung', 'Wissen nicht unmöglich', 'Ihr Gott ist nicht', 'keinen Satz vor Kritik'),
            'es': ('no a cuatro valores lógicos', 'tampoco equivale a la liberación', 'no vuelve imposible el conocimiento', 'Su Dios no es', 'no protege ninguna frase'),
            'ko': ('네 가지 논리적 참값이 아니다', '자체가 해탈인 것도 아니다', '지식이 불가능해지는 것은 아니다', '그녀의 신은 용수의 공이 아니다', '비판을 면제받지는 않는다'),
        }
        for lang, needles in boundaries.items():
            body = ' '.join(p for s in self.entry['copy'][lang]['sections'] for p in s['paragraphs'])
            for needle in needles:
                with self.subTest(lang=lang, needle=needle):
                    self.assertIn(needle, body)
        zh = builder.source_body('nagarjuna', 'zh')
        en = builder.source_body('nagarjuna', 'en')
        self.assertIn('众因缘生法，我说即是无', zh)
        self.assertIn('不是物理世界之外', zh)
        self.assertNotIn('但什么都在', zh)
        self.assertNotIn('No "knowledge" that can be "obtained"', en)
        self.assertNotIn('They arrived at the same place.', en)
        hant = ' '.join(p for s in self.entry['copy']['zh-hant']['sections'] for p in s['paragraphs'])
        self.assertIn('亞里士多德', hant)
        self.assertNotIn('亞裡士多德', hant)
        self.assertIn('鬆開', hant)
        self.assertIn('劃了界限', hant)
        page = builder.source_path_for('nagarjuna').read_text()
        self.assertNotRegex(page, r'<p class="essay-footnote">.*?<p>')

    def test_rendered_paragraphs_linebreaks_urls_and_neighbors(self):
        order = builder.canonical_order()
        available = {e['slug'] for e in order}
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                page = builder.article_html(lang, self.entry, order, available, self.entries)
                for section in self.entry['copy'][lang]['sections']:
                    for paragraph in section['paragraphs']:
                        self.assertIn(builder.paragraph_html(paragraph), page)
                self.assertIn('<br>', builder.paragraph_html(self.entry['copy'][lang]['sections'][2]['paragraphs'][2]))
                self.assertIn('href="thatcher.html"', page)
                self.assertIn('href="woolf.html"', page)
                self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/nagarjuna.html', page)
                self.assertEqual(len(re.findall('<h1>', page)), 1)


if __name__ == '__main__':
    unittest.main()
