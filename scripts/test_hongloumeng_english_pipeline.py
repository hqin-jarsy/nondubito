#!/usr/bin/env python3
"""Structural tests only; passing these tests never certifies a translation."""
import copy
import ast
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
        self.assertEqual(sum(u['characterCount'] for u in blocks), 586224)
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
        for kind in ('verse', 'couplet', 'diagram'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md', 'english-batch-041-045.json'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md', 'english-batch-041-045.json'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md', 'english-batch-041-045.json'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md', 'english-batch-041-045.json'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md', 'english-batch-041-045.json'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md', 'english-batch-041-045.json'):
                (directory / name).write_text('synthetic baseline')
            with patch.object(p, 'STANDARD', directory):
                with self.assertRaisesRegex(ValueError, 'Standard baseline'):
                    p.standard_snapshot()

    def test_every_normative_file_changes_snapshot(self):
        names = ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md', 'english-batch-041-045.json')
        self.assertEqual(len(names), 13)
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md', 'english-batch-041-045.json'):
                (directory / name).write_text('synthetic baseline')
            with patch.object(p, 'STANDARD', directory):
                with self.assertRaisesRegex(ValueError, 'Standard baseline'):
                    p.standard_snapshot()

    def test_wrong_global_source_rejected(self):
        self.progress['sourceHash'] = 'wrong-source'
        with self.assertRaisesRegex(ValueError, 'Wrong source binding'):
            p.validate_progress(self.mapping, self.progress)

    def test_release_always_disabled(self):
        # Static inspection only: never invoke the denied release handler.
        tree = ast.parse(Path(p.__file__).read_text())
        main = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'main')
        guards = [(i, x.value) for i, x in enumerate(main.body)
                  if isinstance(x, ast.Expr) and isinstance(x.value, ast.Call)
                  and isinstance(x.value.func, ast.Name) and x.value.func.id == 'require'
                  and x.value.args and isinstance(x.value.args[0], ast.Compare)
                  and ast.dump(x.value.args[0]) == ast.dump(ast.parse("args.action != 'release'", mode='eval').body)]
        self.assertEqual(len(guards), 1)
        position, guard = guards[0]
        self.assertIn('English publication is disabled', guard.args[1].value)
        load_position = next(i for i, x in enumerate(main.body)
                             if isinstance(x, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'mapping' for t in x.targets))
        self.assertLess(position, load_position)

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




class FinalReadinessV09Tests(unittest.TestCase):
    """Final-status candidate binds real limited review, not new English acceptance."""
    def test_actual_evidence_and_references_bound(self):
        self.assertIsInstance(p.V09_SEMANTIC_EVIDENCE_SHA, str)
        self.assertEqual(p.V09_DELTA_REFERENCES, ('EN-V09-PROJECTION-R1-SEMANTIC-20261111', 'EN-V09-PROJECTION-R2-LOCATOR-DELTA-20261111'))

    def test_final_candidate_current_bindings_validate(self):
        mapping = p.source_map(p.load_source())
        progress = json.loads((p.DATA / 'progress.json').read_bytes())
        if p.CURRENT_SOURCE_EVIDENCE_SHA is None:
            with self.assertRaisesRegex(ValueError, 'Awaiting authenticated current source'):
                p.validate_standard_readiness(mapping, progress)
        else:
            self.assertEqual(p.validate_standard_readiness(mapping, progress), p.EXPECTED_NORMATIVE_SNAPSHOT)
        self.assertEqual(sum(u['state'] == 'accepted' for u in progress['units']), 2461)
        self.assertEqual(sum(u['state'] == 'pending' for u in progress['units']), 2014)
        prior = [u for s,u in zip(mapping['units'],progress['units']) if s['chapter'] <= 35]
        batch = [u for s,u in zip(mapping['units'],progress['units']) if 36 <= s['chapter'] <= 40]
        self.assertEqual(len(prior), 1885)
        self.assertTrue(all(u['state'] == 'accepted' for u in prior))
        self.assertEqual(sum(len(u['reviews']) for u in prior), 5655)
        self.assertEqual(len(batch), 376)
        self.assertTrue(all(u['state'] == 'accepted' for u in batch))
        self.assertEqual(sum(len(u['segments']) for u in batch), 1140)
        self.assertEqual(sum(len(u['reviews']) for u in batch), 1128)
        self.assertEqual(sum(c['state'] == 'accepted' for c in progress['checkpoints']), 9)

    def test_eighth_batch_is_normative(self):
        self.assertIn('english-batch-036-040.json', p.NORMATIVE_FILES)
        self.assertEqual(p.standard_snapshot(), p.EXPECTED_NORMATIVE_SNAPSHOT)


class FreezeReadinessV09Tests(unittest.TestCase):
    """Synthetic current configuration, with untouched real historical metadata.

    This class isolates the historical v0.9/source layer with explicit naming-layer mocks.
    FelicityRevisionTests separately exercises the actual full chain without mocks.
    The original v0.8 purposes are retained, not bypassed. All newly accepted
    English and current review evidence below are explicitly synthetic.
    """
    def setUp(self):
        self.mapping = p.source_map(p.load_source())
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        for name in (*p.NORMATIVE_FILES, 'provenance.json', 'CHECKPOINT.json'):
            (self.directory / name).write_bytes((p.STANDARD / name).read_bytes())
        self.patches = [patch.object(p, 'VERSION', p.V09_VERSION), patch.object(p, 'load_felicity_before', lambda document: self.progress),
                        patch.object(p, 'validate_felicity_revision'),
                        patch.object(p, 'FELICITY_BEFORE_NORMATIVE_SNAPSHOT', p.FELICITY_BEFORE_NORMATIVE_SNAPSHOT),
                        patch.object(p, 'V09_HISTORICAL_NORMATIVE_SNAPSHOT', p.V09_HISTORICAL_NORMATIVE_SNAPSHOT),
                        patch.object(p, 'V09_HISTORICAL_PROVENANCE_SHA', p.V09_HISTORICAL_PROVENANCE_SHA),
                        patch.object(p, 'CURRENT_SOURCE_EVIDENCE_SHA', None),
                        patch.object(p, 'CURRENT_ACCEPTED_BODIES_SHA', p.CURRENT_ACCEPTED_BODIES_SHA),
                        patch.object(p, 'CURRENT_REVIEW_CONTENT_SHA', p.CURRENT_REVIEW_CONTENT_SHA),
                        patch.object(p, 'CURRENT_OLD_REFERENCES_SHA', p.CURRENT_OLD_REFERENCES_SHA),
                        patch.object(p, 'CURRENT_CHECKPOINT_CORPUS_HASHES', p.CURRENT_CHECKPOINT_CORPUS_HASHES),
                        patch.object(p, 'CURRENT_SOURCE_DELTA_REFERENCE', 'SYNTHETIC-CURRENT-SOURCE-ONLY'),
                        patch.object(p, 'STANDARD', self.directory),
                        patch.object(p, 'EXPECTED_NORMATIVE_SNAPSHOT', p.EXPECTED_NORMATIVE_SNAPSHOT),
                        patch.object(p, 'V09_SEMANTIC_EVIDENCE_SHA', None),
                        patch.object(p, 'V09_DELTA_REFERENCES', ('SYNTHETIC-V09-DELTA-NOT-REAL',)),
                        patch.object(p, 'V09_FINAL_STATUS_REFERENCE', 'SYNTHETIC-FINAL-STATUS-NOT-REAL'),
                        patch.object(p, 'V09_FINAL_STATUS_EVIDENCE_SHA', p.V09_FINAL_STATUS_EVIDENCE_SHA)]
        for item in self.patches: item.start()
        self.batch = json.loads((self.directory / 'english-batch-036-040.json').read_bytes())
        self.checkpoint = json.loads((self.directory / 'CHECKPOINT.json').read_bytes())
        self.provenance = json.loads((self.directory / 'provenance.json').read_bytes())
        self.checkpoint = self.checkpoint['previousCheckpoint']
        self.provenance.pop('normative_projection_v010')
        self.provenance.pop(p.FELICITY_AMENDMENT_KEY)  # Only the synthetic historical layer is under test here.
        self.batch.update(status='frozen_editorial_checkpoint', freeze_id='SYNTHETIC-ONLY')
        self.batch['gate'] = {'formalFreeze': True, 'independentEditorialReview': True, 'sourceMigrationComplete': True, 'englishAcceptance': False, 'publicationEnabled': False}
        self.checkpoint.update(state='frozen_editorial_checkpoint', freeze_id='SYNTHETIC-ONLY')
        self.checkpoint['readiness'] = {'sourceInstalled': True, 'independentEditorialReview': 'PASS', 'independentSemanticDeltaReview': 'PASS', 'independentTechnicalReview': 'required_by_installation_contract', 'reviewBindingsCurrent': True, 'publicationEnabled': False, 'normativeDeltaReviewReferences': list(p.V09_DELTA_REFERENCES)}
        t = self.provenance['normative_projection_v09']
        t.update(state='frozen_editorial_checkpoint', reviewBindingsMigrated=True, independentEditorialReview='PASS', independentSemanticDeltaReview='PASS', independentTechnicalReview='required_by_installation_contract')
        t['finalStatusReview'] = {'status': 'PASS', 'reference': p.V09_FINAL_STATUS_REFERENCE, 'normativeSnapshot': None, 'scope': 'SYNTHETIC FINAL STATUS TEST ONLY'}
        t['semanticDeltaReview'] = {'status': 'PASS', 'references': list(p.V09_DELTA_REFERENCES), 'previousNormativeSnapshot': p.V09_PREVIOUS_NORMATIVE_SNAPSHOT, 'normativeSnapshot': None, 'sourceHash': p.V09_HISTORICAL_READING_SHA, 'sourceMapHash': p.V09_HISTORICAL_MAP_SHA, 'acceptedBodiesUnchanged': True, 'notFullCorpusReread': True, 'reviewedEarlierUnitIds': ['hlm-c023-b0063'], 'scope': 'SYNTHETIC TEST ONLY'}
        self.progress = p.initial_progress(self.mapping)
        refs = '; '.join((*p.V09_DELTA_REFERENCES, p.V09_FINAL_STATUS_REFERENCE, *p.NORMATIVE_DELTA_REFERENCES, p.SOURCE_DELTA_REFERENCE, p.CURRENT_SOURCE_DELTA_REFERENCE))
        for s, u in zip(self.mapping['units'], self.progress['units']):
            if s['chapter'] <= 35:
                u.update(state='accepted', segments=[{'kind': s['layout']['kind'], 'text': 'SYNTHETIC TEST TEXT ONLY.'}])
                u['reviews'] = [{'type': typ, 'contentHash': p.content_hash(u), 'standardSnapshot': None, 'reference': refs} for typ in p.REVIEW_TYPES]
        for c in self.progress['checkpoints'][:7]:
            units = [u for s, u in zip(self.mapping['units'], self.progress['units']) if c['first'] <= s['chapter'] <= c['last']]
            c.update(state='accepted', corpusHash=p.batch_hash(units), standardSnapshot=None, reviewReference=refs)
        self.coherent_metadata()

    def tearDown(self):
        for item in reversed(self.patches): item.stop()
        self.temp.cleanup()

    def save(self, name, value):
        (self.directory / name).write_text(json.dumps(value, ensure_ascii=False))

    def coherent_metadata(self):
        self.save('english-batch-036-040.json', self.batch)
        p.EXPECTED_NORMATIVE_SNAPSHOT = p.standard_snapshot()
        p.FELICITY_BEFORE_NORMATIVE_SNAPSHOT = p.EXPECTED_NORMATIVE_SNAPSHOT
        self.checkpoint['normative_snapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        transition = self.provenance['normative_projection_v09']
        p.V09_HISTORICAL_NORMATIVE_SNAPSHOT = p.EXPECTED_NORMATIVE_SNAPSHOT
        transition['candidateNormativeSnapshot'] = p.V09_HISTORICAL_NORMATIVE_SNAPSHOT
        transition['semanticDeltaReview']['normativeSnapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        p.V09_SEMANTIC_EVIDENCE_SHA = p.sha(p.encoded(transition['semanticDeltaReview']))
        self.checkpoint['normativeTransitionV09'] = {k: transition[k] for k in ('previousNormativeSnapshot', 'previousProvenanceSHA256', 'previousCheckpointSHA256', 'candidateNormativeSnapshot')}
        transition['finalStatusReview']['normativeSnapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        p.V09_FINAL_STATUS_EVIDENCE_SHA = p.sha(p.encoded(transition['finalStatusReview']))
        self.checkpoint['readiness'].update(independentFinalStatusReview='PASS', finalStatusReviewReference=p.V09_FINAL_STATUS_REFERENCE, finalStatusEvidenceSHA256=p.V09_FINAL_STATUS_EVIDENCE_SHA)
        self.coherent_current_amendment()
        self.save('provenance.json', self.provenance)
        self.checkpoint['files'] = [{'path': 'docs/hongloumeng/translation/' + n, 'sha256': p.sha((self.directory/n).read_bytes()), 'bytes': (self.directory/n).stat().st_size} for n in (*p.NORMATIVE_FILES, 'provenance.json')]
        self.save('CHECKPOINT.json', self.checkpoint)
        for u in self.progress['units']:
            for r in u['reviews']: r['standardSnapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        for c in self.progress['checkpoints']:
            if c['state'] == 'accepted': c['standardSnapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT

    def coherent_current_amendment(self):
        # Only this test fixture manufactures SYNTHETIC evidence. Production
        # candidates require an independent receipt over exact candidate bytes.
        a = self.provenance[p.CURRENT_SOURCE_AMENDMENT_KEY]
        a.update(state='reviewed_binding_migration', previousNormativeSnapshot=p.V09_HISTORICAL_NORMATIVE_SNAPSHOT,
                 normativeSnapshot=p.EXPECTED_NORMATIVE_SNAPSHOT, reviewBindingsMigrated=True,
                 reference=p.CURRENT_SOURCE_DELTA_REFERENCE)
        p.V09_HISTORICAL_PROVENANCE_SHA = p.sha(p.encoded({k:v for k,v in self.provenance.items() if k != p.CURRENT_SOURCE_AMENDMENT_KEY}))
        a['previousProvenanceSHA256'] = p.V09_HISTORICAL_PROVENANCE_SHA
        earlier = [u for s,u in zip(self.mapping['units'],self.progress['units']) if s['chapter']<=35]
        p.CURRENT_ACCEPTED_BODIES_SHA=p.sha(p.encoded([{k:v for k,v in u.items() if k!='reviews'} for u in earlier]))
        a['acceptedBodiesSHA256']=p.CURRENT_ACCEPTED_BODIES_SHA
        reviews=[r for u in earlier for r in u['reviews']]
        p.CURRENT_REVIEW_CONTENT_SHA=p.sha(p.encoded([r['contentHash'] for r in reviews]))
        a['acceptedReviewContentHashesSHA256']=p.CURRENT_REVIEW_CONTENT_SHA
        suffix='; '+p.CURRENT_SOURCE_DELTA_REFERENCE
        p.CURRENT_OLD_REFERENCES_SHA=p.sha(p.encoded([r['reference'][:-len(suffix)] for r in reviews]))
        p.CURRENT_CHECKPOINT_CORPUS_HASHES=[c['corpusHash'] for c in self.progress['checkpoints'][:7]]
        a['checkpointCorpusHashes']=p.CURRENT_CHECKPOINT_CORPUS_HASHES
        e={'status':'PASS','reference':p.CURRENT_SOURCE_DELTA_REFERENCE,
           'previousNormativeSnapshot':p.V09_HISTORICAL_NORMATIVE_SNAPSHOT,
           'normativeSnapshot':p.EXPECTED_NORMATIVE_SNAPSHOT,'sourceHash':p.READING_SHA,
           'sourceMapHash':p.SOURCE_MAP_SHA,'traditionalHash':p.CURRENT_SOURCE_TRADITIONAL_SHA,
           'changedUnitIds':p.CURRENT_SOURCE_CHANGED_IDS,'acceptedBodiesUnchanged':True,
           'notFullCorpusReread':True,'reviewBindingsMigrationApproved':True,
           'reviewRequestSHA256':p.CURRENT_SOURCE_REVIEW_REQUEST_SHA,'scope':'SYNTHETIC ONLY'}
        a['evidence']=e;p.CURRENT_SOURCE_EVIDENCE_SHA=p.sha(p.encoded(e));a['evidenceSHA256']=p.CURRENT_SOURCE_EVIDENCE_SHA
        self.checkpoint['currentSourceAmendment']={k:a[k] for k in ('id','state','previousNormativeSnapshot','normativeSnapshot','sourceHash','sourceMapHash','traditionalHash','reference','evidenceSHA256','reviewBindingsMigrated')}

    def check(self):
        return p.validate_v09_readiness(self.mapping, self.progress)

    def rejected(self):
        with self.assertRaises(ValueError): self.check()

    def test_source_amendment_missing_or_forged(self):
        for field, value in [('state', 'pending'), ('reference', 'forged'), ('reviewBindingsMigrated', False), ('sourceHash', 'forged'), ('sourceMapHash', 'forged'), ('previousProvenanceSHA256', 'forged'), ('previousCheckpointSHA256', 'forged'), ('evidenceSHA256', 'forged')]:
            original = copy.deepcopy(self.provenance)
            self.provenance[p.SOURCE_AMENDMENT_KEY][field] = value
            self.coherent_metadata(); self.rejected(); self.provenance = original

    def test_source_amendment_previous_checkpoint_preserved(self):
        self.provenance[p.SOURCE_AMENDMENT_KEY]['previousCheckpoint']['scope'] = 'rewritten'
        self.coherent_metadata(); self.rejected()

    def test_source_amendment_requires_real_evidence(self):
        self.provenance[p.SOURCE_AMENDMENT_KEY]['evidence'] = None
        self.coherent_metadata(); self.rejected()

    def test_source_amendment_review_reference_required(self):
        r = self.progress['units'][0]['reviews'][0]
        r['reference'] = '; '.join(x for x in r['reference'].split('; ') if x != p.SOURCE_DELTA_REFERENCE)
        self.rejected()

    def test_source_amendment_seventh_checkpoint_reference_required(self):
        c = self.progress['checkpoints'][6]
        c['reviewReference'] = '; '.join(x for x in c['reviewReference'].split('; ') if x != p.SOURCE_DELTA_REFERENCE)
        self.rejected()

    def test_source_amendment_allows_later_target_lifecycle(self):
        for ident, kind in [('hlm-c038-b0060', 'verse'), ('hlm-c040-b0011', 'prose')]:
            u = next(u for u in self.progress['units'] if u['id'] == ident)
            u.update(state='draft', segments=[{'kind': kind, 'text': 'SYNTHETIC LATER TEXT.'}]); self.check()
            u['reviews'] = [{'type': typ, 'contentHash': p.content_hash(u), 'standardSnapshot': p.EXPECTED_NORMATIVE_SNAPSHOT, 'reference': 'SYNTHETIC LATER REVIEW ONLY'} for typ in p.REVIEW_TYPES]
            for state in ('reviewed', 'accepted'): u['state'] = state; self.check()

    def changed_target(self):
        u = next(u for u in self.progress['units'] if u['id'] == 'hlm-c040-b0011')
        u.update(state='draft', segments=[{'kind': 'prose', 'text': 'SYNTHETIC LATER TEXT.'}])
        return u

    def test_source_amendment_later_target_rejects_old_hash(self):
        self.changed_target()['sourceHash'] = '0'*64; self.rejected()

    def test_source_amendment_later_target_rejects_unreviewed_acceptance(self):
        self.changed_target()['state'] = 'accepted'; self.rejected()

    def test_source_amendment_later_target_rejects_stale_review(self):
        u = self.changed_target(); u['state'] = 'reviewed'
        u['reviews'] = [{'type': typ, 'contentHash': '0'*64, 'standardSnapshot': p.EXPECTED_NORMATIVE_SNAPSHOT, 'reference': 'SYNTHETIC ONLY'} for typ in p.REVIEW_TYPES]; self.rejected()

    def test_installed_configuration(self):
        self.assertEqual(self.check(), p.EXPECTED_NORMATIVE_SNAPSHOT)

    def test_seventh_batch_missing(self):
        (self.directory/'english-batch-031-035.json').unlink(); self.rejected()

    def test_eighth_batch_missing(self):
        (self.directory/'english-batch-036-040.json').unlink(); self.rejected()

    def test_semantic_bytes_changed(self):
        self.batch['policy'] += ' SYNTHETIC TAMPER'; self.save('english-batch-036-040.json', self.batch); self.rejected()

    def test_stale_snapshot(self):
        p.EXPECTED_NORMATIVE_SNAPSHOT = '0'*64; self.rejected()

    def test_pending_checkpoint(self):
        self.checkpoint['state'] = 'pending'; self.save('CHECKPOINT.json', self.checkpoint); self.rejected()

    def test_stale_checkpoint_snapshot(self):
        self.checkpoint['normative_snapshot'] = 'old'; self.save('CHECKPOINT.json', self.checkpoint); self.rejected()

    def test_missing_freeze_id(self):
        self.checkpoint['freeze_id'] = None; self.save('CHECKPOINT.json', self.checkpoint); self.rejected()

    def test_bad_inventory(self):
        original = copy.deepcopy(self.checkpoint)
        for edit in (lambda c:c['files'].pop(), lambda c:c['files'].append(c['files'][0]), lambda c:c['files'][0].update(sha256='0'*64), lambda c:c['files'][0].update(bytes=0)):
            self.checkpoint = copy.deepcopy(original); edit(self.checkpoint); self.save('CHECKPOINT.json', self.checkpoint); self.rejected()

    def test_batch_status_version_or_freeze(self):
        original = copy.deepcopy(self.batch)
        for key, value in [('status', 'pending'), ('version', 'old'), ('freeze_id', 'other')]:
            self.batch = copy.deepcopy(original); self.batch[key] = value; self.coherent_metadata(); self.rejected()

    def test_batch_scope(self):
        self.batch['chapters'] = list(range(31,36)); self.coherent_metadata(); self.rejected()

    def test_source_binding(self):
        original = copy.deepcopy(self.batch)
        for key in ('observedSHA256','boundSHA256','observedSourceMapSHA256','expectedUnitCount','traditionalSHA256'):
            self.batch = copy.deepcopy(original); self.batch['sourceBinding'][key] = 'wrong'; self.coherent_metadata(); self.rejected()

    def test_source_unit_layout(self):
        self.batch['source_units'][0]['layout']['kind'] = 'prose'; self.coherent_metadata(); self.rejected()

    def test_source_unit_pointer(self):
        self.batch['source_units'][0]['sourceTextJSONPointer'] = '/chapters/0/title'; self.coherent_metadata(); self.rejected()

    def test_portable_source_decisions(self):
        original = copy.deepcopy(self.batch)
        for edit in (lambda b:b['sourceReadingDecisions'].pop(), lambda b:b['sourceReadingDecisions'][0].update(adoptedUnit='wrong'), lambda b:b['sourceReadingDecisions'][0].update(traditionalAdoptedUnit='wrong'), lambda b:b['sourceReadingDecisions'][0].update(publicEvidence=[]), lambda b:b['sourceReadingDecisions'][0].update(evidenceLimit='')):
            self.batch = copy.deepcopy(original); edit(self.batch); self.coherent_metadata(); self.rejected()

    def test_readiness_flags(self):
        original = copy.deepcopy(self.checkpoint)
        for key in self.checkpoint['readiness']:
            self.checkpoint = copy.deepcopy(original); self.checkpoint['readiness'][key] = None; self.save('CHECKPOINT.json', self.checkpoint); self.rejected()

    def test_fabricated_references(self):
        self.checkpoint['readiness']['normativeDeltaReviewReferences'] = ['FABRICATED']; self.save('CHECKPOINT.json', self.checkpoint); self.rejected()

    def test_historical_provenance_mutation(self):
        self.provenance['normative_projection_v07']['state'] = 'rewritten'; self.coherent_metadata(); self.rejected()

    def test_historical_checkpoint_mutation(self):
        self.provenance['normative_projection_v09']['previousCheckpoint']['scope'] = 'rewritten'; self.coherent_metadata(); self.rejected()

    def test_historical_clarification_rewritten(self):
        self.provenance['normative_projection_v09']['previousCheckpoint']['normativeAmendment']['reference'] = 'rewritten'; self.coherent_metadata(); self.rejected()

    def test_transition_missing_or_forged(self):
        self.provenance['normative_projection_v08']['references'] = ['FABRICATED']; self.coherent_metadata(); self.rejected()

    def test_provenance_source_or_flags(self):
        original = copy.deepcopy(self.provenance)
        for key in ('sourceHash','sourceMapHash','reviewBindingsMigrated','version','state','publicationEnabled','independentEditorialReview','independentSemanticDeltaReview','independentTechnicalReview'):
            self.provenance = copy.deepcopy(original); self.provenance['normative_projection_v09'][key] = None; self.coherent_metadata(); self.rejected()

    def test_missing_review_reference(self):
        self.progress['units'][0]['reviews'][0]['reference'] = 'OLD-ONLY'; self.rejected()

    def test_prior_batch_acceptance_removed(self):
        self.progress['units'][0]['state'] = 'reviewed'; self.rejected()

    def test_prior_checkpoint_acceptance_removed(self):
        self.progress['checkpoints'][5].update(state='pending',corpusHash=None,standardSnapshot=None,reviewReference=None); self.rejected()

    def test_checkpoint_reference_removed(self):
        self.progress['checkpoints'][5]['reviewReference'] = 'OLD-ONLY'; self.rejected()

    def test_accepted_prose_mutation(self):
        self.progress['units'][0]['segments'][0]['text'] += ' CHANGED'; self.rejected()

    def test_pending_units_unchanged(self):
        self.assertTrue(all(u['state']=='pending' and not u['segments'] and not u['reviews'] for s,u in zip(self.mapping['units'],self.progress['units']) if s['chapter']>35))
        self.assertEqual(p.validate_reader_notes(self.mapping,json.loads((p.DATA/'reader-notes.json').read_bytes())),43)

    def test_current_batch_may_progress(self):
        self.changed_target(); self.check()

    def test_outside_batch_nonpending_rejected(self):
        u=next(u for s,u in zip(self.mapping['units'],self.progress['units']) if s['chapter']==41)
        u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE.'}]); self.rejected()

    def test_outside_batch_content_rejected(self):
        u=next(u for s,u in zip(self.mapping['units'],self.progress['units']) if s['chapter']==41)
        u['segments']=[{'kind':'title','text':'SYNTHETIC FALSE PENDING.'}]; self.rejected()

    def test_outside_batch_review_rejected(self):
        u=next(u for s,u in zip(self.mapping['units'],self.progress['units']) if s['chapter']==41)
        u['reviews']=[{'reference':'SYNTHETIC FALSE PENDING'}]; self.rejected()

    def test_current_evidence_missing_or_forged(self):
        p.V09_SEMANTIC_EVIDENCE_SHA=None; self.rejected()

    def test_current_evidence_scope(self):
        original=copy.deepcopy(self.provenance)
        for key in ('status','references','previousNormativeSnapshot','sourceHash','sourceMapHash','acceptedBodiesUnchanged','notFullCorpusReread','reviewedEarlierUnitIds'):
            self.provenance=copy.deepcopy(original);self.provenance['normative_projection_v09']['semanticDeltaReview'][key]=None;self.coherent_metadata();self.rejected()


    def test_final_status_evidence_missing(self):
        self.provenance['normative_projection_v09'].pop('finalStatusReview')
        self.save('provenance.json', self.provenance)
        for row in self.checkpoint['files']:
            if row['path'].endswith('/provenance.json'):
                raw=(self.directory/'provenance.json').read_bytes();row.update(sha256=p.sha(raw),bytes=len(raw))
        self.save('CHECKPOINT.json',self.checkpoint)
        with self.assertRaisesRegex(ValueError,'Final-status'):self.check()

    def test_final_status_evidence_hash_unbound(self):
        p.V09_FINAL_STATUS_EVIDENCE_SHA=None
        with self.assertRaisesRegex(ValueError,'Final-status'):self.check()

    def test_final_status_reference_required_on_old_reviews(self):
        r=self.progress['units'][0]['reviews'][0]
        r['reference']='; '.join(x for x in r['reference'].split('; ') if x!=p.V09_FINAL_STATUS_REFERENCE)
        with self.assertRaisesRegex(ValueError,'final-status reference'):self.check()

    def test_final_status_reference_required_on_old_checkpoint(self):
        c=self.progress['checkpoints'][6]
        c['reviewReference']='; '.join(x for x in c['reviewReference'].split('; ') if x!=p.V09_FINAL_STATUS_REFERENCE)
        with self.assertRaisesRegex(ValueError,'final-status reference'):self.check()

    def save_current_evidence_change(self):
        self.save('provenance.json', self.provenance)
        for row in self.checkpoint['files']:
            if row['path'].endswith('/provenance.json'):
                raw = (self.directory / 'provenance.json').read_bytes()
                row.update(sha256=p.sha(raw), bytes=len(raw))
        self.save('CHECKPOINT.json', self.checkpoint)

    def test_current_source_evidence_is_required(self):
        p.CURRENT_SOURCE_EVIDENCE_SHA = None
        with self.assertRaisesRegex(ValueError, 'Awaiting authenticated current source'): self.check()

    def test_current_source_reference_is_required(self):
        p.CURRENT_SOURCE_DELTA_REFERENCE = None
        with self.assertRaisesRegex(ValueError, 'Awaiting authenticated current source'): self.check()

    def test_current_source_evidence_hash_cannot_be_relabelled(self):
        self.provenance[p.CURRENT_SOURCE_AMENDMENT_KEY]['evidence']['scope'] = 'FORGED'
        self.save_current_evidence_change()
        with self.assertRaisesRegex(ValueError, 'Current source evidence missing or forged'): self.check()

    def test_current_source_scope_fields_must_match(self):
        original = copy.deepcopy(self.provenance)
        for key in ('status', 'reference', 'previousNormativeSnapshot', 'normativeSnapshot', 'sourceHash', 'sourceMapHash', 'traditionalHash', 'changedUnitIds', 'acceptedBodiesUnchanged', 'notFullCorpusReread', 'reviewBindingsMigrationApproved', 'reviewRequestSHA256'):
            self.provenance = copy.deepcopy(original)
            a = self.provenance[p.CURRENT_SOURCE_AMENDMENT_KEY]
            a['evidence'][key] = None
            p.CURRENT_SOURCE_EVIDENCE_SHA = p.sha(p.encoded(a['evidence']))
            a['evidenceSHA256'] = p.CURRENT_SOURCE_EVIDENCE_SHA
            self.checkpoint['currentSourceAmendment']['evidenceSHA256'] = p.CURRENT_SOURCE_EVIDENCE_SHA
            self.save_current_evidence_change()
            with self.assertRaisesRegex(ValueError, 'Current source evidence scope differs'): self.check()

    def test_current_source_amendment_missing(self):
        self.provenance.pop(p.CURRENT_SOURCE_AMENDMENT_KEY)
        self.save_current_evidence_change()
        with self.assertRaisesRegex(ValueError, 'Current source amendment missing'): self.check()

    def test_current_source_historical_v09_extra_field_rejected(self):
        self.provenance['normative_projection_v09']['inventedRetrospectiveClaim'] = 'not historical'
        self.save_current_evidence_change()
        with self.assertRaisesRegex(ValueError, 'Historical v0.9 provenance changed'): self.check()

    def test_current_source_historical_checkpoint_exact(self):
        self.provenance[p.CURRENT_SOURCE_AMENDMENT_KEY]['previousCheckpoint']['scope'] += ' ALTERED'
        self.save_current_evidence_change()
        with self.assertRaisesRegex(ValueError, 'Historical v0.9 checkpoint changed'): self.check()

    def test_current_source_historical_binding_exact(self):
        self.batch['sourceBindingHistory'][0]['observedSHA256'] = 'FORGED'
        self.coherent_metadata()
        with self.assertRaisesRegex(ValueError, 'Historical source binding changed'): self.check()

    def test_current_source_cannot_claim_future_installation_commit(self):
        self.batch['sourceBinding']['sourceCommit'] = 'f' * 40
        self.coherent_metadata()
        with self.assertRaisesRegex(ValueError, 'must not invent an installation commit'): self.check()

    def test_current_source_author_override_must_be_distinct(self):
        self.batch['sourceReadingDecisions'][2]['kind'] = 'historical_repair'
        self.coherent_metadata()
        with self.assertRaisesRegex(ValueError, 'Explicit author override missing'): self.check()

    def test_current_source_checkpoint_amendment_must_match(self):
        self.checkpoint['currentSourceAmendment']['normativeSnapshot'] = 'old'
        self.save('CHECKPOINT.json', self.checkpoint)
        with self.assertRaisesRegex(ValueError, 'Current checkpoint amendment differs'): self.check()

    def test_current_source_old_reference_prefix_is_preserved(self):
        r = self.progress['units'][0]['reviews'][0]
        r['reference'] = 'REWRITTEN PREFIX; ' + r['reference']
        with self.assertRaisesRegex(ValueError, 'Original review reference prefixes changed'): self.check()

    def test_current_source_accepted_body_cannot_be_rehashed(self):
        u = self.progress['units'][0]
        u['segments'][0]['text'] += ' REWRITTEN'
        for r in u['reviews']: r['contentHash'] = p.content_hash(u)
        with self.assertRaisesRegex(ValueError, 'Earlier accepted English bodies changed'): self.check()

    def test_current_source_review_append_required(self):
        r = self.progress['units'][0]['reviews'][0]
        r['reference'] = r['reference'].removesuffix('; ' + p.CURRENT_SOURCE_DELTA_REFERENCE)
        with self.assertRaisesRegex(ValueError, 'Accepted review missing current source reference'): self.check()

    def test_current_source_checkpoint_append_required(self):
        c = self.progress['checkpoints'][0]
        c['reviewReference'] = c['reviewReference'].removesuffix('; ' + p.CURRENT_SOURCE_DELTA_REFERENCE)
        with self.assertRaisesRegex(ValueError, 'Checkpoint missing current source reference'): self.check()

    def letter_trial(self):
        source=next(s for s in self.mapping['units'] if s['id']=='hlm-c037-b0003')
        unit=next(u for u in self.progress['units'] if u['id']==source['id'])
        unit.update(state='draft',segments=[{'kind':'letter','text':'SYNTHETIC letter paragraph one.'},{'kind':'letter','text':'SYNTHETIC letter paragraph two.'},{'kind':'letter','text':'SYNTHETIC letter paragraph three.'}])
        return unit

    def test_letter_multiple_paragraphs_preserve_one_source_unit(self):
        unit=self.letter_trial();self.check()
        self.assertEqual(len(unit['segments']),3)
        self.assertEqual(sum(u['id']=='hlm-c037-b0003' for u in self.progress['units']),1)

    def test_letter_mixed_kind_rejected(self):
        unit=self.letter_trial();unit['segments'][1]['kind']='prose'
        with self.assertRaisesRegex(ValueError,'kind lost'):self.check()

    def test_letter_empty_paragraph_rejected(self):
        unit=self.letter_trial();unit['segments'][1]['text']=' '
        with self.assertRaisesRegex(ValueError,'Empty translated segment'):self.check()

    def test_letter_stale_source_hash_rejected(self):
        unit=self.letter_trial();unit['sourceHash']='0'*64
        with self.assertRaisesRegex(ValueError,'stale'):self.check()

    def test_other_nonprose_multiple_segments_still_rejected(self):
        original=copy.deepcopy(self.progress)
        for kind in ('title','verse','couplet','diagram'):
            self.progress=copy.deepcopy(original)
            i=next(i for i,s in enumerate(self.mapping['units']) if s['layout']['kind']==kind)
            u=self.progress['units'][i];u.update(state='draft',reviews=[],segments=[{'kind':kind,'text':'SYNTHETIC one.'},{'kind':kind,'text':'SYNTHETIC two.'}])
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError,'one mapped unit'):p.validate_progress(self.mapping,self.progress,p.EXPECTED_NORMATIVE_SNAPSHOT)


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


class FelicityRevisionTests(unittest.TestCase):
    """Actual full readiness chain. No historical/naming guard is mocked here."""
    @classmethod
    def setUpClass(cls):
        cls.mapping = p.source_map(p.load_source())
        cls.original_progress = json.loads((p.DATA / p.V010_BEFORE_FILENAME).read_bytes())
        cls.original_archive = (p.DATA / p.FELICITY_BEFORE_FILENAME).read_bytes()
        cls.original_notes = (p.DATA / 'reader-notes.json').read_bytes()
        cls.norm_files = {n: (p.STANDARD / n).read_bytes() for n in (*p.NORMATIVE_FILES, 'provenance.json', 'CHECKPOINT.json')}

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.standard = self.directory / 'standard'; self.standard.mkdir()
        self.data = self.directory / 'data'; self.data.mkdir()
        for n, b in self.norm_files.items(): (self.standard / n).write_bytes(b)
        (self.data / p.FELICITY_BEFORE_FILENAME).write_bytes(self.original_archive)
        (self.data / 'reader-notes.json').write_bytes(self.original_notes)
        self.progress = copy.deepcopy(self.original_progress)
        self.provenance = json.loads(self.norm_files['provenance.json'])
        self.checkpoint = json.loads(self.norm_files['CHECKPOINT.json'])['previousCheckpoint']
        self.provenance.pop('normative_projection_v010')
        self.patches = [patch.object(p, 'EXPECTED_NORMATIVE_SNAPSHOT', p.V010_PREVIOUS_SNAPSHOT), patch.object(p, 'STANDARD', self.standard), patch.object(p, 'DATA', self.data)]
        for item in self.patches: item.start()

    def tearDown(self):
        for item in reversed(self.patches): item.stop()
        self.temp.cleanup()

    def save_metadata(self):
        (self.standard / 'provenance.json').write_text(json.dumps(self.provenance, ensure_ascii=False))
        for row in self.checkpoint['files']:
            f = self.standard / Path(row['path']).name
            row.update(sha256=p.sha(f.read_bytes()), bytes=f.stat().st_size)
        (self.standard / 'CHECKPOINT.json').write_text(json.dumps(self.checkpoint, ensure_ascii=False))

    def check(self):
        return p.validate_v09_readiness(self.mapping, self.progress, snapshot=p.V010_PREVIOUS_SNAPSHOT,
                                        checkpoint=self.checkpoint, document=self.provenance)

    def test_actual_full_chain_and_historical_inventory(self):
        self.assertEqual(self.check(), p.EXPECTED_NORMATIVE_SNAPSHOT)
        before = json.loads(self.original_archive)
        old = [u for u in before['units'] if u['state'] == 'accepted']
        historical_ids = {u['id'] for u in old}
        now = [u for u in self.progress['units'] if u['id'] in historical_ids]
        self.assertEqual(len(old), 1885); self.assertEqual(len(now), 1885)
        self.assertEqual(sum(len(u['reviews']) for u in now), 5655)
        self.assertEqual(sum(u['segments'] != v['segments'] for u,v in zip(old, now)), 8)
        self.assertEqual(sum(c['state'] == 'accepted' for c in self.progress['checkpoints'][:7]), 7)

    def test_archive_bytes_tamper_rejected(self):
        f = self.data / p.FELICITY_BEFORE_FILENAME; f.write_bytes(self.original_archive + b' ')
        with self.assertRaisesRegex(ValueError, 'Felicity historical progress changed'): self.check()

    def test_archive_path_or_missing_rejected(self):
        self.provenance[p.FELICITY_AMENDMENT_KEY]['previousProgressPath'] = '../elsewhere'
        self.save_metadata()
        with self.assertRaisesRegex(ValueError, 'historical progress path differs'): self.check()

    def test_old_provenance_and_checkpoint_not_rewritten(self):
        self.provenance[p.FELICITY_AMENDMENT_KEY]['previousCheckpoint']['scope'] = 'tampered'
        self.save_metadata()
        with self.assertRaisesRegex(ValueError, 'predecessor checkpoint changed'): self.check()

    def test_norm_evidence_cannot_be_forged(self):
        self.provenance[p.FELICITY_AMENDMENT_KEY]['normativeMigrationReview']['reference'] = 'SYNTHETIC FORGERY'
        self.save_metadata()
        with self.assertRaisesRegex(ValueError, 'normative migration evidence missing or forged'): self.check()

    def test_naming_binding_cannot_be_removed(self):
        del self.checkpoint['currentNamingRevision']; self.save_metadata()
        with self.assertRaisesRegex(ValueError, 'Felicity checkpoint binding differs'): self.check()

    def test_exact_changed_content_required(self):
        u = next(u for u in self.progress['units'] if u['id'] in p.FELICITY_CHANGED_IDS)
        u['segments'][0]['text'] += ' SYNTHETIC TAMPER'
        for r in u['reviews']: r['contentHash'] = p.content_hash(u, self.progress['sourceIssues'])
        with self.assertRaisesRegex(ValueError, 'Felicity reviewed content differs'): self.check()

    def test_old_24_reviews_cannot_be_rebound_as_new(self):
        before = json.loads(self.original_archive)
        u = next(u for u in self.progress['units'] if u['id'] in p.FELICITY_CHANGED_IDS)
        u['reviews'] = copy.deepcopy(next(v for v in before['units'] if v['id'] == u['id'])['reviews'])
        for r in u['reviews']:
            r['contentHash'] = p.content_hash(u, self.progress['sourceIssues']); r['standardSnapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        with self.assertRaisesRegex(ValueError, 'Felicity current review lineage'): self.check()

    def test_other_1877_bodies_cannot_be_rehashed(self):
        u = self.progress['units'][0]; u['segments'][0]['text'] += ' SYNTHETIC TAMPER'
        for r in u['reviews']: r['contentHash'] = p.content_hash(u, self.progress['sourceIssues'])
        with self.assertRaisesRegex(ValueError, 'Earlier accepted English bodies changed'): self.check()

    def test_5631_review_references_are_append_only(self):
        self.progress['units'][0]['reviews'][0]['reference'] = p.FELICITY_MIGRATION_REFERENCE
        with self.assertRaisesRegex(ValueError, 'Felicity current review lineage'): self.check()

    def test_limited_checkpoint_review_and_five_corpora_required(self):
        for i in (0,1,2,3,4,5,6):
            with self.subTest(index=i):
                saved = copy.deepcopy(self.progress['checkpoints'][i])
                self.progress['checkpoints'][i]['corpusHash'] = '0'*64
                with self.assertRaisesRegex(ValueError, 'Felicity current checkpoint lineage'): self.check()
                self.progress['checkpoints'][i] = saved

    def test_historical_six_name_objects_unchanged(self):
        for row in p.FELICITY_HISTORICAL_LOCATORS:
            f = self.standard / row['file']; original = f.read_bytes()
            f.write_bytes(original.replace(b'Feng-er', b'Unapproved-Name'))
            with self.assertRaisesRegex(ValueError, 'Historical Feng-er norm object changed'):
                p.validate_felicity_revision(self.provenance, self.checkpoint, self.mapping, self.progress, json.loads(self.original_archive), p.EXPECTED_NORMATIVE_SNAPSHOT)
            f.write_bytes(original)

    def test_b8_and_b9_future_acceptance_not_capped(self):
        # Synthetic test-only bodies/reviews, never canonical acceptance evidence.
        for first,last in ((36,40),(41,45)):
            for s,u in zip(self.mapping['units'], self.progress['units']):
                if first <= s['chapter'] <= last:
                    u.update(state='accepted', segments=[{'kind':s['layout']['kind'], 'text':'SYNTHETIC FUTURE TEST ONLY.'}])
                    u['reviews'] = [{'type':t, 'contentHash':p.content_hash(u,self.progress['sourceIssues']), 'standardSnapshot':p.EXPECTED_NORMATIVE_SNAPSHOT, 'reference':'SYNTHETIC FUTURE TEST ONLY'} for t in p.REVIEW_TYPES]
            c = self.progress['checkpoints'][(first-1)//5]
            units = [u for s,u in zip(self.mapping['units'],self.progress['units']) if first<=s['chapter']<=last]
            c.update(state='accepted', corpusHash=p.batch_hash(units,self.progress['sourceIssues']), standardSnapshot=p.EXPECTED_NORMATIVE_SNAPSHOT, reviewReference='SYNTHETIC FUTURE TEST ONLY')
            self.assertEqual(self.check(), p.EXPECTED_NORMATIVE_SNAPSHOT)
        s,u = next((s,u) for s,u in zip(self.mapping['units'],self.progress['units']) if s['chapter']==46)
        u.update(state='draft',segments=[{'kind':s['layout']['kind'],'text':'SYNTHETIC FUTURE TEST ONLY.'}])
        self.check()
        self.progress['checkpoints'][8].update(state='pending', corpusHash=None, standardSnapshot=None, reviewReference=None)
        with self.assertRaisesRegex(ValueError, 'Finish preceding five-chapter quality review before expanding'): self.check()


class CurrentV010Tests(unittest.TestCase):
    """Actual current fixture and complete historical chain, with no guard mocks."""
    @classmethod
    def setUpClass(cls):
        cls.mapping = p.source_map(p.load_source())
        cls.original_progress = json.loads((p.DATA / 'progress.json').read_bytes())
        cls.norm_files = {n: (p.STANDARD / n).read_bytes() for n in (*p.NORMATIVE_FILES, 'provenance.json', 'CHECKPOINT.json')}
        cls.archives = {n: (p.DATA / n).read_bytes() for n in (p.V010_BEFORE_FILENAME, p.FELICITY_BEFORE_FILENAME)}

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.standard = self.directory / 'standard'; self.standard.mkdir()
        self.data = self.directory / 'data'; self.data.mkdir()
        for name, raw in self.norm_files.items(): (self.standard / name).write_bytes(raw)
        for name, raw in self.archives.items(): (self.data / name).write_bytes(raw)
        self.progress = copy.deepcopy(self.original_progress)
        self.document = json.loads(self.norm_files['provenance.json'])
        self.checkpoint = json.loads(self.norm_files['CHECKPOINT.json'])
        self.patches = [patch.object(p, 'STANDARD', self.standard), patch.object(p, 'DATA', self.data)]
        for item in self.patches: item.start()

    def tearDown(self):
        for item in reversed(self.patches): item.stop()
        self.temp.cleanup()

    def check(self):
        return p.validate_standard_readiness(self.mapping, self.progress)

    def save_metadata(self):
        (self.standard / 'provenance.json').write_text(json.dumps(self.document, ensure_ascii=False))
        for row in self.checkpoint['files']:
            raw = (self.standard / Path(row['path']).name).read_bytes()
            row.update(sha256=p.sha(raw), bytes=len(raw))
        (self.standard / 'CHECKPOINT.json').write_text(json.dumps(self.checkpoint, ensure_ascii=False))

    def reject(self, message):
        with self.assertRaisesRegex(ValueError, message): self.check()

    def b9(self):
        return [u for s,u in zip(self.mapping['units'],self.progress['units']) if 41 <= s['chapter'] <= 45]

    def pending_ninth_checkpoint(self):
        self.progress['checkpoints'][8].update(state='pending', corpusHash=None, standardSnapshot=None, reviewReference=None)

    def draft46(self):
        unit = next(u for s,u in zip(self.mapping['units'],self.progress['units']) if s['chapter'] == 46)
        unit.update(state='draft', segments=[{'kind':'title', 'text':'SYNTHETIC FUTURE GATE TEST ONLY.'}])
        return unit

    def test_actual_v010_full_chain_counts(self):
        self.assertEqual(self.check(), p.EXPECTED_NORMATIVE_SNAPSHOT)
        self.assertEqual(p.validate_progress(self.mapping,self.progress,p.EXPECTED_NORMATIVE_SNAPSHOT), {'accepted':2461,'pending':2014})
        self.assertEqual(sum(len(u['reviews']) for u in self.progress['units']),7383)
        self.assertEqual(sum(c['state']=='accepted' for c in self.progress['checkpoints']),9)

    def test_ninth_norm_is_bound(self):
        self.assertIn('english-batch-041-045.json',p.NORMATIVE_FILES)
        f=self.standard/'english-batch-041-045.json'; f.write_bytes(f.read_bytes()+b' ')
        self.reject('Unexpected normative snapshot')

    def test_actual_before_raw_bytes_required(self):
        f=self.data/p.V010_BEFORE_FILENAME; f.write_bytes(f.read_bytes()+b' ')
        self.reject('v0.10 historical progress changed')

    def test_actual_before_path_required(self):
        self.document['normative_projection_v010']['previousProgressPath']='../other'
        self.save_metadata(); self.reject('v0.10 historical progress path differs')

    def test_embedded_old_checkpoint_not_current_checkpoint(self):
        self.document['normative_projection_v010']['previousCheckpoint']['version']=p.VERSION
        self.save_metadata(); self.reject('v0.10 predecessor checkpoint changed')

    def test_historical_provenance_not_relabelled(self):
        self.document['normative_projection_v09']['version']=p.VERSION
        self.save_metadata(); self.reject('v0.10 predecessor provenance changed')

    def test_felicity_before_guard_still_runs(self):
        f=self.data/p.FELICITY_BEFORE_FILENAME; f.write_bytes(f.read_bytes()+b' ')
        self.reject('Felicity historical progress changed')

    def test_three_genuine_scoped_receipts_required(self):
        original=copy.deepcopy(self.document)
        for name in p.V010_EVIDENCE_HASHES:
            with self.subTest(name=name):
                self.document=copy.deepcopy(original)
                self.document['normative_projection_v010'][name]['status']='PASS'
                self.save_metadata(); self.reject('scoped review evidence missing or forged')

    def test_not_full_reread_claim_cannot_be_removed(self):
        self.document['normative_projection_v010']['priorNormMigrationReview']['notFullCorpusReread']=False
        self.save_metadata(); self.reject('scoped review evidence missing or forged')

    def test_current_checkpoint_inventory_required(self):
        self.checkpoint['files'][0]['bytes']+=1
        (self.standard/'CHECKPOINT.json').write_text(json.dumps(self.checkpoint))
        self.reject('Partial or stale normative file inventory')

    def test_current_checkpoint_proof_binding_required(self):
        self.checkpoint['normativeTransitionV010']['previousProgressSHA256']='0'*64
        self.save_metadata(); self.reject('v0.10 checkpoint transition differs')

    def test_current_readiness_cannot_claim_technical_pass(self):
        self.checkpoint['readiness']['independentTechnicalReview']='PASS'
        self.save_metadata(); self.reject('Incomplete v0.10 readiness')

    def test_old_review_prefix_and_type_and_hash_unchanged(self):
        original=copy.deepcopy(self.progress)
        for key,value in [('reference',p.V010_MIGRATION_REFERENCE),('type','literary'),('contentHash','0'*64)]:
            with self.subTest(key=key):
                self.progress=copy.deepcopy(original)
                self.progress['units'][0]['reviews'][0][key]=value
                self.reject('v0.10 prior body or review lineage changed')

    def test_old_body_rehash_does_not_authorize_change(self):
        u=self.progress['units'][0];u['segments'][0]['text']+=' SYNTHETIC TAMPER'
        for r in u['reviews']: r['contentHash']=p.content_hash(u,self.progress['sourceIssues'])
        self.reject('v0.10 prior body or review lineage changed')

    def test_old_checkpoint_corpus_and_reference_unchanged(self):
        self.progress['checkpoints'][7]['reviewReference']=p.V010_MIGRATION_REFERENCE
        self.reject('v0.10 prior checkpoint lineage changed')

    def test_old_source_issues_unchanged(self):
        self.progress['sourceIssues'][0]['description']+=' SYNTHETIC TAMPER'
        self.reject('v0.10 source issues changed')

    def test_b9_content_rehash_does_not_authorize_change(self):
        u=self.b9()[0];u['segments'][0]['text']+=' SYNTHETIC TAMPER'
        for r in u['reviews']:r['contentHash']=p.content_hash(u,self.progress['sourceIssues'])
        self.reject('v0.10 current pipeline corpus differs')

    def test_b9_review_preserves_historical_complete_reading_reference(self):
        self.b9()[0]['reviews'][0]['reference']=p.V010_CURRENT_REFERENCE
        self.reject('v0.10 current review lineage differs')

    def test_b9_checkpoint_reference_required(self):
        self.progress['checkpoints'][8]['reviewReference']=p.V010_CURRENT_REFERENCE
        self.reject('v0.10 ninth checkpoint review lineage differs')

    def test_custom_and_historical_hashes_not_pipeline_hashes(self):
        for digest in ('a7157710618ebcdb8398fef58516dadfd2fdc7f7102aebb96d304395d4c66de9','c6ec2039c8bc90cc9d813c4d5fc27e28faef95169425eb3c86a50c53281e330b'):
            with self.subTest(digest=digest):
                self.progress['checkpoints'][8]['corpusHash']=digest
                self.reject('Batch review is stale')

    def test_norm_migration_does_not_require_new_acceptance(self):
        for u in self.b9():u.update(state='draft',reviews=[])
        self.pending_ninth_checkpoint()
        self.assertEqual(self.check(),p.EXPECTED_NORMATIVE_SNAPSHOT)

    def test_reviewed_b9_does_not_require_acceptance(self):
        for u in self.b9():u['state']='reviewed'
        self.pending_ninth_checkpoint();self.check()

    def test_46_gate_accepted_ninth_allows_real_validator(self):
        self.draft46();self.assertEqual(self.check(),p.EXPECTED_NORMATIVE_SNAPSHOT)

    def test_46_gate_pending_ninth_rejects_real_validator(self):
        self.pending_ninth_checkpoint();self.draft46()
        self.reject('Finish preceding five-chapter quality review before expanding')

    def test_future_tenth_acceptance_not_fixed_to_2461(self):
        for source,u in zip(self.mapping['units'],self.progress['units']):
            if 46 <= source['chapter'] <= 50:
                u.update(state='accepted',segments=[{'kind':source['layout']['kind'],'text':'SYNTHETIC FUTURE TEST ONLY.'}])
                u['reviews']=[{'type':t,'contentHash':p.content_hash(u,self.progress['sourceIssues']),'standardSnapshot':p.EXPECTED_NORMATIVE_SNAPSHOT,'reference':'SYNTHETIC FUTURE TEST ONLY'} for t in p.REVIEW_TYPES]
        units=[u for source,u in zip(self.mapping['units'],self.progress['units']) if 46<=source['chapter']<=50]
        self.progress['checkpoints'][9].update(state='accepted',corpusHash=p.batch_hash(units,self.progress['sourceIssues']),standardSnapshot=p.EXPECTED_NORMATIVE_SNAPSHOT,reviewReference='SYNTHETIC FUTURE TEST ONLY')
        self.check()


if __name__ == '__main__':
    unittest.main()
