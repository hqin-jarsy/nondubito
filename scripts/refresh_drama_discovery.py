#!/usr/bin/env python3
"""Scoped, repeatable discovery refresh for eight complete drama editions."""
import argparse
import html
import json
import re
from unittest.mock import patch
import build_drama_series as b
import build_search_index as search
from build_home_updates import render_home
from drama_languages import UI
DATE='2026-11-08'
ID=DATE+'-drama-eight-languages'
UPDATE={'id':ID,'date':DATE,'kind':'expanded','domain':'stories','series_key':'essays/everyday/stories/drama','url':'essays/everyday/stories/drama/index.html','languages':list(b.LANGS),
 'title':{'en':'Structures in Drama · Twenty-three Essays in Eight Languages','zh':'戏剧里的结构：23篇八语全文','zh-hant':'戲劇裡的結構：23篇八語全文'},
 'summary':{'en':'Complete German, French, Spanish, Japanese and Korean translations join the Chinese, Traditional Chinese and independent English editions. Every Chinese paragraph, scene detail, qualification and source note is retained in the five new languages.',
 'zh':'德、法、西、日、韩五语全文加入，连同简体、繁体与原有独立英文版，23篇现可八语阅读。新译保留中文的完整段落、场景细节、论证限定与来源说明。',
 'zh-hant':'德、法、西、日、韓五語全文加入，連同簡體、繁體與原有獨立英文版，23篇現可八語閱讀。新譯保留中文的完整段落、場景細節、論證限定與來源說明。'}}
START='<!-- DRAMA EIGHT LATEST START -->';END='<!-- DRAMA EIGHT LATEST END -->'

def latest_card():
 title=''.join(f'<h3 class="lang-{code}">{html.escape(UPDATE["title"][lang])}</h3>' for lang,code in [('en','en'),('zh','zh'),('zh-hant','hant')])
 summary=''.join(f'<p class="lang-{code}">{html.escape(UPDATE["summary"][lang])}</p>' for lang,code in [('en','en'),('zh','zh'),('zh-hant','hant')])
 return START+f'<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-drama-eight"><header class="updates-date"><h2 id="date-drama-eight"><time datetime="{DATE}">{DATE}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{ID}"><div class="update-meta"><span class="update-kind"><span class="lang-en">Expanded</span><span class="lang-zh">拓展</span><span class="lang-hant">拓展</span></span><span>简 · 繁 · EN · DE · FR · ES · 日本語 · 한국어</span></div>{title}{summary}<a href="essays/everyday/stories/drama/index.html"><span class="lang-en">Read the series →</span><span class="lang-zh">进入系列 →</span><span class="lang-hant">進入系列 →</span></a></article></div></section></div></section>'+END

def render():
 outputs={};path=b.ROOT/'data/site-updates.json';ledger=json.loads(path.read_text())
 ledger['updates']=[UPDATE if u['id']==ID else u for u in ledger['updates']] if any(u['id']==ID for u in ledger['updates']) else [UPDATE]+ledger['updates']
 outputs[path]=json.dumps(ledger,ensure_ascii=False,indent=2)+'\n'
 path=b.ROOT/'latest.html';text=path.read_text();card=latest_card()
 if START in text:text=re.sub(re.escape(START)+r'.*?'+re.escape(END),lambda _:card,text,flags=re.S)
 else:
  at=re.search(r'(?:<!--[^>]*-->\s*)?<section class="updates-section">',text);assert at
  text=text[:at.start()]+card+'\n'+text[at.start():]
 outputs[path]=text
 for path in (b.TARGET.parent/'index.html',b.ROOT/'library.html'):
  text=path.read_text()
  text=text.replace('3–8 languages','8 languages').replace('3–8 种语言','8 种语言').replace('3–8 種語言','8 種語言')
  # These exact phrases belonged to drama, the last three-language collection.
  text=text.replace('Twenty-three essays · Three languages','Twenty-three essays · Eight languages').replace('23 篇 · 三种语言','23 篇 · 八种语言').replace('23 篇 · 三種語言','23 篇 · 八種語言')
  outputs[path]=text
 for lang in b.FOREIGN:
  path=b.ROOT/f'essays/{lang}/index.html';text=path.read_text();start='<!-- DRAMA LANGUAGE HUB START -->';end='<!-- DRAMA LANGUAGE HUB END -->'
  title=html.escape(UI['Structures in Drama'][lang]);tag=html.escape(UI['23 essays · 8 languages'][lang]);deck=html.escape(UI[b.DECK[0]][lang])
  section=start+f'<section class="essays-section" id="drama-eight"><div class="essays-inner"><div class="section-header"><h2>{title}</h2></div><div class="essays-grid"><a class="essay-card" href="../everyday/stories/drama/index.html?lang={lang}"><span class="essay-tag">{tag}</span><h3>{title}</h3><p>{deck}</p></a></div></div></section>'+end
  if start in text:text=re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:section,text,flags=re.S)
  else:
   marker=re.search(r'<footer\b',text);assert marker
   text=text[:marker.start()]+section+'\n'+text[marker.start():]
  outputs[path]=text
 path=b.ROOT/'sitemap.xml';text=path.read_text()
 text,count=re.subn(r'(<loc>https://nondubito.net/essays/everyday/stories/drama/[^<]*</loc>\s*<lastmod>)[^<]+',lambda m:m[1]+DATE,text)
 assert count==24
 text=re.sub(r'(<loc>https://nondubito.net/essays/everyday/stories/</loc>\s*<lastmod>)[^<]+',lambda m:m[1]+DATE,text)
 outputs[path]=text
 return outputs

def search_outputs(paths):
 with patch.object(search,'collect_pages',lambda:sorted(set(paths))):_,fresh=search.build()
 scope={str(p.relative_to(b.ROOT)) for p in paths};outputs={};manifest=json.loads(search.OUTPUT.read_text());unique=set()
 for lang,records in fresh.items():
  path=search.CHUNKS_DIR/f'{lang.lower()}.json';chunk=json.loads(path.read_text());new={r['u']:r for r in records}
  chunk['records']=[new.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']];chunk['records'].extend(new.values())
  outputs[path]=search.serialized(chunk);manifest['languages'][lang]['count']=len(chunk['records']);unique.update(r['u'] for r in chunk['records'])
 manifest['record_count']=len(unique);outputs[search.OUTPUT]=search.serialized(manifest)
 return outputs

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args();outputs=render()
 if args.check:
  stale=[str(p.relative_to(b.ROOT)) for p,t in outputs.items() if p.read_text()!=t]
  paths=list(b.render())+[p for p in outputs if p.suffix=='.html' and p.name!='latest.html']+[b.ROOT/'index.html']
  stale += [str(p.relative_to(b.ROOT)) for p,t in search_outputs(paths).items() if p.read_text()!=t]
  if stale:raise SystemExit('Stale drama discovery: '+', '.join(stale))
  print('OK: drama discovery and scoped search are current');return
 for path,text in outputs.items():path.write_text(text)
 home=b.ROOT/'index.html';home.write_text(render_home())
 paths=list(b.render())+[p for p in outputs if p.suffix=='.html' and p.name!='latest.html']+[home]
 for path,text in search_outputs(paths).items():path.write_text(text)
 print('Refreshed eight-language drama discovery; unrelated search records preserved')
if __name__=='__main__':main()
