"""Validate this series only; re-render and write its structural QA report."""
from pathlib import Path
import json,sys,re,hashlib,subprocess
from urllib.parse import urlsplit,unquote
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from prepare_action_sources import Document
D=R/'data/a-tale-of-two-cities';F=R/'essays/literature/a-tale-of-two-cities'
results={};links=0
for lang in ('en','ja','fr','de','es','ko'):
 payload=json.loads((D/'multilingual'/f'{lang}.json').read_text());assert len(payload['articles'])==4
 stats=[]
 for i,a in enumerate(payload['articles']):
  assert all(x.strip() for x in a['body']);assert len(a['body'])>=18
  p=F/(lang if lang!='en' else '')/(a['slug']+'.html');doc=Document(p.read_text())
  bodies=[n for n in doc.root.walk() if n.has('essay-body') and (lang!='en' or n.has('lang-en'))];assert len(bodies)==1
  t=bodies[0].text()
  for b in a['body']:
   b=b.removeprefix('## ')
   assert b in t,(p,b[:70])
  assert len(re.findall(r'hreflang=',p.read_text()))==8
  stats.append({'slug':a['slug'],'blocks':len(a['body']),'characters':sum(map(len,a['body'])),'words':len(' '.join(a['body']).split())})
 results[lang]=stats
for p in F.rglob('*.html'):
 doc=Document(p.read_text())
 for n in doc.root.walk():
  if n.tag not in ('a','link','script'):continue
  v=n.attrs.get('href',n.attrs.get('src',''));u=urlsplit(v)
  if not v or u.scheme or u.netloc or v.startswith('#'):continue
  target=(R/u.path.lstrip('/') if u.path.startswith('/') else p.parent/unquote(u.path)).resolve()
  assert target.exists(),(str(p.relative_to(R)),v)
  links+=1
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in F.rglob('*') if p.is_file()}
subprocess.run([sys.executable,str(R/'scripts/build_a_tale_of_two_cities_languages.py')],check=True)
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in F.rglob('*') if p.is_file()}
assert before==after,'Build is not idempotent'
receipts={}
for lang in ('ja','fr','de','es','ko'):
 receipt=json.loads((D/'multilingual'/('cross-review-'+lang+'.json')).read_text())
 assert not receipt['remaining'],lang
 assert receipt['language_data_sha256']==hashlib.sha256((D/'multilingual'/(lang+'.json')).read_bytes()).hexdigest(),lang
 receipts[lang]=receipt['language_data_sha256']
report={'independent_review_inputs':receipts,'status':'passed structural checks and verified five independent internal full-read review receipts; no external native-speaker or browser review claimed by this worker','languages':results,'internal_links_checked':links,'html_pages':len(list(F.rglob('*.html'))),'idempotent':True,'full_scene_checklist':['carriage, coin returned, Gaspard and gallows','peasant household and cart yoke; Manette letter and eighteen years','renunciation, Gabelle, two trials, hijacked testimony, shoemaking relapse','Madame Defarge childhood, knitting register, husband stopping, Pross pistol and deafness','London resemblance, Stryver, promise, spy coercion, drugging without consent','seamstress recognition and hand; final conditional narration; no utility ranking']}
(D/'qa-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
