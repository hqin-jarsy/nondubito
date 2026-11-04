"""Read-only evidence checks; never synthesize an approval or render a page.

The fixtures are the genuinely completed DE pair/shared readings already saved
by the editors. Corruptions exist only in local copies. No publication receipt,
canonical whole-series approval, or rendered output is created by these tests.
"""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import prepare_original_series_review as review


BASE=review.ROOT/'data/laughter/multilingual'


def same_length_change(value):
    for index,char in enumerate(value):
        if char.isascii() and char.isalpha():
            return value[:index]+('Y' if char=='X' else 'X')+value[index+1:]
    raise AssertionError('No replaceable character in real reading fixture')


class StrictReadingEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((BASE/'de.json').read_text())
        cls.batch=json.loads((BASE/'cross-review-de-batch01.json').read_text())
        cls.shared=json.loads((BASE/'cross-review-de-shared.json').read_text())
        assert cls.batch['batch_ready'] is True
        assert cls.shared['metadata_ready'] is True
        cls.record=cls.batch['articles_reviewed'][0]
        cls.article=next(a for a in cls.data['articles'] if a['slug']==cls.record['slug'])
        cls.current=cls.batch['current_batch_article_sha256'][cls.record['slug']]
        cls.evidence=cls.shared.get('current_objects_read',cls.shared['objects_read'])[0]

    def test_genuine_completed_partial_evidence_still_matches(self):
        # This verifies existing real partial readings, not whole-series approval.
        review.verify_article_reading(self.article,self.record,self.current)
        review.verify_shared_reading(self.data,self.evidence)
        review.verify_saved_readbacks(self.data,self.batch)
        review.verify_saved_readbacks(self.data,self.shared)

    def test_same_shape_same_length_unreviewed_body_drift_is_rejected(self):
        article=copy.deepcopy(self.article)
        old=article['body'][1]
        article['body'][1]=same_length_change(old)
        self.assertEqual(len(old),len(article['body'][1]))
        self.assertEqual(len(self.article['body']),len(article['body']))
        with self.assertRaises(AssertionError):
            review.verify_article_reading(article,self.record,self.current)

    def test_same_shape_same_length_note_drift_is_rejected(self):
        article=copy.deepcopy(self.article)
        old=article['notes'][0]
        article['notes'][0]=same_length_change(old)
        self.assertEqual(len(old),len(article['notes'][0]))
        self.assertEqual(len(self.article['notes']),len(article['notes']))
        with self.assertRaises(AssertionError):
            review.verify_article_reading(article,self.record,self.current)

    def test_same_length_article_metadata_and_source_title_drift_is_rejected(self):
        for field in ('title','deck','pause','source_note','source-title'):
            with self.subTest(field=field):
                article=copy.deepcopy(self.article)
                if field=='source-title':
                    article['sources'][0]['title']=same_length_change(article['sources'][0]['title'])
                else:article[field]=same_length_change(article[field])
                with self.assertRaises(AssertionError):
                    review.verify_article_reading(article,self.record,self.current)

    def test_same_length_full_shared_metadata_drift_is_rejected(self):
        for group,key in (('series','notice'),('series','index_context'),('ui','paper')):
            with self.subTest(field=group+'.'+key):
                data=copy.deepcopy(self.data)
                if isinstance(data[group][key],list):
                    data[group][key][0]=same_length_change(data[group][key][0])
                else:data[group][key]=same_length_change(data[group][key])
                with self.assertRaises(AssertionError):review.verify_shared_reading(data,self.evidence)

    def test_final_shared_field_values_are_checked_not_only_object_hashes(self):
        evidence=copy.deepcopy(self.evidence)
        evidence['fields'][0]['value']=same_length_change(evidence['fields'][0]['value'])
        with self.assertRaises(AssertionError):review.verify_shared_reading(self.data,evidence)

    def test_real_report_byte_drift_is_rejected(self):
        name='cross-review-de-batch01.json'
        target=BASE/name
        digest=hashlib.sha256(target.read_bytes()).hexdigest()
        original=Path.read_bytes
        def corrupted(path):
            raw=original(path)
            return raw+b' ' if path==target else raw
        with patch.object(Path,'read_bytes',corrupted),self.assertRaises(AssertionError):
            review.read_evidence_report(BASE,name,digest)

    def test_missing_or_stale_actual_saved_field_readback_is_rejected(self):
        for mode in ('missing','stale','unpassed'):
            with self.subTest(mode=mode):
                batch=copy.deepcopy(self.batch)
                post=batch['post_application_readback']
                if mode=='missing':post['fields']=[]
                elif mode=='stale':
                    for field in post['fields']:field['saved_field_sha256']='0'*64
                else:post['passed']=False
                with self.assertRaises(AssertionError):review.verify_saved_readbacks(self.data,batch)

    def test_real_prepare_rejects_same_length_preseal_payload_drift(self):
        # The complete canonical reports are genuine now. Only corrupt a local
        # read of their current manuscript, never create an approving fixture.
        target=BASE/'de.json'
        original=Path.read_text
        for mode in ('body','note','article-metadata','shared-metadata'):
            def corrupted(path,*args,**kwargs):
                text=original(path,*args,**kwargs)
                if path!=target:return text
                data=json.loads(text)
                if mode=='body':data['articles'][0]['body'][1]=same_length_change(data['articles'][0]['body'][1])
                elif mode=='note':data['articles'][0]['notes'][0]=same_length_change(data['articles'][0]['notes'][0])
                elif mode=='article-metadata':data['articles'][0]['deck']=same_length_change(data['articles'][0]['deck'])
                else:data['series']['notice']=same_length_change(data['series']['notice'])
                return json.dumps(data,ensure_ascii=False)
            with self.subTest(mode=mode),patch.object(Path,'read_text',corrupted),self.assertRaises(AssertionError):
                review.prepare('laughter')

    def test_old_profiles_are_not_changed_by_opt_in_gate(self):
        with patch.object(review,'load_language',side_effect=AssertionError('Legacy profile unexpectedly gated')):
            review.require_strict_reading_evidence('legacy',{},None,[])


if __name__=='__main__':unittest.main()
