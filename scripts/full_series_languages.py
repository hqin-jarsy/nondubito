#!/usr/bin/env python3
"""Render complete, editorially reviewed rewrites; never generate translations.

Primary prose is kept separate. New language data carries a per-source-paragraph
coverage record, which supports human review but is not itself a quality score.
"""
from __future__ import annotations
import argparse
import html
import json
import re
from pathlib import Path

from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'en': 'English', 'zh': '简体中文', 'zh-hant': '繁體中文',
          'de': 'Deutsch', 'fr': 'Français', 'es': 'Español', 'ja': '日本語', 'ko': '한국어'}
E = html.escape
GUIDE = {'de':'Einführung','fr':'Introduction','es':'Introducción','ja':'はじめに','ko':'들어가며'}
SUPPLEMENT = {'de':'Ergänzung','fr':'Complément','es':'Complemento','ja':'補論','ko':'보론'}


def essay_label(article,index,language):
    """A prequel must not silently turn source essay 01 into foreign essay 02."""
    match=re.fullmatch(r'ep(\d+)',article['slug'])
    if match:return f'{int(match[1]):02d}'
    if article['slug'] in ('overview','prequel'):return GUIDE[language]
    if article['slug']=='interface':return SUPPLEMENT[language]
    return f'{index+1:02d}'


def profile(series):
    assert re.fullmatch(r'[a-z0-9-]+', series), series
    return json.loads((ROOT/'data'/series/'multilingual/profile.json').read_text())


def load_language(series, language):
    spec = profile(series)
    assert language in spec['languages']
    data = json.loads((ROOT/'data'/series/'multilingual'/f'{language}.json').read_text())
    assert data['language'] == language
    assert [a['slug'] for a in data['articles']] == spec['slugs']
    assert data['review']['unresolved'] == [], (series, language, 'unresolved editorial issues')
    for article in data['articles']:
        source_path = ROOT/'data'/series/(article['slug']+'.json')
        original = json.loads(source_path.read_text()) if source_path.exists() else json.loads((ROOT/'data'/series/'multilingual/source-baseline.json').read_text())[article['slug']]
        source = original['body_zh']
        assert len(article['body']) == len(source), (language, article['slug'], 'missing argument units')
        assert len(article['coverage']) == len(source)
        for p, q, note in zip(source, article['body'], article['coverage']):
            assert isinstance(q, str) and q.strip() and '<' not in q and '�' not in q
            assert p.startswith('## ') == q.startswith('## '), (language, article['slug'], p[:40])
            assert isinstance(note, str) and note.strip()
        article['source_url'] = original.get('source_url', spec['source'])
    return spec, data


def origin(spec):
    return 'https://nondubito.net/' + spec['directory'] + '/'


def alternatives(spec, slug):
    suffix = '' if slug == 'index' else slug+'.html'
    pairs = [('x-default', origin(spec)+suffix), ('zh-Hans', origin(spec)+suffix)]
    pairs += [(code, origin(spec)+code+'/'+suffix) for code in spec['languages']]
    # EN / Hant are reading modes of one legacy canonical, not fabricated URLs.
    return ''.join(f'<link rel="alternate" hreflang="{lang}" href="{url}">' for lang, url in pairs)


def upgrade_primary(text, series, slug):
    spec = profile(series)
    if spec.get('source_format') == 'legacy-html':
        return upgrade_legacy_primary(text,spec,slug)
    links = ''.join(f'<a href="{code}/{slug}.html" lang="{code}">{LABELS[code]}</a>' for code in spec['languages'])
    for label in ('繁體中文', '繁體'):
        pattern = r'<button\b(?=[^>]*data-set-language="zh-hant")[^>]*>'+label+r'</button>'
        anchors = re.findall(pattern,text)
        assert len(anchors) == 1, (series, slug, label)
        anchor = anchors[0]
        # Source builders pass fresh primary markup, not a previously patched file.
        text = text.replace(anchor, anchor+links)
    assert not re.search(r'<link[^>]*rel="alternate"', text)
    return text.replace('</head>', alternatives(spec, slug)+'</head>', 1)


def upgrade_legacy_primary(text,spec,slug):
    """Keep legacy English/Chinese bodies and Hant dictionaries byte-for-byte."""
    start,end='<!-- FULL SERIES LANGUAGE LINKS START -->','<!-- FULL SERIES LANGUAGE LINKS END -->'
    text=re.sub(re.escape(start)+r'.*?'+re.escape(end),'',text,flags=re.S)
    links=''.join(f'<span class="lang-sep">|</span><a class="lang-btn" href="{code}/{slug}.html" lang="{code}">{LABELS[code]}</a>' for code in spec['languages'])
    pattern=r'(<div class="lang-toggle"[^>]*>)(.*?)(</div>)'
    text,n=re.subn(pattern,lambda m:m[1]+m[2]+start+links+end+m[3],text,count=1,flags=re.S)
    assert n==1, (spec['id'],slug,'missing legacy language toggle')
    # Respect explicit same-article links before the saved three-language mode.
    old="var saved=localStorage.getItem('nd_lang')||localStorage.getItem('nondubito-lang')||'zh';"
    new="var requested=new URLSearchParams(location.search).get('lang');\n  var saved=requested||localStorage.getItem('nd_lang')||localStorage.getItem('nondubito-lang')||'zh';"
    if old in text:text=text.replace(old,new,1)
    assert new in text, (spec['id'],slug,'unknown primary language controller')
    alt_start,alt_end='<!-- FULL SERIES ALTERNATES START -->','<!-- FULL SERIES ALTERNATES END -->'
    text=re.sub(re.escape(alt_start)+r'.*?'+re.escape(alt_end),'',text,flags=re.S)
    script='<script defer src="../../language-select.js?v=20261103"></script>'
    text=text.replace(script,'')
    text=re.sub(r'<style id="full-series-language-layout">.*?</style>','',text,flags=re.S)
    layout='<style id="full-series-language-layout">body .lang-toggle.lang-select-menu{display:inline-flex;width:max-content;max-width:100%;}</style>'
    text=re.sub(r'<script id="full-series-language-state">.*?</script>','',text,flags=re.S)
    state='''<script id="full-series-language-state">document.addEventListener('change',function(event){var select=event.target;if(!select.matches('.lang-select'))return;var option=select.options[select.selectedIndex];var language=option&&option.dataset.inlineLanguage;if(!language)return;var url=new URL(location.href);url.searchParams.set('lang',language);history.replaceState(null,'',url);localStorage.setItem('nondubito-lang',language);});</script>'''
    return text.replace('</head>',alt_start+alternatives(spec,slug)+alt_end+script+layout+state+'</head>',1)


def language_links(spec, slug, language):
    rows = []
    for code, label in LABELS.items():
        href = '../'+slug+'.html?lang='+code if code in ('en', 'zh', 'zh-hant') else '../'+code+'/'+slug+'.html'
        current = ' aria-current="page"' if code == language else ''
        rows.append(f'<a href="{E(href)}" lang="{code if code != "zh" else "zh-Hans"}"{current}>{E(label)}</a>')
    return ''.join(rows)


def header(spec, data, slug):
    ui, lang = data['ui'], data['language']
    root = '../' * (len(Path(spec['directory']).parts)+1)
    nav = f'<a href="{root}essays/{lang}/index.html">{E(ui["home"])}</a><a href="index.html">{E(ui["contents"])}</a><a href="{root}library.html?lang=en">{E(ui["library"])}</a>'
    return f'''<header class="site-shell-header"><div class="header-inner"><a href="{root}essays/{lang}/index.html" class="site-title"><span class="title-latin">Non <span>Dubito</span></span></a><nav class="site-shell-nav">{nav}</nav><div class="site-shell-tools"><details class="site-shell-language"><summary class="site-shell-language-summary">{LABELS[lang]} <span aria-hidden="true">⌄</span></summary><div class="site-shell-language-options">{language_links(spec,slug,lang)}</div></details><button class="site-shell-menu-button" type="button" data-site-shell-menu aria-label="{E(ui['menu'])}" aria-controls="site-shell-drawer" aria-expanded="false"><span aria-hidden="true">☰</span></button></div></div></header><div class="site-shell-drawer" id="site-shell-drawer" data-site-shell-drawer><nav>{nav}<a href="{root}search.html?lang=en&amp;ui={lang}&amp;in={lang}">{E(ui['search'])}</a></nav></div>'''


def sources(spec, data, article=None):
    ui = data['ui']
    url = article['source_url'] if article else spec['source']
    note = article.get('source_note', data['series']['source_note']) if article else data['series']['source_note']
    paragraphs = ''.join('<p>'+inline_markdown(p)+'</p>' for p in re.split(r'\n\s*\n',note.strip()))
    return f'<details class="lw-sources"><summary>{E(ui["sources"])}</summary>{paragraphs}<p><a href="{E(url)}">{E(ui["paper"])} ↗</a></p></details>'


def inline_markdown(text):
    """Keep the supplied emphasis/citations without accepting arbitrary HTML."""
    text = E(text)
    text = re.sub(r'\[([^\]]+)\]\((https://[^\s)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    return text


def related(spec, data):
    root = '../' * (len(Path(spec['directory']).parts)+1)
    # The map is explicitly the existing EN/Chinese map; don't imply translation.
    return f'<aside class="lw-related"><h2>{E(data["ui"]["related"])}</h2><a href="{root}essays/sae/index.html?lang=en">{E(data["ui"]["map"])} · EN / 中文</a></aside>'


@tracked_html
def document(spec, data, slug, content, article=None):
    language = data['language']
    title = article['title'] if article else data['series']['title']
    deck = article['deck'] if article else data['series']['deck']
    url = origin(spec)+language+'/'+('' if slug == 'index' else slug+'.html')
    root = '../' * (len(Path(spec['directory']).parts)+1)
    schema = {'@context': 'https://schema.org', '@type': 'Article' if article else 'CollectionPage',
              'name': title, 'description': deck, 'inLanguage': language, 'url': url,
              'author': {'@type': 'Person', 'name': 'Han Qin (秦汉)'},
              'datePublished': spec['date'], 'dateModified': spec['date']}
    if article:
        schema.update(headline=title, mainEntityOfPage=url, citation=article['source_url'],
                      isPartOf={'@type':'CollectionPage', 'url':origin(spec)+language+'/', 'name':data['series']['title']},
                      translationOfWork={'@type':'Article', 'url':origin(spec)+slug+'.html'})
    else:
        schema['hasPart'] = [{'@type':'Article', 'name':a['title'], 'url':origin(spec)+language+'/'+a['slug']+'.html'} for a in data['articles']]
    structured = json.dumps(schema, ensure_ascii=False).replace('<', chr(92)+'u003c')
    font_href='https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=Inter:wght@300;400;500'
    if language in ('ja','ko'):
        font_href+='&family=Noto+Serif+'+('JP' if language=='ja' else 'KR')+':wght@400;500;600'
    fonts='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="'+E(font_href+'&display=swap')+'" rel="stylesheet">'
    return f'''<!doctype html>
<html lang="{language}" data-lang="{language}" data-editions="{language}" data-foreign-edition="true"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} — Non Dubito</title><meta name="description" content="{E(deck)}"><meta name="author" content="Han Qin (秦汉)"><link rel="canonical" href="{url}">{alternatives(spec,slug)}<meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(deck)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary"><link rel="icon" href="{root}favicon.svg" type="image/svg+xml">{fonts}<link rel="stylesheet" href="{root}style.css"><link rel="stylesheet" href="{root}site-shell.css?v=20260905b"><link rel="stylesheet" href="{root}essays/language-writing/reading.css?v=20261103"><script defer src="{root}essays/language-writing/reading.js?v=20261103"></script><script type="application/ld+json">{structured}</script></head><body class="site-shell-page lw-page lw-foreign"><a class="lw-skip" href="#main">{E(data['ui']['read'])}</a>{header(spec,data,slug)}<main id="main" class="lw-wrap">{content}</main><footer class="site-shell-footer"><div class="site-shell-footer-inner"><div class="site-shell-footer-mark">Non <span>Dubito</span></div><div class="site-shell-footer-links"><a href="{root}essays/{language}/index.html">{E(data['ui']['home'])}</a><a href="https://self-as-an-end.net/">{E(data['ui']['theory'])} ↗</a></div></div></footer></body></html>
'''


def render(series):
    spec = profile(series)
    pages = {}
    for language in spec['languages']:
        _, data = load_language(series, language)
        ui, title = data['ui'], data['series']
        cards = ''.join(f'<a class="lw-card" href="{a["slug"]}.html"><p class="lw-kicker">{E(essay_label(a,n,language))}</p><h2>{E(a["title"])}</h2><p>{E(a["deck"])}</p><span class="lw-read">{E(ui["read"])} →</span></a>' for n, a in enumerate(data['articles']))
        count = f'{len(data["articles"])} · ' + ' / '.join(LABELS.values())
        content = f'<section class="lw-hero"><p class="lw-kicker">Non Dubito · {E(ui["series"])}</p><h1>{E(title["title"])}</h1><p class="lw-deck">{E(title["deck"])}</p><p class="lw-meta">{E(count)}</p></section><aside class="lw-opening"><p>{E(title["intro"])}</p><a href="{data["articles"][0]["slug"]}.html">{E(ui["read"])} →</a></aside><section class="lw-grid">{cards}</section><section class="lw-note"><p>{E(title["scope"])}</p></section>'+sources(spec, data)+related(spec, data)
        target = ROOT/spec['directory']/language
        pages[target/'index.html'] = document(spec, data, 'index', content)
        for n, article in enumerate(data['articles']):
            body = '\n'.join('<h2>'+inline_markdown(p[3:])+'</h2>' if p.startswith('## ') else '<p>'+inline_markdown(p)+'</p>' for p in article['body'])
            deck = '<p class="lw-deck">'+E(article['deck'])+'</p>' if article.get('show_deck',True) else ''
            nav = []
            for offset, label in ((-1, 'previous'), (1, 'next')):
                k = n + offset
                other = data['articles'][k] if 0 <= k < len(data['articles']) else None
                href = other['slug']+'.html' if other else 'index.html'
                nav.append(f'<a href="{href}"><small>{E(ui[label] if other else ui["contents"])}</small>{E(other["title"] if other else title["title"])}</a>')
            content = f'<nav class="lw-crumb"><a href="index.html">← {E(title["title"])}</a></nav><article class="lw-article"><div class="lw-head"><p class="lw-kicker">{E(ui["series"])} · {E(essay_label(article,n,language))}</p><h1>{E(article["title"])}</h1>{deck}<p class="lw-meta">Han Qin · <time datetime="{spec["date"]}">{spec["date"]}</time></p></div><div class="essay-body lw-prose" lang="{language}">{body}</div>{sources(spec,data,article)}<nav class="lw-series-nav">'+''.join(nav)+'</nav>'+related(spec,data)+'</article>'
            pages[target/(article['slug']+'.html')] = document(spec, data, article['slug'], content, article)
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--primary', action='store_true', help='also connect preserved legacy primary-page language controls')
    args = parser.parse_args()
    pages = render(args.series)
    if args.primary:
        spec=profile(args.series)
        assert spec.get('source_format')=='legacy-html'
        for slug in ['index',*spec['slugs']]:
            path=ROOT/spec['directory']/(slug+'.html')
            pages[path]=upgrade_primary(path.read_text(),args.series,slug)
    for path, text in pages.items():
        if args.check:
            assert path.read_text() == text, path
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(f'{args.series}: {len(pages)} complete language pages '+('checked' if args.check else 'rendered'))


if __name__ == '__main__':
    main()
