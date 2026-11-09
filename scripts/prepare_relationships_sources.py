#!/usr/bin/env python3
"""One-time lossless snapshot. Refuses to replace an existing receipt."""
import json,hashlib,subprocess
from pathlib import Path
from prepare_action_sources import Document,Node,one
from build_daily_full_editions import div_span
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/relationships-full'
DIRECTORY=ROOT/'essays/everyday/relationships'
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def region(s,l):return s[slice(*div_span(s,'lang-'+l)[1:3])]
def find(d,c):return one(d.root.walk(),lambda n:n.has(c),c)
def main():
 assert not (DATA/'preservation.json').exists(),'Snapshot already exists'
 ip=DIRECTORY/'index.html';it=ip.read_text();indexes={l:Document(region(it,l)) for l in ('zh','hant')}
 receipt={'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'scope':'essays/everyday/relationships','files':{},'chinese_regions':{},'source_snapshots':{}}
 for p in sorted(DIRECTORY.rglob('*.html')):receipt['files'][str(p.relative_to(ROOT))]=sha(p.read_text())
 for p in sorted(DIRECTORY.glob('*.html')):
  s=p.read_text();slug=p.stem;rec={l:sha(region(s,l)) for l in ('zh','hant')};receipt['chinese_regions'][slug]=rec
  if slug=='index':continue
  result={'slug':slug,'episode':int(slug[:2]),'source_url':'https://nondubito.net/'+str(p.relative_to(ROOT))+'?lang=zh','languages':{}}
  for l in ('zh','hant'):
   r=region(s,l);d=Document(r);body=find(d,'article-body');units=[d.raw(n) for n in body.children if isinstance(n,Node)];assert all(n.tag=='p' for n in body.children if isinstance(n,Node))
   card=one(indexes[l].root.walk(),lambda n:n.has('essay-card') and n.attrs.get('href')==p.name,slug)
   deck=one(card.walk(),lambda n:n.tag=='p','deck')
   result['languages'][l]={'title':one(d.root.walk(),lambda n:n.tag=='h1','title').text(),'deck':deck.text(),'chapter':find(d,'chapter-label').text(),'body':units,'body_html':d.raw(body,inner=True),'entry_door':d.raw(find(d,'entry-door'),inner=True),'region_html':r,'source_sha256':sha(d.raw(body,inner=True))}
  result.update({k:result['languages']['zh'][k] for k in ('title','deck','body','source_sha256','entry_door','chapter')})
  out=DATA/'sources'/(slug+'.json');write(out,result);receipt['source_snapshots'][out.name]=sha(out.read_text())
 index={'slug':'index','languages':{}}
 for l,d in indexes.items():
  route=find(d,'reading-route');door=find(d,'theory-door')
  index['languages'][l]={'title':one(d.root.walk(),lambda n:n.tag=='h1','title').text(),'deck':find(d,'series-deck').text(),'route_title':one(route.walk(),lambda n:n.tag=='h2','route title').text(),'route_intro':one(route.walk(),lambda n:n.tag=='p','route intro').text(),'chapters':[n.text() for n in d.root.walk() if n.tag=='h2' and n not in list(route.walk())],'theory_label':one(door.walk(),lambda n:n.tag=='span','theory label').text(),'theory_intro':d.raw(one(door.walk(),lambda n:n.tag=='p','theory intro'),inner=True),'region_html':region(it,l),'source_sha256':sha(region(it,l))}
 index.update(index['languages']['zh']);write(DATA/'sources/index.json',index);receipt['source_snapshots']['index.json']=sha((DATA/'sources/index.json').read_text())
 write(DATA/'preservation.json',receipt)
 write(DATA/'pending-source-decisions.json',{'status':'pending author decision; do not apply','items':[{'slug':'03-solving-your-problem-for-you','paragraph':23,'issue':'帮助者比当事人更能承受不确定 contrasts with helper anxiety in following paragraphs; author decision needed before 更难 correction.'},{'slug':'10-refusal-must-be-real','field':'deck','issue':'只有当“不”能真正结束劝说 contrasts with body paragraph12; author decision needed on qualification.'}],'structural_route':{'original':[1,11,16,21,27,30],'proposed':[1,6,11,16,21,27],'status':'deferred until metadata renderer ready'}})
 print('Snapshotted',len(receipt['chinese_regions'])-1,'essays;',sum(len(json.loads(p.read_text())['body']) for p in (DATA/'sources').glob('[0-9]*.json')),'paragraphs')
if __name__=='__main__':main()
