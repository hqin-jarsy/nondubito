#!/usr/bin/env python3
"""Render complete War Theory translations from reviewed local manuscripts.

This renderer never creates prose. Chinese, retained English, and Traditional
Chinese dictionaries are guarded by hashes. Exact structural parity is a useful
coverage guard, not an assertion of semantic equivalence. Publication additionally
requires independent language review receipts tied to the actual input hashes.
"""
from __future__ import annotations
if not __debug__:
 raise RuntimeError("Optimized Python is not supported: War Theory safety checks require assertions")
import argparse, hashlib, html, json, re
from pathlib import Path
from prepare_action_sources import Document, Node, one
from prepare_war_sources import normalized_legacy_head
from validate_war_manuscripts import load as raw_load,load_index as raw_load_index
import war_effective_texts as effective
from web_analytics import tracked_html

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/war-full'
DIRECTORY=ROOT/'essays/war'
LANGS=('ja','de','fr','es','ko')
SLUGS=(*(f'ep{i:02d}' for i in range(1,8)),*(f'if{i:02d}' for i in range(1,9)),'if-conclusion')
CITATION_LABELS={'ja':'学術原論文：','de':'Wissenschaftlicher Originaltext:','fr':'Article scientifique original :','es':'Artículo académico original:','ko':'학술 원문:'}
LABELS={'ja':'日本語全文訳','de':'Vollständige deutsche Übersetzung','fr':'Traduction française intégrale','es':'Traducción española íntegra','ko':'한국어 완역'}
CSS='''<style id="war-full-reader">.series-container{width:100%;min-width:0}.series-title,.essay-header h1,.entry-title,.entry-title-en,.entry-title-zh,.essay-body,.series-nav-title,.war-nav,.xiyou-nav-title{overflow-wrap:anywhere}.entry-row,.series-nav a,.war-nav a,.xiyou-nav a{min-width:0}.table-scroll{overflow-x:auto;max-width:100%;margin:1.6rem 0}.v-table{overflow-wrap:normal;width:100%;border-collapse:collapse;font-family:var(--sans);font-size:.82rem;min-width:32rem}.v-table th,.v-table td{padding:.55rem .7rem;border:1px solid var(--cream-border);text-align:left;vertical-align:top}.v-table thead th{font-size:.72rem;color:var(--ink-muted);font-weight:600}.v-table td:first-child{font-weight:600}.essay-body.ko{word-break:keep-all}@media(max-width:620px){.v-table{font-size:.75rem;min-width:26rem}}</style>'''

def sha(text):return hashlib.sha256(text.encode()).hexdigest()
def file_sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def patch(text,changes):
 for start,end,value in sorted(changes,reverse=True):text=text[:start]+value+text[end:]
 return text

def inner(node,text):return(node.open_end,node.close_start,text)
def raw_units(doc,node):return [doc.raw(n) for n in node.children if isinstance(n,Node)]
def structure(unit):
 doc=Document(unit)
 return [(n.tag,dict(n.attrs)) for n in doc.root.walk() if n.tag not in ('strong','em')]

def load(lang,slug):return effective.foreign(lang,slug,raw_load(lang,slug))
def load_index(lang):return effective.foreign(lang,'index',raw_load_index(lang))

def english_body(slug,amended=True):
 original=read(BASE/'english-baseline-bodies.json')[slug]
 source=read(BASE/'sources'/(slug+'.json'))
 assert sha(original)==source['english_sha256'],(slug,'English baseline drift')
 path=BASE/'reviews'/('en-'+slug+'.json')
 receipt=read(path) if path.exists() else {}
 changes=receipt.get('changes',[])
 assert receipt['source_sha256']==source['source_sha256'],(slug,'English correction stale')
 doc=Document(original);units=[n for n in doc.root.children if isinstance(n,Node)];edits=[];seen=set()
 for item in changes:
  i=effective.index_of(item);assert 0<=i<len(units),(slug,'English correction index');assert i not in seen,(slug,'duplicate correction');seen.add(i)
  assert doc.raw(units[i])==item['before']==source['body_en'][i],(slug,i,'English correction context')
  effective.same_markup(item['before'],item['after'],(slug,i,'English correction'))
  edits.append((units[i].start,units[i].end,item['after']))
 result=patch(original,edits)
 if amended:
  extra=[c for c in effective.english_second(slug).get('changes',[]) if c.get('field','body')=='body']
  result=effective.body_overlay(slug,'en',result,extra)
 return result

def preserved():
 record=read(BASE/'preservation.json')
 for slug in SLUGS:
  doc=Document(normalized_legacy_head((DIRECTORY/(slug+'.html')).read_text()));source=read(BASE/'sources'/(slug+'.json'))
  for lang,key in [('zh','sha256'),('en','english_sha256')]:
   node=one(doc.root.walk(),lambda n:n.has('essay-body','lang-'+lang),(slug,lang))
   current=doc.raw(node,inner=True)
   if lang=='zh':
    assert sha(current) in effective.allowed_chinese_hashes(slug,record['source_bodies'][slug][key]),(slug,lang,'source changed')
    assert raw_units(doc,node) in (source['body_zh'],effective.source_units(slug)),(slug,lang,'snapshot drift')
   else:
    assert sha(current) in {record['source_bodies'][slug][key],sha(english_body(slug))},(slug,lang,'unrecognized English edits')
 for name,digest in record['traditional_files'].items():assert file_sha(ROOT/name) in effective.traditional_hashes(name,digest),(name,'Traditional Chinese changed')
 return record

def verify_reviews():
 index_receipt=read(BASE/'reviews'/'en-index.json')
 assert index_receipt.get('all_units_read') is True and index_receipt.get('source_sha256')==read(BASE/'index-source.json')['source_sha256'],'English index review missing/stale'
 for lang in (*LANGS,'en'):
  receipt=read(BASE/'reviews'/(lang+'.json'))
  assert receipt['language']==lang and receipt['status']=='passed' and receipt['independent'] is True and receipt['all_units_read'] is True,lang
  assert not receipt['unresolved'],(lang,'open findings')
  assert set(receipt['source_sha256s'])==set(SLUGS),lang
  for slug in SLUGS:
   source=read(BASE/'sources'/(slug+'.json'))
   assert receipt['source_sha256s'][slug]==source['source_sha256'],(lang,slug,'source review stale')
   if lang=='en':assert receipt['english_sha256s'][slug]==sha(english_body(slug)),(lang,slug,'English review stale')
   else:assert receipt['translation_sha256s'][slug]==file_sha(BASE/'translations'/lang/(slug+'.json')),(lang,slug,'translation review stale')
  if lang=='en':assert receipt['index_review_sha256']==file_sha(BASE/'reviews'/'en-index.json'),'English index independent review stale'
  if lang!='en':assert receipt['index_sha256']==file_sha(BASE/'translations'/lang/'index.json'),(lang,'index review stale')
  assert receipt['supporting_sha256s']==effective.supporting_hashes(lang,SLUGS),(lang,'effective review support stale')
  for slug in SLUGS:
   assert receipt['effective_source_sha256s'][slug]==effective.unit_sha(effective.source_units(slug)),(lang,slug,'effective source review stale')
   if lang=='en':
    doc=Document(english_body(slug));units=[doc.raw(n) for n in doc.root.children if isinstance(n,Node)]
   else:units=load(lang,slug)['body']
   assert receipt['effective_body_sha256s'][slug]==effective.unit_sha(units),(lang,slug,'effective body review stale')
 effective.verify_author_traditional()



def reader_routes(text):
 def primary_link(m):
  tag=m[0];code=re.search(r"setItem\('nd_lang','([^']+)'\)",tag)[1]
  tag=re.sub(r'onclick="[^"]*"','',tag)
  return re.sub(r'href="([^"?]+)(?:\?lang=[^"]+)?"',lambda x:'href="'+x[1]+'?lang='+code+'"',tag)
 return re.sub(r'<a\b[^>]*onclick="localStorage\.setItem[^>]*>',primary_link,text)

def safe_preview_directory(path):
 # Resolve symlinks before any rendering or writes. A preview must never be
 # placed anywhere inside the repository, including via an external symlink.
 target=path.expanduser().resolve()
 if target.is_relative_to(ROOT.resolve()):
  raise ValueError('Preview directory must be outside the repository')
 return target

def preview_destinations(directory,outputs):
 directory=safe_preview_directory(directory)
 destinations={}
 for path,value in outputs.items():
  dest=(directory/path.relative_to(ROOT)).resolve()
  if not dest.is_relative_to(directory) or dest.is_relative_to(ROOT.resolve()):
   raise ValueError('Preview destination escapes isolated directory: '+str(dest))
  destinations[dest]=value
 return destinations

def index_title(text,title):
 doc=Document(text);heading=one(doc.root.walk(),lambda n:n.tag=='h1','index title')
 changes=[inner(heading,html.escape(title,quote=False))]
 for node in doc.root.walk():
  if node.tag=='title':changes.append(inner(node,html.escape(title+' — Non Dubito',quote=False)))
  if node.tag=='meta' and (node.attrs.get('property')=='og:title' or node.attrs.get('name')=='twitter:title'):
   attrs=dict(node.attrs);attrs['content']=title+' — Non Dubito'
   changes.append((node.start,node.end,'<meta '+' '.join(k+'="'+html.escape(v,quote=True)+'"' for k,v in attrs.items())+'>'))
 return patch(text,changes)

def english_index(text):
 # Replay exact reviewed index nodes from the frozen local baseline. The final
 # writer still rejects any unrecognised current public-page edit.
 text=(BASE/'index-baseline.html').read_text()
 assert sha(text)==read(BASE/'index-source.json')['source_sha256'],'English index baseline drift'
 path=BASE/'reviews'/'en-index.json'
 if not path.exists():return text
 receipt=read(path);assert receipt['source_sha256']==read(BASE/'index-source.json')['source_sha256'],'stale index source'
 for change in receipt.get('changes',[]):
  before,after=change['before'],change['after']
  assert before!=after,'empty index patch'
  effective.same_markup(before,after,('en','index','first review'))
  if before in text:
   assert text.count(before)==1,('ambiguous index patch',change)
   text=text.replace(before,after,1)
  else:assert text.count(after)==1,('unrecognized index copy',change)
 second=effective.english_second('index')
 for change in second.get('changes',[]):
  before,after=change['before'],change['after']
  assert before!=after and text.count(before)==1,('English index second context',change)
  effective.same_markup(before,after,('en','index','second review'))
  text=text.replace(before,after,1)
 return text

def english_title_routes(text):
 changes={}
 cards=read(BASE/'index-source.json')['cards']
 for slug in SLUGS:
  source=read(BASE/'sources'/(slug+'.json'));old=source['title_en'];new=effective.english_metadata(slug)['title']
  if old==new:continue
  short=cards[slug]['en']['title'];assert old.endswith(short),(slug,'unknown English title prefix')
  prefix=old[:-len(short)];assert new.startswith(prefix),(slug,'English title prefix changed')
  changes[old]=new;changes[short]=new[len(prefix):]
 if not changes:return text
 doc=Document(text);edits=[]
 for node in doc.root.walk():
  if node.tag=='title':
   value=node.text()
   for old,new in sorted(changes.items(),key=lambda x:-len(x[0])):value=value.replace(old,new)
   if value!=node.text():edits.append(inner(node,html.escape(value,quote=False)))
  elif node.tag=='meta' and 'content' in node.attrs:
   value=node.attrs['content']
   for old,new in sorted(changes.items(),key=lambda x:-len(x[0])):value=value.replace(old,new)
   if value!=node.attrs['content']:
    attrs=dict(node.attrs);attrs['content']=value
    edits.append((node.start,node.end,'<meta '+' '.join(k+'="'+html.escape(v,quote=True)+'"' for k,v in attrs.items())+'>'))
  elif node.has('lang-en') and node.text() in changes:
   # Exact title leaves only, never a body-wide substitution.
   assert not any(isinstance(n,Node) for n in node.children),'English title leaf changed shape'
   edits.append(inner(node,html.escape(changes[node.text()],quote=False)))
 return patch(text,edits)

def primary_index_data(lang):
 assert lang in ('zh','en'),'Primary index data supports Simplified Chinese and English'
 # This is reconstructed from the frozen local baseline and exact review
 # overlays, never from the currently published index page.
 text=(BASE/'index-baseline.html').read_text()
 if lang=='en':text=english_title_routes(english_index(text))
 doc=Document(text)
 data={'language':lang,'title':one(doc.root.walk(),lambda n:n.tag=='h1' and n.has('lang-'+lang),'index title').text()}
 intro=one(doc.root.walk(),lambda n:n.has('series-desc','lang-'+lang),'index intro')
 data['intro']=[doc.raw(n) for n in intro.children if isinstance(n,Node)]
 data['groups']=[]
 for group in [n for n in doc.root.walk() if n.has('group-head')]:
  data['groups'].append({key:doc.raw(one(group.walk(),lambda n:n.has(css,'lang-'+lang),(key,lang)),inner=True) for key,css in [('eyebrow','group-eyebrow'),('title','group-title'),('note','group-note')]})
 data['cards']={}
 for card in [n for n in doc.root.walk() if n.has('entry-row')]:
  slug=Path(card.attrs['href']).stem
  data['cards'][slug]={'title':one(card.walk(),lambda n:n.has('entry-title-'+lang),'card title').text(),'deck':one(card.walk(),lambda n:n.has('entry-desc','lang-'+lang),'card deck').text()}
 holder=one(doc.root.walk(),lambda n:n.has('source-note'),'source note')
 data['source_notes']=[doc.raw(n) for n in holder.children if isinstance(n,Node) and n.tag=='span' and n.has('lang-'+lang)]
 assert len(data['intro'])==5 and len(data['groups'])==2 and len(data['cards'])==16 and len(data['source_notes'])==2
 return data

def replace_title(text,title):
 doc=Document(text);edits=[]
 for node in doc.root.walk():
  if node.tag in ('h1','title'):
   value=title if node.tag=='h1' else title+' — Non Dubito'
   edits.append(inner(node,html.escape(value,quote=False)))
  if node.tag=='meta' and (node.attrs.get('property')=='og:title' or node.attrs.get('name')=='twitter:title'):
   attrs=dict(node.attrs);attrs['content']=title+' — Non Dubito'
   edits.append((node.start,node.end,'<meta '+' '.join(k+'="'+html.escape(v,quote=True)+'"' for k,v in attrs.items())+'>'))
 return patch(text,edits)

def article_citation(slug,lang):
 primary=Document(normalized_legacy_head((DIRECTORY/(slug+'.html')).read_text()))
 containers=[n for n in primary.root.walk() if n.has('method-citations') or n.has('essay-footer-note')]
 assert len(containers)==1,(slug,'citation container')
 original=one(containers[0].walk(),lambda n:n.has('lang-en'),slug)
 return primary.raw(original,inner=True).replace('Academic original:',CITATION_LABELS[lang],1)

@tracked_html
def render(partial=False):
 preserved()
 if not partial:verify_reviews()
 outputs={}
 for slug in ('index',*SLUGS):
  path=DIRECTORY/(slug+'.html');text=normalized_legacy_head(path.read_text())
  if slug!='index':
   doc=Document(text);en_node=one(doc.root.walk(),lambda n:n.has('essay-body','lang-en'),slug)
   zh_node=one(doc.root.walk(),lambda n:n.has('essay-body','lang-zh'),slug)
   text=patch(text,[inner(en_node,english_body(slug)),inner(zh_node,effective.body_overlay(slug,'zh',doc.raw(zh_node,inner=True)))])
  else:text=english_index(text)
  text=english_title_routes(text)
  # Both existing controller layouts are known: one spaced, one compact.
  doc=Document(text);controllers=[n for n in doc.root.walk() if n.tag=='script' and not n.attrs.get('src') and "localStorage.getItem('nd_lang')" in doc.raw(n)]
  if controllers:
   assert len(controllers)==1,(slug,'ambiguous old reader controller')
   n=controllers[0];text=patch(text,[(n.start,n.end,'<script src="../../classic-reading.js"></script>')])
  assert text.count('src="../../classic-reading.js"')==1,(slug,'reader controller')
  text=re.sub(r'<style id="war-full-reader">.*?</style>','',text,flags=re.S)
  outputs[path]=text.replace('</head>',CSS+'</head>',1)
 for lang in LANGS:
  available=[slug for slug in SLUGS if (BASE/'translations'/lang/(slug+'.json')).exists()]
  if partial:available=[slug for slug in available if len(read(BASE/'translations'/lang/(slug+'.json')).get('body',[]))==len(read(BASE/'sources'/(slug+'.json'))['body_zh'])]
  else:assert available==list(SLUGS),(lang,'missing manuscripts')
  if not available:continue
  items={slug:load(lang,slug) for slug in available};directory=DIRECTORY/lang
  shared_path=BASE/'translations'/lang/'index.json'
  shared=load_index(lang) if shared_path.exists() else None
  if not partial:assert shared,(lang,'index missing')
  ip=directory/'index.html';texts={p:p.read_text() for p in directory.glob('*.html')}
  for slug,item in items.items():
   path=directory/(slug+'.html');text=replace_title(texts[path],item['title']);doc=Document(text)
   node=one(doc.root.walk(),lambda n:n.has('essay-body'),(lang,slug,'body'))
   edits=[inner(node,'\n'+'\n\n'.join(item['body'])+'\n')]
   if lang=='ko' and not node.has('ko'):
    opening=text[node.start:node.open_end].replace('class="essay-body"','class="essay-body ko"')
    edits.append((node.start,node.open_end,opening))
   footer=one(doc.root.walk(),lambda n:n.has('essay-footer-note'),(lang,slug,'footer'))
   edits.append(inner(footer,'<em>'+html.escape(LABELS[lang])+'. '+article_citation(slug,lang)+'</em>'))
   text=patch(text,edits)
   text=re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*(")',lambda m:m[1]+html.escape(item['deck'],quote=True)+m[2],text)
   texts[path]=text
  text=texts[ip]
  if shared:text=replace_title(text,shared['title'])
  doc=Document(text);edits=[]
  for node in doc.root.walk():
   if node.has('entry-row'):
    slug=Path(node.attrs.get('href','')).stem
    if slug in items:
     title=one(node.walk(),lambda n:n.has('entry-title'),(lang,slug,'card title'))
     deck=one(node.walk(),lambda n:n.has('entry-desc'),(lang,slug,'card deck'))
     edits.extend([inner(title,html.escape(items[slug]['title'])),inner(deck,html.escape(items[slug]['deck']))])
   if shared and node.has('series-desc'):edits.append((node.start,node.end,'<div class="series-desc">'+''.join(shared['intro'])+'</div>'))
  if shared:
   groups=[n for n in doc.root.walk() if n.has('group-head')]
   assert len(groups) in (1,2),(lang,'unexpected group headings')
   def group_html(g):return '<div class="group-head"><span class="entry-num">'+g['eyebrow']+'</span><h2>'+g['title']+'</h2><p>'+g['note']+'</p></div>'
   if len(groups)==1:
    first=one(doc.root.walk(),lambda n:n.has('entry-row') and n.attrs.get('href')=='ep01.html','first group')
    first_list=one(doc.root.walk(),lambda n:n.tag=='ul' and any(x is first for x in n.walk()),'main entry list')
    edits.append((first_list.start,first_list.start,group_html(shared['groups'][0])))
    edits.append((groups[0].start,groups[0].end,group_html(shared['groups'][1])))
   else:
    edits.extend((node.start,node.end,group_html(g)) for node,g in zip(groups,shared['groups']))
   source_note=one(doc.root.walk(),lambda n:n.has('source-note'),(lang,'source note'))
   # The complete localized prose is the manuscript. Existing external links
   # remain accessible as the same primary-source references, not new targets.
   links=[doc.raw(n) for n in source_note.walk() if n.tag=='a']
   if 'war-source-links' in doc.raw(source_note):
    holder=one(source_note.walk(),lambda n:n.has('war-source-links'),'source links')
    links=[doc.raw(n) for n in holder.walk() if n.tag=='a']
   edits.append(inner(source_note,'<p>'+html.escape(shared['source_note'])+'</p><p class="war-source-links">'+' · '.join(links)+'</p>'))
  texts[ip]=patch(text,edits)
  for path,text in texts.items():
   if path!=ip and path.stem not in items:continue
   doc=Document(text);edits=[]
   for node in doc.root.walk():
    if node.has('essay-series') or node.has('series-label'):
     label=(shared['title'] if shared else 'SAE · War Theory')+' · '+LABELS[lang]
     edits.append(inner(node,html.escape(label)))
    if node.has('war-nav'):
     for link in node.children:
      if not isinstance(link,Node) or link.tag!='a':continue
      target=Path(link.attrs.get('href','')).stem
      title=items[target]['title'] if target in items else (shared['title'] if target=='index' and shared else None)
      if title:
       small=one(link.walk(),lambda n:n.tag=='small',(lang,path.stem,'nav label'))
       edits.append(inner(link,doc.raw(small)+html.escape(title)))
   text=reader_routes(patch(text,edits))
   text=re.sub(r'<style id="war-full-reader">.*?</style>','',text,flags=re.S)
   outputs[path]=text.replace('</head>',CSS+'</head>',1)
 return outputs

def write_outputs(outputs):
 baseline=read(BASE/'baseline-pages.json');previous=read(BASE/'rendered-pages.json') if (BASE/'rendered-pages.json').exists() else {}
 for path,value in outputs.items():
  name=str(path.relative_to(ROOT));current=file_sha(path)
  assert current in {baseline.get(name),previous.get(name),sha(value)},(name,'unrecognized concurrent edits; not overwritten')
 for path,value in outputs.items():
  if path.read_text()!=value:path.write_text(value)
 (BASE/'rendered-pages.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(s) for p,s in outputs.items()},indent=2)+'\n')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--preview-dir',type=Path);args=parser.parse_args()
 assert not(args.check and args.preview_dir),'Choose check or preview'
 if args.preview_dir:args.preview_dir=safe_preview_directory(args.preview_dir)
 outputs=render(partial=bool(args.preview_dir))
 if args.preview_dir:
  destinations=preview_destinations(args.preview_dir,outputs)
  for dest,value in destinations.items():
   dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(value)
  print('Preview only:',len(outputs),'pages; independent review gates not bypassed for public pages');return 0
 stale=[p for p,s in outputs.items() if p.read_text()!=s]
 if args.check:
  for p in stale:print('STALE',p.relative_to(ROOT))
  if stale:return 1
 else:write_outputs(outputs)
 print(('Checked' if args.check else 'Rendered'),len(outputs),'pages;',len(stale),'changed');return 0
if __name__=='__main__':raise SystemExit(main())
