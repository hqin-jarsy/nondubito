#!/usr/bin/env python3
"""Render the four reviewed Orwell essays without generating or rewriting prose.

The Chinese article/index bodies are canonical and hash-checked. Translation
units retain paragraph and heading boundaries. Editorial approval is required
before a changed Chinese source can receive an amendment in the preservation
record. Coverage and hashes are safeguards, not semantic-quality evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from prepare_action_sources import Document, Node, one
from build_classic_full_editions import patch, inner, metadata, translated_links

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'essays/literature/nineteen-eighty-four'
DATA=ROOT/'data/nineteen-eighty-four-full'
LANGS=('en','ja','fr','de','es','ko')
LABELS={'ja':'日本語全文訳','fr':'Traduction française intégrale','de':'Vollständige deutsche Übersetzung','es':'Traducción española íntegra','ko':'한국어 완역'}
READER='../../../classic-reading.js'
STYLE='<style id="orwell-full-reader">.culture-page>main:not(.series-container){padding-top:54px}.culture-page .essay-header{padding:2.5rem 1.25rem 2rem}.culture-page .essay-header-inner{max-width:var(--max-w-prose);margin:0 auto}.culture-page .essay-header h1{font-size:clamp(1.8rem,4.5vw,2.8rem);line-height:1.2}.culture-page .essay-header .lang-toggle{border-color:var(--cream-border)}.culture-page .essay-header .lang-btn{color:var(--ink-muted)}.culture-page .essay-header .lang-btn.active{color:var(--ink);background:var(--cream-dark)}.culture-page .essay-header .lang-sep{color:var(--cream-border)}.essay-page-inner,.series-container{min-width:0}.essay-page-title,.series-title,.essay-header h1,.card-title-en,.card-title-zh,.entry-title,.essay-body,.nav-title{overflow-wrap:anywhere}.essay-card,.card-body,.entry-row,.series-nav a,.essay-nav a{min-width:0}.lang-toggle{flex-wrap:wrap}.essay-body>p:first-child{font-family:var(--sans);font-size:.78rem;line-height:1.7;color:var(--ink-muted);border-bottom:1px solid var(--cream-border);padding-bottom:1.25rem;margin-bottom:2.5rem}</style>'

def read_json(path):return json.loads(path.read_text())
def sha(value):return hashlib.sha256(value.encode()).hexdigest()
def source(slug):
 doc=Document((DIRECTORY/(slug+'.html')).read_text())
 node=one(doc.root.walk(),lambda n:n.has('essay-body','lang-zh'),slug)
 return doc.raw(node,inner=True),[doc.raw(n) for n in node.children if isinstance(n,Node)]
def preserved():
 receipt=read_json(DATA/'preservation.json')
 for slug,record in receipt['source_bodies'].items():
  raw,units=source(slug)
  assert sha(raw)==record['sha256'],(slug,'Chinese source differs from approved source')
  assert len(units)==record['units'],slug
 raw,_=source('index')
 assert sha(raw)==receipt['source_index_body_sha256'],'Chinese index changed'
 for name,digest in receipt['traditional_files'].items():
  expected=receipt.get('updated_traditional_files',{}).get(name,digest)
  assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
 return receipt

def load(lang,slug):
 item=read_json(DATA/'translations'/lang/(slug+'.json'))
 raw,units=source(slug)
 assert item['language']==lang and item['slug']==slug
 assert item['source_sha256']==sha(raw),(lang,slug,'stale Chinese source')
 assert len(item['body'])==len(units),(lang,slug,'missing translation units')
 assert item.get('title') and item.get('deck') and item.get('review'),(lang,slug,'missing review or metadata')
 for i,(original,translation) in enumerate(zip(units,item['body']),1):
  a,b=Document(original),Document(translation)
  an=[n for n in a.root.children if isinstance(n,Node)];bn=[n for n in b.root.children if isinstance(n,Node)]
  assert len(bn)==1 and bn[0].tag==an[0].tag,(lang,slug,i,'paragraph/heading boundary')
  assert bn[0].text().strip(),(lang,slug,i,'empty translation')
  assert all(n.tag in ('root','p','h2','strong','em','a','br','sup','sub') for n in b.root.walk()),(lang,slug,i,'unexpected markup')
  assert original.count('<strong>')==translation.count('<strong>'),(lang,slug,i,'lost emphasis')
  assert not re.search(r'\[VERIFY|TODO|TBD|PLACEHOLDER',translation),(lang,slug,i,'placeholder')
 return item

def index_source():return read_json(DATA/'sources/index.json')
def shared(lang):
 item=read_json(DATA/'translations'/lang/'index.json')
 assert item['language']==lang and item.get('title') and item.get('source_note'),(lang,'index metadata')
 assert len(item['intro'])==len(index_source()['intro'])==3,(lang,'index coverage')
 assert all(isinstance(p,str) and p.strip() for p in item['intro'])
 return item

def reading_controls(text,lang):
 if lang=='en':
  text=re.sub(r'<script>\s*\(function\(\)\{\s*var saved=localStorage\.getItem.*?</script>','<script src="'+READER+'"></script>',text,flags=re.S)
  assert text.count('src="'+READER+'"')==1,'primary language controller'
  text=text.replace('Independent English edition','Complete English translation')
 else:
  def primary_link(match):
   tag=match[0];code=re.search(r"setItem\('nd_lang','([^']+)'\)",tag)[1]
   tag=re.sub(r'\s*onclick="[^"]*"','',tag)
   return re.sub(r'href="([^"?]+)(?:\?lang=[^"]+)?"',lambda m:'href="'+m[1]+'?lang='+code+'"',tag)
  text=re.sub(r'<a\b[^>]*onclick="localStorage\.setItem[^>]*>',primary_link,text)
 text=re.sub(r'<style id="orwell-full-reader">.*?</style>','',text,flags=re.S)
 return text.replace('</head>',STYLE+'</head>',1)

def render(partial=False):
 receipt=preserved();slugs=list(receipt['source_bodies']);outputs={}
 for lang in LANGS:
  items={slug:load(lang,slug) for slug in slugs if not partial or (DATA/'translations'/lang/(slug+'.json')).exists()}
  if not items:continue
  directory=DIRECTORY if lang=='en' else DIRECTORY/lang
  texts={p:p.read_text() for p in directory.glob('*.html')}
  index=shared(lang) if (DATA/'translations'/lang/'index.json').exists() else None
  if not partial:assert index is not None,(lang,'missing index')
  aliases={}
  for slug,item in list(items.items())+([('index',index)] if index else []):
   p=directory/(slug+'.html');doc=Document(texts[p])
   h=one(doc.root.walk(),lambda n:n.tag=='h1' and (lang!='en' or n.has('lang-en')),(lang,slug,'title'))
   old=doc.raw(h,inner=True);new=html.escape(item['title'],quote=False)
   if old!=new:aliases[old]=new
  for p,text in texts.items():
   for old,new in sorted(aliases.items(),key=lambda a:len(a[0]),reverse=True):text=text.replace(old,new)
   texts[p]=text
  for slug,item in items.items():
   p=directory/(slug+'.html');text=texts[p];doc=Document(text)
   body=one(doc.root.walk(),lambda n:n.has('essay-body') and (lang!='en' or n.has('lang-en')),(lang,slug,'body'))
   prose=translated_links('\n\n'.join(item['body']),lang,source(slug)[1],DIRECTORY)
   if lang!='en':
    # Culture-page article shells include their neighbor navigation inside the
    # body. Preserve that navigation; the translated final paragraph replaces
    # the obsolete independent-rewriting source note. Never overlap patches.
    nav=one(body.walk(),lambda n:n.has('series-nav'),(lang,slug,'neighbor navigation'))
    prose+='\n'+doc.raw(nav)
   changes=[inner(body,prose)]
   if lang!='en':
    for n in doc.root.walk():
     if n.has('essay-entry-point'):changes.append(inner(n,html.escape(item['deck'])))
   text=metadata(patch(text,changes),item['deck'])
   texts[p]=text
  ip=directory/'index.html';text=texts[ip];doc=Document(text);changes=[]
  section=one(doc.root.walk(),lambda n:n.has('essay-body','lang-en'),'English index') if lang=='en' else one(doc.root.walk(),lambda n:n.tag=='main','foreign index')
  for card in section.walk():
   if card.tag!='a' or not (card.has('essay-card') or card.has('entry-row')):continue
   slug=Path(card.attrs.get('href','')).stem
   if slug not in items:continue
   deck=one(card.walk(),lambda n:n.has('card-desc') or n.has('entry-desc'),(lang,slug,'card description'))
   changes.append(inner(deck,html.escape(items[slug]['deck'])))
  if index:
   if lang=='en':
    paragraphs=[n for n in section.children if isinstance(n,Node) and n.tag=='p']
    assert len(paragraphs)==4,'primary index intro structure'
    for node,value in zip(paragraphs[:3],index['intro']):changes.append(inner(node,value))
    changes.append(inner(paragraphs[3],'<em>'+html.escape(index['source_note'])+'</em>'))
   else:
    desc=one(section.walk(),lambda n:n.has('series-desc'),lang+' intro')
    changes.append(inner(desc,''.join('<p>'+p+'</p>' for p in index['intro'])))
    for n in section.walk():
     if n.has('source-note'):changes.append(inner(n,html.escape(index['source_note'])))
   text=metadata(patch(text,changes),re.sub('<[^>]+>','',index['intro'][0]))
  else:text=patch(text,changes)
  texts[ip]=text
  for p,text in texts.items():outputs[p]=reading_controls(text,lang)
 # No replacement of an English title or deck is allowed to touch Chinese.
 for p,text in outputs.items():
  doc=Document(text)
  if p.parent!=DIRECTORY:continue
  n=one(doc.root.walk(),lambda n:n.has('essay-body','lang-zh'),p.name)
  assert doc.raw(n,inner=True)==source(p.stem)[0],(p,'Chinese body altered during rendering')
 return outputs

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--partial',action='store_true');a=p.parse_args()
 outputs=render(a.partial);stale=[p for p,s in outputs.items() if p.read_text()!=s]
 if a.check:
  for p in stale:print('STALE',p.relative_to(ROOT))
  if stale:return 1
 else:
  for p in stale:p.write_text(outputs[p])
 print(('Checked' if a.check else 'Rendered'),len(outputs),'pages;',len(stale),'changed')
 return 0
if __name__=='__main__':raise SystemExit(main())
