#!/usr/bin/env python3
"""Scoped discovery refresh for reviewed film editions; leave other records alone."""
import json
import re
import xml.etree.ElementTree as ET
import build_search_index as search
from build_sitemap import parse_page,sitemap_xml
from build_film_full_editions import outputs,UI,LANGS,E,DATE,ROOT

def refresh():
    paths=list(outputs())
    for lang in LANGS:
        p=ROOT/'essays'/lang/'index.html';s=p.read_text();u=UI[lang]
        block=f'<!-- FILM FULL EDITIONS START --><section class="essays-section" style="padding:2rem 0"><a href="../film/{lang}/index.html" class="essay-card" style="display:block;text-decoration:none;border-left:3px solid var(--gold);padding:2rem"><h2 style="font-size:1.6rem;font-weight:400">{E(u["cinema"])}</h2><p>{E(u["intro"])}</p><p>{E(u["published"])}</p></a></section><!-- FILM FULL EDITIONS END -->'
        if '<!-- FILM FULL EDITIONS START -->' in s:
            s=re.sub(r'<!-- FILM FULL EDITIONS START -->.*?<!-- FILM FULL EDITIONS END -->',lambda m:block,s,flags=re.S)
        else:
            at=s.index('<section class="essays-section"');s=s[:at]+block+'\n'+s[at:]
        p.write_text(s);paths.append(p)
    scope={str(p.relative_to(ROOT)) for p in paths}
    previous=search.collect_pages
    try:
        search.collect_pages=lambda:paths
        _,fresh=search.build()
    finally:search.collect_pages=previous
    manifest=json.loads(search.OUTPUT.read_text())
    for lang,replacements in fresh.items():
        path=search.CHUNKS_DIR/f'{lang.lower()}.json';chunk=json.loads(path.read_text())
        by_url={r['u']:r for r in replacements}
        chunk['records']=[by_url.pop(r['u'],r) if r['u'] in scope else r for r in chunk['records']]
        chunk['records'].extend(by_url.values())
        if replacements:path.write_text(search.serialized(chunk))
        manifest['languages'][lang]['count']=len(chunk['records'])
    manifest['record_count']=sum(v['count'] for v in manifest['languages'].values())
    search.OUTPUT.write_text(search.serialized(manifest))
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';path=ROOT/'sitemap.xml'
    entries={u.find(ns+'loc').text:u.find(ns+'lastmod').text for u in ET.parse(path).getroot()}
    for p in paths+[ROOT/'latest.html']:
        canonical=parse_page(p).canonical;assert canonical.startswith('https://nondubito.net/')
        entries[canonical]=DATE
    path.write_text(sitemap_xml(sorted(entries.items(),key=lambda x:(x[0]!='https://nondubito.net/',x[0]))))
    print(f'Refreshed {len(scope)} film/discovery pages')

if __name__=='__main__':refresh()
