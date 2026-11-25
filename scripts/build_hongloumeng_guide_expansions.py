#!/usr/bin/env python3
"""Publish the six Red Chamber reader guides, not the novel or academic papers."""
from __future__ import annotations
import argparse
import datetime
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

from build_hongloumeng_hub import ROOT,TARGET,ORIGIN,EDITIONS,load_readings
import build_home_updates as home
import build_search_index as search
from build_sitemap import parse_page,sitemap_xml
from full_series_languages import inline_markdown
from prepare_action_sources import Document,Node,one

DATA=ROOT/'data/hongloumeng/reader-guide-expansion.json'
LANGS={'ja':'日本語','fr':'Français','de':'Deutsch','es':'Español','ko':'한국어'}
EXTRAS={
 'ja':('本文へ移動','読書言語','書架','検索','続編を読む','目次','サイト内ナビゲーション'),
 'fr':('Aller au texte','Langue de lecture','Bibliothèque','Rechercher','Lire la suite originale','Sommaire','Navigation'),
 'de':('Zum Text','Lesesprache','Bibliothek','Suche','Die eigenständige Fortsetzung lesen','Übersicht','Navigation'),
 'es':('Ir al texto','Idioma de lectura','Biblioteca','Buscar','Leer la continuación original','Índice','Navegación del sitio'),
 'ko':('본문으로 건너뛰기','읽기 언어','서가','검색','창작 속편 읽기','차례','사이트 탐색'),
}
ALL={**EDITIONS,**{l:(l+'/',l,n) for l,n in LANGS.items()}}
OLD_SCOPE={'zh':'六篇导读提供八语全文，不要求先读论文。涉及前八十回及通行续书的情节；不提前揭开原创后三十回的关键转折和最终归宿。',
 'zh-hant':'六篇導讀提供八語全文，不要求先讀論文。涉及前八十回及通行續書的情節；不提前揭開原創後三十回的關鍵轉折和最終歸宿。',
 'en':'All six reader essays are available in eight languages. No paper is required first. They discuss the first eighty chapters and the received continuation without revealing the decisive turns or endings of the original continuation.'}
SLUGS=tuple(f'reading-{i:02d}' for i in range(1,7))
START='<!-- RED CHAMBER GUIDE LANGUAGES START -->'
END='<!-- RED CHAMBER GUIDE LANGUAGES END -->'
BLOCK=re.compile(re.escape(START)+r'.*?'+re.escape(END),re.S)

E=html.escape
def read(path):return json.loads(path.read_text())
def dump(value):return json.dumps(value,ensure_ascii=False,indent=2)+'\n'
def sha(value):return hashlib.sha256(value.encode()).hexdigest()
def valid(x):return isinstance(x,str) and bool(x.strip()) and not re.search(r'<|\ufffd|\b(?:TODO|FIXME)\b',x)
def checked(x):
    assert valid(x),repr(x)[:95]
    return x

def source_signature(text):
    d=Document(text)
    return {key:sha(d.raw(one(d.root.walk(),lambda n:n.has(key),key))) for key in
            ('reading-head','reading-prose','reading-sources','reading-related','reading-next','reading-open')}

def import_release(directory,date):
    assert str(datetime.date.fromisoformat(date))==date
    items=load_readings()
    assert tuple(item['slug'] for item in items)==SLUGS
    source={lang:{slug:source_signature((TARGET/d/(slug+'.html')).read_text()) for slug in SLUGS}
            for lang,(d,_,_) in EDITIONS.items()}
    edits={}
    for lang in LANGS:
        base=directory/lang
        m=read(base/'meta.json')
        assert set(m)=={'title','description','note','labels','legacy_note','essays'},lang
        for key in ('title','description','note','legacy_note'):checked(m[key])
        assert set(m['labels'])=={'sources','related','all','previous','next','topic','original'},lang
        for label in m['labels'].values():checked(label)
        assert set(m['essays'])==set(SLUGS),lang
        prose={}
        for item in items:
            slug=item['slug']
            raw=(base/(slug+'.md')).read_text()
            title,*blocks=[' '.join(x.strip().splitlines()) for x in re.split(r'\n\s*\n',raw.strip())]
            assert title.startswith('# ') and valid(title[2:]),(lang,slug,title)
            p={'title':title[2:],'sections':[],'sha256':sha(raw)}
            for block in blocks:
                checked(block)
                if block.startswith('## '):
                    p['sections'].append({'heading':block[3:],'paragraphs':[]})
                else:
                    assert not block.startswith(('# ', '### ')) and p['sections'],(lang,slug)
                    p['sections'][-1]['paragraphs'].append(block)
            src=item['zh']['sections']
            assert [len(s['paragraphs']) for s in src]==[len(s['paragraphs']) for s in p['sections']],(lang,slug,'block alignment')
            row=m['essays'][slug]
            assert set(row)=={'deck','scope','source_note','spoiler','references','related','open'},(lang,slug)
            for key in ('deck','scope','source_note','spoiler','open'):checked(row[key])
            for key,expected in [('references',[f'https://self-as-an-end.net/papers/sae-hongloumeng-{n}.html' for n in item['papers']]),
                                 ('related',item['related'])]:
                links=row[key]
                for label,url in links:checked(label); checked(url)
                actual=[url if key=='references' else urlsplit(url).path.rsplit('/',1)[-1] for label,url in links]
                assert actual==expected,(lang,slug,key,actual,expected)
            prose[slug]=p
        edits[lang]={'metadata':m,'articles':prose}
    return {'date':date,'source':source,'editions':edits}

def primary_article(text,slug,lang,row=None):
    before=source_signature(text)
    if row:assert row['source'][lang][slug]==before,(lang,slug,'approved base changed')
    t=BLOCK.sub('',text)
    up='../' if EDITIONS[lang][0] else ''
    links=''.join(f'<a href="{up}{code}/{slug}.html?lang={code}" data-edition="{code}" lang="{code}">{E(label)}</a>' for code,label in LANGS.items())
    doc=Document(t)
    menu=one(doc.root.walk(),lambda n:n.has('language-menu'),slug)
    nav=one(menu.walk(),lambda n:n.tag=='nav',slug)
    t=t[:nav.close_start]+START+links+END+t[nav.close_start:]
    alts=''.join(f'<link rel="alternate" hreflang="{l}" href="{ORIGIN}{l}/{slug}.html">' for l in LANGS)
    # Distinct marker in <head> can share the safe whole-block reducer.
    t=t.replace('</head>',START+alts+END+'</head>',1)
    assert before==source_signature(t),slug
    return t

def primary_hub(text,lang):
    t=BLOCK.sub('',text)
    doc=Document(t)
    section=one(doc.root.walk(),lambda n:n.tag=='section' and n.attrs.get('id')=='readings',lang)
    note=one(section.walk(),lambda n:n.has('edition-note'),lang)
    up='../' if EDITIONS[lang][0] else ''
    links=''.join(f'<a href="{up}{code}/readings.html" lang="{code}">{E(label)}</a>' for code,label in LANGS.items())
    addition=START+'<div class="featured">'+links+'</div>'+END
    return t[:note.open_end]+E(OLD_SCOPE[lang])+t[note.close_start:note.end]+addition+t[note.end:]

def edition_links(lang,slug,meta):
    idx=slug is None
    links=[]
    for other,(directory,code,label) in ALL.items():
        if idx:
            if other in EDITIONS:
                href='../'+directory+'index.html?lang='+other+'#readings'
                token=''
            else:
                href='../'+directory+'readings.html'
                token=f' data-edition="{other}"'
        else:
            href='../'+directory+slug+'.html?lang='+other
            token=f' data-edition="{other}"'
        current=' aria-current="page"' if other==lang else ''
        links.append(f'<a href="{E(href)}"{token} lang="{code}"{current}>{E(label)}</a>')
    return ''.join(links)

def native_page(lang,release,slug=None):
    loc=release['editions'][lang];m=loc['metadata'];labels=m['labels']
    skip,reading_languages,library,search_word,continuation,contents,nav=EXTRAS[lang]
    root='../../../../'; home_url=root+f'essays/{lang}/index.html'
    first=root+f'classics/hongloumeng/{lang}/index.html'
    sequel=root+f'originals/hongloumeng/{lang}/index.html'
    if not slug:
        title=m['title'];deck=m['description'];file='readings.html'
        cards=''.join(f'<a class="reading-card" href="{s}.html"><span class="eyebrow">{i:02d}</span><h3>{E(loc["articles"][s]["title"])}</h3><p>{E(m["essays"][s]["deck"])}</p></a>' for i,s in enumerate(SLUGS,1))
        body=f'<section class="hero"><h1>{E(title)}</h1><p class="deck">{E(deck)}</p><p class="edition-note">{E(m["note"])}</p></section><div class="reading-grid">{cards}</div>'
        alts=''.join(f'<link rel="alternate" hreflang="{code}" href="{ORIGIN}{l}/readings.html">' for l,(_,code,_) in ALL.items() if l in LANGS)
        alts+=f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}index.html#readings">'
        schema={'@type':'CollectionPage','hasPart':[{'@type':'Article','url':ORIGIN+lang+'/'+s+'.html'} for s in SLUGS]}
    else:
        file=slug+'.html'
        article=loc['articles'][slug];meta=m['essays'][slug]
        title=article['title'];deck=meta['deck'];i=SLUGS.index(slug)
        sections=''.join(f'<section id="section-{n}"><h2>{inline_markdown(s["heading"])}</h2>'+''.join('<p>'+inline_markdown(p)+'</p>' for p in s['paragraphs'])+'</section>' for n,s in enumerate(article['sections'],1))
        references=''.join(f'<li><a href="{E(url)}">{E(label)}</a></li>' for label,url in meta['references'])
        related=''.join(f'<li><a href="../{E(urlsplit(url).path.rsplit("/",1)[-1])}?lang=en" data-legacy-language="en">{E(label)} · EN</a></li>' for label,url in meta['related'])
        steps=[]
        for other,direction in ((i-1,'previous'),(i+1,'next')):
            got=0<=other<len(SLUGS)
            target=SLUGS[other]+'.html' if got else 'readings.html'
            desc=loc['articles'][SLUGS[other]]['title'] if got else labels['all']
            steps.append(f'<a href="{target}"><small>{E(labels[direction] if got else labels["topic"])}</small><span>{E(desc)}</span></a>')
        body=f'''<nav class="reading-crumbs"><a href="readings.html">{E(labels['all'])}</a></nav>
<article><header class="reading-head"><p class="eyebrow">{E(m['title'])} · {i+1:02d}</p><h1>{E(title)}</h1><p class="deck">{E(deck)}</p><p class="reading-byline">Han Qin · <time datetime="{release['date']}">{release['date']}</time></p><p class="reading-scope">{E(meta['scope'])}</p></header>
<div class="reading-prose">{sections}</div>
<details class="reading-sources"><summary>{E(labels['sources'])}</summary><p>{E(meta['source_note'])}</p><aside class="spoiler"><p>{E(meta['spoiler'])}</p></aside><ul>{references}</ul></details>
<aside class="reading-related"><h2>{E(labels['related'])}</h2><ul>{related}</ul><p class="edition-note">{E(m['legacy_note'])}</p></aside>
<nav class="reading-next" aria-label="{E(labels['all'])}">{''.join(steps)}</nav><p class="reading-open">{E(meta['open'])}</p></article>'''
        alts=''.join(f'<link rel="alternate" hreflang="{code}" href="{ORIGIN}{d}{file}">' for d,code,_ in ALL.values())+f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}{file}">'
        schema={'@type':'Article','headline':title,'isPartOf':{'@type':'CollectionPage','name':m['title'],'url':ORIGIN+lang+'/readings.html'},'citation':[u for _,u in meta['references']]}
    canonical=ORIGIN+lang+'/'+file
    schema.update({'@context':'https://schema.org','name':title,'description':deck,'author':{'@type':'Person','name':'Han Qin (秦汉)'},'datePublished':release['date'],'dateModified':release['date'],'inLanguage':lang,'url':canonical})
    structured=json.dumps(schema,ensure_ascii=False).replace('<',chr(92)+'u003c')
    return f'''<!doctype html>
<html lang="{lang}" data-lang="{lang}" data-editions="{lang}" data-explicit-edition="true"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} — Non Dubito</title><meta name="description" content="{E(deck)}"><meta name="author" content="Han Qin"><link rel="canonical" href="{canonical}">{alts}<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(deck)}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="{'article' if slug else 'website'}"><meta name="twitter:card" content="summary"><link rel="icon" href="{root}favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../hongloumeng-hub.css?v=20261003"><script defer src="../hongloumeng-hub.js?v=20261003"></script><script type="application/ld+json">{structured}</script></head>
<body class="reading-page"><a class="skip" href="#main">{E(skip)}</a><header class="site-header"><a class="brand" href="{home_url}">Non <span>Dubito</span></a><nav aria-label="{E(nav)}"><a href="readings.html">{E(contents)}</a><a href="{root}library.html?lang=en">{E(library)}</a><a href="{root}search.html?lang=en&amp;ui={lang}&amp;in={lang}">{E(search_word)}</a></nav><details class="language-menu"><summary>{LANGS[lang]} <span aria-hidden="true">⌄</span></summary><nav aria-label="{E(reading_languages)}">{edition_links(lang,slug,meta if slug else m)}</nav></details></header><main id="main">{body}</main><footer><a href="{first}">{E(labels['original'])}</a> · <a href="{sequel}">{E(continuation)}</a><p>Non Dubito · Han Qin</p></footer><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script></body></html>
'''

def outputs(row):
    out={}
    for lang,(dir,code,label) in EDITIONS.items():
        for slug in SLUGS:
            p=TARGET/dir/(slug+'.html')
            out[p]=primary_article(p.read_text(),slug,lang,row)
        p=TARGET/dir/'index.html'
        out[p]=primary_hub(p.read_text(),lang)
    for lang in LANGS:
        p=TARGET/lang
        out[p/'readings.html']=native_page(lang,row)
        out.update({p/(slug+'.html'):native_page(lang,row,slug) for slug in SLUGS})
    return out

def verify_pages(row,pages):
    for path,text in pages.items():
        doc=Document(text)
        lang=path.parent.name
        if lang not in LANGS:continue
        nodes=list(doc.root.walk())
        scopes=[n for n in nodes if n.has('reading-sources')]
        if path.stem in SLUGS:
            assert len(scopes)==1 and 'open' not in scopes[0].attrs and any(n.has('spoiler') for n in scopes[0].walk()),path
            assert sum(n.tag=='a' and 'data-edition' in n.attrs for n in nodes)==8,path
            assert sum(n.tag=='link' and n.attrs.get('rel')=='alternate' for n in nodes)==9,path
            anchors=[n.attrs['id'] for n in nodes if n.tag=='section' and n.attrs.get('id','').startswith('section-')]
            n=len(row['editions'][lang]['articles'][path.stem]['sections'])
            assert anchors==[f'section-{i}' for i in range(1,n+1)],path
        else:
            assert path.stem=='readings'
            assert [n.attrs['href'] for n in nodes if n.has('reading-card')]==[s+'.html' for s in SLUGS],path
        for n in nodes:
            val=n.attrs.get('href' if n.tag in ('a','link') else 'src','')
            if not val:continue
            u=urlsplit(val)
            if u.scheme or u.netloc:continue
            target=(path.parent/u.path).resolve() if u.path else path
            assert target in pages or target.is_file(),(path,val)

def announce(row):
    ledger=ROOT/'data/site-updates.json';d=read(ledger)
    date=row['date']; key=f'{date}-hongloumeng-six-guides-eight-languages'
    entry={'id':key,'date':date,'kind':'expanded','domain':'stories','series_key':'essays/literature/hlm',
      'url':'essays/literature/hlm/index.html#readings','languages':list(ALL),
      'title':{'en':'Dream of the Red Chamber · Six Reader Guides in Eight Languages','zh':'《红楼梦》：六篇散文导读补齐八语','zh-hant':'《紅樓夢》：六篇散文導讀補齊八語'},
      'summary':{'en':'Six guides now include Japanese, French, German, Spanish and Korean. These guides are separate from the novel and academic papers.','zh':'六篇导读新增日、法、德、西、韩全文，与小说正文及研究论文分开。','zh-hant':'六篇導讀新增日、法、德、西、韓全文，與小說正文及研究論文分開。'}}
    # The ledger is indexed at a canonical, fragment-free page.
    entry['url']=entry['url'].split('#')[0]
    d['updates']=sorted([entry,*[u for u in d['updates'] if u['id']!=key]],key=lambda x:x['date'],reverse=True)
    p=ROOT/'latest.html';s=p.read_text();a='<!-- RED CHAMBER GUIDE LATEST START -->';z='<!-- RED CHAMBER GUIDE LATEST END -->'
    s=re.sub(re.escape(a)+r'.*?'+re.escape(z)+r'\\n?','',s,flags=re.S)
    hit=re.search(r'(?:<!--[^>]*-->\\s*)?<section class="updates-section">',s);assert hit
    modes=(('en','en'),('zh','zh'),('zh-hant','hant'))
    loc=lambda k,tag: ''.join(f'<{tag} class="lang-{css}">{E(entry[k][l])}</{tag}>' for l,css in modes)
    card=f'<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="{key}-date"><header class="updates-date"><h2 id="{key}-date"><time datetime="{date}">{date}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{key}"><div class="update-meta"><span class="update-kind"><span class="lang-en">Expanded</span><span class="lang-zh">拓展</span><span class="lang-hant">拓展</span></span><span>简 · 繁 · EN · JA · FR · DE · ES · KO</span></div>{loc("title","h3")}{loc("summary","p")}<a href="{entry["url"]}#readings"><span class="lang-en">See the reader guides →</span><span class="lang-zh">看散文导读 →</span><span class="lang-hant">看散文導讀 →</span></a></article></div></section></div></section>'
    i=hit.start()
    top=ROOT/'index.html';cfg=read(ROOT/'data/home-updates.json')
    return {ledger:dump(d),p:s[:i]+a+card+z+'\\n'+s[i:],top:home.replace_section(top.read_text(),home.render_section(d['updates'],cfg))}

def discovery(row,pages):
    paths=sorted(pages.keys()|{ROOT/'index.html',ROOT/'latest.html'})
    with patch.object(search,'collect_pages',lambda:paths):
        _,fresh=search.build()
    manifest=read(search.OUTPUT);added=set();out={}
    for lang,records in fresh.items():
        if not records:continue
        p=search.CHUNKS_DIR/f'{lang.lower()}.json';data=read(p)
        before={r['u'] for r in data['records']}
        replacements={r['u']:r for r in records}
        added.update(replacements.keys()-before)
        data['records']=[replacements.pop(r['u'],r) for r in data['records']]
        data['records'].extend(replacements.values())
        manifest['languages'][lang]['count']=len(data['records'])
        out[p]=search.serialized(data)
    manifest['record_count']+=len(added)
    out[search.OUTPUT]=search.serialized(manifest)
    p=ROOT/'sitemap.xml';ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';date=row['date']
    data={u.findtext(ns+'loc'):u.findtext(ns+'lastmod') for u in ET.parse(p).getroot()}
    for path in paths:
        url=parse_page(path).canonical
        assert url.startswith('https://nondubito.net/'),path
        data[url]=max(data.get(url,date),date)
    out[p]=sitemap_xml(list(data.items()))
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--import-dir',type=Path);p.add_argument('--date')
    g=p.add_mutually_exclusive_group()
    g.add_argument('--check-inputs',action='store_true');g.add_argument('--check',action='store_true')
    a=p.parse_args()
    if bool(a.import_dir)!=bool(a.date) or (a.check_inputs and not a.import_dir) or (a.check and a.import_dir):p.error('use --import-dir and --date together; --check verifies written files')
    row=import_release(a.import_dir,a.date) if a.import_dir else read(DATA)
    pages=outputs(row);verify_pages(row,pages)
    if a.check_inputs:
        print('30 drafts, 5 localized guide TOCs, and protected primary scope render successfully.')
        return
    def write(file,text):
        if a.check:assert file.read_text()==text,file
        elif not file.is_file() or file.read_text()!=text:
            file.parent.mkdir(parents=True,exist_ok=True);file.write_text(text)
    if a.import_dir:write(DATA,dump(row))
    for f,t in pages.items():write(f,t)
    for f,t in announce(row).items():write(f,t)
    for f,t in discovery(row,pages).items():write(f,t)
    print('56 scoped guide/project-index outputs, search, sitemap and announcements verified. Original article text unchanged.')

if __name__=='__main__':main()
