#!/usr/bin/env python3
"""Mechanical publication checks, not a certification of translation quality.

Review records must separately describe the real semantic review and its limits.
Supports literary HTML and full reader editions without rewriting either source.
"""
import argparse
import html
import json
import re
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlsplit
from full_series_languages import ROOT, profile, render_prose
from prepare_action_sources import Document


def check(series):
    spec = profile(series)
    base = ROOT/'data'/series/'multilingual'
    directory = ROOT/spec['directory']
    sitemap = ET.parse(ROOT/'sitemap.xml').getroot()
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    urls = {node.find(ns+'loc').text for node in sitemap}
    paths = sorted(directory.glob('*.html'))
    assert {p.stem for p in paths} == {'index',*spec['slugs']}
    for language in spec['languages']:
        data = json.loads((base/f'{language}.json').read_text())
        assert [a['slug'] for a in data['articles']] == spec['slugs']
        translated = sorted((directory/language).glob('*.html'))
        assert {p.stem for p in translated} == {'index',*spec['slugs']}
        paths += translated
        for article in data['articles']:
            text = (directory/language/(article['slug']+'.html')).read_text()
            assert render_prose(article['body']) in text, (language,article['slug'],'body drift')
            assert not re.search(r'TODO|FIXME|\ufffd', '\n'.join(article['body']))
            if isinstance(article.get('coverage'), list):
                if (spec.get('source_format') == 'literary-html'
                        and article.get('source_note')
                        and len(article['coverage']) == len(article['body']) + 1):
                    # The final bibliographical source block may be rendered
                    # separately as an aside, never silently dropped.
                    source = json.loads((base/'source.json').read_text())['articles']
                    original = next(a for a in source if a['slug'] == article['slug'])
                    assert len(article['coverage']) == len(original['body_zh'])
                    assert html.escape(article['source_note']) in text
                else:
                    assert len(article['body']) == len(article['coverage'])
            elif 'coverage' in article:
                # Some literary editions describe coverage in prose. Their
                # per-block alignment is checked by the series validator.
                assert isinstance(article['coverage'], str) and article['coverage'].strip()
        records = json.loads((ROOT/'data/search'/f'{language}.json').read_text())['records']
        indexed = {r['u'] for r in records}
        assert len(indexed) == len(records), (language,'duplicate search record')
        for page in translated:
            assert page.relative_to(ROOT).as_posix() in indexed, page
        channel = (ROOT/f'essays/{language}/index.html').read_text()
        assert '../'+spec['directory'].removeprefix('essays/')+'/'+language+'/index.html' in channel
    for page in paths:
        text = page.read_text()
        doc = Document(text)
        canonical = [n.attrs['href'] for n in doc.root.walk() if n.tag=='link' and n.attrs.get('rel')=='canonical']
        assert len(canonical)==1 and canonical[0] in urls, page
        hreflang = [n.attrs.get('hreflang') for n in doc.root.walk() if n.tag=='link' and 'hreflang' in n.attrs]
        assert len(hreflang)==len(set(hreflang)), (page,hreflang)
        assert set(hreflang)-{'x-default'} == {'en','zh-Hans','zh-Hant','de','fr','es','ja','ko'}, (page,hreflang)
        assert text.count('cloudflareinsights.com/beacon.min.js')==1, page
        headings = len([n for n in doc.root.walk() if n.tag=='h1'])
        assert headings == 1 if page.parent.name in spec['languages'] else headings in (1,2,3), page
        for n in doc.root.walk():
            if n.tag not in ('a','link','script','img'):continue
            raw = n.attrs.get('href' if n.tag in ('a','link') else 'src','')
            u = urlsplit(raw)
            if not u.path or u.scheme or u.netloc:continue
            target = ROOT/unquote(u.path).lstrip('/') if u.path.startswith('/') else page.parent/unquote(u.path)
            assert target.exists(), (page,raw,'missing local target')
    ledger = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
    entry = json.loads((base/'discovery.json').read_text())
    assert sum(x['id']==entry['id'] for x in ledger)==1
    print(f'PASS {series}: {len(paths)} pages; bodies, eight language alternates, links, analytics, discovery')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series')
    check(parser.parse_args().series)
