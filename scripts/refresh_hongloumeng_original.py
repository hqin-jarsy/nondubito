#!/usr/bin/env python3
"""Refresh only original-fiction publication discovery, preserving unrelated records."""
import json
import xml.etree.ElementTree as ET
import build_search_index as search
from build_sitemap import parse_page, sitemap_xml
from build_hongloumeng_original import render, DATE

def refresh():
    paths=list(render())
    paths += [search.ROOT/'essays/literature/hlm'/d/'index.html' for d in ('','en','zh-hant')]
    paths += [search.ROOT/p for p in ('originals/index.html','library.html','essays/literature/index.html')]
    scope={str(p.relative_to(search.ROOT)) for p in paths}
    previous=search.collect_pages
    try:
        search.collect_pages=lambda:paths
        _,fresh=search.build()
    finally:
        search.collect_pages=previous
    manifest=json.loads(search.OUTPUT.read_text());added=set()
    for lang,replacements in fresh.items():
        path=search.CHUNKS_DIR/f'{lang.lower()}.json';chunk=json.loads(path.read_text())
        existing={r['u'] for r in chunk['records']}
        added.update(r['u'] for r in replacements if r['u'] not in existing)
        by_url={r['u']:r for r in replacements}
        chunk['records']=[by_url.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']]
        chunk['records'].extend(by_url.values())
        if replacements:path.write_text(search.serialized(chunk))
        manifest['languages'][lang]['count']=len(chunk['records'])
    manifest['record_count']+=len(added);search.OUTPUT.write_text(search.serialized(manifest))
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';path=search.ROOT/'sitemap.xml'
    entries={u.find(ns+'loc').text:u.find(ns+'lastmod').text for u in ET.parse(path).getroot()}
    for p in paths+[search.ROOT/'latest.html']:
        canonical=parse_page(p).canonical;assert canonical.startswith('https://nondubito.net/')
        entries[canonical]=DATE
    path.write_text(sitemap_xml(sorted(entries.items(),key=lambda x:(x[0]!='https://nondubito.net/',x[0]))))
    print(f'Refreshed {len(scope)} discovery pages; added {len(added)} source records')

if __name__=='__main__':refresh()
