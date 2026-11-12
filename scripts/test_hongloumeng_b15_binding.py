#!/usr/bin/env python3
"""B15 structural and adversarial tests. Synthetic data never grants readiness."""
import ast,copy,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import hongloumeng_english_pipeline as p
import hongloumeng_b15_binding as b

class B15Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.mapping=p.source_map(p.load_source());cls.original=json.loads((p.DATA/'progress.json').read_bytes());cls.ix={u['id']:i for i,u in enumerate(cls.original['units'])}
 def setUp(self):self.progress=copy.deepcopy(self.original)
 def check(self,**kw):
  kw.setdefault('approved',b.SEMANTIC_RECEIPT_SHA256 is not None and b.TECHNICAL_RECEIPT_SHA256 is not None)
  return b.validate_preparation(p,self.mapping,self.progress,**kw)
 def mutate(self,path,raw):
  original=Path.read_bytes
  return patch.object(Path,'read_bytes',lambda f:raw if f==path else original(f))
 def test_preparation_counts_and_no_approval(self):
  r=self.check();self.assertEqual(r['states'],{'accepted':4133,'pending':342});self.assertFalse(r['installationAuthorized']);self.assertFalse(r['publicationEnabled']);self.assertEqual(sum(len(u['reviews']) for u in self.progress['units']),12399)
 def test_genuine_readiness_and_each_missing_receipt_refusal(self):
  if b.SEMANTIC_RECEIPT_SHA256 is None or b.TECHNICAL_RECEIPT_SHA256 is None:
   with self.assertRaisesRegex(ValueError,'independent semantic current-binding review pending'):
    p.validate_standard_readiness(self.mapping,self.progress)
   return
  self.assertEqual(p.validate_standard_readiness(self.mapping,self.progress),b.CURRENT_SNAPSHOT)
  for kind in ['semantic','technical']:
   with self.subTest(kind=kind),patch.object(b,kind.upper()+'_RECEIPT_SHA256',None),self.assertRaisesRegex(ValueError,'independent '+kind+' current-binding review pending'):
    p.validate_standard_readiness(self.mapping,self.progress)
 def test_incomplete_receipt_rejected(self):
  raw=b'{"status":"SYNTHETIC NEGATIVE ONLY"}';original=b.regular
  with patch.object(b,'SEMANTIC_RECEIPT_SHA256',b.sha(raw)),patch.object(b,'regular',side_effect=lambda root,name:raw if name==b.D+'b15-semantic-review.json' else original(root,name)),self.assertRaisesRegex(ValueError,'incomplete semantic'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_wrong_receipt_digest_rejected(self):
  original=b.regular
  with patch.object(b,'SEMANTIC_RECEIPT_SHA256','0'*64),patch.object(b,'regular',side_effect=lambda root,name:b'{}' if name==b.D+'b15-semantic-review.json' else original(root,name)),self.assertRaisesRegex(ValueError,'unpinned semantic'):p.validate_standard_readiness(self.mapping,self.progress)
 def test_preserved_accepted_body_and_review_lineage(self):
  for ident in ['hlm-c002-b0039','hlm-c025-b0012','hlm-c025-b0013','hlm-c025-b0029','hlm-c038-b0060','hlm-c051-title','hlm-c055-b0038','hlm-c071-title','hlm-c057-b0029','hlm-c060-b0017']:
   with self.subTest(ident=ident):
    self.progress=copy.deepcopy(self.original);u=self.progress['units'][self.ix[ident]];u['segments'][0]['text']+=' FORGED'
    for r in u['reviews']:r['contentHash']=p.content_hash(u,self.progress['sourceIssues'])
    with self.assertRaisesRegex(ValueError,'body or review lineage'):self.check(exact_baseline=False)
 def test_existing_review_reference_prefix_preserved(self):
  self.progress['units'][0]['reviews'][0]['reference']='FORGED'
  with self.assertRaisesRegex(ValueError,'review lineage'):self.check()
 def test_stale_review_snapshot_rejected(self):
  self.progress['units'][0]['reviews'][0]['standardSnapshot']=b.PREVIOUS_SNAPSHOT
  with self.assertRaisesRegex(ValueError,'review lineage'):self.check()
 def test_new_reviews_require_authentic_lineage(self):
  self.progress['units'][self.ix['hlm-c071-title']]['reviews'][0]['reference']=b.REFERENCE
  with self.assertRaisesRegex(ValueError,'review lineage'):self.check()
 def test_all_checkpoint_lineage_protected(self):
  for index in [0,4,13,14]:
   self.progress=copy.deepcopy(self.original);self.progress['checkpoints'][index]['reviewReference']='FORGED'
   with self.assertRaisesRegex(ValueError,'checkpoint lineage'):self.check()
 def test_source_hash_cannot_be_reverted(self):
  self.progress['units'][self.ix['hlm-c071-b0008']]['sourceHash']='0'*64
  with self.assertRaisesRegex(ValueError,'review lineage'):self.check()
 def test_prior_source_issue_immutable(self):
  self.progress['sourceIssues'][0]['description']+=' FORGED'
  with self.assertRaisesRegex(ValueError,'source issue'):self.check()
 def test_prior_and_selected_notes_immutable(self):
  path=p.DATA/'reader-notes.json';v=json.loads(path.read_bytes())
  for index in [0,75,76,77]:
   z=copy.deepcopy(v);z['notes'][index]['text']+=' FORGED'
   with self.mutate(path,json.dumps(z).encode()),self.assertRaisesRegex(ValueError,'prior or selected note'):self.check()
 def test_unselected_note_cannot_be_added_in_protected_scope(self):
  path=p.DATA/'reader-notes.json';v=json.loads(path.read_bytes());v['notes'].append(copy.deepcopy(v['notes'][-1]))
  with self.mutate(path,json.dumps(v).encode()),self.assertRaisesRegex(ValueError,'extra note'):self.check(exact_baseline=False)
 def test_selected_note_source_anchor_immutable(self):
  path=p.DATA/'reader-notes.json';v=json.loads(path.read_bytes());v['notes'][76]['sourceHash']='0'*64
  with self.mutate(path,json.dumps(v).encode()),self.assertRaisesRegex(ValueError,'prior or selected note'):self.check()
 def test_exact_public_guidance_pinned(self):
  overlay=json.loads((p.ROOT/b.OVERLAY_RELATIVE).read_bytes())
  for name in overlay['publicFiles']:
   path=p.ROOT/name
   with self.subTest(name=name),self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'normative snapshot'):self.check()
 def test_old_archives_and_source_receipts_pinned(self):
  for name in ['scripts/hongloumeng_b12_binding.py',b.D+'source5665-semantic-review.json',b.D+'b11-current-binding-review.json',b.S+'english-batch-051-055.json',b.D+'history/source-ch56-ch65-before/manifest.json']:
   path=p.ROOT/name
   with self.subTest(name=name),self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'unchanged predecessor'):self.check()
 def test_overwritten_context_archive_pinned(self):
  for name in ['scripts/hongloumeng_english_pipeline.py',b.D+'progress.json',b.S+'english-voices.json',b.S+'provenance.json']:
   path=p.ROOT/b.HISTORY_RELATIVE/name
   with self.subTest(name=name),self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'archived predecessor'):self.check()
 def test_historical_reading_evidence_pinned(self):
  overlay=json.loads((p.ROOT/b.OVERLAY_RELATIVE).read_bytes())
  for name in overlay['evidence']:
   path=p.ROOT/name
   with self.subTest(name=name),self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'reading evidence'):self.check()
 def test_reviewed_draft_files_pinned(self):
  overlay=json.loads((p.ROOT/b.OVERLAY_RELATIVE).read_bytes())
  for row in overlay['draftFiles']:
   path=p.ROOT/row['path']
   with self.subTest(chapter=row['chapter']),self.mutate(path,path.read_bytes()+b' '),self.assertRaisesRegex(ValueError,'exact draft'):self.check()
 def test_metadata_preserves_original_B12(self):
  path=p.STANDARD/'CHECKPOINT.json';v=json.loads(path.read_bytes());v['previousB14']['status']='FORGED'
  with self.mutate(path,json.dumps(v).encode()),self.assertRaisesRegex(ValueError,'metadata or original context'):self.check()
 def test_no_private_policy_or_qa_runtime_reads(self):
  original=Path.read_bytes
  def guarded(path):
   if '/first80/qa/' in str(path) or path.name.startswith('author-'):raise AssertionError('Private source read')
   return original(path)
  with patch.object(Path,'read_bytes',guarded):self.check()
 def test_source_scope_cannot_expand(self):
  v=copy.deepcopy(self.mapping);v['units'][0]['sourceHash']='0'*64
  with self.assertRaisesRegex(ValueError,'current source map'):b.validate_preparation(p,v,self.progress)
 def test_future_draft_76_allowed_without_75_hardcap(self):
  u=self.progress['units'][self.ix['hlm-c076-title']];u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE MECHANICS ONLY'}])
  self.assertEqual(self.check(exact_baseline=False)['states']['draft'],1)
  with self.assertRaisesRegex(ValueError,'review lineage'):self.check()
 def test_future_batch_requires_preceding_checkpoint(self):
  u=self.progress['units'][self.ix['hlm-c076-title']];u.update(state='draft',segments=[{'kind':'title','text':'SYNTHETIC FUTURE MECHANICS ONLY'}])
  self.progress['checkpoints'][14]['state']='pending'
  with self.assertRaises(ValueError):self.check(exact_baseline=False)
 def test_normalized_kinds_match_strict_source_layout(self):
  for source,unit in zip(self.mapping['units'],self.progress['units']):
   if 71<=source['chapter']<=75:
    self.assertTrue(all(segment['kind']==source['layout']['kind'] for segment in unit['segments']))
  self.assertFalse(hasattr(b,'SEGMENT_KIND_EXCEPTIONS'))
  self.assertNotIn('reviewed_segment_kind',Path(p.__file__).read_text())
 def test_wrong_kind_still_rejected_by_strict_validator(self):
  progress=copy.deepcopy(self.original);unit=progress['units'][self.ix['hlm-c071-b0001']];unit['segments'][0]['kind']='verse'
  for review in unit['reviews']:review['contentHash']=p.content_hash(unit,progress['sourceIssues'])
  units=[u for source,u in zip(self.mapping['units'],progress['units']) if 71<=source['chapter']<=75]
  progress['checkpoints'][14]['corpusHash']=p.batch_hash(units,progress['sourceIssues'])
  with self.assertRaisesRegex(ValueError,'Verse, diagram, or prose kind lost'):p.validate_progress(self.mapping,progress,b.CURRENT_SNAPSHOT)
 def test_exact_corpus_and_historical_delta(self):
  overlay=json.loads((p.ROOT/b.OVERLAY_RELATIVE).read_bytes());drafts=[]
  for row in overlay['draftFiles']:drafts.extend(json.loads((p.ROOT/row['path']).read_bytes()))
  self.assertEqual(b.sha(b.canonical(drafts)),overlay['orderedCorpusSHA256'])
  evidence=json.loads((p.ROOT/b.E/'reading-lineage.json').read_bytes());self.assertEqual(len(evidence['units']),237)
  self.assertTrue(all(r['fullEnglishRead'] and r['fullChineseContextRead'] for r in evidence['units']))
 def test_publication_guard_precedes_release_action(self):
  tree=ast.parse(Path(p.__file__).read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');guards=[n for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='require' and n.args and isinstance(n.args[0],ast.Compare) and any(isinstance(x,ast.Constant) and x.value=='release' for x in n.args[0].comparators)];self.assertEqual(len(guards),1);self.assertIsInstance(guards[0].args[0].ops[0],ast.NotEq)
  actions=[n for n in ast.walk(main) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ['load_source','source_map','save_progress']];self.assertTrue(actions);self.assertLess(guards[0].lineno,min(n.lineno for n in actions))
 def test_historical_classification_is_exact_and_never_reads_aliases(self):
  original=Path.read_bytes
  def guarded(path):
   if str(path.relative_to(p.ROOT)) in b.HISTORICAL_NONRUNTIME_WITNESSES:raise AssertionError('Historical-only witness read')
   return original(path)
  with patch.object(Path,'read_bytes',guarded):self.check()
  overlay=json.loads((p.ROOT/b.OVERLAY_RELATIVE).read_bytes())
  self.assertFalse(b.authenticate_historical_classification(p.ROOT,overlay)['exactHistoricalRuntimeReplay'])
 def test_all_current_canonical_source_inputs_required(self):
  for name in ['data/hongloumeng/first80-public/reading.zh.json','data/hongloumeng/first80-public/reading.zh-hant.json',b.D+'source-map.json']:
   path=p.ROOT/name
   with self.subTest(name=name),self.mutate(path,path.read_bytes()+b' '),self.assertRaises(ValueError):self.check()
 def test_exact_historical_entries_cannot_be_reclassified(self):
  overlay=json.loads((p.ROOT/b.OVERLAY_RELATIVE).read_bytes())
  with patch.dict(b.HISTORICAL_NONRUNTIME_WITNESSES,{'docs/hongloumeng/translation/english-standard.md':'0'*64}),self.assertRaisesRegex(ValueError,'classification differs'):b.authenticate_historical_classification(p.ROOT,overlay)
 def test_finite_inventory_and_no_recursive_copy(self):
  h,m=b.authenticate_history(p.ROOT);self.assertEqual(len(m['files']),11);self.assertEqual(len(m['files'])+len(m['unchangedRootFiles']),563)
  self.assertFalse(any('/history/' in k for k in m['files']));self.assertFalse(any(k.startswith('.git/') or k.startswith('data/hongloumeng/first80/') for k in list(m['files'])+list(m['unchangedRootFiles'])))
  self.assertNotIn('copytree',Path(b.__file__).read_text())
 def test_regular_reader_rejects_traversal_and_absolute(self):
  for name in ['../outside.json','/outside.json']:
   with self.assertRaisesRegex(ValueError,'invalid relative path'):b.regular(p.ROOT,name)
 def test_regular_reader_rejects_symlink_and_hardlink(self):
  with tempfile.TemporaryDirectory(prefix='b15-alias-') as td:
   root=Path(td).resolve();(root/'original').write_text('probe');(root/'symbolic').symlink_to(root/'original');os.link(root/'original',root/'hard')
   with self.assertRaisesRegex(ValueError,'symlink'):b.regular(root,'symbolic')
   with self.assertRaisesRegex(ValueError,'hardlink'):b.regular(root,'hard')

if __name__=='__main__':unittest.main(verbosity=2)
