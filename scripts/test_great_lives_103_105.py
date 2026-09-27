"""103–105 full-edition guards. Size and structure do not certify prose quality."""
import re
import unittest
import build_great_lives_languages as b

SLUGS = ('girard', 'schelling', 'eckhart')


class Batch103105Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = b.load_copy()

    def test_full_receipts_and_coverage(self):
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
        removed_claims = {
            'girard': ('所有人都不再彼此模仿欲望', '他晚年没有公开评论过蒂尔的应用方向'),
            'schelling': ('他在她死后四个月里写完了一本书', '一八二零年代末再婚'),
            'eckhart': ('他没有撤回任何东西', '他的名字从多明我会的官方记录里被删除'),
        }
        for slug, claims in removed_claims.items():
            body = b.source_body(slug, 'zh')
            for claim in claims:
                self.assertNotIn(claim, body)
        self.assertRegex(b.source_body('schelling', 'zh'), r'1812|一八一二')
        self.assertRegex(b.source_body('eckhart', 'zh'), r'1327|一三二七')
        self.assertRegex(b.source_body('eckhart', 'zh'), r'1329|一三二九')

    def test_rendering_and_neighbors(self):
        order = b.canonical_order()
        available = {e['slug'] for e in order}
        neighbors = {'girard': ('caozhi', 'schelling'), 'schelling': ('girard', 'eckhart'), 'eckhart': ('schelling', 'rilke')}
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
