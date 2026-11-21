#!/usr/bin/env python3
"""Mechanical release checks for the Monopoly reader editions, never a prose review."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit

import build_monopoly_languages as batch
import build_reader_series as primary
import full_series_languages as languages
from build_sitemap import parse_page
from prepare_action_sources import Document
from web_analytics import TOKEN

ROOT, DIRECTORY, BASE = batch.ROOT, batch.DIRECTORY, batch.BASE
ORIGIN = 'https://nondubito.net/'
NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def sitemap_entries(content):
    rows = [(row.findtext(NS+'loc'), row.findtext(NS+'lastmod')) for row in ET.fromstring(content)]
    assert len(dict(rows)) == len(rows), 'Duplicate sitemap URLs'
    return dict(rows)


def links(nodes, kind):
    return [n.attrs.get('href') for n in nodes if n.tag == 'link' and n.attrs.get('rel') == kind]


def check_page(path, text, spec, slug, language, sitemap):
    doc = Document(text)
    nodes = list(doc.root.walk())
    rel = path.relative_to(ROOT).as_posix()
    canonical = ORIGIN + rel.removesuffix('index.html')
    assert links(nodes, 'canonical') == [canonical] and canonical in sitemap, path
    expected = Document(languages.alternatives(spec, slug))
    actual_alt = [(n.attrs.get('hreflang'), n.attrs.get('href')) for n in nodes if
                  n.tag == 'link' and n.attrs.get('rel') == 'alternate']
    expected_alt = [(n.attrs['hreflang'], n.attrs['href']) for n in expected.root.walk() if n.tag == 'link']
    assert actual_alt == expected_alt and len(actual_alt) == 9, (path, actual_alt)
    for _, url in actual_alt:
        assert url in sitemap, (path, url)
    beacon, = [n for n in nodes if n.tag == 'script' and 'cloudflareinsights.com/beacon.min.js' in n.attrs.get('src','')]
    assert json.loads(beacon.attrs['data-cf-beacon'])['token'] == TOKEN, path
    schema, = [n for n in nodes if n.tag == 'script' and n.attrs.get('type') == 'application/ld+json']
    info = json.loads(schema.text())
    headings = [n for n in nodes if n.tag == 'h1']
    if language:
        assert len(headings) == 1 and info['inLanguage'] == language, path
        for menu in (n for n in nodes if n.has('site-shell-language-options')):
            options = [n for n in menu.walk() if n.tag == 'a']
            assert len(options) == 8 and sum(n.attrs.get('aria-current') == 'page' for n in options) == 1, path
        assert sum(n.has('site-shell-language-options') for n in nodes) == 1, path
    else:
        assert {n.attrs.get('class') for n in headings} == {'lang-en', 'lang-zh', 'lang-hant'}, path
        assert info['inLanguage'] == ['en', 'zh-Hans', 'zh-Hant'], path
        assert sum(n.tag == 'a' and n.attrs.get('lang') in spec['languages'] for n in nodes) == 10, path
    for n in nodes:
        attr = 'href' if n.tag in ('a', 'link') else 'src'
        raw = n.attrs.get(attr, '')
        parts = urlsplit(raw)
        if not raw or parts.scheme or parts.netloc:
            continue
        if not parts.path:
            target = path
        elif parts.path.startswith('/'):
            target = ROOT / unquote(parts.path).lstrip('/')
        else:
            target = path.parent / unquote(parts.path)
        if target.is_dir():
            target /= 'index.html'
        assert target.is_file(), (path, raw)
        if parts.fragment:
            content = text if target.resolve() == path.resolve() else target.read_text()
            assert re.search(r'\bid=["\']'+re.escape(unquote(parts.fragment))+r'["\']', content), (path, raw)
    return doc, nodes


def body_and_refs(doc, nodes, path, row, primary_item=None):
    bodies = [n for n in nodes if n.has('essay-body')]
    source, = [n for n in nodes if n.has('lw-sources')]
    citation_urls = [n.attrs['href'] for n in source.walk()
                     if n.tag == 'a' and n.attrs.get('href','').startswith('https://')]
    if primary_item is not None:
        assert len(bodies) == 3
        for key, language in [('en','en'), ('zh','zh'), ('hant','hant')]:
            node, = [n for n in bodies if n.has('lang-'+language)]
            assert doc.source[node.open_end:node.close_start] == primary.prose(primary_item['body_'+key]), (path, key)
        expected_refs = [r['url'] for r in primary_item['references']]
        assert citation_urls == [primary_item['source_url'], *expected_refs], path
    else:
        node, = bodies
        assert doc.source[node.open_end:node.close_start] == languages.render_prose(row['body']), path
        assert citation_urls == [row['source_url'], *[r['url'] for r in row['references']]], (path, citation_urls)
        labels = [n.text().strip() for n in source.walk()
                  if n.tag == 'a' and n.attrs.get('href','').startswith('https://')][1:]
        assert labels == [r['title']+' ↗' for r in row['references']], (path, labels)


def check():
    spec = languages.profile(batch.KEY)
    release, slugs, related = batch.master_spec()
    assert spec['slugs'] == slugs and spec['related_series'] == related
    assert spec['date'] == release['date']
    pages_primary = primary.render(batch.KEY)
    pages_foreign = languages.render(batch.KEY)
    folder = ROOT / DIRECTORY
    physical = [f'{slug}.html' for slug in ['index', *slugs]]
    assert {p.name for p in folder.glob('*.html')} == set(physical)
    assert len(pages_primary) == len(physical) and len(pages_foreign) == 5 * len(physical)
    sitemap = sitemap_entries((ROOT/'sitemap.xml').read_bytes())
    items = {slug: batch.read(BASE.parent/(slug+'.json')) for slug in slugs}
    for path, text in pages_primary.items():
        assert path.read_text() == text, path
        doc, nodes = check_page(path, text, spec, path.stem, None, sitemap)
        if path.stem != 'index':
            body_and_refs(doc, nodes, path, None, items[path.stem])
    for language in spec['languages']:
        _, data = languages.load_language(batch.KEY, language)
        records = batch.read(ROOT/'data/search'/f'{language}.json')['records']
        indexed = {row['u'] for row in records}
        assert len(records) == len(indexed), language
        assert {p.name for p in (folder/language).glob('*.html')} == set(physical), language
        assert {f'{DIRECTORY}/{language}/{name}' for name in physical} <= indexed, language
        src = (ROOT/f'essays/{language}/index.html').read_text()
        assert src.count(f'../{batch.KEY}/{language}/index.html') == 1, language
        for row in [None, *data['articles']]:
            slug = row['slug'] if row else 'index'
            path = folder / language / f'{slug}.html'
            text = path.read_text()
            assert text == pages_foreign[path], path
            doc, nodes = check_page(path, text, spec, slug, language, sitemap)
            if row:
                assert row['source_sha256'] == hashlib.sha256((BASE.parent/f'{slug}.json').read_bytes()).hexdigest(), path
                assert len(row['body']) == len(items[slug]['body_zh']) == len(row['coverage']), path
                body_and_refs(doc, nodes, path, row)
            else:
                entries = [n.attrs['href'] for n in nodes if n.tag=='a' and n.has('lw-card')]
                assert entries == [f'{episode}.html' for episode in slugs], path
    for language in ('en', 'zh-hans', 'zh-hant'):
        indexed = {row['u'] for row in batch.read(ROOT/'data/search'/f'{language}.json')['records']}
        assert {f'{DIRECTORY}/{name}' for name in physical} <= indexed, language
    entry = batch.read(BASE/'discovery.json')
    update, = [row for row in batch.read(ROOT/'data/site-updates.json')['updates'] if row['id'] == entry['id']]
    assert update == {k:v for k,v in entry.items() if k != 'library_count'}
    assert update['languages'] == [*batch.PRIMARY_CODES, *batch.LOCALES] and update['date'] == release['date']
    latest = (ROOT/'latest.html').read_text()
    mark = 'READER SERIES MONOPOLY LATEST'
    assert latest.count(f'data-update-id="{entry["id"]}"') == 1
    fragment, = re.findall(rf'<!-- {mark} START -->(.*?)<!-- {mark} END -->', latest, re.S)
    assert batch.BADGE in fragment and 'EN / 简 / 繁' not in fragment
    selected, = [row for row in primary.registry() if row['slug'] == batch.KEY]
    assert primary.library_card(selected, None) in (ROOT/'library.html').read_text()
    batch.discover_outputs(check=True)
    print(f'PASS monopoly: {len(pages_primary)+len(pages_foreign)} pages; source bodies, citations, routes, metadata and discovery')


def check_preservation(base):
    def old(path):
        return subprocess.check_output(['git', 'show', f'{base}:{path}'], cwd=ROOT)
    paths = ['index.html','library.html','essays/sae/index.html',
             *[f'essays/{language}/index.html' for language in batch.LOCALES]]
    shared = set(paths)
    boundary = DIRECTORY + '/'
    allowed_canonical = {parse_page(ROOT/path).canonical for path in [*paths,'latest.html']}
    for path in (ROOT/'data/search').glob('*.json'):
        old_rows = json.loads(old(path.relative_to(ROOT).as_posix())).get('records')
        if old_rows is None:
            continue
        new_rows = batch.read(path)['records']
        def outer(rows):
            return {r['u']: r for r in rows if r['u'] not in shared and not r['u'].startswith(boundary)}
        assert outer(old_rows) == outer(new_rows), (path, 'unrelated search drift')
    before = sitemap_entries(old('sitemap.xml'))
    after = sitemap_entries((ROOT/'sitemap.xml').read_bytes())
    assert before.keys() <= after.keys(), 'Prior sitemap URLs removed'
    prefix = ORIGIN + boundary
    assert all(after[url] == date for url, date in before.items()
               if url not in allowed_canonical and not url.startswith(prefix)), 'Unrelated sitemap date changed'
    assert all(url.startswith(prefix) for url in after.keys() - before.keys()), 'Unrelated sitemap URL added'
    old_updates = json.loads(old('data/site-updates.json'))['updates']
    new_updates = batch.read(ROOT/'data/site-updates.json')['updates']
    update_id = batch.read(BASE/'discovery.json')['id']
    def outside(rows):
        return [row for row in rows if row['id'] != update_id]
    assert outside(old_updates) == outside(new_updates), 'Unrelated ledger rows changed'
    print(f'PASS monopoly: unrelated search, sitemap and update ledger preserved from {base}')


def smoke():
    checks = [
        ('build_reader_series.py','--check'), ('test_reader_series.py',), ('test_reader_supplements.py',),
        ('check_site_updates.py',), ('build_home_updates.py','--check'), ('test_home_updates.py',),
        ('test_sitemap_recorded_dates.py',), ('check_web_analytics.py',),
    ]
    for script, *options in checks:
        subprocess.run([sys.executable, '-B', f'scripts/{script}', *options], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', help='Compare unrelated discovery records to this pre-release Git revision')
    parser.add_argument('--site-smoke', action='store_true', help='Also run all-site read-only reader/discovery/analytics smoke')
    args = parser.parse_args()
    check()
    if args.base:
        check_preservation(args.base)
    if args.site_smoke:
        smoke()


if __name__ == '__main__':
    main()
