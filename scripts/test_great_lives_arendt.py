"""090 completeness and factual-boundary guards, not literary quality scores."""
import re
import unittest
import build_great_lives_languages as b


class ArendtFullEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = b.load_copy()
        cls.entry = cls.entries['arendt']

    def test_full_narrative_and_current_receipts(self):
        e = self.entry
        self.assertEqual(e['number'], 90)
        self.assertEqual(e['edition']['status'], 'full')
        self.assertEqual(e['edition']['pending_source_review'], [])
        b.validate_full_edition(e)
        for lang in b.LANGS:
            with self.subTest(lang=lang):
                self.assertEqual([len(s['paragraphs']) for s in e['copy'][lang]['sections']],
                                 [9, 6, 8, 7, 7, 4, 7, 13])
                self.assertEqual(len(e['copy'][lang]['notes']), 3)
                self.assertEqual(e['edition']['translation_source_sha256'][lang],
                                 e['edition']['source_sha256'])
        text = ' '.join(p for s in e['copy']['zh-hant']['sections'] for p in s['paragraphs'])
        for bad in ['髮現', '重復', '划掉', '阿倫特']:
            self.assertNotIn(bad, text)

    def test_retained_narrative_and_boundaries(self):
        markers = {
            'zh-hant': ['1961', '1963', '阿根廷', '脅迫', '兩則題辭', '1958', '屈原', '湯川', '鏡子'],
            'ja': ['1961', '1963', 'アルゼンチン', '強制', '二つの題辞', '1958', '屈原', '湯川', '鏡'],
            'fr': ['1961', '1963', 'Argentine', 'coercition', 'deux épigraphes', '1958', 'Qu Yuan', 'Yukawa', 'miroir'],
            'de': ['1961', '1963', 'Argentinien', 'Zwang', 'zwei Motti', '1958', 'Qu Yuan', 'Yukawa', 'Spiegel'],
            'es': ['1961', '1963', 'Argentina', 'coerción', 'dos epígrafes', '1958', 'Qu Yuan', 'Yukawa', 'espejo'],
            'ko': ['1961', '1963', '아르헨티나', '강요', '두 개의 제사', '1958', '굴원', '유카와', '거울'],
        }
        for lang, words in markers.items():
            text = ' '.join(p for s in self.entry['copy'][lang]['sections'] for p in s['paragraphs'])
            for word in words:
                with self.subTest(lang=lang, word=word):
                    self.assertIn(word, text)

    def test_source_corrections_and_title(self):
        page = b.source_path_for('arendt').read_text()
        self.assertIn('阿伦特：谁在替你判断', page)
        self.assertIn('Arendt: Who Is Judging in Your Place?', page)
        self.assertNotIn('阿伦特：不思考是恶', page)
        self.assertNotIn('Arendt: Not-Thinking Is Evil', page)
        self.assertIn('不是道德保险单，更不是做人的资格考试', page)
        self.assertIn('不是看完艾希曼审判才发明', page)
        self.assertIn('迫害者的责任不能转到受害者身上', page)
        self.assertNotRegex(page, r'<p class="essay-footnote">.*?<p>')
        self.assertNotRegex(b.source_body('arendt', 'en'), r'<ol\b|<li\b')
        for lang in ['zh', 'en']:
            sections = re.split(r'<h2\b[^>]*>.*?</h2>', b.source_body('arendt', lang))[1:]
            self.assertEqual([len(re.findall(r'<p\b', s)) for s in sections],
                             [9, 6, 8, 7, 7, 4, 7, 13])
        for slug in ['yukawa', 'murdoch']:
            neighbor = b.source_path_for(slug).read_text()
            self.assertIn('Arendt: Who Is Judging in Your Place?', neighbor)
            self.assertNotIn('Arendt: Not-Thinking Is Evil', neighbor)

    def test_all_paragraphs_rendered_and_navigation(self):
        order = b.canonical_order()
        available = {e['slug'] for e in order}
        for lang in b.LANGS:
            with self.subTest(lang=lang):
                page = b.article_html(lang, self.entry, order, available, self.entries)
                for s in self.entry['copy'][lang]['sections']:
                    for p in s['paragraphs']:
                        self.assertIn(b.paragraph_html(p), page)
                self.assertIn('href="yukawa.html"', page)
                self.assertIn('href="murdoch.html"', page)
                self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/arendt.html', page)
                self.assertEqual(page.count('<h1>'), 1)


if __name__ == '__main__':
    unittest.main()
