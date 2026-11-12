#!/usr/bin/env python3
"""B10 exact delta regressions. Synthetic mutations are test-only in memory/tempdirs."""
import ast,copy,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import hongloumeng_english_pipeline as p
import hongloumeng_ch002_ending_binding as b
class B10BindingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.mapping=p.source_map(p.load_source());cls.original=json.loads((p.DATA/'progress.json').read_bytes())
  cls.source_ix={u['id']:i for i,u in enumerate(cls.mapping['units'])}
 def setUp(self):self.progress=copy.deepcopy(self.original)
 def check(self):return b.validate_batch046050_preparation(p,self.mapping,self.progress)
 def mutate_file(self,path,data):
  original=Path.read_bytes
  return patch.object(Path,'read_bytes',lambda pp:data if pp==path else original(pp))
 def test_current_preparation_passes(self):
  r=self.check();self.assertEqual(r['states'],{'accepted':2863,'pending':1612});self.assertFalse(r['installationReady'])
 def test_readiness_requires_genuine_review(self):
  with patch.object(b,'B10_RECEIPT_SHA256',None),self.assertRaisesRegex(ValueError,'independent exact current-binding review pending'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_unrelated_pinned_receipt_rejected(self):
  raw=b'{"status":"SYNTHETIC TEST ONLY"}'
  with patch.object(b,'B10_RECEIPT_SHA256',b.sha(raw)),patch.object(b,'regular',return_value=raw),self.assertRaisesRegex(ValueError,'receipt scope differs'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_receipt_bytes_cannot_change(self):
  raw=b'{"status":"SYNTHETIC TEST ONLY"}'
  with patch.object(b,'B10_RECEIPT_SHA256','0'*64),patch.object(b,'regular',return_value=raw),self.assertRaises(ValueError):p.validate_standard_readiness(self.mapping,self.progress)
 def test_exact_old_default_validator_still_passes_in_original_context(self):
  # Reconstruct only for this test. Do not commit another full historical tree.
  history=p.ROOT/b.B10_HISTORY_RELATIVE
  with tempfile.TemporaryDirectory(prefix='b10-source2-original-') as td:
   root=Path(td)
   for relative in ('data/hongloumeng/first80-english','data/hongloumeng/first80-public','docs/hongloumeng/translation','scripts'):
    shutil.copytree(p.ROOT/relative,root/relative)
   for relative in json.loads((history/'manifest.json').read_bytes())['files']:
    target=root/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(history/relative,target)
   r=subprocess.run([sys.executable,'-B',str(root/'scripts/hongloumeng_english_pipeline.py'),'validate'],cwd=root,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads(r.stdout),{'sourceUnits':4475,'states':{'accepted':2461,'pending':2014},'publishable':False})
 def test_new_current_norm_does_not_masquerade_as_old_default(self):
  with self.assertRaisesRegex(ValueError,'current norm changed'):b.validate_readiness(p,self.mapping,self.progress)
 def test_incomplete_continuation_refused(self):
  with self.assertRaisesRegex(ValueError,'incomplete normative continuation'):b.validate_preparation(p,self.mapping,self.progress,normative_history=p.ROOT/b.B10_HISTORY_RELATIVE)
 def test_unrelated_historical_directory_refused(self):
  with self.assertRaisesRegex(ValueError,'wrong bounded continuation'):b.validate_preparation(p,self.mapping,self.progress,normative_history=p.ROOT,continuation_snapshot=b.B10_SNAPSHOT,continuation_reference=b.B10_REFERENCE)
 def test_current_norm_mutation_rejected(self):
  target=p.STANDARD/'english-batch-046-050.json'
  with self.mutate_file(target,target.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'current norm changed'):self.check()
 def test_exact_draft_file_protected(self):
  target=p.DATA/'chapters/ch050.draft.json'
  with self.mutate_file(target,target.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'final draft file changed'):self.check()
 def test_archived_norm_mutation_rejected(self):
  target=p.ROOT/b.B10_HISTORY_RELATIVE/'docs/hongloumeng/translation/english-standard.md'
  with self.mutate_file(target,target.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'historical bytes changed'):self.check()
 def test_archived_progress_mutation_rejected(self):
  target=p.ROOT/b.B10_HISTORY_RELATIVE/'data/hongloumeng/first80-english/progress.json'
  with self.mutate_file(target,target.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'historical bytes changed'):self.check()
 def test_current_metadata_cannot_relabel_source2_history(self):
  target=p.STANDARD/'CHECKPOINT.json';x=json.loads(target.read_bytes());x['previousChapter2AuthorEnding']['status']='FORGED'
  with self.mutate_file(target,json.dumps(x).encode()),self.assertRaisesRegex(ValueError,'current metadata or predecessor'):self.check()
 def test_accepted_chapter2_ending_protected_even_after_rehash(self):
  u=self.progress['units'][self.source_ix['hlm-c002-b0039']];u['segments'][0]['text']+=' FORGED'
  for r in u['reviews']:r['contentHash']=p.content_hash(u,self.progress['sourceIssues'])
  with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check()
 def test_felicity_body_protected(self):
  u=self.progress['units'][self.source_ix['hlm-c025-b0029']];u['segments'][0]['text']+=' FORGED'
  for r in u['reviews']:r['contentHash']=p.content_hash(u,self.progress['sourceIssues'])
  with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check()
 def test_previous_review_reference_protected(self):
  self.progress['units'][0]['reviews'][0]['reference']='FORGED'
  with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check()
 def test_previous_review_snapshot_migration_required(self):
  self.progress['units'][0]['reviews'][0]['standardSnapshot']=b.CURRENT_SNAPSHOT
  with self.assertRaisesRegex(ValueError,'accepted lineage'):self.check()
 def test_nine_old_checkpoint_corpora_protected(self):
  self.progress['checkpoints'][8]['corpusHash']='0'*64
  with self.assertRaisesRegex(ValueError,'scoped cumulative'):self.check()
 def test_current_review_lineage_protected(self):
  self.progress['units'][self.source_ix['hlm-c046-title']]['reviews'][0]['reference']='FORGED'
  with self.assertRaisesRegex(ValueError,'review lineage changed'):self.check()
 def test_current_corpus_bound_after_rehashing_unit_and_checkpoint(self):
  u=self.progress['units'][self.source_ix['hlm-c048-b0024']];u['segments'][0]['text']+=' FORGED'
  for r in u['reviews']:r['contentHash']=p.content_hash(u,self.progress['sourceIssues'])
  current=[u for s,u in zip(self.mapping['units'],self.progress['units']) if 46<=s['chapter']<=50]
  self.progress['checkpoints'][9]['corpusHash']=p.batch_hash(current,self.progress['sourceIssues'])
  with self.assertRaisesRegex(ValueError,'reviewed corpus changed'):self.check()
 def test_current_checkpoint_reference_protected(self):
  self.progress['checkpoints'][9]['reviewReference']='FORGED'
  with self.assertRaisesRegex(ValueError,'checkpoint lineage changed'):self.check()
 def test_old_source_issue_protected(self):
  self.progress['sourceIssues'][0]['description']+=' FORGED'
  with self.assertRaisesRegex(ValueError,'old issue'):self.check()
 def test_old_note_protected(self):
  target=p.DATA/'reader-notes.json';x=json.loads(target.read_bytes());x['notes'][0]['text']+=' FORGED'
  with self.mutate_file(target,json.dumps(x).encode()),self.assertRaisesRegex(ValueError,'old note'):self.check()
 def test_new_note_protected(self):
  target=p.DATA/'reader-notes.json';x=json.loads(target.read_bytes());x['notes'][-1]['text']+=' FORGED'
  with self.mutate_file(target,json.dumps(x).encode()),self.assertRaisesRegex(ValueError,'prior or selected note'):self.check()
 def test_chapter51_draft_remains_possible(self):
  u=self.progress['units'][self.source_ix['hlm-c051-title']];u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE TEST ONLY'}])
  self.assertEqual(self.check()['states']['draft'],1)
 def test_later_five_chapter_acceptance_not_globally_capped(self):
  for s,u in zip(self.mapping['units'],self.progress['units']):
   if 51<=s['chapter']<=55:
    u.update(state='accepted',segments=[{'kind':s['layout']['kind'],'text':'SYNTHETIC FUTURE TEST ONLY'}])
    u['reviews']=[{'type':t,'contentHash':p.content_hash(u,self.progress['sourceIssues']),'standardSnapshot':b.B10_SNAPSHOT,'reference':'SYNTHETIC FUTURE TEST ONLY'} for t in p.REVIEW_TYPES]
  current=[u for s,u in zip(self.mapping['units'],self.progress['units']) if 51<=s['chapter']<=55]
  self.progress['checkpoints'][10].update(state='accepted',corpusHash=p.batch_hash(current,self.progress['sourceIssues']),standardSnapshot=b.B10_SNAPSHOT,reviewReference='SYNTHETIC FUTURE TEST ONLY')
  self.assertEqual(self.check()['states']['accepted'],2863+len(current))
 def test_future_five_chapter_gate_still_required(self):
  u=self.progress['units'][self.source_ix['hlm-c056-title']];u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE TEST ONLY'}])
  with self.assertRaisesRegex(ValueError,'Finish preceding'):self.check()
 def test_private_author_policy_not_runtime_dependency(self):
  original=Path.read_bytes
  def read(path):
   if str(path).startswith(str(p.ROOT/'data/hongloumeng/first80/author-')):raise AssertionError('Private producer input read')
   return original(path)
  with patch.object(Path,'read_bytes',read):self.check()
 def test_no_release_invocation_and_gate_retained(self):
  text=Path(p.__file__).read_text();tree=ast.parse(text);main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
  guards=[n for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require' and n.args and isinstance(n.args[0],ast.Compare) and any(isinstance(c,ast.Constant) and c.value=='release' for c in n.args[0].comparators)]
  self.assertEqual(len(guards),1);self.assertIsInstance(guards[0].args[0].ops[0],ast.NotEq)
if __name__=='__main__':unittest.main()
