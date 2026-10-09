"""Second-batch navigation and full editions; source-language prose is immutable."""
import html
import json
import re
import markdown
import build_anime_full_editions as b

NAMES={'en':'EN','zh':'中文','zh-hant':'繁體','ja':'日本語','fr':'Français','de':'Deutsch','es':'Español','ko':'한국어'}
UI={
 'de':('Anime und Manga','Alle fünf Essays','Voriger Essay','Nächster Essay','Deutsche Neufassung'),
 'fr':('Anime et manga','Les cinq essais','Essai précédent','Essai suivant','Réécriture française'),
 'es':('Anime y manga','Los cinco ensayos','Ensayo anterior','Ensayo siguiente','Reescritura en español'),
 'ja':('アニメと漫画を読む','全五篇の目次','前の篇','次の篇','日本語版'),
 'ko':('애니메이션과 만화 읽기','다섯 편 전체 목차','이전 글','다음 글','한국어판'),
}
TITLES={
 'psycho-pass':['PSYCHO-PASS lesen','Lire PSYCHO-PASS','Leer PSYCHO-PASS','『PSYCHO-PASS サイコパス』を読む','《PSYCHO-PASS》 읽기'],
 'run-with-the-wind':['Run with the Wind lesen','Lire Run with the Wind','Leer Run with the Wind','『風が強く吹いている』を読む','《바람이 강하게 불고 있다》 읽기'],
 'parasyte':['Parasyte lesen','Lire Parasite','Leer Parasyte','『寄生獣』を読む','《기생수》 읽기'],
 'chainsaw-man':['Chainsaw Man lesen','Lire Chainsaw Man','Leer Chainsaw Man','『チェンソーマン』を読む','《체인소 맨》 읽기'],
 'legend-of-the-galactic-heroes':['Legend of the Galactic Heroes lesen','Lire Les Héros de la Galaxie','Leer La leyenda de los héroes de la galaxia','『銀河英雄伝説』を読む','《은하영웅전설》 읽기'],
}

def index_copy(series,lang):
    # All packages carry five localized introductions in their README. Keep the
    # prose before the article list; render cards from the reviewed article copy.
    s=next((b.DATA/'received'/series['slug']).rglob('README.md')).read_text()
    matches=list(re.finditer(r'^## (.+)$',s,re.M))
    patterns={'de':r'^(Deutsch|DE\b|PSYCHO-PASS lesen)',
      'fr':r'^(Français|FR\b|Lire PSYCHO-PASS)',
      'es':r'^(Español|ES\b|Leer PSYCHO-PASS|Lecturas de Parasyte)',
      'ja':r'^(日本語|JA\b)','ko':r'^(한국어|KO\b)'}
    match=next(m for m in matches if re.search(patterns[lang],m[1]))
    end=next((m.start() for m in matches if m.start()>match.start()),len(s))
    section=s[match.end():end]
    section=re.split(r'(?m)^(?:#{3,4}\s*[IVⅠ]|1\.\s*\[|-\s*I\s*·)',section)[0]
    paras=[p.strip() for p in re.split(r'\n\s*\n',section)]
    paras=[p for p in paras if len(b.plain(p))>65 and not p.startswith(('#','[')) and 'Han Qin' not in p and not re.search(r'https?://',p)]
    assert len(paras)>=2,(series['slug'],lang,paras)
    return dict(title=TITLES[series['slug']][b.LANGS.index(lang)],body=markdown.markdown('\n\n'.join(paras)),description=b.plain(paras[0])[:230])

def menu(filename,lang=None):
    items=[]
    for code,label in NAMES.items():
        if lang is None and code in ('en','zh','zh-hant'):
            items.append(f'<button class="lang-btn" data-lang="{code}">{label}</button>')
        elif code==lang:
            items.append(f'<span class="lang-btn active" aria-current="page">{label}</span>')
        else:
            handler=''
            if code in ('en','zh','zh-hant'):
                href='../'+filename
                handler=f' onclick="localStorage.setItem(\'nd_lang\',\'{code}\');localStorage.setItem(\'nondubito-lang\',\'{code}\')"'
            else: href=('../' if lang else '')+code+'/'+filename
            items.append(f'<a class="lang-btn" href="{href}"{handler}>{label}</a>')
    return '<div class="lang-toggle" aria-label="Language">'+''.join(items)+'</div>'

def page(series,lang,copies,ep=None):
    u=UI[lang];intro=index_copy(series,lang);c=copies[ep-1] if ep else intro
    name=series['chapters'][ep-1]+'.html' if ep else 'index.html'
    # Reuse the established visual shell, never the old abbreviated article.
    template=(b.DATA/'templates/psycho-pass'/lang/'1-harmed-then-reclassified.html').read_text()
    shell=template[:template.index('<main>')]
    footer=template[template.index('<footer>'):]
    shell=re.sub(r'<link rel="canonical"[^>]*>',f'<link rel="canonical" href="https://nondubito.net/{series["route"]}/{lang}/{name if ep else ""}">',shell)
    shell=shell.replace('<body class="culture-page">',f'<body class="culture-page {lang}">')
    shell=shell.replace('</head>',f'<meta property="og:url" content="https://nondubito.net/{series["route"]}/{lang}/{name if ep else ""}"><meta property="og:type" content="{"article" if ep else "website"}"></head>')
    back=f'<a class="back-link" href="../../../../essays/anime/index.html">← {b.E(u[0])}</a>'
    title=f'<h1>{b.E(c["title"])}</h1>'
    meta=f'<p class="essay-meta">Han Qin (秦汉) · {b.E(u[4])} · 2026-10-09</p>'
    if ep:
        nav='<nav class="series-nav">'
        if ep>1:nav+=f'<a href="{series["chapters"][ep-2]}.html">← {b.E(u[2])}</a>'
        nav+=f'<a href="index.html">{b.E(u[1])}</a>'
        if ep<len(copies):nav+=f'<a href="{series["chapters"][ep]}.html">{b.E(u[3])} →</a>'
        nav+='</nav>'
        main=f'<main><div class="essay-header">{menu(name,lang)}<a class="back-link" href="index.html">← {b.E(intro["title"])}</a><div class="essay-number">{ep} / {len(copies)}</div>{title}{meta}</div><article class="essay-body">{c["body"]}{nav}</article></main>'
    else:
        cards=''.join(f'<li><a class="entry-row" href="{stem}.html"><div class="entry-num">{i+1} / {len(copies)}</div><div class="entry-title">{b.E(copies[i]["title"])}</div><div class="entry-desc">{b.E(copies[i]["description"])}</div></a></li>' for i,stem in enumerate(series['chapters']))
        main=f'<main class="series-container">{menu(name,lang)}{back}{title}{meta}<div class="series-desc">{intro["body"]}</div><ul class="entry-list">{cards}</ul></main>'
    return b.metadata(shell+main+footer,series,lang,name,c['title'],c['description'])

def legacy(series,name):
    s=(b.DATA/'templates'/series['slug']/name).read_text()
    # Root-language bodies, including the Traditional Chinese assets, stay byte
    # identical. Only the selector and head metadata receive additions.
    s,n=re.subn(r'<div class="lang-toggle"[^>]*>.*?</div>',lambda m:menu(name),s,count=1,flags=re.S)
    assert n==1
    base='https://nondubito.net/'+series['route']+'/'
    suffix='' if name=='index.html' else name
    alternates=''.join(f'<link rel="alternate" hreflang="{l}" href="{base+l+"/"+suffix}">' for l in b.LANGS)
    alternates+=f'<link rel="alternate" hreflang="x-default" href="{base+suffix}">'
    extra=alternates+'<script defer src="../../../language-select.js"></script><style>.lang-toggle:not(.lang-select-menu){flex-wrap:wrap;max-width:100%}</style>'
    return s.replace('</head>','<!-- anime-full-head -->'+extra+'<!-- /anime-full-head --></head>')

def outputs():
    out={}
    for series in b.SERIES:
        for lang in b.LANGS:
            copies=[b.copy(series,lang,i+1) for i in range(len(series['chapters']))]
            out[b.ROOT/series['route']/lang/'index.html']=page(series,lang,copies)
            for ep,stem in enumerate(series['chapters'],1):
                out[b.ROOT/series['route']/lang/(stem+'.html')]=page(series,lang,copies,ep)
        for name in ['index',*series['chapters']]:
            out[b.ROOT/series['route']/(name+'.html')]=legacy(series,name+'.html')
    return out
