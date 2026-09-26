"""Guard 088's full narrative and editorial boundaries, not prose quality."""
import re
import unittest
import build_great_lives_languages as builder


class WoolfFullEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = builder.load_copy()
        cls.entry = cls.entries['woolf']

    def test_complete_sections_and_source_receipts(self):
        e = self.entry
        self.assertEqual(e['number'], 88)
        self.assertEqual(e['edition']['status'], 'full')
        self.assertEqual(e['edition']['pending_source_review'], [])
        builder.validate_full_edition(e)
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                self.assertEqual([len(s['paragraphs']) for s in e['copy'][lang]['sections']],
                                 [8, 7, 5, 11, 4, 7, 8, 14])
                self.assertEqual(len(e['copy'][lang]['notes']), 3)
                self.assertEqual(e['edition']['translation_source_sha256'][lang],
                                 e['edition']['source_sha256'])

    def test_plural_minds_memory_room_and_complete_bridge(self):
        markers = {
            'zh-hant': ('塞普蒂默斯', '莎莉', '普魯斯特', '五百英鎊', '凡妮莎', '薇塔', '大本鐘'),
            'ja': ('セプティマス', 'サリー', 'プルースト', '五百ポンド', 'ヴァネッサ', 'ヴィタ', 'ビッグ・ベン'),
            'fr': ('Septimus', 'Sally', 'Proust', 'cinq cents livres', 'Vanessa', 'Vita', 'Big Ben'),
            'de': ('Septimus', 'Sally', 'Proust', 'fünfhundert Pfund', 'Vanessa', 'Vita', 'Big Ben'),
            'es': ('Septimus', 'Sally', 'Proust', 'quinientas libras', 'Vanessa', 'Vita', 'Big Ben'),
            'ko': ('셉티머스', '샐리', '프루스트', '오백 파운드', '버네사', '비타', '빅벤'),
        }
        endings = {
            'zh-hant': '但你知道了——棉絮下面有東西。',
            'ja': 'でも、もう知っている。綿の下には何かがある。',
            'fr': 'Mais vous savez désormais : il y a quelque chose dessous.',
            'de': 'Aber jetzt weißt du: Darunter ist etwas.',
            'es': 'Pero ahora lo sabes: debajo hay algo.',
            'ko': '하지만 이제 안다. 솜 아래에는 무언가가 있다.',
        }
        for lang in builder.LANGS:
            sections = self.entry['copy'][lang]['sections']
            body = ' '.join(p for s in sections for p in s['paragraphs'])
            with self.subTest(lang=lang):
                for marker in markers[lang]:
                    self.assertIn(marker, body)
                self.assertEqual(sections[-1]['paragraphs'][-1], endings[lang])
                self.assertGreater(len(sections[-1]['paragraphs']), 10)

    def test_no_death_verdict_or_false_philosophical_identity(self):
        boundaries = {
            'zh-hant': ('一封告別信不是', '仍然在', '不能說兩人發現了同一種', '不等於應該永遠這樣做'),
            'ja': ('病歴のすべてではない', 'その人はいる', '同じ「意識空間」を発見したとは言えない', 'いつもそうすべきことは違う'),
            'fr': ('ni un dossier médical complet', 'elle est là', 'sans leur attribuer la découverte', 'ne veut pas dire devoir le faire'),
            'de': ('weder eine vollständige Krankengeschichte', 'ist noch immer hier', 'ohne einen identischen Bewusstseinsraum', 'heißt nicht, es immer bewältigen'),
            'es': ('no es una historia clínica completa', 'la persona sigue aquí', 'sin atribuirles el descubrimiento', 'no significa tener que hacerlo siempre'),
            'ko': ('병력 전체는 아니고', '그 사람은 여전히 있다', '동일한 의식 공간을 발견했다고 할 수는 없다', '늘 그렇게 해야 한다는 것은 다르다'),
        }
        for lang, needles in boundaries.items():
            body = ' '.join(p for s in self.entry['copy'][lang]['sections'] for p in s['paragraphs'])
            for needle in needles:
                with self.subTest(lang=lang, needle=needle):
                    self.assertIn(needle, body)
        zh = builder.source_body('woolf', 'zh')
        en = builder.source_body('woolf', 'en')
        self.assertNotIn('伍尔夫的死是棉絮赢了', zh)
        self.assertNotIn('你就不再"在"了', zh)
        self.assertNotIn('口袋里装满石头', zh)
        self.assertNotIn('consciousness itself — broke', en)
        self.assertNotIn('the whole novel runs inside her consciousness', en)
        hant = ' '.join(p for s in self.entry['copy']['zh-hant']['sections'] for p in s['paragraphs'])
        for bad in ['證明瞭', '貢佈雷', '布魯姆斯伯裡']:
            self.assertNotIn(bad, hant)
        page = builder.source_path_for('woolf').read_text()
        self.assertNotRegex(page, r'<p class="essay-footnote">.*?<p>')
        self.assertNotIn('99.99%', page)

    def test_every_paragraph_renders_with_existing_urls(self):
        order = builder.canonical_order()
        available = {e['slug'] for e in order}
        for lang in builder.LANGS:
            with self.subTest(lang=lang):
                page = builder.article_html(lang, self.entry, order, available, self.entries)
                for section in self.entry['copy'][lang]['sections']:
                    for p in section['paragraphs']:
                        self.assertIn(builder.paragraph_html(p), page)
                self.assertIn('href="nagarjuna.html"', page)
                self.assertIn('href="yukawa.html"', page)
                self.assertIn(f'https://nondubito.net/essays/mingren/{lang}/woolf.html', page)
                self.assertEqual(len(re.findall('<h1>', page)), 1)


if __name__ == '__main__':
    unittest.main()
