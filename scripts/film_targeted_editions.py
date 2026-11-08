"""Scoped full-English overlays for films 50, 56 and 59.

Chinese and Traditional Chinese remain unchanged unless an explicitly approved
revision is recorded. Received foreign manuscripts are immutable provenance.
"""
import html
import re
from pathlib import Path
import markdown
from prepare_action_sources import Document, one
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/film-full'
SLUGS=('raise-the-red-lantern','dead-poets-society','parasite')
DATE='2026-11-08'
UPDATED={'de':'Deutsche Ausgabe: 8. November 2026','fr':'Édition française : 8 novembre 2026','es':'Edición en español: 8 de noviembre de 2026','ja':'日本語版公開：2026年11月8日','ko':'한국어판 공개: 2026년 11월 8일'}

# Keep direct language URLs and next/previous links useful even if storage is denied.
LANG_SCRIPT="""<!-- film-targeted-language --><script>(function(){var allowed=['en','zh','zh-hant'],l=new URLSearchParams(location.search).get('lang');if(allowed.indexOf(l)<0){try{l=localStorage.getItem('nd_lang')||localStorage.getItem('nondubito-lang')}catch(e){}}if(allowed.indexOf(l)<0)l='zh';function set(v){document.documentElement.dataset.lang=v;document.documentElement.lang=v==='zh'?'zh-Hans':v==='zh-hant'?'zh-Hant':'en';try{localStorage.setItem('nd_lang',v);localStorage.setItem('nondubito-lang',v)}catch(e){}var u=new URL(location.href);u.searchParams.set('lang',v);history.replaceState(null,'',u);document.querySelectorAll('a[href]').forEach(function(a){var h=a.getAttribute('href');if(/^(?:index|[123]-[^/?]+)\\.html(?:\\?.*)?$/.test(h))a.setAttribute('href',h.split('?')[0]+'?lang='+v)});document.querySelectorAll('.lang-btn[data-lang]').forEach(function(b){b.classList.toggle('active',b.dataset.lang===v)})}document.documentElement.dataset.lang=l;document.documentElement.lang=l==='zh'?'zh-Hans':l==='zh-hant'?'zh-Hant':'en';document.addEventListener('DOMContentLoaded',function(){set(l);document.querySelectorAll('.lang-btn[data-lang]').forEach(function(b){b.onclick=function(){set(b.dataset.lang)}});var toggle=document.querySelector('.lang-toggle');if(toggle)toggle.addEventListener('change',function(e){var o=e.target.options&&e.target.options[e.target.selectedIndex];if(!o)return;if(o.dataset.inlineLanguage){e.stopImmediatePropagation();set(o.dataset.inlineLanguage)}else if(o.dataset.href){e.stopImmediatePropagation();if(o.dataset.storedLanguage){try{localStorage.setItem('nd_lang',o.dataset.storedLanguage)}catch(x){}}window.location.assign(o.dataset.href)}},true)})})();</script><!-- /film-targeted-language -->"""

def english(film,ep):
    path=DATA/'reviewed'/film['slug']/'en'/f'{ep:02}.md'
    text=path.read_text();title,body=text.split('\n',1)
    assert title.startswith('# ') and '## ' in body,path
    return title[2:].strip(),markdown.markdown(body)

def overlay(source,film,filename):
    if film['slug'] not in SLUGS:return source
    # Replace only the old embedded language controller; never touch article copy.
    if '<!-- film-targeted-language -->' in source:
        source=re.sub(r'<!-- film-targeted-language -->.*?<!-- /film-targeted-language -->',lambda _:LANG_SCRIPT,source,flags=re.S)
    elif '<script>(function(){var allowed=' in source:
        source=re.sub(r'<script>\(function\(\)\{var allowed=.*?</script>',lambda _:LANG_SCRIPT,source,count=1,flags=re.S)
    source,n=re.subn(r'<script>\(function\(\)\{var saved=localStorage.*?</script>',lambda _:LANG_SCRIPT,source,count=1,flags=re.S);assert n in (0,1)
    if filename=='index.html':
        for ep,slug in enumerate(film['chapters'],1):
            title,_=english(film,ep)
            # Both source-language cards share their English title.
            pattern=r'(<a href="'+re.escape(slug)+r'\.html(?:\?[^\"]*)?" class="essay-card">.*?<div class="card-title-en">).*?(</div>)'
            source,n=re.subn(pattern,lambda m:m[1]+html.escape(title)+m[2],source,flags=re.S);assert n==2,(filename,slug,n)
        source=source.replace('Three reading modes','Eight language editions')
        return source
    ep=film['chapters'].index(Path(filename).stem)+1;title,body=english(film,ep)
    doc=Document(source);node=one(doc.root.walk(),lambda n:n.tag=='div' and n.has('essay-body','lang-en'),'English body')
    note='<p class="film-edition-note" style="font-family:var(--sans);font-size:.72rem;color:var(--ink-muted);border-bottom:1px solid var(--cream-border);padding-bottom:1.25rem;"><strong>Edition note:</strong> Complete English edition based on the Chinese original; full-film spoilers. Dialogue is independently translated, not quoted from official subtitles.</p>'
    source=source[:node.open_end]+note+body+source[node.close_start:]
    doc=Document(source);node=one(doc.root.walk(),lambda n:n.tag=='div' and n.has('essay-body','lang-zh'),'Chinese body')
    source=source[:node.start]+revised_chinese_body(doc.raw(node),film['slug'],ep)+source[node.end:]
    source=re.sub(r'(<h1 class="essay-page-title lang-en">).*?(</h1>)',lambda m:m[1]+html.escape(title)+m[2],source,flags=re.S)
    source=re.sub(r'<title>.*?</title>',lambda m:'<title>'+html.escape(title)+' — Non Dubito</title>',source,count=1)
    source=re.sub(r'(<meta property="og:title" content=")[^"]*',lambda m:m[1]+html.escape(title+' — Non Dubito',quote=True),source,count=1)
    return source.replace('Independent English edition','Complete English edition')


def traditional_outputs(pages):
    """Extend existing dictionaries for UI only; preserve all original conversions."""
    import json
    result={}
    additions={'八种语言版本':'八種語言版本','59 个系列 · 177 篇 · 已有 18 部作品八语齐备':'59 個系列 · 177 篇 · 已有 18 部作品八語齊備'}
    for slug in ('',*SLUGS):
        p=ROOT/'essays/film'/slug/'zh-hant-data/index.js';s=p.read_text()
        m=re.search(r'var variants\s*=\s*(\{.*?\});',s,re.S);assert m,p
        values=json.loads(m[1]);values.update(additions)
        result[p]=s[:m.start(1)]+json.dumps(values,ensure_ascii=False,sort_keys=True)+s[m.end(1):]
    result.update(approved_traditional_outputs())
    return result


def approved_changes(slug,episode=None):
    """Only the independently recorded changes approved on 2026-11-08."""
    import json
    path=DATA/'review'/f'{slug}-approved-changes.json'
    if not path.exists():return []
    changes=json.loads(path.read_text())['changes']
    return [c for c in changes if episode is None or c['episode']==episode]


def inline_chinese(text):
    """Match the existing Chinese publisher's inline escaping exactly."""
    text=html.escape(text,quote=True)
    text=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',text)
    return re.sub(r'\*(.+?)\*',r'<em>\1</em>',text)


def revised_chinese_body(body,slug,episode):
    for change in approved_changes(slug,episode):
        before=inline_chinese(change['zh_before']);after=inline_chinese(change['zh_after'])
        if before==after:continue
        if before in body:
            assert body.count(before)==1,(slug,episode,before)
            body=body.replace(before,after,1)
        else:assert after in body,(slug,episode,'missing approved source or result')
    return body


def approved_traditional_outputs():
    """Apply frozen approved dictionary deltas on any build platform."""
    import json
    path=DATA/'review/approved-traditional.json'
    if not path.exists():return {}
    result={}
    for relative,patch in json.loads(path.read_text())['files'].items():
        p=ROOT/relative;s=p.read_text();m=re.search(r'var variants\s*=\s*(\{.*?\});',s,re.S);assert m,p
        values=json.loads(m[1])
        for key in patch['removed']:values.pop(key,None)
        values.update(patch['added'])
        result[p]=s[:m.start(1)]+json.dumps(values,ensure_ascii=False,sort_keys=True)+s[m.end(1):]
    return result
