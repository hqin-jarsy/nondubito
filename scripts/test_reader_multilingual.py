#!/usr/bin/env python3
"""Scoped publication checks for the four November reader-language batches.

These mechanical checks do not certify translation quality. The separate review
record identifies the actual editorial comparisons and their limits.
"""
import argparse
import hashlib
import html
import json
import re
from urllib.parse import unquote, urlsplit
from full_series_languages import ROOT, load_language, profile, render
from build_reader_series import render as render_primary, registry, library_card
from test_language_writing import Tags

SERIES = ('classical-concepts', 'teacher-student', 'university', 'own-faith')

def plain(value):
    return html.unescape(re.sub('<[^>]+>', '', value))

def check(series):
    spec = profile(series)
    base = ROOT / 'data' / series / 'multilingual'
    receipt = json.loads((base / 'publication.json').read_text())
    assert receipt['result'] == 'passed' and receipt['unresolved'] == []
    assert set(receipt['language_data_sha256']) == set(spec['languages'])
    for name, digest in receipt['review_report_sha256'].items():
        report = base / name
        assert hashlib.sha256(report.read_bytes()).hexdigest() == digest
        assert json.loads(report.read_text())['remaining'] == []
    for language, digest in receipt['language_data_sha256'].items():
        assert hashlib.sha256((base / (language + '.json')).read_bytes()).hexdigest() == digest
    for slug, digest in receipt['source_zh_sha256'].items():
        original = json.loads((base.parent / (slug + '.json')).read_text())
        assert hashlib.sha256(json.dumps(original['body_zh'], ensure_ascii=False).encode()).hexdigest() == digest
    pages = render(series)
    assert len(pages) == 5 * (len(spec['slugs']) + 1)
    for language in spec['languages']:
        _, data = load_language(series, language)
        records = json.loads((ROOT / 'data/search' / (language + '.json')).read_text())['records']
        indexed = {r['u'] for r in records}
        for article in data['articles']:
            path = ROOT / spec['directory'] / language / (article['slug'] + '.html')
            body = re.search(r'<div class="essay-body lw-prose"[^>]*>(.*?)</div>', pages[path], re.S)[1]
            paragraphs = re.findall(r'<(?:p|h2)>(.*?)</(?:p|h2)>', body, re.S)
            assert [plain(p) for p in paragraphs] == [plain(p.removeprefix('## ')) for p in article['body']], path
            assert len(article['body']) == len(article['coverage'])
            assert not re.search(r'TODO|FIXME|\ufffd', body), path
            for ref in article['references']:
                assert html.escape(ref['url'], quote=True) in pages[path]
        for slug in ['index', *spec['slugs']]:
            assert spec['directory'] + '/' + language + '/' + slug + '.html' in indexed
        assert '../' + series + '/' + language + '/index.html' in (ROOT / 'essays' / language / 'index.html').read_text()
    sitemap = (ROOT / 'sitemap.xml').read_text()
    for path, text in pages.items():
        assert path.read_text() == text, path
        canonical = 'https://nondubito.net/' + path.relative_to(ROOT).as_posix().removesuffix('index.html')
        assert f'rel="canonical" href="{canonical}"' in text and canonical in sitemap
        assert text.count('<h1>') == 1
        menu = re.search(r'<div class="site-shell-language-options">(.*?)</div>', text, re.S)[1]
        assert menu.count('<a ') == 8 and menu.count('aria-current="page"') == 1
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)[1])
        assert schema['inLanguage'] == path.parent.name
        assert text.count('cloudflareinsights.com/beacon.min.js') == 1
        for tag, attrs in Tags(text).items:
            raw = attrs.get('href' if tag in ('a', 'link') else 'src', '')
            parts = urlsplit(raw)
            if not raw or parts.scheme or parts.netloc:
                continue
            target = ROOT / unquote(parts.path.lstrip('/')) if parts.path.startswith('/') else path.parent / unquote(parts.path)
            if parts.path:
                assert target.is_file(), (path, raw)
            if parts.fragment:
                source = target.read_text() if parts.path else text
                assert re.search(r'\bid=["\']' + re.escape(parts.fragment) + r'["\']', source), (path, raw)
    for path, text in render_primary(series).items():
        assert path.read_text() == text, path
    selected = next(s for s in registry() if s['slug'] == series)
    assert library_card(selected, None) in (ROOT / 'library.html').read_text(), series
    entry = json.loads((base / 'discovery.json').read_text())
    updates = json.loads((ROOT / 'data/site-updates.json').read_text())['updates']
    assert sum(u['id'] == entry['id'] for u in updates) == 1
    print(f'{series}: {len(pages)} translated pages, primary rendering, prose, references, navigation and discovery passed')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series', choices=SERIES, nargs='*')
    args = parser.parse_args()
    for series in args.series or SERIES:
        check(series)
