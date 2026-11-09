#!/usr/bin/env python3
"""Render reviewed translations into existing shells; never generate article prose.

Chinese is read directly from the published canonical pages and checked against
an explicit preservation record. Translation JSON is the only foreign-body input.
Paragraph parity and hashes are safeguards, never substitutes for semantic review.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from prepare_action_sources import Document, Node, one

ROOT=Path(__file__).resolve().parents[1]
LANGS=('en','ja','de','fr','es','ko')
SUPPORTED=('sae-nicomachean',)
LABELS={'ja':'日本語全文訳','de':'Vollständige deutsche Übersetzung',
 'fr':'Traduction française intégrale','es':'Traducción española íntegra','ko':'한국어 완역'}
ZH_NOTE='完整版本：简体中文 · 繁體中文 · English · 日本語 · Français · Deutsch · Español · 한국어。六种外语均以中文底本逐篇对照，保留完整论证、例子与限定。'
HANT_NOTE='完整版本：簡體中文 · 繁體中文 · English · 日本語 · Français · Deutsch · Español · 한국어。六種外語均以中文底本逐篇對照，保留完整論證、例子與限定。'
EN_NOTE='Complete edition · Eight languages. All six foreign-language editions are checked against the complete Chinese essays, preserving their arguments, examples, and qualifications.'

def sha(value):return hashlib.sha256(value.encode()).hexdigest()
def base(series):
 assert series in SUPPORTED,series
 return ROOT/'data'/(series+'-full')
def folder(series):return ROOT/'essays'/series
def read_json(path):return json.loads(path.read_text())
def source(series,slug):
 doc=Document((folder(series)/(slug+'.html')).read_text())
 node=one(doc.root.walk(),lambda n:n.has('essay-body','lang-zh'),slug)
 return doc.raw(node,inner=True),[doc.raw(n) for n in node.children if isinstance(n,Node)]
def preserved(series):
 receipt=read_json(base(series)/'preservation.json')
 for slug,record in receipt['source_bodies'].items():
  raw,units=source(series,slug)
  assert sha(raw)==record['sha256'],(slug,'Chinese source changed')
  assert len(units)==record['units'],slug
 for name,digest in receipt['traditional_files'].items():
  # The index dictionary has a separately recorded editorial note addition.
  expected=receipt.get('updated_traditional_files',{}).get(name,digest)
  assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
 return receipt

def load(series,lang,slug):
 data=read_json(base(series)/'translations'/lang/(slug+'.json'))
 raw,units=source(series,slug)
 assert data['language']==lang and data['slug']==slug
 assert data['source_sha256']==sha(raw),(lang,slug,'stale source')
 assert len(data['body'])==len(units),(lang,slug,'coverage')
 assert data.get('title') and data.get('deck') and data.get('review'),(lang,slug,'missing metadata/review')
 for index,(zh,foreign) in enumerate(zip(units,data['body']),1):
  doc=Document(foreign)
  nodes=[n for n in doc.root.children if isinstance(n,Node)]
  assert len(nodes)==1 and nodes[0].tag in ('p','h2'),(lang,slug,index,'unit type')
  assert nodes[0].text().strip(),(lang,slug,index,'empty')
  assert all(n.tag in ('root','p','h2','strong','em','a','br','sup','sub') for n in doc.root.walk()),(lang,slug,index,'unreviewed markup')
  assert '<strong>' not in zh or foreign.count('<strong>')==zh.count('<strong>'),(lang,slug,index,'lost emphasis')
  assert not re.search(r'\[VERIFY|TODO|TBD|PLACEHOLDER',foreign),(lang,slug,index,'placeholder')
 return data

def patch(text,changes):
 for start,end,value in sorted(changes,reverse=True):text=text[:start]+value+text[end:]
 return text

def inner(node,value):return (node.open_end,node.close_start,value)
def metadata(text,description):
 return re.sub(r'(<meta (?:name|property)="(?:description|og:description)" content=")[^"]*(")',lambda m:m[1]+html.escape(description,quote=True)+m[2],text)

def translated_links(prose,lang,source_units,directory):
 # Resolve the original link targets, regardless of whether an editor used the
 # source-relative or destination-relative form while drafting.
 origins=re.findall(r'href="([^"]+)"',''.join(source_units))
 translated=re.findall(r'href="([^"]+)"',prose)
 assert len(origins)==len(translated),(lang,'source links lost or invented',origins,translated)
 iterator=iter(origins)
 def replace(m):
  href=html.unescape(next(iterator));u=urlsplit(href)
  if lang!='en' and not (u.scheme or u.netloc or href.startswith(('#','/'))):
   target=(directory/u.path).resolve();local=target.parent/lang/target.name
   if local.is_file():
    import os
    href=os.path.relpath(local,directory/lang)
    if u.fragment:href+='#'+u.fragment
   else:href='../'+href
  return 'href="'+html.escape(href,quote=True)+'"'
 return re.sub(r'href="([^"]+)"',replace,prose)

def render(series,partial=False):
 receipt=preserved(series)
 slugs=list(receipt['source_bodies'])
 outputs={}
 for lang in LANGS:
  data={}
  for slug in slugs:
   path=base(series)/'translations'/lang/(slug+'.json')
   if partial and not path.exists():continue
   data[slug]=load(series,lang,slug)
  if not data:continue
  directory=folder(series) if lang=='en' else folder(series)/lang
  texts={p:p.read_text() for p in directory.glob('*.html')}
  # Current headings are discovery/nav aliases. Replace complete text values,
  # longest first, so changing a translated title does not leave stale neighbors.
  aliases={}
  for slug,item in data.items():
   p=directory/(slug+'.html');doc=Document(texts[p])
   h=one(doc.root.walk(),lambda n:n.tag=='h1' and (lang!='en' or n.has('lang-en')),(lang,slug,'title'))
   old=doc.raw(h,inner=True);new=html.escape(item['title'],quote=False)
   if old!=new:aliases[old]=new
  for p,text in texts.items():
   for old,new in sorted(aliases.items(),key=lambda x:len(x[0]),reverse=True):text=text.replace(old,new)
   texts[p]=text
  for slug,item in data.items():
   p=directory/(slug+'.html');text=texts[p];doc=Document(text)
   node=one(doc.root.walk(),lambda n:n.has('essay-body') and (lang!='en' or n.has('lang-en')),(lang,slug,'body'))
   body=translated_links('\n\n'.join(item['body']),lang,source(series,slug)[1],folder(series))
   text=patch(text,[inner(node,body)])
   if lang=='en':
    # Preserve the existing Chinese description exactly, replacing only English.
    zhindex=Document((folder(series)/'index.html').read_text())
    card=one(zhindex.root.walk(),lambda n:n.tag=='a' and n.attrs.get('href')==slug+'.html' and any(c.has('entry-title-zh') for c in n.walk()),slug)
    deck=one(card.walk(),lambda n:n.has('entry-desc'),slug).text()
    text=metadata(text,deck+' '+item['deck'])
   else:
    text=metadata(text,item['deck'])
    doc=Document(text);changes=[]
    for node in doc.root.walk():
     if node.has('essay-series'):
      # Edition labels never substitute for the actual book/series title.
      current=node.text();prefix=current.rsplit(' · ',1)[0]
      changes.append(inner(node,html.escape(prefix+' · '+LABELS[lang])))
    text=patch(text,changes)
   texts[p]=text
  ip=directory/'index.html';text=texts[ip];doc=Document(text);changes=[]
  for node in doc.root.walk():
   if node.tag=='a' and node.has('entry-row'):
    slug=Path(node.attrs.get('href','')).stem
    if slug not in data:continue
    if lang=='en' and not any(n.has('entry-title-en') for n in node.walk()):continue
    deck=one(node.walk(),lambda n:n.has('entry-desc'),(lang,slug,'index deck'))
    changes.append(inner(deck,html.escape(data[slug]['deck'])))
  text=patch(text,changes)
  shared_path=base(series)/'translations'/lang/'index.json'
  shared=read_json(shared_path) if shared_path.exists() else None
  if shared is not None:
   doc=Document(text);changes=[]
   if lang=='en':
    section=one(doc.root.walk(),lambda n:n.has('lang-en') and any(c.has('series-title') for c in n.children if isinstance(c,Node)),'English intro')
   else:section=one(doc.root.walk(),lambda n:n.tag=='main','Index main')
   desc=one(section.walk(),lambda n:n.has('series-desc'),(lang,'intro'))
   # Foreign old introductions are <p>; multiple source paragraphs need a div.
   prose=''.join('<p>'+p+'</p>' for p in shared['intro'])
   changes.append((desc.start,desc.end,'<div class="series-desc">'+prose+'</div>'))
   if lang=='en':
    note=one(section.walk(),lambda n:n.has('edition-note'),'English edition note')
    changes.append(inner(note,EN_NOTE))
   else:
    for n in section.walk():
     if n.has('series-label'):changes.append(inner(n,html.escape(n.text().rsplit(' · ',1)[0]+' · '+LABELS[lang])))
   text=patch(text,changes)
   if lang!='en':
    text=metadata(text,re.sub('<[^>]+>','',shared['intro'][0]))
    for p in texts:
     if p==ip:continue
     doc=Document(texts[p]);changes=[]
     for node in doc.root.walk():
      if node.has('source-note') or node.has('essay-footer-note'):
       changes.append(inner(node,'<em>'+html.escape(shared['source_note'])+'</em>'))
     texts[p]=patch(texts[p],changes)
    doc=Document(text);changes=[]
    for node in doc.root.walk():
     if node.has('source-note') or node.has('essay-footer-note'):
      changes.append(inner(node,html.escape(shared['source_note'])))
    text=patch(text,changes)
  if lang=='en' and shared:
   doc=Document(text);changes=[]
   zhsection=one(doc.root.walk(),lambda n:n.has('lang-zh') and any(c.has('series-title') for c in n.children if isinstance(c,Node)),'Chinese intro')
   note=one(zhsection.walk(),lambda n:n.has('edition-note'),'Chinese edition note')
   changes.append(inner(note,ZH_NOTE));text=patch(text,changes)
   for p in texts:
    if p==ip:continue
    doc=Document(texts[p]);changes=[]
    for block in doc.root.walk():
     if block.has('series-note'):
      note=one(block.walk(),lambda n:n.has('lang-en'),'English source note')
      changes.append(inner(note,html.escape(shared['source_note'])))
    texts[p]=patch(texts[p],changes)
  texts[ip]=text
  for p,text in texts.items():
   if lang=='en':
    text=re.sub(r'<script>\s*\(function\(\)\{\s*var saved=localStorage\.getItem.*?</script>', '<script src="../../classic-reading.js"></script>',text,flags=re.S)
    assert text.count('src="../../classic-reading.js"')==1,(p,'primary language script')
   else:
    # Query links work even when storage is blocked; no unsafe inline writes.
    def primary_link(match):
     tag=match[0]
     code=re.search(r"setItem\('nd_lang','([^']+)'\)",tag)[1]
     tag=re.sub(r'onclick="[^"]*"','',tag)
     return re.sub(r'href="([^"?]+)(?:\?lang=[^"]+)?"',lambda m:'href="'+m[1]+'?lang='+code+'"',tag)
    text=re.sub(r'<a\b[^>]*onclick="localStorage\.setItem[^>]*>',primary_link,text)
   responsive='<style id="classic-full-reader">.series-container{width:100%;min-width:0}.series-title,.essay-header h1,.entry-title,.entry-title-en,.entry-title-zh,.essay-body,.series-nav-title{overflow-wrap:anywhere}.entry-row,.series-nav a,.republic-nav a{min-width:0}</style>'
   text=re.sub(r'<style id="classic-full-reader">.*?</style>','',text,flags=re.S)
   outputs[p]=text.replace('</head>',responsive+'</head>',1)
 return outputs

def main():
 p=argparse.ArgumentParser();p.add_argument('series',choices=SUPPORTED);p.add_argument('--check',action='store_true');p.add_argument('--partial',action='store_true');args=p.parse_args()
 outputs=render(args.series,args.partial)
 stale=[p for p,s in outputs.items() if p.read_text()!=s]
 if args.check:
  for p in stale:print('STALE',p.relative_to(ROOT))
  if stale:return 1
 else:
  for p in stale:p.write_text(outputs[p])
 print(('Checked' if args.check else 'Rendered'),len(outputs),'pages;',len(stale),'changed')
 return 0
if __name__=='__main__':raise SystemExit(main())
