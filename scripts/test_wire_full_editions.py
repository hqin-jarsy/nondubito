import json,re,unittest
from unittest.mock import patch
from urllib.parse import urlsplit,unquote
import build_wire_full_editions as w
import build_collection_languages as compact
class WireEditions(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.output=w.render();cls.editions=w.translations();cls.receipt=w.manifest()
 def test_nine_complete_six_foreign_sources(self):
  self.assertEqual(len(self.editions),9)
  for slug,editions in self.editions.items():
   self.assertEqual(set(editions),set(w.LANGS)|{'en'})
   source=w.source(slug)
   for lang in w.LANGS:
    d=editions[lang];self.assertEqual([b['tag'] for b in d['blocks']],[b['tag'] for b in source['blocks']]);self.assertEqual(sum(b['tag']=='h2' for b in d['blocks']),5);self.assertGreater(sum(b['tag']=='p' for b in d['blocks']),80)
    body=w.rendered_body(d);page=self.output[w.SERIES/lang/(slug+'.html')];self.assertIn(body,page);self.assertIn(w.NOTES[lang],page)
   self.assertGreater(len(re.sub('<[^>]+>',' ',editions['en']['body_html']).split()),900)
 def test_chinese_only_exact_author_corrections(self):
  for item in self.receipt['articles']:
   slug=item['slug'];old=(w.DATA/'received'/(slug+'.html.txt')).read_text();new=self.output[w.SERIES/(slug+'.html')];a,b=w.primary_body(old,'zh');c,d=w.primary_body(new,'zh');self.assertEqual(new[c:d],w.approved_chinese(slug,old[a:b]));self.assertEqual(w.digest(old[a:b]),item['zh_body_sha256'])
 def test_protected_snapshot_and_dictionary_hashes(self):
  for p,expected in self.receipt['snapshots'].items():self.assertEqual(w.digest((w.DATA/'received'/(p+'.txt')).read_bytes()),expected)
  for name,expected in self.receipt['dictionaries'].items():
   original=(w.DATA/'received/zh-hant-data'/name).read_bytes();self.assertEqual(w.digest(original),expected)
   approved=w.DATA/'review/zh-hant-data'/name;self.assertEqual(self.output[w.SERIES/'zh-hant-data'/name],approved.read_text() if approved.exists() else original.decode())
 def test_all_approved_text_nodes_have_traditional_mapping(self):
  mapping=w.read(w.DATA/'review/approved-traditional.json')
  for e in w.read(w.DATA/'review/approved-chinese.json'):
   page=self.output[w.SERIES/'zh-hant-data'/(e['slug']+'.js')];variants=json.loads(re.search(r'var variants\s*=\s*(\{.*?\});',page,re.S)[1])
   for text in re.split('<[^>]+>',e['after']):
    if text and mapping[text]!=text:self.assertEqual(variants.get(text),mapping[text])
 def test_legacy_build_cannot_restore_summaries(self):
  result=compact.render(compact.load_specs({'the-wire'})[0]);self.assertTrue(all(result[p]==s for p,s in self.output.items()))
 def test_all_local_references_exist(self):
  for p,s in self.output.items():
   if p.suffix!='.html':continue
   for href in re.findall(r'(?:href|src)=[\"\']([^\"\']+)',s):
    u=urlsplit(href)
    if u.scheme or u.netloc or not u.path:continue
    target=(p.parent/unquote(u.path)).resolve();self.assertTrue(target.exists(),(p,href))
 def test_canonical_and_analytics(self):
  self.assertEqual(sum(p.suffix=='.html' for p in self.output),60)
  for p,s in self.output.items():
   if p.suffix!='.html':continue
   expected='https://nondubito.net/'+str(p.relative_to(w.ROOT));expected=expected.removesuffix('index.html') if p.name=='index.html' else expected
   self.assertIn('href="'+expected+'"',s);self.assertEqual(s.count('static.cloudflareinsights.com/beacon.min.js'),1)
 def test_acceptance_covers_all_editorial_inputs(self):
  files=w.read(w.DATA/'review/accepted.json')['files']
  required={'source-manifest.json'}|{str(p.relative_to(w.DATA)) for lang in ['source','en',*w.LANGS] for p in (w.DATA/lang).glob('*.json')}|{str(p.relative_to(w.DATA)) for p in (w.DATA/'review').glob('approved-*.json')}|{str(p.relative_to(w.DATA)) for p in (w.DATA/'review/zh-hant-data').glob('*.js')}
  self.assertTrue(required.issubset(files))
 def test_build_matches_checked_in_pages(self):
  for p,s in self.output.items():self.assertEqual(p.read_text(),s,p)
 def test_english_corrections_and_bridges(self):
  for e in w.read(w.DATA/'review/approved-english.json'):
   body=self.editions[e['slug']]['en']['body_html'];self.assertTrue(e['after'] in body,e['slug']);self.assertTrue(e['before'] not in body or e['before'] in e['after'],e['slug'])
  self.assertNotIn('single male teacher',self.editions['08-two-boys']['en']['body_html'])
  self.assertIn('penultimate episode',self.editions['09-the-game']['en']['body_html'])
if __name__=='__main__':unittest.main()
