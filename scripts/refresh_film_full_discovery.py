#!/usr/bin/env python3
"""Scoped, repeatable discovery refresh; preserve unrelated records and dates."""
import argparse
import html
import json
import re
import xml.etree.ElementTree as ET
from unittest.mock import patch
import build_search_index as search
from build_sitemap import parse_page,sitemap_xml
from build_film_full_editions import outputs,UI,LANGS,E,DATE,ROOT
import film_targeted_editions as targeted
from build_home_updates import render_home
ID=targeted.DATE+'-film-three-complete'
UPDATE={'id':ID,'date':targeted.DATE,'kind':'expanded','domain':'stories','series_key':'essays/film','url':'essays/film/index.html','languages':['en','zh','zh-hant',*LANGS],
 'title':{'en':'Three Films · Nine Essays in Eight Languages','zh':'三部电影：九篇八语全文','zh-hant':'三部電影：九篇八語全文'},
 'summary':{'en':'Raise the Red Lantern, Dead Poets Society and Parasite now have full-length English readings and reviewed German, French, Spanish, Japanese and Korean editions alongside the Chinese originals.','zh':'《大红灯笼高高挂》《死亡诗社》《寄生虫》补全英文九篇，并整合复核后的德、法、西、日、韩全文，与中文原作共同组成八语阅读。','zh-hant':'《大紅燈籠高高掛》《死亡詩社》《寄生蟲》補全英文九篇，並整合複核後的德、法、西、日、韓全文，與中文原作共同組成八語閱讀。'}}
START='<!-- FILM THREE LATEST START -->';END='<!-- FILM THREE LATEST END -->'

def latest_card():
 title=''.join(f'<h3 class="lang-{code}">{html.escape(UPDATE["title"][lang])}</h3>' for lang,code in [('en','en'),('zh','zh'),('zh-hant','hant')])
 summary=''.join(f'<p class="lang-{code}">{html.escape(UPDATE["summary"][lang])}</p>' for lang,code in [('en','en'),('zh','zh'),('zh-hant','hant')])
 return START+f'<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-film-three"><header class="updates-date"><h2 id="date-film-three"><time datetime="{targeted.DATE}">{targeted.DATE}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{ID}"><div class="update-meta"><span class="update-kind"><span class="lang-en">Expanded</span><span class="lang-zh">拓展</span><span class="lang-hant">拓展</span></span><span>简 · 繁 · EN · DE · FR · ES · 日本語 · 한국어</span></div>{title}{summary}<a href="essays/film/index.html"><span class="lang-en">Explore the films →</span><span class="lang-zh">进入电影书架 →</span><span class="lang-hant">進入電影書架 →</span></a></article></div></section></div></section>'+END

def render():
    result={};paths=list(outputs())
    for lang in LANGS:
        p=ROOT/'essays'/lang/'index.html';s=p.read_text();u=UI[lang]
        block=f'<!-- FILM FULL EDITIONS START --><section class="essays-section" style="padding:2rem 0"><a href="../film/{lang}/index.html" class="essay-card" style="display:block;text-decoration:none;border-left:3px solid var(--gold);padding:2rem"><h2 style="font-size:1.6rem;font-weight:400">{E(u["cinema"])}</h2><p>{E(u["intro"])}</p><p>{E(u["published"])}</p></a></section><!-- FILM FULL EDITIONS END -->'
        if '<!-- FILM FULL EDITIONS START -->' in s:s=re.sub(r'<!-- FILM FULL EDITIONS START -->.*?<!-- FILM FULL EDITIONS END -->',lambda m:block,s,flags=re.S)
        else:
            at=s.index('<section class="essays-section"');s=s[:at]+block+'\n'+s[at:]
        result[p]=s;paths.append(p)
    p=ROOT/'data/site-updates.json';ledger=json.loads(p.read_text());ledger['updates']=[UPDATE if u['id']==ID else u for u in ledger['updates']] if any(u['id']==ID for u in ledger['updates']) else [UPDATE]+ledger['updates'];result[p]=json.dumps(ledger,ensure_ascii=False,indent=2)+'\n'
    p=ROOT/'latest.html';s=p.read_text();card=latest_card()
    if START in s:s=re.sub(re.escape(START)+r'.*?'+re.escape(END),lambda m:card,s,flags=re.S)
    else:
        at=re.search(r'(?:<!--[^>]*-->\s*)?<section class="updates-section">',s);assert at;s=s[:at.start()]+card+'\n'+s[at.start():]
    result[p]=s
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';p=ROOT/'sitemap.xml'
    entries={u.find(ns+'loc').text:u.find(ns+'lastmod').text for u in ET.parse(p).getroot()}
    for page in paths+[ROOT/'latest.html',ROOT/'index.html']:
        if page.suffix!='.html':continue
        canonical=parse_page(page).canonical;assert canonical.startswith('https://nondubito.net/')
        if any('/'+slug+'/' in canonical for slug in targeted.SLUGS) or page.parent.name in LANGS and page.name=='index.html' and page.parent.parent in (ROOT/'essays',ROOT/'essays/film') or page in [ROOT/'essays/film/index.html',ROOT/'latest.html',ROOT/'index.html']:
            entries[canonical]=targeted.DATE
        elif canonical not in entries:entries[canonical]=DATE
    result[p]=sitemap_xml(sorted(entries.items(),key=lambda x:(x[0]!='https://nondubito.net/',x[0])))
    return result,paths

def search_outputs(paths):
    paths=[p for p in paths if p.suffix=='.html'];scope={str(p.relative_to(ROOT)) for p in paths};result={}
    with patch.object(search,'collect_pages',lambda:paths):_,fresh=search.build()
    manifest=json.loads(search.OUTPUT.read_text());unique=set()
    for lang,replacements in fresh.items():
        p=search.CHUNKS_DIR/f'{lang.lower()}.json';chunk=json.loads(p.read_text());by_url={r['u']:r for r in replacements}
        chunk['records']=[by_url.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']];chunk['records'].extend(by_url.values())
        result[p]=search.serialized(chunk);manifest['languages'][lang]['count']=len(chunk['records']);unique.update(r['u'] for r in chunk['records'])
    manifest['record_count']=len(unique);result[search.OUTPUT]=search.serialized(manifest)
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();result,paths=render()
    if args.check:
        assert all(p.read_text()==s for p,s in result.items()),'Stale film discovery'
        assert (ROOT/'index.html').read_text()==render_home(),'Stale homepage'
    else:
        for p,s in result.items():p.write_text(s)
        (ROOT/'index.html').write_text(render_home())
    for p,s in search_outputs(paths+[ROOT/'index.html',ROOT/'latest.html']).items():
        if args.check:assert p.read_text()==s,p
        else:p.write_text(s)
    print(('Verified' if args.check else 'Refreshed')+' film discovery, homepage, scoped search and recorded publication dates')
if __name__=='__main__':main()
