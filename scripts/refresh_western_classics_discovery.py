#!/usr/bin/env python3
"""Scoped discovery refresh; preserve unrelated search records and sitemap dates."""
import json
import xml.etree.ElementTree as ET
import build_search_index as search
from build_sitemap import parse_page, sitemap_xml

ROOT = search.ROOT

def refresh():
    paths = sorted(p for slug in ('sae-descartes','sae-spinoza','sae-western')
                   for p in (ROOT/'essays'/slug).glob('*.html'))
    scope = {str(p.relative_to(ROOT)) for p in paths}
    original_collect = search.collect_pages
    try:
        search.collect_pages = lambda: paths
        _, fresh = search.build()
    finally:
        search.collect_pages = original_collect
    manifest = json.loads(search.OUTPUT.read_text())
    added_urls = set()
    for lang, replacements in fresh.items():
        path = search.CHUNKS_DIR/f'{lang.lower()}.json'
        chunk = json.loads(path.read_text())
        existing = {r['u'] for r in chunk['records']}
        added_urls.update(r['u'] for r in replacements if r['u'] not in existing)
        by_url = {r['u']:r for r in replacements}
        chunk['records'] = [by_url.pop(r['u'], r) if r['u'] in scope else r for r in chunk['records']]
        chunk['records'].extend(by_url.values())
        if replacements:
            path.write_text(search.serialized(chunk))
        manifest['languages'][lang]['count'] = len(chunk['records'])
    manifest['record_count'] += len(added_urls)
    search.OUTPUT.write_text(search.serialized(manifest))
    sitemap = ROOT/'sitemap.xml'
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    entries = {u.find(ns+'loc').text:u.find(ns+'lastmod').text for u in ET.parse(sitemap).getroot()}
    for path in paths + [ROOT/p for p in ('library.html','explore.html','latest.html')]:
        canonical = parse_page(path).canonical
        assert canonical.startswith('https://nondubito.net/')
        entries[canonical] = '2026-10-03'
    sitemap.write_text(sitemap_xml(sorted(entries.items(), key=lambda x:(x[0]!='https://nondubito.net/',x[0]))))
    print(f'Refreshed {len(scope)} discovery pages; {len(added_urls)} new source records')

if __name__ == '__main__':
    refresh()
