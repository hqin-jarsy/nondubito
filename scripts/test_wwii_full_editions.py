#!/usr/bin/env python3
"""Structural checks. Passing these is not a semantic review certificate."""
import copy,json,re,unittest
from urllib.parse import urlsplit,unquote
from pathlib import Path
from unittest.mock import patch
import build_wwii_full_editions as b
from prepare_action_sources import Document,Node,one
class WWII(unittest.TestCase):
 def test_baseline_integrity(self):
  manifest=b.read_json(b.DATA/'baseline.json');self.assertEqual(len(manifest['files']),36)
  for name,h in manifest['files'].items():self.assertEqual(b.file_sha(b.DATA/'baseline'/Path(name).relative_to('essays/wwii')),h)
 def test_source_unit_coverage(self):
  expected=[47,51,45,56,54]
  for slug,count in zip(b.SLUGS,expected):
   source=b.source(slug);self.assertEqual(len(source['body']),count)
   for unit in source['body']:
    d=Document(unit);nodes=[n for n in d.root.children if isinstance(n,Node)];self.assertEqual(len(nodes),1);self.assertIn(nodes[0].tag,('p','h2'));self.assertTrue(nodes[0].text().strip())
 def test_drafts_have_no_implicit_completeness(self):
  slug=b.SLUGS[0];s=b.source(slug);fixture=dict(s,language='en',title='Fixture',deck='Fixture',review='Fixture')
  b.validate(fixture,'en',slug)
  for bad in (None,'','<p>TODO</p>','<script>bad()</script>','<p onclick="bad()">Bad</p>'):
   broken=copy.deepcopy(fixture);broken['body'][0]=bad
   with self.assertRaises(AssertionError):b.validate(broken,'en',slug)
  for key,value in [('source_sha256','0'*64),('slug','wrong'),('language','de')]:
   broken=copy.deepcopy(fixture);broken[key]=value
   with self.assertRaises(AssertionError):b.validate(broken,'en',slug)
 def test_all_primary_and_foreign_controls(self):
  for lang in b.LANGS:
   path=b.DATA/'baseline'/('' if lang=='en' else lang)/(b.SLUGS[0]+'.html');text=b.controls(path.read_text(),lang,b.SLUGS[0]);d=Document(text)
   toggle=b.find(d,'lang-toggle');nodes=[n for n in toggle.children if isinstance(n,Node) and n.has('lang-btn')];self.assertEqual(len(nodes),8)
   if lang=='en':
    self.assertEqual(text.count('id="wwii-full-controller"'),1);self.assertEqual([n.attrs.get('data-lang-button') for n in nodes[:3]],['en','zh','zh-hant']);self.assertIn('try{return localStorage',text)
   else:
    self.assertNotIn('onclick=',text);self.assertEqual(len([n for n in nodes if n.attrs.get('aria-current')=='page']),1)
    for code in ('en','zh','zh-hant'):self.assertTrue(any(n.attrs.get('href','').endswith('?lang='+code) for n in nodes))
 def test_final_receipt_blocks_pending_sources(self):
  original=b.read_json
  def read(path):return dict(status='pending',unresolved=['fixture']) if path.name=='source-finalization.json' else original(path)
  with patch.object(b,'read_json',read),self.assertRaises(AssertionError):b.reviewed()
 def test_source_semantic_hashes(self):
  for slug in b.SLUGS:
   source=b.source(slug)
   self.assertEqual(source['source_sha256'],b.digest(json.dumps({k:source[k] for k in ('title','body')},ensure_ascii=False,separators=(',',':'))))
 def test_deterministic_preview_and_routes(self):
  # Synthetic complete units exercise rendering even while actual drafts are pending.
  def fixture(lang,slug):return dict(b.source(slug),language=lang,title=lang+' '+slug,deck='Fixture description',review='Structural fixture, not semantic approval')
  with patch.object(b,'load',fixture):
   outputs=b.render(preview=True);self.assertEqual(outputs,b.render(preview=True))
  self.assertEqual(len(outputs),36)
  for path,text in outputs.items():
   d=Document(text);toggle=b.find(d,'lang-toggle')
   self.assertEqual(len([n for n in toggle.children if isinstance(n,Node) and n.has('lang-btn')]),8)
   self.assertNotIn('zh-hant.js',text)
   canonical=one(d.root.walk(),lambda n:n.tag=='link' and n.attrs.get('rel')=='canonical','canonical').attrs['href']
   self.assertEqual(canonical,'https://nondubito.net/'+str(path.relative_to(b.ROOT)).replace('index.html',''))
   for n in d.root.walk():
    url=n.attrs.get('href') if n.tag in ('a','link') else n.attrs.get('src') if n.tag in ('script','img') else None
    if not url:continue
    parsed=urlsplit(url)
    if parsed.scheme or parsed.netloc or not parsed.path:continue
    target=(b.ROOT/unquote(parsed.path.lstrip('/')) if parsed.path.startswith('/') else path.parent/unquote(parsed.path)).resolve()
    if parsed.path.endswith('/'):target/='index.html'
    self.assertTrue(target in outputs or target.exists(),(path,url))
    if parsed.fragment and target.suffix=='.html':
     target_text=outputs.get(target) or target.read_text()
     self.assertTrue(re.search(r'(?:id|name)=[\"\']'+re.escape(unquote(parsed.fragment))+r'[\"\']',target_text),(path,url,'missing fragment'))
   if path.name=='index.html' and path.parent==b.DIRECTORY:
    for code in ('en','zh','hant'):
     body=one(d.root.walk(),lambda n:n.has('essay-body') and n.has('lang-'+code),'index body')
     self.assertEqual(len([n for n in body.walk() if n.has('essay-card')]),5)
   self.assertEqual(text.count('static.cloudflareinsights.com/beacon.min.js'),1)
 def test_preview_cannot_overwrite_repository(self):
  for path in (b.ROOT,b.DIRECTORY,b.ROOT/'data/preview'):
   with patch('sys.argv',['build','--preview',str(path)]),patch.object(b,'render',return_value={}):
    with self.assertRaisesRegex(AssertionError,'outside the repository'):b.main()
 def test_final_review_and_output(self):
  if not (b.DATA/'source-finalization.json').exists():self.skipTest('Source finalization still pending')
  if b.read_json(b.DATA/'source-finalization.json')['status']!='approved':self.skipTest('Source questions pending')
  if not all((b.DATA/'reviews'/(l+'.json')).exists() for l in b.LANGS+('zh-Hant',)):self.skipTest('Independent reviews pending')
  items=b.reviewed();self.assertEqual(len(items),35);outputs=b.render();self.assertEqual(len(outputs),36)
  for path,text in outputs.items():
   d=Document(text);self.assertEqual(text.count('static.cloudflareinsights.com/beacon.min.js'),1);self.assertNotIn('PENDING',text)
   for n in d.root.walk():
    if n.has('essay-body'):self.assertFalse(any(x.tag=='h3' for x in n.walk()))
   if path.name!='index.html':
    lang=path.parent.name if path.parent.name in b.LANGS[1:] else 'en';slug=path.stem
    if lang=='en':
     for cls,code in [('lang-en','en'),('lang-zh',None),('lang-hant','zh-Hant')]:
      body=one(d.root.walk(),lambda n:n.has('essay-body') and n.has(cls),cls);units=[n for n in body.children if isinstance(n,Node)];self.assertEqual(len(units),len(b.source(slug)['body']))
    else:self.assertEqual(len([n for n in b.find(d,'essay-body').children if isinstance(n,Node)]),len(b.source(slug)['body']))
if __name__=='__main__':unittest.main()
