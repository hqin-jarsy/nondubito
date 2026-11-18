#!/usr/bin/env python3
"""Apply recorded, authorized Childhood source corrections; keep original snapshot."""
from pathlib import Path
import json,re,sys,html,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from prepare_action_sources import Document,Node
R=Path(__file__).resolve().parents[1];D=R/'data/childhood';M=D/'multilingual'
source=json.loads((M/'source-original.json').read_text());current=json.loads((M/'source.json').read_text());changes=json.loads((D/'source-corrections.json').read_text())['corrections']
for c in changes:
 ep=c['article']-1;b=c['source_block']-1;a=source['articles'][ep];old=c['before'];new=c['after'];assert a['body_zh'][b]==old
 p=R/a['source_html'];text=p.read_text();doc=Document(text);body=next(n for n in doc.root.walk() if n.has('essay-body','lang-zh'))
 expected={old.removeprefix('## '),new.removeprefix('## '),current['articles'][ep]['body_zh'][b].removeprefix('## ')}
 node=next((n for n in body.children if isinstance(n,Node) and n.text().strip() in expected),None);assert node,(ep,b)
 p.write_text(text[:node.open_end]+html.escape(new.removeprefix('## '))+text[node.close_start:])
 hp=p.parent/'zh-hant-data'/(p.stem+'.js');ht=hp.read_text();m=re.search(r'var variants = (\{.*?\});',ht,re.S);v=json.loads(m.group(1));v.pop(old.removeprefix('## '),None);v[new.removeprefix('## ')]=c['zh_hant'].removeprefix('## ');assert v[new.removeprefix('## ')];hp.write_text(ht[:m.start(1)]+json.dumps(v,ensure_ascii=False,separators=(',',':'))+ht[m.end(1):]);a['body_zh'][b]=new
for a in source['articles']:a['source_sha256']=hashlib.sha256((R/a['source_html']).read_bytes()).hexdigest()
source['note']='Complete Chinese source with documented authorized corrections. Original Chinese and old English retained in source-original.json; block alignment unchanged. Old English is audit material, not translation authority.'
(M/'source.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n');print('Applied',len(changes),'documented source/Hant corrections; source blocks unchanged.')
