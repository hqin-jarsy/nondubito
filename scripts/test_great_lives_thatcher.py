"""Protect the 086 full reading edition, not a literary-quality score."""
import re
import unittest

import build_great_lives_languages as builder


class ThatcherFullEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = builder.load_copy()
        cls.entry = cls.entries['thatcher']

    def test_full_source_receipts_and_complete_eight_section_arc(self):
        entry = self.entry
        self.assertEqual(entry['number'], 86)
        self.assertEqual(entry['edition']['status'], 'full')
        self.assertEqual(entry['edition']['pending_source_review'], [])
        builder.validate_full_edition(entry)
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                sections = entry['copy'][lang]['sections']
                self.assertEqual([len(s['paragraphs']) for s in sections],
                                 [9, 7, 6, 6, 7, 10, 9, 13])
                self.assertEqual(entry['edition']['translation_source_sha256'][lang],
                                 entry['edition']['source_sha256'])
                self.assertEqual(len(entry['copy'][lang]['notes']), 3)

    def test_cross_essay_figures_and_full_bridge_are_not_summarized_away(self):
        markers = {
            'zh-hant': ('孔德', '波普爾', '狄拉克', '屈原', '費希特', '麥克林托克', '薇依'),
            'ja': ('コント', 'ポパー', 'ディラック', '屈原', 'フィヒテ', 'マクリントック', 'ヴェイユ'),
            'fr': ('Comte', 'Popper', 'Dirac', 'Qu Yuan', 'Fichte', 'McClintock', 'Weil'),
            'de': ('Comte', 'Popper', 'Dirac', 'Qu Yuan', 'Fichte', 'McClintock', 'Weil'),
            'es': ('Comte', 'Popper', 'Dirac', 'Qu Yuan', 'Fichte', 'McClintock', 'Weil'),
            'ko': ('콩트', '포퍼', '디랙', '굴원', '피히테', '매클린톡', '베유'),
        }
        endings = {
            'zh-hant': ['她聽到了。', '她沒有轉頭。', '這位女士不轉彎。'],
            'ja': ['彼女には聞こえた。', '振り向かなかった。', 'この女は、引き返さない。'],
            'fr': ['Elle l’entend.', 'Elle ne tourne pas la tête.', 'Cette dame ne fera pas demi-tour.'],
            'de': ['Sie hört sie.', 'Sie dreht den Kopf nicht.', 'Diese Frau kehrt nicht um.'],
            'es': ['Ella lo oye.', 'No vuelve la cabeza.', 'Esta señora no dará marcha atrás.'],
            'ko': ['그녀는 들었다.', '고개를 돌리지 않았다.', '이 여자는 돌아서지 않는다.'],
        }
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                sections = self.entry['copy'][lang]['sections']
                door = ' '.join(sections[2]['paragraphs'])
                for name in markers[lang]:
                    self.assertIn(name, door)
                bridge = sections[7]['paragraphs']
                self.assertIn('TINA', bridge[7])
                self.assertEqual(bridge[-3:], endings[lang])

    def test_fact_boundaries_remain_in_every_reading_edition(self):
        markers = {
            'zh-hant': ('《自由憲章》', '未必', '並非沒有妥協', '並非人人', '沒有選擇', '不是說阿倫特輕視行動', '想像'),
            'ja': ('『自由の条件』', '言い切れない', '妥協', '一様', '選んでいない', '行動を軽視', '想像'),
            'fr': ('La Constitution de la liberté', 'pas un procès-verbal assuré', 'transigé', 'pas voté d’un seul bloc', 'n’avaient pas choisi', 'ne signifie pas qu’Arendt négligeait', 'imaginaire'),
            'de': ('Die Verfassung der Freiheit', 'gesichertes Protokoll', 'Kompromisse', 'nicht einheitlich', 'nicht gewählt', 'heißt nicht, Arendt', 'vorgestellten'),
            'es': ('Los fundamentos de la libertad', 'No es un acta indiscutible', 'rectificaran', 'no votó como un bloque', 'no habían elegido', 'No significa que Arendt', 'imaginario'),
            'ko': ('『자유헌정론』', '확실한 현장 기록', '타협', '한 표', '선택하지 않은', '가볍게 여겼다는 뜻은 아니다', '상상'),
        }
        for lang, needles in markers.items():
            body = ' '.join(p for s in self.entry['copy'][lang]['sections'] for p in s['paragraphs'])
            for needle in needles:
                with self.subTest(lang=lang, needle=needle):
                    self.assertIn(needle, body)
        zh = builder.source_body('thatcher', 'zh')
        en = builder.source_body('thatcher', 'en')
        self.assertIn('《自由宪章》', zh)
        self.assertNotIn('把《通往奴役之路》拍', zh)
        self.assertNotIn('一半人', zh)
        self.assertIn('1970年代中期', zh)
        self.assertIn('mid-1970s', en)
        self.assertNotIn('<ol>', en)
        self.assertIn('<p>1925. Grantham. A grocery shop.</p>', en)
        page = builder.source_path_for('thatcher').read_text()
        self.assertNotRegex(page, r'<p class="essay-footnote">.*?<p>')
        self.assertNotIn('19502952ff', page)

    def test_all_paragraphs_render_with_stable_language_urls_and_navigation(self):
        order = builder.canonical_order()
        available = {e['slug'] for e in order}
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                page = builder.article_html(lang, self.entry, order, available, self.entries)
                for section in self.entry['copy'][lang]['sections']:
                    for paragraph in section['paragraphs']:
                        self.assertIn(builder.paragraph_html(paragraph), page)
                self.assertIn('href="weil.html"', page)
                self.assertIn('href="nagarjuna.html"', page)
                self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/thatcher.html', page)
                self.assertEqual(len(re.findall('<h1>', page)), 1)


if __name__ == '__main__':
    unittest.main()
