"""Append later companions to existing series without replacing their routes."""
import html
import hashlib
import json
import re

from full_series_languages import ROOT, LABELS, alternatives, load_language, profile


def availability(text):
    for before,after in [
        ('仅提供简体中文、繁体中文与英文。','八语全文。'),('僅提供簡體中文、繁體中文與英文。','八語全文。'),
        ('Available only in Simplified Chinese, Traditional Chinese, and English.','Available in all eight languages.'),
        ('00E is available in Simplified Chinese, Traditional Chinese, and English.','00E is also available in all eight languages.'),
        ('提供简体中文、繁体中文与英文','提供八种语言'),('提供簡體中文、繁體中文與英文','提供八種語言'),
        ('简中／繁中／EN','八语'),('簡中／繁中／EN','八語'),('ZH / TC / EN','Eight languages'),
        ('00E 提供简体中文、英文与繁体中文','00E 同样提供八语全文'),
        ('Twelve original papers in eight languages, plus the new introduction 00E in Simplified Chinese, English, and Traditional Chinese.','Twelve original papers and the introduction 00E, all in eight languages.')
    ]:text=text.replace(before,after)
    return text


def route_snapshot(series):
    spec=profile(series)
    directory=ROOT/spec['directory']
    result={'old_native_files':{},'index_entries':{},'primary_sources':{}}
    for lang in spec['languages']:
        for path in sorted((directory/lang).glob('*.html')):
            if path.stem in ['index',*spec['slugs']]:continue
            text=path.read_text()
            if series=='method-companion' and path.stem in ('00','viii'):
                text=re.sub(r'<nav class="method-nav">.*?</nav>','',text,flags=re.S)
            result['old_native_files'][str(path.relative_to(ROOT))]=hashlib.sha256(text.encode()).hexdigest()
    for lang in ['',*spec['languages']]:
        path=directory/lang/'index.html';text=path.read_text()
        entries=re.findall(r'<a\b(?=[^>]*class="[^\"]*\bentry-row\b)[^>]*>.*?</a>',text,re.S)
        if series=='method-companion':entries=[e for e in entries if 'href="00e.html"' not in e]
        assert len(entries)==(12 if series=='method-companion' else (30 if not lang else 15)),(path,len(entries))
        result['index_entries'][str(path.relative_to(ROOT))]=hashlib.sha256(''.join(entries).encode()).hexdigest()
    if series=='method-companion':
        for code in ('en','zh','zh-hant'):
            p=ROOT/'data/method-introduction'/(code+'.json')
            result['primary_sources'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        p=directory/'zh-hant-data/index.js'
        result['primary_sources'][str(p.relative_to(ROOT))]=hashlib.sha256(availability(p.read_text()).encode()).hexdigest()
    else:
        p=directory/'zh-hant-data/index.js'
        result['primary_sources'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def marked(text,name,content,position=None):
    start,end=f'<!-- {name} START -->',f'<!-- {name} END -->'
    if start in text:
        assert text.count(start)==text.count(end)==1
        return re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:start+content+end,text,flags=re.S)
    assert position is not None
    return text[:position]+start+content+end+text[position:]


def dropdown(text):
    script='<script defer src="../../language-select.js?v=20261103"></script>'
    # Resolve the path for existing native indexes one level below primary.
    root='../../../' if re.search(r'<html[^>]+lang="(?:de|fr|es|ja|ko)"',text) else '../../'
    script=script.replace('../../language-select',root+'language-select')
    if script not in text:text=text.replace('</head>',script+'</head>',1)
    style='<style id="companion-language-layout">.lang-toggle.lang-select-menu{display:inline-flex;width:max-content;max-width:100%;}</style>'
    if 'id="companion-language-layout"' not in text:text=text.replace('</head>',style+'</head>',1)
    return text


def upgrade_companion_primary(text,series):
    spec=profile(series)
    slug=spec['slugs'][0]
    text=text.replace('<script defer src="../../language-select.js?v=20261103"></script>','')
    text=re.sub(r'<style id="companion-language-layout">.*?</style>','',text,flags=re.S)
    start,end='<!-- COMPANION LANGUAGE LINKS START -->','<!-- COMPANION LANGUAGE LINKS END -->'
    text=re.sub(re.escape(start)+r'.*?'+re.escape(end),'',text,flags=re.S)
    links=''.join(f'<span class="lang-sep">|</span><a class="lang-btn" href="{lang}/{slug}.html" lang="{lang}">{LABELS[lang]}</a>' for lang in spec['languages'])
    text,n=re.subn(r'(<div class="lang-toggle"[^>]*>)(.*?)(</div>)',lambda m:m[1]+m[2]+start+links+end+m[3],text,count=1,flags=re.S)
    assert n==1
    if spec['primary_format']=='foundations-bridge':
        old="var saved=localStorage.getItem('nd_lang')||localStorage.getItem('nondubito-lang')||'en';"
        new="var requested=new URLSearchParams(location.search).get('lang');\n      var saved=requested||localStorage.getItem('nd_lang')||localStorage.getItem('nondubito-lang')||'en';"
        if old in text:text=text.replace(old,new,1)
        assert new in text
    # The primary URL has three reading modes, not three distinct canonicals.
    a,b='<!-- COMPANION ALTERNATES START -->','<!-- COMPANION ALTERNATES END -->'
    text=re.sub(re.escape(a)+r'.*?'+re.escape(b),'',text,flags=re.S)
    text=re.sub(r'<link\b(?=[^>]*rel="alternate")[^>]*>','',text)
    text=text.replace('</head>',a+alternatives(spec,slug)+b+'</head>',1)
    state='''<script id="companion-language-state">(function(){function sync(language){if(['en','zh','zh-hant'].indexOf(language)<0)return;document.documentElement.setAttribute('data-lang',language);document.documentElement.lang=language==='zh'?'zh-Hans':language==='zh-hant'?'zh-Hant':'en';var url=new URL(location.href);url.searchParams.set('lang',language);history.replaceState(null,'',url);localStorage.setItem('nd_lang',language);localStorage.setItem('nondubito-lang',language);var select=document.querySelector('.lang-toggle .lang-select');if(select){Array.prototype.forEach.call(select.options,function(option,index){if(option.dataset.inlineLanguage===language)select.selectedIndex=index;});}var suffix=language==='zh-hant'?'hant':language;var heading=document.querySelector('h1.lang-'+suffix);if(heading)document.title=heading.textContent+' — Non Dubito';}document.addEventListener('DOMContentLoaded',function(){sync(document.documentElement.getAttribute('data-lang'));});document.addEventListener('change',function(event){if(!event.target.matches('.lang-toggle .lang-select'))return;var option=event.target.options[event.target.selectedIndex];sync(option.dataset.inlineLanguage);});})();</script>'''
    text=re.sub(r'<script id="companion-language-state">.*?</script>','',text,flags=re.S)
    text=text.replace('</head>',state+'</head>',1)
    text=dropdown(text)
    head,separator,body=text.partition('</head>')
    return re.sub(r'(?m)^[ \t]+$', '', head)+separator+body


def native_indexes(series):
    spec=profile(series)
    pages={}
    for lang in spec['languages']:
        _,data=load_language(series,lang)
        article=data['articles'][0]
        path=ROOT/spec['directory']/lang/'index.html'
        text=path.read_text()
        card='<aside style="margin:2rem 0;padding:1.3rem;border-left:3px solid var(--gold);background:var(--cream-dark)"><p class="entry-num">'+html.escape(data['ui']['series'])+'</p><h2 style="font-weight:400;font-size:1.35rem;margin:.6rem 0"><a href="'+article['slug']+'.html">'+html.escape(article['title'])+'</a></h2><p style="line-height:1.8">'+html.escape(article['deck'])+'</p><a href="'+article['slug']+'.html">'+html.escape(data['ui']['read'])+' →</a></aside>'
        anchor=re.search(r'<(?:ul|div) class="(?:entry-list|part-heading)"',text)
        assert anchor,(series,lang,'unknown index')
        text=marked(text,'COMPANION '+series.upper(),card,anchor.start())
        pages[path]=dropdown(text)
        if series=='method-companion':
            for slug,old_target,direction in [('00','viii','next'),('viii','00','previous')]:
                p=path.with_name(slug+'.html');source=p.read_text()
                match=re.search(r'<nav class="method-nav">.*?</nav>',source,re.S);assert match
                nav=match[0]
                replacement='<a href="00e.html"><small>'+html.escape(data['ui'][direction])+'</small>'+html.escape(article['title'])+'</a>'
                # Re-apply idempotently to the actual neighbor, not its body.
                nav,n=re.subn(r'<a href="(?:'+old_target+r'|00e)\.html">.*?</a>',lambda _:replacement,nav,count=1,flags=re.S)
                assert n==1
                pages[p]=source[:match.start()]+nav+source[match.end():]
    return pages


def primary_index(series):
    spec=profile(series);path=ROOT/spec['directory']/'index.html';text=path.read_text()
    if series=='method-companion':return {path:dropdown(availability(text)),path.parent/'zh-hant-data/index.js':availability((path.parent/'zh-hant-data/index.js').read_text())}
    source=(path.parent/'remainder-and-subject.html').read_text()
    def value(code,kind):
        pattern=r'<h1 class="lang-'+code+r'">(.*?)</h1>' if kind=='title' else r'<p class="bridge-deck lang-'+code+r'">(.*?)</p>'
        return re.search(pattern,source,re.S)[1]
    def tri(kind):
        return '<span class="lang-en">'+value('en',kind)+'</span><span class="lang-zh"><span class="context-hans">'+value('zh',kind)+'</span><span class="context-hant">'+value('hant',kind)+'</span></span>'
    card='<aside style="margin:2rem 0;padding:1.3rem;border-left:3px solid var(--gold);background:var(--cream-dark)"><p class="entry-num"><span class="lang-en">A short bridge · Eight languages</span><span class="lang-zh"><span class="context-hans">入门桥梁 · 八语全文</span><span class="context-hant">入門橋梁 · 八語全文</span></span></p><h2 style="font-weight:400;font-size:1.35rem;margin:.6rem 0"><a href="remainder-and-subject.html">'+tri('title')+'</a></h2><p style="line-height:1.8">'+tri('deck')+'</p></aside>'
    toggle=re.search(r'<div class="lang-toggle"[^>]*>.*?</div>',text,re.S);assert toggle
    return {path:dropdown(marked(text,'FOUNDATIONS BRIDGE ENTRY',card,toggle.end()))}
