#!/usr/bin/env python3
"""Refresh only the new short-fiction shelf and its publication entrances."""
import argparse
import json
import xml.etree.ElementTree as ET
from unittest.mock import patch
import build_search_index as search
from build_sitemap import parse_page, sitemap_xml
from build_socrates_original import ROOT, DATE, render as story_pages


def render():
    paths=list(story_pages())+[ROOT/p for p in ('originals/index.html','library.html','index.html')]
    scope={p.relative_to(ROOT).as_posix() for p in paths}
    with patch.object(search,'collect_pages',lambda:paths):
        _,fresh=search.build()
    manifest=json.loads(search.OUTPUT.read_text());outputs={};added=set()
    for lang,replacements in fresh.items():
        path=search.CHUNKS_DIR/f'{lang.lower()}.json';chunk=json.loads(path.read_text())
        known={r['u'] for r in chunk['records']}
        added.update(r['u'] for r in replacements if r['u'] not in known)
        by_url={r['u']:r for r in replacements}
        chunk['records']=[by_url.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']]
        chunk['records'].extend(by_url.values())
        if replacements:outputs[path]=search.serialized(chunk)
        manifest['languages'][lang]['count']=len(chunk['records'])
    manifest['record_count']+=len(added)
    outputs[search.OUTPUT]=search.serialized(manifest)
    path=ROOT/'sitemap.xml';ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    entries={u.find(ns+'loc').text:u.find(ns+'lastmod').text for u in ET.parse(path).getroot()}
    for p in paths+[ROOT/'latest.html']:
        canonical=parse_page(p).canonical
        assert canonical.startswith('https://nondubito.net/')
        entries[canonical]=max(entries.get(canonical,DATE),DATE)
    outputs[path]=sitemap_xml(list(entries.items()))
    return outputs


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');a=parser.parse_args()
    for path,text in render().items():
        if a.check:assert path.read_text()==text,f'Stale scoped discovery: {path}'
        else:path.write_text(text)
    print(('Checked' if a.check else 'Refreshed')+' Socrates discovery; unrelated records and sitemap dates retained')

if __name__=='__main__':main()
