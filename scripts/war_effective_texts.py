#!/usr/bin/env python3
"""Source-bound War author corrections and independent linguistic repair overlays.

Frozen source/manuscript files remain the evidence for the original readings.
Only exact before/after units are overlaid; final release approval must bind every
supporting receipt and effective body hash. This module itself never writes pages.
"""
from __future__ import annotations
if not __debug__:
 raise RuntimeError('Optimized Python is not supported: editorial guards require assertions')
import copy,hashlib,json,re
from pathlib import Path
from prepare_action_sources import Document,Node
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/war-full'
AUTHOR=BASE/'author-amendments'
ZH_MANIFEST=AUTHOR/'2026-11-10-zh.json'
AUTHOR_UNITS={('ep03',21),('ep03',22),('ep03',42),('ep03',50),('ep03',51),('ep04',19),('ep04',20),('ep06',30)}
AUTHOR_LANGS=('zh','zh-hant','en','ja','de','fr','es','ko')
def read(path):return json.loads(path.read_text())
def file_sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def sha(text):return hashlib.sha256(text.encode()).hexdigest()
def unit_sha(units):return sha(json.dumps(units,ensure_ascii=False,separators=(',',':')))
def structure(text):return [(n.tag,n.attrs) for n in Document(text).root.walk()]
def same_markup(before,after,label):
 assert structure(before)==structure(after) and re.findall(r'</?[A-Za-z][^>]*>',before)==re.findall(r'</?[A-Za-z][^>]*>',after),(label,'markup changed')
def index_of(change):
 values=[]
 for key in ('unit','unit_1based','body_index','index'):
  if key in change:assert type(change[key]) is int,'Unit index must be an integer'
 for key in ('unit','unit_1based'):
  if key in change:values.append(change[key]-1)
 if 'body_index' in change:values.append(change['body_index'])
 if 'index' in change:values.append(change['index'])
 assert values and all(type(v) is int and v==values[0] for v in values),'Missing/inconsistent unit index'
 return values[0]
def overlay_units(original,changes,label):
 result=list(original);seen=set()
 for c in changes:
  i=index_of(c);assert 0<=i<len(result),(label,'unit outside body',i)
  assert i not in seen,(label,'duplicate unit',i);seen.add(i)
  assert result[i] in (c['before'],c['after']),(label,'exact before/after mismatch',i)
  same_markup(c['before'],c['after'],(label,i))
  result[i]=c['after']
 return result

def author_changes(slug,lang):
 path=ZH_MANIFEST if lang=='zh' else AUTHOR/(lang+'.json')
 record=read(path)
 assert record['language']==lang,(lang,'author language mismatch')
 coordinates=[(c['slug'],c['unit']) for c in record['changes']]
 assert len(coordinates)==8 and set(coordinates)==AUTHOR_UNITS,(lang,'author scope/coverage mismatch')
 if lang!='zh':assert record['zh_manifest_sha256']==file_sha(ZH_MANIFEST),(lang,'stale author source')
 changes=[c for c in record['changes'] if c['slug']==slug]
 source=read(BASE/'sources'/(slug+'.json'))
 zh={(c['slug'],c['unit']):c for c in read(ZH_MANIFEST)['changes']}
 for c in changes:
  assert c['source_sha256']==source['source_sha256'],(lang,slug,'stale original source')
  if lang!='zh':
   expected=zh[(slug,c['unit'])]['after']
   if 'zh_after_sha256' in c:assert c['zh_after_sha256']==sha(expected),(lang,slug,'author delta hash mismatch')
   else:assert c.get('zh_after')==expected,(lang,slug,'author delta text mismatch')
 return changes

def source_units(slug):
 return overlay_units(read(BASE/'sources'/(slug+'.json'))['body_zh'],author_changes(slug,'zh'),(slug,'zh author'))

def body_overlay(slug,lang,body,extra_changes=()):
 doc=Document(body);nodes=[n for n in doc.root.children if isinstance(n,Node)]
 units=overlay_units([doc.raw(n) for n in nodes],author_changes(slug,lang),(slug,lang,'author'))
 units=overlay_units(units,extra_changes,(slug,lang,'independent linguistic'))
 for n,value in reversed(list(zip(nodes,units))):
  body=body[:n.start]+value+body[n.end:]
 return body

def review_path(lang,slug):return BASE/'reviews'/(lang+'-'+slug+'.json')
def review_record(lang,slug):
 path=review_path(lang,slug)
 if not path.exists():return {}
 receipt=read(path)
 source=read(BASE/('index-source.json' if slug=='index' else 'sources/'+slug+'.json'))
 assert receipt['source_sha256']==source['source_sha256'],(lang,slug,'stale review source')
 manuscript=BASE/'translations'/lang/(slug+'.json')
 assert receipt['manuscript_sha256']==file_sha(manuscript),(lang,slug,'stale review manuscript')
 return receipt

def metadata_overlay(item,changes,label):
 item=copy.deepcopy(item);seen=set()
 for c in changes:
  field=c['field']
  if field=='body':continue
  if field=='intro':key=('intro',index_of(c));target=item['intro'];index=key[1]
  elif field in ('title','deck','source_note'):
   key=(field,);target=item;index=field
  else:
   m=re.fullmatch(r'groups\[([01])\]\.(eyebrow|title|note)',field)
   assert m,(label,'unsupported metadata field',field)
   key=('groups',int(m[1]),m[2]);target=item['groups'][int(m[1])];index=m[2]
  assert key not in seen,(label,'duplicate metadata patch',key);seen.add(key)
  assert target[index] in (c['before'],c['after']),(label,'metadata context mismatch',key)
  same_markup(c['before'],c['after'],(label,key))
  target[index]=c['after']
 return item

def foreign(lang,slug,item):
 receipt=review_record(lang,slug);changes=receipt.get('changes',[]);item=copy.deepcopy(item)
 if slug!='index':
  item['body']=overlay_units(item['body'],author_changes(slug,lang),(slug,lang,'author'))
  item['body']=overlay_units(item['body'],[c for c in changes if c.get('field','body')=='body'],(slug,lang,'review'))
 return metadata_overlay(item,[c for c in changes if c.get('field','body')!='body'],(slug,lang))

def supporting_hashes(lang,slugs):
 paths=[ZH_MANIFEST,AUTHOR/(lang+'.json')]
 paths += [review_path(lang,s) for s in ('index',*slugs)]
 paths += [BASE/'reviews'/('en-second-summary.json' if lang=='en' else lang+'-full-review.json')]
 if lang=='en':paths += [BASE/'reviews/en-second'/(s+'.json') for s in ('index',*slugs)]
 return {str(p.relative_to(ROOT)):file_sha(p) for p in paths}

def english_second(slug):
 path=BASE/'reviews/en-second'/(slug+'.json')
 if not path.exists():return {}
 receipt=read(path)
 assert receipt.get('independent') is True and receipt.get('all_units_read') is True,(slug,'English independent reading missing')
 source_path=BASE/('index-source.json' if slug=='index' else 'sources/'+slug+'.json')
 assert receipt['source_file_sha256']==file_sha(source_path),(slug,'English second source file stale')
 assert receipt['source_sha256']==read(source_path)['source_sha256'],(slug,'English second source stale')
 first=review_path('en',slug)
 assert receipt['first_review_sha256']==file_sha(first),(slug,'English second review stale')
 assert receipt['zh_author_manifest_sha256']==file_sha(ZH_MANIFEST),(slug,'English second source patch stale')
 assert receipt['en_author_manifest_sha256']==file_sha(AUTHOR/'en.json'),(slug,'English second author patch stale')
 return receipt

def english_metadata(slug):
 source=read(BASE/'sources'/(slug+'.json'))
 item={'title':source['title_en'],'deck':source['deck_en']}
 first=read(review_path('en',slug))
 item=metadata_overlay(item,first.get('metadata_changes',[]),(slug,'en first metadata'))
 return metadata_overlay(item,[c for c in english_second(slug).get('changes',[]) if c.get('field','body')!='body'],(slug,'en second metadata'))

def allowed_chinese_hashes(slug,original_hash):
 result={original_hash};path=AUTHOR/'original-bodies.json'
 original=read(path).get(slug,{}).get('zh') if path.exists() else None
 if original is not None:
  assert sha(original)==original_hash,(slug,'archived Chinese changed')
  result.add(sha(body_overlay(slug,'zh',original)))
 return result

def traditional_hashes(name,original_hash):
 result={original_hash};path=AUTHOR/'traditional-patches.json'
 if path.exists():
  receipt=read(path).get(name)
  if receipt:
   assert receipt['before_sha256']==original_hash,'Traditional baseline mismatch'
   result.add(receipt['after_sha256'])
 return result

def integration_input_paths():
 slugs=(*(f'ep{i:02d}' for i in range(1,8)),*(f'if{i:02d}' for i in range(1,9)),'if-conclusion')
 paths=[BASE/name for name in ('preservation.json','baseline-pages.json','english-baseline-bodies.json','index-source.json','index-baseline.html')]
 paths += [BASE/'sources'/(slug+'.json') for slug in slugs]
 paths += [AUTHOR/name for name in ('2026-11-10-zh.json','original-bodies.json','zh-hant-review.json','traditional-patches.json')]
 paths += [AUTHOR/(lang+'.json') for lang in AUTHOR_LANGS if lang!='zh']
 paths += [AUTHOR/'baseline-traditional'/(slug+'.js') for slug in ('ep03','ep04','ep06')]
 paths += [BASE/'reviews'/'author-amendments-proposed.json']
 for lang in ('ja','de','fr','es','ko','en'):
  paths += [review_path(lang,slug) for slug in ('index',*slugs)]
  paths += [BASE/'reviews'/(lang+'.json')]
  if lang!='en':paths += [BASE/'translations'/lang/(slug+'.json') for slug in ('index',*slugs)]
  if lang in ('ja','de','fr','es','ko'):paths += [BASE/'reviews'/(lang+'-full-review.json')]
 paths += [BASE/'reviews/en-second'/(slug+'.json') for slug in ('index',*slugs)]
 paths += [BASE/'reviews/en-second-summary.json']
 paths += [ROOT/'scripts'/name for name in ('war_effective_texts.py','build_war_full_editions.py','prepare_war_author_traditional.py','validate_war_manuscripts.py')]
 return paths

def verify_author_traditional():
 receipt=read(AUTHOR/'zh-hant-review.json')
 assert receipt['status']=='passed' and receipt.get('independent') is True,'Traditional author review missing'
 assert receipt['zh_manifest_sha256']==file_sha(ZH_MANIFEST),'Traditional source review stale'
 assert receipt['hant_manifest_sha256']==file_sha(AUTHOR/'zh-hant.json'),'Traditional manuscript review stale'
 assert receipt.get('all_8_units_read') is True and receipt.get('units_read')==8,'Traditional coverage missing'
 integration=read(AUTHOR/'integration-review.json')
 assert integration['status']=='passed' and integration.get('independent') is True and not integration['unresolved'],'Author integration incomplete'
 assert set(integration['input_sha256s'])=={str(p.relative_to(ROOT)) for p in integration_input_paths()},'Author integration input coverage incomplete'
 mappings=integration['author_mapping_checks']
 assert len(mappings)==64 and {(c['language'],c['slug'],c['unit']) for c in mappings}=={(lang,slug,unit) for lang in AUTHOR_LANGS for slug,unit in AUTHOR_UNITS},'Author integration mapping coverage incomplete'
 for c in mappings:
  change=next(x for x in author_changes(c['slug'],c['language']) if x['unit']==c['unit'])
  assert c['before_sha256']==sha(change['before']) and c['after_sha256']==sha(change['after']) and c['exact_before_match'] is True and c['tags_preserved'] is True,'Author integration mapping stale'
 for name,digest in integration['input_sha256s'].items():
  assert file_sha(ROOT/name)==digest,(name,'Author integration stale')
 for name,r in read(AUTHOR/'traditional-patches.json').items():
  assert file_sha(ROOT/name)==r['after_sha256'],(name,'Traditional correction not applied')
