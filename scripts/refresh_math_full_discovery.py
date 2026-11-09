#!/usr/bin/env python3
"""Refresh only Mathematics discovery records and the latest homepage digest."""
import argparse,html,json,re,xml.etree.ElementTree as ET
from unittest.mock import patch
import build_search_index as search
from build_sitemap import parse_page,sitemap_xml
from build_home_updates import render_home
from build_math_history_full_editions import ROOT,SERIES,DATE,LANGS,read
ID=DATE+'-math-complete'
UPDATE={'id':ID,'date':DATE,'kind':'expanded','domain':'history','series_key':'essays/math-history','url':'essays/math-history/index.html','languages':['en','zh','zh-hant',*LANGS],
 'title':{'en':'Mathematics · 25 Complete Essays in Eight Languages','zh':'数学史：25篇八语完整阅读','zh-hant':'數學史：25篇八語完整閱讀'},
 'summary':{'en':'German, French, Spanish, Japanese and Korean full editions join the existing English and Chinese editions, with localized contents, sources and reading routes.','zh':'新增德、法、西、日、韩五语全文，与原有中英版本衔接，配套本地化目录、史料与阅读导航。','zh-hant':'新增德、法、西、日、韓五語全文，與原有中英版本銜接，配套本地化目錄、史料與閱讀導覽。'}}

START='<!-- MATH COMPLETE LATEST START -->';END='<!-- MATH COMPLETE LATEST END -->'
def latest_card():
 title=''.join(f'<h3 class="lang-{css}">{html.escape(UPDATE["title"][lang])}</h3>' for lang,css in [('en','en'),('zh','zh'),('zh-hant','hant')]);summary=''.join(f'<p class="lang-{css}">{html.escape(UPDATE["summary"][lang])}</p>' for lang,css in [('en','en'),('zh','zh'),('zh-hant','hant')])
 return START+f'<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-math-complete"><header class="updates-date"><h2 id="date-math-complete"><time datetime="{DATE}">{DATE}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{ID}"><div class="update-meta"><span class="update-kind"><span class="lang-en">Expanded</span><span class="lang-zh">拓展</span><span class="lang-hant">拓展</span></span><span>简 · 繁 · EN · DE · FR · ES · 日本語 · 한국어</span></div>{title}{summary}<a href="essays/math-history/index.html"><span class="lang-en">Read the series →</span><span class="lang-zh">进入系列 →</span><span class="lang-hant">進入系列 →</span></a></article></div></section></div></section>'+END

def hub_outputs():
 result={}
 for lang in LANGS:
  ui=read(ROOT/'data/math-history-full'/lang/'ui.json');p=ROOT/'essays'/lang/'index.html';s=p.read_text()
  start='<!-- MATH FULL HUB START -->';end='<!-- MATH FULL HUB END -->'
  card=start+f'<a class="essay-card" href="../math-history/{lang}/index.html" style="display:block;padding:2rem;border-left:3px solid var(--gold)"><h3>{html.escape(ui["series_title"])}</h3><p>{html.escape(ui["deck"])}</p><p>{html.escape(ui["status"])}</p></a>'+end
  if start in s:s=re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda m:card,s,flags=re.S)
  else:
   marker='<!-- sae-bridges-language-hub-cards -->';assert marker in s;s=s.replace(marker,marker+card)
  result[p]=s
 return result

def library_outputs():
 p=ROOT/'library.html';s=p.read_text()
 pattern=r'<a href="essays/math-history/index\.html" class="series-card series-card-flagship">.*?</a>'
 matches=list(re.finditer(pattern,s,re.S));assert len(matches)==1,'Expected one Mathematics library card'
 old=matches[0].group();new=old
 for before,after in [('A new flagship · EN / 简 / 繁','25 essays · Eight languages'),('数学史新旗舰 · 英 / 简 / 繁','25篇 · 八语全文'),('數學史新旗艦 · 英 / 簡 / 繁','25篇 · 八語全文')]:
  if before in new:assert new.count(before)==1;new=new.replace(before,after)
  else:assert after in new,('Unexpected Mathematics library copy',before)
 return {p:s.replace(old,new,1)}

def discovery():
 from build_math_history_full_editions import render
 for page,expected in render().items():
  assert page.exists() and page.read_text()==expected,("Build accepted mathematics pages before discovery",page)
 result=hub_outputs();result.update(library_outputs());p=ROOT/'data/site-updates.json';ledger=read(p);ledger['updates']=[UPDATE if u['id']==ID else u for u in ledger['updates']] if any(u['id']==ID for u in ledger['updates']) else [UPDATE]+ledger['updates'];result[p]=json.dumps(ledger,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'latest.html';s=p.read_text();card=latest_card()
 if START in s:s=re.sub(re.escape(START)+r'.*?'+re.escape(END),lambda m:card,s,flags=re.S)
 else:
  at=re.search(r'(?:<!--[^>]*-->\s*)?<section class="updates-section">',s);assert at;s=s[:at.start()]+card+'\n'+s[at.start():]
 result[p]=s
 p=ROOT/'sitemap.xml';ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';entries={u.find(ns+'loc').text:u.find(ns+'lastmod').text for u in ET.parse(p).getroot()}
 for page in list(SERIES.rglob('*.html'))+[ROOT/'essays'/lang/'index.html' for lang in LANGS]+[ROOT/'index.html',ROOT/'latest.html',ROOT/'library.html']:
  canonical=parse_page(page).canonical;assert canonical.startswith('https://nondubito.net/');entries[canonical]=max(entries.get(canonical,DATE),DATE)
 result[p]=sitemap_xml(sorted(entries.items(),key=lambda x:(x[0]!='https://nondubito.net/',x[0])))
 return result

def search_outputs():
 paths=list(SERIES.rglob('*.html'))+[ROOT/'essays'/lang/'index.html' for lang in LANGS]+[ROOT/'index.html',ROOT/'latest.html',ROOT/'library.html'];scope={str(p.relative_to(ROOT)) for p in paths};result={}
 with patch.object(search,'collect_pages',lambda:paths):_,fresh=search.build()
 manifest=read(search.OUTPUT);unique=set()
 for lang,records in fresh.items():
  p=search.CHUNKS_DIR/f'{lang.lower()}.json';chunk=read(p);new={r['u']:r for r in records}
  chunk['records']=[new.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']];chunk['records'].extend(new.values());result[p]=search.serialized(chunk);manifest['languages'][lang]['count']=len(chunk['records']);unique.update(r['u'] for r in chunk['records'])
 manifest['record_count']=len(unique);result[search.OUTPUT]=search.serialized(manifest);return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 for p,s in discovery().items():
  if args.check:assert p.read_text()==s,('Stale Mathematics discovery',p)
  else:p.write_text(s)
 p=ROOT/'index.html';s=render_home()
 if args.check:assert p.read_text()==s,'Stale home digest'
 else:p.write_text(s)
 for p,s in search_outputs().items():
  if args.check:assert p.read_text()==s,('Stale scoped search',p)
  else:p.write_text(s)
 print(('Verified' if args.check else 'Refreshed')+' Mathematics discovery, scoped search, homepage and sitemap dates')
if __name__=='__main__':main()
