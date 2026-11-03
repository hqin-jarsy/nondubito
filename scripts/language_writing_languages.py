"""Render the five reviewed full-length Language & Writing editions.

No translation is generated here. Received text remains immutable; corrections
are explicit counted substitutions, and legacy three-language prose is separate.
"""
from pathlib import Path
import hashlib
import html
import json
import re
from web_analytics import tracked_html

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/language-writing'
TARGET=ROOT/'essays/language-writing'
DATE='2026-11-03'
LANGUAGES=('de','fr','es','ja','ko')
LABELS={'en':'English','zh':'简体中文','zh-hant':'繁體中文',
        'de':'Deutsch','fr':'Français','es':'Español','ja':'日本語','ko':'한국어'}
ORIGIN='https://nondubito.net/essays/language-writing/'
SLUGS=('index','ep01','ep02','ep03')
E=html.escape


def alternatives(slug):
    suffix='' if slug=='index' else slug+'.html'
    # Three legacy reading modes share one canonical. Do not invent indexable
    # English/Traditional query-string alternates.
    pairs=[('x-default',ORIGIN+suffix),('zh-Hans',ORIGIN+suffix)]
    pairs += [(lang,ORIGIN+lang+'/'+suffix) for lang in LANGUAGES]
    return ''.join(f'<link rel="alternate" hreflang="{lang}" href="{url}">' for lang,url in pairs)


def legacy_header(header,slug):
    links=''.join(f'<a href="{lang}/{slug}.html" lang="{lang}">{label}</a>' for lang,label in LABELS.items() if lang in LANGUAGES)
    # Header dropdown and mobile drawer keep their existing three mode buttons.
    for label in ('繁體中文','繁體'):
        marker=f'<button type="button" data-set-language="zh-hant">{label}</button>'
        assert header.count(marker)==1
        header=header.replace(marker,marker+links)
    return header


def load_language(lang):
    assert lang in LANGUAGES
    ui=json.loads((DATA/'languages.json').read_text())[lang]
    receipt=json.loads((DATA/'multilingual-publication.json').read_text())
    corrections=json.loads((DATA/'corrections.json').read_text())
    records=json.loads((DATA/'received/MANIFEST.json').read_text())['records']
    articles=[]
    for slug,count in (('ep01',39),('ep02',29),('ep03',30)):
        path=DATA/'received'/f'{slug}.{lang}.md'
        raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==receipt['received_files'][str(path.relative_to(DATA))]
        text=raw.decode()
        for fix in corrections:
            if fix['language']==lang and fix['episode']==slug:
                assert text.count(fix['before'])==fix['count'],fix
                text=text.replace(fix['before'],fix['after'])
        blocks=re.split(r'\n\s*\n',text.strip())
        note_at=max(i for i,b in enumerate(blocks) if b.startswith('## '))
        body=blocks[2:note_at]
        assert len(body)==count and sum(b.startswith('## ') for b in body)==3
        assert blocks[0].startswith('# ') and note_at+1<len(blocks)
        assert all('<' not in b and '�' not in b for b in body)
        record=next(r for r in records if r['episode']==slug and r['language']==lang)
        original=json.loads((DATA/(slug+'.json')).read_text())
        assert original['source_url'] in record['references']
        articles.append({'slug':slug,'number':int(slug[-2:]),'title':blocks[0][2:],
                         'deck':blocks[1],'body':body,'source_note':blocks[note_at+1],
                         'references':record['references'],'source_url':original['source_url']})
    return ui,articles


def language_links(slug,lang):
    links=[]
    for code,label in LABELS.items():
        href='../'+slug+'.html?lang='+code if code in ('en','zh','zh-hant') else '../'+code+'/'+slug+'.html'
        active=' aria-current="page"' if code==lang else ''
        links.append(f'<a href="{E(href)}" lang="{code if code!="zh" else "zh-Hans"}"{active}>{label}</a>')
    return ''.join(links)


def header(ui,slug,lang):
    links=language_links(slug,lang)
    nav=f'<a href="../../{lang}/index.html">{E(ui["home"])}</a><a href="index.html">{E(ui["contents"])}</a><a href="../../../library.html?lang=en">{E(ui["library"])}</a>'
    return f'''<header class="site-shell-header"><div class="header-inner"><a href="../../{lang}/index.html" class="site-title"><span class="title-latin">Non <span>Dubito</span></span></a><nav class="site-shell-nav">{nav}</nav><div class="site-shell-tools"><details class="site-shell-language"><summary class="site-shell-language-summary">{E(ui['label'])} <span aria-hidden="true">⌄</span></summary><div class="site-shell-language-options">{links}</div></details><button class="site-shell-menu-button" type="button" data-site-shell-menu aria-label="{E(ui['menu'])}" aria-controls="site-shell-drawer" aria-expanded="false"><span aria-hidden="true">☰</span></button></div></div></header><div class="site-shell-drawer" id="site-shell-drawer" data-site-shell-drawer><nav>{nav}<a href="../../../search.html?lang=en&amp;ui={lang}&amp;in={lang}">{E(ui['search'])}</a></nav></div>'''


def related(ui,lang):
    return f'<aside class="lw-related"><h2>{E(ui["related"])}</h2><a href="../../method/{lang}/index.html">{E(ui["method"])}</a><a href="../../sae/index.html?lang=en">{E(ui["map"])}</a></aside>'


@tracked_html
def document(ui,lang,slug,content,article=None,articles=None):
    title=article['title'] if article else ui['title']
    deck=article['deck'] if article else ui['deck']
    url=ORIGIN+lang+'/'+('' if slug=='index' else slug+'.html')
    schema={'@context':'https://schema.org','@type':'Article' if article else 'CollectionPage',
            'name':title,'description':deck,'inLanguage':lang,'url':url,
            'author':{'@type':'Person','name':'Han Qin (秦汉)'},'datePublished':DATE,'dateModified':DATE}
    if article:
        schema.update(headline=title,mainEntityOfPage=url,citation=article['source_url'],
                      isPartOf={'@type':'CollectionPage','name':ui['title'],'url':ORIGIN+lang+'/'},
                      translationOfWork={'@type':'Article','url':ORIGIN+slug+'.html'})
    else:
        schema['hasPart']=[{'@type':'Article','name':a['title'],'url':ORIGIN+lang+'/'+a['slug']+'.html'} for a in articles]
    structured=json.dumps(schema,ensure_ascii=False).replace('<',chr(92)+'u003c')
    return f'''<!DOCTYPE html>
<html lang="{lang}" data-lang="{lang}" data-editions="{lang}" data-foreign-edition="true"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} — Non Dubito</title><meta name="description" content="{E(deck)}"><meta name="author" content="Han Qin (秦汉)"><link rel="canonical" href="{url}">{alternatives(slug)}<meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(deck)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary"><link rel="icon" href="../../../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../../../style.css"><link rel="stylesheet" href="../../../site-shell.css?v=20260905b"><link rel="stylesheet" href="../reading.css?v=20261103"><script defer src="../reading.js?v=20261103"></script><script type="application/ld+json">{structured}</script></head><body class="site-shell-page lw-page lw-foreign"><a class="lw-skip" href="#main">{E(ui['read'])}</a>{header(ui,slug,lang)}<main id="main" class="lw-wrap">{content}</main><footer class="site-shell-footer"><div class="site-shell-footer-inner"><div class="site-shell-footer-mark">Non <span>Dubito</span></div><div class="site-shell-footer-links"><a href="../../{lang}/index.html">{E(ui['home'])}</a><a href="https://self-as-an-end.net/">{E(ui['theory'])} ↗</a></div></div></footer></body></html>
'''


def render_foreign():
    pages={}
    for lang in LANGUAGES:
        ui,articles=load_language(lang)
        cards=''.join(f'<a class="lw-card" href="{a["slug"]}.html"><p class="lw-kicker">{a["number"]:02}</p><h2>{E(a["title"])}</h2><p>{E(a["deck"])}</p><span class="lw-read">{E(ui["read"])} →</span></a>' for a in articles)
        index=f'<section class="lw-hero"><p class="lw-kicker">Non Dubito · {E(ui["series"])}</p><h1>{E(ui["title"])}</h1><p class="lw-deck">{E(ui["deck"])}</p><p class="lw-meta">{E(ui["count"])}</p></section><aside class="lw-opening"><p>{E(ui["intro"])}</p><a href="ep01.html">{E(ui["start"])} →</a></aside><section class="lw-grid">{cards}</section><section class="lw-note"><p>{E(ui["scope"])}</p></section>'+related(ui,lang)
        pages[TARGET/lang/'index.html']=document(ui,lang,'index',index,articles=articles)
        for i,a in enumerate(articles):
            prose='\n'.join('<h2>'+E(p[3:])+'</h2>' if p.startswith('## ') else '<p>'+E(p)+'</p>' for p in a['body'])
            notes='<p>'+E(a['source_note'])+'</p>'
            for ref in a['references']:
                label=ui['paper'] if ref==a['source_url'] else 'Attention Is All You Need · §3.4' if 'arxiv.org' in ref else 'Priberam · saudade' if 'priberam' in ref else 'Stanford Encyclopedia · Japanese Aesthetics'
                notes+=f'<p><a href="{E(ref)}">{E(label)} ↗</a></p>'
            nav=[]
            for offset,kind in ((-1,'previous'),(1,'next')):
                neighbor=i+offset
                other=articles[neighbor] if 0<=neighbor<len(articles) else None
                nav.append(f'<a href="{other["slug"]+".html" if other else "index.html"}"><small>{E(ui[kind] if other else ui["contents"])}</small>{E(other["title"] if other else ui["title"])}</a>')
            content=f'<nav class="lw-crumb"><a href="index.html">← {E(ui["series"])}</a></nav><article class="lw-article"><div class="lw-head"><p class="lw-kicker">{E(ui["series"])} · {a["number"]:02}</p><h1>{E(a["title"])}</h1><p class="lw-deck">{E(a["deck"])}</p><p class="lw-meta">Han Qin · <time datetime="{DATE}">{DATE}</time></p></div><div class="essay-body lw-prose" lang="{lang}">{prose}</div><details class="lw-sources"><summary>{E(ui["sources"])}</summary>{notes}</details><nav class="lw-series-nav">'+''.join(nav)+'</nav>'+related(ui,lang)+'</article>'
            pages[TARGET/lang/(a['slug']+'.html')]=document(ui,lang,a['slug'],content,article=a)
    return pages
