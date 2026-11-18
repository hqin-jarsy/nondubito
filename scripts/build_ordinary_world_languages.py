#!/usr/bin/env python3
"""Render Ordinary World from persistent language JSON; never touch shared discovery.
English drafting import is separate: compile_ordinary_world_english.py.
"""
from pathlib import Path
import json
import ordinary_world_literary_render as r
R=Path(__file__).resolve().parents[1];D=R/'data/ordinary-world/multilingual'
directory='essays/literature/ordinary-world';key='ordinary-world'
def main():
 source=json.loads((D/'source.json').read_text())['articles'];slugs=[a['slug'] for a in source]
 for lang in ['en','ja','fr','de','es','ko']:
  payload=json.loads((D/(lang+'.json')).read_text());assert [a['slug'] for a in payload['articles']]==slugs,lang
  for a,original in zip(payload['articles'],source):
   n=len(original['body_zh']);assert len(a['body']) in (n,n-1),(lang,a['slug'],len(a['body']),n)
   assert len(a['body'])==n or a.get('source_note'),(lang,a['slug'],'missing source note')
   assert [i for i,x in enumerate(a['body']) if x.startswith('## ')]==[i for i,x in enumerate(original['body_zh']) if x.startswith('## ')],(lang,a['slug'],'heading alignment')
 english=json.loads((D/'en.json').read_text());lookup={a['slug']:a['body']+([a['source_note']] if len(a['body'])==len(source[i]['body_zh'])-1 else []) for i,a in enumerate(english['articles'])}
 r.patch_primary(directory,lookup);r.render(directory,key)
 profile={'id':key,'directory':directory,'date':'2026-11-18','source_format':'literary-html','slugs':slugs,'languages':['de','fr','es','ja','ko'],'primary_editions':{'en':'','zh':'','zh-hant':''},'builder':'scripts/build_ordinary_world_languages.py','source':'Complete Chinese essays frozen in source-original.json, then corrected as documented in ../source-corrections.json.','draft_format':'Persistent language JSON; complete source-block coverage, final bibliographic block optionally held in source_note.'}
 (D/'profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n')
 print('Ordinary World: 5 restored English essays, 30 foreign-language pages; shared indexes untouched.')
if __name__=='__main__':main()
