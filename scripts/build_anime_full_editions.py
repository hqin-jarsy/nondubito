#!/usr/bin/env python3
"""Full anime editions, rendered into the existing series design and URLs."""
import argparse
import html
import json
import re
from urllib.parse import urlsplit
import markdown
from import_anime_full_editions import ROOT, DATA, LANGS

DATE = '2026-10-08'
EDITION_LABELS={'de':'Über diese Ausgabe','fr':'À propos de cette édition','es':'Sobre esta edición','ja':'この版について','ko':'이 판본에 관하여'}
RECEIPT = json.loads((DATA/'batch01-received.json').read_text())
SERIES = RECEIPT['series']
E = lambda s: html.escape(s, quote=True)

def plain(s):
    return html.unescape(re.sub('<[^>]+>', '', markdown.markdown(s))).strip()

def source(series, lang, ep):
    return DATA/'reviewed'/series['slug']/lang/f'EP{ep:02}.md'

def copy(series, lang, ep):
    text = source(series,lang,ep).read_text()
    m = re.search(r'(?m)^# (.+)$',text)
    assert m
    title = plain(m[1])
    paragraphs = re.split(r'\n\s*\n',text[m.end():].strip())
    kept=[]
    for p in paragraphs:
        # Remove bylines and pure navigation only. Edition notes, plot scope,
        # quoted speech, qualifications and source notes remain in full.
        if 'Han Qin' in p and len(p)<350: continue
        if re.fullmatch(r'(?:\[[^\]]*\]\([^)]*\)\s*(?:[·|]\s*)?)+',p): continue
        if series['slug']=='kimetsu' and p.startswith(('Demon Slayer ·','『鬼滅の刃』を読む','《귀멸의 칼날》 읽기')): continue
        kept.append(p)
    def link(m):
        label,url=m[1],m[2]
        if urlsplit(url).scheme: return m[0]
        name=url.split('/')[-1]
        n=re.match(r'(?:EP)?0?(\d+)(?:_|\.md)',name,re.I)
        if n: return f'[{label}]({series["chapters"][int(n[1])-1]}.html)'
        if name.lower() in ('readme.md','index.md'): return f'[{label}](index.html)'
        raise AssertionError((series['slug'],lang,ep,url))
    md='\n\n'.join(kept)
    md=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,md)
    body=markdown.markdown(md)
    note=r'(<p><strong>(?:Zur Ausgabe|Zur Textgrundlage|Note[^<]*|Nota[^<]*|原文の版について|この[^<]*版について|판본 안내|원문 판본 안내)[^<]*</strong>.*?</p>)'
    body=re.sub(note,lambda m:'<details class="edition-note"><summary>'+EDITION_LABELS[lang]+'</summary>'+m[1]+'</details>',body,flags=re.S)
    # Use prose, not a delivery/edition note, for the search-result excerpt.
    candidates=[plain(p) for p in kept if not p.startswith(('*','#','[','原文：','中国語原文','중국어')) and len(plain(p))>55]
    desc=(candidates[0] if candidates else title)[:230]
    return {'title':title,'body':body,'description':desc,'markdown':md}

def metadata(s, series, lang, filename, title, desc):
    s=re.sub(r'<title>.*?</title>',lambda m:f'<title>{E(title)} — Non Dubito</title>',s,count=1,flags=re.S)
    for key,value in [('name="description"',desc),('property="og:title"',title+' — Non Dubito'),('property="og:description"',desc)]:
        s=re.sub(r'<meta '+key+r' content="[^"]*">',lambda m:f'<meta {key} content="{E(value)}">',s,count=1)
    s=re.sub(r'<link rel="alternate"[^>]*>','',s)
    s=re.sub(r'<script type="application/ld\+json">.*?</script>','',s,flags=re.S)
    base='https://nondubito.net/'+series['route']+'/'
    suffix='' if filename=='index.html' else filename
    links=''.join(f'<link rel="alternate" hreflang="{l}" href="{base+l+"/"+suffix}">' for l in LANGS)
    links+=f'<link rel="alternate" hreflang="x-default" href="{base+suffix}">'
    schema={'@context':'https://schema.org','@type':'Article' if suffix else 'CollectionPage','name':title,'headline':title,'description':desc,'url':base+lang+'/'+suffix,'inLanguage':lang,'author':{'@type':'Person','name':'Han Qin (秦汉)'},'dateModified':DATE}
    if suffix: schema['isPartOf']={'@type':'CollectionPage','url':base+lang+'/'}
    else: schema['hasPart']=[{'@type':'Article','url':base+lang+'/'+n+'.html'} for n in series['chapters']]
    extra=links+'<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script>'
    if 'language-select.js' not in s: extra+='<script defer src="../../../../language-select.js"></script>'
    extra+='<style>.culture-page .essay-header{max-width:900px;margin:0 auto;padding:110px 2rem 0}.culture-page .essay-header h1{font-size:clamp(2rem,5vw,3.1rem)}.culture-page .series-container{max-width:900px;margin:0 auto;padding:110px 2rem 60px}.essay-body{overflow-wrap:anywhere}.essay-body blockquote{margin:1.5rem 0;padding-left:1.25rem;border-left:2px solid var(--gold)}.essay-body ul,.essay-body ol{padding-left:1.5rem}.lang-toggle:not(.lang-select-menu){flex-wrap:wrap;max-width:100%}.edition-note{font-size:.85rem;color:var(--ink-muted);margin-bottom:2rem}.edition-note summary{cursor:pointer;font-family:var(--sans)}@media(max-width:620px){.culture-page .essay-header{padding:90px 1.5rem 0}.culture-page .series-container{padding:90px 1.5rem 60px}}</style>'
    extra+='<style>.culture-page .essay-header .lang-toggle.lang-select-menu{display:inline-flex;width:fit-content;margin-left:0;margin-right:0}.culture-page .essay-header .lang-select{color:var(--ink);background:#fff;border-color:var(--cream-border)}.culture-page .essay-header .lang-select-chevron{color:var(--ink-muted)}</style>'
    return s.replace('</head>',extra+'</head>',1)

def outputs():
    result={}
    for series in SERIES:
        for lang in LANGS:
            copies=[copy(series,lang,i+1) for i in range(len(series['chapters']))]
            for i,name in enumerate(series['chapters']):
                c=copies[i];s=(DATA/'templates'/series['slug']/lang/(name+'.html')).read_text()
                s,n=re.subn(r'(<article class="essay-body">).*?(<nav class="series-nav">)',lambda m:m[1]+c['body']+m[2],s,count=1,flags=re.S);assert n==1
                s,n=re.subn(r'<h1[^>]*>.*?</h1>',lambda m:'<h1>'+E(c['title'])+'</h1>',s,count=1,flags=re.S);assert n==1
                s=re.sub(r'(<p class="essay-entry-point">).*?(</p>)',lambda m:m[1]+E(c['description'])+m[2],s,flags=re.S)
                # Update the neighboring article titles without replacing the UI.
                def nav(m):
                    target=m[1][:-5]
                    return m[0].replace(m[2],E(copies[series['chapters'].index(target)]['title']))
                s=re.sub(r'<a[^>]*href="([^"]+\.html)"[^>]*><span class="nav-copy">.*?<span class="nav-title">(.*?)</span>',nav,s,flags=re.S)
                s=metadata(s,series,lang,name+'.html',c['title'],c['description'])
                result[ROOT/series['route']/lang/(name+'.html')]=s
            s=(DATA/'templates'/series['slug']/lang/'index.html').read_text()
            def card(m):
                target=m[1][:-5];c=copies[series['chapters'].index(target)]
                value=re.sub(r'(<div class="entry-title">).*?(</div>)',lambda x:x[1]+E(c['title'])+x[2],m[0],flags=re.S)
                return re.sub(r'(<div class="entry-desc">).*?(</div>)',lambda x:x[1]+E(c['description'])+x[2],value,flags=re.S)
            s,n=re.subn(r'<a href="([^"]+\.html)" class="entry-row">.*?</a>',card,s,flags=re.S);assert n==len(copies)
            title=html.unescape(re.sub('<[^>]+>','',re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S)[1]))
            desc=html.unescape(re.search(r'<meta name="description" content="([^"]*)">',s)[1])
            result[ROOT/series['route']/lang/'index.html']=metadata(s,series,lang,'index.html',title,desc)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    pages=outputs()
    for path,s in pages.items():
        if args.check: assert path.read_text()==s,path
        else: path.write_text(s)
    print(('Verified' if args.check else 'Built'),len(pages),'anime article/index pages')
