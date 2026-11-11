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
        self.assertEqual(sum(u['characterCount'] for u in blocks), 586222)
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md'):
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md'):
                (directory / name).write_text('synthetic baseline')
            with patch.object(p, 'STANDARD', directory):
                with self.assertRaisesRegex(ValueError, 'Standard baseline'):
                    p.standard_snapshot()

    def test_every_normative_file_changes_snapshot(self):
        names = ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-016-020.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md')
        self.assertEqual(len(names), 12)
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
            for name in ('english-standard.md', 'english-terms.json', 'english-voices.json', 'english-batch-001-005.json', 'english-batch-006-010.json', 'english-batch-011-015.json', 'english-batch-021-025.json', 'english-batch-026-030.json', 'english-batch-031-035.json', 'english-batch-036-040.json', 'CHANGELOG.md'):
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
        self.assertEqual(p.validate_standard_readiness(mapping, progress), p.EXPECTED_NORMATIVE_SNAPSHOT)
        self.assertEqual(sum(u['state'] == 'accepted' for u in progress['units']), 1885)
        self.assertEqual(sum(u['state'] == 'pending' for u in progress['units']), 2590)

    def test_eighth_batch_is_normative(self):
        self.assertIn('english-batch-036-040.json', p.NORMATIVE_FILES)
        self.assertEqual(p.standard_snapshot(), p.EXPECTED_NORMATIVE_SNAPSHOT)


class FreezeReadinessV09Tests(unittest.TestCase):
    """Synthetic current configuration, with untouched real historical metadata.

    The original v0.8 purposes are retained, not bypassed. All newly accepted
    English and current review evidence below are explicitly synthetic.
    """
    def setUp(self):
        self.mapping = p.source_map(p.load_source())
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        for name in (*p.NORMATIVE_FILES, 'provenance.json', 'CHECKPOINT.json'):
            (self.directory / name).write_bytes((p.STANDARD / name).read_bytes())
        self.patches = [patch.object(p, 'STANDARD', self.directory),
                        patch.object(p, 'EXPECTED_NORMATIVE_SNAPSHOT', p.EXPECTED_NORMATIVE_SNAPSHOT),
                        patch.object(p, 'V09_SEMANTIC_EVIDENCE_SHA', None),
                        patch.object(p, 'V09_DELTA_REFERENCES', ('SYNTHETIC-V09-DELTA-NOT-REAL',)),
                        patch.object(p, 'V09_FINAL_STATUS_REFERENCE', 'SYNTHETIC-FINAL-STATUS-NOT-REAL'),
                        patch.object(p, 'V09_FINAL_STATUS_EVIDENCE_SHA', p.V09_FINAL_STATUS_EVIDENCE_SHA)]
        for item in self.patches: item.start()
        self.batch = json.loads((self.directory / 'english-batch-036-040.json').read_bytes())
        self.checkpoint = json.loads((self.directory / 'CHECKPOINT.json').read_bytes())
        self.provenance = json.loads((self.directory / 'provenance.json').read_bytes())
        self.batch.update(status='frozen_editorial_checkpoint', freeze_id='SYNTHETIC-ONLY')
        self.batch['gate'] = {'formalFreeze': True, 'independentEditorialReview': True, 'sourceMigrationComplete': True, 'englishAcceptance': False, 'publicationEnabled': False}
        self.checkpoint.update(state='frozen_editorial_checkpoint', freeze_id='SYNTHETIC-ONLY')
        self.checkpoint['readiness'] = {'sourceInstalled': True, 'independentEditorialReview': 'PASS', 'independentSemanticDeltaReview': 'PASS', 'independentTechnicalReview': 'required_by_installation_contract', 'reviewBindingsCurrent': True, 'publicationEnabled': False, 'normativeDeltaReviewReferences': list(p.V09_DELTA_REFERENCES)}
        t = self.provenance['normative_projection_v09']
        t.update(state='frozen_editorial_checkpoint', reviewBindingsMigrated=True, independentEditorialReview='PASS', independentSemanticDeltaReview='PASS', independentTechnicalReview='required_by_installation_contract')
        t['finalStatusReview'] = {'status': 'PASS', 'reference': p.V09_FINAL_STATUS_REFERENCE, 'normativeSnapshot': None, 'scope': 'SYNTHETIC FINAL STATUS TEST ONLY'}
        t['semanticDeltaReview'] = {'status': 'PASS', 'references': list(p.V09_DELTA_REFERENCES), 'previousNormativeSnapshot': p.V09_PREVIOUS_NORMATIVE_SNAPSHOT, 'normativeSnapshot': None, 'sourceHash': p.READING_SHA, 'sourceMapHash': p.SOURCE_MAP_SHA, 'acceptedBodiesUnchanged': True, 'notFullCorpusReread': True, 'reviewedEarlierUnitIds': ['hlm-c023-b0063'], 'scope': 'SYNTHETIC TEST ONLY'}
        self.progress = p.initial_progress(self.mapping)
        refs = '; '.join((*p.V09_DELTA_REFERENCES, p.V09_FINAL_STATUS_REFERENCE, *p.NORMATIVE_DELTA_REFERENCES, p.SOURCE_DELTA_REFERENCE))
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
        self.checkpoint['normative_snapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        transition = self.provenance['normative_projection_v09']
        transition['candidateNormativeSnapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        transition['semanticDeltaReview']['normativeSnapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        p.V09_SEMANTIC_EVIDENCE_SHA = p.sha(p.encoded(transition['semanticDeltaReview']))
        self.checkpoint['normativeTransitionV09'] = {k: transition[k] for k in ('previousNormativeSnapshot', 'previousProvenanceSHA256', 'previousCheckpointSHA256', 'candidateNormativeSnapshot')}
        transition['finalStatusReview']['normativeSnapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        p.V09_FINAL_STATUS_EVIDENCE_SHA = p.sha(p.encoded(transition['finalStatusReview']))
        self.checkpoint['readiness'].update(independentFinalStatusReview='PASS', finalStatusReviewReference=p.V09_FINAL_STATUS_REFERENCE, finalStatusEvidenceSHA256=p.V09_FINAL_STATUS_EVIDENCE_SHA)
        self.save('provenance.json', self.provenance)
        self.checkpoint['files'] = [{'path': 'docs/hongloumeng/translation/' + n, 'sha256': p.sha((self.directory/n).read_bytes()), 'bytes': (self.directory/n).stat().st_size} for n in (*p.NORMATIVE_FILES, 'provenance.json')]
        self.save('CHECKPOINT.json', self.checkpoint)
        for u in self.progress['units']:
            for r in u['reviews']: r['standardSnapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT
        for c in self.progress['checkpoints']:
            if c['state'] == 'accepted': c['standardSnapshot'] = p.EXPECTED_NORMATIVE_SNAPSHOT

    def check(self):
        return p.validate_standard_readiness(self.mapping, self.progress)

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
        for key in ('observedSHA256','installedRepairedSHA256','observedSourceMapSHA256','expectedUnitCount','traditionalSHA256'):
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
        self.assertEqual(p.validate_reader_notes(self.mapping,json.loads((p.DATA/'reader-notes.json').read_bytes())),20)

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


if __name__ == '__main__':
    unittest.main()
