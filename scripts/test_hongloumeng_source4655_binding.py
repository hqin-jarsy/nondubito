#!/usr/bin/env python3
"""Current source4655 engineering/negative tests; no synthetic receipt grants readiness."""
import copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import hongloumeng_english_pipeline as p
import hongloumeng_source4655_binding as b

class SourceBindingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.mapping=p.source_map(p.load_source())
  cls.before=json.loads((p.ROOT/b.HISTORY_RELATIVE/'data/hongloumeng/first80-english/progress.json').read_bytes())
  cls.original=json.loads((p.DATA/'progress.json').read_bytes())
  cls.refs={kind:json.loads((p.DATA/('source4655-'+kind+'-review.json')).read_bytes())['reference'] for kind in ['semantic','technical']}
 def setUp(self):self.progress=copy.deepcopy(self.original)
 def check(self,**kw):
  options=dict(review_reference=self.refs['semantic'],approved_metadata=self.refs);options.update(kw)
  return b.validate_preparation(p,self.mapping,self.progress,**options)
 def test_complete_final_state_with_genuine_receipts(self):
  result=self.check();self.assertFalse(result['installationReady']);self.assertEqual(result['states'],{'accepted':2461,'pending':2014})
  self.assertNotEqual(result['normativeSnapshot'],result['previousNormativeSnapshot'])
  self.assertEqual(p.validate_standard_readiness(self.mapping,self.progress),p.EXPECTED_NORMATIVE_SNAPSHOT)
 def test_missing_real_receipt_keeps_runtime_closed(self):
  with patch.object(b,'SEMANTIC_REVIEW_SHA256',None),self.assertRaisesRegex(ValueError,'semantic review is pending'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_receipt_hash_cannot_be_forged(self):
  with patch.object(b,'SEMANTIC_REVIEW_SHA256','0'*64),patch.object(b,'regular',return_value=b'{}'),self.assertRaisesRegex(ValueError,'unpinned semantic'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_unrelated_receipt_scope_rejected_even_if_hash_is_pinned(self):
  raw=b'{"status":"SYNTHETIC TEST ONLY"}'
  with patch.object(b,'SEMANTIC_REVIEW_SHA256',b.sha(raw)),patch.object(b,'regular',return_value=raw),self.assertRaisesRegex(ValueError,'incomplete semantic'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_old_readiness_cannot_accidentally_run_in_new_context(self):
  with self.assertRaisesRegex(ValueError,'exact pre-source4655 context'):p.validate_pre_source4655_readiness(self.mapping,self.progress)
 def test_archived_inputs_and_dependencies_tamper(self):
  names=['data/hongloumeng/first80-public/reading.zh.json','data/hongloumeng/first80-public/manifest.json',
         'data/hongloumeng/first80-public/reading.zh-hant.json','data/hongloumeng/first80-english/source-map.json',
         'data/hongloumeng/first80-english/progress.json','data/hongloumeng/first80-english/v010-20261111.before.json',
         'data/hongloumeng/first80-english/felicity-20261111.before.json','docs/hongloumeng/translation/english-batch-041-045.json',
         'docs/hongloumeng/translation/provenance.json','docs/hongloumeng/translation/CHECKPOINT.json',
         'scripts/hongloumeng_english_pipeline.py','scripts/build_hongloumeng_reading.py','scripts/web_analytics.py']
  original=Path.read_bytes
  for name in names:
   with self.subTest(name=name):
    target=p.ROOT/b.HISTORY_RELATIVE/name
    with patch.object(Path,'read_bytes',lambda path:original(path)+b' ' if path==target else original(path)),self.assertRaisesRegex(ValueError,'historical bytes changed'):self.check()
 def test_historical_manifest_tamper(self):
  original=Path.read_bytes;target=p.ROOT/b.HISTORY_RELATIVE/'history-manifest.json'
  with patch.object(Path,'read_bytes',lambda path:original(path)+b' ' if path==target else original(path)),self.assertRaisesRegex(ValueError,'historical manifest changed'):self.check()
 def test_current_bound_artifact_tamper(self):
  overlay=json.loads((p.ROOT/b.OVERLAY_RELATIVE).read_bytes());original=Path.read_bytes
  for relative in overlay['currentArtifactSHA256']:
   if relative==b.SOURCE_POLICY_EVIDENCE_PATH:continue
   with self.subTest(relative=relative):
    target=p.ROOT/relative
    with patch.object(Path,'read_bytes',lambda path:original(path)+b' ' if path==target else original(path)),self.assertRaisesRegex(ValueError,'current artifact changed'):self.check()
 def test_overlay_is_normative_and_exactly_pinned(self):
  self.assertEqual(len(p.NORMATIVE_FILES),14)
  original=Path.read_bytes;target=p.STANDARD/'source-binding-ch46-ch55.json'
  with patch.object(Path,'read_bytes',lambda path:original(path)+b' ' if path==target else original(path)),self.assertRaisesRegex(ValueError,'overlay changed'):self.check()
 def test_current_frozen_normative_bytes_cannot_change(self):
  original=Path.read_bytes;target=p.STANDARD/'english-batch-036-040.json'
  with patch.object(Path,'read_bytes',lambda path:original(path)+b' ' if path==target else original(path)),self.assertRaisesRegex(ValueError,'current normative snapshot changed'):self.check()
 def test_current_checkpoint_cannot_relabel_original(self):
  original=Path.read_bytes;target=p.STANDARD/'CHECKPOINT.json';changed=json.loads(original(target));changed['previousV010']['readiness']['sourceInstalled']=False;raw=json.dumps(changed).encode()
  with patch.object(Path,'read_bytes',lambda path:raw if path==target else original(path)),self.assertRaisesRegex(ValueError,'transition or frozen predecessor changed'):self.check()
 def test_current_before_image_still_exact(self):
  original=Path.read_bytes;target=p.DATA/p.FELICITY_BEFORE_FILENAME
  with patch.object(Path,'read_bytes',lambda path:original(path)+b' ' if path==target else original(path)),self.assertRaisesRegex(ValueError,'live historical before image changed'):self.check()
 def test_one_old_review_snapshot_left_behind_is_rejected(self):
  self.progress['units'][0]['reviews'][0]['standardSnapshot']=b.PREVIOUS_SNAPSHOT
  with self.assertRaisesRegex(ValueError,'old review lineage changed'):self.check()
 def test_partial_checkpoint_migration_rejected(self):
  self.progress['checkpoints'][8]['standardSnapshot']=b.PREVIOUS_SNAPSHOT
  with self.assertRaisesRegex(ValueError,'checkpoint or old reference lineage changed'):self.check()
 def test_old_reference_prefix_cannot_change(self):
  self.progress['units'][0]['reviews'][0]['reference']='invented'
  with self.assertRaisesRegex(ValueError,'old review lineage changed'):self.check()
 def test_accepted_body_rehash_does_not_authorize_change(self):
  u=self.progress['units'][0];u['segments'][0]['text']+=' FORGED'
  for r in u['reviews']:r['contentHash']=p.content_hash(u,self.progress['sourceIssues'])
  with self.assertRaisesRegex(ValueError,'accepted body or old review lineage changed'):self.check()
 def test_prior_issue_cannot_change(self):
  self.progress['sourceIssues'][0]['description']+=' FORGED'
  with self.assertRaisesRegex(ValueError,'previous source issue changed'):self.check()
 def test_prior_note_cannot_change(self):
  original=Path.read_bytes;target=p.DATA/'reader-notes.json';changed=json.loads(original(target));changed['notes'][0]['text']+=' FORGED';raw=json.dumps(changed).encode()
  with patch.object(Path,'read_bytes',lambda path:raw if path==target else original(path)),self.assertRaisesRegex(ValueError,'prior reader note changed'):self.check()
 def test_wrong_pending_source_hash_rejected(self):
  i=next(i for i,u in enumerate(self.progress['units']) if u['id']=='hlm-c046-b0006');self.progress['units'][i]['sourceHash']=self.before['units'][i]['sourceHash']
  with self.assertRaisesRegex(ValueError,'extra progress delta'):self.check()
 def test_46_draft_may_progress_after_real_approval_mechanics(self):
  u=next(u for u in self.progress['units'] if u['id']=='hlm-c046-title');u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE TEST ONLY'}])
  result=self.check(exact_baseline=False);self.assertEqual(result['states']['draft'],1)
 def test_46_draft_requires_ninth_checkpoint(self):
  u=next(u for u in self.progress['units'] if u['id']=='hlm-c046-title');u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE TEST ONLY'}])
  self.progress['checkpoints'][8].update(state='pending',corpusHash=None,standardSnapshot=None,reviewReference=None)
  with self.assertRaisesRegex(ValueError,'checkpoint or old reference lineage changed'):self.check(exact_baseline=False)
  with self.assertRaisesRegex(ValueError,'Finish preceding'):p.validate_progress(self.mapping,self.progress,p.EXPECTED_NORMATIVE_SNAPSHOT)
 def test_future_tenth_acceptance_not_capped(self):
  for source,u in zip(self.mapping['units'],self.progress['units']):
   if 46<=source['chapter']<=50:
    u.update(state='accepted',segments=[{'kind':source['layout']['kind'],'text':'SYNTHETIC FUTURE TEST ONLY.'}])
    u['reviews']=[{'type':t,'contentHash':p.content_hash(u,self.progress['sourceIssues']),'standardSnapshot':p.EXPECTED_NORMATIVE_SNAPSHOT,'reference':'SYNTHETIC FUTURE TEST ONLY'} for t in p.REVIEW_TYPES]
  units=[u for source,u in zip(self.mapping['units'],self.progress['units']) if 46<=source['chapter']<=50]
  self.progress['checkpoints'][9].update(state='accepted',corpusHash=p.batch_hash(units,self.progress['sourceIssues']),standardSnapshot=p.EXPECTED_NORMATIVE_SNAPSHOT,reviewReference='SYNTHETIC FUTURE TEST ONLY')
  self.assertEqual(self.check(exact_baseline=False)['states']['accepted'],2863)
 def test_real_receipts_still_require_final_metadata_transition(self):
  # Mechanical fixture only. No receipt exists and runtime remains closed.
  refs={'semantic':'SYNTHETIC SEMANTIC TEST ONLY','technical':'SYNTHETIC TECHNICAL TEST ONLY'}
  with self.assertRaisesRegex(ValueError,'transition or frozen predecessor changed'):
   self.check(review_reference=refs['semantic'],approved_metadata=refs)
 def test_reference_suffix_is_exact_and_append_only_with_real_reference(self):
  self.check()
  self.progress['units'][0]['reviews'][0]['reference']=self.refs['semantic']
  with self.assertRaisesRegex(ValueError,'old review lineage changed'):self.check()
 def test_actual_receipt_bytes_cannot_change(self):
  original=Path.read_bytes
  for kind in ['semantic','technical']:
   target=p.DATA/('source4655-'+kind+'-review.json')
   with patch.object(Path,'read_bytes',lambda path:original(path)+b' ' if path==target else original(path)),self.assertRaisesRegex(ValueError,'unpinned '+kind):p.validate_standard_readiness(self.mapping,self.progress)
 def test_genuine_suffix_cannot_be_omitted(self):
  self.progress['units'][0]['reviews'][0]['reference']=self.before['units'][0]['reviews'][0]['reference']
  with self.assertRaisesRegex(ValueError,'old review lineage changed'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_second_chapter_content_requires_separate_revision(self):
  u=next(u for u in self.progress['units'] if u['id']=='hlm-c002-b0018');u['segments'][-1]['text']+=' AUTHOR REVISION NOT PART OF THIS TRANSACTION'
  for r in u['reviews']:r['contentHash']=p.content_hash(u,self.progress['sourceIssues'])
  with self.assertRaisesRegex(ValueError,'accepted body or old review lineage changed'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_public_runtime_never_reads_private_policy(self):
  original=Path.read_bytes;target=p.ROOT/b.SOURCE_POLICY_EVIDENCE_PATH
  def no_private(path):
   if path==target:raise AssertionError('Public English validator read private source policy')
   return original(path)
  with patch.object(Path,'read_bytes',no_private):
   self.assertEqual(p.validate_standard_readiness(self.mapping,self.progress),p.EXPECTED_NORMATIVE_SNAPSHOT)
 def test_generation_policy_identity_cannot_be_removed_or_replaced(self):
  original=json.loads((p.ROOT/b.OVERLAY_RELATIVE).read_bytes())['currentArtifactSHA256']
  for value in [None,'0'*64]:
   changed=copy.deepcopy(original)
   if value is None:changed.pop(b.SOURCE_POLICY_EVIDENCE_PATH)
   else:changed[b.SOURCE_POLICY_EVIDENCE_PATH]=value
   with self.assertRaisesRegex(ValueError,'generation policy evidence identity changed'):b.validate_public_artifacts(p.ROOT,changed)
if __name__=='__main__':unittest.main()
