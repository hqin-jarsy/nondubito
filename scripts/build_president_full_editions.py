#!/usr/bin/env python3
"""Publish frozen, fully reviewed president batches; never read external ZIPs.

Chinese/English remain the original essays plus explicit local copyedits.
--freeze records final manuscript hashes after independent language review.
--check is read-only; a normal rebuild uses checked-in sources only.
"""
import argparse
from datetime import date
import html
import json
import re
from pathlib import Path

from import_president_full_editions import ROOT, DATA, LANGS, sha, body_fragment
from test_daodejing_sources import Page
from build_worldcup_full_editions import render
from build_emperor_traditional import TraditionalConverter, TextCollector, reading_script

SERIES = ROOT / 'essays/president'
LABELS = {'en':'English','zh':'简体中文','zh-hant':'繁體中文','ja':'日本語','fr':'Français','de':'Deutsch','es':'Español','ko':'한국어'}
TOC = dict(de='In diesem Essay',fr='Dans cet essai',es='En este ensayo',ja='この篇の目次',ko='이 글의 목차')
STYLE = '''<style id="president-full-style">
.essay-main{box-sizing:border-box;width:100%;min-width:0;max-width:820px;margin:0 auto;padding:96px 28px 70px;overflow-wrap:anywhere}
.essay-main .essay-body{max-width:none;margin:0;padding:0}
.essay-main .essay-header{position:static;display:block;height:auto;background:none;border:0;padding:0;margin:0 0 2rem;backdrop-filter:none;text-align:left;color:var(--ink)}
.essay-main .essay-header h1{font-size:clamp(1.8rem,4vw,2.7rem);line-height:1.4;color:var(--ink);overflow-wrap:anywhere;text-wrap:balance}
.essay-main .essay-meta{color:var(--ink-muted)}
.essay-main .lang-toggle{margin-bottom:1.5rem}
.essay-main .lang-toggle.lang-select-menu{display:inline-flex;width:fit-content;max-width:100%;margin:0 0 1.5rem;background:transparent}
.essay-main .lang-select{color:var(--ink-light);background:white;border-color:var(--cream-border)}
.essay-main .lang-select-chevron{color:var(--ink-muted)}
.essay-main .lang-btn{color:var(--ink-muted)}
.essay-main .lang-btn.active{color:var(--green);background:var(--cream-dark)}
.essay-main .essay-titles{max-width:none;margin:0}
.president-full h2{line-height:1.55;scroll-margin-top:100px}
.president-full p{overflow-wrap:break-word}
html[lang="ko"] .president-full p{word-break:keep-all;overflow-wrap:break-word}
.president-toc{margin:1.5rem 0 2rem;padding:1rem 1.25rem;border:1px solid var(--cream-border)}
.president-toc summary{cursor:pointer;font-family:var(--sans);color:var(--ink-muted)}
.president-toc ul{padding-left:1.3rem}.president-toc li{margin:.5rem 0;line-height:1.6}
.president-toc a{color:var(--ink-light)}
.entry-title,.entry-desc,.series-nav a{overflow-wrap:anywhere}
[data-lang="zh-hant"] .lang-en{display:none}
@media(max-width:600px){.essay-main{padding:88px 22px 50px}}
</style>'''


def replace_node(source, predicate, inner):
    nodes = [n for n in Page(source).nodes if predicate(n)]
    assert len(nodes)==1, ('ambiguous node',len(nodes))
    node=nodes[0]; offsets=[0]
    for line in source.splitlines(keepends=True): offsets.append(offsets[-1]+len(line))
    start=offsets[node.start[0]-1]+node.start[1]
    end=offsets[node.end[0]-1]+node.end[1]
    start=source.index('>',start)+1
    return source[:start]+inner+source[end:]


def source_copies(batch):
    receipt=json.loads((DATA/f'{batch}-received.json').read_text())
    plan=json.loads((DATA/f'{batch}-source-copyedits.json').read_text())
    copies={}
    for key,record in receipt['originals'].items():
        text=json.loads((DATA/f'{key}.json').read_text())
        assert sha(text)==record['sha256'], (key,'original snapshot changed')
        for before,after in plan['edits'].get(key,[]):
            assert text.count(before)==1,(key,before)
            text=text.replace(before,after,1)
        copies[key]=text
    return copies


def freeze(batch):
    target=DATA/f'{batch}-review.json'
    assert not target.exists(), 'Frozen review exists; never silently reapprove changed manuscripts'
    reviews=[DATA/f'{batch}-{langs}-review.json' for langs in ('de-fr','ja-ko','es')]
    assert all(p.exists() for p in reviews),'All three completed language reviews required'
    received=json.loads((DATA/f'{batch}-received.json').read_text())
    result=dict(batch=batch,episodes=received['episodes'],received_sha256=sha((DATA/f'{batch}-received.json').read_bytes()),
                copyedits_sha256=sha((DATA/f'{batch}-source-copyedits.json').read_bytes()),
                language_reviews={p.name:sha(p.read_bytes()) for p in reviews},manuscripts={},source_bodies={})
    for key,r in received['manuscripts'].items():
        text=(DATA/f'{key}.md').read_text()
        headings=re.findall(r'^## (.+)$',text,re.M)
        assert len(headings)==r['sections'],key
        result['manuscripts'][key]=dict(sha256=sha(text),title=text.splitlines()[0][2:],sections=len(headings),paragraphs=render(text.split('\n',1)[1]).count('<p>'))
    result['source_bodies']={key:sha(text) for key,text in source_copies(batch).items()}
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')


def toggle(ep, lang=None):
    choices=[]
    for code,label in LABELS.items():
        if code in ('en','zh','zh-hant') and lang is None:
            choices.append(f'<button class="lang-btn" data-lang="{code}">{label}</button>')
        elif code==lang:
            choices.append(f'<span class="lang-btn active" aria-current="page">{label}</span>')
        else:
            if code in ('en','zh','zh-hant'):
                href=f'../{ep}.html?lang={code}'
                extra=f' onclick="localStorage.setItem(\'nd_lang\',\'{code}\')"'
            else:
                href=f'{"../" if lang else ""}{code}/{ep}.html'; extra=''
            choices.append(f'<a class="lang-btn edition-link" href="{href}"{extra}>{label}</a>')
    return '\n'+'\n<span class="lang-sep">|</span>\n'.join(choices)+'\n'


def style(source, depth):
    source=re.sub(r'<style id="president-full-style">.*?</style>\s*','',source,flags=re.S)
    script=f'<script defer src="{depth}language-select.js"></script>'
    source=re.sub(re.escape(script)+r'\s*','',source)
    source=source.replace('</head>',STYLE+'\n'+script+'\n</head>',1)
    return source


def outputs(batch):
    receipt=json.loads((DATA/f'{batch}-review.json').read_text())
    assert sha((DATA/f'{batch}-received.json').read_bytes())==receipt['received_sha256']
    assert sha((DATA/f'{batch}-source-copyedits.json').read_bytes())==receipt['copyedits_sha256']
    for file,digest in receipt['language_reviews'].items(): assert sha((DATA/file).read_bytes())==digest,file
    out={}; source=source_copies(batch); titles={}
    for key,r in receipt['manuscripts'].items():
        text=(DATA/f'{key}.md').read_text(); assert sha(text)==r['sha256'],key
        ep,lang=key.split('.'); titles[key]=r['title']; path=SERIES/lang/f'{ep}.html'
        page=path.read_text(); headings=re.findall(r'^## (.+)$',text,re.M)
        body=render(text.split('\n',1)[1].strip()); count=iter(range(1,len(headings)+1))
        body=re.sub('<h2>',lambda _:f'<h2 id="section-{next(count)}">',body)
        toc=f'<details class="president-toc"><summary>{TOC[lang]}</summary><ul>'
        toc+=''.join(f'<li><a href="#section-{i}">{html.escape(h)}</a></li>' for i,h in enumerate(headings,1))+'</ul></details>'
        page=replace_node(page,lambda n:n.has_class('essay-body'),toc+'\n<div class="president-full">\n'+body+'\n</div>')
        page=replace_node(page,lambda n:n.tag=='h1',html.escape(r['title']))
        page=re.sub(r'<p class="essay-subtitle"[^>]*>.*?</p>','',page,flags=re.S)
        page=re.sub(r'<title>.*?</title>',lambda _:'<title>'+html.escape(r['title'])+' — Non Dubito</title>',page,count=1,flags=re.S)
        page=re.sub(r'(<meta property="og:title" content=")[^"]*(")',lambda m:m[1]+html.escape(r['title']+' — Non Dubito',quote=True)+m[2],page)
        page=replace_node(page,lambda n:n.has_class('lang-toggle'),toggle(ep,lang))
        out[path]=style(page,'../../../')
    converter=TraditionalConverter()
    try:
        for number in receipt['episodes']:
            ep=f'ep{number:02}';path=SERIES/f'{ep}.html';page=path.read_text()
            for lang in ('zh','en'):
                body=source[f'{ep}.{lang}'];assert sha(body)==receipt['source_bodies'][f'{ep}.{lang}']
                page=replace_node(page,lambda n:n.has_class('essay-body') and n.has_class('lang-'+lang),body)
            new="var saved = new URLSearchParams(location.search).get('lang') || localStorage.getItem('nd_lang') || 'zh';\n      if (!['zh','zh-hant','en'].includes(saved)) saved = 'zh';\n      localStorage.setItem('nd_lang', saved);\n      document.documentElement.setAttribute('data-lang', saved);"
            page,n=re.subn(r"var saved = .*?document.documentElement.setAttribute\('data-lang', saved\);",lambda _:new,page,count=1,flags=re.S)
            assert n==1,path
            page=replace_node(page,lambda n:n.has_class('lang-toggle'),toggle(ep))
            page=style(page,'../../')
            tag=f'<script defer src="zh-hant-data/{ep}.js"></script>'
            if tag not in page:page=page.replace('</body>',tag+'\n</body>')
            # Older, not-yet-upgraded series pages have only ZH/EN. Explicit
            # fallback prevents their old scripts displaying both bodies.
            def fallback(match):
                node=match[0]
                if 'data-president-fallback' in node:return node
                return node[:-1]+''' data-president-fallback="true" onclick="if(document.documentElement.dataset.lang==='zh-hant')localStorage.setItem('nd_lang','zh')">'''
            page=re.sub(r'<a\b[^>]*href="(?:index|ep06)\.html"[^>]*>',fallback,page)
            collector=TextCollector();collector.feed(page)
            variants={s:converter.convert(s) for s in collector.text}
            variants={s:t for s,t in variants.items() if s!=t}
            out[SERIES/'zh-hant-data'/f'{ep}.js']=reading_script(variants,path)
            out[path]=page
    finally:converter.close()
    for lang in LANGS:
        path=SERIES/lang/'index.html';page=path.read_text()
        def entry(match):
            block=match[0]; found=re.search(r'href="(ep\d{2})\.html"',block)
            if not found or found[1]+'.'+lang not in titles:return block
            title=titles[found[1]+'.'+lang]
            block=re.sub(r'(<div\b[^>]*class="(?:entry-title|card-title-en)"[^>]*>).*?(</div>)',lambda m:m[1]+html.escape(title)+m[2],block,flags=re.S)
            return re.sub(r'<div class="entry-subtitle">.*?</div>','',block,flags=re.S)
        page=re.sub(r'<a\b[^>]*>.*?</a>',entry,page,flags=re.S)
        # Ensure the shared select sees all seven existing index choices.
        page=page.replace('class="edition-link"','class="lang-btn edition-link"')
        script='<script defer src="../../../language-select.js"></script>'
        if script not in page:page=page.replace('</head>',script+'\n</head>',1)
        out[path]=page
    return out


def refresh(changed):
    import build_search_index as search
    _,chunks=search.build();scope={p.relative_to(ROOT).as_posix() for p in changed if p.suffix=='.html'}
    for lang in search.SEARCH_LANGUAGES:
        path=ROOT/f'data/search/{lang.lower()}.json';current=json.loads(path.read_text())
        fresh={r['u']:r for r in chunks[lang] if r['u'] in scope}
        if not fresh:continue
        current['records']=[fresh.pop(r['u'],r) for r in current['records']]
        current['records'].extend(fresh.values())
        # Preserve chunk metadata; only adjust count if the chunk uses it.
        if 'count' in current:current['count']=len(current['records'])
        path.write_text(search.serialized(current))
    manifest_path=ROOT/'data/search-index.json';manifest=json.loads(manifest_path.read_text())
    for lang in search.SEARCH_LANGUAGES:
        manifest['languages'][lang]['count']=len(json.loads((ROOT/f'data/search/{lang.lower()}.json').read_text())['records'])
    manifest_path.write_text(search.serialized(manifest))
    path=ROOT/'sitemap.xml';text=path.read_text()
    for rel in scope:
        url=rel.removesuffix('index.html') if rel.endswith('/index.html') else rel
        pattern=r'(<loc>https://nondubito.net/'+re.escape(url)+r'</loc>\s*<lastmod>)[^<]*(</lastmod>)'
        text,n=re.subn(pattern,lambda m:m[1]+date.today().isoformat()+m[2],text)
        assert n==1,rel
    path.write_text(text)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch',default='batch01');parser.add_argument('--freeze',action='store_true')
    parser.add_argument('--check',action='store_true');parser.add_argument('--refresh-indexes',action='store_true')
    args=parser.parse_args()
    assert not(args.check and (args.freeze or args.refresh_indexes))
    if args.freeze:freeze(args.batch)
    expected=outputs(args.batch);stale=[p for p,t in expected.items() if not p.exists() or p.read_text()!=t]
    if args.check:
        assert not stale, [str(p.relative_to(ROOT)) for p in stale]
        print(f'OK: {len(expected)} reproducible batch outputs');return
    for path in stale:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(expected[path])
    if args.refresh_indexes:refresh(expected)
    print(f'Published {len(stale)} updated files from frozen {args.batch}')


if __name__=='__main__':main()
