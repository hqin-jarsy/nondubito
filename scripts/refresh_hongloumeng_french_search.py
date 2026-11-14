#!/usr/bin/env python3
"""Refresh only the validated French reader's search records; read-only by default."""
import argparse
import json
from pathlib import Path

import build_search_index as search
from build_content_registry import scan_page
from build_hongloumeng_reading import checked_input_paths
from hongloumeng_french_availability import french_publication, PREFIX

ROOT = Path(__file__).resolve().parents[1]


def outputs(root=ROOT):
    publication = french_publication(root)
    if publication is None:
        raise ValueError('French reader is not published')
    manifest_path = root / 'data/search-index.json'
    chunk_path = root / 'data/search/fr.json'
    checked_input_paths([manifest_path, chunk_path])
    manifest = json.loads(manifest_path.read_text())
    chunk = json.loads(chunk_path.read_text())
    if chunk['language'] != 'fr':
        raise ValueError('Invalid French search chunk')
    replacements = {}
    for path in publication['paths']:
        source = path.read_text(encoding='utf-8')
        page = scan_page(root, path, source=source)
        if page['languages'] != ['fr'] or page['html_lang'] != 'fr':
            raise ValueError('French search page must have only its declared language')
        if search.is_redirect(source) or 'noindex' in source.lower():
            raise ValueError('French search page is not indexable')
        title = page['titles'].get('fr') or page['document_title']
        if not title:
            raise ValueError('French search page has no title')
        replacements[page['path']] = dict(u=page['path'], k=page['record_type'],
            d=page['domain'], c=page['category'], s=page['series'], n=page['sequence'],
            t=title, x=page['description'] or '', q=search.extract_search_text(source))
    old = chunk['records']
    # Reject stale private/review records instead of silently perpetuating them.
    if any(r['u'].startswith(PREFIX) and r['u'] not in replacements for r in old):
        raise ValueError('Unexpected French reader URL in existing index')
    records = [replacements.pop(r['u']) if r['u'] in replacements else r for r in old]
    records.extend(replacements[url] for url in sorted(replacements))
    if len({r['u'] for r in records}) != len(records):
        raise ValueError('Duplicate French search URLs')
    chunk['records'] = records
    manifest['record_count'] += len(records) - len(old)
    manifest['languages']['fr']['count'] = len(records)
    return {manifest_path: search.serialized(manifest), chunk_path: search.serialized(chunk)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    planned = outputs()
    stale = [p for p, content in planned.items() if p.read_text() != content]
    if args.write:
        for path in stale:
            path.write_text(planned[path], encoding='utf-8')
        print(f'Updated {len(stale)} French search files')
        return 0
    for path in stale:
        print('STALE:', path.relative_to(ROOT))
    if not stale:
        print('OK: French reader search is current (82 pages)')
    return int(bool(stale))


if __name__ == '__main__':
    raise SystemExit(main())
