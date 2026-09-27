#!/usr/bin/env python3
"""Render the reviewed EP01 full manuscripts into stable Eurasian-series URLs.

No translation or rewriting happens here. Only EP01 is opted in. The bilingual
URL remains bilingual; Traditional Chinese has its own page. Existing EP02–22
are not regenerated. Source receipts guard against accidental manuscript drift.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
import markdown
from build_emperor_full_editions import replace_div

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/ouya-full'
SERIES = ROOT / 'essays/ouya'
LANGS = ('zh-Hans', 'zh-Hant', 'en', 'ja', 'fr', 'de', 'es', 'ko')
NAMES = {'zh-Hans':'简体中文','zh-Hant':'繁體中文','en':'English','ja':'日本語','fr':'Français','de':'Deutsch','es':'Español','ko':'한국어'}
COUNTS = dict(zip(LANGS, (122,122,132,121,135,134,120,121)))
DECKS = {
 'zh-Hans':'雅典把公民理解为参与权，斯巴达把公民理解为必须维持的成员身份。两条船、一次审判和一场远征，照见两种秩序的代价。',
 'zh-Hant':'雅典把公民理解為參與權，斯巴達把公民理解為必須維持的成員身份。兩條船、一次審判和一場遠征，照見兩種秩序的代價。',
 'en':'Athens centred citizenship on participation, Sparta on membership to be maintained. Two ships, a trial, and an expedition reveal the costs of both orders.',
 'ja':'参加を核にしたアテナイと、成員であり続けることを求めたスパルタ。二隻の船、裁判、遠征から、二つの秩序の代価をたどる。',
 'fr':"Participer à Athènes, conserver sa place à Sparte : deux navires, un procès et une expédition éclairent le prix de ces deux ordres politiques.",
 'de':'In Athen zählt die Teilnahme, in Sparta die fortdauernde Zugehörigkeit. Zwei Schiffe, ein Prozess und eine Expedition zeigen die Kosten beider Ordnungen.',
 'es':'Atenas sitúa la participación en el centro; Esparta exige conservar la pertenencia. Dos barcos, un juicio y una expedición muestran el precio de ambos órdenes.',
 'ko':'참여를 중심에 놓은 아테네와 성원 자격을 계속 유지하도록 요구한 스파르타. 두 척의 배, 재판, 원정이 두 질서의 대가를 비춘다.'
}
NOTES = {
 'zh-Hans':('史料与阅读','本文借“构、余项、人是目的”对读历史，不把这些词当作古人的自述。古代记载、人口估计和后世解释各有边界；不同制度阶段不能拼成一套永远不变的规则。'),
 'zh-Hant':('史料與閱讀','本文借「構、餘項、人是目的」對讀歷史，不把這些詞當作古人的自述。古代記載、人口估計和後世解釋各有邊界；不同制度階段不能拼成一套永遠不變的規則。'),
 'en':('Sources and reading','Construct, remainder, and the person as an end are the interpretive vocabulary of this essay, not the ancient actors’ own terms. Ancient accounts, population estimates, and later interpretations have different limits; successive institutional arrangements are not one timeless rulebook.'),
 'ja':('史料と読書','構、余項、人間は目的であるという言葉は、本篇が歴史を読むための言葉であり、古代の人々自身の表現ではない。古代の記録、人口推計、後世の解釈にはそれぞれ限界があり、異なる時期の制度を一つの不変の規則にはできない。'),
 'fr':('Sources et lectures',"Construction, reste et personne comme fin sont les termes de lecture de cet essai, non ceux des acteurs antiques. Récits anciens, estimations démographiques et interprétations ultérieures ont des limites différentes ; les institutions de plusieurs époques ne forment pas un règlement immuable."),
 'de':('Quellen und Lektüre','Gefüge, Rest und Mensch als Zweck sind die Deutungsbegriffe dieses Essays, nicht die eigenen Begriffe der antiken Handelnden. Antike Berichte, Bevölkerungsschätzungen und spätere Deutungen haben unterschiedliche Grenzen; Einrichtungen verschiedener Epochen bilden kein zeitloses Regelwerk.'),
 'es':('Fuentes y lecturas','Construcción, resto y persona como fin son los términos de lectura de este ensayo, no las palabras de los actores antiguos. Los relatos, las estimaciones de población y las interpretaciones posteriores tienen límites distintos; las instituciones de diferentes épocas no forman un reglamento inmutable.'),
 'ko':('사료와 읽기','구성체, 잔여, 인간은 목적이라는 말은 이 글이 역사를 읽는 언어이지 고대인의 자기 진술이 아니다. 고대 기록, 인구 추계, 후대의 해석에는 서로 다른 한계가 있다. 여러 시기의 제도를 하나의 변하지 않는 규칙으로 합칠 수는 없다.')
}
SOURCES = [
 ('Aristotle · Athenian Constitution 41–43','https://classics.mit.edu/Aristotle/athenian_const.2.2.html'),
 ('Aristotle · Politics II.9','https://classics.mit.edu/Aristotle/politics.2.two.html'),
 ('Plutarch · Lycurgus 15','https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Lycurgus*.html'),
 ('Plato · Apology','https://classics.mit.edu/Plato/apology.html'),
 ('Thucydides · VI.8–26','https://classics.mit.edu/Thucydides/pelopwar.6.sixth.html'),
 ('Thucydides · V.34','https://classics.mit.edu/Thucydides/pelopwar.5.fifth.html'),
 ('Thucydides · History (IV.80; VII.86–87)','https://www.gutenberg.org/files/7142/7142-h/7142-h.htm'),
 ('Strabo · Geography VIII.5.4','https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Strabo/8E*.html'),
 ('Sophocles · Antigone','https://classics.mit.edu/Sophocles/antigone.html'),
 ('Kant · Groundwork, humanity formula','https://www.gutenberg.org/files/5682/5682-h/5682-h.htm')
]
STYLE = '''<style id="ouya-full-style">
.ouya-full p{line-height:1.9;overflow-wrap:anywhere}
.ouya-full h2{margin-top:2.5em;line-height:1.4;scroll-margin-top:110px}
.ouya-sources{margin-top:3rem;padding-top:1.5rem;border-top:1px solid var(--cream-border);font-size:.88rem}
.ouya-sources h2{font-size:1.1rem}.ouya-sources ul{padding-left:1.25em;overflow-wrap:anywhere}
.ouya-series-back{display:block;margin:1.5rem 0;font-size:.85rem;color:var(--ink-muted)}
</style>'''
STATE_SCRIPT = '''<script id="ouya-inline-language">
(function(){
 var q=new URLSearchParams(location.search).get('lang'), saved='zh';
 try {saved=localStorage.getItem('nd_lang')||'zh';} catch(e){}
 var lang=q==='en'||q==='zh'?q:(saved==='en'?'en':'zh');
 document.documentElement.setAttribute('data-lang',lang);
 document.documentElement.lang=lang==='en'?'en':'zh-Hans';
 try {localStorage.setItem('nd_lang',lang);} catch(e){}
 document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('.lang-btn[data-lang]').forEach(function(b){
   b.classList.toggle('active',b.dataset.lang===lang);
   b.addEventListener('click',function(){
    document.documentElement.setAttribute('data-lang',b.dataset.lang);
    document.documentElement.lang=b.dataset.lang==='en'?'en':'zh-Hans';
    try {localStorage.setItem('nd_lang',b.dataset.lang);} catch(e){}
   });
  });
 });
})();
</script>'''

def manuscripts():
    receipt=json.loads((DATA/'ep01-review.json').read_text())
    result={}
    for lang in LANGS:
        raw=(DATA/f'ep01.{lang}.md').read_text()
        assert hashlib.sha256(raw.encode()).hexdigest()==receipt['published_sha256'][lang],lang
        blocks=raw.strip().split('\n\n')
        assert blocks[0].startswith('# ') and blocks[1].startswith('Han Qin')
        body='\n\n'.join(blocks[2:])
        assert len(re.findall(r'^## ',body,re.M))==7
        assert len([p for p in blocks[2:] if not p.startswith('## ')])==COUNTS[lang]
        result[lang]={'title':blocks[0][2:], 'body':body}
    return result

def body_html(lang,copy):
    text=markdown.markdown(copy['body'])
    n=iter(range(1,8))
    text=re.sub(r'<h2>',lambda _:f'<h2 id="{lang.lower()}-section-{next(n)}">',text)
    label,note=NOTES[lang]
    links='\n'.join(f'<li><a href="{html.escape(u,quote=True)}">{html.escape(t)}</a></li>' for t,u in SOURCES)
    return f'<div class="ouya-full" data-edition="v0.1.3-local-20260927">\n{text}\n</div>\n<aside class="ouya-sources"><h2>{html.escape(label)}</h2><p>{html.escape(note)}</p><ul>{links}</ul></aside>'

def language_menu(lang):
    links=[]
    for code in ('en','zh-Hans','zh-Hant','ja','fr','de','es','ko'):
        if lang=='root' and code in ('zh-Hans','en'):
            links.append(f'<button class="lang-btn" data-lang="{"zh" if code=="zh-Hans" else "en"}">{NAMES[code]}</button>')
        elif code==lang:
            links.append(f'<span class="lang-btn active" aria-current="page">{NAMES[code]}</span>')
        else:
            href=('' if lang=='root' else '../')
            if code in ('en','zh-Hans'):href+='ep01.html?lang='+('zh' if code=='zh-Hans' else 'en')
            else:href+=code.lower()+'/ep01.html'
            links.append(f'<a class="lang-btn" href="{href}">{NAMES[code]}</a>')
    return '<div class="lang-toggle">\n'+'\n<span class="lang-sep">|</span>\n'.join(links)+'\n</div>'

def metadata(s,title,desc,url):
    s=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+' — Non Dubito</title>',s,flags=re.S)
    s=re.sub(r'<meta (?:name="description"|property="og:description") content="[^"]*">',lambda m:('<meta name="description"' if 'name=' in m[0] else '<meta property="og:description"')+' content="'+html.escape(desc,quote=True)+'">',s)
    s=re.sub(r'<meta property="og:title" content="[^"]*">','<meta property="og:title" content="'+html.escape(title,quote=True)+' — Non Dubito">',s)
    return re.sub(r'<link rel="canonical" href="[^"]*">',f'<link rel="canonical" href="{url}">',s)

def resources(s,prefix):
    s=re.sub(r'<style id="ouya-full-style">.*?</style>\s*','',s,flags=re.S)
    s=re.sub(r'<script[^>]*src="[^"]*language-select\.js[^"]*"[^>]*></script>\s*','',s)
    return s.replace('</head>',STYLE+f'\n<script defer src="{prefix}language-select.js"></script>\n</head>')

def outputs():
    copies=manuscripts();out={}
    root=SERIES/'ep01.html';s=root.read_text()
    for code,lang in [('zh','zh-Hans'),('en','en')]:
        s=replace_div(s,'essay-body lang-'+code,body_html(lang,copies[lang]))
        s=re.sub(r'(<h1 class="lang-'+code+r'">).*?(</h1>)',lambda m:m[1]+html.escape(copies[lang]['title'])+m[2],s,flags=re.S)
    s=re.sub(r'<div class="lang-toggle">.*?</div>',language_menu('root'),s,flags=re.S)
    s=re.sub(r'<script(?: id="ouya-inline-language")?>.*?</script>',lambda m:STATE_SCRIPT if ('var saved' in m[0] or 'ouya-inline-language' in m[0]) else m[0],s,flags=re.S)
    s=metadata(s,copies['zh-Hans']['title'],DECKS['zh-Hans'],'https://nondubito.net/essays/ouya/ep01.html')
    out[root]=resources(s,'../../')
    for lang in ('ja','fr','de','es','ko','zh-Hant'):
        p=SERIES/lang.lower()/'ep01.html'
        s=p.read_text() if p.exists() else (SERIES/'ja/ep01.html').read_text()
        s=replace_div(s,'essay-body',body_html(lang,copies[lang]))
        s=re.sub(r'<html lang="[^"]*">',f'<html lang="{lang}">',s)
        s=re.sub(r'<div class="lang-toggle">.*?</div>',language_menu(lang),s,flags=re.S)
        s=re.sub(r'(<h1\b[^>]*>).*?(</h1>)',lambda m:m[1]+html.escape(copies[lang]['title'])+m[2],s,count=1,flags=re.S)
        s=re.sub(r'<p class="essay-subtitle">.*?</p>\s*','',s,flags=re.S)
        s=re.sub(r'<a class="ouya-series-back".*?</a>\s*','',s,flags=re.S)
        label={'ja':'← シリーズ目次','fr':'← Tous les essais','de':'← Zur Reihe','es':'← Índice de la serie','ko':'← 시리즈 목차','zh-Hant':'← 系列目錄（簡體／English）'}[lang]
        href='index.html' if lang!='zh-Hant' else '../index.html'
        onclick='' if lang!='zh-Hant' else ' onclick="localStorage.setItem(\'nd_lang\',\'zh\')"'
        s=s.replace('<header class="essay-header">',f'<a class="ouya-series-back" href="{href}"{onclick}>{label}</a>\n<header class="essay-header">',1)
        if lang=='zh-Hant':
            s=re.sub(r'<div class="essay-series-label">.*?</div>','<div class="essay-series-label">鑿構週期律 · 歐亞帝王系列 — 第01篇／共22篇</div>',s)
            s=re.sub(r'<span class="xiyou-nav-sub">.*?</span>','<span class="xiyou-nav-sub">下一篇（簡體）</span>',s)
            s=re.sub(r'<span class="xiyou-nav-title">.*?</span>','<span class="xiyou-nav-title">亞歷山大與希臘化</span>',s)
            s=re.sub(r'<a href="(?:\.\./)?ep02.html"', '<a href="../ep02.html" onclick="localStorage.setItem(\'nd_lang\',\'zh\')"',s)
            # Prevent duplicate onclick attributes after repeat builds.
            s=s.replace(' onclick="localStorage.setItem(\'nd_lang\',\'zh\')" onclick="localStorage.setItem(\'nd_lang\',\'zh\')"',' onclick="localStorage.setItem(\'nd_lang\',\'zh\')"')
        s=metadata(s,copies[lang]['title'],DECKS[lang],f'https://nondubito.net/essays/ouya/{lang.lower()}/ep01.html')
        out[p]=resources(s,'../../../')
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result=outputs();stale=[]
    for path,s in result.items():
        if args.check:
            if not path.exists() or path.read_text()!=s:stale.append(str(path.relative_to(ROOT)))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(s)
    if stale:raise SystemExit('Stale EP01 pages: '+', '.join(stale))
    print(('OK' if args.check else 'Wrote')+': 7 EP01 URLs, 8 complete language editions')
if __name__=='__main__':main()
