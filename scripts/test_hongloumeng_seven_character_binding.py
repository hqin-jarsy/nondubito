"""Real predecessor replay and fail-closed bounded chapter49 mutation checks."""
import copy,json,unittest
from unittest.mock import patch
import hongloumeng_seven_character_binding as b
import hongloumeng_english_pipeline as p

class SevenCharacter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads((p.DATA/'source-map.json').read_text())
        cls.progress=json.loads((p.DATA/'progress.json').read_text())
    def run_prepared(self,mapping=None,progress=None):
        return b.validate_preparation(p,mapping or self.mapping,progress or self.progress)
    def test_real_preparation_and_predecessor_chain(self):
        self.assertEqual(self.run_prepared(),p.EXPECTED_NORMATIVE_SNAPSHOT)
    def test_unrelated_english_change_fails(self):
        progress=copy.deepcopy(self.progress);progress['units'][0]['segments'][0]['text']+='!'
        with self.assertRaisesRegex(ValueError,'English delta widened'):self.run_prepared(progress=progress)
    def test_unrelated_source_change_fails(self):
        source=copy.deepcopy(p.load_source());source['chapters'][0]['blocks'][0]['text']+='!'
        with patch.object(p,'load_source',return_value=source),self.assertRaisesRegex(ValueError,'Source delta widened'):self.run_prepared()
    def test_unrelated_mapping_change_fails(self):
        mapping=copy.deepcopy(self.mapping);mapping['units'][0]['sourceHash']='0'*64
        with self.assertRaisesRegex(ValueError,'source map differs'):self.run_prepared(mapping=mapping)
    def test_stale_html_fails(self):
        original=b.regular;path='classics/hongloumeng/ch049.html'
        def stale(root,name):return original(root,name)+b' ' if name==path else original(root,name)
        with patch.object(b,'regular',stale),self.assertRaisesRegex(ValueError,'successor bytes differ'):self.run_prepared()
    def test_corrupt_predecessor_fails(self):
        original=b.regular
        def corrupt(root,name):
            raw=original(root,name)
            return raw+b' ' if str(root).endswith(b.HISTORY) and name.endswith('progress.json') else raw
        with patch.object(b,'regular',corrupt),self.assertRaisesRegex(ValueError,'archive differs'):b.predecessor()
    def test_no_independent_review_fails_closed(self):
        with patch.object(b,'REVIEW_SHA256',None),self.assertRaisesRegex(ValueError,'review pending'):b.validate_readiness(p,self.mapping,self.progress)
    def test_no_semantic_review_fails_closed(self):
        with patch.object(b,'SEMANTIC_SHA256',None),self.assertRaisesRegex(ValueError,'semantic review pending'):self.run_prepared()
    def test_wrong_binding_hash_fails(self):
        with patch.object(b,'BINDING_SHA256','0'*64),self.assertRaisesRegex(ValueError,'Unpinned'):self.run_prepared()
    def test_stale_target_review_hash_fails(self):
        progress=copy.deepcopy(self.progress)
        next(u for u in progress['units'] if u['id']==b.TARGET)['reviews'][0]['contentHash']='0'*64
        with self.assertRaisesRegex(ValueError,'English delta widened'):self.run_prepared(progress=progress)
    def test_changed_character_count_fails(self):
        mapping=copy.deepcopy(self.mapping)
        next(u for u in mapping['units'] if u['id']==b.TARGET)['characterCount']+=1
        with self.assertRaisesRegex(ValueError,'source map differs'):self.run_prepared(mapping=mapping)
    def test_changed_reader_notes_bytes_fails(self):
        original=b.regular
        def stale(root,name):return original(root,name)+b' ' if name==b.D+'reader-notes.json' else original(root,name)
        with patch.object(b,'regular',stale),self.assertRaisesRegex(ValueError,'successor bytes differ'):self.run_prepared()
    def test_frozen_note_overlay_and_anchor(self):
        import build_hongloumeng_reading_english as render
        note=next(n for n in json.loads((p.DATA/'reader-notes.json').read_text())['notes'] if n['unitId']==b.TARGET)
        source=next(u for u in self.mapping['units'] if u['id']==b.TARGET)
        unit=next(u for u in self.progress['units'] if u['id']==b.TARGET)
        record=b.binding()['beforeReaderNoteRecord'];changed=b.note_record(record,note,source,unit)
        self.assertEqual(changed['anchor']['start'],260);self.assertEqual(changed['anchor']['end'],271)
        self.assertEqual(render.note_location(note,source,unit,{},{}),(0,271))
        for field in ['text','textSHA256']:
            bad=copy.deepcopy(record);bad[field]+='!'
            with self.assertRaisesRegex(ValueError,'Frozen reader-note placement differs'):b.note_record(bad,note,source,unit)
        bad=copy.deepcopy(note);bad['text']+='!'
        with self.assertRaisesRegex(ValueError,'Bounded reader note differs'):b.note_record(record,bad,source,unit)
    def test_stale_production_notes_hash_fails(self):
        # Isolate the exact-input gate; readiness failure is covered separately.
        import build_hongloumeng_reading_english as render
        import hongloumeng_reading_presentation_binding as presentation
        import hongloumeng_ch005_author_binding as author
        import hongloumeng_two_readings_binding as two
        import hongloumeng_rose_paste_binding as rose
        approval=json.loads((p.DATA/'reading-publication.json').read_text())
        approval.update(sevenCharacterBindingSHA256=b.BINDING_SHA256,sevenCharacterReviewSHA256=b.REVIEW_SHA256,
            rosePasteBindingSHA256=rose.BINDING_SHA256,rosePasteReviewSHA256=rose.REVIEW_SHA256,
            twoReadingsBindingSHA256=two.BINDING_SHA256,twoReadingsReviewSHA256=two.REVIEW_SHA256,
            chapter5BindingSHA256=author.BINDING_SHA256,chapter5ReviewSHA256=author.REVIEW_SHA256,
            presentationBindingSHA256=presentation.BINDING_SHA256,presentationReviewSHA256=presentation.REVIEW_SHA256,
            sourceHash=self.mapping['sourceHash'],standardSnapshot=p.EXPECTED_NORMATIVE_SNAPSHOT,
            progressHash=p.sha((p.DATA/'progress.json').read_bytes()),notesHash=p.sha((p.DATA/'reader-notes.json').read_bytes()))
        names=set(approval['implementationHashes'])|{'hongloumeng_seven_character_binding.py'}
        approval['implementationHashes']={name:p.sha((p.ROOT/'scripts'/name).read_bytes()) for name in names}
        notes=json.loads((p.DATA/'reader-notes.json').read_text())
        with patch.object(render,'load_validated',return_value=(self.mapping,self.progress,notes,p.EXPECTED_NORMATIVE_SNAPSHOT)):
            self.assertIn('classics/hongloumeng/en/ch049.html',render.production_plan(approval))
            approval['notesHash']='0'*64
            with self.assertRaisesRegex(ValueError,'exact-input local-generation approval'):render.production_plan(approval)
    def test_non_target_html_change_rejected_even_if_file_hash_rebound(self):
        original=b.regular
        def stale(root,name):
            raw=original(root,name)
            return raw+b' ' if str(root)==str(p.ROOT) and name=='classics/hongloumeng/en/ch049.html' else raw
        with patch.object(b,'regular',stale),self.assertRaisesRegex(ValueError,'HTML delta widened'):b.validate_html()
    @unittest.skipUnless((p.ROOT/"scripts/build_hongloumeng_first80.py").exists(), "Optional private producer unavailable")
    def test_private_producer_coordinates_and_public_parity(self):
        import build_hongloumeng_first80 as producer
        before=producer.model(apply_seven_character=False);model=producer.model();source=p.load_source()
        for actual,expected in zip(model['chapters'],source['chapters']):
            self.assertEqual([x['text'] for x in actual['blocks']],[x['text'] for x in expected['blocks']])
        old=before['chapters'][48];new=model['chapters'][48]
        self.assertEqual(len(new['body']),len(old['body']))
        for i,(a,z) in enumerate(zip(old['blocks'],new['blocks'])):
            self.assertEqual((a['start_char'],a['end_char']),(z['start_char'],z['end_char']))
            self.assertEqual(z['body_start'],a['body_start']);self.assertEqual(z['body_end'],a['body_end'])
            self.assertEqual(new['body'][z['body_start']:z['body_end']],z['text'])
        self.assertTrue(producer.render(model))
    def test_preserved_rose_and_nested_two_suites_on_authenticated_predecessor(self):
        import sys
        import test_hongloumeng_rose_paste_binding as legacy
        pipe,_,_,_,prior=b.predecessor()
        history=p.ROOT/b.HISTORY
        trad=b.load_module(history/'scripts/build_hongloumeng_first80_traditional.py','_seven_test_prior_trad')
        trad.DATA=history/'data/hongloumeng/first80-public'
        outputs=trad.outputs
        trad.outputs=lambda data=trad.DATA: outputs(trad.DATA if data==p.ROOT/'data/hongloumeng/first80-public' else data)
        from contextlib import ExitStack
        with ExitStack() as stack:
            stack.enter_context(patch.object(legacy,'p',pipe));stack.enter_context(patch.object(legacy,'b',prior))
            stack.enter_context(patch.dict(sys.modules,{'build_hongloumeng_first80_traditional':trad}))
            if (p.ROOT/'scripts/build_hongloumeng_first80.py').exists():
                import build_hongloumeng_first80 as producer
                real_model=producer.model
                def prior_model(*args,**kwargs):
                    kwargs['apply_seven_character']=False;return real_model(*args,**kwargs)
                stack.enter_context(patch.object(producer,'model',prior_model))
            result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromTestCase(legacy.RosePaste).run(result)
        self.assertEqual(result.testsRun,13);self.assertEqual(result.errors,[]);self.assertEqual(result.failures,[])

if __name__=='__main__':unittest.main()
