#!/usr/bin/env python3
"""Scoped data/HTML checks, not a substitute for editorial review."""
import json,sys,subprocess,hashlib
from pathlib import Path
from urllib.parse import urlsplit,unquote
from prepare_action_sources import Document
from web_analytics import issue,Document as AnalyticsDocument
R=Path(__file__).resolve().parents[1];D=R/'data/catch-22/multilingual';P=R/'essays/literature/catch-22'
spec=json.loads((D/'profile.json').read_text());counts=[29,28,32,36];errors=[]
for lang in spec['languages']:
 data=json.loads((D/(lang+'.json')).read_text())
 assert [a['slug'] for a in data['articles']]==spec['slugs']
 for i,a in enumerate(data['articles']):
  assert len(a['body'])==counts[i] and len(a['coverage'])==counts[i]
  assert all(p.strip() and '�' not in p for p in a['body'])
for p in [*P.glob('*.html'),*P.glob('*/*.html')]:
 d=Document(p.read_text());nodes=list(d.root.walk());links=[n for n in nodes if n.tag=='link']
 assert len([n for n in links if n.attrs.get('rel')=='alternate'])==8,p
 assert len([n for n in links if n.attrs.get('rel')=='canonical'])==1,p
 assert issue(AnalyticsDocument(p.read_text())) is None,p
 for n in nodes:
  for attr in ('href','src'):
   href=n.attrs.get(attr,'');u=urlsplit(href)
   if not href or u.scheme or href.startswith('//') or not u.path:continue
   q=(p.parent/unquote(u.path)).resolve()
   if not q.exists():errors.append([str(p.relative_to(R)),href])
for slug in spec['slugs']:
 p=P/(slug+'.html');base=Document(subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(R))],cwd=R,text=True));now=Document(p.read_text())
 extract=lambda d:d.raw(next(n for n in d.root.walk() if n.has('essay-body','lang-zh')))
 expected=extract(base).replace('一直拖到最后一章才写出来','一直拖到倒数第二章（第四十一章）才写出来').replace('最后一章掀开的时候','倒数第二章掀开的时候')
 assert expected==extract(now),slug
assert not errors,errors
result=dict(result='passed',pages=30,new_language_pages=25,paragraphs_per_language=counts,checks=['all five languages, four complete paragraph arrays each','8 alternate links and 1 canonical per page','all local href/src targets exist','analytics issue() clean per page','Chinese essay-body preservation except two authorized Chapter 41 corrections'],limitations=['Not a browser/layout test','Not a native-speaker or independent scholarly certification'])
(D/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
