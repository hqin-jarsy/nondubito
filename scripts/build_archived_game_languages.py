#!/usr/bin/env python3
"""Rebuild reviewed October game editions; original archived manuscripts remain immutable."""
from pathlib import Path
import argparse,json,hashlib,re,html
import frostpunk_game_render as r
from prepare_action_sources import Document,Node
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(key):
 D=R/'data'/key/'multilingual';directory='essays/games/'+key
 receipt=json.loads((D/'publication.json').read_text());assert receipt['editorial_clearance']=='independent-full-text-review-and-parent-source-clearance'
 manifest=json.loads((D/'archive-manifest.json').read_text())
 # Original archive bytes were checked during import, not published in this repository.
 assert manifest['files'] and all(len(h)==64 for h in manifest['files'].values())
 for lang,h in receipt['languages'].items():assert sha(D/(lang+'.json'))==h,(lang,'changed after review')
 assert sha(D/'source.json')==receipt['source_sha256']
 source=json.loads((D/'source.json').read_text());original=json.loads((D/'source-original.json').read_text());led=json.loads((D/'source-corrections.json').read_text())
 for a,o in zip(source['articles'],original['articles']):
  p=R/a['source_html'];text=p.read_text();d=Document(text);edits=[]
  for l in ['zh','en']:
   body=next(n for n in d.root.walk() if n.has('essay-body','lang-'+l));nodes=[n for n in body.children if isinstance(n,Node) and n.text().strip() and '版本说明' not in n.text() and 'Edition note:' not in n.text() and not n.has('edition-note')]
   assert len(nodes)==len(a['body_'+l]),(key,a['slug'],l,'node count')
   for i,(n,before,after) in enumerate(zip(nodes,o['body_'+l],a['body_'+l])):
    actual=('## ' if n.tag=='h2' else '')+n.text().strip();assert actual in (before,after),(p,l,i,'unrelated source drift')
    if before!=after and actual!=after:
     c=next(c for c in led['changes'] if c['path']==a['source_html'] and c['language']==l and c['block']==i);edits.append((n.open_end,n.close_start,c['after_html']))
  for start,end,new in sorted(edits,reverse=True):text=text[:start]+new+text[end:]
  for m in led.get('derived_metadata',[]):
   if m['path']==a['source_html']:text=text.replace(html.escape(m['before'],quote=True),html.escape(m['after'],quote=True))
  p.write_text(text)
  hp=p.parent/'zh-hant-data'/(p.stem+'.js');raw=hp.read_text();m=re.search(r'var variants\s*=\s*(\{.*?\});',raw,re.S);v=json.loads(m[1])
  for c in led['changes']:
   if c['path']==a['source_html'] and c['language']=='zh':
    assert c['before'] in v or c['after'] in v,(p,c['block'],'Hant key absent');v.pop(c['before'],None);v[c['after']]=c['zh_hant']
  hp.write_text(raw[:m.start(1)]+json.dumps(v,ensure_ascii=False,separators=(',',':'))+raw[m.end(1):])
 # The imported drafts have their own segmentation; source notes are never conditionally dropped.
 r.patch_primary(directory)
 for lang in receipt['languages']:
  payload=json.loads((D/(lang+'.json')).read_text());s=payload['series'];arts=payload['articles'];dest=R/directory/lang;dest.mkdir(exist_ok=True)
  assert [a['slug'] for a in arts]==[a['slug'] for a in source['articles']]
  for i,a in enumerate(arts):
   assert a['source_note'] and len(a['body'])==a['archive_body_blocks']
   nav='<div class="essay-nav">'+('' if i==0 else '<a href="'+arts[i-1]['slug']+'.html">← '+html.escape(r.ui[lang][1])+': '+html.escape(arts[i-1]['title'])+'</a>')+('<span></span>' if i+1==len(arts) else '<a href="'+arts[i+1]['slug']+'.html">'+html.escape(r.ui[lang][2])+': '+html.escape(arts[i+1]['title'])+' →</a>')+'</div>'
   prose=r.render_prose(a['body'])+'<aside class="edition-note"><p>'+html.escape(a['source_note'])+'</p></aside>'
   (dest/(a['slug']+'.html')).write_text(r.page(directory,lang,a['slug'],a['title'],a['deck'],s['title'],prose,nav,str(i+1)+' / '+str(len(arts)),a.get('edition_note','')))
  intro=s.get('intro',[]);intro=[intro] if isinstance(intro,str) else intro
  cards='<div class="essay-list">'+''.join('<a class="essay-card" href="'+a['slug']+'.html"><span class="card-num">'+str(i+1)+'</span><div class="card-body"><h2>'+html.escape(a['title'])+'</h2><p class="card-desc">'+html.escape(a['deck'])+'</p></div></a>' for i,a in enumerate(arts))+'</div>'
  body=r.render_prose([s['deck']]+intro+([s['note']] if s.get('note') else []))+cards
  (dest/'index.html').write_text(r.page(directory,lang,'index',s['title'],s['deck'],s['title'],body,count='4 · 8 '+{'ja':'言語','fr':'langues','de':'Sprachen','es':'idiomas','ko':'개 언어'}[lang]))
 print(key+': archived full drafts rendered; source corrections and hashes verified.')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('series',choices=['sky-children-of-the-light','civilization','elden-ring']);main(p.parse_args().series)
