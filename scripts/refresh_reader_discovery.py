#!/usr/bin/env python3
"""Refresh one reader series; preserve unrelated records and sitemap dates."""
import argparse
import json
import xml.etree.ElementTree as ET
from unittest.mock import patch
import build_search_index as search
from build_reader_series import ROOT,registry
from build_sitemap import parse_page,sitemap_xml


def render(slug):
    s = next(s for s in registry() if s['slug']==slug)
    paths = sorted((ROOT/f'essays/{slug}').glob('*.html'))
    assert len(paths)==s['count']+1
    paths += [ROOT/p for p in ('index.html','library.html','essays/sae/index.html')]
    scope = {p.relative_to(ROOT).as_posix() for p in paths}
    with patch.object(search,'collect_pages',lambda:paths):
        _,fresh = search.build()
    manifest = json.loads(search.OUTPUT.read_text())
    added = set()
    outputs = {}
    for lang,replacements in fresh.items():
        path = search.CHUNKS_DIR/f'{lang.lower()}.json'
        chunk = json.loads(path.read_text())
        existing = {r['u'] for r in chunk['records']}
        added.update(r['u'] for r in replacements if r['u'] not in existing)
        by_url = {r['u']:r for r in replacements}
        chunk['records'] = [by_url.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']]
        chunk['records'].extend(by_url.values())
        if replacements:outputs[path]=search.serialized(chunk)
        manifest['languages'][lang]['count']=len(chunk['records'])
    manifest['record_count']+=len(added)
    outputs[search.OUTPUT]=search.serialized(manifest)
    sitemap = ROOT/'sitemap.xml'
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    entries = {u.find(ns+'loc').text:u.find(ns+'lastmod').text for u in ET.parse(sitemap).getroot()}
    for path in paths+[ROOT/'latest.html']:
        canonical = parse_page(path).canonical
        assert canonical.startswith('https://nondubito.net/')
        entries[canonical]=s['date']
    outputs[sitemap]=sitemap_xml(sorted(entries.items(),key=lambda x:(x[0]!='https://nondubito.net/',x[0])))
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series')
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    for path,text in render(args.series).items():
        if args.check:assert path.read_text()==text,f'Stale scoped discovery: {path}'
        else:path.write_text(text)
    print(('Checked' if args.check else 'Refreshed')+f' scoped discovery: {args.series}; unrelated entries retained')


if __name__=='__main__':main()
