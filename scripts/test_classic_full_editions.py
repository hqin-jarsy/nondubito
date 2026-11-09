#!/usr/bin/env python3
"""Structural regressions for reviewed classical essays, not translation scoring."""
import copy
import hashlib
import html
import json
import re
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit,unquote
import build_classic_full_editions as build
from prepare_action_sources import Document,Node,one

SERIES='sae-nicomachean'
class ClassicFullEditions(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.receipt=build.preserved(SERIES)
  cls.slugs=list(cls.receipt['source_bodies'])
  cls.output=build.render(SERIES)
 def test_full_inventory_and_saved_output(self):
  self.assertEqual(len(self.slugs),13)
  self.assertEqual(len(self.output),84)
  for path,value in self.output.items():self.assertEqual(path.read_text(),value,str(path))
  for lang in build.LANGS:
   self.assertTrue((build.base(SERIES)/'translations'/lang/'index.json').exists())
   for batch in ('01','02','03'):
    report=build.read_json(build.base(SERIES)/'reviews'/(lang+'-batch'+batch+'.json'))
    self.assertEqual(report['language'],lang)
 def test_source_and_traditional_preservation(self):
  self.assertEqual(sum(x['units'] for x in self.receipt['source_bodies'].values()),778)
  for name,digest in self.receipt['traditional_files'].items():
   if name.endswith('/index.js'):continue
   self.assertEqual(hashlib.sha256((build.ROOT/name).read_bytes()).hexdigest(),self.receipt.get('updated_traditional_files',{}).get(name,digest))
  index=(build.folder(SERIES)/'index.html').read_text()
  self.assertIn(build.ZH_NOTE,index)
  self.assertIn(build.HANT_NOTE,(build.folder(SERIES)/'zh-hant-data/index.js').read_text())
 def test_traditional_browser_title_maps_updated_english_titles(self):
  for slug in self.slugs:
   text=self.output[build.folder(SERIES)/(slug+'.html')]
   title=html.unescape(re.search(r'<title>(.*?)</title>',text,re.S)[1])
   raw=(build.folder(SERIES)/'zh-hant-data'/(slug+'.js')).read_text()
   variants=json.loads(re.search(r'var variants = (\{.*?\});',raw)[1])
   self.assertIn(title,variants)
 def test_exact_complete_rendered_bodies(self):
  for lang in build.LANGS:
   for slug in self.slugs:
    a=build.load(SERIES,lang,slug)
    path=build.folder(SERIES)/(lang if lang!='en' else '')/(slug+'.html')
    doc=Document(self.output[path])
    body=one(doc.root.walk(),lambda n:n.has('essay-body') and (lang!='en' or n.has('lang-en')),'body')
    expected=build.translated_links('\n\n'.join(a['body']),lang,build.source(SERIES,slug)[1],build.folder(SERIES))
    self.assertEqual(doc.raw(body,inner=True),expected)
    self.assertEqual(len([n for n in body.children if isinstance(n,Node)]),len(a['body']))
    self.assertNotIn('<section',doc.raw(body))
    self.assertNotIn('<h3',doc.raw(body))
 def test_chrome_language_routes_and_local_targets(self):
  for path,text in self.output.items():
   doc=Document(text)
   self.assertEqual(len([n for n in doc.root.walk() if n.tag=='main']),1)
   self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1)
   canonical='https://nondubito.net/'+path.relative_to(build.ROOT).as_posix().removesuffix('index.html')
   self.assertIn('rel="canonical" href="'+canonical+'"',text)
   menu=one(doc.root.walk(),lambda n:n.has('lang-toggle'),'language menu')
   buttons=[n for n in menu.walk() if n.has('lang-btn')]
   self.assertEqual(len(buttons),8)
   for node in doc.root.walk():
    href=node.attrs.get('href')
    if not href:continue
    u=urlsplit(href)
    if u.scheme or u.netloc:continue
    target=(path.parent/unquote(u.path)).resolve() if u.path else path
    if target.is_dir():target=target/'index.html'
    self.assertTrue(target.is_file(),(path,href))
 def test_translated_titles_decks_and_neighbor_titles(self):
  for lang in build.LANGS:
   directory=build.folder(SERIES)/(lang if lang!='en' else '')
   index=Document(self.output[directory/'index.html'])
   for slug in self.slugs:
    a=build.load(SERIES,lang,slug);text=self.output[directory/(slug+'.html')];doc=Document(text)
    h=one(doc.root.walk(),lambda n:n.tag=='h1' and (lang!='en' or n.has('lang-en')),'title')
    self.assertEqual(h.text(),a['title'])
    card=one(index.root.walk(),lambda n:n.tag=='a' and n.has('entry-row') and n.attrs.get('href')==slug+'.html' and (lang!='en' or any(c.has('entry-title-en') for c in n.walk())),'card')
    self.assertEqual(one(card.walk(),lambda n:n.has('entry-desc'),'deck').text(),a['deck'])
    self.assertIn(html.escape(a['deck'],quote=True),text)
 def test_no_independent_reconstruction_labels(self):
  forbidden=('independent rewrite','independent editorial reconstructions','Eigenständige deutsche Neufassung','日本語独立再構成版','Réécriture française','Versión española reescrita','한국어 재구성판')
  for path,text in self.output.items():
   for phrase in forbidden:self.assertNotIn(phrase,text,(path,phrase))
 def test_independent_english_review_matches_saved_text(self):
  report=build.read_json(build.base(SERIES)/'reviews/independent-english-review.json')
  self.assertEqual(report['paragraphs'],778)
  self.assertEqual(report['unresolved_translation_issues'],[])
  for slug,digest in report['saved_translation_sha256'].items():
   path=build.base(SERIES)/'translations/en'/(slug+'.json')
   self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),digest,slug)
 def test_stale_source_and_missing_unit_are_rejected(self):
  path=build.base(SERIES)/'translations/en/ep01.json';original=build.read_json
  for field in ('source_sha256','body'):
   data=original(path);data[field]='0'*64 if field=='source_sha256' else data['body'][:-1]
   def changed(p):return copy.deepcopy(data) if p==path else original(p)
   with patch.object(build,'read_json',changed),self.assertRaises(AssertionError):build.load(SERIES,'en','ep01')
 def test_english_argument_regressions(self):
  checks={'ep01':('mathematician','orator','meeting','final guarantee','Speusippus'),
   'ep02':('list of names','smallest good','local','ability to stop'),
   'ep03':('One waits for events','Closure of the object','subject of the whole'),
   'ep04':('does not say repetition is necessary','philosophical judgments','Across the many judgments'),
   'ep05':('not four truth values','replaceable','difference of type')}
  for slug,anchors in checks.items():
   body='\n'.join(build.load(SERIES,'en',slug)['body'])
   for anchor in anchors:self.assertIn(anchor,body)
 def test_search_contains_native_titles(self):
  for lang in build.LANGS:
   records=build.read_json(build.ROOT/'data/search'/(lang+'.json'))['records']
   byurl={x['u']:x for x in records}
   for slug in self.slugs:
    path='essays/'+SERIES+'/'+('' if lang=='en' else lang+'/')+slug+'.html'
    self.assertIn(path,byurl)
    self.assertEqual(byurl[path]['t'],build.load(SERIES,lang,slug)['title'])
if __name__=='__main__':unittest.main()
