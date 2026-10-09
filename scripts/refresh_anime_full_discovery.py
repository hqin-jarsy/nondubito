#!/usr/bin/env python3
"""Refresh existing anime search records and sitemap dates only within scope."""
import json
import xml.etree.ElementTree as ET
import build_search_index as search
from build_sitemap import parse_page, sitemap_xml
from build_anime_full_editions import outputs, DATE, ROOT, BATCH

def refresh():
    paths=list(outputs())
    if BATCH in ('02', '03', '04'): paths += [ROOT/'essays/anime/index.html']+[ROOT/'essays'/lang/'index.html' for lang in ('de','fr','es','ja','ko')]
    scope={str(p.relative_to(ROOT)) for p in paths}
    previous=search.collect_pages
    try:
        search.collect_pages=lambda: paths
        _,fresh=search.build()
    finally: search.collect_pages=previous
    manifest=json.loads(search.OUTPUT.read_text())
    for lang,replacements in fresh.items():
        if not replacements: continue
        p=search.CHUNKS_DIR/f'{lang.lower()}.json';chunk=json.loads(p.read_text())
        by_url={r['u']:r for r in replacements}
        chunk['records']=[by_url.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']]
        chunk['records'].extend(by_url.values());p.write_text(search.serialized(chunk))
        manifest['languages'][lang]['count']=len(chunk['records'])
    manifest['record_count']=sum(v['count'] for v in manifest['languages'].values())
    search.OUTPUT.write_text(search.serialized(manifest))
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';p=ROOT/'sitemap.xml'
    entries={u.find(ns+'loc').text:u.find(ns+'lastmod').text for u in ET.parse(p).getroot()}
    for page in paths+[ROOT/'latest.html']: entries[parse_page(page).canonical]=DATE
    p.write_text(sitemap_xml(sorted(entries.items(),key=lambda x:(x[0]!='https://nondubito.net/',x[0]))))
    print('Refreshed',len(paths),'anime search records and sitemap dates')

if __name__=='__main__': refresh()
