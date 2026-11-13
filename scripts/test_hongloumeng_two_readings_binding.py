"""Actual two-reading predecessor and bounded-delta mutation controls."""
import copy,json,unittest
from unittest.mock import patch
import hongloumeng_two_readings_binding as b
import hongloumeng_english_pipeline as p

class TwoReadings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads((p.DATA/'source-map.json').read_text())
        cls.progress=json.loads((p.DATA/'progress.json').read_text())
    def run_prepared(self,mapping=None,progress=None):
        return b.validate_preparation(p,mapping or self.mapping,progress or self.progress)
    def test_real_preparation_and_prior_author_acceptance(self):
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
        original=b.regular;path='classics/hongloumeng/ch005.html'
        def stale(root,name):return original(root,name)+b' ' if name==path else original(root,name)
        with patch.object(b,'regular',stale),self.assertRaisesRegex(ValueError,'successor bytes differ'):self.run_prepared()
    def test_corrupt_predecessor_fails(self):
        original=b.regular
        def corrupt(root,name):
            raw=original(root,name)
            return raw+b' ' if str(root).endswith(b.HISTORY) and name.endswith('progress.json') else raw
        with patch.object(b,'regular',corrupt),self.assertRaisesRegex(ValueError,'archive differs'):b.predecessor()
    def test_no_independent_review_fails_closed(self):
        with patch.object(b,'REVIEW_SHA256',None),self.assertRaisesRegex(ValueError,'review pending'):
            b.validate_readiness(p,self.mapping,self.progress)
    @unittest.skipUnless((p.ROOT/"scripts/build_hongloumeng_first80.py").exists(), "Optional private producer unavailable")
    def test_private_producer_matches_public(self):
        import build_hongloumeng_first80 as producer
        model=producer.model();source=p.load_source()
        for actual,expected in zip(model['chapters'],source['chapters']):
            self.assertEqual([x['text'] for x in actual['blocks']],[x['text'] for x in expected['blocks']])
        self.assertTrue(producer.render(model))
        self.assertIn('贪欢媾',source['chapters'][4]['blocks'][123]['text'])

if __name__=='__main__':unittest.main()
