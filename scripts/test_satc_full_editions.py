import json,re,unittest
from unittest.mock import patch
from urllib.parse import urlsplit,unquote
import build_satc_full_editions as w
import build_collection_languages as compact
class SatcEditions(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.output=w.render();cls.editions=w.translations();cls.receipt=w.manifest()
 def test_ten_complete_six_foreign_sources(self):
  self.assertEqual(len(self.editions),10)
  for slug,editions in self.editions.items():
   self.assertEqual(set(editions),set(w.LANGS)|{'en'})
   source=w.source(slug)
   for lang in w.LANGS:
    d=editions[lang];self.assertEqual([b['tag'] for b in d['blocks']],[b['tag'] for b in source['blocks']]);self.assertEqual(sum(b['tag']=='h2' for b in d['blocks']),sum(b['tag']=='h2' for b in source['blocks']));self.assertGreater(sum(b['tag']=='p' for b in d['blocks']),60)
    body=w.rendered_body(d);page=self.output[w.SERIES/lang/(slug+'.html')];self.assertIn(body,page);self.assertIn(w.NOTES[lang],page)
   self.assertGreater(len(re.sub('<[^>]+>',' ',editions['en']['body_html']).split()),600)
 def test_final_source_note_keeps_series_scope(self):
  last=self.editions['10-i-love-me-more']
  for lang in w.LANGS:
   note=last[lang]['source_note']
   self.assertRegex(note,re.compile(r'And Just Like That|앤 저스트 라이크 댓',re.I),(lang,'missing sequel exclusion scope'))
   first=self.editions['01-the-column'][lang]['source_note']
   self.assertGreater(len(note),len(first)+40,(lang,'scope note shortened'))
  self.assertIn('These ten essays draw on the original series and both films',last['en']['body_html'])
  self.assertIn('they do not cover And Just Like That',last['en']['body_html'])
 def test_chinese_only_exact_author_corrections(self):
  for item in self.receipt['articles']:
   slug=item['slug'];old=(w.DATA/'received'/(slug+'.html.txt')).read_text();new=self.output[w.SERIES/(slug+'.html')];a,b=w.primary_body(old,'zh');c,d=w.primary_body(new,'zh');self.assertEqual(new[c:d],w.approved_chinese(slug,old[a:b]));self.assertEqual(w.digest(old[a:b]),item['zh_body_sha256'])
 def test_protected_snapshot_and_dictionary_hashes(self):
  for p,expected in self.receipt['snapshots'].items():self.assertEqual(w.digest((w.DATA/'received'/(p+'.txt')).read_bytes()),expected)
  for name,expected in self.receipt['dictionaries'].items():
   original=(w.DATA/'received/zh-hant-data'/name).read_bytes();self.assertEqual(w.digest(original),expected)
   approved=w.DATA/'review/zh-hant-data'/name;self.assertEqual(self.output[w.SERIES/'zh-hant-data'/name],approved.read_text() if approved.exists() else original.decode())
 def test_all_approved_text_nodes_have_traditional_mapping(self):
  mapping=w.read(w.DATA/'review/approved-traditional.json') if (w.DATA/'review/approved-traditional.json').exists() else {}
  for e in w.read(w.DATA/'review/approved-chinese.json'):
   page=self.output[w.SERIES/'zh-hant-data'/(e['slug']+'.js')];variants=json.loads(re.search(r'var variants\s*=\s*(\{.*?\});',page,re.S)[1])
   for text in re.split('<[^>]+>',e['after']):
    if re.search('[\u3400-\u9fff]',text):
     self.assertIn(text,mapping)
     if mapping[text]!=text:self.assertEqual(variants.get(text),mapping[text])
 def test_legacy_build_cannot_restore_summaries(self):
  result=compact.render(compact.load_specs({'sex-and-the-city'})[0]);self.assertTrue(all(result[p]==s for p,s in self.output.items()))
 def test_all_local_references_exist(self):
  for p,s in self.output.items():
   if p.suffix!='.html':continue
   for href in re.findall(r'(?:href|src)=[\"\']([^\"\']+)',s):
    u=urlsplit(href)
    if u.scheme or u.netloc or not u.path:continue
    target=(p.parent/unquote(u.path)).resolve();self.assertTrue(target.exists(),(p,href))
 def test_canonical_and_analytics(self):
  self.assertEqual(sum(p.suffix=='.html' for p in self.output),66)
  for p,s in self.output.items():
   if p.suffix!='.html':continue
   expected='https://nondubito.net/'+str(p.relative_to(w.ROOT));expected=expected.removesuffix('index.html') if p.name=='index.html' else expected
   self.assertIn('href="'+expected+'"',s);self.assertEqual(s.count('static.cloudflareinsights.com/beacon.min.js'),1)
 def test_acceptance_covers_all_editorial_inputs(self):
  files=w.read(w.DATA/'review/accepted.json')['files']
  required={'source-manifest.json'}|{str(p.relative_to(w.DATA)) for lang in ['source','en',*w.LANGS] for p in (w.DATA/lang).glob('*.json')}|{str(p.relative_to(w.DATA)) for p in (w.DATA/'review').glob('approved-*.json')}|{str(p.relative_to(w.DATA)) for p in (w.DATA/'review/zh-hant-data').glob('*.js')}
  self.assertTrue(required.issubset(files))
 def test_pending_acceptance_is_rejected(self):
  original=w.read
  def pending(p):
   value=original(p)
   if p==w.DATA/'review/accepted.json':value['status']='draft'
   return value
  with patch.object(w,'read',pending),self.assertRaisesRegex(AssertionError,'acceptance is pending'):
   w.translations()
 def test_incomplete_acceptance_is_rejected(self):
  original=w.read
  def incomplete(p):
   value=original(p)
   if p==w.DATA/'review/accepted.json':value['files'].pop('source-manifest.json')
   return value
  with patch.object(w,'read',incomplete),self.assertRaisesRegex(AssertionError,'Incomplete editorial acceptance'):
   w.translations()
 def test_stale_acceptance_is_rejected(self):
  original=w.read
  def stale(p):
   value=original(p)
   if p==w.DATA/'review/accepted.json':value['files']['source-manifest.json']='0'*64
   return value
  with patch.object(w,'read',stale),self.assertRaisesRegex(AssertionError,'editorial reacceptance required'):
   w.translations()
 def test_unknown_page_edit_is_preserved(self):
  from pathlib import Path
  page=next(p for p in self.output if p.suffix=='.html');original=Path.read_text
  def changed(p,*args,**kwargs):return original(p,*args,**kwargs)+('<!-- unknown edit -->' if p==page else '')
  with patch.object(Path,'read_text',changed),self.assertRaisesRegex(AssertionError,'preserve manual edits'):
   w.protect(page,self.output[page])
 def test_build_matches_checked_in_pages(self):
  for p,s in self.output.items():self.assertEqual(p.read_text(),s,p)
if __name__=='__main__':unittest.main()
