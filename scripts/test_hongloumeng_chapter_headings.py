"""Check the visible revised chapter headings, indices and search surfaces."""
from datetime import date
import json
from pathlib import Path
import unittest

import build_hongloumeng_reading as simplified
import build_hongloumeng_reading_english as english
import build_hongloumeng_reading_traditional as traditional
from hongloumeng_chapter_headings import HEADINGS, chapter, catalog, replace_heading


ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'classics/hongloumeng/'


class ChapterHeadingsTest(unittest.TestCase):
    def test_all_public_surfaces(self):
        for number, headings in HEADINGS.items():
            for lang, (old, new) in headings.items():
                with self.subTest(chapter=number, language=lang):
                    folder = PREFIX + ('' if lang == 'zh-Hans' else lang.lower() + '/')
                    path = folder + f'ch{number:03d}.html'
                    page = (ROOT / path).read_text()
                    index = (ROOT / folder / 'index.html').read_text()
                    self.assertEqual(chapter(page, lang, number), page)
                    self.assertEqual(catalog(index, lang, number), index)
                    records = json.loads((ROOT / f'data/search/{lang.lower()}.json').read_text())['records']
                    row, = (r for r in records if r['u'] == path)
                    for field in ('t', 'q'):
                        for before, after in zip(old, new):
                            self.assertNotIn(before, row[field])
                            self.assertIn(after, row[field])
                    if lang.startswith('zh-'):
                        self.assertEqual(tuple(len(half) for half in new), (8,) * len(new))

    def test_chinese_release_regeneration(self):
        for module, lang in ((simplified, 'zh-Hans'), (traditional, 'zh-Hant')):
            with self.subTest(language=lang):
                reading, manifest = module.load()
                pages = module.render(reading, manifest, mode='release', assets={}, bilingual=False)
                for number, headings in HEADINGS.items():
                    for half in headings[lang][1]:
                        self.assertIn(half, pages[f'ch{number:03d}.html'])
                        self.assertIn(half, pages['index.html'])

    def test_english_release_regeneration(self):
        mapping, _, _, snapshot = english.load_validated()
        pipeline = english.pipeline
        approval = dict(
            schemaVersion=1, scope='english-first80-local-generation',
            publicationDate=date.today().isoformat(), sourceHash=mapping['sourceHash'],
            standardSnapshot=snapshot,
            progressHash=pipeline.sha((pipeline.DATA / 'progress.json').read_bytes()),
            notesHash=pipeline.sha((pipeline.DATA / 'reader-notes.json').read_bytes()),
        )
        pages = english.production_plan(approval)
        for number, headings in HEADINGS.items():
            for half in headings['en'][1]:
                self.assertIn(half, pages[PREFIX + f'en/ch{number:03d}.html'])
                self.assertIn(half, pages[PREFIX + 'en/index.html'])

    def test_exact_bounds(self):
        old, new = HEADINGS[18]['zh-Hans']
        src = f'<title>{" ".join(old)}</title><h1>{" ".join(old)}</h1><p>{old[0]}</p>'
        self.assertEqual(chapter(src, 'zh-Hans'),
                         f'<title>{" ".join(new)}</title><h1>{" ".join(new)}</h1><p>{old[0]}</p>')
        with self.assertRaises(ValueError):
            replace_heading(old[0] + new[1], 'zh-Hans', 1)
