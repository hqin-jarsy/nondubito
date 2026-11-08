#!/usr/bin/env python3
"""Scoped, repeatable discovery refresh for the complete Analects editions."""
import argparse
import html
import json
import re
from pathlib import Path
import build_analects_full_editions as b
import build_search_index as search
from build_home_updates import render_home

DATE='2026-11-08'
ID=DATE+'-analects-complete-editions'
UPDATE={
 'id':ID,'date':DATE,'kind':'expanded','domain':'literature','url':'essays/analects/index.html',
 'languages':['zh','zh-hant','en','de','fr','es','ja','ko'],
 'title':{'en':'The Analects, Reopened · Fifty Complete Essays','zh':'大知解论语：五十篇八语全文','zh-hant':'大知解論語：五十篇八語全文'},
 'summary':{
  'en':'All fifty English essays now follow the complete Chinese texts. The existing revised German, French, Spanish, Japanese and Korean manuscripts replace the shorter web editions. Scenes, arguments, quotations and source notes remain together; documented minor factual corrections are synchronized across editions.',
  'zh':'五十篇英文按完整中文补齐，德、法、西、日、韩则整合既有修订全文，替换网站旧短版。保留场景、论证、引文与出处，明确的小错逐项记录并同步各语。',
  'zh-hant':'五十篇英文按完整中文補齊，德、法、西、日、韓則整合既有修訂全文，替換網站舊短版。保留場景、論證、引文與出處，明確的小錯逐項記錄並同步各語。'}
}
START='<!-- ANALECTS COMPLETE LATEST START -->'
END='<!-- ANALECTS COMPLETE LATEST END -->'
TAGS={'de':'Vollständige Reihe · 50 Essays','fr':'Série intégrale · 50 essais','es':'Serie completa · 50 ensayos','ja':'全50篇・全文版','ko':'전50편·전문판'}


def latest_card():
    title=''.join(f'<h3 class="lang-{code}">{html.escape(UPDATE["title"][lang])}</h3>' for lang,code in [('en','en'),('zh','zh'),('zh-hant','hant')])
    summary=''.join(f'<p class="lang-{code}">{html.escape(UPDATE["summary"][lang])}</p>' for lang,code in [('en','en'),('zh','zh'),('zh-hant','hant')])
    return START+f'<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-analects-complete"><header class="updates-date"><h2 id="date-analects-complete"><time datetime="{DATE}">{DATE}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{ID}"><div class="update-meta"><span class="update-kind"><span class="lang-en">Complete editions</span><span class="lang-zh">全文整合</span><span class="lang-hant">全文整合</span></span><span>简 · 繁 · EN · DE · FR · ES · 日本語 · 한국어</span></div>{title}{summary}<a href="essays/analects/index.html"><span class="lang-en">Read the series →</span><span class="lang-zh">进入系列 →</span><span class="lang-hant">進入系列 →</span></a></article></div></section></div></section>'+END


def render():
    outputs={}
    path=b.ROOT/'data/site-updates.json';ledger=b.read_json(path)
    ledger['updates']=[UPDATE]+[u for u in ledger['updates'] if u['id']!=ID]
    outputs[path]=json.dumps(ledger,ensure_ascii=False,indent=2)+'\n'
    path=b.ROOT/'latest.html';text=path.read_text();card=latest_card()
    if START in text:
        text=re.sub(re.escape(START)+r'.*?'+re.escape(END),lambda _:card,text,flags=re.S)
    else:
        at=re.search(r'(?:<!--[^>]*-->\s*)?<section class="updates-section">',text)
        assert at
        text=text[:at.start()]+card+'\n'+text[at.start():]
    outputs[path]=text
    path=b.ROOT/'library.html';text=path.read_text();m=re.search(r'<a href="essays/analects/index.html" class="series-card">.*?</a>',text,re.S);assert m
    card=m[0].replace('50 essays · 8 languages','50 complete essays · 8 languages').replace('50 篇 · 8 种语言','50 篇全文 · 8 种语言').replace('50 篇 · 8 種語言','50 篇全文 · 8 種語言')
    outputs[path]=text[:m.start()]+card+text[m.end():]
    from build_analects_languages import UI
    for lang,tag in TAGS.items():
        path=b.ROOT/f'essays/{lang}/index.html';text=path.read_text();m=re.search(r'<!-- ANALECTS LANGUAGE HUB START -->.*?<!-- ANALECTS LANGUAGE HUB END -->',text,re.S);assert m
        card=m[0].replace(html.escape(UI[lang]['channel_tag']),html.escape(tag))
        outputs[path]=text[:m.start()]+card+text[m.end():]
    return outputs


def refresh_search(paths):
    scope={str(p.relative_to(b.ROOT)) for p in paths}
    original=search.collect_pages
    try:
        search.collect_pages=lambda:paths
        _,fresh=search.build()
    finally:search.collect_pages=original
    manifest=json.loads(search.OUTPUT.read_text())
    unique_urls=set()
    for lang,replacements in fresh.items():
        path=search.CHUNKS_DIR/f'{lang.lower()}.json';chunk=json.loads(path.read_text());by_url={r['u']:r for r in replacements}
        chunk['records']=[by_url.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']]
        chunk['records'].extend(by_url.values());path.write_text(search.serialized(chunk))
        manifest['languages'][lang]['count']=len(chunk['records'])
        unique_urls.update(r['u'] for r in chunk['records'])
    manifest['record_count']=len(unique_urls)
    search.OUTPUT.write_text(search.serialized(manifest))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    outputs=render()
    if args.check:
        stale=[str(p.relative_to(b.ROOT)) for p,t in outputs.items() if p.read_text()!=t]
        if stale:raise SystemExit('Stale Analects discovery: '+', '.join(stale))
        print('OK: Analects ledger, Latest, library and five language hubs');return
    for path,text in outputs.items():path.write_text(text)
    home=b.ROOT/'index.html';home.write_text(render_home())
    paths=list(b.render())+[p for p in outputs if p.suffix=='.html' and p.name!='latest.html']+[home]
    refresh_search(paths)
    print('Refreshed complete Analects discovery without replacing unrelated search records')

if __name__=='__main__':main()
