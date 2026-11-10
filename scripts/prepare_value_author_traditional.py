#!/usr/bin/env python3
"""Update only author-approved full text-node keys in two Traditional dictionaries."""
from __future__ import annotations
if not __debug__:
 raise RuntimeError('Optimized Python is not supported: dictionary amendments require assertions')
import argparse,json,re
from pathlib import Path
import value_author_amendments as a
from prepare_action_sources import Document,Node

def texts(s):
 def walk(n):
  for x in n.children:
   if isinstance(x,Node):yield from walk(x)
   else:yield x
 return list(walk(Document(s).root))

def outputs():
 result={};receipts={};manifest=a.read(a.MANIFEST)
 for slug in sorted({x['slug'] for x in manifest['patches'] if x['language']=='zh'}):
  path=a.ROOT/'essays/sae-value/zh-hant-data'/(slug+'.js')
  baseline=a.BASE/'baseline-traditional'/(slug+'.js');raw=baseline.read_text()
  match=re.search(r'var variants = (\{.*?\});\n',raw,re.S);assert match,'Dictionary not found'
  old=json.loads(match[1]);variants=dict(old);changes=[]
  hant={x['unit']:x for x in a.patches(slug,'zh-hant')}
  for x in a.patches(slug,'zh'):
   h=hant[x['unit']];parts=[texts(z) for z in (x['before'],x['after'],h['before'],h['after'])]
   assert len({len(z) for z in parts})==1,'Changed text-node shape'
   for before,after,hbefore,hafter in zip(*parts):
    assert old.get(before,before)==hbefore,(slug,x['unit'],'Traditional before differs')
    if before==after:
     assert hbefore==hafter,'Unauthorised Traditional-only change';continue
    assert before in variants,'Old complete text-node key missing'
    assert after not in variants,'New text-node key unexpectedly exists'
    del variants[before];variants[after]=hafter
    changes.append({'unit':x['unit'],'before_key':before,'before_value':hbefore,'after_key':after,'after_value':hafter})
  unchanged=set(old)-{x['before_key'] for x in changes}
  assert all(variants[k]==old[k] for k in unchanged),'Unrelated dictionary changed'
  new=raw[:match.start(1)]+json.dumps(variants,ensure_ascii=False,sort_keys=True)+raw[match.end(1):]
  result[path]=new;receipts[str(path.relative_to(a.ROOT))]={'before_sha256':a.sha(raw),'after_sha256':a.sha(new),'unchanged_entries':len(unchanged),'changes':changes}
 result[a.BASE/'traditional-patches.json']=json.dumps(receipts,ensure_ascii=False,indent=2)+'\n'
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args();out=outputs()
 receipts=json.loads(out[a.BASE/'traditional-patches.json'])
 for path,text in out.items():
  if path.name=='traditional-patches.json':continue
  r=receipts[str(path.relative_to(a.ROOT))]
  assert a.file_sha(path) in (r['before_sha256'],r['after_sha256']),'Unrecognized current dictionary edits'
 stale=[p for p,t in out.items() if not p.exists() or p.read_text()!=t]
 if args.check:
  assert not stale,('Stale Traditional author amendments',stale)
 else:
  for path,text in out.items():
   if not path.exists() or path.read_text()!=text:path.write_text(text)
 print(('Checked' if args.check else 'Prepared'),'four changed text-node mappings; all unrelated mappings retained.')
if __name__=='__main__':main()
