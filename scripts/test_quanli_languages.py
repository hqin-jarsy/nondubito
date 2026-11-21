#!/usr/bin/env python3
"""Verify changes stay inside the approved five-locale Power proof surface."""
import argparse
import json
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

from build_content_registry import extract_canonical
from build_search_index import extract_search_text
from revise_quanli_languages import (
    ROOT, PAGES, SLUGS, LOCALES, CHANGES, body_span, digest, extract,
    load_editions, outputs, pretty, read, tokenize, write,
)


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.hrefs = []
        self.ids = set()
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and attrs.get('href'):
            self.hrefs.append(attrs['href'])
        if attrs.get('id'):
            self.ids.add(attrs['id'])


def article_paths():
    return [PAGES/lang/f'{slug}.html' for lang in LOCALES for slug in SLUGS]


def canonical(url):
    if url.endswith('/index.html'):
        return url[:-len('index.html')]
    return url


def check_routes():
    urls = {canonical(el.text) for el in ET.parse(ROOT/'sitemap.xml').findall('.//{*}loc')}
    for language in ('', *LOCALES):
        base = PAGES / language
        for slug in ['index', *SLUGS]:
            path = base/f'{slug}.html'
            text = read(path)
            url = 'https://nondubito.net/' + path.relative_to(ROOT).as_posix()
            assert canonical(extract_canonical(text)) == canonical(url), path
            assert canonical(url) in urls, path
            page = Page(text)
            actual = set()
            for href in page.hrefs:
                link = urlsplit(urljoin(url, href))
                if link.hostname != 'nondubito.net':
                    continue
                target = ROOT/unquote(link.path.lstrip('/'))
                if target.is_dir():
                    target /= 'index.html'
                assert target.is_file(), f'{path.relative_to(ROOT)}: {href}'
                if target.parent == base:
                    actual.add(target.stem)
            if slug == 'index':
                assert set(SLUGS) <= actual, path
            else:
                assert 'index' in actual, path
                n = SLUGS.index(slug)
                if n:
                    assert SLUGS[n-1] in actual, path
                if n+1 < len(SLUGS):
                    assert SLUGS[n+1] in actual, path


def snapshot():
    changed = article_paths()
    watched = [p for p in PAGES.rglob('*') if p.is_file() and p.suffix in ('.html','.js')]
    watched.extend([ROOT/n for n in ('sitemap.xml','library.html','index.html','latest.html',
                                    'data/search-index.json','essays/sae/index.html')])
    watched.extend([ROOT/f'essays/{l}/index.html' for l in LOCALES])
    watched.extend([ROOT/f'data/search/{l}.json' for l in ('en', 'zh-hans', 'zh-hant')])
    fixed = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(watched) if p not in changed}
    shells = {}
    for path in changed:
        text = read(path)
        a,b = body_span(text)
        shells[path.relative_to(ROOT).as_posix()] = sha256((text[:a]+text[b:]).encode()).hexdigest()
    queries = {}
    for locale in LOCALES:
        path = ROOT/f'data/search/{locale}.json'
        chunk = json.loads(read(path))
        paths = {f'essays/quanli/{locale}/{slug}.html' for slug in SLUGS}
        for record in chunk['records']:
            if record['u'] in paths:
                record.pop('q')
        queries[locale] = sha256(pretty(chunk).encode()).hexdigest()
    return {'fixed': fixed, 'shells': shells, 'queries_without_target_headings': queries}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot', type=Path,
                   help='write the baseline before the translation-only import')
    p.add_argument('--baseline', type=Path,
                   help='verify that everything except the 35 bodies and their 35 search queries stayed unchanged')
    args = p.parse_args()
    check_routes()
    if args.snapshot:
        write(args.snapshot, pretty(snapshot()))
        print('Baseline saved for all existing Power routes, academic notes, locales and discovery')
        return
    payloads = load_editions(CHANGES, extract(), scratch_names=False)
    for path, expected in outputs(payloads).items():
        assert read(path) == expected, path
    for lang, payload in payloads.items():
        indexed = {r['u']:r for r in json.loads(read(ROOT/f'data/search/{lang}.json'))['records']}
        for article in payload['articles']:
            path = PAGES / lang / f'{article["slug"]}.html'
            text = read(path)
            assert tokenize(text[slice(*body_span(text))], source=False) == article['body'], path
            record = indexed[path.relative_to(ROOT).as_posix()]
            assert record['q'] == extract_search_text(text), path
    if args.baseline:
        baseline = json.loads(read(args.baseline))
        current = snapshot()
        for section in current:
            assert baseline[section].keys() == current[section].keys(), section
            for name, value in current[section].items():
                assert baseline[section][name] == value, (section, name)
    print(f'Checked 48 existing routes; 35 exact localized bodies/search queries; baseline={bool(args.baseline)}')


if __name__ == '__main__':
    main()
