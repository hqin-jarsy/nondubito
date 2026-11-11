#!/usr/bin/env python3
"""Structural tests only; passing these tests never certifies a translation."""
import copy
import json
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
        self.assertEqual(len(self.mapping['units']), 4475)
        blocks = [u for u in self.mapping['units'] if u['index']]
        self.assertEqual(sum(u['characterCount'] for u in blocks), 586221)
        self.assertEqual(len([u for u in blocks if u['chapter'] <= 5]), 378)
        self.assertEqual(sum(u['characterCount'] for u in blocks if u['chapter'] <= 5), 35513)
        self.assertEqual(len({u['id'] for u in self.mapping['units']}), 4475)

    def test_pending_corpus_is_valid_but_not_publishable(self):
        self.assertEqual(p.validate_progress(self.mapping, self.progress), {'pending': 4475})
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'CHANGELOG.md'):
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

    def test_second_batch_decision_alone_invalidates_review(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'CHANGELOG.md'):
                (directory / name).write_text('baseline')
            with patch.object(p, 'STANDARD', directory):
                before = p.standard_snapshot()
                unit = self.draft()
                unit['reviews'] = [{'type': kind, 'contentHash': p.content_hash(unit), 'standardSnapshot': before, 'reference': 'synthetic-test-only'} for kind in p.REVIEW_TYPES]
                unit['state'] = 'accepted'
                p.validate_progress(self.mapping, self.progress, before)
                (directory / 'english-batch-006-010.json').write_text('changed decision only')
                after = p.standard_snapshot()
                self.assertNotEqual(before, after)
                with self.assertRaisesRegex(ValueError, 'standard change'):
                    p.validate_progress(self.mapping, self.progress, after)

    def test_third_batch_decision_alone_invalidates_review(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'CHANGELOG.md'):
                (directory / name).write_text('baseline')
            with patch.object(p, 'STANDARD', directory):
                before = p.standard_snapshot()
                unit = self.draft()
                unit['reviews'] = [{'type': kind, 'contentHash': p.content_hash(unit), 'standardSnapshot': before, 'reference': 'synthetic-test-only'} for kind in p.REVIEW_TYPES]
                unit['state'] = 'accepted'
                p.validate_progress(self.mapping, self.progress, before)
                (directory / 'english-batch-011-015.json').write_text('changed decision only')
                after = p.standard_snapshot()
                self.assertNotEqual(before, after)
                with self.assertRaisesRegex(ValueError, 'standard change'):
                    p.validate_progress(self.mapping, self.progress, after)

    def test_fourth_batch_decision_alone_invalidates_review(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'CHANGELOG.md'):
                (directory / name).write_text('baseline')
            with patch.object(p, 'STANDARD', directory):
                before = p.standard_snapshot()
                unit = self.draft()
                unit['reviews'] = [{'type': kind, 'contentHash': p.content_hash(unit), 'standardSnapshot': before, 'reference': 'synthetic-test-only'} for kind in p.REVIEW_TYPES]
                unit['state'] = 'accepted'
                p.validate_progress(self.mapping, self.progress, before)
                (directory / 'english-batch-016-020.json').write_text('changed decision only')
                after = p.standard_snapshot()
                self.assertNotEqual(before, after)
                with self.assertRaisesRegex(ValueError, 'standard change'):
                    p.validate_progress(self.mapping, self.progress, after)

    def test_fifth_batch_decision_alone_invalidates_review(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'CHANGELOG.md'):
                (directory / name).write_text('baseline')
            with patch.object(p, 'STANDARD', directory):
                before = p.standard_snapshot()
                unit = self.draft()
                unit['reviews'] = [{'type': kind, 'contentHash': p.content_hash(unit), 'standardSnapshot': before, 'reference': 'synthetic-test-only'} for kind in p.REVIEW_TYPES]
                unit['state'] = 'accepted'
                p.validate_progress(self.mapping, self.progress, before)
                (directory / 'english-batch-021-025.json').write_text('changed decision only')
                after = p.standard_snapshot()
                self.assertNotEqual(before, after)
                with self.assertRaisesRegex(ValueError, 'standard change'):
                    p.validate_progress(self.mapping, self.progress, after)

    def test_missing_fifth_normative_file_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-026-030.json', 'CHANGELOG.md'):
                (directory / name).write_text('synthetic baseline')
            with patch.object(p, 'STANDARD', directory):
                with self.assertRaisesRegex(ValueError, 'Standard baseline'):
                    p.standard_snapshot()

    def test_every_normative_file_changes_snapshot(self):
        names = ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'CHANGELOG.md')
        self.assertEqual(len(names), 10)
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for name in names:
                (directory / name).write_text('synthetic baseline')
            with patch.object(p, 'STANDARD', directory):
                before = p.standard_snapshot()
                for name in names:
                    with self.subTest(name=name):
                        (directory / name).write_text('synthetic delta')
                        self.assertNotEqual(before, p.standard_snapshot())
                        (directory / name).write_text('synthetic baseline')
                        self.assertEqual(before, p.standard_snapshot())

    def accept_synthetic_first_twenty(self):
        # Synthetic test-only evidence, never written to a real corpus.
        for i, source in enumerate(self.mapping['units']):
            if source['chapter'] > 20:
                break
            unit = self.draft(i)
            unit['reviews'] = [{'type': kind, 'contentHash': p.content_hash(unit), 'standardSnapshot': 'test-snapshot', 'reference': 'synthetic-test-only'} for kind in p.REVIEW_TYPES]
            unit['state'] = 'accepted'
        for c in self.progress['checkpoints'][:4]:
            units = [u for source,u in zip(self.mapping['units'], self.progress['units']) if c['first'] <= source['chapter'] <= c['last']]
            c.update(state='accepted', corpusHash=p.batch_hash(units), standardSnapshot='test-snapshot', reviewReference='synthetic-test-only')

    def test_chapter_twenty_one_requires_fourth_checkpoint(self):
        self.accept_synthetic_first_twenty()
        i = next(i for i,u in enumerate(self.mapping['units']) if u['chapter'] == 21)
        self.draft(i)
        self.assertEqual(p.validate_progress(self.mapping, self.progress, 'test-snapshot')['draft'], 1)
        self.progress['checkpoints'][3].update(state='pending', corpusHash=None, standardSnapshot=None, reviewReference=None)
        with self.assertRaisesRegex(ValueError, 'preceding five-chapter'):
            p.validate_progress(self.mapping, self.progress, 'test-snapshot')

    def test_chapter_twenty_six_waits_for_fifth_checkpoint(self):
        self.accept_synthetic_first_twenty()
        i = next(i for i,u in enumerate(self.mapping['units']) if u['chapter'] == 26)
        self.draft(i)
        with self.assertRaisesRegex(ValueError, 'preceding five-chapter'):
            p.validate_progress(self.mapping, self.progress, 'test-snapshot')

    def test_missing_fourth_normative_file_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'CHANGELOG.md'):
                (directory / name).write_text('synthetic baseline')
            with patch.object(p, 'STANDARD', directory):
                with self.assertRaisesRegex(ValueError, 'Standard baseline'):
                    p.standard_snapshot()

    def test_wrong_global_source_rejected(self):
        self.progress['sourceHash'] = 'wrong-source'
        with self.assertRaisesRegex(ValueError, 'Wrong source binding'):
            p.validate_progress(self.mapping, self.progress)

    def test_release_always_disabled(self):
        with patch('sys.argv', ['pipeline', 'release']):
            with self.assertRaisesRegex(ValueError, 'publication is disabled'):
                p.main()

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

    def test_reader_notes_are_separate_and_source_bound(self):
        unit = self.mapping['units'][0]
        note = {'unitId': unit['id'], 'sourceHash': unit['sourceHash'], 'glossaryId': 'test', 'type': 'translator_note', 'text': 'A separate explanatory note.', 'presentationStatus': 'not_integrated_in_reading_presentation'}
        notes = {'schemaVersion': 1, 'sourceHash': self.mapping['sourceHash'], 'notes': [note]}
        before = copy.deepcopy(self.progress)
        self.assertEqual(p.validate_reader_notes(self.mapping, notes), 1)
        self.assertEqual(self.progress, before)
        self.assertNotIn('notes', p.assemble_wip(self.mapping, self.progress))
        for field, value in [('sourceHash', 'stale'), ('unitId', 'unknown'), ('type', 'original_text'), ('presentationStatus', 'integrated')]:
            changed = copy.deepcopy(notes)
            changed['notes'][0][field] = value
            with self.assertRaises(ValueError):
                p.validate_reader_notes(self.mapping, changed)




class FreezeReadinessTests(unittest.TestCase):
    """Synthetic configuration records only; never review evidence for real text."""
    def setUp(self):
        self.mapping = p.source_map(p.load_source())
        self.progress = p.initial_progress(self.mapping)
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.patcher = patch.object(p, 'STANDARD', self.directory)
        self.patcher.start()
        self.ref_patch = patch.object(p, 'NORMATIVE_DELTA_REFERENCES', ('EN-SYNTHETIC-TEST-ONLY', 'EN-SYNTHETIC-FINAL-TEST-ONLY'))
        self.ref_patch.start()
        self.snapshot_patch = patch.object(p, 'EXPECTED_NORMATIVE_SNAPSHOT', 'synthetic')
        self.snapshot_patch.start()
        for name in p.NORMATIVE_FILES:
            (self.directory / name).write_text('Synthetic test-only normative fixture.')
        self.batch = {'version': p.VERSION, 'status': 'frozen_editorial_checkpoint',
                      'freeze_id': 'SYNTHETIC-TEST-ONLY', 'chapters': list(range(26, 31)),
                      'sourceBinding': {'sha256': p.READING_SHA, 'manifestSha256': p.MANIFEST_SHA, 'sourceMapSha256': p.SOURCE_MAP_SHA, 'unitCount': 328},
                      'source_units': [copy.deepcopy(u) for u in self.mapping['units'] if 26 <= u['chapter'] <= 30]}
        self.checkpoint = {'version': p.VERSION, 'state': 'frozen_editorial_checkpoint', 'freeze_id': 'SYNTHETIC-TEST-ONLY',
                          'readiness': {'sourceInstalled': True, 'independentEditorialReview': 'PASS',
                                        'independentTechnicalReview': 'required_by_installation_contract', 'reviewBindingsCurrent': True,
                                        'normativeDeltaReviewReferences': list(p.NORMATIVE_DELTA_REFERENCES), 'publicationEnabled': False}}
        self.refresh()

    def tearDown(self):
        self.snapshot_patch.stop()
        self.ref_patch.stop()
        self.patcher.stop()
        self.temp.cleanup()

    def refresh(self):
        (self.directory / 'english-batch-026-030.json').write_text(json.dumps(self.batch))
        self.snapshot = p.standard_snapshot()
        p.EXPECTED_NORMATIVE_SNAPSHOT = self.snapshot
        provenance = {'normative_projection_v07': {'version': p.VERSION, 'state': 'frozen_editorial_checkpoint',
                     'sourceHash': p.READING_SHA, 'sourceMapHash': p.SOURCE_MAP_SHA, 'normativeSnapshot': self.snapshot,
                     'independentNormativeDeltaReview': 'EN-SYNTHETIC-TEST-ONLY', 'finalNormativeDeltaReview': 'EN-SYNTHETIC-FINAL-TEST-ONLY',
                     'independentTechnicalReview': 'required_by_installation_contract', 'reviewBindingsMigrated': True}}
        (self.directory / 'provenance.json').write_text(json.dumps(provenance))
        self.checkpoint['normative_snapshot'] = self.snapshot
        self.checkpoint['files'] = [{'path': 'docs/hongloumeng/translation/' + name,
                                    'sha256': p.sha((self.directory / name).read_bytes()),
                                    'bytes': (self.directory / name).stat().st_size}
                                   for name in (*p.NORMATIVE_FILES, 'provenance.json')]
        self.save_checkpoint()

    def save_checkpoint(self):
        (self.directory / 'CHECKPOINT.json').write_text(json.dumps(self.checkpoint))

    def test_coherent_synthetic_freeze(self):
        self.assertEqual(p.validate_standard_readiness(self.mapping, self.progress), self.snapshot)
        self.assertFalse(p.assemble_wip(self.mapping, self.progress)['publishable'])

    def test_pending_freeze_and_incomplete_readiness_rejected(self):
        self.checkpoint['state'] = 'editorial_working_candidate'
        self.save_checkpoint()
        with self.assertRaisesRegex(ValueError, 'not ready'):
            p.validate_standard_readiness(self.mapping, self.progress)
        self.checkpoint['state'] = 'frozen_editorial_checkpoint'
        for field, value in [('sourceInstalled', False), ('independentEditorialReview', 'pending'),
                             ('independentTechnicalReview', 'pending'), ('reviewBindingsCurrent', False), ('publicationEnabled', True)]:
            with self.subTest(field=field):
                previous = self.checkpoint['readiness'][field]
                self.checkpoint['readiness'][field] = value
                self.save_checkpoint()
                with self.assertRaisesRegex(ValueError, 'Incomplete freeze'):
                    p.validate_standard_readiness(self.mapping, self.progress)
                self.checkpoint['readiness'][field] = previous

    def test_new_batch_source_and_identity_drift_rejected(self):
        self.batch['source_units'][0]['sourceHash'] = 'stale'
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'IDs or layouts'):
            p.validate_standard_readiness(self.mapping, self.progress)
        self.batch['source_units'] = [copy.deepcopy(u) for u in self.mapping['units'] if 26 <= u['chapter'] <= 30]
        self.batch['sourceBinding']['sha256'] = 'old-source'
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'source binding'):
            p.validate_standard_readiness(self.mapping, self.progress)

    def test_sixth_batch_wrong_scope_and_partial_freeze_rejected(self):
        self.batch['chapters'] = [21, 22, 23, 24, 25]
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'chapter scope'):
            p.validate_standard_readiness(self.mapping, self.progress)
        self.batch['chapters'] = list(range(26, 31))
        self.refresh()
        self.checkpoint['files'].pop()
        self.save_checkpoint()
        with self.assertRaisesRegex(ValueError, 'file inventory'):
            p.validate_standard_readiness(self.mapping, self.progress)

    def test_wrong_source_map_sha_rejected(self):
        self.batch['sourceBinding']['sourceMapSha256'] = '0' * 64
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'source binding'):
            p.validate_standard_readiness(self.mapping, self.progress)

    def test_coherent_fabricated_reference_rejected(self):
        self.checkpoint['readiness']['normativeDeltaReviewReferences'] = ['EN-FABRICATED-NO-EVIDENCE', 'EN-FABRICATED-FINAL']
        self.save_checkpoint()
        with self.assertRaisesRegex(ValueError, 'Unexpected normative delta'):
            p.validate_standard_readiness(self.mapping, self.progress)

    def test_sixth_batch_missing_or_stale_rejected(self):
        (self.directory / 'english-batch-026-030.json').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'Unexpected normative|Partial or stale'):
            p.validate_standard_readiness(self.mapping, self.progress)
        (self.directory / 'english-batch-026-030.json').unlink()
        with self.assertRaisesRegex(ValueError, 'baseline'):
            p.standard_snapshot()


if __name__ == '__main__':
    unittest.main()
