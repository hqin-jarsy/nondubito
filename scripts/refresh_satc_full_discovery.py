#!/usr/bin/env python3
"""Refresh only Sex and the City discovery records and the latest homepage digest."""
import argparse,html,json,re,xml.etree.ElementTree as ET
from unittest.mock import patch
import build_search_index as search
from build_sitemap import parse_page,sitemap_xml
from build_home_updates import render_home
from build_satc_full_editions import ROOT,SERIES,DATE,LANGS,read
ID=DATE+'-satc-complete'
UPDATE={'id':ID,'date':DATE,'kind':'expanded','domain':'tv','series_key':'essays/tv/sex-and-the-city','url':'essays/tv/sex-and-the-city/index.html','languages':['en','zh','zh-hant',*LANGS],
 'title':{'en':'Sex and the City · Ten Complete Readings','zh':'《欲望都市》：十篇八语完整阅读','zh-hant':'《慾望城市》：十篇八語完整閱讀'},
 'summary':{'en':'Ten English editions expanded and reviewed; German, French, Spanish, Japanese and Korean summaries replaced with full translations. Author-approved factual corrections are synchronized across all eight editions.','zh':'复核补充十篇英文，将德法西日韩摘要换为完整译文；作者认可的剧情事实修正同步八语，保留原有论点与行文节奏。','zh-hant':'複核補充十篇英文，將德法西日韓摘要換為完整譯文；作者認可的劇情事實修正同步八語，保留原有論點與行文節奏。'}}
START='<!-- SATC COMPLETE LATEST START -->';END='<!-- SATC COMPLETE LATEST END -->'
def latest_card():
 title=''.join(f'<h3 class="lang-{css}">{html.escape(UPDATE["title"][lang])}</h3>' for lang,css in [('en','en'),('zh','zh'),('zh-hant','hant')]);summary=''.join(f'<p class="lang-{css}">{html.escape(UPDATE["summary"][lang])}</p>' for lang,css in [('en','en'),('zh','zh'),('zh-hant','hant')])
 return START+f'<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-satc-complete"><header class="updates-date"><h2 id="date-satc-complete"><time datetime="{DATE}">{DATE}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{ID}"><div class="update-meta"><span class="update-kind"><span class="lang-en">Expanded</span><span class="lang-zh">拓展</span><span class="lang-hant">拓展</span></span><span>简 · 繁 · EN · DE · FR · ES · 日本語 · 한국어</span></div>{title}{summary}<a href="essays/tv/sex-and-the-city/index.html"><span class="lang-en">Read the series →</span><span class="lang-zh">进入系列 →</span><span class="lang-hant">進入系列 →</span></a></article></div></section></div></section>'+END

def discovery():
 result={};p=ROOT/'data/site-updates.json';ledger=read(p);ledger['updates']=[UPDATE if u['id']==ID else u for u in ledger['updates']] if any(u['id']==ID for u in ledger['updates']) else [UPDATE]+ledger['updates'];result[p]=json.dumps(ledger,ensure_ascii=False,indent=2)+'\n'
 p=ROOT/'latest.html';s=p.read_text();card=latest_card()
 if START in s:s=re.sub(re.escape(START)+r'.*?'+re.escape(END),lambda m:card,s,flags=re.S)
 else:
  at=re.search(r'(?:<!--[^>]*-->\s*)?<section class="updates-section">',s);assert at;s=s[:at.start()]+card+'\n'+s[at.start():]
 result[p]=s
 p=ROOT/'sitemap.xml';ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';entries={u.find(ns+'loc').text:u.find(ns+'lastmod').text for u in ET.parse(p).getroot()}
 for page in list(SERIES.rglob('*.html'))+[ROOT/'index.html',ROOT/'latest.html']:
  canonical=parse_page(page).canonical;assert canonical.startswith('https://nondubito.net/');entries[canonical]=DATE
 result[p]=sitemap_xml(sorted(entries.items(),key=lambda x:(x[0]!='https://nondubito.net/',x[0])))
 return result

def search_outputs():
 paths=list(SERIES.rglob('*.html'))+[ROOT/'index.html',ROOT/'latest.html'];scope={str(p.relative_to(ROOT)) for p in paths};result={}
 with patch.object(search,'collect_pages',lambda:paths):_,fresh=search.build()
 manifest=read(search.OUTPUT);unique=set()
 for lang,records in fresh.items():
  p=search.CHUNKS_DIR/f'{lang.lower()}.json';chunk=read(p);new={r['u']:r for r in records}
  chunk['records']=[new.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']];chunk['records'].extend(new.values());result[p]=search.serialized(chunk);manifest['languages'][lang]['count']=len(chunk['records']);unique.update(r['u'] for r in chunk['records'])
 manifest['record_count']=len(unique);result[search.OUTPUT]=search.serialized(manifest);return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 for p,s in discovery().items():
  if args.check:assert p.read_text()==s,('Stale Sex and the City discovery',p)
  else:p.write_text(s)
 p=ROOT/'index.html';s=render_home()
 if args.check:assert p.read_text()==s,'Stale home digest'
 else:p.write_text(s)
 for p,s in search_outputs().items():
  if args.check:assert p.read_text()==s,('Stale scoped search',p)
  else:p.write_text(s)
 print(('Verified' if args.check else 'Refreshed')+' Sex and the City discovery, scoped search, homepage and sitemap dates')
if __name__=='__main__':main()
