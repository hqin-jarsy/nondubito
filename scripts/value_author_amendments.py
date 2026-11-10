#!/usr/bin/env python3
"""Apply narrowly authorised, independently reviewed Value Theory errata.

Original translation/source receipts remain immutable evidence for the restoration
commit. A second, source-bound review gate covers only these later author deltas.
"""
from __future__ import annotations
if not __debug__:
 raise RuntimeError('Optimized Python is not supported: author amendments require safety assertions')
import hashlib,json,re
from pathlib import Path
from prepare_action_sources import Document,Node,one
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'data/sae-value-full/author-amendments'
MANIFEST=BASE/'2026-11-10.json'
def read(p):return json.loads(p.read_text())
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def file_sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def patches(slug,language):
 if not MANIFEST.exists():return []
 return [x for x in read(MANIFEST)['patches'] if x['slug']==slug and x['language']==language]
def structure(s):return [(n.tag,n.attrs) for n in Document(s).root.walk()]
def units(slug,language,original):
 result=list(original);seen=set()
 for item in patches(slug,language):
  i=item['unit']-1;assert i not in seen,'duplicate author amendment';seen.add(i)
  assert 0<=i<len(result),'author amendment index'
  assert result[i] in (item['before'],item['after']),(slug,language,item['unit'],'author amendment context mismatch')
  assert structure(item['before'])==structure(item['after']),'author amendment changes markup'
  result[i]=item['after']
 return result

def body(slug,language,original):
 doc=Document(original);nodes=[n for n in doc.root.children if isinstance(n,Node)]
 expected=units(slug,language,[doc.raw(n) for n in nodes]);edits=[]
 for n,new in zip(nodes,expected):
  if doc.raw(n)!=new:edits.append((n.start,n.end,new))
 for start,end,new in sorted(edits,reverse=True):original=original[:start]+new+original[end:]
 return original

def original_bodies():
 return read(BASE/'original-bodies.json') if (BASE/'original-bodies.json').exists() else {}

def allowed_chinese_hashes(slug,original_hash):
 result={original_hash};original=original_bodies().get(slug,{}).get('zh')
 if original is not None:
  assert sha(original)==original_hash,'original Chinese archive drift'
  result.add(sha(body(slug,'zh',original)))
 return result

def traditional_hashes(name,original_hash):
 result={original_hash};path=BASE/'traditional-patches.json'
 if path.exists():
  record=read(path).get(name)
  if record:
   assert record['before_sha256']==original_hash,'Traditional baseline mismatch'
   result.add(record['after_sha256'])
 return result

def verify():
 if not MANIFEST.exists():return
 receipt=read(BASE/'review.json')
 assert receipt['status']=='passed' and receipt['independent'] is True and receipt['all_changed_units_read'] is True,'Author amendment review missing'
 assert receipt['manifest_sha256']==file_sha(MANIFEST),'Author amendment review stale'
 assert receipt['traditional_patches_sha256']==file_sha(BASE/'traditional-patches.json'),'Traditional amendment review stale'
 for name,r in read(BASE/'traditional-patches.json').items():
  assert file_sha(ROOT/name)==r['after_sha256'],(name,'Traditional corrections not applied')
 assert not receipt['unresolved'],'Unresolved author amendment finding'
