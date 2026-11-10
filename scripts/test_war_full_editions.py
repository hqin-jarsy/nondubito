#!/usr/bin/env python3
"""War Theory restoration safeguards. --release adds complete-edition checks."""
import argparse,copy,hashlib,html,json,re,unittest,tempfile,sys,subprocess,os
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit,unquote
import build_war_full_editions as full
import validate_war_manuscripts as validator
from prepare_action_sources import Document,Node,one

class WarPreflight(unittest.TestCase):
 def test_chinese_traditional_and_english_baselines(self):
  record=full.preserved()
  self.assertEqual(sum(r['units'] for r in record['source_bodies'].values()),1121)
  self.assertEqual(set(record['source_bodies']),set(full.SLUGS))
 def test_completed_manuscripts_preserve_rich_structure(self):
  checked=0
  for lang in full.LANGS:
   for slug in full.SLUGS:
    p=full.BASE/'translations'/lang/(slug+'.json')
    if not p.exists():continue
    data=full.read(p);source=full.read(full.BASE/'sources'/(slug+'.json'))
    if len(data.get('body',[]))!=len(source['body_zh']):continue
    full.load(lang,slug);checked+=1
  self.assertGreaterEqual(checked,5)
 def test_loader_rejects_truncated_copy(self):
  target=full.BASE/'translations/de/ep01.json';data=full.read(target);data=copy.deepcopy(data);data['body']=data['body'][:-1];original=validator.read
  with patch.object(validator,'read',lambda p:data if p==target else original(p)):
   with self.assertRaisesRegex(AssertionError,'unit coverage'):full.load('de','ep01')
 def test_loader_rejects_stale_source(self):
  target=full.BASE/'translations/de/ep01.json';data=full.read(target);data=copy.deepcopy(data);data['source_sha256']='stale';original=validator.read
  with patch.object(validator,'read',lambda p:data if p==target else original(p)):
   with self.assertRaisesRegex(AssertionError,'source hash'):full.load('de','ep01')
 def test_table_shape_detects_missing_cells(self):
  self.assertNotEqual(full.structure('<div><table><tr><td>A</td><td>B</td></tr></table></div>'),full.structure('<div><table><tr><td>A</td></tr></table></div>'))
 def test_english_patches_are_local_and_source_bound(self):
  for slug in full.SLUGS:
   body=full.english_body(slug);doc=Document(body);units=[doc.raw(n) for n in doc.root.children if isinstance(n,Node)]
   source=full.read(full.BASE/'sources'/(slug+'.json'))
   self.assertEqual(len(units),len(source['body_en']))
   p=full.BASE/'reviews'/('en-'+slug+'.json');r=full.read(p) if p.exists() else {};changes={x['unit']-1:x['after'] for x in r.get('changes',[])}
   expected=[changes.get(i,u) for i,u in enumerate(source['body_en'])]
   for c in full.effective.author_changes(slug,'en'):expected[c['unit']-1]=c['after']
   for c in full.effective.english_second(slug).get('changes',[]):
    if c.get('field','body')=='body':expected[full.effective.index_of(c)]=c['after']
   self.assertEqual(units,expected)


 def test_exact_overlays_reject_context_structure_index_and_duplicates(self):
  e=full.effective;original=['<p>One</p>','<p>Two</p>'];change={'unit':1,'before':original[0],'after':'<p>Revised</p>'}
  result=e.overlay_units(original,[change],'test')
  self.assertEqual(result,['<p>Revised</p>','<p>Two</p>']);self.assertEqual(original,['<p>One</p>','<p>Two</p>'])
  self.assertEqual(e.overlay_units(result,[change],'test'),result)
  for bad in [dict(change,before='<p>Unknown</p>'),dict(change,after='<div>Revised</div>'),dict(change,unit=0),dict(change,unit=4),dict(change,body_index=1)]:
   with self.assertRaises(AssertionError):e.overlay_units(original,[bad],'test')
  with self.assertRaisesRegex(AssertionError,'duplicate'):e.overlay_units(original,[change,change],'test')
 def test_exact_overlays_preserve_emphasis_and_link_attributes(self):
  e=full.effective
  for before,after in [('<p><em>Text</em></p>','<p>Text</p>'),('<p><strong>Text</strong></p>','<p>Text</p>'),('<p><a href="a.html">A</a></p>','<p><a href="b.html">A</a></p>')]:
   with self.assertRaisesRegex(AssertionError,'markup changed'):
    e.overlay_units([before],[{'unit':1,'before':before,'after':after}],'negative markup')
 def test_boolean_indices_are_not_integer_unit_positions(self):
  for change in ({'unit':True},{'body_index':False}):
   with self.assertRaisesRegex(AssertionError,'must be an integer'):full.effective.index_of(change)
 def test_author_and_integration_require_complete_input_coverage(self):
  e=full.effective;read=e.read;manifest=copy.deepcopy(read(e.ZH_MANIFEST));manifest['changes'].pop()
  with patch.object(e,'read',lambda p:manifest if p==e.ZH_MANIFEST else read(p)):
   with self.assertRaisesRegex(AssertionError,'scope/coverage mismatch'):e.author_changes('ep03','zh')
  target=e.AUTHOR/'integration-review.json';receipt=copy.deepcopy(read(target));receipt['input_sha256s'].pop(next(iter(receipt['input_sha256s'])))
  with patch.object(e,'read',lambda p:receipt if p==target else read(p)):
   with self.assertRaisesRegex(AssertionError,'input coverage incomplete'):e.verify_author_traditional()

 def test_independent_overlay_refuses_stale_receipt(self):
  e=full.effective;path=e.review_path('de','ep04');receipt=copy.deepcopy(e.read(path));receipt['manuscript_sha256']='stale';read=e.read
  with patch.object(e,'read',lambda p:receipt if p==path else read(p)):
   with self.assertRaisesRegex(AssertionError,'stale review manuscript'):full.load('de','ep04')
 def test_english_second_review_refuses_changed_first_review(self):
  e=full.effective;path=e.BASE/'reviews/en-second/ep01.json';receipt=copy.deepcopy(e.read(path));receipt['first_review_sha256']='stale';read=e.read
  with patch.object(e,'read',lambda p:receipt if p==path else read(p)):
   with self.assertRaisesRegex(AssertionError,'second review stale'):full.english_body('ep01')
 def test_author_dictionary_changes_eight_body_nodes_and_one_title(self):
  import prepare_war_author_traditional as traditional
  outputs=traditional.outputs();records=json.loads(outputs[full.effective.AUTHOR/'traditional-patches.json'])
  changes=[c for r in records.values() for c in r['changes']]
  self.assertEqual(len(changes),9)
  self.assertEqual(sum('unit' in c for c in changes),8)
  self.assertEqual(sum(c.get('field')=='document_title' for c in changes),1)
  for name,receipt in records.items():
   path=full.ROOT/name;old=(full.effective.AUTHOR/'baseline-traditional'/path.name).read_text();new=outputs[path]
   pattern=r'var variants = (\{.*?\});\n';om=re.search(pattern,old,re.S);nm=re.search(pattern,new,re.S)
   before=json.loads(om[1]);after=json.loads(nm[1]);changed={c['before_key'] for c in receipt['changes']}
   self.assertEqual({k:v for k,v in before.items() if k not in changed},{k:v for k,v in after.items() if k not in {c['after_key'] for c in receipt['changes']}})
   self.assertEqual(old[:om.start(1)]+old[om.end(1):],new[:nm.start(1)]+new[nm.end(1):])
 def test_effective_manuscripts_keep_source_structure(self):
  for lang in full.LANGS:
   for slug in full.SLUGS:
    for i,(source,target) in enumerate(zip(full.effective.source_units(slug),full.load(lang,slug)['body'])):
     validator.unit_check(source,target,(lang,slug,i))
 def test_primary_index_expectations_are_complete_and_source_bound(self):
  for lang in ('zh','en'):
   data=full.primary_index_data(lang)
   self.assertEqual(len(data['intro']),5);self.assertEqual(len(data['groups']),2)
   self.assertEqual(set(data['cards']),set(full.SLUGS));self.assertEqual(len(data['source_notes']),2)
  self.assertEqual(full.primary_index_data('zh')['cards'],{slug:{key:full.read(full.BASE/'index-source.json')['cards'][slug]['zh'][key] for key in ('title','deck')} for slug in full.SLUGS})

 def test_source_notes_hide_the_other_primary_language(self):
  for selected,hidden in [('zh','en'),('zh-hant','en'),('en','zh')]:
   self.assertIn('[data-lang="'+selected+'"] .source-note>.lang-'+hidden,full.CSS)
  self.assertIn('{display:none!important}',full.CSS)
 def test_war_search_carries_language_only_for_primary_routes(self):
  text=(full.ROOT/'search.js').read_text()
  start=text.index('if ((/^essays\\/war');end=text.index(') && readingLanguage)',start)
  condition=text[start:end]
  self.assertIn(r'/^essays\/war\/(?:index|ep[0-9]{2}|if[0-9]{2}|if-conclusion)\.html$/.test(record.u)',condition)
  pattern=re.compile(r'^essays/war/(?:index|ep[0-9]{2}|if[0-9]{2}|if-conclusion)\.html$')
  for slug in ('index',*full.SLUGS):self.assertRegex('essays/war/'+slug+'.html',pattern)
  for route in ('essays/war/ja/ep01.html','essays/war/index 2.html','essays/other/ep01.html'):
   self.assertIsNone(pattern.match(route),route)

 def test_english_index_matches_reviewed_article_metadata(self):
  cards=full.primary_index_data('en')['cards']
  for slug in full.SLUGS:
   item=full.effective.english_metadata(slug)
   self.assertTrue(item['title'].endswith(cards[slug]['title']),(slug,item['title'],cards[slug]['title']))
   self.assertEqual(Document(item['deck']).root.text(),cards[slug]['deck'],slug)
 def test_discovery_rejects_unknown_concurrent_edits_before_writing(self):
  import refresh_war_full_discovery as discovery
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);target=root/'search.json';target.write_text('unknown concurrent edit')
   with patch.object(Path,'write_text') as write:
    with self.assertRaisesRegex(AssertionError,'changed concurrently'):
     discovery.write_outputs({target:'new'}, {target:full.sha('original')})
    write.assert_not_called()

 def test_optimized_python_rejected_on_module_import(self):
  code='import sys;sys.path.insert(0,'+repr(str(full.ROOT/'scripts'))+');import build_war_full_editions'
  for flags,optimize in [(['-O'],'0'),([], '1')]:
   with self.subTest(flags=flags,optimize=optimize):
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONOPTIMIZE=optimize)
    result=subprocess.run([sys.executable,*flags,'-c',code],capture_output=True,text=True,env=env)
    self.assertNotEqual(result.returncode,0)
    self.assertIn('Optimized Python is not supported',result.stderr)
 def test_preview_rejects_repository_paths_before_render(self):
  for target in (full.ROOT,full.DIRECTORY,full.ROOT/'new-preview'):
   with self.subTest(target=target),patch.object(sys,'argv',['build','--preview-dir',str(target)]),patch.object(full,'render') as render:
    with self.assertRaisesRegex(ValueError,'outside the repository'):full.main()
    render.assert_not_called()
 def test_preview_resolves_symlinks(self):
  with tempfile.TemporaryDirectory() as tmp:
   outside=Path(tmp);(outside/'linked-repository').symlink_to(full.ROOT,target_is_directory=True)
   with self.assertRaisesRegex(ValueError,'outside the repository'):
    full.safe_preview_directory(outside/'linked-repository'/'new-preview')
   self.assertEqual(full.safe_preview_directory(outside/'safe-preview'),(outside/'safe-preview').resolve())
 def test_preview_rejects_nested_symlink_escape(self):
  with tempfile.TemporaryDirectory() as tmp:
   directory=Path(tmp);(directory/'essays').symlink_to(full.ROOT/'essays',target_is_directory=True)
   with self.assertRaisesRegex(ValueError,'escapes isolated directory'):
    full.preview_destinations(directory,{full.DIRECTORY/'fr/ep01.html':'draft'})
 def test_index_title_updates_heading_and_metadata_safely(self):
  source='<html><head><title>Old — Non Dubito</title><meta property="og:title" content="Old"><meta name="twitter:title" content="Old"></head><body><h1 class="series-title">Old</h1><p>Old prose retained</p></body></html>'
  title='New & "quoted" <title>'
  result=full.index_title(source,title);doc=Document(result)
  self.assertEqual(one(doc.root.walk(),lambda n:n.tag=='h1','h1').text(),title)
  self.assertEqual(one(doc.root.walk(),lambda n:n.tag=='title','title').text(),title+' — Non Dubito')
  for node in doc.root.walk():
   if node.tag=='meta':self.assertEqual(node.attrs['content'],title+' — Non Dubito')
  self.assertIn('<p>Old prose retained</p>',result)
  self.assertEqual(full.index_title(result,title),result)


 def test_writer_rejects_unknown_concurrent_change_before_writing(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);target=root/'page.html';target.write_text('unknown user edit')
   with patch.object(full,'ROOT',root),patch.object(full,'BASE',root),patch.object(full,'read',return_value={'page.html':full.sha('baseline')}),patch.object(Path,'write_text') as write:
    with self.assertRaisesRegex(AssertionError,'unrecognized concurrent edits'):
     full.write_outputs({target:'new rendered version'})
    write.assert_not_called()
   self.assertEqual(target.read_text(),'unknown user edit')
 def test_reviews_reject_missing_receipt(self):
  with patch.object(full,'read',side_effect=FileNotFoundError('missing independent receipt')):
   with self.assertRaises(FileNotFoundError):full.verify_reviews()
 def test_reviews_reject_stale_source_and_translation(self):
  actual_read=full.read
  def original(p):
   if p==full.BASE/'reviews/en-index.json':return {'all_units_read':True,'source_sha256':actual_read(full.BASE/'index-source.json')['source_sha256']}
   return actual_read(p)
  sources={slug:original(full.BASE/'sources'/(slug+'.json')) for slug in full.SLUGS}
  for fault in ('source','translation'):
   receipt={'language':'ja','status':'passed','independent':True,'all_units_read':True,'unresolved':[],
    'source_sha256s':{slug:sources[slug]['source_sha256'] for slug in full.SLUGS},
    'translation_sha256s':{slug:'current-translation-hash' for slug in full.SLUGS}}
   if fault=='source':receipt['source_sha256s']['ep01']='stale'
   else:receipt['translation_sha256s']['ep01']='stale'
   with self.subTest(fault=fault),patch.object(full,'file_sha',return_value='current-translation-hash'),patch.object(full,'read',lambda p:receipt if p==full.BASE/'reviews/ja.json' else original(p)):
    with self.assertRaisesRegex(AssertionError,fault+' review stale'):full.verify_reviews()

 def test_partial_preview_is_idempotent_and_keeps_source_bodies(self):
  outputs=full.render(partial=True);original=Path.read_text
  def preview_read(p,*args,**kwargs):return outputs[p] if p in outputs else original(p,*args,**kwargs)
  with patch.object(Path,'read_text',preview_read):again=full.render(partial=True)
  for p,text in outputs.items():self.assertEqual(again[p],text,str(p))
  for p,text in outputs.items():
   doc=Document(text)
   self.assertEqual(text.count('</head>'),1,str(p))
   self.assertEqual(text.count('id="war-full-reader"'),1,str(p))
   self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1,str(p))
   if p.parent==full.DIRECTORY and p.stem!='index':
    body=one(doc.root.walk(),lambda n:n.has('essay-body','lang-zh'),'zh')
    self.assertEqual(full.raw_units(doc,body),full.effective.source_units(p.stem))
 def test_index_group_headings_precede_lists_and_complete_cards(self):
  for p,text in full.render(partial=True).items():
   if p.stem!='index' or p.parent.name not in full.LANGS:continue
   if not (full.BASE/'translations'/p.parent.name/'index.json').exists():continue
   doc=Document(text);groups=[n for n in doc.root.walk() if n.has('group-head')]
   lists=[n for n in doc.root.walk() if n.has('entry-list')]
   self.assertEqual(len(groups),2)
   self.assertEqual(len(lists),2)
   for group,entries in zip(groups,lists):self.assertLessEqual(group.end,entries.start)
   self.assertEqual(sum(n.has('entry-row') for n in doc.root.walk()),16)


class WarRelease(unittest.TestCase):
 def test_current_independent_receipts_and_complete_manuscripts(self):
  full.verify_reviews()
  for lang in full.LANGS:
   for slug in full.SLUGS:full.load(lang,slug)
 def test_generated_pages_are_current_and_full(self):
  outputs=full.render();self.assertEqual(len(outputs),102)
  for p,text in outputs.items():
   self.assertEqual(p.read_text(),text,str(p))
   if p.stem=='index':continue
   doc=Document(text);lang=p.parent.name if p.parent!=full.DIRECTORY else 'en'
   node=one(doc.root.walk(),lambda n:n.has('essay-body') and (lang!='en' or n.has('lang-en')),str(p))
   units=full.raw_units(doc,node)
   expected=full.read(full.BASE/'sources'/(p.stem+'.json'))['body_zh']
   self.assertEqual(len(units),len(expected),(lang,p.stem))
   if lang!='en':self.assertEqual(units,full.load(lang,p.stem)['body'])
 def test_discovery_is_current_and_preserves_unrelated_entries(self):
  import refresh_war_full_discovery as discovery
  import xml.etree.ElementTree as ET
  outputs=discovery.outputs()
  for path,value in outputs.items():
   self.assertEqual(path.read_text(),value,str(path))
   relative=str(path.relative_to(full.ROOT))
   old=subprocess.check_output(['git','show','HEAD:'+relative],cwd=full.ROOT,text=True)
   if relative.startswith('data/search/'):
    before=json.loads(old)['records'];after=json.loads(value)['records']
    self.assertEqual([r for r in before if not r['u'].startswith('essays/war/')],[r for r in after if not r['u'].startswith('essays/war/')],relative)
   elif relative=='sitemap.xml':
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    extract=lambda raw:{n.find(ns+'loc').text:n.find(ns+'lastmod').text for n in ET.fromstring(raw) if '/essays/war/' not in n.find(ns+'loc').text}
    self.assertEqual(extract(old),extract(value))

 def test_links_eight_languages_citations_and_analytics(self):
  for p,text in full.render().items():
   doc=Document(text)
   toggles=[n for n in doc.root.walk() if n.has('lang-btn')]
   self.assertEqual(len(toggles),8,str(p))
   self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1,str(p))
   self.assertIn('1c920752456e42b5b5469641245a07c2',text)
   self.assertEqual(text.count('id="war-full-reader"'),1)
   for node in doc.root.walk():
    if node.tag=='link' and node.attrs.get('rel')=='canonical':self.assertTrue(node.attrs['href'].startswith('https://nondubito.net/essays/war/'))
    href=node.attrs.get('href')
    if not href:continue
    u=urlsplit(html.unescape(href))
    if u.scheme or u.netloc or not u.path:continue
    self.assertTrue((p.parent/unquote(u.path)).resolve().exists(),(str(p),href))
   if p.parent.name in full.LANGS and p.stem!='index':
    citations=one(doc.root.walk(),lambda n:n.has('essay-footer-note'),str(p))
    self.assertEqual(sum(n.tag=='a' for n in citations.walk()),3 if p.stem.startswith('ep') else 2,str(p))
    self.assertNotIn('onclick="localStorage.setItem',text)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--release',action='store_true');a=parser.parse_args()
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(WarPreflight)
 if a.release:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(WarRelease))
 else:print('PREFLIGHT ONLY: incomplete manuscripts and independent review are not certified.')
 raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
