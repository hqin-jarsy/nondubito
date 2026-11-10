#!/usr/bin/env python3
"""Value Theory restoration safeguards. --release adds complete-edition checks."""
import argparse,copy,hashlib,html,json,re,unittest,tempfile,sys,subprocess,os
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit,unquote
import build_value_full_editions as full
from prepare_action_sources import Document,Node,one

class ValuePreflight(unittest.TestCase):
 def test_chinese_traditional_and_english_baselines(self):
  record=full.preserved()
  self.assertEqual(sum(r['units'] for r in record['source_bodies'].values()),1097)
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
  target=full.BASE/'translations/de/prequel.json';data=full.read(target);data=copy.deepcopy(data);data['body']=data['body'][:-1];original=full.read
  with patch.object(full,'read',lambda p:data if p==target else original(p)):
   with self.assertRaisesRegex(AssertionError,'unit coverage'):full.load('de','prequel')
 def test_loader_rejects_stale_source(self):
  target=full.BASE/'translations/de/prequel.json';data=full.read(target);data=copy.deepcopy(data);data['source_sha256']='stale';original=full.read
  with patch.object(full,'read',lambda p:data if p==target else original(p)):
   with self.assertRaisesRegex(AssertionError,'stale source'):full.load('de','prequel')
 def test_table_shape_detects_missing_cells(self):
  self.assertNotEqual(full.structure('<div><table><tr><td>A</td><td>B</td></tr></table></div>'),full.structure('<div><table><tr><td>A</td></tr></table></div>'))
 def test_english_patches_are_local_and_source_bound(self):
  for slug in full.SLUGS:
   body=full.english_body(slug);doc=Document(body);units=[doc.raw(n) for n in doc.root.children if isinstance(n,Node)]
   source=full.read(full.BASE/'sources'/(slug+'.json'))
   self.assertEqual(len(units),len(source['body_en']))
   p=full.BASE/'reviews'/('en-'+slug+'.json');r=full.read(p) if p.exists() else {};changes={x['unit']-1:x['after'] for x in r.get('changes',[])}
   self.assertEqual(units,[changes.get(i,u) for i,u in enumerate(source['body_en'])])


 def test_optimized_python_rejected_on_module_import(self):
  code='import sys;sys.path.insert(0,'+repr(str(full.ROOT/'scripts'))+');import build_value_full_editions'
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
    full.preview_destinations(directory,{full.DIRECTORY/'fr/prequel.html':'draft'})
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
  original=full.read
  sources={slug:original(full.BASE/'sources'/(slug+'.json')) for slug in full.SLUGS}
  for fault in ('source','translation'):
   receipt={'language':'ja','status':'passed','independent':True,'all_units_read':True,'unresolved':[],
    'source_sha256s':{slug:sources[slug]['source_sha256'] for slug in full.SLUGS},
    'translation_sha256s':{slug:'current-translation-hash' for slug in full.SLUGS}}
   if fault=='source':receipt['source_sha256s']['prequel']='stale'
   else:receipt['translation_sha256s']['prequel']='stale'
   with self.subTest(fault=fault),patch.object(full,'file_sha',return_value='current-translation-hash'),patch.object(full,'read',lambda p:receipt if p==full.BASE/'reviews/ja.json' else original(p)):
    with self.assertRaisesRegex(AssertionError,fault+' review stale'):full.verify_reviews()
 def test_discovery_refuses_stale_public_pages_before_building(self):
  import refresh_value_full_discovery as discovery
  outputs={full.DIRECTORY/('test'+str(i)+'.html'):'reviewed' for i in range(54)}
  with patch.object(full,'render',return_value=outputs),patch.object(Path,'read_text',return_value='stale'),patch.object(discovery.search,'build') as build:
   with self.assertRaisesRegex(ValueError,'Render reviewed public pages'):discovery.outputs()
   build.assert_not_called()


class ValueRelease(unittest.TestCase):
 def test_current_independent_receipts_and_complete_manuscripts(self):
  full.verify_reviews()
  for lang in full.LANGS:
   for slug in full.SLUGS:full.load(lang,slug)
 def test_generated_pages_are_current_and_full(self):
  outputs=full.render();self.assertEqual(len(outputs),54)
  for p,text in outputs.items():
   self.assertEqual(p.read_text(),text,str(p))
   if p.stem=='index':continue
   doc=Document(text);lang=p.parent.name if p.parent!=full.DIRECTORY else 'en'
   node=one(doc.root.walk(),lambda n:n.has('essay-body') and (lang!='en' or n.has('lang-en')),str(p))
   units=full.raw_units(doc,node)
   expected=full.read(full.BASE/'sources'/(p.stem+'.json'))['body_zh']
   self.assertEqual(len(units),len(expected),(lang,p.stem))
   if lang!='en':self.assertEqual(units,full.load(lang,p.stem)['body'])
 def test_links_eight_languages_citations_and_analytics(self):
  for p,text in full.render().items():
   doc=Document(text)
   toggles=[n for n in doc.root.walk() if n.has('lang-btn')]
   self.assertEqual(len(toggles),8,str(p))
   self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1,str(p))
   self.assertIn('1c920752456e42b5b5469641245a07c2',text)
   self.assertEqual(text.count('id="value-full-reader"'),1)
   for node in doc.root.walk():
    if node.tag=='link' and node.attrs.get('rel')=='canonical':self.assertTrue(node.attrs['href'].startswith('https://nondubito.net/essays/sae-value/'))
    href=node.attrs.get('href')
    if not href:continue
    u=urlsplit(html.unescape(href))
    if u.scheme or u.netloc or not u.path:continue
    self.assertTrue((p.parent/unquote(u.path)).resolve().exists(),(str(p),href))
   if p.parent.name in full.LANGS and p.stem!='index':
    citations=one(doc.root.walk(),lambda n:n.has('value-full-citations'),str(p))
    self.assertEqual(sum(n.tag=='a' for n in citations.walk()),2,str(p))
    self.assertNotIn('onclick="localStorage.setItem',text)
 def test_discovery_scope_and_search(self):
  import refresh_value_full_discovery as discovery
  for path,value in discovery.outputs().items():self.assertEqual(path.read_text(),value,str(path))
  for lang in full.LANGS:
   records=full.read(full.ROOT/f'data/search/{lang}.json')['records'];urls={r['u'] for r in records}
   for slug in ('index',*full.SLUGS):self.assertIn(f'essays/sae-value/{lang}/{slug}.html',urls)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--release',action='store_true');a=parser.parse_args()
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(ValuePreflight)
 if a.release:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ValueRelease))
 else:print('PREFLIGHT ONLY: incomplete manuscripts and independent review are not certified.')
 raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
