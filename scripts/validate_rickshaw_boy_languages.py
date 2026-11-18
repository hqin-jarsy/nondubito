#!/usr/bin/env python3
"""Scoped structural integrity and source coverage, not literary/native review."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
import json,re,hashlib
from prepare_action_sources import Document,Node
from full_series_languages import render_prose
from web_analytics import issue,Document as AnalyticsDocument
R=Path(__file__).resolve().parents[1];D=R/'data/rickshaw-boy/multilingual';P=R/'essays/literature/rickshaw-boy'
source=json.loads((D/'source.json').read_text())['articles'];original=json.loads((D/'source-original.json').read_text())['articles'];corrections=json.loads((D.parent/'source-corrections.json').read_text())['corrections'];allowed={(x['article'],x['source_block']) for x in corrections};counts=[len(a['body_zh']) for a in source];errors=[];blocks={};link_count=0
for lang in ['en','ja','fr','de','es','ko']:
 data=json.loads((D/(lang+'.json')).read_text());assert [a['slug'] for a in data['articles']]==[a['slug'] for a in source]
 blocks[lang]=[]
 for i,(a,s) in enumerate(zip(data['articles'],source)):
  assert len(a['body']) in (counts[i],counts[i]-1),(lang,i)
  assert len(a['body'])==counts[i] or a.get('source_note')
  assert all(p.strip() and '�' not in p for p in a['body'])
  assert [j for j,x in enumerate(a['body']) if x.startswith('## ')]==[j for j,x in enumerate(s['body_zh']) if x.startswith('## ')]
  p=P/(a['slug']+'.html') if lang=='en' else P/lang/(a['slug']+'.html')
  assert render_prose(a['body']) in p.read_text(),(lang,a['slug'],'body not rendered')
  blocks[lang].append(len(a['body']))
for i,(s,o) in enumerate(zip(source,original)):
 p=R/s['source_html'];d=Document(p.read_text());n=next(n for n in d.root.walk() if n.has('essay-body','lang-zh'))
 actual=[('## ' if x.tag=='h2' else '')+x.text().strip() for x in n.children if isinstance(x,Node) and x.text().strip() and '版本说明' not in x.text()]
 assert actual==s['body_zh'],s['slug']
 v=json.loads(re.search(r'var variants = (\{.*?\});',(P/'zh-hant-data'/(s['slug']+'.js')).read_text(),re.S).group(1))
 for j,(a,b) in enumerate(zip(actual,o['body_zh'])):
  if a!=b:
   assert (i+1,j+1) in allowed,(i,j,'undocumented source change')
   assert v.get(a.removeprefix('## ')),(i,j,'missing or empty Traditional Chinese')
pages=[*P.glob('*.html'),*P.glob('*/*.html')];assert len(pages)==24
for p in pages:
 d=Document(p.read_text());nodes=list(d.root.walk());links=[n for n in nodes if n.tag=='link']
 assert len([n for n in links if n.attrs.get('rel')=='alternate'])==8,p
 assert len([n for n in links if n.attrs.get('rel')=='canonical'])==1,p
 assert issue(AnalyticsDocument(p.read_text())) is None,p
 assert not any(n.tag=='h3' for n in nodes),p
 for n in nodes:
  for attr in ['href','src']:
   href=n.attrs.get(attr) or '';u=urlsplit(href)
   if not href or u.scheme or href.startswith('//') or not u.path:continue
   link_count+=1;q=(p.parent/unquote(u.path)).resolve()
   if not q.exists():errors.append([str(p.relative_to(R)),href])
assert not errors,errors
result={'result':'passed','pages':24,'new_language_pages':20,'source_blocks':counts,'target_body_blocks':blocks,'local_links_checked':link_count,'checks':['Complete source-aligned arrays; final bibliography can be source_note','All language body prose present in generated pages','8 alternates and one canonical per page','Local links exist; analytics clean; no unstyled h3','Chinese changes limited to recorded blocks; modified Traditional Chinese mappings nonempty'],'limitations':['No native-speaker or scholarly certification','Browser/mobile visual checks performed separately by coordinator'],'language_sha256':{l:hashlib.sha256((D/(l+'.json')).read_bytes()).hexdigest() for l in blocks}}
(D/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
