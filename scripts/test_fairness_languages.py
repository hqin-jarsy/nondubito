#!/usr/bin/env python3
"""Mechanical checks for the five complete Fairness editions.

These checks verify completeness and routes, not editorial correctness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import build_fairness_languages as batch
import build_reader_series as primary
import full_series_languages as languages
from build_sitemap import parse_page
from test_monopoly_languages import body_and_refs, check_page, sitemap_entries

ROOT, BASE = batch.ROOT, batch.BASE
ORIGIN = 'https://nondubito.net/'
DIRECTORY = batch.DIRECTORY

def check():
    spec = languages.profile(batch.KEY)
    release, slugs, _ = batch.master_spec()
    primary_pages = primary.render(batch.KEY)
    localized_pages = languages.render(batch.KEY)
    assert len(primary_pages) == 13 and len(localized_pages) == 65
    originals = {slug: batch.read(BASE.parent/(slug+'.json')) for slug in slugs}
    sitemap = sitemap_entries((ROOT/'sitemap.xml').read_bytes())
    for path, text in primary_pages.items():
        assert path.read_text() == text, path
        doc, nodes = check_page(path,text,spec,path.stem,None,sitemap)
        if path.stem != 'index':
            body_and_refs(doc,nodes,path,None,originals[path.stem])
    for lang in spec['languages']:
        _, data = languages.load_language(batch.KEY, lang)
        records = batch.read(ROOT/'data/search'/f'{lang}.json')['records']
        indexed = {row['u']:row for row in records}
        assert len(indexed)==len(records), lang
        language_hub = (ROOT/'essays'/lang/'index.html').read_text()
        assert language_hub.count(f'../fairness/{lang}/index.html') == 1
        physical = ROOT/DIRECTORY/lang
        assert {p.stem for p in physical.glob('*.html')} == {'index', *slugs}, physical
        for article in [None, *data['articles']]:
            slug = article['slug'] if article else 'index'
            path = physical/(slug+'.html')
            text = path.read_text()
            assert text == localized_pages[path], path
            rel = path.relative_to(ROOT).as_posix()
            assert indexed[rel]['d']=='sae-philosophy', (lang, rel)
            assert indexed[rel]['x']==(article or data['series'])['deck'], (lang,rel,'localized deck drift')
            canonical = ORIGIN + rel.removesuffix('index.html')
            assert sitemap[canonical] == spec['date'], path
            doc, nodes = check_page(path,text,spec,slug,lang,sitemap)
            if article is None:
                for g in spec['index_groups']:
                    group, = [n for n in nodes if n.attrs.get('id') == g['id']]
                    assert [n.attrs['href'] for n in group.walk() if n.has('lw-card')]==[slug+'.html' for slug in g['slugs']], (lang,g['id'])
                assert [len(g['slugs']) for g in spec['index_groups']]==[6,5,1], lang
                continue
            n = slugs.index(slug)
            neighbors = [slugs[j]+'.html' if 0 <= j < len(slugs) else 'index.html#reading-route' for j in (n-1,n+1)]
            nav, = [node for node in nodes if node.has('lw-series-nav')]
            assert [node.attrs['href'] for node in nav.walk() if node.tag=='a'] == neighbors, path
            assert article['source_sha256']==hashlib.sha256((BASE.parent/(slug+'.json')).read_bytes()).hexdigest(), path
            body_and_refs(doc,nodes,path,article)
    for lang in ('en','zh-hans','zh-hant'):
        records=batch.read(ROOT/'data/search'/f'{lang}.json')['records']
        indexed={r['u'] for r in records}
        assert {path.relative_to(ROOT).as_posix() for path in primary_pages} <= indexed, lang
    entry = batch.read(BASE/'discovery.json')
    assert entry['languages']==[*batch.PRIMARY_CODES,*batch.LOCALES]
    entries=batch.read(ROOT/'data/site-updates.json')['updates']
    added, = [u for u in entries if u['id']==entry['id']]
    assert added=={k:v for k,v in entry.items() if k!='library_count'}
    prior, = [u for u in entries if u['id']==release['date']+'-fairness-reader-series']
    assert prior['languages']==batch.PRIMARY_CODES
    assert (ROOT/'latest.html').read_text().count(f'data-update-id="{entry["id"]}"')==1
    selected,=(r for r in primary.registry() if r['slug']==batch.KEY)
    assert primary.library_card(selected,None) in (ROOT/'library.html').read_text()
    batch.discover_outputs(check=True)
    print('PASS Fairness: 13 primary pages, 65 localized pages, all bodies, source references, reading groups and discovery.')

def preservation(base):
    def old(path):
        return subprocess.check_output(['git','show',f'{base}:{path}'],cwd=ROOT)
    shared = ['index.html','library.html','essays/sae/index.html',*[f'essays/{lang}/index.html' for lang in batch.LOCALES]]
    boundary=DIRECTORY+'/'
    for path in (ROOT/'data/search').glob('*.json'):
        earlier=json.loads(old(path.relative_to(ROOT).as_posix())).get('records')
        if earlier is None:continue
        current=batch.read(path)['records']
        def other(rows):return {r['u']:r for r in rows if r['u'] not in shared and not r['u'].startswith(boundary)}
        assert other(earlier)==other(current),(path,'unrelated search drift')
    before=sitemap_entries(old('sitemap.xml'))
    after=sitemap_entries((ROOT/'sitemap.xml').read_bytes())
    canonicals={parse_page(ROOT/p).canonical for p in [*shared,'latest.html']}
    assert before.keys() <= after.keys()
    assert all(after[u]==date for u,date in before.items() if u not in canonicals and not u.startswith(ORIGIN+boundary))
    assert all(u.startswith(ORIGIN+boundary) for u in after.keys()-before.keys())
    for slug in ['publication',*batch.master_spec()[1]]:
        path=f'data/fairness/{slug}.json'
        assert (ROOT/path).read_bytes()==old(path), path
    for slug in ['index',*batch.master_spec()[1]]:
        path=f'{DIRECTORY}/{slug}.html'
        src=old(path).decode()
        dst=(ROOT/path).read_text()
        for css in batch.PROTECTED_CLASSES:
            assert batch.protected(src,css)==batch.protected(dst,css),(path,css)
    ledger='data/site-updates.json'
    addition=batch.read(BASE/'discovery.json')['id']
    assert json.loads(old(ledger))['updates']==[u for u in batch.read(ROOT/ledger)['updates'] if u['id']!=addition]
    print(f'PASS original Fairness bodies/metadata and unrelated search/sitemap/update records preserved from {base}')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',help='Pre-expansion Git revision for unrelated-content checks')
    args=parser.parse_args()
    check()
    if args.base:preservation(args.base)
