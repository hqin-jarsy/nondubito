#!/usr/bin/env python3
"""B11 bounded integration regressions. All proposed mutations are test-only."""
import ast,copy,json,os,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
import hongloumeng_english_pipeline as p
import hongloumeng_b11_binding as b
class B11BindingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.mapping=p.source_map(p.load_source());cls.original=json.loads((p.DATA/'progress.json').read_bytes());cls.ix={s['id']:i for i,s in enumerate(cls.mapping['units'])}
 def setUp(self):self.progress=copy.deepcopy(self.original)
 def check(self):return b.validate_preparation(p,self.mapping,self.progress)
 def mutate(self,path,data):
  read=Path.read_bytes
  return patch.object(Path,'read_bytes',lambda target:data if target==path else read(target))
 def reject_file(self,path,mutator):
  raw=path.read_bytes();x=json.loads(raw);mutator(x)
  with self.mutate(path,json.dumps(x,ensure_ascii=False).encode()),self.assertRaises(ValueError):self.check()
 def test_preparation_passes_but_is_not_installation_approval(self):
  x=self.check();self.assertEqual(x['states'],{'accepted':3155,'pending':1320});self.assertFalse(x['installationReady']);self.assertFalse(x['publicationEnabled'])
 def test_normal_readiness_requires_real_receipt(self):
  with patch.object(b,'RECEIPT_SHA256',None),self.assertRaisesRegex(ValueError,'independent exact current-binding'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_arbitrary_hashed_receipt_rejected(self):
  raw=b'{"status":"SYNTHETIC NEGATIVE TEST ONLY"}'
  with patch.object(b,'RECEIPT_SHA256',b.sha(raw)),patch.object(b,'regular',return_value=raw),self.assertRaisesRegex(ValueError,'review scope differs'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_wrong_receipt_hash_rejected(self):
  with patch.object(b,'RECEIPT_SHA256','0'*64),patch.object(b,'regular',return_value=b'{}'),self.assertRaisesRegex(ValueError,'receipt changed'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_exact_original_b10_context_passes(self):
  h,m,parent,mapping,progress=b.load_parent(p.ROOT);self.assertEqual(parent.standard_snapshot(),b.PREVIOUS_SNAPSHOT);self.assertEqual(parent.validate_progress(mapping,progress,b.PREVIOUS_SNAPSHOT),{'accepted':2863,'pending':1612})
 def test_changed_ch25_cannot_pass_original_b10_validator(self):
  import hongloumeng_ch002_ending_binding as old
  with self.assertRaises(ValueError):old.validate_batch046050_readiness(p,self.mapping,self.progress)
 def test_current_source_mutation_rejected(self):
  path=p.SOURCE/'reading.zh.json'
  with self.mutate(path,path.read_bytes()+b' '),self.assertRaises(ValueError):self.check()
 def test_current_source_map_mutation_rejected(self):self.reject_file(p.DATA/'source-map.json',lambda x:x['units'][0].update(sourceHash='0'*64))
 def test_norm_mutation_rejected(self):
  path=p.STANDARD/'english-standard.md'
  with self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'current norm changed'):self.check()
 def test_current_term_mutation_rejected(self):self.reject_file(p.STANDARD/'english-batch-051-055.json',lambda x:x['terms'][0].update(form='FORGED'))
 def test_historical_object_mutation_rejected(self):self.reject_file(p.STANDARD/'english-terms.json',lambda x:x['entries'][0].update(form='FORGED'))
 def test_prior_batch_mutation_rejected(self):
  path=p.STANDARD/'english-batch-046-050.json'
  with self.mutate(path,path.read_bytes()+b' '),self.assertRaises(ValueError):self.check()
 def test_historical_manifest_mutation_rejected(self):
  path=p.ROOT/b.HISTORY_RELATIVE/'manifest.json'
  with self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'historical manifest changed'):self.check()
 def test_old_six_ch25_reviews_are_protected(self):
  path=p.ROOT/b.HISTORY_RELATIVE/'data/hongloumeng/first80-english/progress.json'
  self.reject_file(path,lambda x:x['units'][self.ix['hlm-c025-b0012']]['reviews'][0].update(reference='FORGED'))
 def test_old_source_history_is_protected(self):
  path=p.ROOT/'data/hongloumeng/first80-english/history/source-ch46-ch55-before/history-manifest.json'
  with self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'unchanged predecessor byte changed'):self.check()
 def test_genuine_limited_evidence_is_pinned(self):
  path=p.ROOT/b.E/'content-assessments.json'
  with self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'historical evidence changed'):self.check()
 def test_accepted25_only_weight_tokens(self):
  unit=self.progress['units'][self.ix['hlm-c025-b0012']];unit['segments'][0]['text']+=' FORGED'
  for r in unit['reviews']:r['contentHash']=p.content_hash(unit,self.progress['sourceIssues'])
  with self.assertRaisesRegex(ValueError,'accepted body or review lineage'):self.check()
 def test_accepted25_old_body_cannot_keep_new_reviews(self):
  unit=self.progress['units'][self.ix['hlm-c025-b0012']]
  for s in unit['segments']:s['text']=s['text'].replace('catties','jin').replace('catty','jin')
  for r in unit['reviews']:r['contentHash']=p.content_hash(unit,self.progress['sourceIssues'])
  with self.assertRaisesRegex(ValueError,'accepted body or review lineage'):self.check()
 def test_accepted25_cannot_reuse_old_review_reference(self):
  self.progress['units'][self.ix['hlm-c025-b0013']]['reviews'][0]['reference']='chapter-025-independent-editorial-review-2026-11-11-final-delta'
  with self.assertRaisesRegex(ValueError,'accepted body or review lineage'):self.check()
 def test_accepted25_cannot_reuse_old_hash(self):
  self.progress['units'][self.ix['hlm-c025-b0012']]['reviews'][0]['contentHash']='0911cd9b62341511512c0a64c5fc0c408b160eec47d6ac4214aa47b213921f4f'
  with self.assertRaisesRegex(ValueError,'accepted body or review lineage'):self.check()
 def test_batch5_requires_new_limited_delta_hash(self):
  self.progress['checkpoints'][4]['corpusHash']='0e517c5e038c812608e0a9d427bef6bb7264a4672063a4b4cc15a6ad71c7dc4e'
  with self.assertRaisesRegex(ValueError,'batch5 delta'):self.check()
 def test_batch5_original_reference_is_retained(self):
  self.progress['checkpoints'][4]['reviewReference']=b.REFERENCE
  with self.assertRaisesRegex(ValueError,'checkpoint lineage'):self.check()
 def test_author_chapter2_ending_is_unchanged(self):
  self.progress['units'][self.ix['hlm-c002-b0039']]['segments'][0]['text']+=' FORGED'
  with self.assertRaisesRegex(ValueError,'accepted body or review lineage'):self.check()
 def test_felicity_is_unchanged(self):
  self.progress['units'][self.ix['hlm-c025-b0029']]['segments'][0]['text']+=' FORGED'
  with self.assertRaisesRegex(ValueError,'accepted body or review lineage'):self.check()
 def test_unrelated_accepted_body_is_unchanged(self):
  self.progress['units'][self.ix['hlm-c040-title']]['segments'][0]['text']+=' FORGED'
  with self.assertRaisesRegex(ValueError,'accepted body or review lineage'):self.check()
 def test_b11_rehash_cannot_launder_prose_change(self):
  u=self.progress['units'][self.ix['hlm-c053-b0014']];u['segments'][0]['text']+=' FORGED'
  for r in u['reviews']:r['contentHash']=p.content_hash(u,self.progress['sourceIssues'])
  self.progress['checkpoints'][10]['corpusHash']=p.batch_hash([u for s,u in zip(self.mapping['units'],self.progress['units']) if 51<=s['chapter']<=55],self.progress['sourceIssues'])
  with self.assertRaisesRegex(ValueError,'accepted body or review lineage'):self.check()
 def test_exact_draft_artifact_protected(self):
  path=p.DATA/'chapters/ch055.draft.json'
  with self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'exact draft file changed'):self.check()
 def test_b11_review_reference_protected(self):
  self.progress['units'][self.ix['hlm-c051-title']]['reviews'][0]['reference']='FORGED'
  with self.assertRaisesRegex(ValueError,'accepted body or review lineage'):self.check()
 def test_b11_checkpoint_reference_protected(self):
  self.progress['checkpoints'][10]['reviewReference']='FORGED'
  with self.assertRaisesRegex(ValueError,'checkpoint lineage'):self.check()
 def test_existing_issue_preserved(self):
  self.progress['sourceIssues'][0]['description']+=' FORGED'
  with self.assertRaisesRegex(ValueError,'existing source issue changed'):self.check()
 def test_existing_note_preserved(self):self.reject_file(p.DATA/'reader-notes.json',lambda x:x['notes'][0].update(text='FORGED'))
 def test_selected_note_preserved(self):self.reject_file(p.DATA/'reader-notes.json',lambda x:x['notes'][-1].update(text='FORGED'))
 def test_note_placement_after_answer_preserved(self):self.reject_file(p.STANDARD/'english-batch-051-055.json',lambda x:x['selectedReaderNotes'][-1]['anchor'].update(segmentIndex=1))
 def test_transition_metadata_preserved(self):self.reject_file(p.STANDARD/'CHECKPOINT.json',lambda x:x['previousB10'].update(status='FORGED'))
 def test_ch56_draft_still_possible(self):
  u=self.progress['units'][self.ix['hlm-c056-title']];u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE TEST ONLY'}]);self.assertEqual(self.check()['states']['draft'],1)
 def test_next_five_acceptance_not_capped_at55(self):
  current=[]
  for s,u in zip(self.mapping['units'],self.progress['units']):
   if 56<=s['chapter']<=60:
    u.update(state='accepted',segments=[{'kind':s['layout']['kind'],'text':'SYNTHETIC FUTURE TEST ONLY'}]);u['reviews']=[{'type':t,'contentHash':p.content_hash(u,self.progress['sourceIssues']),'standardSnapshot':b.CURRENT_SNAPSHOT,'reference':'SYNTHETIC FUTURE TEST ONLY'} for t in p.REVIEW_TYPES];current.append(u)
  self.progress['checkpoints'][11].update(state='accepted',corpusHash=p.batch_hash(current,self.progress['sourceIssues']),standardSnapshot=b.CURRENT_SNAPSHOT,reviewReference='SYNTHETIC FUTURE TEST ONLY')
  self.assertEqual(self.check()['states']['accepted'],3155+len(current))
 def test_future_five_chapter_gate_required(self):
  u=self.progress['units'][self.ix['hlm-c061-title']];u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE TEST ONLY'}])
  with self.assertRaisesRegex(ValueError,'Finish preceding'):self.check()
 def test_future_source_issue_allowed(self):
  s=self.mapping['units'][self.ix['hlm-c056-title']];self.progress['sourceIssues'].append({'id':'SYNTHETIC-FUTURE','unitId':s['id'],'sourceHash':s['sourceHash'],'state':'open','description':'SYNTHETIC FUTURE TEST ONLY','resolution':None});self.check()
 def test_private_paths_not_read(self):
  read=Path.read_bytes
  def guard(path):
   if '/first80/qa/' in str(path) or any(x.startswith('author-') for x in path.parts):raise AssertionError('Private runtime read')
   return read(path)
  with patch.object(Path,'read_bytes',guard):self.check()
 def test_release_guard_inspected_without_invocation(self):
  tree=ast.parse(Path(p.__file__).read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');guards=[n for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require' and n.args and isinstance(n.args[0],ast.Compare) and any(isinstance(c,ast.Constant) and c.value=='release' for c in n.args[0].comparators)];self.assertEqual(len(guards),1);self.assertIsInstance(guards[0].args[0].ops[0],ast.NotEq)
if __name__=='__main__':unittest.main(verbosity=2)
