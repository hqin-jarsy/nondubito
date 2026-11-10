#!/usr/bin/env python3
"""Structural tests only; passing these tests never certifies a translation."""
import copy
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import hongloumeng_english_pipeline as p


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = p.source_map(p.load_source())

    def setUp(self):
        self.progress = p.initial_progress(self.mapping)

    def draft(self, index=0):
        unit = self.progress['units'][index]
        unit['state'] = 'draft'
        unit['segments'] = [{'kind': self.mapping['units'][index]['layout']['kind'], 'text': 'Synthetic test fixture only.'}]
        return unit

    def rejected(self):
        with self.assertRaises(ValueError):
            p.validate_progress(self.mapping, self.progress, 'test-snapshot')

    def test_frozen_inventory(self):
        self.assertEqual(len(self.mapping['units']), 4474)
        blocks = [u for u in self.mapping['units'] if u['index']]
        self.assertEqual(sum(u['characterCount'] for u in blocks), 586205)
        self.assertEqual(len([u for u in blocks if u['chapter'] <= 5]), 378)
        self.assertEqual(sum(u['characterCount'] for u in blocks if u['chapter'] <= 5), 35513)
        self.assertEqual(len({u['id'] for u in self.mapping['units']}), 4474)

    def test_pending_corpus_is_valid_but_not_publishable(self):
        self.assertEqual(p.validate_progress(self.mapping, self.progress), {'pending': 4474})
        assembly = p.assemble_wip(self.mapping, self.progress)
        self.assertFalse(assembly['publishable'])
        self.assertEqual(assembly, p.assemble_wip(self.mapping, self.progress))

    def test_missing_duplicate_reordered_or_stale_units(self):
        original = copy.deepcopy(self.progress)
        self.progress['units'].pop(); self.rejected()
        self.progress = copy.deepcopy(original)
        self.progress['units'][1] = self.progress['units'][0]; self.rejected()
        self.progress = copy.deepcopy(original)
        self.progress['units'][1:3] = reversed(self.progress['units'][1:3]); self.rejected()
        self.progress = copy.deepcopy(original)
        self.progress['units'][0]['sourceHash'] = 'stale'; self.rejected()

    def test_prose_resegmentation(self):
        unit = self.draft(1)
        unit['segments'].append({'kind': 'prose', 'text': 'Another test paragraph.'})
        self.assertEqual(p.validate_progress(self.mapping, self.progress)['draft'], 1)

    def test_pending_with_content_rejected(self):
        self.draft()['state'] = 'pending'; self.rejected()

    def test_accepted_requires_three_reviews(self):
        self.draft()['state'] = 'accepted'; self.rejected()

    def test_review_binds_exact_text_and_standard(self):
        unit = self.draft()
        unit['reviews'] = [{'type': kind, 'contentHash': p.content_hash(unit), 'standardSnapshot': 'test-snapshot', 'reference': 'synthetic-test-only'} for kind in p.REVIEW_TYPES]
        unit['state'] = 'accepted'
        self.assertEqual(p.validate_progress(self.mapping, self.progress, 'test-snapshot')['accepted'], 1)
        with self.assertRaises(ValueError):
            p.validate_progress(self.mapping, self.progress, 'changed-standard')
        unit['segments'][0]['text'] += ' Changed.'; self.rejected()

    def test_verse_and_diagram_integrity(self):
        for kind in ('verse', 'couplet', 'diagram', 'letter'):
            self.progress = p.initial_progress(self.mapping)
            i = next(i for i,u in enumerate(self.mapping['units']) if u['layout']['kind'] == kind)
            unit = self.draft(i)
            unit['segments'][0]['kind'] = 'prose'; self.rejected()
            unit['segments'][0]['kind'] = kind
            unit['segments'] *= 2; self.rejected()

    def test_chinese_placeholder_rejected(self):
        self.draft()['segments'][0]['text'] = p.load_source()['chapters'][0]['title']; self.rejected()

    def test_expansion_waits_for_batch_review(self):
        i = next(i for i,u in enumerate(self.mapping['units']) if u['chapter'] == 6)
        self.draft(i); self.rejected()

    def test_incomplete_batch_cannot_be_accepted(self):
        self.progress['checkpoints'][0].update(state='accepted', corpusHash='fake', standardSnapshot='test-snapshot', reviewReference='fake')
        self.rejected()

    def test_batch_decision_alone_invalidates_review(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'CHANGELOG.md'):
                (directory / name).write_text('baseline')
            with patch.object(p, 'STANDARD', directory):
                before = p.standard_snapshot()
                unit = self.draft()
                unit['reviews'] = [{'type': kind, 'contentHash': p.content_hash(unit), 'standardSnapshot': before, 'reference': 'synthetic-test-only'} for kind in p.REVIEW_TYPES]
                unit['state'] = 'accepted'
                p.validate_progress(self.mapping, self.progress, before)
                (directory / 'english-batch-001-005.json').write_text('changed decision only')
                after = p.standard_snapshot()
                self.assertNotEqual(before, after)
                with self.assertRaisesRegex(ValueError, 'standard change'):
                    p.validate_progress(self.mapping, self.progress, after)

    def test_open_issue_blocks_acceptance_and_resolution_invalidates_review(self):
        unit = self.draft()
        issue = {'id': 'test-issue', 'unitId': unit['id'], 'sourceHash': unit['sourceHash'], 'state': 'open', 'description': 'An actual source question', 'resolution': None}
        self.progress['sourceIssues'] = [issue]
        unit['reviews'] = [{'type': kind, 'contentHash': p.content_hash(unit, [issue]), 'standardSnapshot': 'test-snapshot', 'reference': 'synthetic-test-only'} for kind in p.REVIEW_TYPES]
        unit['state'] = 'accepted'
        with self.assertRaisesRegex(ValueError, 'open source issue'):
            p.validate_progress(self.mapping, self.progress, 'test-snapshot')
        issue.update(state='resolved', resolution='Verified source and translation repair')
        with self.assertRaisesRegex(ValueError, 'source-issue change'):
            p.validate_progress(self.mapping, self.progress, 'test-snapshot')
        for review in unit['reviews']:
            review['contentHash'] = p.content_hash(unit, [issue])
        p.validate_progress(self.mapping, self.progress, 'test-snapshot')
        issue['description'] += ' Changed.'
        self.rejected()

    def test_ellipsis_is_not_automatically_a_source_issue(self):
        self.draft()['segments'][0]['text'] = 'A deliberate hesitation...'
        p.validate_progress(self.mapping, self.progress)

    def test_atomic_save_failures_preserve_canonical(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'progress.json'
            path.write_bytes(b'original canonical bytes')
            def partial_write(value, stream, **kwargs):
                stream.write('partial')
                raise OSError('injected partial write failure')
            for target, side_effect in (('json.dump', partial_write), ('os.replace', OSError('injected replace failure'))):
                with patch('hongloumeng_english_pipeline.' + target, side_effect=side_effect):
                    with self.assertRaises(OSError):
                        p.save_progress(path, self.progress)
                self.assertEqual(path.read_bytes(), b'original canonical bytes')
                self.assertEqual(list(Path(folder).iterdir()), [path])
            p.save_progress(path, self.progress)
            self.assertEqual(p.json.loads(path.read_text()), self.progress)


if __name__ == '__main__':
    unittest.main()
