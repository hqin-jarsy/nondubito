#!/usr/bin/env python3
"""Refresh only this publication's search records and sitemap entries."""
import json
import xml.etree.ElementTree as ET
import build_search_index as search
from build_sitemap import parse_page, sitemap_xml
from build_paleontology import render, DATE, LANGS, PUBLISHED, destination

def refresh():
    before = {destination(lang, ep): destination(lang, ep).read_bytes()
              for lang in LANGS for ep in (None, *PUBLISHED)
              if destination(lang, ep).exists()}
    paths = list(render()) + [search.ROOT / 'library.html']
    paths += [search.ROOT / f'essays/{lang}/index.html' for lang in ('de','fr','es','ja','ko')]
    scope = {str(p.relative_to(search.ROOT)) for p in paths}
    previous = search.collect_pages
    try:
        search.collect_pages = lambda: paths
        _, fresh = search.build()
    finally:
        search.collect_pages = previous
    manifest = json.loads(search.OUTPUT.read_text()); added = set()
    for lang, replacements in fresh.items():
        path = search.CHUNKS_DIR / f'{lang.lower()}.json'
        chunk = json.loads(path.read_text())
        existing = {r['u'] for r in chunk['records']}
        added.update(r['u'] for r in replacements if r['u'] not in existing)
        by_url = {r['u']: r for r in replacements}
        chunk['records'] = [by_url.pop(r['u'], r) if r['u'] in scope else r for r in chunk['records']]
        chunk['records'].extend(by_url.values())
        if replacements:
            path.write_text(search.serialized(chunk))
        manifest['languages'][lang]['count'] = len(chunk['records'])
    manifest['record_count'] += len(added)
    search.OUTPUT.write_text(search.serialized(manifest))
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    path = search.ROOT / 'sitemap.xml'
    entries = {u.find(ns+'loc').text: u.find(ns+'lastmod').text for u in ET.parse(path).getroot()}
    for p in paths + [search.ROOT / 'latest.html']:
        canonical = parse_page(p).canonical
        assert canonical.startswith('https://nondubito.net/')
        # Rebuilding unchanged articles must not advertise a fresh modification.
        if canonical not in entries or p not in before or p.read_bytes() != before[p]:
            entries[canonical] = DATE
    path.write_text(sitemap_xml(sorted(entries.items(), key=lambda x: (x[0] != 'https://nondubito.net/', x[0]))))
    print(f'Refreshed {len(scope)} discovery pages; added {len(added)} source records')

if __name__ == '__main__':
    refresh()
