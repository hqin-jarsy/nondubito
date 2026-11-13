"""Bounded chapter72 corrections, fail-closed receipts, authenticated 21-test replay."""
import copy,json,sys,unittest
from contextlib import ExitStack
from unittest.mock import patch
import hongloumeng_ch072_decisions_binding as b
import hongloumeng_english_pipeline as p


class Chapter72Decisions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads((p.DATA/'source-map.json').read_text())
        cls.progress=json.loads((p.DATA/'progress.json').read_text())
    def prepared(self,mapping=None,progress=None):
        return b.validate_preparation(p,mapping or self.mapping,progress or self.progress)
    def test_real_preparation_and_predecessor(self):
        self.assertEqual(self.prepared(),p.EXPECTED_NORMATIVE_SNAPSHOT)
    def test_unrelated_english_change_fails(self):
        progress=copy.deepcopy(self.progress);progress['units'][0]['segments'][0]['text']+='!'
        with self.assertRaisesRegex(ValueError,'English delta widened'):self.prepared(progress=progress)
    def test_unrelated_source_change_fails(self):
        source=copy.deepcopy(p.load_source());source['chapters'][0]['blocks'][0]['text']+='!'
        with patch.object(p,'load_source',return_value=source),self.assertRaisesRegex(ValueError,'Source delta widened'):self.prepared()
    def test_unrelated_mapping_change_fails(self):
        mapping=copy.deepcopy(self.mapping);mapping['units'][0]['sourceHash']='0'*64
        with self.assertRaisesRegex(ValueError,'source map differs'):self.prepared(mapping=mapping)
    def test_no_technical_receipt_fails_closed(self):
        with patch.object(b,'REVIEW_SHA256',None),self.assertRaisesRegex(ValueError,'review pending'):b.validate_readiness(p,self.mapping,self.progress)
    def test_no_semantic_receipt_fails_closed(self):
        with patch.object(b,'SEMANTIC_SHA256',None),self.assertRaisesRegex(ValueError,'semantic review pending'):self.prepared()
    def test_wrong_binding_hash_fails(self):
        with patch.object(b,'BINDING_SHA256','0'*64),self.assertRaisesRegex(ValueError,'Unpinned'):self.prepared()
    def test_stale_html_fails(self):
        original=b.regular
        def stale(root,path):
            raw=original(root,path)
            return raw+b' ' if path=='classics/hongloumeng/en/ch072.html' else raw
        with patch.object(b,'regular',stale),self.assertRaisesRegex(ValueError,'successor bytes differ'):self.prepared()
    def test_corrupt_archive_fails(self):
        original=b.regular
        def corrupt(root,path):
            raw=original(root,path)
            return raw+b' ' if str(root).endswith(b.HISTORY) and path.endswith('progress.json') else raw
        with patch.object(b,'regular',corrupt),self.assertRaisesRegex(ValueError,'archive differs'):b.predecessor()
    def test_stale_review_hash_fails(self):
        progress=copy.deepcopy(self.progress)
        next(u for u in progress['units'] if u['id']==b.TARGETS[0])['reviews'][0]['contentHash']='0'*64
        with self.assertRaisesRegex(ValueError,'English delta widened'):self.prepared(progress=progress)
    def test_changed_character_count_fails(self):
        mapping=copy.deepcopy(self.mapping)
        next(u for u in mapping['units'] if u['id']==b.TARGETS[1])['characterCount']+=1
        with self.assertRaisesRegex(ValueError,'source map differs'):self.prepared(mapping=mapping)
    def test_non_target_html_delta_fails(self):
        original=b.regular
        def stale(root,path):
            raw=original(root,path)
            return raw+b' ' if str(root)==str(p.ROOT) and path=='classics/hongloumeng/en/ch072.html' else raw
        with patch.object(b,'regular',stale),self.assertRaisesRegex(ValueError,'HTML delta widened'):b.validate_html()
    def test_no_target_note_and_unchanged_notes(self):
        _,_,_,oldnotes,_=b.predecessor()
        current=json.loads((p.DATA/'reader-notes.json').read_text())
        self.assertEqual(current['notes'],oldnotes['notes'])
        self.assertFalse([n for n in current['notes'] if n['unitId'] in b.TARGETS])
    def test_only_expected_character_count_changes(self):
        _,oldmap,_,_,_=b.predecessor()
        for a,z in zip(oldmap['units'],self.mapping['units']):
            self.assertEqual(a['id'],z['id']);self.assertEqual(a['layout'],z['layout'])
            self.assertEqual(z['characterCount']-a['characterCount'],int(a['id']=='hlm-c072-b0022'))
    def test_candidate_hash_tamper_fails(self):
        original=b.regular
        def corrupt(root,path):
            raw=original(root,path)
            return raw+b' ' if path==b.D+'ch072-decisions-semantic-candidate.json' else raw
        with patch.object(b,'regular',corrupt),self.assertRaisesRegex(ValueError,'Frozen semantic candidate differs'):self.prepared()
    def test_preserved_dependency_tamper_fails(self):
        original=b.regular
        def corrupt(root,path):
            raw=original(root,path)
            return raw+b' ' if path=='scripts/test_hongloumeng_seven_character_binding.py' else raw
        with patch.object(b,'regular',corrupt),self.assertRaisesRegex(ValueError,'Preserved predecessor dependency differs'):b.binding()
    def test_public_history_excludes_private_producer(self):
        self.assertFalse((p.ROOT/b.HISTORY/'scripts/build_hongloumeng_first80.py').exists())
        self.assertNotIn('scripts/build_hongloumeng_first80.py',b.binding()['files'])
    def test_public_preparation_never_imports_private_producer(self):
        import builtins
        original=builtins.__import__
        def no_private(name,*args,**kwargs):
            if name=='build_hongloumeng_first80':raise AssertionError('Public readiness imported private producer')
            return original(name,*args,**kwargs)
        with patch.object(builtins,'__import__',no_private):
            self.assertEqual(self.prepared(),p.EXPECTED_NORMATIVE_SNAPSHOT)
    def test_production_exact_input_notes_gate(self):
        # Isolate only exact-input approval equality; normal load_validated
        # still requires the independent technical receipt separately.
        import build_hongloumeng_reading_english as render
        approval=json.loads((p.DATA/'reading-publication.json').read_text())
        approval.update(chapter72BindingSHA256=b.BINDING_SHA256,chapter72ReviewSHA256=b.REVIEW_SHA256,
            sourceHash=self.mapping['sourceHash'],standardSnapshot=p.EXPECTED_NORMATIVE_SNAPSHOT,
            progressHash=p.sha((p.DATA/'progress.json').read_bytes()),notesHash=p.sha((p.DATA/'reader-notes.json').read_bytes()))
        names=set(approval['implementationHashes'])|{'hongloumeng_ch072_decisions_binding.py'}
        approval['implementationHashes']={name:p.sha((p.ROOT/'scripts'/name).read_bytes()) for name in names}
        notes=json.loads((p.DATA/'reader-notes.json').read_text())
        with patch.object(render,'load_validated',return_value=(self.mapping,self.progress,notes,p.EXPECTED_NORMATIVE_SNAPSHOT)):
            self.assertIn('classics/hongloumeng/en/ch072.html',render.production_plan(approval))
            approval['notesHash']='0'*64
            with self.assertRaisesRegex(ValueError,'exact-input local-generation approval'):render.production_plan(approval)
    def test_preserved_later_suite_authenticated_replay(self):
        import test_hongloumeng_later_two_readings_binding as legacy
        pipe,_,_,_,prior=b.predecessor();history=p.ROOT/b.HISTORY
        trad=b.load_module(history/'scripts/build_hongloumeng_first80_traditional.py','_later_test_prior_trad')
        trad.DATA=history/'data/hongloumeng/first80-public';outputs=trad.outputs
        trad.outputs=lambda data=trad.DATA: outputs(trad.DATA if data==p.ROOT/'data/hongloumeng/first80-public' else data)
        with ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules,{'hongloumeng_english_pipeline':pipe,'hongloumeng_later_two_readings_binding':prior,'build_hongloumeng_first80_traditional':trad}))
            render=b.load_module(history/'scripts/build_hongloumeng_reading_english.py','_later_test_prior_render')
            # Original tests bind implementation bytes in the current root;
            # the archived renderer still executes its exact prior gate.
            render.__file__=str(p.ROOT/'scripts/build_hongloumeng_reading_english.py')
            stack.enter_context(patch.dict(sys.modules,{'build_hongloumeng_reading_english':render}))
            stack.enter_context(patch.object(legacy,'p',pipe));stack.enter_context(patch.object(legacy,'b',prior))
            result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromTestCase(legacy.LaterTwoReadings).run(result)
        self.assertEqual(result.testsRun,21);self.assertEqual(result.errors,[]);self.assertEqual(result.failures,[])


if __name__=='__main__':unittest.main()
