"""091–093 completeness and editorial-boundary guards, not quality scores."""
import re
import unittest
import build_great_lives_languages as b

COUNTS = {
    'murdoch': [7, 9, 10, 5, 7, 5, 7, 12],
    'ibnkhaldun': [7, 7, 7, 6, 7, 6, 5, 12],
    'vygotsky': [5, 9, 8, 4, 5, 7, 5, 16],
}


class Batch091093Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = b.load_copy()

    def test_complete_narratives_and_receipts(self):
        for slug, counts in COUNTS.items():
            e = self.entries[slug]
            self.assertEqual(e['edition']['status'], 'full')
            self.assertEqual(e['edition']['pending_source_review'], [])
            b.validate_full_edition(e)
            for lang in b.LANGS:
                with self.subTest(slug=slug, lang=lang):
                    c = e['copy'][lang]
                    self.assertEqual([len(s['paragraphs']) for s in c['sections']], counts)
                    self.assertEqual(len(c['notes']), 3)
                    self.assertEqual(e['edition']['translation_source_sha256'][lang],
                                     e['edition']['source_sha256'])
            text = ' '.join(p for s in e['copy']['zh-hant']['sections'] for p in s['paragraphs'])
            for bad in ['髮現', '髮明', '髮展', '發明瞭', '重復', '阿倫特']:
                self.assertNotIn(bad, text)

    def test_source_structure_and_editorial_boundaries(self):
        markers = {
            'murdoch': ['去我不是把人消灭', '不保证看得公正', '一个人的价值也不需要靠作品来续期'],
            'ibnkhaldun': ['五个月', '120年', '不是一个人凭空发明了全部社会科学'],
            'vygotsky': ['1976年', '不是维果茨基本人提出的术语', '不是等到会独立行走才算一个人'],
        }
        for slug, counts in COUNTS.items():
            page = b.source_path_for(slug).read_text()
            for marker in markers[slug]:
                self.assertIn(marker, page)
            self.assertNotRegex(page, r'<p class="essay-footnote">.*?<p>')
            for lang in ['zh', 'en']:
                with self.subTest(slug=slug, lang=lang):
                    body = b.source_body(slug, lang)
                    self.assertNotRegex(body, r'<ol\b|<li\b')
                    sections = re.split(r'<h2\b[^>]*>.*?</h2>', body)[1:]
                    self.assertEqual([len(re.findall(r'<p\b', s)) for s in sections], counts)

    def test_cross_language_narrative_markers(self):
        markers = {
            'murdoch': {
                'zh-hant': ['紅隼', 'M', 'D', '1997', '鄂蘭', '小說'],
                'ja': ['M', 'D', '1997', 'アーレント'],
                'fr': ['M', 'D', '1997', 'Arendt'],
                'de': ['M', 'D', '1997', 'Arendt'],
                'es': ['M', 'D', '1997', 'Arendt'],
                'ko': ['M', 'D', '1997', '아렌트'],
            },
            'ibnkhaldun': {
                'zh-hant': ['1377', '1401', '一百二十', '費希特'],
                'ja': ['1377', '1401', '百二十', 'フィヒテ'],
                'fr': ['1377', '1401', 'cent vingt', 'Fichte'],
                'de': ['1377', '1401', '120', 'Fichte'],
                'es': ['1377', '1401', 'ciento veinte', 'Fichte'],
                'ko': ['1377', '1401', '120', '피히테'],
            },
            'vygotsky': {
                'zh-hant': ['摩西', '1976', '1956', '1962', '1978', '波蘭尼'],
                'ja': ['モーセ', '一九七六', '一九五六', '一九六二', '一九七八', 'ポランニー'],
                'fr': ['Moïse', '1976', '1956', '1962', '1978', 'Polanyi'],
                'de': ['Mose', '1976', '1956', '1962', '1978', 'Polanyi'],
                'es': ['Moisés', '1976', '1956', '1962', '1978', 'Polanyi'],
                'ko': ['모세', '1976', '1956', '1962', '1978', '폴라니'],
            },
        }
        for slug, languages in markers.items():
            for lang, words in languages.items():
                text = ' '.join(p for s in self.entries[slug]['copy'][lang]['sections'] for p in s['paragraphs'])
                for word in words:
                    with self.subTest(slug=slug, lang=lang, word=word):
                        self.assertIn(word, text)

    def test_rendered_paragraphs_and_navigation(self):
        order = b.canonical_order()
        available = {e['slug'] for e in order}
        neighbors = {'murdoch': ('arendt', 'ibnkhaldun'),
                     'ibnkhaldun': ('murdoch', 'vygotsky'),
                     'vygotsky': ('ibnkhaldun', 'strawson')}
        for slug in COUNTS:
            e = self.entries[slug]
            for lang in b.LANGS:
                with self.subTest(slug=slug, lang=lang):
                    page = b.article_html(lang, e, order, available, self.entries)
                    for section in e['copy'][lang]['sections']:
                        for p in section['paragraphs']:
                            self.assertIn(b.paragraph_html(p), page)
                    for neighbor in neighbors[slug]:
                        self.assertIn(f'href="{neighbor}.html"', page)
                    self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/{slug}.html', page)
                    self.assertEqual(page.count('<h1>'), 1)


if __name__ == '__main__':
    unittest.main()
