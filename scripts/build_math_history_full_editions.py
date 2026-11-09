#!/usr/bin/env python3
"""Guarded full mathematics editions. Editorial acceptance is never inferred."""
from __future__ import annotations
import argparse, hashlib, html, json, re
from pathlib import Path
import markdown
from web_analytics import tracked_html
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/math-history-full'
SERIES=ROOT/'essays/math-history'
LANGS=('de','fr','es','ja','ko')
ALL=('en','zh','zh-hant',*LANGS)
LABELS=('EN','简体','繁體','Deutsch','Français','Español','日本語','한국어')
DATE='2026-11-09'
def read(p):return json.loads(p.read_text())
def digest(s):return hashlib.sha256(s if isinstance(s,bytes) else s.encode()).hexdigest()
def esc(s):return html.escape(str(s),quote=True)
def required_inputs():
    paths=[DATA/'source-manifest.json',ROOT/'data/math-history/traditional-cache.json']
    paths += [DATA/lang/f'ep{i:02d}.md' for lang in LANGS for i in range(1,26)]
    paths += [DATA/lang/'ui.json' for lang in LANGS]
    paths += [DATA/'source'/f'ep{i:02d}.json' for i in range(1,26)]
    paths += sorted((ROOT/'data/math-history').glob('*.json'))
    paths += sorted((DATA/'review').glob('approved-*'))
    return list(dict.fromkeys(paths))

def acceptance():
    receipt=DATA/'review/accepted.json'
    assert receipt.exists(),'Missing editorial acceptance receipt'
    r=read(receipt);assert r.get('status')=='accepted','Editorial acceptance is pending'
    required={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in required_inputs()}
    assert set(required)<=set(r.get('files',{})),'Incomplete editorial acceptance receipt (keys must be repository-relative)'
    for name,sha in r['files'].items():
        p=ROOT/name;assert p.resolve().is_relative_to(ROOT.resolve())
        assert digest(p.read_bytes())==sha,('Reviewed input drift',name)
    m=read(DATA/'source-manifest.json')
    approved=read(DATA/'review/approved-primary.json') if (DATA/'review/approved-primary.json').exists() else {}
    for name,sha in m['primary_inputs'].items():
        current=digest((ROOT/name).read_bytes())
        if current!=sha:
            change=approved.get(name,{})
            assert change.get('before_hash')==sha and change.get('after_hash')==current,('Unapproved primary input change',name)
    for archive in m['archives']:
        for entry in archive['members'].values():assert digest((DATA/entry['path']).read_bytes())==entry['sha256']
    for name,sha in m['snapshots'].items():assert digest((DATA/'received/website'/(name+'.txt')).read_bytes())==sha
    for entry in m['entries']:assert digest((DATA/'source'/f'ep{entry["id"]:02d}.json').read_bytes())==entry['source_sha256']
    return r

def manuscript(lang,i):
    raw=(DATA/lang/f'ep{i:02d}.md').read_text()
    assert not re.search(r'<\s*(?:script|iframe|style)\b',raw,re.I)
    pre,body=raw.split('\n## ',1);parts=re.split(r'\n\s*\n',pre.strip())
    authors=[n for n,p in enumerate(parts) if re.search(r'Han Qin|秦汉|秦漢',p)]
    assert len(authors)==1,(lang,i,'author')
    title=parts[0].removeprefix('# ').strip();deck=parts[3] if authors[0]==1 else parts[authors[0]-1]
    # Old redundant manuscript navigation is replaced by one local-language nav.
    body='## '+body
    body=re.sub(r'<a id="section-\d+"></a>','',body)
    body=re.sub(r'^\[[^\n]+\]\(https://nondubito.net/essays/math-history/(?:index|ep\d+)\.html\)\s*$', '',body,flags=re.M)
    headings=re.findall(r'^## (.+)$',body,re.M);assert len(headings)==9,(lang,i,len(headings))
    rendered=markdown.markdown(body)
    ids=iter(range(1,10));rendered=re.sub('<h2>',lambda _:f'<h2 id="section-{next(ids)}">',rendered)
    return dict(title=title,deck=deck,body=rendered,headings=headings)

def route(lang,name):return ('../' if lang in ('en','zh','zh-hant') else '../'+lang+'/')+name+(('?lang='+lang) if lang in ('en','zh','zh-hant') else '')
def language_nav(name,current,primary=False):
    links=[]
    for lang,label in zip(ALL,LABELS):
        url=(name+'?lang='+lang if lang in ALL[:3] else lang+'/'+name) if primary else route(lang,name)
        links.append(f'<a href="{url}" hreflang="{lang}" data-math-language="{lang}"'+(' aria-current="page"' if lang==current else '')+f'>{label}</a>')
    return '<nav class="math-languages" aria-label="Languages">'+''.join(links)+'</nav>'

def alternatives(name,primary=False):
    base='https://nondubito.net/essays/math-history/'
    return ''.join(f'<link rel="alternate" hreflang="{lang}" href="{base}{name+"?lang="+lang if lang in ALL[:3] else lang+"/"+name}">' for lang in ALL)

@tracked_html
def foreign_page(lang,name,d,ui,content):
    url='https://nondubito.net/essays/math-history/'+lang+('/' if name=='index.html' else '/'+name)
    schema={'@context':'https://schema.org','@type':'CollectionPage' if name=='index.html' else 'Article','name':d['title'],'headline':d['title'],'description':d['deck'],'inLanguage':lang,'url':url,'author':{'@type':'Person','name':'Han Qin'},'datePublished':DATE,'dateModified':DATE}
    schema_json=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    s=f'''<!DOCTYPE html><html lang="{lang}" data-lang="{lang}" data-editions="{lang}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(d['title'])} — Non Dubito</title><meta name="description" content="{esc(d['deck'])}"><meta property="og:title" content="{esc(d['title'])}"><meta property="og:description" content="{esc(d['deck'])}"><meta property="og:url" content="{url}"><meta property="og:type" content="{'website' if name=='index.html' else 'article'}"><meta name="twitter:card" content="summary"><link rel="canonical" href="{url}">{alternatives(name)}<link rel="icon" href="../../../favicon.svg"><link rel="stylesheet" href="../../../style.css"><link rel="stylesheet" href="../math-history.css"><link rel="stylesheet" href="../math-full.css"><script defer src="../math-full.js"></script><script type="application/ld+json">{schema_json}</script></head><body class="math-history-page math-foreign"><header class="math-full-header"><a href="../../../index.html">NON DUBITO</a>{language_nav(name,lang)}</header><main id="main-content" class="math-wrap">{content}</main></body></html>'''
    return s

def protect(p,s):
    if not p.exists():return
    name=str(p.relative_to(SERIES));m=read(DATA/'source-manifest.json')
    previous=read(DATA/'last-build.json') if (DATA/'last-build.json').exists() else {}
    assert digest(p.read_bytes()) in {digest(s),m['snapshots'].get(name),previous.get(name)},('Unknown manual change; preserve before rebuilding',p)

def render(primary=None,guard=True):
    acceptance()
    if primary is None:
        import build_math_history as base
        primary=base.outputs(full=False)
    assert set(primary)=={SERIES/"index.html"}|{SERIES/f"ep{i:02d}.html" for i in range(1,26)}, "Full release requires all 26 primary pages"
    result={}
    for p,s in primary.items():
        nav=language_nav(p.name,'en',True)
        s=s.replace('../../site-shell.js?v=20260905b','math-site-shell.js')
        s=re.sub(r'"dateModified": "[0-9-]+"', '"dateModified": "'+DATE+'"', s)
        s=s.replace('<main id="main-content"',nav+'<main id="main-content"',1)
        s=s.replace('</head>',alternatives(p.name,True)+'<link rel="stylesheet" href="math-full.css"><script defer src="math-full.js"></script></head>')
        s=s.replace('25 complete essays · English and both Chinese scripts','25 complete essays · Eight languages').replace('全25篇 · 简体中文、繁体中文与英文完整版','全25篇 · 八语完整版').replace('全25篇 · 簡體中文、繁體中文與英文完整版','全25篇 · 八語完整版')
        result[p]=s
    import build_math_history as base
    for lang in LANGS:
        ui=read(DATA/lang/'ui.json');assert len(ui['groups'])==5
        entries={i:manuscript(lang,i) for i in range(1,26)}
        groups=[]
        for n,(slug,_,__,ids) in enumerate(base.GROUPS):
            cards=''.join(f'<a class="math-card" href="ep{i:02d}.html"><span class="math-number">{i:02d}</span><div><h3>{esc(entries[i]["title"])}</h3><p>{esc(entries[i]["deck"])}</p><span class="math-read">{esc(ui["read"])}</span></div></a>' for i in ids)
            groups.append(f'<section class="math-group" id="{slug}"><h2>{esc(ui["groups"][n])}</h2><div class="math-grid">{cards}</div></section>')
        content=f'<section class="math-hero"><p class="math-kicker">{esc(ui["cycle"])}</p><h1>{esc(ui["series_title"])}</h1><p class="math-deck math-search-deck">{esc(ui["deck"])}</p><p class="math-meta">{esc(ui["status"])}</p><p class="math-promise">{esc(ui["promise"])}</p></section>'+''.join(groups)+f'<aside class="math-afterword">{esc(ui["afterword"])}</aside>'
        result[SERIES/lang/'index.html']=foreign_page(lang,'index.html',{'title':ui['series_title'],'deck':ui['deck']},ui,content)
        for i,d in entries.items():
            links=[]
            for j,key in [(i-1,'previous'),(i+1,'next')]:
                links.append(f'<a href="ep{j:02d}.html"><small>{esc(ui[key])}</small>{esc(entries[j]["title"])}</a>' if j in entries else f'<a href="index.html">{esc(ui["contents"])}</a>')
            toc=''.join(f'<li><a href="#section-{j}">{esc(h)}</a></li>' for j,h in enumerate(d['headings'],1))
            content=f'<article class="math-article"><nav class="math-breadcrumbs" aria-label="{esc(ui["contents"])}"><a href="index.html">{esc(ui["series_title"])}</a></nav><section class="math-head"><p class="math-kicker">{esc(ui["subject"])} · {i:02d} / 25</p><h1>{esc(d["title"])}</h1><p class="math-deck math-search-deck">{esc(d["deck"])}</p><p class="math-meta">{esc(ui["edition"])}</p></section><details class="math-toc"><summary>{esc(ui["toc"])}</summary><ol>{toc}</ol></details><div class="math-prose" lang="{lang}">{d["body"]}</div><nav class="math-series-nav" aria-label="{esc(ui["contents"])}">'+''.join(links)+'</nav></article>'
            result[SERIES/lang/f'ep{i:02d}.html']=foreign_page(lang,f'ep{i:02d}.html',d,ui,content)
    assert len(result)==156, "Full release requires 156 pages / 208 language views"
    if guard:
        for p,s in result.items():protect(p,s)
    return result

def upgrade_outputs(outputs):
    receipt=DATA/'review/accepted.json'
    if receipt.exists() and read(receipt).get('status')=='accepted':return render(outputs)
    assert not (DATA/'last-build.json').exists() and not any((SERIES/l/'index.html').exists() for l in LANGS),'Cannot regress released editions while editorial acceptance is pending'
    for p,s in outputs.items():
        protect(p,s)
        assert p.exists() and p.read_text()==s, ("Editorial acceptance pending: primary changes cannot be published",p)
    return outputs

def record(outputs):
    (DATA/'last-build.json').write_text(json.dumps({str(p.relative_to(SERIES)):digest(s) for p,s in outputs.items()},indent=2)+'\n')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();outputs=render()
    for p,s in outputs.items():
        if args.check:assert p.exists() and p.read_text()==s,('Stale full mathematics edition',p)
        else:p.parent.mkdir(exist_ok=True,parents=True);p.write_text(s)
    if not args.check:record(outputs)
    print(('Verified' if args.check else 'Built')+' 156 pages / 208 language views')
if __name__=='__main__':main()
