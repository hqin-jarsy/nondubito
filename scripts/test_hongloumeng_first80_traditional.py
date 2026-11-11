#!/usr/bin/env python3
"""Structural and contextual regressions for the frozen Traditional edition."""
import copy
import json
import unittest
import build_hongloumeng_first80_traditional as build


class TraditionalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.source_manifest = build.load_source()
        cls.rules = json.loads((build.DATA / 'conversion.zh-hant.json').read_text())
        cls.target = build.apply_rules(cls.source, cls.rules)
        cls.outputs = build.outputs()

    def test_reproducible(self):
        for name, expected in self.outputs.items():
            self.assertEqual((build.DATA / name).read_text(), expected)

    def test_structure_and_no_added_or_removed_characters(self):
        self.assertEqual(len(self.target['chapters']), 80)
        self.assertEqual(sum(len(c['blocks']) for c in self.target['chapters']), 4395)
        total = 0
        for a, b in zip(self.source['chapters'], self.target['chapters']):
            self.assertEqual(a.keys(), b.keys())
            self.assertEqual(a['number'], b['number'])
            self.assertEqual(len(a['title']), len(b['title']))
            for x, y in zip(a['blocks'], b['blocks']):
                self.assertEqual({k: v for k, v in x.items() if k != 'text'}, {k: v for k, v in y.items() if k != 'text'})
                self.assertEqual(len(x['text']), len(y['text']))
                total += len(y['text'])
        self.assertEqual(total, 586222)

    def test_seven_approved_source_decisions(self):
        cases = [
            (28, 45, '开不完春柳春花满画楼，', '開不完春柳春花滿畫樓，', 1),
            (28, 126, '玉玦扇坠', '玉玦扇墜', 1),
            (24, 34, '恰值焙茗走来', '恰值焙茗走來', 1),
            (6, 25, '打箩柜筛面', '打籮櫃篩麵', 1),
            (6, 32, '面目清秀，身材俊俏', '面目清秀，身材俊俏', 1),
            (8, 38, '吃了半碗碧粳粥', '吃了半碗碧粳粥', 1),
            (10, 23, '右关虚而无神', '右關虛而無神', 2),
            (17, 43, '此处蕉棠两植', '此處蕉棠兩植', 1),
            (18, 22, '说不尽帘卷虾须', '說不盡簾捲蝦鬚', 1),
            (18, 125, '是赐厨役、优伶、百戏、杂行人丁的', '是賜廚役、優伶、百戲、雜行人丁的', 1),
        ]
        for chapter, index, simplified, traditional, count in cases:
            self.assertEqual(self.source['chapters'][chapter-1]['blocks'][index-1]['text'].count(simplified), count)
            self.assertEqual(self.target['chapters'][chapter-1]['blocks'][index-1]['text'].count(traditional), count)

    def test_manifest_shape_and_assets(self):
        manifest = json.loads(self.outputs['manifest.zh-hant.json'])
        self.assertEqual(manifest.keys(), self.source_manifest.keys())
        self.assertEqual(manifest['build'], self.source_manifest['build'])
        for key in ('chapter_count', 'character_count', 'block_count', 'layout_group_count', 'diagram_line_count'):
            self.assertEqual(manifest[key], self.source_manifest[key])
        self.assertEqual(manifest['reading_sha256'], build.sha(self.outputs['reading.zh-hant.json']))

    def test_frozen_exception_anchors(self):
        if not self.rules['exceptions']:
            self.fail('Expected contextual distinctions')
        invalid = copy.deepcopy(self.rules)
        invalid['exceptions'][0]['unit_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'context hash mismatch'):
            build.apply_rules(self.source, invalid)
        duplicate = copy.deepcopy(self.rules)
        duplicate['exceptions'].append(copy.deepcopy(duplicate['exceptions'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate exception'):
            build.apply_rules(self.source, duplicate)

    def test_source_binding(self):
        invalid = copy.deepcopy(self.rules)
        invalid['source_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'source mismatch'):
            build.apply_rules(self.source, invalid)

    def test_non_cjk_targets_rejected(self):
        for target in ('A', chr(0x4DC0), chr(0x24AEB)):
            invalid = copy.deepcopy(self.rules)
            invalid['characters']['红'] = target
            with self.assertRaisesRegex(ValueError, 'CJK character mapping'):
                build.apply_rules(self.source, invalid)
            invalid = copy.deepcopy(self.rules)
            invalid['exceptions'][0]['target'] = target
            with self.assertRaisesRegex(ValueError, 'Invalid exception'):
                build.apply_rules(self.source, invalid)

    def test_contextual_regressions(self):
        def body(n):
            return ''.join(b['text'] for b in self.target['chapters'][n - 1]['blocks'])
        examples = {1: ('自云', '一干裙釵', '鬚眉'), 3: ('比干',),
                    5: ('子系中山狼',), 17: ('范石湖', '複道'),
                    24: ('䰖',), 27: ('干旄',), 29: ('㻞',),
                    41: ('綠玉斗', '兩張几'), 42: ('薑湯',),
                    58: ('修樹',), 62: ('汗巴',)}
        for n, phrases in examples.items():
            for phrase in phrases:
                self.assertTrue(phrase in body(n), (n, phrase))
        self.assertIn('青板姊妹', body(6))
        # A rare supplementary character is not a conversion fallback target.
        s = ''.join(b['text'] for c in self.source['chapters'] for b in c['blocks'])
        t = ''.join(b['text'] for c in self.target['chapters'] for b in c['blocks'])
        self.assertEqual(s.count(chr(0x24AEB)), 1)
        self.assertEqual(s.count(chr(0x24AEB)), t.count(chr(0x24AEB)))
        self.assertEqual(s.count('䰖'), t.count('䰖'))
        self.assertEqual(s.count('㻞'), t.count('㻞'))
        self.assertNotIn('裏', t)


if __name__ == '__main__':
    unittest.main()
