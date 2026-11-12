#!/usr/bin/env python3
"""Public-only source transition regressions; synthetic fixtures never grant readiness."""
import ast,copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import hongloumeng_english_pipeline as p
import hongloumeng_source5665_binding as b

class Source5665Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.mapping=p.source_map(p.load_source());cls.original=json.loads((p.DATA/'progress.json').read_bytes());cls.before=json.loads((p.ROOT/b.HISTORY_RELATIVE/b.D/'progress.json').read_bytes());cls.ix={u['id']:i for i,u in enumerate(cls.original['units'])}
 def setUp(self):self.progress=copy.deepcopy(self.original)
 def check(self,**kw):
  if b.SEMANTIC_RECEIPT_SHA256 is not None and b.TECHNICAL_RECEIPT_SHA256 is not None:
   kw.setdefault('reference',json.loads((p.DATA/'source5665-semantic-review.json').read_bytes())['reference'])
   kw.setdefault('technical_reference',json.loads((p.DATA/'source5665-technical-review.json').read_bytes())['reference'])
  return b.validate_preparation(p,self.mapping,self.progress,**kw)
 def mutate(self,path,raw):
  original=Path.read_bytes
  return patch.object(Path,'read_bytes',lambda f:raw if f==path else original(f))
 def test_complete_pending_preparation(self):
  r=self.check();self.assertEqual(r['states'],{'accepted':3155,'pending':1320});self.assertEqual((r['sourceChanges'],r['sourceSpans'],r['acceptedBodiesChanged']),(13,16,0));self.assertFalse(r['installationReady']);self.assertFalse(r['publicationEnabled'])
 def test_real_semantic_and_technical_receipts_required(self):
  for kind in ['semantic','technical']:
   with self.subTest(kind=kind),patch.object(b,kind.upper()+'_RECEIPT_SHA256',None),self.assertRaisesRegex(ValueError,'independent '+kind+' review pending'):
    p.validate_standard_readiness(self.mapping,self.progress)
 def test_no_arbitrary_receipt_can_grant_approval(self):
  raw=b'{"status":"SYNTHETIC NEGATIVE ONLY"}'
  with patch.object(b,'SEMANTIC_RECEIPT_SHA256',b.sha(raw)),patch.object(b,'regular',return_value=raw),self.assertRaisesRegex(ValueError,'incomplete semantic'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_wrong_receipt_digest_rejected(self):
  with patch.object(b,'SEMANTIC_RECEIPT_SHA256','0'*64),patch.object(b,'regular',return_value=b'{}'),self.assertRaisesRegex(ValueError,'unpinned semantic'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_no_accepted_content_or_reference_drift(self):
  for ident in ['hlm-c002-b0039','hlm-c025-b0012','hlm-c025-b0013','hlm-c025-b0029','hlm-c038-b0060','hlm-c051-title','hlm-c055-b0038']:
   with self.subTest(ident=ident):
    self.progress=copy.deepcopy(self.original);u=self.progress['units'][self.ix[ident]];u['segments'][0]['text']+=' FORGED'
    for r in u['reviews']:r['contentHash']=p.content_hash(u,self.progress['sourceIssues'])
    with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check(exact_baseline=False)
 def test_original_review_prefix_cannot_change(self):
  self.progress['units'][0]['reviews'][0]['reference']='FORGED'
  with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check()
 def test_old_snapshot_cannot_remain(self):
  self.progress['units'][0]['reviews'][0]['standardSnapshot']=b.PREVIOUS_SNAPSHOT
  with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check()
 def test_accepted_batch_checkpoints_preserved(self):
  for index in [0,4,10]:
   self.progress=copy.deepcopy(self.original);self.progress['checkpoints'][index]['reviewReference']='FORGED'
   with self.assertRaisesRegex(ValueError,'checkpoint lineage'):self.check()
 def test_source_unit_hash_must_migrate(self):
  i=self.ix['hlm-c056-b0008'];self.progress['units'][i]['sourceHash']=self.before['units'][i]['sourceHash']
  with self.assertRaisesRegex(ValueError,'bounded unit delta'):self.check()
 def test_new_unit_must_not_be_accepted_by_source_change(self):
  self.progress['units'][self.ix['hlm-c056-b0008']]['state']='accepted'
  with self.assertRaisesRegex(ValueError,'bounded unit delta'):self.check()
 def test_prior_source_issue_immutable(self):
  self.progress['sourceIssues'][0]['description']+=' FORGED'
  with self.assertRaisesRegex(ValueError,'historical source issue'):self.check()
 def test_prior_note_immutable(self):
  path=p.DATA/'reader-notes.json';v=json.loads(path.read_bytes());v['notes'][0]['text']+=' FORGED'
  with self.mutate(path,json.dumps(v).encode()),self.assertRaisesRegex(ValueError,'historical reader note'):self.check()
 def test_existing_context_files_pinned(self):
  history,manifest=b.authenticate_history(p.ROOT)
  names=['scripts/test_hongloumeng_english_pipeline.py',b.P+'reading.zh.json',b.D+'progress.json',b.S+'CHECKPOINT.json']
  for name in names:
   path=history/name
   with self.subTest(name=name),self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'archived predecessor changed'):self.check()
 def test_unchanged_historical_archives_pinned(self):
  history,manifest=b.authenticate_history(p.ROOT)
  names=['data/hongloumeng/first80-english/b11-current-binding-review.json','data/hongloumeng/first80-english/history/source-ch46-ch55-before/history-manifest.json','data/hongloumeng/first80-english/history/ch002-ending-before/history-manifest.json','docs/hongloumeng/translation/english-batch-051-055.json']
  for name in names:
   path=p.ROOT/name
   with self.subTest(name=name),self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'unchanged predecessor changed'):self.check()
 def test_exact_public_artifacts_pinned(self):
  overlay=json.loads((p.ROOT/b.OVERLAY_RELATIVE).read_bytes())
  for name in overlay['currentArtifacts']:
   path=p.ROOT/name
   with self.subTest(name=name),self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'current artifact changed'):self.check()
 def test_overlay_and_history_manifest_pinned(self):
  for rel in [b.OVERLAY_RELATIVE,b.HISTORY_RELATIVE+'/manifest.json']:
   path=p.ROOT/rel
   with self.subTest(rel=rel),self.mutate(path,path.read_bytes()+b' '),self.assertRaises(ValueError):self.check()
 def test_private_policy_and_qa_are_not_runtime_dependencies(self):
  original=Path.read_bytes
  def guarded(path):
   if '/first80/qa/' in str(path) or path.name.startswith('author-'):raise AssertionError('Private source read')
   return original(path)
  with patch.object(Path,'read_bytes',guarded):self.check()
 def test_frozen_metadata_keeps_original_b11(self):
  path=p.STANDARD/'CHECKPOINT.json';v=json.loads(path.read_bytes());v['previousB11']['status']='FORGED'
  with self.mutate(path,json.dumps(v).encode()),self.assertRaisesRegex(ValueError,'metadata or historical context'):self.check()
 def test_changed_source_scope_cannot_widen(self):
  v=copy.deepcopy(self.mapping);v['units'][0]['sourceHash']='0'*64
  with self.assertRaisesRegex(ValueError,'current map differs'):b.validate_preparation(p,v,self.progress)
 def test_future_draft_allowed_after_genuine_source_binding(self):
  u=self.progress['units'][self.ix['hlm-c056-title']];u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE MECHANICS ONLY'}])
  self.assertEqual(self.check(exact_baseline=False)['states']['draft'],1)
  self.assertEqual(p.validate_standard_readiness(self.mapping,self.progress),b.CURRENT_SNAPSHOT)
  with patch.object(b,'SEMANTIC_RECEIPT_SHA256',None),self.assertRaisesRegex(ValueError,'independent semantic review pending'):
   p.validate_standard_readiness(self.mapping,self.progress)
 def test_future_batch12_acceptance_not_capped(self):
  for s,u in zip(self.mapping['units'],self.progress['units']):
   if 56<=s['chapter']<=60:
    u.update(state='accepted',segments=[{'kind':s['layout']['kind'],'text':'SYNTHETIC FUTURE MECHANICS ONLY.'}]);u['reviews']=[{'type':t,'contentHash':p.content_hash(u,self.progress['sourceIssues']),'standardSnapshot':b.CURRENT_SNAPSHOT,'reference':'SYNTHETIC FUTURE MECHANICS ONLY'} for t in p.REVIEW_TYPES]
  units=[u for s,u in zip(self.mapping['units'],self.progress['units']) if 56<=s['chapter']<=60]
  self.progress['checkpoints'][11].update(state='accepted',corpusHash=p.batch_hash(units,self.progress['sourceIssues']),standardSnapshot=b.CURRENT_SNAPSHOT,reviewReference='SYNTHETIC FUTURE MECHANICS ONLY')
  self.assertEqual(self.check(exact_baseline=False)['states']['accepted'],3388)
 def test_future_batch_requires_preceding_checkpoint(self):
  u=self.progress['units'][self.ix['hlm-c061-title']];u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE ONLY'}])
  with self.assertRaisesRegex(ValueError,'Finish preceding'):self.check(exact_baseline=False)
 def test_no_english_release_gate_relaxation(self):
  tree=ast.parse(Path(p.__file__).read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');guards=[n for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require' and n.args and isinstance(n.args[0],ast.Compare) and any(isinstance(x,ast.Constant) and x.value=='release' for x in n.args[0].comparators)];self.assertEqual(len(guards),1);self.assertIsInstance(guards[0].args[0].ops[0],ast.NotEq)
 def test_finite_fixture_existing_destination_refused(self):
  with tempfile.TemporaryDirectory(prefix='source5665-negative-') as td:
   with self.assertRaisesRegex(ValueError,'output exists'):b.materialize_predecessor(p.ROOT,Path(td))

if __name__=='__main__':unittest.main(verbosity=2)
