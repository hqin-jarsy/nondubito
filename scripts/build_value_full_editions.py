#!/usr/bin/env python3
"""Render complete Value Theory translations from reviewed local manuscripts.

This renderer never creates prose. Chinese, retained English, and Traditional
Chinese dictionaries are guarded by hashes. Exact structural parity is a useful
coverage guard, not an assertion of semantic equivalence. Publication additionally
requires independent language review receipts tied to the actual input hashes.
"""
from __future__ import annotations
if not __debug__:
 raise RuntimeError("Optimized Python is not supported: Value Theory safety checks require assertions")
import argparse, hashlib, html, json, re
from pathlib import Path
from prepare_action_sources import Document, Node, one

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/sae-value-full'
DIRECTORY=ROOT/'essays/sae-value'
LANGS=('ja','de','fr','es','ko')
SLUGS=('prequel',*(f'ep{i:02d}' for i in range(1,7)),'prospect')
CITATION_LABELS={'ja':'学術原論文：','de':'Wissenschaftlicher Originaltext:','fr':'Article scientifique original :','es':'Artículo académico original:','ko':'학술 원문:'}
LABELS={'ja':'日本語全文訳','de':'Vollständige deutsche Übersetzung','fr':'Traduction française intégrale','es':'Traducción española íntegra','ko':'한국어 완역'}
CSS='''<style id="value-full-reader">.series-container{width:100%;min-width:0}.series-title,.essay-header h1,.entry-title,.entry-title-en,.entry-title-zh,.essay-body,.series-nav-title{overflow-wrap:anywhere}.entry-row,.series-nav a{min-width:0}.table-scroll{overflow-x:auto;max-width:100%;margin:1.6rem 0}.v-table{overflow-wrap:normal;width:100%;border-collapse:collapse;font-family:var(--sans);font-size:.82rem;min-width:32rem}.v-table th,.v-table td{padding:.55rem .7rem;border:1px solid var(--cream-border);text-align:left;vertical-align:top}.v-table thead th{font-size:.72rem;color:var(--ink-muted);font-weight:600}.v-table td:first-child{font-weight:600}.essay-body.ko{word-break:keep-all}@media(max-width:620px){.v-table{font-size:.75rem;min-width:26rem}}</style>'''

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

def english_body(slug):
 original=read(BASE/'english-baseline-bodies.json')[slug]
 source=read(BASE/'sources'/(slug+'.json'))
 assert sha(original)==source['english_sha256'],(slug,'English baseline drift')
 path=BASE/'reviews'/('en-'+slug+'.json')
 receipt=read(path) if path.exists() else {}
 changes=receipt.get('changes',[])
 if not changes:return original
 assert receipt['source_sha256']==source['source_sha256'],(slug,'English correction stale')
 doc=Document(original);units=[n for n in doc.root.children if isinstance(n,Node)];edits=[];seen=set()
 for item in changes:
  i=item['unit']-1;assert i not in seen,(slug,'duplicate correction');seen.add(i)
  assert doc.raw(units[i])==item['before']==source['body_en'][i],(slug,i,'English correction context')
  assert structure(item['before'])==structure(item['after']),(slug,i,'English correction markup')
  edits.append((units[i].start,units[i].end,item['after']))
 return patch(original,edits)

def preserved():
 record=read(BASE/'preservation.json')
 for slug in SLUGS:
  doc=Document((DIRECTORY/(slug+'.html')).read_text());source=read(BASE/'sources'/(slug+'.json'))
  for lang,key in [('zh','sha256'),('en','english_sha256')]:
   node=one(doc.root.walk(),lambda n:n.has('essay-body','lang-'+lang),(slug,lang))
   current=doc.raw(node,inner=True)
   if lang=='zh':
    assert sha(current)==record['source_bodies'][slug][key],(slug,lang,'source changed')
    assert raw_units(doc,node)==source['body_'+lang],(slug,lang,'snapshot drift')
   else:
    assert sha(current) in {record['source_bodies'][slug][key],sha(english_body(slug))},(slug,lang,'unrecognized English edits')
 for name,digest in record['traditional_files'].items():assert file_sha(ROOT/name)==digest,(name,'Traditional Chinese changed')
 return record

def load(lang,slug):
 path=BASE/'translations'/lang/(slug+'.json');data=read(path);source=read(BASE/'sources'/(slug+'.json'))
 assert data['language']==lang and data['slug']==slug,(lang,slug,'identity')
 assert data['source_sha256']==source['source_sha256'],(lang,slug,'stale source')
 assert data.get('title') and data.get('deck') and data.get('review'),(lang,slug,'metadata')
 assert len(data['body'])==len(source['body_zh']),(lang,slug,'unit coverage')
 for i,(zh,foreign) in enumerate(zip(source['body_zh'],data['body']),1):
  assert structure(zh)==structure(foreign),(lang,slug,i,'structural coverage')
  for tag in ('strong','em'):assert zh.count('<'+tag+'>')==foreign.count('<'+tag+'>'),(lang,slug,i,'emphasis')
  assert Document(foreign).root.text().strip(),(lang,slug,i,'empty unit')
  source_refs=re.findall(r'\d{2}DD',zh);target_refs=re.findall(r'\d{2}DD',foreign)
  # Chinese sometimes spells out the 14-to-15 bridge; rendering its DD
  # labels explicitly is a faithful expansion, not an added reference.
  valid_refs=[source_refs]
  if not source_refs and '十四到十五' in zh:valid_refs.append(['14DD','15DD'])
  assert target_refs in valid_refs,(lang,slug,i,'DD references')
  assert not re.search(r'\[VERIFY|TODO|TBD|PLACEHOLDER',foreign),(lang,slug,i,'placeholder')
 return data

def verify_reviews():
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
  if lang!='en':assert receipt['index_sha256']==file_sha(BASE/'translations'/lang/'index.json'),(lang,'index review stale')


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

def render(partial=False):
 preserved()
 if not partial:verify_reviews()
 outputs={}
 # Chinese prose and Traditional dictionaries remain unchanged; existing English
 # receives only source-bound reviewed patches. The shared controller makes
 # explicit language links survive unavailable storage.
 for slug in ('index',*SLUGS):
  path=DIRECTORY/(slug+'.html');text=path.read_text()
  if slug!='index':
   doc=Document(text);node=one(doc.root.walk(),lambda n:n.has('essay-body','lang-en'),slug)
   text=patch(text,[inner(node,english_body(slug))])
  text=re.sub(r'<script>\s*\(function\(\)\{\s*var saved=localStorage\.getItem.*?</script>','<script src="../../classic-reading.js"></script>',text,flags=re.S)
  assert text.count('src="../../classic-reading.js"')==1,(slug,'reader controller')
  text=re.sub(r'<style id="value-full-reader">.*?</style>','',text,flags=re.S)
  outputs[path]=text.replace('</head>',CSS+'</head>',1)
 for lang in LANGS:
  available=[slug for slug in SLUGS if (BASE/'translations'/lang/(slug+'.json')).exists()]
  if partial:
   available=[slug for slug in available if len(read(BASE/'translations'/lang/(slug+'.json')).get('body',[]))==len(read(BASE/'sources'/(slug+'.json'))['body_zh'])]
  else:assert available==list(SLUGS),(lang,'missing manuscripts')
  if not available:continue
  items={slug:load(lang,slug) for slug in available}
  directory=DIRECTORY/lang
  texts={p:p.read_text() for p in directory.glob('*.html')}
  aliases={}
  for slug,item in items.items():
   doc=Document(texts[directory/(slug+'.html')]);title=one(doc.root.walk(),lambda n:n.tag=='h1',(lang,slug,'title'))
   old=doc.raw(title,inner=True);new=html.escape(item['title'],quote=False)
   if old!=new:aliases[old]=new
  for path,text in texts.items():
   for old,new in sorted(aliases.items(),key=lambda x:len(x[0]),reverse=True):text=text.replace(old,new)
   texts[path]=text
  shared_path=BASE/'translations'/lang/'index.json';shared=read(shared_path) if shared_path.exists() else None
  if not partial:assert shared and shared.get('title') and shared.get('intro') and shared.get('source_note'),lang
  if shared and shared.get('title'):
   texts[directory/'index.html']=index_title(texts[directory/'index.html'],shared['title'])
  for slug,item in items.items():
   path=directory/(slug+'.html');text=texts[path];doc=Document(text)
   node=one(doc.root.walk(),lambda n:n.has('essay-body'),(lang,slug,'body'))
   text=patch(text,[inner(node,'\n'+'\n\n'.join(item['body'])+'\n')])
   text=re.sub(r'(<meta (?:name|property)="(?:description|og:description)" content=")[^"]*(")',lambda m:m[1]+html.escape(item['deck'],quote=True)+m[2],text)
   # Retain the verified academic paper and DOI targets rather than a
   # generic unlinked source claim. Bibliographic titles remain as published.
   primary=Document((DIRECTORY/(slug+'.html')).read_text())
   citations=one(primary.root.walk(),lambda n:n.has('method-citations'),slug)
   citation=one(citations.walk(),lambda n:n.tag=='p' and n.has('lang-en'),slug)
   prose=primary.raw(citation,inner=True).replace('Academic original:',CITATION_LABELS[lang],1)
   block='<div class="method-citations value-full-citations"><p>'+prose+'</p></div>'
   text=re.sub(r'<div class="method-citations value-full-citations">.*?</div>','',text,flags=re.S)
   text=text.replace('<div class="essay-footer-note">',block+'<div class="essay-footer-note">',1)
   texts[path]=text
  ip=directory/'index.html';doc=Document(texts[ip]);changes=[]
  for node in doc.root.walk():
   if node.has('entry-row'):
    slug=Path(node.attrs.get('href','')).stem
    if slug in items:
     deck=one(node.walk(),lambda n:n.has('entry-desc'),(lang,slug,'deck'))
     changes.append(inner(deck,html.escape(items[slug]['deck'])))
   if shared and node.has('series-desc'):
    assert all(isinstance(p,str) and p for p in shared['intro']),lang
    prose=''.join(p if p.lstrip().startswith('<p') else '<p>'+p+'</p>' for p in shared['intro'])
    changes.append((node.start,node.end,'<div class="series-desc">'+prose+'</div>'))
  texts[ip]=patch(texts[ip],changes)
  for path,text in texts.items():
   if path!=ip and path.stem not in items:continue
   doc=Document(text);changes=[]
   for node in doc.root.walk():
    if node.has('essay-series') or node.has('series-label'):
     changes.append(inner(node,html.escape(node.text().rsplit(' · ',1)[0]+' · '+LABELS[lang])))
    if shared and (node.has('source-note') or node.has('essay-footer-note')):
     changes.append(inner(node,html.escape(shared['source_note'])))
   text=reader_routes(patch(text,changes))
   text=re.sub(r'<style id="value-full-reader">.*?</style>','',text,flags=re.S)
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
