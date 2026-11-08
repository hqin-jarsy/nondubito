#!/usr/bin/env python3
"""Whole-corpus integrity checks. These do not claim native editorial review."""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit,unquote
from unittest.mock import patch
import build_fables_full_editions as b
from test_companion_languages import Parsed,Node

class FablesFullEditions(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.receipt=b.manifest()
  cls.editions=b.editions()

 def test_sources_snapshots_and_chinese_are_unchanged(self):
  self.assertEqual(len(self.receipt['essays']),23)
  self.assertEqual(len(self.receipt['snapshots']),144)
  for rel,digest in self.receipt['snapshots'].items():
   self.assertEqual(b.digest(b.snapshot(rel).read_bytes()),digest,rel)
  for filename,codes in self.receipt['chinese_regions'].items():
   now=(b.SERIES/filename).read_text()
   before=b.snapshot(filename).read_text()
   for code,digest in codes.items():
    self.assertEqual(b.digest(b.region(before,'lang-'+code)),digest,(filename,code))
    self.assertEqual(b.region(now,'lang-'+code),b.approved_chinese_region(filename,code))
   # Non-article reading entrances stay verbatim too.
   for css in ('entry-door','related-note'):
    self.assertEqual(Parsed(before).nodes('div',css),Parsed(now).nodes('div',css))
  for item in self.receipt['essays']:
   src=b.source(item['episode'])
   part=b.approved_chinese_region(item['slug']+'.html','zh')
   main=Parsed(b.within_body(part,'article-body'))
   rebuilt=Parsed(b.body(src['blocks']))
   self.assertEqual(main.root,rebuilt.root,item['slug'])

 def test_only_recorded_source_corrections_are_applied(self):
  corrections=b.read_json(b.DATA/'source-corrections.json')['edits']
  self.assertEqual([(e['episode'],e['text_index']) for e in corrections],[(6,3),(20,90)])
  for edit in corrections:
   episode=edit['episode'];index=edit['text_index']
   original_path=b.DATA/'source-original'/f'{episode:02}.json'
   original=b.read_json(original_path)
   item=next(i for i in self.receipt['essays'] if i['episode']==episode)
   self.assertEqual(b.digest(original_path.read_bytes()),item['original_source_sha256'])
   expected=json.loads(json.dumps(original))
   self.assertEqual(expected['texts'][index],edit['before'])
   expected['texts'][index]=edit['after']
   changed=[block for block in expected['blocks'] if block.get('text')==edit['before']]
   self.assertEqual(len(changed),1)
   changed[0]['text']=edit['after']
   self.assertEqual(b.source(episode),expected)
  self.assertEqual(b.source(20)['texts'][90],'他们没有强行让婆罗门放下羊。')
  self.assertEqual(b.source(20)['texts'][20],'“你怎么把一头驴扛在肩上？快把它放下，别让更多人看见。”')
  approved=corrections[1]['translations']
  self.assertEqual(set(approved),set(b.FOREIGN))
  for lang,change in approved.items():
   self.assertEqual(b.read_json(b.DATA/'translations'/lang/'20.json')[90],change['after'])


 def test_every_paragraph_quote_break_and_emphasis_is_rendered(self):
  for slug,copies in self.editions.items():
   for lang,blocks in copies.items():
    p=b.SERIES/(slug+'.html') if lang=='en' else b.SERIES/lang/(slug+'.html')
    text=p.read_text()
    part=b.region(text,'lang-en') if lang=='en' else text
    tree=Parsed(part)
    self.assertEqual(tree.nodes('h1')[0].text(),b.title(blocks),(slug,lang))
    actual=Parsed(b.within_body(part,'article-body'))
    expected=Parsed(b.body(blocks))
    self.assertEqual(actual.root,expected.root,(slug,lang))
    src=b.source(int(slug[:2]))
    self.assertEqual(len(actual.nodes('p')),len(src['texts'])-1,(slug,lang))
    for tag in ('strong','em','br','blockquote','hr'):
     self.assertEqual(len(actual.nodes(tag)),len(Parsed(b.body(src['blocks'])).nodes(tag)),(slug,lang,tag))
    self.assertNotIn('\ufffd',text)
    self.assertEqual(len(tree.nodes('div','article-body')),1)
    self.assertTrue(tree.nodes('div','article-body')[0].has_class('full-edition'),(slug,lang))

 def test_language_routes_all_navigation_and_local_links(self):
  for p in b.SERIES.rglob('*.html'):
   text=p.read_text();tree=Parsed(text);primary=p.parent==b.SERIES
   menus=tree.nodes('div','lang-toggle' if primary else 'language-route')
   self.assertEqual(len(menus),1,p)
   choices=[n for n in menus[0].walk() if n.has_class('lang-btn')]
   self.assertEqual(len(choices),8,p)
   self.assertEqual(sum(n.tag=='button' for n in choices),3 if primary else 0,p)
   self.assertEqual(sum(n.tag=='a' for n in choices),5 if primary else 7,p)
   expected=set()
   for code in ('ja','fr','de','es','ko'):
    if not primary and code==p.parent.name:continue
    expected.add(((b.SERIES/code/p.name).resolve(),''))
   if not primary:
    expected.update(((b.SERIES/p.name).resolve(),'lang='+code) for code in ('en','zh','zh-hant'))
   else:
    self.assertIn("if(q&&['en','zh','zh-hant'].indexOf(q)!==-1){localStorage.setItem('nd_lang',saved);localStorage.setItem('nondubito-lang',saved);}",text,p)
    self.assertIn("languageURL.searchParams.set('lang',saved);history.replaceState(history.state,'',languageURL.href);",text,p)
   actual=set()
   for n in choices:
    if n.tag!='a':continue
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
   part=b.region(text,'lang-en') if primary else text
   lang='en' if primary else p.parent.name
   for n in Parsed(part).nodes('a'):
    slug=Path(urlsplit(n.attrs.get('href','')).path).stem
    if slug not in self.editions or n.has_class('lang-btn'):continue
    self.assertIn(b.title(self.editions[slug][lang]),n.text(),(p,slug))
   if p.stem in self.editions:
    links=Parsed(part).nodes('a','series-nav-btn')
    ep=int(p.stem[:2])
    expected_eps=({ep-1} if ep>1 else set())|({ep+1} if ep<23 else set())
    actual_eps={int(Path(n.attrs['href']).stem[:2]) for n in links if Path(n.attrs['href']).stem in self.editions}
    self.assertEqual(actual_eps,expected_eps,p)
    for n in links:
     self.assertIn('→' if n.has_class('next') else '←',n.text(),p)
   if p.stem=='index':self.assertEqual(len(Parsed(part).nodes('a','essay-card')),23,p)
   back=tree.nodes('a','back-link')
   self.assertEqual(len(back),1,p)
   target=(p.parent/urlsplit(back[0].attrs['href']).path).resolve()
   expected_back=(b.SERIES.parent/'index.html') if p.stem=='index' else (p.parent/'index.html')
   self.assertEqual(target,expected_back.resolve(),p)
   self.assertEqual(text.count('static.cloudflareinsights.com/beacon.min.js'),1,p)
   canonical=tree.nodes('link')[0]
   self.assertTrue(any(n.attrs.get('rel')=='canonical' for n in tree.nodes('link')),p)

 def test_rebuild_is_idempotent(self):
  for p,text in b.render().items():self.assertEqual(p.read_text(),text,p)

 def test_manual_foreign_edits_are_protected(self):
  slug=self.receipt['essays'][0]['slug']
  for lang in b.FOREIGN:
   p=b.SERIES/(slug+'.html') if lang=='en' else b.SERIES/lang/(slug+'.html')
   text=p.read_text()
   def inject(part):return b.within(part,'article-body',lambda body:body+'<p>USER_EDIT_SENTINEL</p>')
   changed=b.within(text,'lang-en',inject) if lang=='en' else inject(text)
   with self.subTest(lang=lang,field='body'),self.assertRaisesRegex(AssertionError,'Foreign HTML prose changed'):
    b.guard(p,changed,lang,self.editions[slug][lang])
   def change_title(part):return re.sub(r'(<h1[^>]*>)',r'\1USER_EDIT_SENTINEL',part,count=1)
   changed=b.within(text,'lang-en',change_title) if lang=='en' else change_title(text)
   with self.subTest(lang=lang,field='title'),self.assertRaisesRegex(AssertionError,'Foreign HTML prose changed'):
    b.guard(p,changed,lang,self.editions[slug][lang])

 def test_search_titles_and_scoped_rebuild(self):
  for p,text in b.search_outputs().items():self.assertEqual(p.read_text(),text,p)
  for lang in b.FOREIGN:
   records=b.read_json(b.ROOT/'data/search'/f'{lang}.json')['records']
   indexed={x['u']:x for x in records}
   for slug,copies in self.editions.items():
    route='essays/everyday/stories/fables/'+('' if lang=='en' else lang+'/')+slug+'.html'
    self.assertEqual(indexed[route]['t'],b.title(copies[lang]),(lang,slug))

 def test_full_body_class_preserves_existing_language_class(self):
  before='<div class="article-body ko"><p>Test</p></div>'
  after=b.mark_full_body(before)
  self.assertEqual(after,'<div class="article-body ko full-edition"><p>Test</p></div>')
  self.assertEqual(b.mark_full_body(after),after)

 def test_review_batches_exist_and_markup_fails_closed(self):
  for lang in b.FOREIGN:
   for batch in ('01-05','06-10','11-15','16-20','21-23'):
    matches=list((b.DATA/'reviews').glob(f'{lang}*{batch}*.md'))
    self.assertTrue(matches,(lang,batch))
    self.assertGreater(len(matches[0].read_text()),100,(lang,batch))
  for value in ('<script>bad</script>','*broken'):
   with self.assertRaises(AssertionError):b.inline(value)
  self.assertEqual(b.inline('A & B; **bold** and *italic*\nnext'),'A &amp; B; <strong>bold</strong> and <em>italic</em><br />\nnext')

if __name__=='__main__':unittest.main()
