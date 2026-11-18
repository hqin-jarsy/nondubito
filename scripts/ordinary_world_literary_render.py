"""Ordinary World literary-template adapter. Drafts live in data/ordinary-world/multilingual.
Run build_ordinary_world_languages.py to compile and render; no shared navigation writes.
"""
import sys,re,json,html
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from prepare_action_sources import Document,Node
from full_series_languages import render_prose
from web_analytics import ensure_analytics
E=html.escape
names={'en':'EN','zh':'中文','zh-hant':'繁體','ja':'日本語','fr':'Français','de':'Deutsch','es':'Español','ko':'한국어'}
ui={
'ja':['目次','前の篇','次の篇','文学・文化','全篇','ホーム','書架','この版について'],
'fr':['Sommaire','Essai précédent','Essai suivant','Littérature et culture','Tous les essais','Accueil','Bibliothèque','À propos de cette édition'],
'de':['Inhalt','Voriger Essay','Nächster Essay','Literatur und Kultur','Alle Essays','Startseite','Bibliothek','Zu dieser Ausgabe'],
'es':['Índice','Ensayo anterior','Ensayo siguiente','Literatura y cultura','Todos los ensayos','Inicio','Biblioteca','Sobre esta edición'],
'ko':['목차','이전 글','다음 글','문학과 문화','전체 글','홈','자료실','이 판본에 대하여']}
def routes(directory,slug,lang=None,absolute=False):
 base='https://nondubito.net/'+directory+'/' if absolute else ('../' if lang else '')
 return {k:base+(slug+'.html?lang='+k if k in ('en','zh','zh-hant') else k+'/'+slug+'.html') for k in names}
def toggle(directory,slug,lang=None):
 rr=routes(directory,slug,lang)
 return '<div class="lang-toggle" style="margin-bottom:.8rem;flex-wrap:wrap;">'+''.join('<a class="lang-btn'+(' active' if k==lang else '')+'" href="'+E(v)+'" lang="'+({'zh':'zh-Hans','zh-hant':'zh-Hant'}.get(k,k))+'">'+names[k]+'</a>' for k,v in rr.items())+'</div>'
def hreflang(directory,slug):
 return '\n'.join('<link rel="alternate" hreflang="'+({'zh':'zh-Hans','zh-hant':'zh-Hant'}.get(k,k))+'" href="'+E(v)+'">' for k,v in routes(directory,slug,absolute=True).items())
def patch_primary(directory,english=None):
 folder=R/directory
 for p in sorted(folder.glob('*.html')):
  text=p.read_text();d=Document(text)
  edits=[]
  if english and p.stem!='index':
   body=next(n for n in d.root.walk() if n.has('essay-body','lang-en'))
   content='<p class="edition-note"><strong>Edition note:</strong> A complete English rendering of the Chinese essay, preserving its scenes and argument. Full-book spoilers.</p>\n'+render_prose(english[p.stem])
   edits.append((body.open_end,body.close_start,content))
  tog=next(n for n in d.root.walk() if n.has('lang-toggle'))
  added=''.join('<span class="lang-sep">|</span><a class="lang-btn" href="'+k+'/'+p.name+'">'+names[k]+'</a>' for k in ('ja','fr','de','es','ko'))
  if 'href="ja/' not in d.raw(tog):edits.append((tog.close_start,tog.close_start,added))
  for a,b,v in sorted(edits,reverse=True):text=text[:a]+v+text[b:]
  text=text.replace("var saved=localStorage.getItem('nd_lang')", "var saved=new URLSearchParams(location.search).get('lang')||localStorage.getItem('nd_lang')")
  if 'hreflang=' not in text:text=text.replace('</head>',hreflang(directory,p.stem)+'\n</head>')
  if english:text=text.replace('Independent English edition','Complete English edition')
  if p.stem=='index':
   text=text.replace('Three reading modes','Eight languages').replace('English · Simplified · Traditional','Eight languages').replace('英文 · 简体 · 繁体','八语阅读').replace('English · 简 / 繁 · Cultural analysis','8 languages · Cultural analysis').replace('英文 · 简 / 繁 · 作品解读','八语 · 作品解读').replace('>英 · 简 · 繁<','>八语阅读<')
   text=text.replace('Five independent English and Chinese essays','Five essays in eight languages').replace('Four independent English and Chinese essays','Five essays in eight languages').replace('English · 简 / 繁 · Literary criticism','8 languages · Literary criticism')
  text=text.replace('class="lang-toggle" style="margin-bottom:.8rem;"','class="lang-toggle" style="margin-bottom:.8rem;display:flex;flex-wrap:wrap;"')
  p.write_text(ensure_analytics(text))
  if p.stem=='index':
   dictionary=folder/'zh-hant-data/index.js'
   if dictionary.exists():
    js=dictionary.read_text();m=re.search(r'var variants = (\{.*?\});',js,re.S)
    if m:
     v=json.loads(m.group(1));v.update({'八语阅读':'八語閱讀','八语 · 作品解读':'八語 · 作品解讀'})
     dictionary.write_text(js[:m.start(1)]+json.dumps(v,ensure_ascii=False,separators=(',',':'))+js[m.end(1):])
def page(directory,lang,slug,title,deck,series_title,body,nav='',count='',note=''):
 u=ui[lang]; depth='../'*(len(Path(directory).parts)+1)
 canonical='https://nondubito.net/'+directory+'/'+lang+'/'+slug+'.html'
 f='Noto+Serif+JP' if lang=='ja' else 'Noto+Serif+KR' if lang=='ko' else 'EB+Garamond'
 intro='<p class="edition-note" style="font-family:var(--sans);font-size:.85rem;color:var(--ink-muted);border-bottom:1px solid var(--cream-border);padding-bottom:1.25rem;margin-bottom:2rem;"><strong>'+E(u[7])+':</strong> '+E(note)+'</p>' if note else ''
 text=f'''<!DOCTYPE html>
<html lang="{lang}" data-lang="{lang}"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{E(title)} — Non Dubito</title><meta name="description" content="{E(deck,quote=True)}"><meta name="author" content="Han Qin (秦汉)">
<meta property="og:type" content="article"><meta property="og:title" content="{E(title,quote=True)} — Non Dubito"><meta property="og:description" content="{E(deck,quote=True)}"><meta property="og:url" content="{canonical}"><meta name="twitter:card" content="summary">
<link rel="canonical" href="{canonical}">{hreflang(directory,slug)}
<link rel="stylesheet" href="{depth}style.css"><link rel="icon" type="image/svg+xml" href="{depth}favicon.svg"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&amp;family=Inter:wght@300;400;500&amp;family={f}:wght@400;500;600&amp;display=swap" rel="stylesheet">
<style>.essay-body{{font-family:{"'Noto Serif JP'," if lang=='ja' else "'Noto Serif KR'," if lang=='ko' else ""}var(--serif),serif;overflow-wrap:break-word}}.lang-toggle{{display:flex;gap:.45rem;flex-wrap:wrap}}.essay-page-title{{overflow-wrap:break-word;text-wrap:balance}}.essay-nav{{max-width:var(--max-w);margin:0 auto;padding:0 1.25rem 3rem;display:flex;flex-wrap:wrap;gap:1rem;justify-content:space-between}}.essay-nav a{{flex:1 1 14rem;min-width:0;overflow-wrap:anywhere}}.essay-card{{color:inherit;text-decoration:none}}</style>
</head><body>
<header><div class="header-inner"><a href="{depth}index.html" class="site-title"><span class="title-latin">Non <span style="color:var(--gold)">Dubito</span></span><span class="title-sub">Essays in the Self-as-an-End Tradition</span></a><nav><a href="{depth}index.html">{u[5]}</a><a href="{depth}library.html">{u[6]}</a><a href="https://self-as-an-end.net" target="_blank" rel="noopener">Self-as-an-End ↗</a></nav></div></header>
<main class="essay-page"><div class="essay-page-hero"><div class="essay-page-inner"><a class="back-link" href="{'../index.html' if slug=='index' else 'index.html'}">← {E('中文 · English' if slug=='index' else series_title)}</a>
{toggle(directory,slug,lang)}<div class="essay-page-num">{E(count)}</div><h1 class="essay-page-title">{E(title)}</h1><div class="essay-page-meta"><span>Han Qin (秦汉)</span><span>{names[lang]}</span></div></div></div>
<div class="essay-body">{intro}{body}</div>{nav}</main>
<footer><div class="footer-inner"><div class="footer-brand"><div class="footer-logo">Non <span>Dubito</span></div><div class="footer-tagline">A mind in many languages</div></div></div><div class="footer-bottom"><span>© 2026 Han Qin (秦汉) · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></span><span>nondubito.net</span></div></footer></body></html>'''
 return ensure_analytics(text)
def render(directory,key):
 source_counts={a['slug']:len(a['body_zh']) for a in json.loads((R/'data'/key/'multilingual/source.json').read_text())['articles']}
 for lang in ('ja','fr','de','es','ko'):
  payload=json.loads((R/'data'/key/'multilingual'/(lang+'.json')).read_text());s=payload['series'];arts=payload['articles'];dest=R/directory/lang;dest.mkdir(exist_ok=True)
  for i,a in enumerate(arts):
   nav='<div class="essay-nav">'+('' if i==0 else '<a href="'+arts[i-1]['slug']+'.html">← '+E(ui[lang][1])+': '+E(arts[i-1]['title'])+'</a>')+('<span></span>' if i+1==len(arts) else '<a href="'+arts[i+1]['slug']+'.html">'+E(ui[lang][2])+': '+E(arts[i+1]['title'])+' →</a>')+'</div>'
   (dest/(a['slug']+'.html')).write_text(page(directory,lang,a['slug'],a['title'],a['deck'],s['title'],render_prose(a['body'])+('<aside class="edition-note"><p>'+E(a['source_note'])+'</p></aside>' if a.get('source_note') and len(a['body'])==source_counts[a['slug']]-1 else ''),nav,str(i+1)+' / '+str(len(arts)),a.get('edition_note','')))
  intro=s.get('intro',[]);intro=[intro] if isinstance(intro,str) else intro
  cards='<div class="essay-list">'+''.join('<a class="essay-card" href="'+a['slug']+'.html"><span class="card-num">'+str(i+1)+'</span><div class="card-body"><h2>'+E(a['title'])+'</h2><p class="card-desc">'+E(a['deck'])+'</p></div></a>' for i,a in enumerate(arts))+'</div>'
  body=render_prose([s['deck']]+intro+([s['note']] if s.get('note') else []))+cards
  (dest/'index.html').write_text(page(directory,lang,'index',s['title'],s['deck'],s['title'],body,count=str(len(arts))+' · 8 '+{'ja':'言語','fr':'langues','de':'Sprachen','es':'idiomas','ko':'개 언어'}[lang]))
if __name__=='__main__':
 directory,key=sys.argv[1:3]
 assert key=='ordinary-world' and directory=='essays/literature/ordinary-world'
 english=None # English patching is coordinated by build_ordinary_world_languages.py
 patch_primary(directory,english);render(directory,key)
