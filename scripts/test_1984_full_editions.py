#!/usr/bin/env python3
"""Structural safeguards for the complete Orwell essays, not translation scoring."""
import copy
import hashlib
import html
import json
import re
import unittest
from unittest.mock import patch
from urllib.parse import unquote,urlsplit
import build_1984_full_editions as build
from prepare_action_sources import Document,Node,one

class OrwellFullEditions(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.receipt=build.preserved();cls.slugs=list(cls.receipt['source_bodies']);cls.output=build.render()
 def test_inventory_and_saved_pages(self):
  self.assertEqual(len(self.slugs),4);self.assertEqual(len(self.output),30)
  self.assertEqual(sum(x['units'] for x in self.receipt['source_bodies'].values()),422)
  self.assertEqual(sum(x['paragraphs'] for x in self.receipt['source_bodies'].values()),390)
  self.assertEqual(sum(x['headings'] for x in self.receipt['source_bodies'].values()),32)
  for path,text in self.output.items():self.assertEqual(path.read_text(),text,str(path))
  for lang in build.LANGS:
   report=build.read_json(build.DATA/'reviews'/(lang+'-batch01.json'))
   self.assertEqual(report['language'],lang)
 def test_source_snapshots_and_approved_bodies(self):
  for slug in self.slugs:
   snapshot=build.read_json(build.DATA/'sources'/(slug+'.json'));raw,units=build.source(slug)
   self.assertEqual(snapshot['body'],units);self.assertEqual(snapshot['source_sha256'],build.sha(raw))
  for path,digest in self.receipt['traditional_files'].items():
   self.assertEqual(hashlib.sha256((build.ROOT/path).read_bytes()).hexdigest(),self.receipt.get('updated_traditional_files',{}).get(path,digest))
 def test_exact_complete_translation_bodies(self):
  for lang in build.LANGS:
   for slug in self.slugs:
    item=build.load(lang,slug);path=build.DIRECTORY/('' if lang=='en' else lang)/(slug+'.html')
    doc=Document(self.output[path]);body=one(doc.root.walk(),lambda n:n.has('essay-body') and (lang!='en' or n.has('lang-en')),'body')
    units=[n for n in body.children if isinstance(n,Node) and n.tag in ('p','h2')]
    self.assertEqual([doc.raw(n) for n in units],item['body'])
    self.assertEqual(len(units),len(item['body']))
    if lang!='en':self.assertEqual(len([n for n in body.children if isinstance(n,Node) and n.has('series-nav')]),1)
 def test_titles_cards_decks_and_shared_intro(self):
  for lang in build.LANGS:
   folder=build.DIRECTORY/('' if lang=='en' else lang);index=Document(self.output[folder/'index.html'])
   section=one(index.root.walk(),lambda n:n.has('essay-body','lang-en'),'index') if lang=='en' else one(index.root.walk(),lambda n:n.tag=='main','index')
   self.assertEqual(one(index.root.walk(),lambda n:n.tag=='h1' and (lang!='en' or n.has('lang-en')),'index title').text(),build.shared(lang)['title'])
   for intro in build.shared(lang)['intro']:self.assertIn(intro,self.output[folder/'index.html'])
   for slug in self.slugs:
    item=build.load(lang,slug);doc=Document(self.output[folder/(slug+'.html')])
    title=one(doc.root.walk(),lambda n:n.tag=='h1' and (lang!='en' or n.has('lang-en')),'title')
    self.assertEqual(title.text(),item['title'])
    card=one(section.walk(),lambda n:n.tag=='a' and n.attrs.get('href')==slug+'.html','card')
    self.assertEqual(one(card.walk(),lambda n:n.has('card-desc') or n.has('entry-desc'),'deck').text(),item['deck'])
    self.assertIn(html.escape(item['deck'],quote=True),self.output[folder/(slug+'.html')])
 def test_canonical_analytics_and_local_assets(self):
  for path,text in self.output.items():
   doc=Document(text);self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1)
   canonical='https://nondubito.net/'+path.relative_to(build.ROOT).as_posix().removesuffix('index.html')
   self.assertIn('rel="canonical" href="'+canonical+'"',text)
   for node in doc.root.walk():
    for attr in ('href','src'):
     value=node.attrs.get(attr)
     if not value:continue
     u=urlsplit(value)
     if u.scheme or u.netloc:continue
     target=(path.parent/unquote(u.path)).resolve() if u.path else path
     if target.is_dir():target=target/'index.html'
     self.assertTrue(target.is_file(),(path,value))
 def test_eight_language_routes_and_storage_safety(self):
  for path,text in self.output.items():
   doc=Document(text);menu=one(doc.root.walk(),lambda n:n.has('lang-toggle'),'language menu')
   controls=[n for n in menu.walk() if n.has('lang-btn')];self.assertEqual(len(controls),8)
   if path.parent==build.DIRECTORY:
    self.assertIn('src="'+build.READER+'"',text)
    self.assertNotIn('var saved=localStorage.getItem',text)
   else:
    self.assertNotIn('onclick="localStorage',text)
    for lang in ('en','zh','zh-hant'):self.assertIn('../'+path.name+'?lang='+lang,text)
 def test_neighbor_navigation_stays_in_edition(self):
  for lang in build.LANGS:
   folder=build.DIRECTORY/('' if lang=='en' else lang)
   for i,slug in enumerate(self.slugs):
    doc=Document(self.output[folder/(slug+'.html')]);nav=one(doc.root.walk(),lambda n:n.has('essay-nav') or n.has('series-nav'),'article nav')
    targets=[n.attrs['href'] for n in nav.walk() if n.tag=='a']
    expected=[]
    if i:expected.append(self.slugs[i-1]+'.html')
    if i+1<len(self.slugs):expected.append(self.slugs[i+1]+'.html')
    elif lang in ('en','ja'):expected.append('index.html')
    self.assertEqual(targets,expected)
 def test_traditional_titles_remain_accessible(self):
  for slug in ['index']+self.slugs:
   raw=(build.DIRECTORY/'zh-hant-data'/(slug+'.js')).read_text()
   variants=json.loads(re.search(r'var variants = (\{.*?\});',raw)[1])
   title=html.unescape(re.search(r'<title>(.*?)</title>',self.output[build.DIRECTORY/(slug+'.html')],re.S)[1])
   self.assertIn(title,variants,slug)
 def test_reconstruction_labels_removed(self):
  forbidden=('Independent English edition','independent English rewriting','eigenständige deutsche Neufassung','réécriture autonome','reescritura independiente','独立再構成','독립적인 재구성')
  for path,text in self.output.items():
   for phrase in forbidden:self.assertNotIn(phrase,text,(path,phrase))
 def test_stale_source_missing_unit_and_wrong_boundary_rejected(self):
  path=build.DATA/'translations/en'/(self.slugs[0]+'.json');original=build.read_json
  data=original(path)
  changes=[dict(data,source_sha256='0'*64),dict(data,body=data['body'][:-1])]
  body=list(data['body']);body[1]=body[1].replace('<p>','<h2>').replace('</p>','</h2>');changes.append(dict(data,body=body))
  for changed in changes:
   def replacement(p):return copy.deepcopy(changed) if p==path else original(p)
   with patch.object(build,'read_json',replacement),self.assertRaises(AssertionError):build.load('en',self.slugs[0])
 def test_search_titles_and_article_descriptions(self):
  for lang in build.LANGS:
   records=build.read_json(build.ROOT/'data/search'/(lang+'.json'))['records'];urls={r['u']:r for r in records}
   for slug in ['index']+self.slugs:
    key='essays/literature/nineteen-eighty-four/'+('' if lang=='en' else lang+'/')+slug+'.html'
    item=build.shared(lang) if slug=='index' else build.load(lang,slug)
    self.assertEqual(urls[key]['t'],item['title'])
    if slug!='index':self.assertEqual(urls[key]['x'],item['deck'])
 def test_approved_source_amendments_are_exact_and_reversible(self):
  changes=build.read_json(build.DATA/'reviews/approved-source-changes.json')
  self.assertEqual(changes['status'],'applied')
  self.assertEqual(len(changes['changes']),31)
  self.assertEqual(self.receipt['approved_source_amendment']['status'],'applied')
  self.assertEqual(set(changes['source_hashes']),set(self.slugs))
  for slug in self.slugs:
   raw,units=build.source(slug);restored=raw
   hashes=changes['source_hashes'][slug]
   self.assertEqual(build.sha(raw),hashes['new'])
   self.assertEqual(hashes['old'],self.receipt['approved_source_amendment']['original_source_bodies'][slug]['sha256'])
   for change in changes['changes']:
    if change['essay']!=slug:continue
    self.assertEqual(units[change['unit_1based']-1],change['new_html'])
    self.assertEqual(restored.count(change['new_html']),1)
    self.assertEqual(re.findall(r'</?(?:p|h2|strong|em)\b[^>]*>',change['old_html']),re.findall(r'</?(?:p|h2|strong|em)\b[^>]*>',change['new_html']))
    restored=restored.replace(change['new_html'],change['old_html'],1)
   self.assertEqual(build.sha(restored),hashes['old'],(slug,'unrecorded Chinese change'))
 def test_changed_chinese_text_nodes_have_traditional_mappings(self):
  changes=build.read_json(build.DATA/'reviews/approved-source-changes.json')
  dictionaries={}
  for slug in self.slugs:
   text=(build.DIRECTORY/'zh-hant-data'/(slug+'.js')).read_text()
   dictionaries[slug]=json.loads(re.search(r'var variants = (\{.*?\});',text)[1])
  for change in changes['changes']:
   for node in Document(change['new_html']).root.walk():
    for child in node.children:
     if isinstance(child,str) and re.search(r'[\u4e00-\u9fff]',child):
      self.assertIn(child.strip(),dictionaries[change['essay']],(change['essay'],change['unit_1based'],child))
 def test_translations_preserve_all_emphasis_sequences(self):
  for lang in build.LANGS:
   for slug in self.slugs:
    _,units=build.source(slug);item=build.load(lang,slug)
    for i,(original,translated) in enumerate(zip(units,item['body']),1):
     self.assertEqual(re.findall(r'</?(?:p|h2|strong|em)\b[^>]*>',original),re.findall(r'</?(?:p|h2|strong|em)\b[^>]*>',translated),(lang,slug,i))
 def test_independent_reviews_and_final_amendment_seals(self):
  historical=build.read_json(build.DATA/'reviews/independent-english-review.json')
  self.assertEqual(historical['source_units'],422)
  self.assertEqual(historical['unresolved_translation_issues'],[])
  self.assertEqual(set(historical['saved_translation_sha256']),set(self.slugs))
  final=build.read_json(build.DATA/'reviews/independent-approved-amendment-review.json')
  self.assertEqual(final['unresolved_translation_issues'],[])
  self.assertEqual(set(final['saved_translation_sha256']),set(build.LANGS))
  for lang,hashes in final['saved_translation_sha256'].items():
   self.assertEqual(set(hashes),set(self.slugs))
   for slug,digest in hashes.items():
    self.assertEqual(hashlib.sha256((build.DATA/'translations'/lang/(slug+'.json')).read_bytes()).hexdigest(),digest)
if __name__=='__main__':unittest.main()
