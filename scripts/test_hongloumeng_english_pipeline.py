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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'CHANGELOG.md'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'CHANGELOG.md'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'CHANGELOG.md'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'CHANGELOG.md'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'CHANGELOG.md'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'CHANGELOG.md'):
                (directory / name).write_text('synthetic baseline')
            with patch.object(p, 'STANDARD', directory):
                with self.assertRaisesRegex(ValueError, 'Standard baseline'):
                    p.standard_snapshot()

    def test_every_normative_file_changes_snapshot(self):
        names = ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'CHANGELOG.md')
        self.assertEqual(len(names), 11)
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'CHANGELOG.md'):
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




class FreezeReadinessV08Tests(unittest.TestCase):
    """Tamper tests use copies only. These tests never certify editorial quality."""
    def setUp(self):
        self.mapping = p.source_map(p.load_source())
        self.progress = json.loads((p.DATA / 'progress.json').read_bytes())
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        for name in (*p.NORMATIVE_FILES, 'provenance.json', 'CHECKPOINT.json'):
            (self.directory / name).write_bytes((p.STANDARD / name).read_bytes())
        self.patch = patch.object(p, 'STANDARD', self.directory)
        self.patch.start()
        self.expected = patch.object(p, 'EXPECTED_NORMATIVE_SNAPSHOT', p.EXPECTED_NORMATIVE_SNAPSHOT)
        self.expected.start()
        self.batch = json.loads((self.directory / 'english-batch-031-035.json').read_bytes())
        self.checkpoint = json.loads((self.directory / 'CHECKPOINT.json').read_bytes())
        self.provenance = json.loads((self.directory / 'provenance.json').read_bytes())

    def tearDown(self):
        self.expected.stop()
        self.patch.stop()
        self.temp.cleanup()

    def save(self, name, obj):
        (self.directory / name).write_text(json.dumps(obj))

    def check(self):
        return p.validate_standard_readiness(self.mapping, self.progress)

    def coherent_metadata(self):
        self.save('english-batch-031-035.json', self.batch)
        self.save('provenance.json', self.provenance)
        p.EXPECTED_NORMATIVE_SNAPSHOT = p.standard_snapshot()
        self.checkpoint['normative_snapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        self.checkpoint['normativeTransitionV08']['normativeSnapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        self.provenance['normative_projection_v08']['normativeSnapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        self.save('provenance.json', self.provenance)
        for row in self.checkpoint['files']:
            name = Path(row['path']).name
            if (self.directory / name).is_file():
                raw = (self.directory / name).read_bytes()
                row.update(sha256=p.sha(raw), bytes=len(raw))
        self.save('CHECKPOINT.json', self.checkpoint)

    def test_installed_configuration(self):
        self.assertEqual(self.check(), p.EXPECTED_NORMATIVE_SNAPSHOT)

    def test_seventh_batch_missing(self):
        (self.directory / 'english-batch-031-035.json').unlink()
        with self.assertRaises(ValueError): self.check()

    def test_semantic_bytes_changed(self):
        self.batch['terms'][66]['scope'] += ' Synthetic unauthorized change.'
        self.save('english-batch-031-035.json', self.batch)
        with self.assertRaisesRegex(ValueError, 'Unexpected normative snapshot'): self.check()

    def test_stale_snapshot(self):
        p.EXPECTED_NORMATIVE_SNAPSHOT = 'stale'
        with self.assertRaisesRegex(ValueError, 'Unexpected normative snapshot'): self.check()

    def test_pending_checkpoint(self):
        self.checkpoint['state'] = 'pending'
        self.save('CHECKPOINT.json', self.checkpoint)
        with self.assertRaisesRegex(ValueError, 'not ready'): self.check()

    def test_stale_checkpoint_snapshot(self):
        self.checkpoint['normative_snapshot'] = 'old'
        self.save('CHECKPOINT.json', self.checkpoint)
        with self.assertRaisesRegex(ValueError, 'Partial or stale'): self.check()

    def test_missing_freeze_id(self):
        self.checkpoint['freeze_id'] = ''
        self.save('CHECKPOINT.json', self.checkpoint)
        with self.assertRaisesRegex(ValueError, 'Freeze identifier'): self.check()

    def test_bad_inventory(self):
        for mode in ('duplicate', 'missing', 'hash', 'bytes'):
            original = copy.deepcopy(self.checkpoint)
            if mode == 'duplicate': self.checkpoint['files'].append(copy.deepcopy(self.checkpoint['files'][0]))
            elif mode == 'missing': self.checkpoint['files'].pop(0)
            elif mode == 'hash': self.checkpoint['files'][0]['sha256'] = 'wrong'
            else: self.checkpoint['files'][0]['bytes'] = -1
            self.save('CHECKPOINT.json', self.checkpoint)
            with self.subTest(mode=mode), self.assertRaises(ValueError): self.check()
            self.checkpoint = original

    def test_batch_status_version_or_freeze(self):
        for key in ('version', 'status', 'freeze_id'):
            old = self.batch[key];self.batch[key] = 'wrong';self.coherent_metadata()
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'seventh batch'): self.check()
            self.batch[key] = old

    def test_batch_scope(self):
        self.batch['chapters'] = list(range(26,31));self.coherent_metadata()
        with self.assertRaisesRegex(ValueError, 'chapter scope'): self.check()

    def test_source_binding(self):
        for key in ('sha256', 'manifestSha256', 'sourceMapSha256', 'sourceMapSHA256', 'unitCount', 'currentBatchUnits', 'totalSourceUnits'):
            old = self.batch['sourceBinding'][key];self.batch['sourceBinding'][key] = 'wrong';self.coherent_metadata()
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'source binding'): self.check()
            self.batch['sourceBinding'][key] = old

    def test_source_unit_layout(self):
        self.batch['source_units'][0]['layout']['kind'] = 'prose';self.coherent_metadata()
        with self.assertRaisesRegex(ValueError, 'layouts drifted'): self.check()

    def test_readiness_flags(self):
        for key, value in [('sourceInstalled', False), ('independentEditorialReview', 'pending'), ('independentTechnicalReview', 'PASS'), ('reviewBindingsCurrent', False), ('publicationEnabled', True)]:
            old = self.checkpoint['readiness'][key];self.checkpoint['readiness'][key] = value;self.save('CHECKPOINT.json', self.checkpoint)
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'Incomplete freeze'): self.check()
            self.checkpoint['readiness'][key] = old

    def test_fabricated_references(self):
        self.checkpoint['readiness']['normativeDeltaReviewReferences'] = ['FABRICATED']
        self.save('CHECKPOINT.json', self.checkpoint)
        with self.assertRaisesRegex(ValueError, 'Unexpected normative delta'): self.check()

    def test_historical_provenance_mutation(self):
        self.provenance['normative_projection_v07']['state'] = 'rewritten';self.coherent_metadata()
        with self.assertRaisesRegex(ValueError, 'Historical provenance'): self.check()

    def test_historical_checkpoint_mutation(self):
        self.provenance['normative_projection_v08']['previousCheckpoint']['scope'] = 'rewritten';self.coherent_metadata()
        with self.assertRaisesRegex(ValueError, 'Historical checkpoint'): self.check()

    def test_historical_clarification_rewritten(self):
        self.checkpoint['normativeAmendment']['reference'] = 'rewritten';self.save('CHECKPOINT.json', self.checkpoint)
        with self.assertRaisesRegex(ValueError, 'Historical clarification'): self.check()

    def test_transition_missing_or_forged(self):
        self.provenance['normative_projection_v08']['references'] = ['FABRICATED'];self.coherent_metadata()
        with self.assertRaisesRegex(ValueError, 'transition chain'): self.check()

    def test_provenance_source_or_flags(self):
        for key, value in [('sourceHash', 'wrong'), ('sourceMapHash', 'wrong'), ('reviewBindingsMigrated', False), ('independentTechnicalReview', 'PASS')]:
            old=self.provenance['normative_projection_v08'][key];self.provenance['normative_projection_v08'][key]=value;self.coherent_metadata()
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'provenance binding'): self.check()
            self.provenance['normative_projection_v08'][key]=old

    def test_missing_review_reference(self):
        self.progress['units'][0]['reviews'][0]['reference'] = 'OLD-ONLY'
        with self.assertRaisesRegex(ValueError, 'missing actual normative'): self.check()

    def test_prior_batch_acceptance_removed(self):
        self.progress['units'][0]['state'] = 'reviewed'
        with self.assertRaisesRegex(ValueError, 'six batches'): self.check()

    def test_prior_checkpoint_acceptance_removed(self):
        self.progress['checkpoints'][5]['state'] = 'pending'
        with self.assertRaisesRegex(ValueError, 'six checkpoints'): self.check()

    def test_checkpoint_reference_removed(self):
        self.progress['checkpoints'][5]['reviewReference'] = 'OLD-ONLY'
        with self.assertRaisesRegex(ValueError, 'Checkpoint missing'): self.check()

    def test_accepted_prose_mutation(self):
        self.progress['units'][0]['segments'][0]['text'] += ' Synthetic change.'
        with self.assertRaisesRegex(ValueError, 'stale'): self.check()

    def assert_outside_batch_pending(self, progress):
        last_chapter = max(self.batch['chapters'])
        self.assertTrue(all(u['state'] == 'pending' and not u['segments'] and not u['reviews']
                            for m, u in zip(self.mapping['units'], progress['units'])
                            if m['chapter'] > last_chapter))

    def test_pending_units_unchanged(self):
        self.assert_outside_batch_pending(self.progress)
        self.assertEqual(p.validate_reader_notes(self.mapping,json.loads((p.DATA/'reader-notes.json').read_bytes())),20)

    def test_current_batch_may_progress(self):
        progress = copy.deepcopy(self.progress)
        index = next(i for i, m in enumerate(self.mapping['units'])
                     if m['chapter'] == max(self.batch['chapters']))
        # Only the boundary assertion is under test; this is not review evidence.
        for state in ('pending', 'draft', 'reviewed', 'accepted'):
            progress['units'][index].update(state=state, segments=[], reviews=[])
            with self.subTest(state=state):
                self.assert_outside_batch_pending(progress)

    def test_outside_batch_nonpending_rejected(self):
        for chapter in (max(self.batch['chapters']) + 1, max(m['chapter'] for m in self.mapping['units'])):
            progress = copy.deepcopy(self.progress)
            index = next(i for i, m in enumerate(self.mapping['units']) if m['chapter'] == chapter)
            progress['units'][index]['state'] = 'draft'
            with self.subTest(chapter=chapter), self.assertRaises(AssertionError):
                self.assert_outside_batch_pending(progress)

    def test_outside_batch_content_rejected(self):
        for chapter in (max(self.batch['chapters']) + 1, max(m['chapter'] for m in self.mapping['units'])):
            progress = copy.deepcopy(self.progress)
            index = next(i for i, m in enumerate(self.mapping['units']) if m['chapter'] == chapter)
            progress['units'][index]['segments'] = [{'kind': 'title', 'text': 'Synthetic boundary probe only.'}]
            with self.subTest(chapter=chapter), self.assertRaises(AssertionError):
                self.assert_outside_batch_pending(progress)

    def test_outside_batch_review_rejected(self):
        for chapter in (max(self.batch['chapters']) + 1, max(m['chapter'] for m in self.mapping['units'])):
            progress = copy.deepcopy(self.progress)
            index = next(i for i, m in enumerate(self.mapping['units']) if m['chapter'] == chapter)
            progress['units'][index]['reviews'] = [{'reference': 'synthetic-boundary-probe-only'}]
            with self.subTest(chapter=chapter), self.assertRaises(AssertionError):
                self.assert_outside_batch_pending(progress)


class ClosingQuoteTests(unittest.TestCase):
    """Synthetic acceptance fixtures exercise mechanics, never editorial approval."""
    QUOTES = ('hlm-c028-b0092', 'hlm-c028-b0123', 'hlm-c040-b0055', 'hlm-c040-b0060')
    SNAPSHOT = 'synthetic-closing-quote-test-only'

    @classmethod
    def setUpClass(cls):
        cls.mapping = p.source_map(p.load_source())
        cls.positions = {u['id']: i for i, u in enumerate(cls.mapping['units'])}
        cls.fixtures = {}
        for last in (25, 35):
            progress = p.initial_progress(cls.mapping)
            for source, unit in zip(cls.mapping['units'], progress['units']):
                if source['chapter'] <= last:
                    unit.update(state='accepted', segments=[{'kind': source['layout']['kind'],
                                'text': 'Synthetic closing-quote test fixture only.'}])
                    unit['reviews'] = [{'type': kind, 'contentHash': p.content_hash(unit),
                                        'standardSnapshot': cls.SNAPSHOT, 'reference': 'synthetic-test-only'}
                                       for kind in p.REVIEW_TYPES]
            for checkpoint in progress['checkpoints']:
                if checkpoint['last'] <= last:
                    units = [u for s, u in zip(cls.mapping['units'], progress['units'])
                             if checkpoint['first'] <= s['chapter'] <= checkpoint['last']]
                    checkpoint.update(state='accepted', corpusHash=p.batch_hash(units),
                                      standardSnapshot=cls.SNAPSHOT, reviewReference='synthetic-test-only')
            cls.fixtures[last] = progress

    def trial(self, identifier=QUOTES[0], text='’'):
        position = self.positions[identifier]
        last = 25 if self.mapping['units'][position]['chapter'] < 31 else 35
        progress = copy.deepcopy(self.fixtures[last])
        unit = progress['units'][position]
        unit.update(state='draft', segments=[{'kind': 'prose', 'text': text}], reviews=[])
        return progress, unit

    def validate(self, progress, mapping=None):
        return p.validate_progress(self.mapping if mapping is None else mapping, progress, self.SNAPSHOT)

    def test_actual_four_source_units_and_supported_closers(self):
        self.assertEqual(p.closing_quote_source_ids(self.mapping), set(self.QUOTES))
        for identifier in self.QUOTES:
            for closer in ('’', "'", '"'):
                with self.subTest(identifier=identifier, closer=closer):
                    progress, unit = self.trial(identifier, closer)
                    self.assertEqual(self.validate(progress)['draft'], 1)
                    self.assertEqual(unit['segments'], [{'kind': 'prose', 'text': closer}])

    def test_invalid_punctuation_empty_digits_chinese_and_padding(self):
        for text in ('', ' ', '\n', '”', '‘', '“', '`', '.', '...', '…', '。', ',', '—',
                     '123', '未译中文', '’’', ' ’', '’ ', '’\n', '\u200b’', '\u202e’'):
            with self.subTest(text=text):
                progress, unit = self.trial(text=text)
                with self.assertRaises(ValueError):
                    self.validate(progress)

    def test_ordinary_prose_and_title_cannot_use_closer(self):
        for position in (0, 1):
            progress = copy.deepcopy(self.fixtures[25])
            progress['units'][position].update(state='draft', reviews=[], segments=[
                {'kind': self.mapping['units'][position]['layout']['kind'], 'text': '’'}])
            with self.subTest(position=position), self.assertRaisesRegex(ValueError, 'No English letters'):
                self.validate(progress)

    def test_verse_cannot_use_closer(self):
        position = next(i for i, u in enumerate(self.mapping['units']) if u['layout']['kind'] == 'verse')
        progress = copy.deepcopy(self.fixtures[25])
        progress['units'][position].update(state='draft', reviews=[], segments=[{'kind': 'verse', 'text': '’'}])
        with self.assertRaisesRegex(ValueError, 'No English letters'):
            self.validate(progress)

    def test_standalone_quote_cannot_split_or_add_filler(self):
        for other in ('’', 'Synthetic filler.'):
            progress, unit = self.trial()
            unit['segments'].append({'kind': 'prose', 'text': other})
            with self.subTest(other=other), self.assertRaisesRegex(ValueError, 'No English letters'):
                self.validate(progress)

    def test_wrong_unit_id_or_source_hash_rejected(self):
        for field, value in [('id', 'hlm-c028-b0093'), ('sourceHash', '0' * 64)]:
            progress, unit = self.trial()
            unit[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'missing, duplicated, reordered, or stale'):
                self.validate(progress)

    def test_wrong_segment_kind_rejected(self):
        progress, unit = self.trial()
        unit['segments'][0]['kind'] = 'verse'
        with self.assertRaisesRegex(ValueError, 'kind lost'):
            self.validate(progress)

    def test_forged_map_unit_hash_id_length_or_layout_rejected(self):
        for field, value in [('sourceHash', '0' * 64), ('id', 'hlm-c028-b9999'),
                             ('characterCount', 2), ('layout', {'kind': 'prose', 'first': True})]:
            mapping = copy.deepcopy(self.mapping)
            progress, unit = self.trial()
            source = mapping['units'][self.positions[self.QUOTES[0]]]
            source[field] = value
            if field in ('id', 'sourceHash'):
                unit[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Closing-quote source map differs'):
                self.validate(progress, mapping)

    def test_forged_title_map_and_matching_segment_rejected(self):
        mapping = copy.deepcopy(self.mapping)
        progress, unit = self.trial()
        mapping['units'][self.positions[self.QUOTES[0]]]['layout'] = {'kind': 'title'}
        unit['segments'][0]['kind'] = 'title'
        with self.assertRaisesRegex(ValueError, 'Closing-quote source map differs'):
            self.validate(progress, mapping)

    def test_wrong_global_source_or_manifest_or_body_rejected(self):
        for field in ('sourceHash', 'manifestHash', 'bodyHash'):
            mapping = copy.deepcopy(self.mapping)
            mapping[field] = '0' * 64
            progress, unit = self.trial()
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate(progress, mapping)

    def test_modified_actual_source_or_manifest_rejected(self):
        original = Path.read_bytes
        for name in ('reading.zh.json', 'manifest.json'):
            def read(path):
                raw = original(path)
                return raw + b' ' if path == p.SOURCE / name else raw
            progress, unit = self.trial()
            with self.subTest(name=name), patch.object(Path, 'read_bytes', read):
                with self.assertRaisesRegex(ValueError, 'Frozen Chinese source changed'):
                    self.validate(progress)

    def test_map_order_duplicate_or_missing_unit_rejected(self):
        for mode in ('reordered', 'duplicate', 'missing'):
            mapping = copy.deepcopy(self.mapping)
            progress, unit = self.trial()
            if mode == 'reordered':
                mapping['units'][-2:] = reversed(mapping['units'][-2:])
            elif mode == 'duplicate':
                mapping['units'][-1] = copy.deepcopy(mapping['units'][-2])
            else:
                mapping['units'].pop()
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                self.validate(progress, mapping)

    def test_no_source_reload_for_ordinary_accepted_fixture(self):
        with patch.object(p, 'load_source', side_effect=AssertionError('Unexpected fallback')):
            self.validate(copy.deepcopy(self.fixtures[25]))

    def test_source_validation_once_for_two_quote_units_per_call(self):
        progress, unit = self.trial()
        other = progress['units'][self.positions[self.QUOTES[1]]]
        other.update(state='draft', segments=[{'kind': 'prose', 'text': '’'}], reviews=[])
        with patch.object(p, 'load_source', wraps=p.load_source) as load:
            self.assertEqual(self.validate(progress)['draft'], 2)
            self.assertEqual(load.call_count, 1)

    def test_quote_does_not_bypass_preceding_batch_gate(self):
        progress = p.initial_progress(self.mapping)
        position = self.positions[self.QUOTES[-1]]
        progress['units'][position].update(state='draft', segments=[{'kind': 'prose', 'text': '’'}])
        with self.assertRaisesRegex(ValueError, 'preceding five-chapter'):
            self.validate(progress)

    def test_quote_does_not_bypass_review_or_issue_acceptance(self):
        progress, unit = self.trial()
        unit['state'] = 'accepted'
        with self.assertRaisesRegex(ValueError, 'all required'):
            self.validate(progress)
        unit['reviews'] = [{'type': kind, 'contentHash': p.content_hash(unit),
                            'standardSnapshot': self.SNAPSHOT, 'reference': 'synthetic-test-only'}
                           for kind in p.REVIEW_TYPES]
        progress['sourceIssues'] = [{'id': 'synthetic-quote-issue', 'unitId': unit['id'],
                                   'sourceHash': unit['sourceHash'], 'state': 'open',
                                   'description': 'Synthetic test only.', 'resolution': None}]
        for review in unit['reviews']:
            review['contentHash'] = p.content_hash(unit, progress['sourceIssues'])
        with self.assertRaisesRegex(ValueError, 'blocked by open source issue'):
            self.validate(progress)

    def test_quote_content_change_invalidates_review(self):
        progress, unit = self.trial()
        unit['reviews'] = [{'type': 'bilingual', 'contentHash': p.content_hash(unit),
                            'standardSnapshot': self.SNAPSHOT, 'reference': 'synthetic-test-only'}]
        unit['segments'][0]['text'] = "'"
        with self.assertRaisesRegex(ValueError, 'Review is stale'):
            self.validate(progress)


if __name__ == '__main__':
    unittest.main()
