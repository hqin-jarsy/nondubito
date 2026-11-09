#!/usr/bin/env python3
"""Structural safeguards and in-memory rendering tests, NOT semantic certification."""
import copy,html,json,re,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from urllib.parse import urlsplit,unquote
import build_relationships_full_editions as b
from prepare_action_sources import Document,Node,one

class RelationshipsFull(unittest.TestCase):
 def test_sources_and_preservation(self):
  r=b.preserved();self.assertEqual(len(b.slugs()),30)
  self.assertEqual(sum(len(b.source(s)['body']) for s in b.slugs()),1237)
  self.assertEqual(len(r['files']),186)
  for slug in b.slugs():
   s=b.source(slug)
   for lang in ('zh','hant'):
    e=s['languages'][lang];self.assertEqual(b.sha(e['body_html']),e['source_sha256'])
    self.assertEqual(len(e['body']),len(s['body']))
    for unit in e['body']:self.assertEqual(Document(unit).root.children[0].tag,'p')
 def test_safe_paragraphs(self):
  b.validate_inline('<p><em>A</em> <strong>B</strong></p>','<p><em>甲</em> <strong>乙</strong></p>',True)
  for bad in ('<p>A</p><p>B</p>','<h2>A</h2>','<p onclick="x()">A</p>','<p>TODO</p>','<p></p>','Loose<p>A</p>'):
   with self.subTest(bad=bad),self.assertRaises(AssertionError):b.validate_inline(bad,'<p>甲</p>',True)
  with self.assertRaises(AssertionError):b.validate_inline('<p>A</p>','<p><strong>甲</strong></p>',True)
 def test_inline_rejects_nested_paragraphs_and_missing_targets(self):
  for value,original in [('<p>A<p>B</p></p>','<p>甲乙</p>'),
                         ('<p><a>A</a></p>','<p><a href="a.html">甲</a></p>'),
                         ('<p><!-- hidden -->A</p>','<p>甲</p>'),
                         ('<p><a href="javascript:alert(1)">A</a></p>','<p><a href="a.html">甲</a></p>')]:
   with self.subTest(value=value),self.assertRaises(AssertionError):b.validate_inline(value,original,True)
 def test_links_restore_source_with_all_quoting_and_query(self):
  original=['<p><a href="target.html?lang=en&amp;ref=source#part">甲</a></p>']
  for draft in ["<p><a href='wrong.html'>A</a></p>",'<p><a href=wrong.html>A</a></p>']:
   with patch.object(Path,'is_file',return_value=True):result=b.translated_links(draft,'de',original,b.DIRECTORY)
   anchor=one(Document(result).root.walk(),lambda n:n.tag=='a','link')
   self.assertEqual(anchor.attrs['href'],'target.html?lang=en&ref=source#part')
   with patch.object(Path,'is_file',return_value=False):result=b.translated_links(draft,'de',original,b.DIRECTORY)
   self.assertEqual(one(Document(result).root.walk(),lambda n:n.tag=='a','link').attrs['href'],'../target.html?lang=en&ref=source#part')
 def test_review_hashes_use_exact_bytes(self):
  target=Mock();target.read_bytes.return_value=b'line\r\n'
  self.assertEqual(b.file_sha(target),b.hashlib.sha256(b'line\r\n').hexdigest())
  self.assertNotEqual(b.file_sha(target),b.sha('line\n'))
 def test_batch_receipt_gates(self):
  names={f'{lang}/{slug}.json' for lang in b.LANGS for slug in b.slugs()[:5]}
  receipt=dict(episodes=list(range(1,6)),status='reviewed',independent_semantic_review=True,
               review_scope='Fixture structural tests, not actual acceptance',reviewer='TEST',limitations='TEST ONLY',
               translation_sha256={name:b.file_sha(b.DATA/'translations'/name) for name in names})
  original_read=b.read_json;original_glob=Path.glob;receipt_path=b.DATA/'reviews/batch01.json'
  def glob(path,pattern):return iter([receipt_path]) if path==b.DATA/'reviews' and pattern=='batch*.json' else original_glob(path,pattern)
  def read(path):return receipt if path==receipt_path else original_read(path)
  with patch.object(Path,'glob',glob),patch.object(b,'read_json',side_effect=read):
   self.assertEqual(len(b.reviewed()),30)
   with self.assertRaises(AssertionError):b.reviewed(complete=True)
   receipt['independent_semantic_review']=False
   with self.assertRaises(AssertionError):b.reviewed()
   receipt['independent_semantic_review']=True
   name=next(iter(names));old=receipt['translation_sha256'][name];receipt['translation_sha256'][name]='0'*64
   with self.assertRaises(AssertionError):b.reviewed()
   receipt['translation_sha256'][name]=old;receipt['translation_sha256'].pop(name)
   with self.assertRaises(AssertionError):b.reviewed()
 def test_discovery_date_is_stable(self):
  import refresh_relationships_full_discovery as discovery
  self.assertEqual(discovery.PUBLICATION_DATE,'2026-11-09')
  with patch.object(discovery.full,'reviewed',return_value={}),patch.object(discovery.full,'render',return_value={}):
   self.assertEqual(discovery.outputs(),{})
   with self.assertRaises(ValueError):discovery.outputs('invalid-date')
 def test_discovery_preserves_unrelated_records_and_dates(self):
  import refresh_relationships_full_discovery as discovery
  for lang,path in [('en',b.page('en',b.slugs()[0])),('en',b.page('en','index')),('de',b.page('de','index'))]:
   key=path.relative_to(b.ROOT).as_posix()
   chunk_path=discovery.search.CHUNKS_DIR/(lang+'.json');before=b.read_json(chunk_path)
   existing=next(r for r in before['records'] if r['u']==key)
   updated=dict(existing,t='TEST fixture title',x='TEST fixture deck')
   with patch.object(discovery.full,'reviewed',return_value={}),patch.object(discovery.full,'render',return_value={path:path.read_text()}),patch.object(discovery.search,'build',return_value=({}, {lang:[updated]})):
    outputs=discovery.outputs()
   after=json.loads(outputs[chunk_path])
   self.assertEqual([r for r in before['records'] if r['u']!=key],[r for r in after['records'] if r['u']!=key])
   self.assertEqual(next(r for r in after['records'] if r['u']==key),updated)
   ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
   def entries(root):return {node.find(ns+'loc').text:node.find(ns+'lastmod').text for node in root}
   original=entries(discovery.ET.parse(b.ROOT/'sitemap.xml').getroot())
   result=entries(discovery.ET.fromstring(outputs[b.ROOT/'sitemap.xml']))
   canonical=discovery.parse_page(path).canonical
   if path.name=='index.html':self.assertTrue(canonical.endswith('/'),canonical)
   self.assertEqual({k:v for k,v in original.items() if k!=canonical},{k:v for k,v in result.items() if k!=canonical})
   self.assertEqual(result[canonical],max(original.get(canonical,discovery.PUBLICATION_DATE),discovery.PUBLICATION_DATE))
 def test_in_memory_all_language_shells(self):
  slug=b.slugs()[0];s=b.source(slug)
  # Synthetic fixture explicitly copied from source: checks renderer only.
  fixtures={(lang,slug):dict(s,language=lang,title='Fixture & Title',deck='Fixture deck',review='TEST ONLY',chapter='Fixture chapter') for lang in b.LANGS}
  original_load=b.load
  with patch.object(b,'load',side_effect=lambda l,s:fixtures[l,s] if (l,s) in fixtures else original_load(l,s)):outputs=b.render(preview=list(fixtures))
  for lang in b.LANGS:
   path=b.page(lang,slug);text=outputs[path];region=b.region(text,'en') if lang=='en' else text
   d=Document(region);body=b.find(d,'article-body');self.assertEqual(len([n for n in body.children if isinstance(n,Node)]),len(s['body']))
   self.assertEqual(one(d.root.walk(),lambda n:n.tag=='h1','title').text(),'Fixture & Title')
   self.assertEqual(text.count('static.cloudflareinsights.com/beacon.min.js'),1)
   self.assertIn('calc(54px +',text)
   self.assertIn('.article-head h1,.essay-card h3,.series-hero h1{hyphens:auto;-webkit-hyphens:auto}',text)
   self.assertEqual(b.controls(b.controls(text,lang),lang),b.controls(text,lang))
   allnodes=Document(text);toggle=b.find(allnodes,'lang-toggle');links=[n for n in toggle.walk() if n.tag=='a']
   self.assertEqual(len(links),5 if lang=='en' else 7)
   for n in allnodes.root.walk():
    if n.tag!='a' or not n.attrs.get('href'):continue
    u=urlsplit(n.attrs['href'])
    if u.scheme or not u.path or u.path.startswith('/'):continue
    self.assertTrue((path.parent/unquote(u.path)).resolve().exists(),(path,n.attrs['href']))
   if lang=='en':
    for l in ('zh','hant'):self.assertEqual(b.region(text,l),b.region(path.read_text(),l))
    self.assertIn("try{return localStorage.getItem",text)
    self.assertIn("history.replaceState",text)
   else:self.assertNotIn('onclick="localStorage.setItem',text)
   index=outputs[b.page(lang,'index')];idr=b.region(index,'en') if lang=='en' else index
   card=one(Document(idr).root.walk(),lambda n:n.has('essay-card') and n.attrs['href']==slug+'.html','card')
   self.assertIn('Fixture & Title',card.text());self.assertIn('Fixture deck',card.text())
 def test_route_repair_preserves_all_card_prose(self):
  text=b.source('index')['languages']['zh']['region_html'];fixed=b.index_region(text,{},fix_routes=True)
  a=Document(text);d=Document(fixed)
  self.assertEqual([int(Path(n.attrs['href']).stem[:2]) for n in b.find(d,'route-links').walk() if n.tag=='a'],list(b.ROUTE))
  self.assertEqual([a.raw(n) for n in a.root.walk() if n.has('essay-card')],[d.raw(n) for n in d.root.walk() if n.has('essay-card')])
  self.assertEqual(fixed,b.index_region(fixed,{},fix_routes=True))
 def test_existing_drafts_are_structural_only(self):
  for lang in b.LANGS:
   for p in (b.DATA/'translations'/lang).glob('*.json'):
    with self.subTest(path=p):b.load(lang,p.stem)
 def test_every_available_draft_renders_exact_full_body(self):
  keys=[(lang,p.stem) for lang in b.LANGS for p in (b.DATA/'translations'/lang).glob('[0-9]*.json')]
  outputs=b.render(preview=keys)
  for lang,slug in keys:
   item=b.load(lang,slug);path=b.page(lang,slug);text=outputs[path]
   region=b.region(text,'en') if lang=='en' else text
   doc=Document(region);body=b.find(doc,'article-body')
   expected=b.translated_links('\n'.join(item['body']),lang,b.source(slug)['body'],b.DIRECTORY)
   self.assertEqual([doc.raw(n) for n in body.children if isinstance(n,Node)],
                    [Document(expected).raw(n) for n in Document(expected).root.children if isinstance(n,Node)])
   self.assertEqual(one(doc.root.walk(),lambda n:n.tag=='h1','title').text(),item['title'])
   self.assertEqual(b.find(doc,'chapter-label').text(),item['chapter'])
   for node in b.find(doc,'series-nav').walk():
    if node.tag!='a':continue
    target=Path(node.attrs.get('href','')).stem
    if (lang,target) in keys:self.assertIn(b.load(lang,target)['title'],node.text())

   door=b.translated_links(item['entry_door'],lang,[b.source(slug)['entry_door']],b.DIRECTORY)
   self.assertEqual(doc.raw(b.find(doc,'entry-door'),inner=True),door)
   self.assertIn(html.escape(item['deck'],quote=True),text)
   self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1)
   if lang=='en':
    for l in ('zh','hant'):self.assertEqual(b.region(text,l),b.region(path.read_text(),l))
 def test_stale_source_and_missing_paragraph_rejected(self):
  paths=list((b.DATA/'translations/en').glob('[0-9]*.json'))
  if not paths:self.skipTest('No English drafts yet')
  p=sorted(paths)[0];original=b.read_json;item=original(p)
  for changed in (dict(item,source_sha256='0'*64),dict(item,body=item['body'][:-1])):
   def replacement(path):return copy.deepcopy(changed) if path==p else original(path)
   with patch.object(b,'read_json',side_effect=replacement),self.assertRaises(AssertionError):b.load('en',p.stem)
 def test_all_chinese_bodies_remain_verbatim(self):
  for slug in b.slugs():
   text=b.page('en',slug).read_text()
   for lang in ('zh','hant'):
    self.assertEqual(b.region(text,lang),b.source(slug)['languages'][lang]['region_html'])
 def test_index_draft_preview_is_explicit_and_complete(self):
  with self.assertRaises(AssertionError):b.render(preview_index=True)
  with self.assertRaises(AssertionError):b.render(complete=True,preview=[])
  outputs=b.render(preview=[],preview_index=True)
  for lang in b.LANGS:
   if not (b.DATA/'translations'/lang/'index.json').exists():continue
   item=b.load(lang,'index');path=b.page(lang,'index');text=outputs[path]
   raw=b.region(text,'en') if lang=='en' else text;doc=Document(raw)
   self.assertEqual(one(doc.root.walk(),lambda n:n.tag=='h1','title').text(),item['title'])
   self.assertEqual(b.find(doc,'series-deck').text(),item['deck'])
   route=b.find(doc,'reading-route');door=b.find(doc,'theory-door')
   self.assertEqual(one(route.walk(),lambda n:n.tag=='h2','route title').text(),item['route_title'])
   self.assertEqual(one(route.walk(),lambda n:n.tag=='p','route intro').text(),item['route_intro'])
   self.assertEqual(one(door.walk(),lambda n:n.tag=='span','theory label').text(),item['theory_label'])
   expected=b.translated_links(item['theory_intro'],lang,[b.source('index')['theory_intro']],b.DIRECTORY)
   self.assertEqual(doc.raw(one(door.walk(),lambda n:n.tag=='p','theory intro'),inner=True),expected)
   self.assertIn('<title>'+html.escape(item['title']+' — Non Dubito',quote=True)+'</title>',text)

   heads=[n for n in doc.root.walk() if n.has('chapter-head')]
   self.assertEqual([one(n.walk(),lambda t:t.tag=='h2','chapter').text() for n in heads],item['chapters'])
   if lang=='en':
    for l in ('zh','hant'):self.assertEqual(b.region(text,l),b.region(path.read_text(),l))
 def test_pending_source_publication_requires_explicit_preservation(self):
  original=(b.DATA/'pending-source-decisions.json').read_bytes()
  target=Mock();target.read_text.return_value='old public HTML'
  decisions={'status':'pending author decision; do not apply'}
  with patch.object(b,'render',return_value={target:'reviewed translation'}),patch.object(b,'read_json',return_value=decisions),patch('sys.argv',['build_relationships_full_editions.py']):
   with self.assertRaises(AssertionError):b.main()
  target.write_text.assert_not_called()
  with patch.object(b,'render',return_value={target:'reviewed translation'}),patch.object(b,'read_json',return_value=decisions),patch.object(b,'preserved') as safeguard,patch('sys.argv',['build_relationships_full_editions.py','--preserve-pending-source']),patch('builtins.print'):
   self.assertEqual(b.main(),0);safeguard.assert_called_once()
  target.write_text.assert_called_once_with('reviewed translation')
  self.assertEqual((b.DATA/'pending-source-decisions.json').read_bytes(),original)
  self.assertEqual(decisions['status'],'pending author decision; do not apply')
 def test_published_reviewed_discovery_records(self):
  records=b.reviewed()
  if not records:self.skipTest('No review batches published yet')
  chunks={}
  for lang,slug in records:
   if lang not in chunks:chunks[lang]={r['u']:r for r in b.read_json(b.ROOT/'data/search'/(lang+'.json'))['records']}
   item=records[lang,slug];key=str(b.page(lang,slug).relative_to(b.ROOT))
   self.assertEqual(chunks[lang][key]['t'],item['title'])
   self.assertEqual(chunks[lang][key]['x'],item['deck'])
 def test_reviewed_pages_navigation_and_canonical(self):
  records=b.reviewed()
  if not records:self.skipTest('No review batches published yet')
  for (lang,slug),item in records.items():
   path=b.page(lang,slug);text=path.read_text();doc=Document(b.region(text,'en') if lang=='en' else text)
   canonical='https://nondubito.net/'+path.relative_to(b.ROOT).as_posix()
   self.assertIn('rel="canonical" href="'+canonical+'"',text)
   nav=b.find(doc,'series-nav')
   for node in nav.walk():
    if node.tag!='a':continue
    target=Path(node.attrs.get('href','')).stem
    if (lang,target) in records:self.assertIn(records[lang,target]['title'],node.text())
   whole=Document(text);controls=[n for n in b.find(whole,'lang-toggle').walk() if n.has('lang-btn')]
   self.assertEqual(len(controls),8)
 def test_draft_chapter_labels_match_index(self):
  for lang in b.LANGS:
   ip=b.DATA/'translations'/lang/'index.json'
   if not ip.exists():continue
   chapters=b.load(lang,'index')['chapters']
   for p in (b.DATA/'translations'/lang).glob('[0-9]*.json'):
    item=b.load(lang,p.stem)
    self.assertEqual(item['chapter'],chapters[(int(p.stem[:2])-1)//5],(lang,p.stem))
 def test_reviewed_outputs_current(self):
  for p,s in b.render().items():self.assertEqual(p.read_text(),s,str(p))

if __name__=='__main__':unittest.main()
