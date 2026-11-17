#!/usr/bin/env python3
"""Static checks for this series only; does not claim browser or native-speaker QA."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,hashlib
from prepare_action_sources import Document
from full_series_languages import render_prose
R=Path(__file__).resolve().parents[1];S=R/'essays/literature/the-moon-and-sixpence';D=R/'data/the-moon-and-sixpence/multilingual'
class Scan(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.lang=None;self.canonical=[];self.alternates=[];self.text=[];self.skip=0
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='html':self.lang=a.get('lang')
  if t in ('a','link','script','img'):
   v=a.get('href',a.get('src'))
   if v:self.links.append(v)
  if t=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
  if t=='link' and a.get('rel')=='alternate':self.alternates.append(a.get('hreflang'))
  if t in ('script','style'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style') and self.skip:self.skip-=1
 def handle_data(self,d):
  if not self.skip:self.text.append(d)
profile=json.loads((D/'profile.json').read_text());slugs=profile['slugs'];stats={}
for lang in ['en']+profile['languages']:
 p=json.loads((D/(lang+'.json')).read_text());assert [a['slug'] for a in p['articles']]==slugs
 assert [len(a['body']) for a in p['articles']]==[32,39,35,33]
 stats[lang]=[]
 for a in p['articles']:
  path=S/(a['slug']+'.html') if lang=='en' else S/lang/(a['slug']+'.html')
  raw=path.read_text();doc=Document(raw);body=next(n for n in doc.root.walk() if n.has('essay-body','lang-en')) if lang=='en' else next(n for n in doc.root.walk() if n.has('essay-body'))
  assert render_prose(a['body']) in doc.raw(body),(lang,a['slug'],'draft/render mismatch')
  assert all(x.strip() for x in a['body'])
  stats[lang].append({'slug':a['slug'],'blocks':len(a['body']),'words':sum(len(t.split()) for t in a['body']),'characters':sum(len(t) for t in a['body'])})
links=0
for p in sorted(S.rglob('*.html')):
 sc=Scan();sc.feed(p.read_text());assert len(sc.canonical)==1,p
 assert set(sc.alternates)=={'en','zh-Hans','zh-Hant','ja','fr','de','es','ko'},p
 if p.parent.name in profile['languages']:assert sc.lang==p.parent.name,p
 for url in sc.links:
  u=urlsplit(url)
  if u.scheme or u.netloc or not u.path:continue
  target=(R/unquote(u.path.lstrip('/'))) if u.path.startswith('/') else p.parent/unquote(u.path)
  assert target.exists(),(p,url)
  links+=1
 if p.parent==S:
  js=(S/'zh-hant-data'/(p.stem+'.js')).read_text();m=re.search(r'var variants = (\{.*?\});',js,re.S);v=json.loads(m.group(1))
  doc=Document(p.read_text());zh=[n for n in doc.root.walk() if n.has('essay-body','lang-zh')]
  if zh:
   z=Scan();z.feed(doc.raw(zh[0]))
   for t in z.text:
    if re.search(r'[\u3400-\u9fff]',t):assert t in v,(p,t)
# Confirm core factual corrections without testing subjective interpretation as fact.
text='\n'.join(p.read_text() for p in S.glob('*.html'))
for bad in ['斧子','在瞎了之后的那段时间里','没有人看见过','儿子引了一句《圣经》','他没有受过训练']:
 assert bad not in text,bad
print(json.dumps({'pages':len(list(S.rglob('*.html'))),'local_links_checked':links,'editions':stats,'result':'pass'},ensure_ascii=False,indent=2))
