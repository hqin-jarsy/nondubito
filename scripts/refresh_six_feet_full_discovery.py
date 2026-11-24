#!/usr/bin/env python3
"""Refresh scoped Six Feet Under discovery without moving existing URLs."""
import argparse
import json
import re
import xml.etree.ElementTree as ET
from unittest.mock import patch

import build_search_index as search
from build_home_updates import render_home
from build_sitemap import parse_page, sitemap_xml
from build_six_feet_full_editions import DATE, LANGS, ROOT, SERIES

ID = DATE + "-six-feet-under-complete"
UPDATE = {
    "id":ID,"date":DATE,"kind":"expanded","domain":"tv","series_key":"essays/tv/six-feet-under",
    "url":"essays/tv/six-feet-under/index.html","languages":["en","zh","zh-hant",*LANGS],
    "title":{"en":"Six Feet Under · Nine Complete Readings","zh":"《六尺之下》：九篇八语完整阅读","zh-hant":"《六尺之下》：九篇八語完整閱讀"},
    "summary":{"en":"Nine essays reviewed against the series. The brief English, Japanese, French, German, Spanish and Korean versions have been replaced with complete readings.",
               "zh":"九篇逐一复核剧情与正文；英日法德西韩六语短版均换为全文，简繁同步修订。",
               "zh-hant":"九篇逐一複核劇情與正文；英日法德西韓六語短版均換為全文，簡繁同步修訂。"},
}
START = "<!-- SIX FEET UNDER COMPLETE LATEST START -->"
END = "<!-- SIX FEET UNDER COMPLETE LATEST END -->"

def read(p): return json.loads(p.read_text())

def card():
    title = "".join(f'<h3 class="lang-{css}">{UPDATE["title"][lang]}</h3>' for lang,css in (("en","en"),("zh","zh"),("zh-hant","hant")))
    deck = "".join(f'<p class="lang-{css}">{UPDATE["summary"][lang]}</p>' for lang,css in (("en","en"),("zh","zh"),("zh-hant","hant")))
    return START + f'<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-six-feet-under-complete"><header class="updates-date"><h2 id="date-six-feet-under-complete"><time datetime="{DATE}">{DATE}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{ID}"><div class="update-meta"><span class="update-kind"><span class="lang-en">Expanded</span><span class="lang-zh">拓展</span><span class="lang-hant">拓展</span></span><span>简 · 繁 · EN · 日本語 · FR · DE · ES · 한국어</span></div>{title}{deck}<a href="{UPDATE["url"]}"><span class="lang-en">Read the series →</span><span class="lang-zh">进入系列 →</span><span class="lang-hant">進入系列 →</span></a></article></div></section></div></section>' + END

def announcements():
    ledger = ROOT/"data/site-updates.json"
    payload = read(ledger)
    prior = payload["updates"]
    payload["updates"] = [UPDATE]+[u for u in prior if u["id"] != ID]
    latest = ROOT/"latest.html"
    original = latest.read_text()
    if START in original:
        latest_html = re.sub(re.escape(START)+".*?"+re.escape(END),lambda _:card(), original, count=1, flags=re.S)
    else:
        at = re.search(r'(?:<!--[^>]*-->\s*)?<section class="updates-section">', original)
        assert at
        latest_html = original[:at.start()] + card() + "\n" + original[at.start():]
    return {ledger:json.dumps(payload,ensure_ascii=False,indent=2)+"\n",latest:latest_html}

def discovery():
    paths = sorted(p for p in SERIES.rglob("*.html") if not search.COLLISION_NAME.search(p.name))
    assert len(paths)==60
    paths.append(ROOT/"index.html")
    scope = {str(p.relative_to(ROOT)) for p in paths}
    with patch.object(search,"collect_pages",lambda:paths):
        _,fresh=search.build()
    manifest=read(search.OUTPUT)
    unique=set()
    result={}
    for lang in search.SEARCH_LANGUAGES:
        p=search.CHUNKS_DIR/f"{lang.lower()}.json"
        chunk=read(p)
        new={r["u"]:r for r in fresh.get(lang,[])}
        current=[r for r in chunk["records"] if r["u"] not in scope or r["u"] in new]
        chunk["records"]=[new.pop(r["u"],r) if r["u"] in scope else r for r in current]
        chunk["records"].extend(new.values())
        manifest["languages"][lang]["count"]=len(chunk["records"])
        unique.update(r["u"] for r in chunk["records"])
        result[p]=search.serialized(chunk)
    manifest["record_count"]=len(unique)
    result[search.OUTPUT]=search.serialized(manifest)
    p=ROOT/"sitemap.xml"
    ns="{http://www.sitemaps.org/schemas/sitemap/0.9}"
    entries={u.findtext(ns+"loc"):u.findtext(ns+"lastmod") for u in ET.parse(p).getroot()}
    for page in paths+[ROOT/"latest.html"]:
        canonical=parse_page(page).canonical
        assert canonical in entries, (page,canonical)
        entries[canonical]=max(DATE,entries[canonical])
    result[p]=sitemap_xml(list(entries.items()))
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check",action="store_true")
    check=ap.parse_args().check
    def apply(paths):
        for p,value in paths.items():
            if check: assert p.read_text()==value,p
            elif p.read_text()!=value:p.write_text(value)
    apply(announcements())
    apply({ROOT/"index.html":render_home()})
    apply(discovery())
    print(("Verified" if check else "Refreshed"),"Six Feet Under discovery, search and sitemap dates")

if __name__=="__main__": main()
