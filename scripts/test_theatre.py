#!/usr/bin/env python3
"""Content, metadata, language parity, links, and discovery checks for theatre."""
import json
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

from build_theatre import ROOT, load, outputs
from build_content_registry import scan_page, parse_library_categories


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag in ('script', 'link'):
            self.links.append(attrs.get('src', attrs.get('href', '')))


for path, expected in outputs().items():
    source = path.read_text()
    assert source == expected, path
    record = scan_page(ROOT, path)
    assert record['domain'] == 'stories' and record['category'] == 'theatre', record
    assert set(record['languages']) == {'en', 'zh-Hans', 'zh-Hant'}, record
    assert all(record['titles'].get(l) for l in ('en', 'zh-Hans', 'zh-Hant'))
    links = Links()
    links.feed(source)
    for href in links.links:
        url = urlsplit(href)
        if url.scheme or not url.path:
            continue
        target = (path.parent / unquote(url.path)).resolve()
        assert target.is_file(), (path, href)
    if path.name == 'hamilton.html':
        articles = re.findall(r'<article class="rf-prose lang-\w+"[^>]*>(.*?)</article>', source, re.S)
        assert len(articles) == 3
        assert all(a.count('<h2>') == 4 for a in articles)
        assert len({a.count('<p') for a in articles}) == 1, 'paragraph parity'
        assert not any('<a ' in a for a in articles), 'no inline links'
        schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', source, re.S).group(1))
        assert schema['@type'] == 'Article' and schema['about']['@type'] == 'CreativeWork'
        assert 'Book' not in schema['about'].values()
        assert len(load('en')[2].split()) > 1800, 'complete translation, not a summary'
        assert len(load('zh')[2]) > 3500

categories = parse_library_categories(ROOT / 'library.html')
assert len(categories) == 18
assert len({c['number'] for c in categories}) == 18
assert any(c['href'] == 'essays/theatre/index.html' for c in categories)
for filename in ('index.html', 'explore.html', 'library.html', 'latest.html'):
    assert 'essays/theatre/index.html' in (ROOT / filename).read_text(), filename
for language in ('en', 'zh-hans', 'zh-hant'):
    records = json.loads((ROOT / f'data/search/{language}.json').read_text())['records']
    matches = [r for r in records if r['u'].startswith('essays/theatre/')]
    assert len(matches) == 2 and all(r['d'] == 'stories' for r in matches)
for url in ('https://nondubito.net/essays/theatre/', 'https://nondubito.net/essays/theatre/hamilton.html'):
    assert f'<loc>{url}</loc>' in (ROOT / 'sitemap.xml').read_text()
print('OK: theatre content, full translation, metadata, local links, and discovery')
