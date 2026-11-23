#!/usr/bin/env python3
"""Refresh only this publication's search records and sitemap entries."""
import json
import re
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET
import build_search_index as search
from build_sitemap import parse_page
from build_hominins import render, DATE, LANGS, ARTICLES, destination

def refresh():
    # Add this release and refresh only its directly affected discovery pages.
    before = {destination(lang, ep): destination(lang, ep).read_bytes()
              for lang in LANGS for ep in (None, *ARTICLES)
              if destination(lang, ep).exists()}
    paths = list(render()) + [search.ROOT / p for p in ('library.html','explore.html')]
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
    source = path.read_text()
    locations = [u.find(ns + 'loc').text for u in ET.fromstring(source)]
    assert len(locations) == len(set(locations)), 'duplicate sitemap locations'
    existing = set(locations)
    additions = []
    for p in paths + [search.ROOT / 'latest.html']:
        canonical = parse_page(p).canonical
        assert canonical.startswith('https://nondubito.net/')
        uri = escape(canonical)
        if canonical not in existing:
            additions.append((canonical, f'  <url>\n    <loc>{uri}</loc>\n    <lastmod>{DATE}</lastmod>\n  </url>\n'))
            existing.add(canonical)
        elif p not in before or p.read_bytes() != before[p]:
            pattern = rf'(<loc>{re.escape(uri)}</loc>\s*<lastmod>)[^<]+(</lastmod>)'
            source, count = re.subn(pattern, lambda m: m[1] + DATE + m[2], source)
            assert count == 1, (canonical, count)
    assert source.count('</urlset>') == 1
    source = source.replace('</urlset>', ''.join(x[1] for x in sorted(additions)) + '</urlset>')
    path.write_text(source)
    print(f'Refreshed {len(scope)} discovery pages; added {len(added)} source records')

if __name__ == '__main__':
    refresh()
