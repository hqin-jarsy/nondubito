#!/usr/bin/env python3
import ast,copy,json,unittest
from pathlib import Path
from unittest.mock import patch
import hongloumeng_english_pipeline as p
import hongloumeng_ch002_ending_binding as b
class Chapter2BindingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.mapping=p.source_map(p.load_source());cls.original=json.loads((p.DATA/'progress.json').read_bytes());cls.parent=p.ROOT/b.HISTORY_RELATIVE
  cls.before=json.loads((cls.parent/'data/hongloumeng/first80-english/progress.json').read_bytes());cls.ix=next(i for i,u in enumerate(cls.original['units']) if u['id']==b.TARGET)
 def setUp(self):self.progress=copy.deepcopy(self.original)
 def check(self,**kwargs):return b.validate_preparation(p,self.mapping,self.progress,**kwargs)
 def test_prospective_preparation_passes_without_installation_claim(self):
  result=self.check();self.assertEqual(result['states'],{'accepted':2461,'pending':2014});self.assertFalse(result['installationReady'])
 def test_missing_independent_binding_review_blocks_readiness(self):
  with self.assertRaisesRegex(ValueError,'current-binding/engineering review pending'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_fake_pinned_receipt_fails_scope(self):
  raw=b'{"status":"SYNTHETIC TEST ONLY"}'
  with patch.object(b,'CURRENT_BINDING_REVIEW_SHA256',b.sha(raw)),patch.object(b,'regular',return_value=raw),self.assertRaisesRegex(ValueError,'review scope differs'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_parent_unchanged_prefix_proof_not_applied_to_current(self):
  import hongloumeng_source4655_binding as old
  with self.assertRaises(ValueError):old.validate_readiness(p,self.mapping,self.progress)
 def test_exact_new_target_and_real_three_assessments(self):
  u=self.progress['units'][self.ix]
  self.assertEqual(u['segments'],[{'kind':'prose','text':'Yu-cun hurriedly turned to look. To learn who it was, listen to the next chapter.'}])
  self.assertEqual(len(u['reviews']),3);self.assertEqual({r['type'] for r in u['reviews']},set(p.REVIEW_TYPES))
  self.assertEqual(p.content_hash(u,self.progress['sourceIssues']),'504097d3d96b0e122f2fa7a02c6ac0a3865e5743bf3857e185bdf8a973bfebb9')
 def test_target_old_reviews_cannot_be_recycled(self):
  self.progress['units'][self.ix]['reviews']=copy.deepcopy(self.before['units'][self.ix]['reviews'])
  with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check()
 def test_target_edit_and_mechanical_rehash_rejected(self):
  u=self.progress['units'][self.ix];u['segments'][0]['text']+=' FORGED'
  for r in u['reviews']:r['contentHash']=p.content_hash(u,self.progress['sourceIssues'])
  with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check()
 def test_adjacent_english_edit_rejected(self):
  self.progress['units'][self.ix-1]['segments'][-1]['text']+=' FORGED'
  with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check()
 def test_split_target_segment_rejected(self):
  self.progress['units'][self.ix]['segments']=[{'kind':'prose','text':'Yu-cun hurriedly turned to look.'},{'kind':'prose','text':'To learn who it was, listen to the next chapter.'}]
  with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check()
 def test_other_accepted_review_prefix_protected(self):
  self.progress['units'][0]['reviews'][0]['reference']='FORGED'
  with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check()
 def test_incomplete_snapshot_migration_rejected(self):
  self.progress['units'][0]['reviews'][0]['standardSnapshot']=b.PREVIOUS_SNAPSHOT
  with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check()
 def test_first_checkpoint_old_hash_rejected(self):
  self.progress['checkpoints'][0]['corpusHash']=self.before['checkpoints'][0]['corpusHash']
  with self.assertRaisesRegex(ValueError,'scoped cumulative'):self.check()
 def test_other_checkpoint_body_hash_protected(self):
  self.progress['checkpoints'][8]['corpusHash']='0'*64
  with self.assertRaisesRegex(ValueError,'scoped cumulative'):self.check()
 def test_source4655_pending_hash_cannot_regress(self):
  u=next(x for x in self.progress['units'] if x['id']=='hlm-c046-b0006');u['sourceHash']='0'*64
  with self.assertRaisesRegex(ValueError,'bounded unit'):self.check()
 def test_prior_source_issue_protected(self):
  self.progress['sourceIssues'][0]['description']+=' FORGED'
  with self.assertRaisesRegex(ValueError,'old issue'):self.check()
 def test_old_note_protected(self):
  original=Path.read_bytes;target=p.DATA/'reader-notes.json';obj=json.loads(original(target));obj['notes'][0]['text']+=' FORGED';raw=json.dumps(obj).encode()
  with patch.object(Path,'read_bytes',lambda path:raw if path==target else original(path)),self.assertRaisesRegex(ValueError,'old note'):self.check()
 def test_semantic_receipt_bytes_protected(self):
  original=Path.read_bytes;target=p.DATA/'ch002-ending-semantic-review.json'
  with patch.object(Path,'read_bytes',lambda path:original(path)+b' ' if path==target else original(path)),self.assertRaisesRegex(ValueError,'semantic receipt changed'):self.check()
 def test_parent_old_target_history_protected(self):
  original=Path.read_bytes;target=self.parent/'data/hongloumeng/first80-english/progress.json'
  with patch.object(Path,'read_bytes',lambda path:original(path)+b' ' if path==target else original(path)),self.assertRaisesRegex(ValueError,'parent byte changed'):self.check()
 def test_original_normative_object_protected(self):
  original=Path.read_bytes;target=p.STANDARD/'english-batch-041-045.json'
  with patch.object(Path,'read_bytes',lambda path:original(path)+b' ' if path==target else original(path)),self.assertRaisesRegex(ValueError,'current norm changed'):self.check()
 def test_prior_overlay_immutable(self):
  original=Path.read_bytes;target=p.STANDARD/'source-binding-ch46-ch55.json'
  with patch.object(Path,'read_bytes',lambda path:original(path)+b' ' if path==target else original(path)),self.assertRaisesRegex(ValueError,'current norm changed'):self.check()
 def test_current_transition_cannot_relabel_history(self):
  original=Path.read_bytes;target=p.STANDARD/'CHECKPOINT.json';obj=json.loads(original(target));obj['previousSource4655']['status']='FORGED';raw=json.dumps(obj).encode()
  with patch.object(Path,'read_bytes',lambda path:raw if path==target else original(path)),self.assertRaisesRegex(ValueError,'transition metadata'):self.check()
 def test_private_producer_policy_is_not_runtime_dependency(self):
  original=Path.read_bytes;target=p.ROOT/'data/hongloumeng/first80/author-ch002-ending-policy.json'
  def read(path):
   if path==target:raise AssertionError('Private producer policy must not be read by English runtime')
   return original(path)
  with patch.object(Path,'read_bytes',read):self.check()
 def test_new_source_character_totals_recomputed(self):
  blocks=[u for u in self.mapping['units'] if u['index']]
  self.assertEqual(sum(u['characterCount'] for u in blocks),586240)
  self.assertEqual(sum(u['characterCount'] for u in blocks if u['chapter']<=5),35525)
 def test_future_46_draft_not_globally_capped(self):
  u=next(x for x in self.progress['units'] if x['id']=='hlm-c046-title');u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE TEST ONLY'}])
  self.assertEqual(self.check(exact_baseline=False)['states']['draft'],1)
 def test_future_batch_still_requires_accepted_ninth_checkpoint(self):
  u=next(x for x in self.progress['units'] if x['id']=='hlm-c046-title');u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE TEST ONLY'}]);self.progress['checkpoints'][8].update(state='pending',corpusHash=None,standardSnapshot=None,reviewReference=None)
  with self.assertRaisesRegex(ValueError,'Finish preceding'):p.validate_progress(self.mapping,self.progress,p.EXPECTED_NORMATIVE_SNAPSHOT)
 def test_future_tenth_batch_acceptance_not_artificially_capped(self):
  for source,u in zip(self.mapping['units'],self.progress['units']):
   if 46<=source['chapter']<=50:
    u.update(state='accepted',segments=[{'kind':source['layout']['kind'],'text':'SYNTHETIC FUTURE TEST ONLY.'}])
    u['reviews']=[{'type':t,'contentHash':p.content_hash(u,self.progress['sourceIssues']),'standardSnapshot':p.EXPECTED_NORMATIVE_SNAPSHOT,'reference':'SYNTHETIC FUTURE TEST ONLY'} for t in p.REVIEW_TYPES]
  units=[u for source,u in zip(self.mapping['units'],self.progress['units']) if 46<=source['chapter']<=50]
  self.progress['checkpoints'][9].update(state='accepted',corpusHash=p.batch_hash(units,self.progress['sourceIssues']),standardSnapshot=p.EXPECTED_NORMATIVE_SNAPSHOT,reviewReference='SYNTHETIC FUTURE TEST ONLY')
  self.assertEqual(self.check(exact_baseline=False)['states']['accepted'],2863)
 def test_no_english_release_handler_invoked(self):
  tree=ast.parse(Path(p.__file__).read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
  source=ast.get_source_segment(Path(p.__file__).read_text(),main)
  gates=[n for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require' and n.args and isinstance(n.args[0],ast.Compare) and any(isinstance(c,ast.Constant) and c.value=='release' for c in n.args[0].comparators)]
  self.assertEqual(len(gates),1);gate=gates[0]
  self.assertIsInstance(gate.args[0].ops[0],ast.NotEq);self.assertIn('disabled',gate.args[1].value.lower())
  load=next(n for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='load_source')
  self.assertLess(gate.lineno,load.lineno)
if __name__=='__main__':unittest.main()
