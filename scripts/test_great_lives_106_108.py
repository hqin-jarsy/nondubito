"""106–108 full-edition guards. Size and structure do not certify prose quality."""
import re
import unittest
import build_great_lives_languages as b

SLUGS = ('rilke', 'nobel', 'king')


class Batch106108Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = b.load_copy()

    def test_full_receipts_and_coverage(self):
        self.assertEqual(len(self.entries), 108)
        self.assertEqual(sum(e.get('edition', {}).get('status') == 'full' for e in self.entries.values()), 108)
        self.assertEqual(b.canonical_order()[-1]['slug'], 'king')
        for slug in SLUGS:
            e = self.entries[slug]
            self.assertEqual(e['edition']['status'], 'full')
            self.assertEqual(e['edition']['pending_source_review'], [])
            self.assertEqual(len(e['edition']['required_topics']), 8)
            b.validate_full_edition(e)
            for lang in b.LANGS:
                self.assertEqual(e['edition']['translation_source_sha256'][lang], e['edition']['source_sha256'])
                self.assertEqual(len(e['copy'][lang]['sections']), 8)
                self.assertGreaterEqual(len(e['copy'][lang]['notes']), 2)

    def test_full_prose_not_synopsis(self):
        for slug in SLUGS:
            for lang in b.LANGS:
                with self.subTest(slug=slug, lang=lang):
                    sections = self.entries[slug]['copy'][lang]['sections']
                    self.assertTrue(all(len(s['paragraphs']) >= 6 for s in sections))
                    body = ' '.join(p for s in sections for p in s['paragraphs'])
                    units = len(body.split()) if lang in ('fr', 'de', 'es') else len(re.sub(r'\s+', '', body))
                    self.assertGreater(units, 3000 if lang in ('fr', 'de', 'es') else 6000)
                    self.assertGreaterEqual(len(sections[-1]['paragraphs']), 20)
                    self.assertIn('bridge', sections[-1]['covers'][0])

    def test_bilingual_and_traditional_sections(self):
        for slug in SLUGS:
            for lang in ('zh', 'en'):
                body = b.source_body(slug, lang)
                self.assertEqual(len(re.findall(r'<h2\b', body)), 8)
                self.assertNotRegex(body, r'<ol\b|<li\b')
            source_sections = re.split(r'<h2\b[^>]*>.*?</h2>', b.source_body(slug, 'zh'), flags=re.S)[1:]
            traditional = self.entries[slug]['copy']['zh-hant']['sections']
            self.assertEqual([len(re.findall(r'<p\b', s)) for s in source_sections], [len(s['paragraphs']) for s in traditional])
            text = ' '.join(p for s in traditional for p in s['paragraphs'])
            for bad in ('髮現', '髮明', '髮展', '重復', '沈默', '何乾', '萬裡'):
                self.assertNotIn(bad, text)

    def test_research_links(self):
        for slug in SLUGS:
            sources = self.entries[slug]['sources']
            self.assertGreaterEqual(len(sources), 4)
            self.assertEqual(len(sources), len({s['url'] for s in sources}))
            for source in sources:
                self.assertTrue(source['title'].strip())
                self.assertTrue(source['url'].startswith(('https://', 'http://')))

    def test_corrected_source_claims_do_not_regress(self):
        king = b.source_body('king', 'zh')
        self.assertIn('1996年分六册', king)
        self.assertIn('苏不是唯一的幸存者', king)
        self.assertIn('文学安排', king)
        self.assertNotIn('手机', king)
        self.assertNotIn('竹简', king)
        self.assertGreaterEqual(len(self.entries['king']['copy']['zh-hant']['sections'][-1]['paragraphs']), 70)
        self.assertIn('斯蒂芬', king)
        nobel = b.source_body('nobel', 'zh')
        self.assertIn('尚无确证', nobel)
        self.assertIn('王储', nobel)
        self.assertNotIn('一九三五年颁给', nobel)
        self.assertEqual(self.entries['king']['number'], 108)

    def test_rendering_and_neighbors(self):
        order = b.canonical_order()
        available = {e['slug'] for e in order}
        neighbors = {'rilke': ('eckhart', 'nobel'), 'nobel': ('rilke', 'king'), 'king': ('nobel',)}
        for slug in SLUGS:
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
