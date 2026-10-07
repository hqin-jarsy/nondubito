#!/usr/bin/env python3
"""Render full film editions from reviewed Markdown, with legacy bodies preserved."""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
import markdown
from import_film_full_editions import ROOT, DATA, LANGS

DATE='2026-10-07'
NAMES={'en':'English','zh':'简体中文','zh-hant':'繁體中文','de':'Deutsch','fr':'Français','es':'Español','ja':'日本語','ko':'한국어'}
GROUPS={'de':'Deutsch','fr':'Français','es':'Español','ja':'日本語','ko':'한국어'}
UI=json.loads((DATA/'ui.json').read_text())
FILMS=json.loads((DATA/'batch01-received.json').read_text())['films']
E=lambda s:html.escape(str(s),quote=True)

def plain(s):
    return html.unescape(re.sub('<[^>]+>','',markdown.markdown(s))).strip()

def index_source(film,lang):
    root=DATA/'reviewed'/film['slug']
    for name in ('INDEX.md','index.md','README.md'):
        p=root/lang/name
        if p.exists():return p,p.read_text()
    p=root/'README.md';s=p.read_text()
    pattern=r'(?m)^(?:## '+re.escape(GROUPS[lang])+r'|\*\*'+re.escape(GROUPS[lang])+r'\*\*)\s*$'
    m=re.search(pattern,s);assert m,(film['slug'],lang)
    rest=s[m.end():]
    end=re.search(r'(?m)^(?:## (?:Deutsch|Français|Español|日本語|한국어)|\*\*(?:Deutsch|Français|Español|日本語|한국어)\*\*)\s*$',rest)
    if end:rest=rest[:end.start()]
    rest=re.sub(r'(?m)^原作版权.*$','',rest)
    return p,rest

def split_copy(film,lang,ep=None):
    if ep is None:p,s=index_source(film,lang)
    else:
        p=DATA/'reviewed'/film['slug']/lang/f'EP{ep:02}.md';s=p.read_text()
    m=re.search(r'(?m)^#{1,3} (.+)$',s);assert m,p
    title=plain(m[1]);text=s[m.end():].strip()
    if ep is None:
        # Delivery-package instructions are not reader-facing edition information.
        text=re.sub(r'(?m)^## (?:Zu dieser Ausgabe|À propos des éditions|Sobre esta edición|この日本語版について|판본과 읽기 안내)\s*\n+[^\n]+\n*','',text)
    paragraphs=re.split(r'\n\s*\n',text)
    # Only publication furniture is removed; essay paragraphs and final notes stay.
    note=r'^\*{0,2}(?:Zur Ausgabe|Zu dieser Ausgabe|Note sur l[’\x27]édition|Note d[’\x27]édition|À propos de cette édition|Sobre esta edición|Nota de edición|Nota sobre esta edición|版について|この版について|판본 안내|판본에 관하여|이 판에 관하여)'
    paragraphs=[x for x in paragraphs if not ('Han Qin' in x and len(x)<260) and not re.search(note,x) and not (ep is not None and re.fullmatch(r'(?:\[[^\]]*\]\([^)]*\)\s*(?:[·|]\s*)?)+',x) and not re.search(r'https?://',x))]
    if ep is None:
        paragraphs=[x for x in paragraphs if not ('·' in x and len(x)<220 and '[' not in x)]
    text='\n\n'.join(paragraphs)
    def link(m):
        label,url=m[1],m[2].strip('<>')
        if urlsplit(url).scheme:return m[0]
        target=(p.parent/url.split('#')[0]).resolve()
        n=re.fullmatch(r'EP0([123])\.md',target.name,re.I)
        if n:return '['+label+']('+film['chapters'][int(n[1])-1]+'.html)'
        if target.name.lower() in ('index.md','readme.md','multilingual_index.md'):return '['+label+'](index.html)'
        raise AssertionError((p,url))
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,text)
    md=markdown.Markdown(extensions=['toc'])
    body=md.convert(text)
    # Series-card headings are not nested article section headings.
    if ep is None:body=re.sub(r'<(/?)h[34]\b',r'<\1h2',body)
    desc=next((plain(x) for x in paragraphs if not x.startswith(('#','[','Han Qin','**')) and len(plain(x))>65),title)
    return dict(title=title,body=body,description=desc[:230],toc=md.toc,source=str(p.relative_to(DATA)))

def menu(film,filename,lang=None,hub=False):
    links=[]
    for key,label in NAMES.items():
        if lang is None and key in ('en','zh','zh-hant'):
            links.append(f'<button class="lang-btn" data-lang="{key}">{label}</button>');continue
        if key==lang:
            links.append(f'<span class="lang-btn active" aria-current="page">{label}</span>');continue
        if key in ('en','zh','zh-hant'):
            href=f'../{filename}?lang={key}'
            handler=f' onclick="localStorage.setItem(\'nd_lang\',\'{key}\')"'
        else:href=f'{"../" if lang else ""}{key}/{filename}';handler=''
        links.append(f'<a class="lang-btn edition-link" href="{href}"{handler}>{label}</a>')
    return '<div class="lang-toggle" aria-label="Language">'+''.join(links)+'</div>'

def alternate_links(slug,filename,hub=False):
    base='https://nondubito.net/essays/film/'+(slug+'/' if slug else '')
    suffix='' if filename=='index.html' else filename
    return ''.join(f'<link rel="alternate" hreflang="{l}" href="{base+l+"/"+suffix}">' for l in LANGS)+f'<link rel="alternate" hreflang="x-default" href="{base+suffix}">'

def page(film,lang,copy,ep=None,hub=False):
    u=UI[lang];slug=film['slug'];filename=film['chapters'][ep-1]+'.html' if ep else 'index.html'
    depth='../../../' if hub else '../../../../'
    route='essays/film/'+('' if hub else slug+'/')+lang+'/'
    canonical='https://nondubito.net/'+route+('' if filename=='index.html' else filename)
    series_href='index.html';cinema_href='index.html' if hub else '../../'+lang+'/index.html'
    schema={'@context':'https://schema.org','@type':'Article' if ep else 'CollectionPage','headline':copy['title'],'name':copy['title'],'description':copy['description'],'url':canonical,'inLanguage':lang,'author':{'@type':'Person','name':'Han Qin (秦汉)'},'datePublished':DATE,'dateModified':DATE}
    nav=''
    if ep:
        schema['isPartOf']={'@type':'CollectionPage','url':'https://nondubito.net/'+route}
        nav='<nav class="ff-nav">'
        if ep>1:nav+=f'<a href="{film["chapters"][ep-2]}.html">← {E(u["previous"])}</a>'
        nav+=f'<a href="index.html">{E(u["all"])}</a>'
        if ep<3:nav+=f'<a href="{film["chapters"][ep]}.html">{E(u["next"])} →</a>'
        nav+='</nav>'
    elif not hub:
        schema['hasPart']=[{'@type':'Article','url':'https://nondubito.net/'+route+x+'.html'} for x in film['chapters']]
    toc=f'<details class="ff-toc"><summary>{E(u["toc"])}</summary>{copy["toc"]}</details>' if ep else ''
    title=E(copy['title']);description=E(copy['description'])
    body=(f'<p class="ff-meta">{E(u["edition"])}</p>' if not hub else '')+copy['body']
    return f'''<!DOCTYPE html>
<html lang="{lang}" data-lang="{lang}" data-editions="{lang}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} — Non Dubito</title><meta name="description" content="{description}"><meta name="author" content="Han Qin (秦汉)"><link rel="canonical" href="{canonical}">{alternate_links('' if hub else slug,filename)}<meta property="og:title" content="{title}"><meta property="og:description" content="{description}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="{'article' if ep else 'website'}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary"><link rel="icon" href="{depth}favicon.svg"><link rel="stylesheet" href="{'../' if hub else '../../'}film-editions.css?v=20261007"><script defer src="{depth}language-select.js"></script><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head><body><a class="ff-skip" href="#main">↓ {E(u['read'])}</a><header class="ff-header"><a class="ff-brand" href="{depth}index.html">Non <span>Dubito</span></a><nav><a href="{cinema_href}">{E(u['cinema'])}</a><a href="{depth}essays/{lang}/index.html">{NAMES[lang]}</a><a href="{depth}library.html">{E(u['library'])}</a></nav></header><main id="main" class="ff-page">{menu(film,filename,lang,hub)}<p class="ff-kicker">NON DUBITO · {E(u['cinema'])}{' · '+str(ep)+' / 3' if ep else ''}</p><h1>{title}</h1><p class="ff-meta">Han Qin (秦汉) · {E(u['updated'])}</p>{toc}<div class="ff-body">{body}</div>{nav}</main><footer class="ff-footer"><a href="{cinema_href}">← {E(u['cinema'])}</a><p>© 2026 Han Qin (秦汉) · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · Non Dubito</p></footer></body></html>
'''

def legacy(path,film,hub=False):
    s=path.read_text();filename=path.name
    s,n=re.subn(r'<div class="lang-toggle"[^>]*>.*?</div>',lambda m:menu(film,filename),s,count=1,flags=re.S)
    assert n==1,path
    depth='../../' if hub else '../../../'
    s=re.sub(r'<!-- film-full-head -->.*?<!-- /film-full-head -->','',s,flags=re.S)
    extra=f'''<!-- film-full-head -->{alternate_links('' if hub else film['slug'],filename)}<style>.lang-toggle:not(.lang-select-menu){{flex-wrap:wrap;max-width:100%;gap:.4rem}}.lang-toggle .edition-link{{text-decoration:none}}</style><script>(function(){{var l=new URLSearchParams(location.search).get('lang');if(['en','zh','zh-hant'].indexOf(l)>=0){{localStorage.setItem('nd_lang',l);localStorage.setItem('nondubito-lang',l);document.documentElement.dataset.lang=l;document.documentElement.lang=l==='zh'?'zh-Hans':l;}}}})();</script><script defer src="{depth}language-select.js"></script><!-- /film-full-head -->'''
    s=s.replace('</head>',extra+'</head>',1)
    # Update only the hero's edition label, outside all protected essay bodies.
    boundary=s.index('<div class="essay-body')
    head,body=s[:boundary],s[boundary:]
    if hub:
        head=head.replace('Fifty-nine series · One hundred seventy-seven essays · Three reading modes','59 film series · 177 essays · First 5 series in 8 languages')
        head=head.replace('五十九个系列 · 一百七十七篇 · 英 / 简 / 繁','59 个系列 · 177 篇 · 首批 5 部作品八语齐备')
    else:
        head=head.replace('English · Simplified · Traditional','8 language editions')
        head=head.replace('英文 · 简体 · 繁体','八种语言版本')
    s=head+body
    return s

def outputs():
    out={};series={}
    for film in FILMS:
        for lang in LANGS:
            root=ROOT/'essays/film'/film['slug']/lang
            c=split_copy(film,lang);series[film['slug'],lang]=c
            out[root/'index.html']=page(film,lang,c)
            for ep,slug in enumerate(film['chapters'],1):out[root/(slug+'.html')]=page(film,lang,split_copy(film,lang,ep),ep)
        for name in ['index',*film['chapters']]:
            p=ROOT/'essays/film'/film['slug']/(name+'.html');out[p]=legacy(p,film)
    for lang in LANGS:
        u=UI[lang];cards=''.join(f'<a class="ff-card" href="../{f["slug"]}/{lang}/index.html"><span>{f["number"]:02}</span><h2>{E(series[f["slug"],lang]["title"])}</h2><p>{E(series[f["slug"],lang]["description"])}</p></a>' for f in FILMS)
        c={'title':u['cinema'],'description':u['intro'],'body':f'<p>{E(u["intro"])}</p><p class="ff-meta">{E(u["published"])}</p><div class="ff-grid">{cards}</div>'}
        out[ROOT/'essays/film'/lang/'index.html']=page({'slug':'','chapters':[]},lang,c,hub=True)
    p=ROOT/'essays/film/index.html';out[p]=legacy(p,{'slug':''},hub=True)
    return out

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--check',action='store_true');args=a.parse_args()
    pages=outputs()
    for p,s in pages.items():
        if args.check:assert p.exists() and p.read_text()==s,p
        else:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
    print(('Verified' if args.check else 'Built'),len(pages),'film pages')
