"""Bounded ch5 successor: real baseline and in-memory negative controls."""
import copy,json,unittest
from unittest.mock import patch
import hongloumeng_ch005_author_binding as a
import hongloumeng_english_pipeline as p

class Chapter5Binding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads((p.DATA/'source-map.json').read_text())
        cls.progress=json.loads((p.DATA/'progress.json').read_text())
    def test_real_current_preparation(self):
        self.assertEqual(a.validate_preparation(p,self.mapping,self.progress),p.EXPECTED_NORMATIVE_SNAPSHOT)
    def test_unrelated_english_change_rejected(self):
        changed=copy.deepcopy(self.progress)
        next(u for u in changed['units'] if u['id']!=a.TARGET)['segments'][0]['text']+='!'
        with self.assertRaisesRegex(ValueError,'delta widened'):
            a.validate_preparation(p,self.mapping,changed)
    def test_unrelated_mapping_change_rejected(self):
        changed=copy.deepcopy(self.mapping);changed['units'][0]['sourceHash']='0'*64
        with self.assertRaisesRegex(ValueError,'map differs'):
            a.validate_preparation(p,changed,self.progress)
    def test_archive_and_runtime_corruption_rejected(self):
        bound=a.binding();original=a.regular
        targets=[(a.ROOT/a.HISTORY,next(iter(bound['predecessorFiles']))),
                 (a.ROOT,next(iter(bound['unchangedRuntimeHashes'])))]
        for root,path in targets:
            def fake(r,q):
                raw=original(r,q)
                return raw+b' ' if Path(r)==root and q==path else raw
            from pathlib import Path
            with patch.object(a,'regular',fake),self.assertRaises(ValueError):
                a.predecessor(a.ROOT,bound)
    def test_missing_independent_review_cannot_pass(self):
        with patch.object(a,'REVIEW_SHA256',None),self.assertRaises((OSError,ValueError)):
            a.require_review(a.ROOT,a.binding())

if __name__=='__main__':unittest.main()
