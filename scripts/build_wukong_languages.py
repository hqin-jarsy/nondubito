#!/usr/bin/env python3
"""Render Black Myth: Wukong from persistent language JSON; never touch shared discovery.
English drafting import is separate: prepare_wukong_english.py.
"""
from pathlib import Path
import json
import wukong_game_render as r
R=Path(__file__).resolve().parents[1];D=R/'data/black-myth-wukong/multilingual'
directory='essays/games/black-myth-wukong';key='black-myth-wukong'
def main():
 source=json.loads((D/'source.json').read_text())['articles'];original=json.loads((D/'source-original.json').read_text())['articles'];slugs=[a['slug'] for a in source]
 for lang in ['en','ja','fr','de','es','ko']:
  payload=json.loads((D/(lang+'.json')).read_text());assert [a['slug'] for a in payload['articles']]==slugs,lang
  if lang=='en':
   ledger=json.loads((D.parent/'english-corrections.json').read_text())['articles']
   assert [a['body'] for a in payload['articles']]==[a['revised_body'] for a in ledger]
   continue
  for a,original_zh in zip(payload['articles'],source):
   n=len(original_zh['body_zh']);assert len(a['body']) in (n,n-1),(lang,a['slug'],len(a['body']),n)
   assert len(a['body'])==n or a.get('source_note'),(lang,a['slug'],'missing source note')
   assert [i for i,x in enumerate(a['body']) if x.startswith('## ')]==[i for i,x in enumerate(original_zh['body_zh']) if x.startswith('## ')],(lang,a['slug'],'heading alignment')
 english=json.loads((D/'en.json').read_text());lookup={a['slug']:a['body'] for a in english['articles']}
 r.patch_primary(directory,lookup);r.render(directory,key)
 profile={'id':key,'directory':directory,'date':'2026-11-18','source_format':'literary-html','additional_discovery_paths':['essays/zh-hant/index.html'],'slugs':slugs,'languages':['de','fr','es','ja','ko'],'primary_editions':{'en':'','zh':'','zh-hant':''},'builder':'scripts/build_wukong_languages.py','source':'Complete Chinese essays frozen in source-original.json, then corrected as documented in ../source-corrections.json.','draft_format':'Persistent JSON: original independent English argument retained with local factual corrections; new five languages cover complete Chinese blocks, final bibliography optionally in source_note.'}
 (D/'profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n')
 print('Black Myth: Wukong: 4 locally corrected independent English essays, 25 foreign-language pages; shared indexes untouched.')
if __name__=='__main__':main()
