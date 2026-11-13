"""Current-state checks that replaced the retired hash-pinned binding chain.

Retired 2026-11-13 by the owner's decision; see
data/hongloumeng/first80-english/binding-chain-retirement.json. What is checked
here is the present tree: frozen standard, exact approval of the rendered data,
the bounded chapter49 note overlay, a single Japanese placeholder table, and
byte-identical generated editions plus the hand-edited Japanese HTML.
"""
import json
import re
import unittest
from unittest.mock import patch
import hongloumeng_english_pipeline as pipeline
import build_hongloumeng_reading_english as english

APPROVAL_FIELDS = {'schemaVersion', 'scope', 'sourceHash', 'standardSnapshot',
                   'progressHash', 'notesHash', 'publicationDate'}


class StandardAndApproval(unittest.TestCase):
    def test_normative_standard_unchanged(self):
        self.assertEqual(pipeline.validate_standard_readiness(None, None),
                         pipeline.EXPECTED_NORMATIVE_SNAPSHOT)

    def test_normative_change_rejected(self):
        with patch.object(pipeline, 'standard_snapshot', return_value='0'*64):
            with self.assertRaisesRegex(ValueError, 'normative snapshot'):
                pipeline.validate_standard_readiness(None, None)

    def test_approval_records_actual_data(self):
        approval = json.loads((pipeline.DATA/'reading-publication.json').read_text())
        self.assertEqual(set(approval), APPROVAL_FIELDS)
        self.assertEqual(approval['sourceHash'], pipeline.READING_SHA)
        self.assertEqual(approval['standardSnapshot'], pipeline.EXPECTED_NORMATIVE_SNAPSHOT)
        self.assertEqual(approval['progressHash'], pipeline.sha((pipeline.DATA/'progress.json').read_bytes()))
        self.assertEqual(approval['notesHash'], pipeline.sha((pipeline.DATA/'reader-notes.json').read_bytes()))

    def test_approval_mismatch_rejected(self):
        approval = json.loads((pipeline.DATA/'reading-publication.json').read_text())
        # publicationDate is the recorded first-generation date, not a data hash.
        for change in ({'progressHash': '0'*64}, {'notesHash': '0'*64},
                       {'standardSnapshot': '0'*64}, {'implementationHashes': {}}):
            with self.assertRaisesRegex(ValueError, 'approval'):
                english.production_plan(dict(approval, **change))


class Chapter49Overlay(unittest.TestCase):
    def test_bounded_overlay_without_chain(self):
        from hongloumeng_seven_character_binding import note_record, TARGET
        mapping = pipeline.source_map(pipeline.load_source())
        progress = json.loads((pipeline.DATA/'progress.json').read_text())
        notes = json.loads((pipeline.DATA/'reader-notes.json').read_text())
        note = next(n for n in notes['notes'] if n['unitId'] == TARGET)
        source = next(u for u in mapping['units'] if u['id'] == TARGET)
        unit = next(u for u in progress['units'] if u['id'] == TARGET)
        name, position = re.fullmatch(r'(english-batch-[0-9]{3}-[0-9]{3}\.json)#/selectedReaderNotes/(\d+)',
                                      note['glossaryId']).groups()
        frozen = json.loads((pipeline.STANDARD/name).read_text())['selectedReaderNotes'][int(position)]
        record = note_record(frozen, note, source, unit, pipeline.ROOT)
        anchor = record['anchor']
        self.assertEqual(record['text'], note['text'])
        self.assertEqual(unit['segments'][0]['text'][anchor['start']:anchor['end']], anchor['text'])
        self.assertEqual((anchor['start'], anchor['end']),
                         (frozen['anchor']['start']+1, frozen['anchor']['end']+1))


class JapanesePlaceholders(unittest.TestCase):
    def test_single_table_matches_data_and_pages(self):
        from hongloumeng_japanese_availability import japanese_publication
        root = pipeline.ROOT
        current = japanese_publication(root)
        self.assertEqual(current['partial'], {})
        hub = (root/'essays/literature/hlm/index.html').read_text()
        self.assertIn('日文版有4处依作者决定保留中文原文', hub)


class ReaderEditions(unittest.TestCase):
    def test_all_reader_editions_byte_identical(self):
        import refresh_hongloumeng_reading_discovery as d
        public = pipeline.ROOT/'data/hongloumeng/first80-public'
        m = json.loads((public/'manifest.json').read_text())
        mt = json.loads((public/'manifest.zh-hant.json').read_text())
        approval = dict(text_version=m['text_version'], reading_sha256=m['reading_sha256'],
                        body_sha256=m['body_sha256'], assets_sha256=m['build']['assets_sha256'],
                        boundaries_finalized=True)
        traditional = dict(action='publish-hongloumeng-first80-traditional', approved=True,
                           text_version=mt['text_version'], reading_sha256=mt['reading_sha256'],
                           body_sha256=mt['body_sha256'], assets_sha256=mt['build']['assets_sha256'],
                           boundaries_finalized=True)
        paths = d.validate_published_reader(pipeline.ROOT, approval, traditional_approval=traditional)
        prefixes = {'classics/hongloumeng/'+p for p in ('zh-hant/', 'en/', 'ja/')}
        counts = {}
        for path in paths:
            relative = path.relative_to(pipeline.ROOT).as_posix()
            key = next((p for p in prefixes if relative.startswith(p)), 'classics/hongloumeng/')
            counts[key] = counts.get(key, 0) + 1
        self.assertEqual(counts, {'classics/hongloumeng/': 82, 'classics/hongloumeng/zh-hant/': 82,
                                  'classics/hongloumeng/en/': 82, 'classics/hongloumeng/ja/': 82})


if __name__ == '__main__':
    unittest.main()
