#!/usr/bin/env python3
"""Publish the author's unchanged Socrates manuscript, not a historical essay."""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from build_home_updates import render_home
from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/originals/socrates'
TARGET = ROOT / 'originals/short-stories'
DATE = '2026-11-23'
SOURCE_SHA = '6c5f8e9169248abd9ab248db3ee5b8515c752b034bbf1ed8dff898a02e622d5d'
UPDATE_ID = DATE + '-socrates-original'
EDITION = {'zh': ('', 'zh-Hans', '中文'), 'zh-hant': ('zh-hant/', 'zh-Hant', '繁體中文')}
COPY = {
    'zh': {'title':'苏格拉底', 'shelf':'短篇小说', 'originals':'原创作品', 'read':'阅读小说',
           'deck':'雅典的一家酒馆里，众人谈论城邦大事。一个伙计记下了苏格拉底来去的日子。',
           'intro':'秦汉的原创短篇。故事从人物的言语、动作与选择里展开，不另附解读。',
           'kind':'秦汉原创 · 短篇小说', 'edition':'中文原作',
           'note':'文学虚构，非历史实录。',
           'nav':('从这里开始','探索','最近更新','关于','搜索','菜单')},
    'zh-hant': {'title':'蘇格拉底', 'shelf':'短篇小說', 'originals':'原創作品', 'read':'閱讀小說',
           'deck':'雅典的一家酒館裡，眾人談論城邦大事。一個夥計記下了蘇格拉底來去的日子。',
           'intro':'秦漢的原創短篇。故事從人物的言語、動作與選擇裡展開，不另附解讀。',
           'kind':'秦漢原創 · 短篇小說', 'edition':'繁體閱讀版',
           'note':'文學虛構，非歷史實錄。',
           'nav':('從這裡開始','探索','最近更新','關於','搜尋','選單')},
}

def esc(value):
    return html.escape(str(value), quote=True)

def manuscript(lang):
    meta = json.loads((DATA/'publication.json').read_text())
    raw = (DATA/('zh.txt' if lang=='zh' else 'zh-hant.txt')).read_bytes()
    expected = SOURCE_SHA if lang=='zh' else meta['traditional_sha256']
    assert hashlib.sha256(raw).hexdigest()==expected, 'Manuscript changed: author approval required'
    assert meta['source_sha256']==SOURCE_SHA
    paragraphs = raw.decode().strip().split('\n\n')
    assert len(paragraphs)==meta['paragraphs']==66
    return paragraphs

def url(lang, filename):
    return 'https://nondubito.net/originals/short-stories/'+EDITION[lang][0]+('' if filename=='index.html' else filename)

def shell(lang, filename):
    prefix = '../../../' if lang=='zh-hant' else '../../'
    c = COPY[lang]
    nav = ''.join(f'<a href="{prefix}{path}?lang={lang}">{label}</a>'
                  for path,label in zip(('start.html','explore.html','latest.html','about.html'),c['nav']))
    editions = ''.join(f'<a href="{"../" if lang=="zh-hant" else ""}{directory}{filename}" lang="{code}"'
                       + (' aria-current="page"' if mode==lang else '')+f'>{label}</a>'
                       for mode,(directory,code,label) in EDITION.items())
    return f'''<header class="site-shell-header"><div class="header-inner"><a href="{prefix}index.html?lang={lang}" class="site-title" aria-label="Non Dubito"><span class="title-latin">Non <span>Dubito</span></span><span class="title-sub">A Mind in Many Languages</span></a><nav class="site-shell-nav" aria-label="主导航">{nav}</nav><div class="site-shell-tools"><a class="site-shell-tool" href="{prefix}search.html?lang={lang}">{c['nav'][4]}</a><details class="site-shell-language"><summary class="site-shell-language-summary">{EDITION[lang][2]} <span aria-hidden="true">⌄</span></summary><div class="site-shell-language-options">{editions}</div></details><button class="site-shell-menu-button" type="button" data-short-fiction-menu aria-controls="site-shell-drawer" aria-expanded="false">{c['nav'][5]} ☰</button></div></div></header><div class="site-shell-drawer" id="site-shell-drawer"><nav aria-label="移动导航">{nav}<a href="{prefix}originals/index.html?lang={lang}">{c['originals']}</a></nav><div class="site-shell-mobile-languages">{editions}</div></div>'''

MENU_JS = '''document.addEventListener('DOMContentLoaded',function(){var b=document.querySelector('[data-short-fiction-menu]'),d=document.getElementById('site-shell-drawer'),l=document.querySelector('.site-shell-language');function close(){d.classList.remove('open');b.setAttribute('aria-expanded','false');}b.addEventListener('click',function(){b.setAttribute('aria-expanded',String(d.classList.toggle('open')));});d.querySelectorAll('a').forEach(function(a){a.addEventListener('click',close);});document.addEventListener('keydown',function(e){if(e.key==='Escape'){close();l.open=false;}});document.addEventListener('click',function(e){if(l.open&&!l.contains(e.target))l.open=false;});});'''

def page(lang, filename):
    c = COPY[lang]; code=EDITION[lang][1]
    prefix = '../../../' if lang=='zh-hant' else '../../'
    css = 'cjk'+(' tc' if lang=='zh-hant' else '')
    suffix = 'hant' if lang=='zh-hant' else 'zh'
    title = c['shelf'] if filename=='index.html' else c['title']
    desc = c['intro'] if filename=='index.html' else c['deck']
    alternate=''.join(f'<link rel="alternate" hreflang="{v[1]}" href="{url(k,filename)}">' for k,v in EDITION.items())
    schema = {'@context':'https://schema.org','@type':'CollectionPage' if filename=='index.html' else 'CreativeWork',
              'name':title,'description':desc,'inLanguage':code,'url':url(lang,filename),
              'author':{'@type':'Person','name':'Han Qin (秦汉)'},'datePublished':DATE}
    if filename=='index.html':
        body=f'''<main class="shelf-wrap"><section class="shelf-intro"><a class="fiction-back" href="{prefix}originals/index.html?lang={lang}">← {c['originals']}</a><p class="fiction-kicker">Non Dubito · {c['originals']}</p><h1 class="{css} lang-{suffix}">{title}</h1><p>{desc}</p></section><a class="story-card" href="socrates.html" data-search="Socrates 苏格拉底 蘇格拉底"><span class="story-card-no">01</span><div><h2 class="{css}">{c['title']}</h2><p>{c['deck']}</p><span>{c['read']} →</span></div></a></main>'''
        schema['hasPart']={'@type':'CreativeWork','name':c['title'],'url':url(lang,'socrates.html')}
    else:
        schema.update(genre='Short fiction',isPartOf={'@type':'CollectionPage','name':c['shelf'],'url':url(lang,'index.html')})
        paragraphs='\n'.join('<p>'+html.escape(p,quote=False)+'</p>' for p in manuscript(lang))
        author='秦漢' if lang=='zh-hant' else '秦汉'
        body=f'''<main class="fiction-wrap"><section class="fiction-hero"><a class="fiction-back" href="index.html">← {c['shelf']}</a><p class="fiction-kicker">{c['kind']}</p><h1 class="fiction-title {css} lang-{suffix}">{title}</h1><div class="fiction-meta"><span>{author} · Han Qin</span><time datetime="{DATE}">2026 · 11 · 23</time><span>{c['edition']}</span></div></section><article class="fiction-body {css}" data-original-manuscript="{lang}">\n{paragraphs}\n</article><p class="fiction-note">{c['note']}</p></main>'''
    footer=f'<footer class="site-shell-footer"><div class="site-shell-footer-inner"><div class="site-shell-footer-mark">Non <span>Dubito</span></div><div class="site-shell-footer-links"><a href="{prefix}originals/index.html?lang={lang}">{c["originals"]}</a><a href="{prefix}library.html?lang={lang}">Library</a><a href="https://self-as-an-end.net">SAE Theory ↗</a></div></div></footer>'
    return f'''<!DOCTYPE html><html lang="{code}" data-lang="{lang}" data-editions="{lang}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{title} — Non Dubito</title><meta name="description" content="{esc(desc)}"><meta name="author" content="Han Qin (秦汉)"><meta property="og:type" content="{'website' if filename=='index.html' else 'article'}"><meta property="og:title" content="{title} — Non Dubito"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url(lang,filename)}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary"><link rel="canonical" href="{url(lang,filename)}">{alternate}<link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg"><link rel="stylesheet" href="{prefix}style.css"><link rel="stylesheet" href="{prefix}site-shell.css?v=20260905b"><link rel="stylesheet" href="{prefix}originals/short-science-fiction/merger-day.css?v=20260909"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;family=Noto+Serif+TC:wght@400;500;600&amp;display=swap" rel="stylesheet"></head><body class="site-shell-page explicit-hant">{shell(lang,filename)}{body}{footer}<script>{MENU_JS}</script><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></body></html>'''

def localized(values, tag='span', css=''):
    return ''.join(f'<{tag} class="lang-{s}{" "+css if css else ""}">{esc(values[k])}</{tag}>' for k,s in [('en','en'),('zh','zh'),('zh-hant','hant')])

TITLE={'en':'Socrates · An Original Short Story','zh':'《苏格拉底》：原创短篇','zh-hant':'《蘇格拉底》：原創短篇'}
SUMMARY={'en':'An Athenian tavern, its young waiter, and a man who keeps asking questions. Chinese original with a Traditional Chinese reading edition; no English translation yet.',
         'zh':COPY['zh']['deck']+'简体原文与繁体阅读版完整发布，保留作者定稿。',
         'zh-hant':COPY['zh-hant']['deck']+'簡體原文與繁體閱讀版完整發佈，保留作者定稿。'}

def supporting_pages():
    pages={}; p=ROOT/'originals/index.html';text=p.read_text()
    text=text.replace('Original fiction by Han Qin: short science fiction and an original continuation of Dream of the Red Chamber.','Original fiction by Han Qin: short science fiction, short stories, and an original continuation of Dream of the Red Chamber.')
    text=text.replace('The first shelf begins with short science fiction. Its questions arrive through rooms, gestures, technologies, and choices; the fiction is left to make its own argument.','Browse short science fiction, short stories, and an original continuation of Dream of the Red Chamber. The questions arise through the fiction itself.')
    text=text.replace('第一层书架从短篇科幻开始。问题从房间、动作、技术与选择里发生；小说不另附一套理论说明。','这里有短篇科幻、短篇小说与长篇续写。问题从人物、言语与选择里发生；小说不另附一套理论说明。')
    text=text.replace('第一層書架從短篇科幻開始。問題從房間、動作、技術與選擇裡發生；小說不另附一套理論說明。','這裡有短篇科幻、短篇小說與長篇續寫。問題從人物、言語與選擇裡發生；小說不另附一套理論說明。')
    old="var saved=localStorage.getItem('nd_lang')||localStorage.getItem('nondubito-lang')||'zh';"
    text=text.replace(old,"var saved=new URLSearchParams(window.location.search).get('lang')||localStorage.getItem('nd_lang')||localStorage.getItem('nondubito-lang')||'zh';")
    for lang,suffix in [('en','en'),('zh','zh'),('zh-hant','hant')]:
        marker='SHORT FICTION ORIGINALS '+suffix.upper()
        text=re.sub(r'<!-- '+marker+r' START -->.*?<!-- '+marker+r' END -->','',text,flags=re.S)
        start=text.index('<div class="essay-body lang-'+suffix+'"')
        end=text.find('<div class="essay-body lang-',start+1)
        if end==-1:end=text.index('<footer',start)
        pos=text.rfind('</a>',start,end)+4;assert pos>start
        target='short-stories/'+('zh-hant/' if lang=='zh-hant' else '')+'index.html'
        label='Short Fiction' if lang=='en' else COPY[lang]['shelf']
        tag='1 story · Simplified / Traditional Chinese' if lang=='en' else ('1 篇 · 简 / 繁' if lang=='zh' else '1 篇 · 簡 / 繁')
        desc='Socrates: an Athenian tavern and its young waiter. Chinese text; English translation not yet available.' if lang=='en' else '首篇《'+COPY[lang]['title']+'》。'+COPY[lang]['deck']
        card=f'<!-- {marker} START --><a href="{target}" class="essay-card" data-search="Socrates 苏格拉底 蘇格拉底 short fiction"><span class="card-num">03</span><div class="card-body"><div class="card-lang-tag">{tag}</div><div class="card-title-{"en" if lang=="en" else "zh"}">{label}</div><p class="card-desc">{desc}</p><div class="card-meta"><span class="card-badge full">{"Read in Chinese" if lang=="en" else COPY[lang]["read"]}</span></div></div></a><!-- {marker} END -->'
        text=text[:pos]+card+text[pos:]
    pages[p]=text
    p=ROOT/'library.html';text=p.read_text();marker='SHORT FICTION LIBRARY'
    text=re.sub(r'<!-- '+marker+r' START -->.*?<!-- '+marker+r' END -->\n?','',text,flags=re.S)
    start=text.index('<span class="lib-section-tag">Category 17</span>');end=text.index('</section>',start)
    pos=text.rfind('</div>',start,end);assert pos>start
    card=f'''<!-- {marker} START --><a href="originals/short-stories/index.html" class="series-card" data-search="Socrates 苏格拉底 蘇格拉底 short fiction"><span class="series-card-count">1 story · 简 / 繁</span><div class="series-card-title-en">Short Fiction</div><div class="series-card-title-zh cl-zh">短篇小说</div><div class="series-card-title-zh cl-hant">短篇小說</div><p class="series-card-desc-en lang-en">Socrates: an Athenian tavern and its young waiter. Complete Simplified and Traditional Chinese text; English translation not yet available.</p><p class="series-card-desc-zh lang-zh cl-zh">首篇《苏格拉底》。{COPY['zh']['deck']}</p><p class="series-card-desc-zh lang-zh cl-hant">首篇《蘇格拉底》。{COPY['zh-hant']['deck']}</p><span class="series-card-arrow lang-en">Read in Chinese →</span><span class="series-card-arrow lang-zh cl-zh">进入书架 →</span><span class="series-card-arrow lang-zh cl-hant">進入書架 →</span></a><!-- {marker} END -->\n'''
    card=card.replace('1 story · 简 / 繁',localized({'en':'1 story · Chinese text','zh':'1 篇 · 简 / 繁','zh-hant':'1 篇 · 簡 / 繁'}))
    pages[p]=text[:pos]+card+text[pos:]
    p=ROOT/'data/site-updates.json';ledger=json.loads(p.read_text())
    entry=dict(id=UPDATE_ID,date=DATE,kind='new',domain='stories',series_key='originals/short-stories',url='originals/short-stories/socrates.html',languages=['zh','zh-hant'],title=TITLE,summary=SUMMARY)
    ledger['updates']=[entry]+[v for v in ledger['updates'] if v['id']!=UPDATE_ID]
    pages[p]=json.dumps(ledger,ensure_ascii=False,indent=2)+'\n'
    p=ROOT/'latest.html';text=p.read_text();marker='SOCRATES ORIGINAL UPDATE'
    text=re.sub(r'<!-- '+marker+r' START -->.*?<!-- '+marker+r' END -->\n?','',text,flags=re.S)
    pos=text.index('<!--',text.index('<main class="site-shell-main">'))
    block=f'<!-- {marker} START --><section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-socrates-original"><header class="updates-date"><h2 id="date-socrates-original"><time datetime="{DATE}">{DATE}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{UPDATE_ID}"><div class="update-meta">'+localized({'en':'New original fiction','zh':'原创新作','zh-hant':'原創新作'})+'<span>简 / 繁</span></div>'+localized(TITLE,'h3')+localized(SUMMARY,'p')+'<a href="originals/short-stories/socrates.html">'+localized({'en':'Read in Chinese →','zh':'阅读小说 →','zh-hant':'閱讀小說 →'})+'</a></article></div></section></div></section><!-- '+marker+' END -->\n'
    pages[p]=text[:pos]+block+text[pos:]
    return pages

@tracked_html
def render():
    return {TARGET/EDITION[k][0]/filename:page(k,filename) for k in EDITION for filename in ('index.html','socrates.html')}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    outputs=render();outputs.update(supporting_pages())
    if a.check:
        assert all(path.is_file() and path.read_text()==text for path,text in outputs.items()),'Stale Socrates publication'
        assert (ROOT/'index.html').read_text()==render_home(),'Stale home updates'
    else:
        for path,text in outputs.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        (ROOT/'index.html').write_text(render_home())
    print(('Checked' if a.check else 'Published locally')+': Socrates,66 unchanged paragraphs, two complete Chinese editions')

if __name__=='__main__':main()
