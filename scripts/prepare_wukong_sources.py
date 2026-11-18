#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply the reviewed original-coordinate ledger; never touch shared navigation."""
from pathlib import Path
import json,re,html,sys
from prepare_action_sources import Document,Node
R=Path(__file__).resolve().parents[1];D=R/'data/black-myth-wukong';M=D/'multilingual'
s=json.loads((M/'source-original.json').read_text());ledger=json.loads((D/'source-corrections.json').read_text());changes=ledger['corrections']
for i,a in enumerate(s['articles'],1):
 cs=[c for c in changes if c['article']==i];lookup={c['source_block']:c for c in cs};p=R/a['source_html'];t=p.read_text();d=Document(t);body=next(n for n in d.root.walk() if n.has('essay-body','lang-zh'));nodes=[n for n in body.children if isinstance(n,Node) and n.text().strip() and '版本说明' not in n.text()]
 revised=[lookup.get(j,{}).get('after',b) for j,b in enumerate(a['body_zh'],1)];revised=[b for b in revised if b is not None]
 actual=[('## ' if n.tag=='h2' else '')+n.text().strip() for n in nodes]
 if actual!=revised:
  assert actual==a['body_zh'],(i,'source differs from original and revised')
  edits=[]
  for c in cs:
   n=nodes[c['source_block']-1];assert c['before']==a['body_zh'][c['source_block']-1]
   edits.append((n.start,n.end,'') if c['after'] is None else (n.open_end,n.close_start,html.escape(c['after'].removeprefix('## '))))
  for start,end,value in sorted(edits,reverse=True):t=t[:start]+value+t[end:]
  p.write_text(t)
 hp=p.parent/'zh-hant-data'/(p.stem+'.js');ht=hp.read_text();m=re.search(r'var variants = (\{.*?\});',ht,re.S);v=json.loads(m.group(1))
 for c in cs:
  old=c['before'].removeprefix('## ')
  if c['before'] not in revised:v.pop(old,None)
  if c['after'] is not None:v[c['after'].removeprefix('## ')]=c['zh_hant'].removeprefix('## ')
 hp.write_text(ht[:m.start(1)]+json.dumps(v,ensure_ascii=False,separators=(',',':'))+ht[m.end(1):]);a['body_zh']=revised
s['note']='Reviewed Chinese source with documented factual and dependent-interpretation corrections. Original Chinese and independent English retained in source-original.json; only two exact duplicate Chinese paragraphs deleted. Old English is audit material, not the authority for new translations.'
(M/'source.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print('Applied',len(changes),'source corrections; blocks',[len(a['body_zh']) for a in s['articles']])
