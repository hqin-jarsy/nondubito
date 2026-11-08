#!/usr/bin/env python3
"""Whole-series structure/preservation tests, not a substitute for language review."""
import json,re,unittest
from pathlib import Path
from urllib.parse import urlsplit,unquote
import build_ancient_full_editions as b
from test_companion_languages import Parsed,Node

class AncientFullEditions(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.receipt=b.manifest();cls.editions=b.editions()

 def test_sources_snapshots_and_only_recorded_chinese_changes(self):
  self.assertEqual(len(self.receipt['essays']),19)
  self.assertEqual(len(self.receipt['snapshot_files']),120)
  for key in ('source_files','snapshot_files'):
   for rel,digest in self.receipt[key].items():self.assertEqual(b.digest((b.DATA/rel).read_bytes()),digest,rel)
  baseline=b.read_json(b.DATA/'chinese-baseline.json')
  self.assertEqual(len(baseline),20)
  for filename,codes in baseline.items():
   before=b.snapshot(filename).read_text();now=(b.SERIES/filename).read_text()
   for code,digest in codes.items():
    self.assertEqual(b.digest(b.region(before,'lang-'+code)),digest,(filename,code))
    self.assertEqual(b.approved_chinese_region(filename,code),b.region(now,'lang-'+code),(filename,code))
   for css in ('entry-door','related-note'):
    self.assertEqual(Parsed(before).nodes('div',css),Parsed(now).nodes('div',css))

 def test_chinese_corrections_are_exact_and_limited(self):
  records=b.source_corrections()
  self.assertEqual({(r['episode'],r['block']) for r in records},{(15,31),(4,104)})
  for item in self.receipt['essays']:
   for lang in ('zh-Hans','zh-Hant'):
    original=b.read_json(b.DATA/'source'/f"{item['episode']:02}.{lang}.json")
    expected=json.loads(json.dumps(original))
    for record in records:
     if item['episode']==record['episode']:
      change=record['edits'][lang]
      self.assertEqual(original[record['block']]['text'],change['before'])
      self.assertEqual(len(change['after'])-len(change['before']),1)
      expected[record['block']]['text']=change['after']
    self.assertEqual(b.source(item['episode'],lang),expected)

 def test_approved_izanagi_sentence_is_synchronized_in_six_translations(self):
  record=b.approved_corrections()[0]
  for lang in b.FOREIGN:
   blocks=b.read_json(b.DATA/'translations'/f'04.{lang}.json')
   self.assertEqual(blocks[104]['text'],record['translations'][lang]['after'])
   self.assertNotEqual(blocks[104]['text'],record['translations'][lang]['before'])

 def test_all_152_texts_order_emphasis_and_source_alignment(self):
  for slug,copies in self.editions.items():
   src=b.source(int(slug[:2]))
   for lang,blocks in copies.items():
    with self.subTest(slug=slug,lang=lang):
     primary=lang in ('zh-Hans','zh-Hant','en')
     p=b.SERIES/(slug+'.html') if primary else b.SERIES/lang/(slug+'.html')
     text=p.read_text()
     if primary:text=b.region(text,'lang-'+{'en':'en','zh-Hans':'zh','zh-Hant':'hant'}[lang])
     tree=Parsed(text);self.assertEqual(tree.nodes('h1')[0].text(),b.title(blocks))
     main=tree.nodes('div','article-body' if primary else 'collection-body')[0]
     actual=[n for n in main.children if isinstance(n,Node)]
     expected=[n for n in Parsed(b.body(blocks)).root.children if isinstance(n,Node)]
     self.assertEqual(actual,expected)
     self.assertEqual([x['tag'] for x in src],[x['tag'] for x in blocks])
     self.assertNotIn('\ufffd',text)

 def test_routes_navigation_links_analytics_and_canonicals(self):
  for p in b.SERIES.rglob('*.html'):
   text=p.read_text();tree=Parsed(text);primary=p.parent==b.SERIES
   menus=tree.nodes('div','lang-toggle' if primary else 'language-route');self.assertEqual(len(menus),1,p)
   choices=[n for n in menus[0].walk() if n.has_class('lang-btn')]
   self.assertEqual(len(choices),8,p)
   self.assertEqual(sum(n.tag=='button' for n in choices),3 if primary else 0,p)
   expected={((b.SERIES/lang/p.name).resolve(),'') for lang in ('ja','fr','de','es','ko') if primary or p.parent.name!=lang}
   if not primary:expected.update(((b.SERIES/p.name).resolve(),'lang='+lang) for lang in ('en','zh','zh-hant'))
   actual=set()
   for n in choices:
    if n.tag=='a':
     u=urlsplit(n.attrs['href']);actual.add(((p.parent/unquote(u.path)).resolve(),u.query))
   self.assertEqual(actual,expected,p)
   for n in tree.nodes():
    val=n.attrs.get('href') if n.tag in ('a','link') else n.attrs.get('src') if n.tag in ('script','img') else None
    if not val:continue
    u=urlsplit(val)
    if u.scheme or u.netloc:continue
    target=(p.parent/unquote(u.path)).resolve() if u.path else p
    self.assertTrue(target.is_file(),(p,val))
    if u.fragment:self.assertTrue(any(n.attrs.get('id')==u.fragment for n in Parsed(target.read_text()).nodes()),(p,val))
   part=b.region(text,'lang-en') if primary else text;lang='en' if primary else p.parent.name
   for n in Parsed(part).nodes('a'):
    slug=Path(urlsplit(n.attrs.get('href','')).path).stem
    if slug not in self.editions or n.has_class('lang-btn'):continue
    self.assertIn(b.title(self.editions[slug][lang]),n.text(),(p,slug))
   if p.stem in self.editions:
    links=Parsed(part).nodes('a','series-nav-btn') if primary else [n for n in Parsed(part).nodes('nav','collection-nav')[0].walk() if n.tag=='a']
    ep=int(p.stem[:2]);neighbors=({ep-1} if ep>1 else set())|({ep+1} if ep<19 else set())
    found=set()
    for n in links:
     target=Path(urlsplit(n.attrs['href']).path).stem
     if target not in self.editions:continue
     found.add(int(target[:2]));self.assertIn('←' if int(target[:2])<ep else '→',n.text(),p)
    self.assertEqual(found,neighbors,p)
   else:self.assertEqual(len(Parsed(part).nodes('a','essay-card' if primary else 'collection-card')),19,p)
   self.assertEqual(text.count('static.cloudflareinsights.com/beacon.min.js'),1,p)
   original=Parsed(b.snapshot(p.relative_to(b.SERIES)).read_text())
   self.assertEqual([n.attrs['href'] for n in tree.nodes('link') if n.attrs.get('rel')=='canonical'],[n.attrs['href'] for n in original.nodes('link') if n.attrs.get('rel')=='canonical'],p)

 def test_rebuild_and_compact_builder_idempotence(self):
  for p,text in b.render().items():self.assertEqual(p.read_text(),text,p)
  from build_collection_languages import load_specs,render
  output=render(load_specs({'ancient-stories'})[0]);self.assertEqual(len(output),120)
  for p,text in output.items():self.assertEqual(p.read_text(),text,p)

 def test_guard_rejects_unrecorded_foreign_title_and_body_edits(self):
  slug=self.receipt['essays'][0]['slug']
  for lang in b.FOREIGN:
   p=b.SERIES/(slug+'.html') if lang=='en' else b.SERIES/lang/(slug+'.html');text=p.read_text()
   for field in ('title','body'):
    def inject(part):
     if field=='title':return re.sub(r'(<h1[^>]*>)',r'\1USER_EDIT_SENTINEL',part,count=1)
     return b.within(part,'article-body' if lang=='en' else 'collection-body',lambda v:v+'<p>USER_EDIT_SENTINEL</p>')
    changed=b.within(text,'lang-en',inject) if lang=='en' else inject(text)
    with self.subTest(lang=lang,field=field),self.assertRaisesRegex(AssertionError,'Foreign HTML prose changed'):b.guard(p,changed,lang,self.editions[slug][lang])

 def test_search_is_current_and_keeps_existing_routes(self):
  for p,text in b.search_outputs().items():self.assertEqual(p.read_text(),text,p)
  prefix=str(b.SERIES.relative_to(b.ROOT))+'/'
  for lang in b.LANGS:
   path=b.ROOT/'data/search'/f'{lang.lower()}.json';rows=b.read_json(path)['records'];target=[r for r in rows if r['u'].startswith(prefix)]
   self.assertEqual(len(target),20,(lang,len(target)))
   for row in target:
    slug=Path(urlsplit(row['u']).path).stem
    if slug in self.editions:self.assertEqual(row['t'],b.title(self.editions[slug][lang]),(lang,slug))

 def test_batch_reviews_exist(self):
  for batch in ('01-05','06-10','11-15','16-19'):
   p=b.DATA/'reviews'/f'batch-{batch}.md';self.assertTrue(p.is_file(),p);self.assertGreater(len(p.read_text()),150,p)

 def test_explicit_language_queries_and_toggles_persist(self):
  for p in b.SERIES.glob('*.html'):
   text=p.read_text()
   self.assertIn("if(q&&['en','zh','zh-hant'].indexOf(q)!==-1){localStorage.setItem('nd_lang',saved);localStorage.setItem('nondubito-lang',saved);}",text,p)
   self.assertIn("languageURL.searchParams.set('lang',saved);history.replaceState(history.state,'',languageURL.href);",text,p)

if __name__=='__main__':unittest.main()
