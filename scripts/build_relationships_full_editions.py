#!/usr/bin/env python3
"""Independent, review-gated Relationships renderer. Never generates prose.

Only hashes and structural completeness are checked here. Semantic review must
be recorded honestly by a reader in reviews/batchNN.json before publication.
No daily-full import, global rebuild, or implicit Chinese correction is run.
"""
import argparse,hashlib,html,json,os,re
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit
from prepare_action_sources import Document,Node,one
from build_daily_full_editions import div_span,within,update_links
from build_classic_full_editions import patch,inner,metadata
from web_analytics import tracked_html
from prepare_relationships_sources import sha,region
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/relationships-full'
DIRECTORY=ROOT/'essays/everyday/relationships'
LANGS=('en','ja','fr','de','es','ko')
ROUTE=(1,6,11,16,21,27)
STYLE='<style id="relationships-full-reader">.article-head h1,.article-body,.essay-card h3,.series-nav-btn,.series-hero h1{overflow-wrap:anywhere}.article-head h1,.essay-card h3,.series-hero h1{hyphens:auto;-webkit-hyphens:auto}.article-shell,.essay-card,.series-nav-btn{min-width:0}.series-nav-btn{flex:1}.series-wrap{padding-top:calc(54px + 3rem)}@media(max-width:760px){.series-wrap{padding-top:calc(54px + 2.3rem)}}</style>'
CONTROLLER="""<script id="relationships-full-controller">(function(){function read(k){try{return localStorage.getItem(k)}catch(e){return null}}function save(k,v){try{localStorage.setItem(k,v)}catch(e){}}function valid(v){return ['en','zh','zh-hant'].indexOf(v)!==-1}var q=new URLSearchParams(location.search).get('lang'),saved=q||read('nd_lang')||read('nondubito-lang')||'zh';if(!valid(saved))saved='zh';function apply(){document.documentElement.dataset.lang=saved;document.documentElement.lang=saved==='zh-hant'?'zh-Hant':(saved==='zh'?'zh-Hans':'en');document.querySelectorAll('[data-lang-button]').forEach(function(b){b.classList.toggle('active',b.dataset.langButton===saved)})}apply();document.addEventListener('DOMContentLoaded',function(){apply();document.querySelectorAll('[data-lang-button]').forEach(function(b){b.addEventListener('click',function(){var v=b.dataset.langButton;if(!valid(v))return;saved=v;save('nd_lang',saved);save('nondubito-lang',saved);var u=new URL(location.href);u.searchParams.set('lang',saved);history.replaceState(null,'',u);apply()})})})})();</script>"""
def read_json(p):return json.loads(p.read_text(encoding="utf-8"))
def file_sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def source(slug):return read_json(DATA/'sources'/(slug+'.json'))
def slugs():return sorted(p.stem for p in (DATA/'sources').glob('[0-9]*.json'))
def find(d,cls):return one(d.root.walk(),lambda n:n.has(cls),cls)
def page(lang,slug):return (DIRECTORY if lang=='en' else DIRECTORY/lang)/(slug+'.html')
def preserved():
 r=read_json(DATA/'preservation.json')
 for name,h in r['source_snapshots'].items():assert file_sha(DATA/'sources'/name)==h,('snapshot changed',name)
 for slug,langs in r['chinese_regions'].items():
  text=(DIRECTORY/(slug+'.html')).read_text()
  for lang,h in langs.items():
   actual=region(text,lang)
   expected=source(slug)['languages'][lang]['region_html']
   assert sha(actual)==h or (slug=='index' and actual==index_region(expected,{},fix_routes=True)),('Chinese region changed without approved amendment',slug,lang)
 return r

def validate_inline(value,original,paragraph=False):
 assert isinstance(value,str) and value.strip()
 d=Document(value);nodes=[n for n in d.root.children if isinstance(n,Node)]
 if paragraph:assert len(nodes)==1 and nodes[0].tag=='p' and not any(isinstance(n,str) and n.strip() for n in d.root.children),'one paragraph per source unit'
 assert d.root.text().strip() and not re.search(r'\[VERIFY|TODO|TBD|PLACEHOLDER|\ufffd',value),'empty/unfinished translation'
 allowed={'root','p','strong','em','a','br','sup','sub','b','i'}
 assert all(n.tag in allowed for n in d.root.walk()),'unexpected markup'
 assert sum(n.tag=='p' for n in d.root.walk())==(1 if paragraph else 0),'nested/unexpected paragraph'
 assert not re.search(r'<!--|<!|<\?',value),'unexpected non-prose markup'
 for n in d.root.walk():
  assert all(k in ('href','title') and isinstance(v,str) for k,v in n.attrs.items()),'unexpected HTML attributes'
  if n.tag=='a':assert isinstance(n.attrs.get('href'),str) and n.attrs['href'].strip(),'missing link target'
  if 'href' in n.attrs:
   assert n.tag=='a' and isinstance(n.attrs['href'],str),'unexpected link attribute'
   assert not urlsplit(n.attrs['href']).scheme or urlsplit(n.attrs['href']).scheme in ('https','http'),'unsafe link'
 a=Document(original)
 for tag in ('strong','em','b','i','br','sup','sub','a'):
  assert sum(n.tag==tag for n in a.root.walk())==sum(n.tag==tag for n in d.root.walk()),('lost/added formatting',tag)

def translated_links(prose,lang,source_units,directory):
 # Always restore source targets, regardless of a draft's quoting or URL edits.
 original=Document(''.join(source_units));draft=Document(prose)
 origins=[n.attrs['href'] for n in original.root.walk() if n.tag=='a']
 anchors=[n for n in draft.root.walk() if n.tag=='a']
 assert len(origins)==len(anchors),'source links lost or invented'
 changes=[]
 for href,node in zip(origins,anchors):
  u=urlsplit(href)
  assert not u.scheme or u.scheme in ('https','http'),'unsafe source link'
  if lang!='en' and not (u.scheme or u.netloc or href.startswith(('#','/'))):
   target=(directory/u.path).resolve();local=target.parent/lang/target.name
   rebased=os.path.relpath(local,directory/lang) if local.is_file() else '../'+u.path
   href=urlunsplit(('', '', rebased,u.query,u.fragment))
  attrs=dict(node.attrs,href=href)
  opening='<a'+''.join(' '+k+'="'+html.escape(v,quote=True)+'"' for k,v in attrs.items())+'>'
  changes.append((node.start,node.open_end,opening))
 return patch(prose,changes)

def load(lang,slug):
 s=source(slug);item=read_json(DATA/'translations'/lang/(slug+'.json'))
 assert item['language']==lang and item['slug']==slug and item['source_sha256']==s['source_sha256'],(lang,slug,'source mismatch')
 for k in ('title','deck','review'):assert isinstance(item.get(k),str) and item[k].strip(),(lang,slug,k)
 if slug=='index':
  for k in ('route_title','route_intro','theory_label','theory_intro'):assert isinstance(item.get(k),str) and item[k].strip(),(lang,k)
  assert len(item['chapters'])==6 and all(isinstance(x,str) and x.strip() for x in item['chapters'])
  validate_inline(item['theory_intro'],s['theory_intro'])
 else:
  assert len(item['body'])==len(s['body']),(lang,slug,'paragraph coverage')
  for original,value in zip(s['body'],item['body']):validate_inline(value,original,True)
  for k in ('entry_door','chapter'):assert isinstance(item.get(k),str) and item[k].strip(),(lang,slug,k)
  validate_inline(item['entry_door'],s['entry_door'])
 return item

def reviewed(complete=False):
 """Only an exact six-language, five-essay receipt unlocks a batch."""
 result={};all_slugs=slugs()
 for p in sorted((DATA/'reviews').glob('batch*.json')):
  r=read_json(p);episodes=r['episodes'];assert len(episodes)==5 and episodes==list(range(episodes[0],episodes[0]+5)) and episodes[0] in (1,6,11,16,21,26)
  assert r['status']=='reviewed' and r.get('independent_semantic_review') is True and r['review_scope'].strip() and r['reviewer'].strip() and r['limitations'].strip()
  expected={f'{lang}/{slug}.json' for lang in LANGS for slug in all_slugs if int(slug[:2]) in episodes}
  assert set(r['translation_sha256'])==expected,(p,'receipt coverage')
  for name,h in r['translation_sha256'].items():
   assert file_sha(DATA/'translations'/name)==h,(name,'review stale')
   lang,filename=name.split('/');key=(lang,filename[:-5]);assert key not in result,'overlapping reviews';result[key]=load(*key)
 if complete:assert len(result)==180,'Full publication requires all six five-essay reviews'
 return result

def title_metadata(text,title,deck):
 escaped=html.escape(title+' — Non Dubito',quote=True)
 text=re.sub(r'<title>.*?</title>',lambda m:'<title>'+escaped+'</title>',text,count=1,flags=re.S)
 text=re.sub(r'(<meta property="og:title" content=")[^"]*(")',lambda m:m[1]+escaped+m[2],text)
 return metadata(text,deck)

def article_region(text,item,lang):
 d=Document(text);s=source(item['slug']);body='\n'+'\n'.join(item['body'])+'\n'
 body=translated_links(body,lang,s['body'],DIRECTORY)
 door=translated_links(item['entry_door'],lang,[s['entry_door']],DIRECTORY)
 return patch(text,[inner(find(d,'article-body'),body),inner(one(d.root.walk(),lambda n:n.tag=='h1','article title'),html.escape(item['title'])),inner(find(d,'chapter-label'),html.escape(item['chapter'])),inner(find(d,'entry-door'),door)])

def index_region(text,items,shared=None,fix_routes=False):
 d=Document(text);changes=[]
 for card in d.root.walk():
  if not card.has('essay-card'):continue
  slug=Path(card.attrs['href']).stem
  if slug not in items:continue
  changes.extend([inner(one(card.walk(),lambda n:n.tag=='h3','card title'),html.escape(items[slug]['title'])),inner(one(card.walk(),lambda n:n.tag=='p','card deck'),html.escape(items[slug]['deck']))])
 if shared:
  route=find(d,'reading-route');door=find(d,'theory-door')
  for node,value in [(one(d.root.walk(),lambda n:n.tag=='h1','index title'),shared['title']),(find(d,'series-deck'),shared['deck']),(one(route.walk(),lambda n:n.tag=='h2','route title'),shared['route_title']),(one(route.walk(),lambda n:n.tag=='p','route intro'),shared['route_intro']),(one(door.walk(),lambda n:n.tag=='span','theory label'),shared['theory_label'])]:changes.append(inner(node,html.escape(value)))
  changes.append(inner(one(door.walk(),lambda n:n.tag=='p','theory intro'),translated_links(shared['theory_intro'],shared['language'],[source('index')['theory_intro']],DIRECTORY)))
  heads=[n for n in d.root.walk() if n.has('chapter-head')];assert len(heads)==6
  for n,value in zip(heads,shared['chapters']):changes.append(inner(one(n.walk(),lambda x:x.tag=='h2','chapter'),html.escape(value)))
 if fix_routes:
  routes=find(d,'route-links');cards={int(Path(n.attrs['href']).stem[:2]):n for n in d.root.walk() if n.has('essay-card')}
  values=[]
  for ep in ROUTE:
   card=cards[ep];slug=Path(card.attrs['href']).stem;title=items[slug]['title'] if slug in items else one(card.walk(),lambda n:n.tag=='h3','route target').text()
   values.append('<a href="'+card.attrs['href']+'"><span>'+f'{ep:02}'+'</span>'+html.escape(title)+'</a>')
  changes.append(inner(routes,''.join(values)))
 return patch(text,changes)

def controls(text,lang):
 text=re.sub(r'<style id="relationships-full-reader">.*?</style>','',text,flags=re.S)
 if lang=='en':
  text=re.sub(r'<script(?: id="relationships-full-controller")?>\(function\(\).*?</script>',lambda m:CONTROLLER,text,count=1,flags=re.S)
  assert text.count('id="relationships-full-controller"')==1
 else:text=re.sub(r' onclick="localStorage\.setItem[^\"]*"','',text)
 return text.replace('</head>',STYLE+'</head>',1)

@tracked_html
def render(complete=False,fix_routes=False,preview=None,preview_index=False):
 assert not complete or preview is None,'Complete publication cannot use unreviewed previews'
 preserved();records=reviewed(complete) if preview is None else {key:load(*key) for key in preview};outputs={}
 # Index metadata gets its own exact hash receipt; unfinished drafts are ignored.
 shared={};rp=DATA/'reviews/index.json'
 if preview_index:
  assert preview is not None,'Index draft preview must be explicit and non-publishing'
  shared={lang:load(lang,'index') for lang in LANGS if (DATA/'translations'/lang/'index.json').exists()}
 elif rp.exists():
  r=read_json(rp);assert r['status']=='reviewed' and r.get('independent_semantic_review') is True and all(isinstance(r.get(k),str) and r[k].strip() for k in ('review_scope','reviewer','limitations'))
  assert set(r['translation_sha256'])=={f'{l}/index.json' for l in LANGS}
  for name,h in r['translation_sha256'].items():
   assert file_sha(DATA/'translations'/name)==h
   lang=name.split('/')[0];shared[lang]=load(lang,'index')
 if complete:assert len(shared)==6,'Index review missing'
 if fix_routes:assert complete,'Route repair is final-publication-only'
 for lang in LANGS:
  items={slug:item for (l,slug),item in records.items() if l==lang}
  if not items and lang not in shared:continue
  directory=page(lang,'index').parent
  assert page(lang,'index').is_file(),'Missing series index'
  assert all(page(lang,slug).is_file() for slug in items),'Missing article page'
  for path in sorted(directory.glob('*.html')):
   text=path.read_text();original=text;slug=path.stem
   if slug in items:
    fn=lambda t:article_region(t,items[slug],lang)
    text=within(text,'lang-en',fn) if lang=='en' else fn(text)
    text=title_metadata(text,items[slug]['title'],items[slug]['deck'])
   if slug=='index':
    fn=lambda t:index_region(t,items,shared.get(lang),fix_routes)
    text=within(text,'lang-en',fn) if lang=='en' else fn(text)
    if lang in shared:text=title_metadata(text,shared[lang]['title'],shared[lang]['deck'])
   editions={s+'.html':{'languages':{lang:i}} for s,i in items.items()}
   text=within(text,'lang-en',lambda t:update_links(t,editions,lang)) if lang=='en' else update_links(text,editions,lang)
   if lang=='en':
    # Shared reading-next cards sit outside the main English div.
    d=Document(text);changes=[]
    for a in d.root.walk():
     if a.tag!='a' or a.attrs.get('href') not in editions:continue
     for n in a.walk():
      if n.tag=='span' and n.has('lang-en') and n.text() not in ('Next in this series','Open series →'):
       if any(parent.has('reading-next-card') for parent in [a]) and not n.text().startswith('Next'):changes.append(inner(n,html.escape(editions[a.attrs['href']]['languages'][lang]['title'])))
    text=patch(text,changes)
    if fix_routes and slug=='index':
     for l in ('zh','hant'):text=within(text,'lang-'+l,lambda t:index_region(t,{},fix_routes=True))
   if text!=original or slug in items or slug=='index':outputs[path]=controls(text,lang)
 for p,text in outputs.items():
  if p.parent!=DIRECTORY:continue
  for l in ('zh','hant'):
   old=region(p.read_text(),l);new=region(text,l)
   if fix_routes and p.stem=='index':old=index_region(old,{},fix_routes=True)
   assert new==old,(p,l,'Chinese prose changed')
 return outputs

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--complete',action='store_true');p.add_argument('--fix-routes',action='store_true');p.add_argument('--preserve-pending-source',action='store_true',help='Publish faithful reviewed translations while retaining unresolved source observations and unchanged Chinese');a=p.parse_args()
 outputs=render(a.complete,a.fix_routes);stale=[p for p,s in outputs.items() if p.read_text()!=s]
 if a.check:
  for p in stale:print('STALE',p.relative_to(ROOT))
 else:

  if stale:
   decisions=read_json(DATA/'pending-source-decisions.json')
   assert decisions['status']=='resolved' or a.preserve_pending_source,'Pending source observations require --preserve-pending-source; no Chinese amendment is approved by this flag'
   if decisions['status']!='resolved':preserved()
  for p in stale:p.write_text(outputs[p])
 print(('Checked' if a.check else 'Rendered'),len(outputs),'pages;',len(stale),'changed; unreviewed drafts ignored')
 return int(a.check and bool(stale))
if __name__=='__main__':raise SystemExit(main())
