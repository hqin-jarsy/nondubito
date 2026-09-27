"""097–099 structure, source-receipt and editorial-boundary guards.

Counts catch truncation, not literary quality or native-language fluency.
"""
import re
import unittest
import build_great_lives_languages as b

COUNTS = {
    'hypatia': [9, 13, 17, 14, 18, 25, 24, 18],
    'aquinas': [12, 22, 27, 30, 24, 26, 25, 27],
    'bergson': [16, 30, 22, 28, 19, 26, 12, 31],
}
FOREIGN = {
    'hypatia': [9, 12, 12, 13, 17, 19, 20, 16],
    'aquinas': [9, 15, 16, 14, 12, 12, 12, 14],
    'bergson': [9, 16, 13, 15, 11, 13, 7, 17],
}
JAPANESE = {
    'hypatia': COUNTS['hypatia'],
    'aquinas': [12, 22, 27, 30, 24, 22, 25, 27],
    'bergson': [10, 17, 13, 15, 12, 13, 7, 18],
}


class Batch097099Tests(unittest.TestCase):
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
                    counts = COUNTS[slug] if lang == 'zh-hant' else JAPANESE[slug] if lang == 'ja' else FOREIGN[slug]
                    self.assertEqual([len(s['paragraphs']) for s in c['sections']], counts)
                    self.assertEqual(len(c['notes']), 3)
                    self.assertEqual(e['edition']['translation_source_sha256'][lang], e['edition']['source_sha256'])
                    body = ' '.join(p for s in c['sections'] for p in s['paragraphs'])
                    if lang in ('fr', 'de', 'es'):
                        self.assertGreater(len(body.split()), 2800)
                    else:
                        self.assertGreater(len(re.sub(r'\s+', '', body)), 6500)

    def test_bilingual_structure_and_boundaries(self):
        markers = {
            'hypatia': ['大斋期', '阿蒙尼乌斯', '约翰·斐洛波努斯', '不能当成已经结案', '通常被认为死于413'],
            'aquinas': ['爱尔兰的彼得', '支持把顽固异端', '不是让信仰替一个已经成立的矛盾盖章', '第九十题'],
            'bergson': ['1940年9月27日', '1937年', '不是替他的全部人生盖上无过的印章'],
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
        self.assertIn('does not refute physicalism', b.source_body('bergson', 'en'))
        self.assertIn('execution', b.source_body('aquinas', 'en'))
        self.assertNotIn('conflict was real and could only be resolved by faith', b.source_body('aquinas', 'en'))

    def test_source_links_and_final_scene_anchors(self):
        for slug in COUNTS:
            e = self.entries[slug]
            self.assertGreaterEqual(len(e['sources']), 5)
            for lang in b.LANGS:
                last = e['copy'][lang]['sections'][-1]
                self.assertGreaterEqual(len(last['paragraphs']), 14)
                self.assertIn('bridge', last['covers'][0])
        for lang, term in {'zh-hant': '異端', 'ja': '異端', 'fr': 'hérétiques', 'de': 'Häretiker', 'es': 'herejes', 'ko': '이단'}.items():
            self.assertIn(term, ' '.join(self.entries['aquinas']['copy'][lang]['sections'][6]['paragraphs']))
        for lang in b.LANGS:
            body = ' '.join(self.entries['bergson']['copy'][lang]['sections'][5]['paragraphs'])
            self.assertIn('1937', body)
            self.assertIn('1940', body)
            self.assertIn('1941', body)

    def test_traditional_and_japanese_cleanup(self):
        for slug in COUNTS:
            body = ' '.join(p for s in self.entries[slug]['copy']['zh-hant']['sections'] for p in s['paragraphs'])
            for bad in ['髮現', '髮明', '髮展', '重復', '沈默']:
                self.assertNotIn(bad, body)
        self.assertNotIn('提醒', ' '.join(p for s in self.entries['aquinas']['copy']['ja']['sections'] for p in s['paragraphs']))

    def test_rendered_paragraphs_and_navigation(self):
        order = b.canonical_order()
        available = {e['slug'] for e in order}
        neighbors = {'hypatia': ('polanyi', 'aquinas'), 'aquinas': ('hypatia', 'bergson'), 'bergson': ('aquinas', 'levinas')}
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
