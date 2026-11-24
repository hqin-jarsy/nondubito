#!/usr/bin/env python3
"""Update only the five Boethius language editions in search, sitemap and news."""
import argparse
import json
import re
import xml.etree.ElementTree as ET
from unittest.mock import patch

import build_search_index as search
from build_home_updates import render_home
from build_sitemap import parse_page, sitemap_xml
from build_sae_consolation_full import DATE, LANGS, ROOT, SERIES

ID=DATE+"-sae-consolation-complete"
URL="essays/sae-consolation/index.html"
TITLE={"en":"The Consolation of Philosophy · Six Complete Readings","zh":"波爱修斯《哲学的慰藉》：六篇八语完整阅读","zh-hant":"波愛修斯《哲學的慰藉》：六篇八語完整閱讀"}
DECK={"en":"The six Boethius readings now also have full Japanese, French, German, Spanish and Korean editions. The existing Chinese and English editions are unchanged.",
      "zh":"波爱修斯六篇解读的日法德西韩短版换为全文，保留原有中英文版本。",
      "zh-hant":"波愛修斯六篇解讀的日法德西韓短版換為全文，保留原有中英文版本。"}
UPDATE={"id":ID,"date":DATE,"kind":"expanded","domain":"sae","series_key":"essays/sae-consolation",
        "url":URL,"languages":["en","zh","zh-hant",*LANGS],"title":TITLE,"summary":DECK}
START="<!-- SAE CONSOLATION COMPLETE LATEST START -->"
END="<!-- SAE CONSOLATION COMPLETE LATEST END -->"

def read(p): return json.loads(p.read_text())

def news():
    ledger=ROOT/"data/site-updates.json"
    data=read(ledger)
    data["updates"]=[UPDATE]+[x for x in data["updates"] if x["id"]!=ID]
    latest=ROOT/"latest.html"; old=latest.read_text()
    modes=(("en","en"),("zh","zh"),("zh-hant","hant"))
    title="".join(f'<h3 class="lang-{css}">{TITLE[l]}</h3>' for l,css in modes)
    deck="".join(f'<p class="lang-{css}">{DECK[l]}</p>' for l,css in modes)
    new=START+f'<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-sae-consolation-complete"><header class="updates-date"><h2 id="date-sae-consolation-complete"><time datetime="{DATE}">{DATE}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{ID}"><div class="update-meta"><span class="update-kind"><span class="lang-en">Expanded</span><span class="lang-zh">拓展</span><span class="lang-hant">拓展</span></span><span>简 · 繁 · EN · 日本語 · FR · DE · ES · 한국어</span></div>{title}{deck}<a href="{URL}"><span class="lang-en">Read the series →</span><span class="lang-zh">进入系列 →</span><span class="lang-hant">進入系列 →</span></a></article></div></section></div></section>'+END
    if START in old:
        new=re.sub(re.escape(START)+".*?"+re.escape(END),lambda _:new,old,count=1,flags=re.S)
    else:
        at=re.search(r'(?:<!--[^>]*-->\s*)?<section class="updates-section">',old)
        assert at
        new=old[:at.start()]+new+"\n"+old[at.start():]
    return {ledger:json.dumps(data,ensure_ascii=False,indent=2)+"\n",latest:new}

def discovery():
    paths=sorted(SERIES/lang/f"ep{i:02}.html" for lang in LANGS for i in range(1,7))
    paths.append(ROOT/"index.html")
    scope={p.relative_to(ROOT).as_posix() for p in paths}
    with patch.object(search,"collect_pages",lambda:paths):
        _,fresh=search.build()
    result={}
    for lang in search.SEARCH_LANGUAGES:
        p=search.CHUNKS_DIR/f"{lang.lower()}.json"
        data=read(p); new={r["u"]:r for r in fresh.get(lang,[])}
        assert set(new)=={r["u"] for r in data["records"] if r["u"] in scope},lang
        data["records"]=[new.get(r["u"],r) for r in data["records"]]
        result[p]=search.serialized(data)
    sitemap=ROOT/"sitemap.xml"; ns="{http://www.sitemaps.org/schemas/sitemap/0.9}"
    entries={u.findtext(ns+"loc"):u.findtext(ns+"lastmod") for u in ET.parse(sitemap).getroot()}
    for page in paths+[ROOT/"latest.html"]:
        url=parse_page(page).canonical
        assert url in entries, (page,url)
        entries[url]=max(DATE,entries[url])
    result[sitemap]=sitemap_xml(list(entries.items()))
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check",action="store_true")
    check=ap.parse_args().check
    def emit(output):
        for p,text in output.items():
            if check: assert p.read_text()==text,p
            elif p.read_text()!=text:p.write_text(text)
    emit(news())
    emit({ROOT/"index.html":render_home()})
    emit(discovery())
    print(("Verified" if check else "Refreshed"),"scoped Boethius discovery; no new URLs")

if __name__=="__main__": main()
