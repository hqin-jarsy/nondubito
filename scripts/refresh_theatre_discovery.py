#!/usr/bin/env python3
"""Refresh theatre discovery, preserving unrelated search records and URL dates."""
import argparse
from collections import Counter
import json
import xml.etree.ElementTree as ET
from unittest.mock import patch

import build_search_index as search
from build_theatre import ROOT
from theatre_language_batch import DATE, LANGUAGES, SLUGS
from build_sitemap import parse_page, sitemap_xml
from build_content_registry import scan_page, group_pages, parse_library_categories, render_audit


def publication_paths():
    primary = [ROOT / 'essays/theatre/index.html'] + [
        ROOT / f'essays/theatre/{slug}.html' for slug in SLUGS]
    localized = [ROOT / f'essays/theatre/{lang}/{slug}.html'
                 for lang in LANGUAGES for slug in ('index', *SLUGS)]
    return primary + localized


def registry_outputs(baseline=None):
    registry_path = ROOT / 'data/content-registry-prototype.json'
    audit_path = ROOT / 'reports/content-registry-prototype-audit.json'
    registry = baseline['registry'] if baseline else json.loads(registry_path.read_text())
    audit = baseline['audit'] if baseline else json.loads(audit_path.read_text())
    records, collisions = group_pages([scan_page(ROOT, path) for path in publication_paths()])
    assert not collisions
    by_id = {r['content_id']: r for r in records}
    assert len(by_id) == 4 and set(by_id) <= {r['content_id'] for r in registry['records']}
    new_paths = set()
    current = []
    for old in registry['records']:
        refreshed = by_id.get(old['content_id'])
        if refreshed:
            # This is an edition expansion, not a new work or identity.
            new_paths.update({e['path'] for e in refreshed['editions'].values()} -
                             {e['path'] for e in old['editions'].values()})
            current.append(dict(old, titles=refreshed['titles'], editions=refreshed['editions'],
                                description=refreshed['description'], updated_at=DATE,
                                update_kind='expanded'))
        else:
            current.append(old)
    registry['records'] = current
    categories = parse_library_categories(ROOT / 'library.html')
    theatre = next(c for c in categories if c['href'] == 'essays/theatre/index.html')
    registry['library_categories'] = [theatre if c['href'] == theatre['href'] else c
                                      for c in registry['library_categories']]
    all_records = registry['records']
    audit['scanned_html_pages'] += len(new_paths)
    audit['canonical_records'] = len(all_records)
    audit['library_category_count'] = len(registry['library_categories'])
    audit['library_series_card_count'] = sum(c['series_count'] for c in registry['library_categories'])
    audit['record_type_counts'] = dict(sorted(Counter(r['record_type'] for r in all_records).items()))
    audit['language_record_counts'] = dict(sorted(Counter(l for r in all_records for l in r['editions']).items()))
    audit['edition_count_distribution'] = {str(n): count for n, count in
                                           sorted(Counter(len(r['editions']) for r in all_records).items())}
    note = (f'Theatre editions were updated incrementally on {DATE}. Other series retain '
            'their prior snapshot records and diagnostics; this is not a new all-site audit.')
    audit['scoped_update'] = note
    report = render_audit(audit).replace('# Content registry prototype audit\n',
                                          '# Content registry prototype audit\n\n' + note + '\n', 1)
    return {registry_path: json.dumps(registry, ensure_ascii=False, indent=2) + '\n',
            audit_path: json.dumps(audit, ensure_ascii=False, indent=2) + '\n',
            ROOT / 'reports/content-registry-prototype-audit.md': report}


def outputs(registry_baseline=None):
    paths = publication_paths() + [ROOT / p for p in ('index.html', 'library.html')]
    paths += [ROOT / f'essays/{lang}/index.html' for lang in LANGUAGES]
    scope = {p.relative_to(ROOT).as_posix() for p in paths}
    with patch.object(search, 'collect_pages', lambda: paths):
        _, fresh = search.build()
    manifest = json.loads(search.OUTPUT.read_text())
    chunks = {lang: json.loads((search.CHUNKS_DIR / f'{lang.lower()}.json').read_text())
              for lang in search.SEARCH_LANGUAGES}
    prior_urls = {r['u'] for chunk in chunks.values() for r in chunk['records']}
    new_urls = {r['u'] for records in fresh.values() for r in records} - prior_urls
    result = {}
    for lang, replacements in fresh.items():
        chunk = chunks[lang]
        by_url = {r['u']: r for r in replacements}
        original_unrelated = [r for r in chunk['records'] if r['u'] not in scope]
        merged = []
        for record in chunk['records']:
            if record['u'] not in scope:
                merged.append(record)
            elif record['u'] in by_url:
                merged.append(by_url.pop(record['u']))
        merged.extend(by_url.values())
        assert [r for r in merged if r['u'] not in scope] == original_unrelated
        chunk['records'] = merged
        manifest['languages'][lang]['count'] = len(merged)
        result[search.CHUNKS_DIR / f'{lang.lower()}.json'] = search.serialized(chunk)
    manifest['record_count'] += len(new_urls)
    result[search.OUTPUT] = search.serialized(manifest)

    sitemap = ROOT / 'sitemap.xml'
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    entries = {u.findtext(ns + 'loc'): u.findtext(ns + 'lastmod')
               for u in ET.parse(sitemap).getroot()}
    # Mapping insertion order preserves the existing sitemap order. Append only
    # new canonical URLs; existing originals retain their datePublished on page.
    changed = paths + [ROOT / p for p in ('explore.html', 'latest.html')]
    for page in changed:
        metadata = parse_page(page)
        assert metadata.canonical.startswith('https://nondubito.net/')
        assert metadata.title and metadata.description and metadata.html_lang
        assert 'noindex' not in metadata.robots
        entries[metadata.canonical] = max(entries.get(metadata.canonical, DATE), DATE)
    result[sitemap] = sitemap_xml(list(entries.items()))
    result.update(registry_outputs(registry_baseline))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, text in outputs().items():
        if args.check:
            assert path.read_text() == text, f'Stale scoped discovery: {path}'
        elif path.read_text() != text:
            path.write_text(text)
    print(('Checked' if args.check else 'Refreshed') +
          ' theatre search and sitemap; unrelated records and dates retained')


if __name__ == '__main__':
    main()
