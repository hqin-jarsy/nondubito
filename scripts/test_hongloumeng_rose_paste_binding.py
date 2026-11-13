"""Real predecessor replay and fail-closed bounded chapter44 mutation checks."""
import copy,json,unittest
from unittest.mock import patch
import hongloumeng_rose_paste_binding as b
import hongloumeng_english_pipeline as p

class RosePaste(unittest.TestCase):
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
        original=b.regular;path='classics/hongloumeng/ch044.html'
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
    def test_wrong_traditional_exception_offset_fails(self):
        import build_hongloumeng_first80_traditional as trad
        rules=json.loads((trad.DATA/'conversion.zh-hant.json').read_text())
        row=next(x for x in rules['exceptions'] if x['chapter']==44 and x['block']==23)
        self.assertEqual(row['offset'],102);row['offset']=101
        with self.assertRaisesRegex(ValueError,'Exception source mismatch'):trad.apply_rules(p.load_source(),rules)
    @unittest.skipUnless((p.ROOT/"scripts/build_hongloumeng_first80.py").exists(), "Optional private producer unavailable")
    def test_private_producer_coordinates_and_public_parity(self):
        import build_hongloumeng_first80 as producer
        before=producer.model(apply_rose_paste=False);model=producer.model();source=p.load_source()
        for actual,expected in zip(model['chapters'],source['chapters']):
            self.assertEqual([x['text'] for x in actual['blocks']],[x['text'] for x in expected['blocks']])
        old=before['chapters'][43];new=model['chapters'][43]
        self.assertEqual(len(new['body']),len(old['body'])+1)
        for i,(a,z) in enumerate(zip(old['blocks'],new['blocks'])):
            self.assertEqual((a['start_char'],a['end_char']),(z['start_char'],z['end_char']))
            self.assertEqual(z['body_start'],a['body_start']+(i>23));self.assertEqual(z['body_end'],a['body_end']+(i>=23))
            self.assertEqual(new['body'][z['body_start']:z['body_end']],z['text'])
        self.assertTrue(producer.render(model))
    def test_preserved_two_readings_suite_on_authenticated_predecessor(self):
        import test_hongloumeng_two_readings_binding as legacy
        pipe,_,_,_,prior=b.predecessor()
        if not (p.ROOT/'scripts/build_hongloumeng_first80.py').exists():
            with patch.object(legacy,'p',pipe),patch.object(legacy,'b',prior):
                result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromTestCase(legacy.TwoReadings).run(result)
            self.assertEqual(result.testsRun,8);self.assertEqual(result.errors,[]);self.assertEqual(result.failures,[])
            return
        import build_hongloumeng_first80 as producer
        real_model=producer.model
        def prior_model(*args,**kwargs):
            kwargs['apply_rose_paste']=False;return real_model(*args,**kwargs)
        with patch.object(legacy,'p',pipe),patch.object(legacy,'b',prior),patch.object(producer,'model',prior_model):
            result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromTestCase(legacy.TwoReadings).run(result)
        self.assertEqual(result.testsRun,8);self.assertEqual(result.errors,[]);self.assertEqual(result.failures,[])

if __name__=='__main__':unittest.main()
