"""Keep shared Rickshaw Boy cards aligned with the reviewed series description."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RickshawEntryCards(unittest.TestCase):
    def test_shared_descriptions_match_reviewed_index(self):
        corrections = json.loads((ROOT / 'data/rickshaw-boy/multilingual/index-source-corrections.json').read_text())
        zh = corrections['chinese']
        en = corrections['english']
        local = (ROOT / 'essays/literature/rickshaw-boy/zh-hant-data/index.js').read_text()
        variants = json.loads(re.search(r'var variants = (.*);', local).group(1))
        hant = variants[zh['after']]
        for name in ['library.html', 'essays/literature/index.html']:
            text = (ROOT / name).read_text()
            for item in [zh, en]:
                self.assertIn(item['after'], text, name)
                self.assertNotIn(item['before'], text, name)
        for name in ['zh-hant-data/index.js', 'essays/literature/zh-hant-data/index.js']:
            text = (ROOT / name).read_text()
            mapping = json.loads(re.search(r'var variants = (.*);', text).group(1))
            self.assertEqual(mapping[zh['after']], hant, name)
            self.assertNotIn(zh['before'], mapping, name)
        text = (ROOT / 'essays/zh-hant/index.html').read_text()
        self.assertIn(hant, text)
        self.assertNotIn('一輛三次失去的車', text)


if __name__ == '__main__':
    unittest.main()
