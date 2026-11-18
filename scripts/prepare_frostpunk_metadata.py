#!/usr/bin/env python3
"""Scoped metadata/edition-note synchronization; does not alter frozen prose."""
from pathlib import Path
import json,re,html,subprocess
from prepare_action_sources import Document,Node
R=Path(__file__).resolve().parents[1];P=R/'essays/games/frostpunk';D=R/'data/frostpunk';M=D/'multilingual'
en=json.loads((M/'en.json').read_text());source=json.loads((M/'source.json').read_text());lookup={a['slug']:a for a in en['articles']};records=[]
new_en='Four essays on the Book of Laws, choices that create the need for further control, the parallel functions of Order and Faith, and a reading of the game’s moral boundary through the place left for dissent.'
new_zh='四篇从法典与管理者的视野，读到选择怎样制造下一次选择、秩序与信仰怎样走进同一个房间，以及从“人还能不能说不”来读游戏的边界。'
zh_note='版本说明：保留原散文结构，按可核游戏画面与开发资料修正具体机制及直接依赖的论述。关于权力与边界的讨论属于本文读法，不是全部结局条件的算法清单。全文含剧透。'
for p in sorted(P.glob('*.html')):
 t=p.read_text();d=Document(t);edits=[];han=[]
 for n in d.root.walk():
  if n.tag=='meta' and (n.attrs.get('name')=='description' or n.attrs.get('property')=='og:description'):
   before=n.attrs['content'];after=new_en if p.stem=='index' else lookup[p.stem]['deck'];raw=d.raw(n);new=raw.replace(html.escape(before,quote=True),html.escape(after,quote=True))
   # Original ampersands are already escaped by serializer in these pages.
   if new==raw and before!=after:new=re.sub(r'content="[^"]*"','content="'+html.escape(after,quote=True)+'"',raw)
   edits.append((n.start,n.end,new));records.append(dict(path=str(p.relative_to(R)),kind='description',before=before,after=after))
 if p.stem=='index':
  for lang,after in [('en',new_en),('zh',new_zh)]:
   body=next(n for n in d.root.walk() if n.has('essay-body','lang-'+lang));n=next(n for n in body.children if isinstance(n,Node) and n.tag=='p');before=n.text();edits.append((n.open_end,n.close_start,html.escape(after)));records.append(dict(path=str(p.relative_to(R)),kind='index-'+lang,before=before,after=after))
   if lang=='zh':han.append((before,after))
 else:
  body=next(n for n in d.root.walk() if n.has('essay-body','lang-zh'))
  for n in body.children:
   if isinstance(n,Node) and n.text().startswith('版本说明'):
    before=n.text();edits.append((n.open_end,n.close_start,html.escape(zh_note)));records.append(dict(path=str(p.relative_to(R)),kind='edition-note-zh',before=before,after=zh_note));han.append((before,zh_note))
 for a,b,v in sorted(edits,reverse=True):t=t[:a]+v+t[b:]
 p.write_text(t)
 if han:
  hp=P/'zh-hant-data'/(p.stem+'.js');ht=hp.read_text();m=re.search(r'var variants\s*=\s*(\{.*?\});',ht,re.S);v=json.loads(m.group(1));js='ObjC.import("Foundation");var a='+json.dumps([x[1] for x in han],ensure_ascii=False)+';JSON.stringify(a.map(function(s){return ObjC.unwrap($(s).stringByApplyingTransformReverse($("Hans-Hant"),false));}));';q=Path('/tmp/frost-metadata-hant.js');q.write_text(js);tr=json.loads(subprocess.check_output(['osascript','-l','JavaScript',str(q)],text=True))
  for (before,after),traditional in zip(han,tr):v.pop(before,None);v[after]=traditional
  hp.write_text(ht[:m.start(1)]+json.dumps(v,ensure_ascii=False,separators=(',',':'))+ht[m.end(1):])
# Do not replace the first-change audit on idempotent reruns.
f=D/'metadata-corrections.json'
if not f.exists():f.write_text(json.dumps(dict(series=dict(en=new_en,zh=new_zh),corrections=records),ensure_ascii=False,indent=2)+'\n')
print('Scoped metadata and Chinese edition notes synchronized')
