#!/usr/bin/env python3
"""Render reviewed literary JSON, retaining independent English and scoped sources.
Usage: build_reviewed_literary_languages.py SERIES. Does not update shared discovery.
Translation and semantic reviews are authored separately, never inferred by this script.
"""
import argparse,html,json,re
from pathlib import Path
from prepare_action_sources import Document,Node
import don_literary_render as r
from web_analytics import ensure_analytics
R=Path(__file__).resolve().parents[1]
def write(path,value):path.write_text(value,encoding='utf-8')
def main(key):
 assert re.fullmatch(r'[a-z0-9-]+',key)
 D=R/'data'/key;M=D/'multilingual';profile=json.loads((M/'profile.json').read_text());directory=profile['directory'];folder=R/directory
 source=json.loads((M/'source.json').read_text());original=json.loads((M/'source-original.json').read_text());slugs=[a['slug'] for a in source['articles']]
 assert slugs==profile['slugs']
 for lang in ('ja','fr','de','es','ko'):
  data=json.loads((M/(lang+'.json')).read_text());assert [a['slug'] for a in data['articles']]==slugs
  for a,s in zip(data['articles'],source['articles']):
   n=len(s['body_zh']);assert len(a['body'])==n or (len(a['body'])==n-1 and a.get('source_note')),(lang,a['slug'],'coverage')
   assert [i for i,b in enumerate(a['body']) if b.startswith('## ')]==[i for i,b in enumerate(s['body_zh']) if b.startswith('## ')],(lang,a['slug'],'headings')
 ledger=json.loads((D/'source-corrections.json').read_text())['changes']
 english=json.loads((M/'en.json').read_text());assert [a['body'] for a in english['articles']]==[a['body_en'] for a in source['articles']]
 for old,new in zip(original['articles'],source['articles']):
  p=folder/(new['slug']+'.html');text=p.read_text();doc=Document(text);edits=[]
  for lang in ('zh','en'):
   body=next(n for n in doc.root.walk() if n.has('essay-body','lang-'+lang))
   nodes=[n for n in body.children if isinstance(n,Node) and n.text().strip() and 'edition-note' not in n.attrs.get('class','') and '版本说明' not in n.text() and 'Edition note:' not in n.text()]
   actual=[('## ' if n.tag=='h2' else '')+n.text().strip() for n in nodes]
   assert actual in (old['body_'+lang],new['body_'+lang]),(p,lang,'unreviewed source drift')
   if actual!=new['body_'+lang]:
    assert len(nodes)==len(new['body_'+lang])
    for n,a,b in zip(nodes,actual,new['body_'+lang]):
     if a!=b:
      correction=next(c for c in ledger if c['slug']==p.stem and c['language']==lang and c['block']==nodes.index(n))
      inline=[x for x in n.walk() if x is not n]
      assert not inline or correction.get('after_html'),(p,lang,n.text(),'inline markup needs explicit preservation')
      edits.append((n.open_end,n.close_start,correction.get('after_html',html.escape(b.removeprefix('## ')))))
  for start,end,value in sorted(edits,reverse=True):text=text[:start]+value+text[end:]
  write(p,text)
  hp=folder/'zh-hant-data'/(p.stem+'.js');ht=hp.read_text();match=re.search(r'var variants\s*=\s*(\{.*?\});',ht,re.S);variants=json.loads(match[1])
  for c in ledger:
   if c['slug']==p.stem and c['language']=='zh':
    variants.pop(c['before'].removeprefix('## '),None);variants[c['after'].removeprefix('## ')]=c['zh_hant'].removeprefix('## ');variants.update(c.get('hant_variants',{}))
  write(hp,ht[:match.start(1)]+json.dumps(variants,ensure_ascii=False,separators=(',',':'))+ht[match.end(1):])
 for p in folder.glob('*.html'):
  text=p.read_text();doc=Document(text);toggle=next(n for n in doc.root.walk() if n.has('lang-toggle'))
  if 'href="ja/' not in doc.raw(toggle):
   added=''.join('<span class="lang-sep">|</span><a class="lang-btn" href="'+k+'/'+p.name+'">'+r.names[k]+'</a>' for k in ('ja','fr','de','es','ko'));text=text[:toggle.close_start]+added+text[toggle.close_start:]
  text=text.replace("var saved=localStorage.getItem('nd_lang')","var saved=new URLSearchParams(location.search).get('lang')||localStorage.getItem('nd_lang')")
  if 'hreflang=' not in text:text=text.replace('</head>',r.hreflang(directory,p.stem)+'\n</head>')
  text=text.replace('class="lang-toggle" style="margin-bottom:.8rem;"','class="lang-toggle" style="margin-bottom:.8rem;display:flex;flex-wrap:wrap;"')
  if p.stem=='index':
   for a,b in [('Three reading modes','Eight languages'),('English · Simplified · Traditional','Eight languages'),('英文 · 简体 · 繁体','八语阅读'),('English · 简 / 繁 · Literary criticism','8 languages · Literary criticism'),('英文 · 简 / 繁 · 作品解读','八语 · 作品解读'),('>英 · 简 · 繁<','>八语阅读<')]:text=text.replace(a,b)
   text=re.sub(r'(Three|Four|Five) independent English and Chinese essays',str(len(slugs))+' essays in eight languages',text)
  write(p,ensure_analytics(text))
 hp=folder/'zh-hant-data/index.js';ht=hp.read_text();match=re.search(r'var variants\s*=\s*(\{.*?\});',ht,re.S);variants=json.loads(match[1]);variants.update({'八语阅读':'八語閱讀','八语 · 作品解读':'八語 · 作品解讀'});write(hp,ht[:match.start(1)]+json.dumps(variants,ensure_ascii=False,separators=(',',':'))+ht[match.end(1):])
 r.render(directory,key)
 print(key,': reviewed primary corrections and',5*(len(slugs)+1),'new-language pages; shared navigation untouched')
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('series');main(parser.parse_args().series)
