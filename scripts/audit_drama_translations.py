#!/usr/bin/env python3
"""Verify complete, accepted drama translation batches without confusing counts with semantic review."""
import argparse
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/drama-full'
LANGS=('de','fr','es','ja','ko')
REVIEWER={'de':'ko','fr':'de','es':'fr','ja':'es','ko':'ja'}
BATCHES=((1,5),(6,10),(11,15),(16,20),(21,23))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def audit(through=23):
 manifest=json.loads((DATA/'source-manifest.json').read_text())
 for relative,expected in manifest['source_files'].items():assert digest(ROOT/relative)==expected,('Original input changed',relative)
 paragraphs=0;files=0
 for first,last in BATCHES:
  if last>through:break
  receipt=json.loads((DATA/f'review/batch-{first:02}-{last:02}.json').read_text())
  assert receipt['range']==[first,last] and receipt['status']=='accepted-after-corrections'
  expected_paths={f'data/drama-full/{lang}/{n:02}.json' for lang in LANGS for n in range(first,last+1)}
  assert set(receipt['files'])==expected_paths,('Incomplete acceptance receipt',first,last)
  for lang in LANGS:
   for name in (f'{lang}-{first:02}-{last:02}.md',f'cross-{lang}-{first:02}-{last:02}-by-{REVIEWER[lang]}.md'):
    assert (DATA/'review'/name).is_file(),('Missing review report',name)
   for n in range(first,last+1):
    path=DATA/lang/f'{n:02}.json';source=json.loads((ROOT/f'data/drama/{n:02}.json').read_text());target=json.loads(path.read_text())
    assert digest(path)==receipt['files'][str(path.relative_to(ROOT))],('Translation changed after acceptance',path)
    assert set(target)=={'id','lang','work','author','title','deck','body','source_note','source_labels'} and target['id']==n and target['lang']==lang,path
    assert len(target['body'])==len(source['body_zh']) and len(target['source_labels'])==len(source['sources']),path
    for src,dst in zip(source['body_zh'],target['body']):
     assert isinstance(dst,str) and dst.strip() and dst!=src and '\ufffd' not in dst,path
     assert src.count('Self-as-an-End')==dst.count('Self-as-an-End') and src.count('*')==dst.count('*'),path
    files+=1;paragraphs+=len(target['body'])
 return {'through':through,'translations':files,'paragraphs':paragraphs,'note':'Hashes and paragraph coverage verify the reviewed files; they do not themselves establish translation quality.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--through',type=int,choices=(5,10,15,20,23),default=23);args=p.parse_args();print(json.dumps(audit(args.through),ensure_ascii=False))
if __name__=='__main__':main()
