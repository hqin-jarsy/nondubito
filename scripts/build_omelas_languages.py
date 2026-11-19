#!/usr/bin/env python3
"""Render the two approved Omelas essays, preserving the established primary URLs."""
from pathlib import Path
import json,re,html
from prepare_action_sources import Document
from full_series_languages import render_prose
from web_analytics import ensure_analytics
import don_literary_render as layout
R=Path(__file__).resolve().parents[1];D=R/'data/omelas/multilingual';DIR='essays/science-fiction/the-ones-who-walk-away-from-omelas';F=R/DIR
LANGS=['en','zh','zh-hant','ja','fr','de','es','ko'];SLUGS=['1-why-happiness-needs-a-child','2-what-walking-away-refuses'];E=html.escape
CLASS={'en':'en','zh':'zh','zh-hant':'hant'}
def body(a,note):return render_prose(a['body'])+'<aside class="edition-note" style="margin-top:2.5rem;font-size:.9rem;color:var(--ink-muted)"><p>'+E(note)+'</p></aside>'
def index_body(payload,lang):
 s=payload['series'];cards=[]
 for i,a in enumerate(payload['articles']):
  cards.append('<a href="'+a['slug']+'.html" class="essay-card"><span class="card-num">'+['I','II'][i]+'</span><div class="card-body"><h2>'+E(a['title'])+'</h2><p class="card-desc">'+E(a['deck'])+'</p><div class="card-meta"><span>2026</span><span class="card-badge full">'+('八語閱讀' if lang=='zh-hant' else '八语阅读' if lang=='zh' else '8 languages')+'</span></div></div></a>')
 return '<p class="sf-intro">'+E(s['deck'])+'</p><p class="edition-note">'+E(s['source_note'])+'</p><div class="essay-list" style="margin-top:3rem">'+''.join(cards)+'</div>'
def primary_nav(payload, language, article):
 other=payload['articles'][1-article]
 href=E(other['slug']+'.html')
 title=E(other['title'])
 if article == 0:
  return f'<div class="essay-nav"><span></span><span><a href="{href}">{title} →</a></span></div>'
 back={'en':'Back to the series','zh':'返回系列','zh-hant':'返回系列'}[language]
 return f'<div class="essay-nav"><span><a href="{href}">← {title}</a></span><span><a href="index.html">{back} →</a></span></div>'

def main():
 data={l:json.loads((D/(l+'.json')).read_text()) for l in LANGS}
 for l,p in data.items():
  assert [a['slug'] for a in p['articles']]==SLUGS
  assert [len(a['body']) for a in p['articles']]==[7,5],l
 for slug in ['index']+SLUGS:
  path=F/(slug+'.html');text=path.read_text();doc=Document(text);edits=[];article=None if slug=='index' else SLUGS.index(slug)
  for l,suffix in CLASS.items():
   p=data[l];a=p['series'] if article is None else p['articles'][article];title=a['title']
   n=next(n for n in doc.root.walk() if n.has('essay-page-title','lang-'+suffix));edits.append((n.open_end,n.close_start,E(title)))
   n=next(n for n in doc.root.walk() if n.has('essay-body','lang-'+suffix));content=index_body(p,l) if article is None else body(a,p['series']['source_note'])+primary_nav(p,l,article);edits.append((n.open_end,n.close_start,content))
  for start,end,new in sorted(edits,reverse=True):text=text[:start]+new+text[end:]
  en=data['en']['series'] if article is None else data['en']['articles'][article]
  text=re.sub(r'<title>.*?</title>','<title>'+E(en['title'])+' — Non Dubito</title>',text)
  for key,val in [('description',en['deck']),('og:description',en['deck']),('og:title',en['title']+' — Non Dubito')]:
   text=re.sub(r'(<meta (?:name|property)="'+re.escape(key)+r'" content=")[^"]*',lambda m:m[1]+E(val,quote=True),text)
  # Do not rewrite historic canonical/og URLs, publication dates, header or footer.
  text=text.replace("var saved=localStorage.getItem('nd_lang')","var saved=new URLSearchParams(location.search).get('lang')||localStorage.getItem('nd_lang')")
  # Keep query, saved preference and navigation aligned after an explicit switch.
  text=text.replace("btn.classList.toggle('active',btn.getAttribute('data-lang')===cur);", "btn.classList.toggle('active',btn.getAttribute('data-lang')===cur);btn.setAttribute('aria-pressed',String(btn.getAttribute('data-lang')===cur));") if "btn.setAttribute('aria-pressed'" not in text else text
  marker="localStorage.setItem('nondubito-lang',lang);update();"
  replacement="localStorage.setItem('nondubito-lang',lang);var url=new URL(location.href);url.searchParams.set('lang',lang);history.replaceState(history.state,'',url.href);update();"
  text=text.replace(marker,replacement).replace("history.replaceState(null,'',url.href)","history.replaceState(history.state,'',url.href)")
  marker="});}btns.forEach(function(btn){btn.addEventListener"
  replacement="});document.querySelectorAll('a[href]').forEach(function(a){var u=new URL(a.getAttribute('href'),location.href);var base=location.pathname.slice(0,location.pathname.lastIndexOf('/')+1);if(u.origin===location.origin&&u.pathname.slice(0,u.pathname.lastIndexOf('/')+1)===base&&u.pathname.endsWith('.html')){u.searchParams.set('lang',cur);a.setAttribute('href',u.pathname.slice(base.length)+u.search+u.hash);}});}btns.forEach(function(btn){btn.addEventListener"
  if "document.querySelectorAll('a[href]').forEach" not in text:text=text.replace(marker,replacement)

  text=re.sub(r'<link rel="alternate"[^>]+>\s*','',text)
  text=text.replace('</head>',layout.hreflang(DIR,slug)+'\n</head>')
  d=Document(text);n=next(n for n in d.root.walk() if n.has('lang-toggle'));inside=d.raw(n)
  if 'href="ja/' not in inside:
   links=''.join('<span class="lang-sep">|</span><a class="lang-btn" href="'+l+'/'+slug+'.html">'+layout.names[l]+'</a>' for l in LANGS[3:]);text=text[:n.close_start]+links+text[n.close_start:]
  text=text.replace('class="lang-toggle" style="margin-bottom:.8rem;"','class="lang-toggle" style="margin-bottom:.8rem;display:flex;flex-wrap:wrap;"')
  text=text.replace('English · Simplified · Traditional','Eight languages').replace('英文 · 简体 · 繁体','八语阅读').replace('英文 · 簡體 · 繁體','八語閱讀').replace('Independent English edition','English translation of the revised Chinese essay')
  path.write_text(ensure_analytics(text))
 for l in LANGS[3:]:
  p=data[l];s=p['series'];dest=F/l;dest.mkdir(exist_ok=True)
  for i,a in enumerate(p['articles']):
   other=p['articles'][1-i];nav='<div class="essay-nav"><a href="'+other['slug']+'.html">'+('← ' if i else '')+E(other['title'])+(' →' if not i else '')+'</a></div>'
   (dest/(a['slug']+'.html')).write_text(layout.page(DIR,l,a['slug'],a['title'],a['deck'],s['title'],body(a,s['source_note']),nav,str(i+1)+' / 2'))
  (dest/'index.html').write_text(layout.page(DIR,l,'index',s['title'],s['deck'],s['title'],index_body(p,l),count='2 · 8 '+{'ja':'言語','fr':'langues','de':'Sprachen','es':'idiomas','ko':'개 언어'}[l]))
 # Existing three primary-language category cards, without altering other works.
 path=R/'essays/science-fiction/index.html';text=path.read_text();d=Document(text);cards=[n for n in d.root.walk() if n.tag=='a' and n.attrs.get('href')==F.name+'/index.html'];assert len(cards)==3
 edits=[]
 search=' '.join(data[l]['series']['title']+' '+data[l]['series']['deck'] for l in CLASS)
 for n,l in zip(cards,CLASS):
  raw=d.raw(n);p=data[l]['series'];raw=re.sub(r'data-search="[^"]*"','data-search="'+E(search,quote=True)+'"',raw)
  raw=re.sub(r'(<h2[^>]*>).*?(</h2>)',lambda m:m[1]+E(p['title'])+m[2],raw)
  raw=re.sub(r'(<p[^>]*>).*?(</p>)',lambda m:m[1]+E(p['deck'])+m[2],raw)
  raw=raw.replace('EN / 简 / 繁','8 languages').replace('英 / 简 / 繁','八语').replace('英 / 簡 / 繁','八語');edits.append((n.start,n.end,raw))
 for a,b,v in sorted(edits,reverse=True):text=text[:a]+v+text[b:]
 path.write_text(text)
 print('Omelas: 2 approved essays in eight languages; 18 physical pages, original primary URLs retained.')
if __name__=='__main__':main()
