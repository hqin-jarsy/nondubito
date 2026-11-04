#!/usr/bin/env python3
"""Render complete, editorially reviewed rewrites; never generate translations.

Primary prose is kept separate. New language data carries a per-source-paragraph
coverage record, which supports human review but is not itself a quality score.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
from pathlib import Path

from web_analytics import tracked_html
from clustered_language_indexes import grouped_index, validate_groups

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'en': 'English', 'zh': '简体中文', 'zh-hant': '繁體中文',
          'de': 'Deutsch', 'fr': 'Français', 'es': 'Español', 'ja': '日本語', 'ko': '한국어'}
E = html.escape
GUIDE = {'de':'Einführung','fr':'Introduction','es':'Introducción','ja':'はじめに','ko':'들어가며'}
SUPPLEMENT = {'de':'Ergänzung','fr':'Complément','es':'Complemento','ja':'補論','ko':'보론'}
SPECIAL_STUDY = {'de':'Eigenständige Studie','fr':'Étude indépendante','es':'Estudio independiente','ja':'独立した特論','ko':'독립 특론'}


def article_count(language,n):
    return {'de':f'{n} '+('Essay' if n==1 else 'Essays'),'fr':f'{n} '+('essai' if n==1 else 'essais'),'es':f'{n} '+('ensayo' if n==1 else 'ensayos'),'ja':f'{n}篇','ko':f'글 {n}편'}[language]


def collection_count(spec,language,n):
    separate=len(spec.get('standalone_slugs',[]))
    if not separate:return article_count(language,n)
    studies={'de':f'{separate} eigenständige '+('Studie' if separate==1 else 'Studien'),
             'fr':f'{separate} étude'+('' if separate==1 else 's')+' indépendante'+('' if separate==1 else 's'),
             'es':f'{separate} estudio'+('' if separate==1 else 's')+' independiente'+('' if separate==1 else 's'),
             'ja':f'独立特論{separate}篇','ko':f'독립 특론 {separate}편'}
    return article_count(language,n-separate)+' + '+studies[language]


def edition_count(language,n,spec=None):
    count=collection_count(spec,language,n) if spec else article_count(language,n)
    return count+' · '+{'de':'8 Sprachen','fr':'8 langues','es':'8 idiomas','ja':'8言語','ko':'8개 언어'}[language]


def essay_label(article,index,language):
    """A prequel must not silently turn source essay 01 into foreign essay 02."""
    match=re.fullmatch(r'ep(\d+)',article['slug'])
    if match:return f'{int(match[1]):02d}'
    if article['slug'] in ('overview','prequel'):return GUIDE[language]
    if article['slug']=='interface':return SUPPLEMENT[language]
    if article['slug']=='adversity':return SPECIAL_STUDY[language]
    return f'{index+1:02d}'


def profile(series):
    assert re.fullmatch(r'[a-z0-9-]+', series), series
    return json.loads((ROOT/'data'/series/'multilingual/profile.json').read_text())


def source_directory(series, spec=None):
    """Use a nested published collection without copying or rebasing its sources."""
    spec = spec or profile(series)
    path = (ROOT/spec.get('source_directory', 'data/'+series)).resolve()
    assert path.is_relative_to((ROOT/'data').resolve()), (series, 'source outside data')
    return path


def require_review_seal(series,spec):
    """A structural match is not editorial approval; require the frozen review."""
    if not spec.get('require_review_seal'):return
    base=ROOT/'data'/series/'multilingual'
    receipt=json.loads((base/'publication.json').read_text())
    assert receipt['result']=='passed' and receipt['unresolved']==[]
    assert receipt['languages']==spec['languages'] and receipt['slugs']==spec['slugs']
    for name in ('cross-review-de-fr.json','cross-review-ja-ko.json','cross-review-es.json'):
        assert name in receipt['reports']
        report=json.loads((base/name).read_text())
        assert report['remaining']==[],(series,name,'unfinished review')
        if spec.get('require_explicit_publication_approval'):
            assert report.get('publication_ready') is True,(series,name,'not approved for publication')
    for name in receipt['reports']:
        actual=hashlib.sha256((base/name).read_bytes()).hexdigest()
        assert receipt['review_report_sha256'][name]==actual,(series,name,'review changed after seal')
    for language in spec['languages']:
        actual=hashlib.sha256((base/(language+'.json')).read_bytes()).hexdigest()
        assert receipt['language_data_sha256'][language]==actual,(series,language,'draft changed after review')
    preservation=json.loads((base/'preservation.json').read_text())
    for name,digest in preservation.get('protected_files',{}).items():
        actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        assert digest==actual,(series,name,'protected primary source changed after review')
    for slug in spec['slugs']:
        actual=hashlib.sha256((source_directory(series,spec)/(slug+'.json')).read_bytes()).hexdigest()
        assert preservation['source_data'][slug]==actual,(series,slug,'source changed after review')


def load_language(series, language):
    spec = profile(series)
    assert language in spec['languages']
    data = json.loads((ROOT/'data'/series/'multilingual'/f'{language}.json').read_text())
    assert data['language'] == language
    assert [a['slug'] for a in data['articles']] == spec['slugs']
    assert data['review']['unresolved'] == [], (series, language, 'unresolved editorial issues')
    validate_groups(spec, data)
    if spec.get('visible_notice'):
        assert isinstance(data['series']['notice'],str) and data['series']['notice'].strip()
    if spec.get('index_context_source'):
        context=json.loads((ROOT/spec['index_context_source']).read_text())['body_zh']
        assert len(data['series']['index_context'])==len(context)
        assert len(data['series']['index_context_coverage'])==len(context)
        for p,q,note in zip(context,data['series']['index_context'],data['series']['index_context_coverage']):
            assert isinstance(q,str) and q.strip() and '<' not in q
            assert block_kind(p)==block_kind(q)
            assert isinstance(note,str) and note.strip()
    for article in data['articles']:
        source_path = source_directory(series,spec)/(article['slug']+'.json')
        original = json.loads(source_path.read_text()) if source_path.exists() else json.loads((ROOT/'data'/series/'multilingual/source-baseline.json').read_text())[article['slug']]
        source = original['body_zh']
        assert len(article['body']) == len(source), (language, article['slug'], 'missing argument units')
        assert len(article['coverage']) == len(source)
        for p, q, note in zip(source, article['body'], article['coverage']):
            assert isinstance(q, str) and q.strip() and '<' not in q and '�' not in q
            assert p.startswith('## ') == q.startswith('## '), (language, article['slug'], p[:40])
            assert isinstance(note, str) and note.strip()
            if spec.get('append_only') or spec.get('preserve_block_types'):
                assert block_kind(p)==block_kind(q),(language,article['slug'],'changed block type',p[:40])
        article['source_url'] = original.get('source_url', spec['source'])
        if spec.get('numbered_sources'):
            assert [(x['id'],x['url']) for x in article['sources']] == [(x['id'],x['url']) for x in original['sources']]
            assert all(x['title'].strip() and x['note'].strip() for x in article['sources'])
            for p,q in zip(source,article['body']):
                assert re.findall(r'\[(\d+)\]',p)==re.findall(r'\[(\d+)\]',q), (language,article['slug'],'reference moved or lost')
            assert article['kicker'].strip()
            article['source_url'] = original['sources'][0]['url']
            article['_temporal_coverage'] = original.get('coverage')
            for key in ('theory_heading','theory_note'):
                assert data['ui'][key].strip()
            assert data['series']['count_label'].strip()
        if spec.get('theory_companions'):
            assert isinstance(article.get('takeaway'), str) and article['takeaway'].strip()
            assert [link['slug'] for link in article['case_links']] == original['case_slugs']
            assert all(isinstance(link['title'], str) and link['title'].strip() for link in article['case_links'])
            for key in ('case_heading', 'case_note', 'takeaway_heading'):
                assert isinstance(data['ui'].get(key), str) and data['ui'][key].strip()
    return spec, data


def block_kind(text):
    if text.startswith('## '):return 'heading'
    if text.startswith('> '):return 'quote'
    match=re.match(r'([1-9])\. ',text)
    if match:return 'item:'+match[1]
    match=re.match(r'\*\*(1[3-6]DD)\*\* ',text)
    if match:return match[1]
    return 'paragraph'


def render_prose(units, citations=None, source_label=''):
    blocks=[]
    items=[]
    def inline(text):
        result=inline_markdown(text)
        if citations:
            result=re.sub(r'\[(\d+)\]',lambda m:'<sup class="st-cite"><a href="'+E(citations[int(m[1])])+'" aria-label="'+E(source_label+' '+m[1])+'">['+m[1]+']</a></sup>',result)
        return result
    def flush():
        if items:
            blocks.append('<ol>'+''.join('<li>'+inline(x)+'</li>' for x in items)+'</ol>')
            items.clear()
    for text in units:
        if re.match(r'^[1-9]\. ',text):items.append(text[3:]);continue
        flush()
        if text.startswith('## '):blocks.append('<h2>'+inline(text[3:])+'</h2>')
        elif text.startswith('> '):blocks.append('<blockquote>'+inline(text[2:])+'</blockquote>')
        else:blocks.append('<p>'+inline(text)+'</p>')
    flush()
    return '\n'.join(blocks)


def primary_bodies(spec,text):
    if spec.get('primary_format')=='foundations-bridge':
        return ''.join(re.findall(r'<article class="bridge-body[^>]*>.*?</article>',text,re.S))
    return ''.join(re.findall(r'<div class="essay-body[^>]*>.*?</div>',text,re.S))


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
    if slug in spec.get('modern_slugs',[]):
        return upgrade_mixed_modern_primary(text,spec,slug)
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


def upgrade_mixed_modern_primary(text,spec,slug):
    """Add routes to a newer standalone page inside a legacy series, idempotently."""
    start,end='<!-- MIXED SERIES LANGUAGE LINKS START -->','<!-- MIXED SERIES LANGUAGE LINKS END -->'
    text=re.sub(re.escape(start)+r'.*?'+re.escape(end),'',text,flags=re.S)
    links=''.join(f'<a href="{code}/{slug}.html" lang="{code}">{LABELS[code]}</a>' for code in spec['languages'])
    pattern=r'<button\b(?=[^>]*data-set-language="zh-hant")[^>]*>.*?</button>'
    text,n=re.subn(pattern,lambda m:m[0]+start+links+end,text,flags=re.S)
    assert n==2,(spec['id'],slug,'desktop and drawer language controls required')
    a,b='<!-- MIXED SERIES ALTERNATES START -->','<!-- MIXED SERIES ALTERNATES END -->'
    text=re.sub(re.escape(a)+r'.*?'+re.escape(b),'',text,flags=re.S)
    assert not re.search(r'<link[^>]*rel="alternate"',text)
    return text.replace('</head>',a+alternatives(spec,slug)+b+'</head>',1)


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
    if article and spec.get('numbered_sources'):
        refs='<ol class="st-source-list">'+''.join('<li><a href="'+E(s['url'])+'">'+E(s['title'])+'</a><p>'+inline_markdown(s['note'])+'</p></li>' for s in article['sources'])+'</ol>'
        return f'<details class="lw-sources"><summary>{E(ui["sources"])}</summary>{paragraphs}{refs}<p><a href="{E(spec["source"])}">{E(ui["paper"])} ↗</a></p></details>'
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
    links=f'<a href="{root}essays/sae/index.html?lang=en">{E(data["ui"]["map"])} · EN / 中文</a>'
    for target in spec.get('related_series',[]):
        target_spec,target_data=load_language(target,data['language'])
        links+=f'<a href="{root}{target_spec["directory"]}/{data["language"]}/index.html">{E(target_data["series"]["title"])}</a>'
    return f'<aside class="lw-related"><h2>{E(data["ui"]["related"])}</h2>{links}</aside>'


def theory_companions(spec, data, article):
    """Keep the published takeaway and evidence route, honestly labeled by edition."""
    if not spec.get('theory_companions'):
        return ''
    config = spec['theory_companions']
    if config.get('native'):
        _, native = load_language(config['series'], data['language'])
        lookup = {a['slug']: a['title'] for a in native['articles']}
        links = ''.join('<a href="'+E(config['path']+data['language']+'/'+link['slug']+'.html')+'">'
                        +E(lookup[link['slug']])+'</a>' for link in article['case_links'])
    else:
        links = ''.join('<a href="'+E(config['path']+link['slug']+'.html?lang=en')+'">'
                        +E(link['title'])+' · EN / 中文</a>' for link in article['case_links'])
    return ('<aside class="lw-note pe-takeaway"><h2>'+E(data['ui']['takeaway_heading'])+'</h2><p>'
            +E(article['takeaway'])+'</p></aside><aside class="lw-related pe-case-companion"><h2>'
            +E(data['ui']['case_heading'])+'</h2><p>'+E(data['ui']['case_note'])+'</p>'+links+'</aside>')


def theory_case_route(spec, data):
    if not spec.get('theory_companions'):
        return ''
    config = spec['theory_companions']
    suffix = data['language']+'/index.html#cases' if config.get('native') else 'index.html?lang=en#cases'
    label = '' if config.get('native') else ' · EN / 中文'
    return ('<aside class="lw-related pe-case-route"><h2>'+E(data['ui']['case_heading'])
            +'</h2><p>'+E(data['ui']['case_note'])+'</p><a href="'
            +E(config['path']+suffix)+'">'
            +E(data['ui']['case_heading'])+label+' →</a></aside>')


def case_theory_route(spec, data, article=None):
    """A documented case tests a theory; it is not a substitute for reading it."""
    if not spec.get('case_theory_series'):
        return ''
    from political_economy_routes import CASE_TO_THEORY
    target, native = load_language(spec['case_theory_series'], data['language'])
    root = '../' * (len(Path(spec['directory']).parts)+1)
    base = root+target['directory']+'/'+data['language']+'/'
    lookup = {a['slug']:a for a in native['articles']}
    links = ''.join('<a href="'+E(base+slug+'.html')+'">'+E(lookup[slug]['title'])+'</a>'
                    for slug in CASE_TO_THEORY[article['slug']]) if article else ''
    links += '<a href="'+E(base+'index.html')+'">'+E(native['series']['title'])+' →</a>'
    return ('<aside class="lw-related pe-theory-companion"><h2>'+E(data['ui']['theory_heading'])
            +'</h2><p>'+E(data['ui']['theory_note'])+'</p>'+links+'</aside>')


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
        if spec.get('numbered_sources'):
            schema['citation'] = [s['url'] for s in article['sources']]
            if article.get('_temporal_coverage'):
                schema['temporalCoverage'] = article['_temporal_coverage']
    else:
        schema['hasPart'] = [{'@type':'Article', 'name':a['title'], 'url':origin(spec)+language+'/'+a['slug']+'.html'} for a in data['articles']]
    structured = json.dumps(schema, ensure_ascii=False).replace('<', chr(92)+'u003c')
    font_href='https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=Inter:wght@300;400;500'
    if language in ('ja','ko'):
        font_href+='&family=Noto+Serif+'+('JP' if language=='ja' else 'KR')+':wght@400;500;600'
    fonts='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="'+E(font_href+'&display=swap')+'" rel="stylesheet">'
    grouped_css = f'<link rel="stylesheet" href="{root}essays/language-writing/grouped-reading.css?v=20261103b">' if spec.get('index_groups') and slug == 'index' else ''
    if spec.get('numbered_sources'):
        grouped_css += f'<link rel="stylesheet" href="{root}essays/state-transitions/reading.css?v=20261029">'
    return f'''<!doctype html>
<html lang="{language}" data-lang="{language}" data-editions="{language}" data-foreign-edition="true"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} — Non Dubito</title><meta name="description" content="{E(deck)}"><meta name="author" content="Han Qin (秦汉)"><link rel="canonical" href="{url}">{alternatives(spec,slug)}<meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(deck)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary"><link rel="icon" href="{root}favicon.svg" type="image/svg+xml">{fonts}<link rel="stylesheet" href="{root}style.css"><link rel="stylesheet" href="{root}site-shell.css?v=20260905b"><link rel="stylesheet" href="{root}essays/language-writing/reading.css?v={spec.get('reading_css_version','20261103')}">{grouped_css}<script defer src="{root}essays/language-writing/reading.js?v=20261103"></script><script type="application/ld+json">{structured}</script></head><body class="site-shell-page lw-page lw-foreign"><a class="lw-skip" href="#main">{E(data['ui']['read'])}</a>{header(spec,data,slug)}<main id="main" class="lw-wrap">{content}</main><footer class="site-shell-footer"><div class="site-shell-footer-inner"><div class="site-shell-footer-mark">Non <span>Dubito</span></div><div class="site-shell-footer-links"><a href="{root}essays/{language}/index.html">{E(data['ui']['home'])}</a><a href="https://self-as-an-end.net/">{E(data['ui']['theory'])} ↗</a></div></div></footer></body></html>
'''


def render(series):
    spec = profile(series)
    require_review_seal(series,spec)
    pages = {}
    for language in spec['languages']:
        _, data = load_language(series, language)
        ui, title = data['ui'], data['series']
        notice=('<p class="lw-meta" style="max-width:70ch;line-height:1.75">'+E(title['notice'])+'</p>') if spec.get('visible_notice') else ''
        card_rows=[]
        for n,a in enumerate(data['articles']):
            card=f'<a class="lw-card" href="{a["slug"]}.html"><p class="lw-kicker">{E(a.get("kicker",essay_label(a,n,language)))}</p><h2>{E(a["title"])}</h2><p>{E(a["deck"])}</p><span class="lw-read">{E(ui["read"])} →</span></a>'
            card_rows.append((a['slug'],card))
        standalone=set(spec.get('standalone_slugs',[]))
        grid='<section class="lw-grid">'+''.join(card for slug,card in card_rows if slug not in standalone)+'</section>'
        if standalone:
            grid+='<section class="lw-note"><h2>'+E(SPECIAL_STUDY[language])+'</h2></section><section class="lw-grid">'+''.join(card for slug,card in card_rows if slug in standalone)+'</section>'
        if spec.get('index_groups'):
            grid = grouped_index(spec, data, card_rows)
        count = title.get('count_label',collection_count(spec,language,len(data['articles'])))+' · '+' / '.join(LABELS.values())
        context=title.get('index_context',[])
        assert isinstance(context,list) and all(isinstance(p,str) and p.strip() for p in context)
        index_context='<section class="lw-note">'+render_prose(context)+'</section>' if context else ''
        content = f'<section class="lw-hero"><p class="lw-kicker">Non Dubito · {E(ui["series"])}</p><h1>{E(title["title"])}</h1><p class="lw-deck">{E(title["deck"])}</p><p class="lw-meta">{E(count)}</p>{notice}</section>'+case_theory_route(spec,data)+f'<aside class="lw-opening"><p>{E(title["intro"])}</p><a href="{data["articles"][0]["slug"]}.html">{E(ui["read"])} →</a></aside>{grid}<section class="lw-note"><p>{E(title["scope"])}</p></section>'+index_context+theory_case_route(spec,data)+sources(spec, data)+related(spec, data)
        target = ROOT/spec['directory']/language
        if not spec.get('append_only'):
            pages[target/'index.html'] = document(spec, data, 'index', content)
        for n, article in enumerate(data['articles']):
            citations = {s['id']:s['url'] for s in article['sources']} if spec.get('numbered_sources') else None
            body = render_prose(article['body'],citations,ui['sources'])
            deck = '<p class="lw-deck">'+E(article['deck'])+'</p>' if article.get('show_deck',True) else ''
            nav = []
            for offset, label in ((-1, 'previous'), (1, 'next')):
                k = n + offset
                other = data['articles'][k] if 0 <= k < len(data['articles']) else None
                if standalone and (article['slug'] in standalone or (other and other['slug'] in standalone)):
                    other=None
                href = other['slug']+'.html' if other else 'index.html'
                if not other and spec.get('index_groups'):
                    href += '#reading-route'
                nav.append(f'<a href="{href}"><small>{E(ui[label] if other else ui["contents"])}</small>{E(other["title"] if other else title["title"])}</a>')
            if article['slug'] in standalone:
                nav=nav[:1]
            label=article.get('kicker',essay_label(article,n,language))
            if spec.get('append_only'):
                label=SUPPLEMENT[language] if spec['article_label']=='supplement' else spec['article_label']
                nav=[]
                for direction,slug in spec.get('neighbors',{}).items():
                    neighbor=(target/(slug+'.html')).read_text()
                    heading=re.search(r'<h1\b[^>]*>(.*?)</h1>',neighbor,re.S)[1]
                    heading=html.unescape(re.sub(r'<[^>]+>','',heading))
                    nav.append(f'<a href="{slug}.html"><small>{E(ui[direction])}</small>{E(heading)}</a>')
                if len(nav)<2:nav.append(f'<a href="index.html"><small>{E(ui["contents"])}</small>{E(title["title"])}</a>')
            content = f'<nav class="lw-crumb"><a href="index.html">← {E(title["title"])}</a></nav><article class="lw-article"><div class="lw-head"><p class="lw-kicker">{E(ui["series"])} · {E(label)}</p><h1>{E(article["title"])}</h1>{deck}<p class="lw-meta">Han Qin · <time datetime="{spec["date"]}">{spec["date"]}</time></p>{notice}</div><div class="essay-body lw-prose" lang="{language}">{body}</div>{theory_companions(spec,data,article)}{case_theory_route(spec,data,article)}{sources(spec,data,article)}<nav class="lw-series-nav">'+''.join(nav)+'</nav>'+related(spec,data)+'</article>'
            pages[target/(article['slug']+'.html')] = document(spec, data, article['slug'], content, article)
    return pages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--primary', action='store_true', help='also connect preserved primary-page language controls')
    args = parser.parse_args()
    pages = render(args.series)
    if args.primary:
        spec=profile(args.series)
        assert spec.get('source_format') in ('legacy-html','modern-html')
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
