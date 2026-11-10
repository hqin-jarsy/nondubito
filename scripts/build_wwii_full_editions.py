#!/usr/bin/env python3
"""Render complete WWII translations from frozen, reviewed units, never prose.

A source-finalization receipt and exact independent five-essay language reviews
are required for writes. Drafts can only render to an explicitly separate preview
folder. Original pages remain in data/wwii-full/baseline for comparison.
"""
import argparse,hashlib,html,json,re
from pathlib import Path
from prepare_action_sources import Document,Node,one
from web_analytics import tracked_html
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/wwii-full';DIRECTORY=ROOT/'essays/wwii'
LANGS=('en','ja','fr','de','es','ko');SLUGS=('1-weimar','2-institutions','3-four-systems','4-promise','5-cracks')
LABELS={'en':'EN','zh':'简体','zh-hant':'繁體','ja':'日本語','fr':'Français','de':'Deutsch','es':'Español','ko':'한국어'}
NOTES={'ja':'中国語の全段落に対応する完全版です。歴史上の留保と各言語の表現を確認しています。','fr':'Version intégrale fondée sur tous les paragraphes chinois, avec les précisions historiques nécessaires.','de':'Vollständige Fassung auf Grundlage aller chinesischen Absätze. Historische Präzisierungen bleiben erhalten; Erklärung bedeutet weder Entschuldigung noch eine Zuschreibung kollektiver Schuld.','es':'Versión íntegra basada en todos los párrafos chinos, con las precisiones históricas necesarias.','ko':'중국어 본문의 모든 문단에 대응하는 완전판입니다. 필요한 역사적 한정과 표현을 함께 검토했습니다.'}
STYLE='''<style id="wwii-full-style">.essay-page-title,.essay-header h1,.series-title,.essay-body,.entry-title,.nav-title{overflow-wrap:anywhere}.essay-page-title,.essay-header h1,.series-title,.entry-title,.nav-title{hyphens:auto;-webkit-hyphens:auto}.essay-card,.card-body,.nav-copy,.entry-row,.series-nav a{min-width:0}.lang-toggle{display:flex;flex-wrap:wrap;gap:.45rem;align-items:center}.wwii-primary .lang-en,.wwii-primary .lang-zh,.wwii-primary .lang-hant{display:none!important}.wwii-primary[data-lang="en"] .lang-en,.wwii-primary[data-lang="zh"] .lang-zh,.wwii-primary[data-lang="zh-hant"] .lang-hant{display:revert!important}.wwii-primary[data-lang="en"] .lang-zh,.wwii-primary[data-lang="en"] .lang-hant,.wwii-primary[data-lang="zh"] .lang-en,.wwii-primary[data-lang="zh"] .lang-hant,.wwii-primary[data-lang="zh-hant"] .lang-en,.wwii-primary[data-lang="zh-hant"] .lang-zh{display:none!important}html[lang="ko"] .essay-body{word-break:keep-all}html[lang="ja"] .essay-body,html[lang="ko"] .essay-body{font-family:var(--cjk),serif}</style>'''
CONTROLLER='''<script id="wwii-full-controller">(function(){function read(k){try{return localStorage.getItem(k)}catch(e){return null}}function save(k,v){try{localStorage.setItem(k,v)}catch(e){}}function valid(v){return ['en','zh','zh-hant'].indexOf(v)!==-1}var q=new URLSearchParams(location.search).get('lang'),saved=q||read('nd_lang')||read('nondubito-lang')||'zh';if(!valid(saved))saved='zh';save('nd_lang',saved);save('nondubito-lang',saved);function apply(){document.documentElement.dataset.lang=saved;document.documentElement.lang=saved==='zh-hant'?'zh-Hant':saved==='zh'?'zh-Hans':'en';document.querySelectorAll('[data-lang-button]').forEach(function(b){b.classList.toggle('active',b.dataset.langButton===saved);b.setAttribute('aria-pressed',String(b.dataset.langButton===saved))});document.querySelectorAll('a[data-primary-route]').forEach(function(a){var u=new URL(a.href,location.href);u.searchParams.set('lang',saved);a.href=u.pathname+u.search+u.hash})}apply();document.addEventListener('DOMContentLoaded',function(){apply();document.querySelectorAll('[data-lang-button]').forEach(function(b){b.addEventListener('click',function(){var v=b.dataset.langButton;if(!valid(v))return;saved=v;save('nd_lang',saved);save('nondubito-lang',saved);var u=new URL(location.href);u.searchParams.set('lang',saved);history.replaceState(null,'',u);apply()})})})})();</script>'''
def read_json(p):return json.loads(p.read_text())
def digest(value):return hashlib.sha256(value if isinstance(value,bytes) else value.encode()).hexdigest()
def file_sha(p):return digest(p.read_bytes())
def source(slug):return read_json(DATA/'sources'/(slug+'.json'))
def find(d,cls):return one(d.root.walk(),lambda n:n.has(cls),cls)
def patch(text,edits):
 for a,b,value in sorted(edits,reverse=True):text=text[:a]+value+text[b:]
 return text

def validate(item,lang,slug):
 s=source(slug);assert item['language']==lang and item['slug']==slug and item['source_sha256']==s['source_sha256'],(lang,slug,'source mismatch')
 assert all(isinstance(item.get(k),str) and item[k].strip() for k in ('title','deck'))
 assert isinstance(item.get('review'),(str,dict)) and item['review'],(lang,slug,'missing review annotation')
 assert len(item['body'])==len(s['body']),(lang,slug,'coverage')
 for original,value in zip(s['body'],item['body']):
  assert isinstance(value,str) and value.strip() and not re.search(r'TODO|TBD|\[VERIFY|\ufffd',value),(lang,slug,'incomplete draft')
  d=Document(value);nodes=[n for n in d.root.children if isinstance(n,Node)];o=Document(original);on=[n for n in o.root.children if isinstance(n,Node)]
  assert len(nodes)==len(on)==1 and nodes[0].tag==on[0].tag and nodes[0].text().strip(),(lang,slug,'block mismatch')
  assert all(n.tag in ('root','h2','p','em','strong','a','br','sup','sub') for n in d.root.walk())
  assert not any(isinstance(n,str) and n.strip() for n in d.root.children)
  for n in d.root.walk():assert all(k in ('href','title') for k in n.attrs)
  assert [n.attrs.get('href') for n in d.root.walk() if n.tag=='a']==[n.attrs.get('href') for n in o.root.walk() if n.tag=='a']
 return item

def load(lang,slug):return validate(read_json(DATA/'translations'/lang/(slug+'.json')),lang,slug)
def reviewed():
 state=read_json(DATA/'source-finalization.json');assert state['status']=='approved' and not state['unresolved'], 'Source questions remain pending'
 assert state['source_files']=={s+'.json':file_sha(DATA/'sources'/(s+'.json')) for s in SLUGS},'Source finalization stale'
 for lang in LANGS+('zh-Hant',):
  r=read_json(DATA/'reviews'/(lang+'.json'))
  assert r['status']=='reviewed' and r['independent_semantic_review'] is True and r['reviewer'] and r['scope'] and r['limitations']
  if lang=='zh-Hant':assert r['index_traditional_sha256']==file_sha(DATA/'index-traditional.json'),'Traditional index review stale'
  assert r['files']=={s+'.json':file_sha(DATA/'translations'/lang/(s+'.json')) for s in SLUGS},(lang,'stale or incomplete review')
 return {(l,s):load(l,s) for l in LANGS+('zh-Hant',) for s in SLUGS}
def controls(text,lang,slug):
 d=Document(text);n=find(d,'lang-toggle');buttons=[]
 for code,label in LABELS.items():
  if lang=='en' and code in ('en','zh','zh-hant'):buttons.append(f'<button class="lang-btn" data-lang-button="{code}">{label}</button>')
  elif code==lang:buttons.append(f'<span class="lang-btn active" aria-current="page">{label}</span>')
  else:
   href=(('' if lang=='en' else '../')+slug+'.html?lang='+code) if code in ('en','zh','zh-hant') else (('' if lang=='en' else '../')+code+'/'+slug+'.html')
   buttons.append(f'<a class="lang-btn" href="{href}">{label}</a>')
 text=patch(text,[(n.open_end,n.close_start,'\n'+'\n<span class="lang-sep">|</span>\n'.join(buttons)+'\n')])
 text=re.sub(r' onclick="localStorage\.setItem[^\"]*"','',text)
 if lang=='en':
  d=Document(text);number=find(d,'essay-page-num')
  label={'zh':'二战与人的目的','hant':'二戰與人的目的','en':'World War II and the Person as an End'}
  prefix=('Series · ' if slug=='index' else str(SLUGS.index(slug)+1)+' / 5 · ')
  text=patch(text,[(number.open_end,number.close_start,''.join('<span class="lang-'+code+'">'+prefix+title+'</span>' for code,title in label.items()))])
  text=re.sub(r'<html\b[^>]*>','<html lang="zh-Hans" data-lang="zh" class="wwii-primary">',text,count=1)
  text=re.sub(r'<script>\s*\(function\(\)\{.*?</script>',lambda m:CONTROLLER,text,count=1,flags=re.S)
  assert text.count('id="wwii-full-controller"')==1
  text=re.sub(r'(<a\b[^>]*href=")(index|[1-5]-[^"?/]+)(\.html)(")',r'\1\2\3\4 data-primary-route="1"',text)
 return text.replace('href="../../../index.html#essays"','href="../../../library.html"').replace('</head>',STYLE+'</head>',1)
def metadata(text,title,deck):
 esc=html.escape(title+' — Non Dubito',quote=True);text=re.sub(r'<title>.*?</title>',lambda m:'<title>'+esc+'</title>',text,count=1,flags=re.S)
 text=re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*(")',lambda m:m[1]+html.escape(deck,quote=True)+m[2],text)
 return re.sub(r'(<meta property="og:title" content=")[^"]*(")',lambda m:m[1]+esc+m[2],text)

@tracked_html
def render(preview=False):
 items={(l,s):load(l,s) for l in LANGS+('zh-Hant',) for s in SLUGS} if preview else reviewed();out={}
 for slug in SLUGS:
  s=source(slug)
  for lang in LANGS:
   item=items[lang,slug];base=DATA/'baseline'/('' if lang=='en' else lang)/(slug+'.html');text=base.read_text();d=Document(text);edits=[]
   if lang=='en':
    for code,body in [('en',item['body']),('zh',s['body'])]:
     node=one(d.root.walk(),lambda n:n.has('essay-body') and n.has('lang-'+code),'body');edits.append((node.open_end,node.close_start,'\n'+'\n'.join(body)+'\n'))
     if code=='zh':edits.append((node.end,node.end,'\n<div class="essay-body lang-hant" style="font-family:var(--cjk),serif;">\n'+'\n'.join(items['zh-Hant',slug]['body'])+'\n</div>'))
    h=one(d.root.walk(),lambda n:n.tag=='h1' and n.has('lang-en'),'English title');edits.append((h.open_end,h.close_start,html.escape(item['title'])))
    h=one(d.root.walk(),lambda n:n.tag=='h1' and n.has('lang-zh'),'Chinese title');edits.append((h.end,h.end,'<h1 class="essay-page-title lang-hant" style="font-family:var(--cjk),serif;">'+html.escape(items['zh-Hant',slug]['title'])+'</h1>'))
   else:
    b=find(d,'essay-body');edits.append((b.open_end,b.close_start,'\n'+'\n'.join(item['body'])+'\n'))
    h=one(d.root.walk(),lambda n:n.tag=='h1','title');edits.append((h.open_end,h.close_start,html.escape(item['title'])))
    entry=find(d,'essay-entry-point');edits.append((entry.open_end,entry.close_start,html.escape(item['deck'])))
    note=find(d,'source-note');edits.append((note.open_end,note.close_start,'<p>'+NOTES[lang]+' <a href="../'+slug+'.html?lang=zh">中文</a> · <a href="../'+slug+'.html?lang=en">English</a></p>'))
    for a in d.root.walk():
     if a.tag=='a':
      target=Path(a.attrs.get('href','')).stem
      for n in a.walk():
       if n.has('nav-title') and target in SLUGS:edits.append((n.open_end,n.close_start,html.escape(items[lang,target]['title'])))
   if lang=='en':
    for a in d.root.walk():
     href=a.attrs.get('href','') if a.tag=='a' else ''
     if not re.fullmatch(r'(index|[1-5]-[^/]+)\.html',href):continue
     target=Path(href).stem;labels=[]
     for code in ('zh','en','hant'):
      if target=='index':label={'zh':'← 二战与人的目的','en':'← World War II and the Person as an End','hant':'← 二戰與人的目的'}[code]
      elif target in SLUGS:
       title=source(target)['title'] if code=='zh' else items['en' if code=='en' else 'zh-Hant',target]['title']
       label=('← ' if SLUGS.index(target)<SLUGS.index(slug) else '→ ')+title
      else:continue
      labels.append('<span class="lang-'+code+'">'+html.escape(label)+'</span>')
     edits.append((a.open_end,a.close_start,''.join(labels)))
   text=patch(text,edits);text=controls(text,lang,slug)
   if lang!='en':text=metadata(text,item['title'],item['deck'])
   out=(out|{(DIRECTORY if lang=='en' else DIRECTORY/lang)/(slug+'.html'):text})
 out.update(indexes(items))
 return out

def indexes(items):
 out={};base=(DATA/'baseline/index.html').read_text();d=Document(base);b=find(d,'essay-body')
 paras=[n for n in b.children if isinstance(n,Node) and n.tag=='p' and not n.has('lang-zh') and not n.has('lang-en')]
 assert len(paras)==2
 en_intro=['From the railway carriage of 1918 to the opening of the Berlin Wall in 1989, and on to the present. This series asks: when systems confront human beings, how can people truly become ends rather than tools?','The Second World War was more than a struggle between good and evil. It placed the relationship between institutions, systems, and people under extreme pressure. How far can a system go when it treats people as means? When cracks exist in a system, what can they make possible? Five essays, from Weimar’s collapse to the end of the Cold War, look in the ruins of history for answers that still matter today.']
 index_data=read_json(DATA/'index-traditional.json')
 blocks=[]
 for code in ('zh','en','hant'):
  intro=[n.text().strip() for n in paras] if code=='zh' else en_intro if code=='en' else index_data['intro']
  note={'zh':'全系列提供简体、繁體及六种外语全文版本。','hant':'全系列提供簡體、繁體及六種外語全文版本。','en':'Complete editions in Simplified and Traditional Chinese and six other languages.'}[code]
  content='<p class="edition-note">'+note+'</p>'+''.join('<p>'+html.escape(x)+'</p>' for x in intro)+'<div class="essay-list">'
  for i,slug in enumerate(SLUGS):
   card=one(d.root.walk(),lambda n:n.tag=='a' and n.has('essay-card') and n.attrs.get('href')==slug+'.html','card')
   title=source(slug)['title'] if code=='zh' else items['en' if code=='en' else 'zh-Hant',slug]['title']
   deck=one(card.walk(),lambda n:n.has('card-desc'),'deck').text() if code=='zh' else items['en',slug]['deck'] if code=='en' else index_data['decks'][i]
   q={'en':'en','zh':'zh','hant':'zh-hant'}[code]
   content+=f'<a class="essay-card" href="{slug}.html?lang={q}"><span class="card-num">{i+1:02}</span><div class="card-body"><div class="card-title-en">{html.escape(title)}</div><p class="card-desc">{html.escape(deck)}</p></div></a>'
  blocks.append('<div class="essay-body lang-'+code+'">'+content+'</div></div>')
 h=one(d.root.walk(),lambda n:n.tag=='h1','title');titles='<h1 class="essay-page-title lang-zh">二战与人的目的</h1><h1 class="essay-page-title lang-hant">二戰與人的目的</h1><h1 class="essay-page-title lang-en">World War II and the Person as an End</h1>'
 text=patch(base,[(b.start,b.end,'\n'.join(blocks)),(h.start,h.end,titles)]).replace('七种语言 · History &amp; Philosophy','8 reading editions · History &amp; Philosophy')
 out[DIRECTORY/'index.html']=controls(text,'en','index')
 for lang in LANGS[1:]:
  text=(DATA/'baseline'/lang/'index.html').read_text();d=Document(text);edits=[]
  for a in d.root.walk():
   if not a.has('entry-row'):continue
   slug=Path(a.attrs['href']).stem
   if slug not in SLUGS:continue
   for cls,key in [('entry-title','title'),('entry-desc','deck')]:
    n=one(a.walk(),lambda n:n.has(cls),cls);edits.append((n.open_end,n.close_start,html.escape(items[lang,slug][key])))
  out[DIRECTORY/lang/'index.html']=controls(patch(text,edits),lang,'index')
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--preview',type=Path);a=p.parse_args();out=render(preview=a.preview is not None);changed=[]
 if a.preview:
  assert not a.preview.resolve().is_relative_to(ROOT.resolve()),'Preview must be outside the repository'
 for path,text in out.items():
  dest=a.preview/path.relative_to(ROOT) if a.preview else path
  if not dest.exists() or dest.read_text()!=text:
   changed.append(str(dest))
   if not a.check:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text)
 if a.check and changed:raise SystemExit('Stale WWII render: '+', '.join(changed))
 print(('Verified' if a.check else 'Rendered')+' '+str(len(out))+' complete readers; changed '+str(len(changed)))
if __name__=='__main__':main()
