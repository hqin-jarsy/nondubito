#!/usr/bin/env python3
"""Check one literary series refresh did not rewrite unrelated discovery records.

Run before committing, or pass --base with the preceding commit afterward.
Canonical URLs (including directory-form Home/channel URLs) define sitemap scope.
"""
import argparse
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from full_series_languages import ROOT, profile
from build_sitemap import parse_page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series')
    parser.add_argument('--base', default='HEAD')
    args = parser.parse_args()
    spec = profile(args.series)
    assert spec['source_format'] == 'literary-html'
    prefix = spec['directory'] + '/'
    shared = {'index.html', 'library.html', 'essays/literature/index.html'}
    shared.update(f'essays/{language}/index.html' for language in spec['languages'])

    def previous(path):
        return subprocess.check_output(['git', 'show', f'{args.base}:{path}'], cwd=ROOT)

    for path in sorted((ROOT / 'data/search').glob('*.json')):
        old = json.loads(previous(path.relative_to(ROOT).as_posix()))
        new = json.loads(path.read_text())
        if 'records' not in old:
            continue

        def outside(data):
            return {row['u']: row for row in data['records']
                    if not row['u'].startswith(prefix) and row['u'] not in shared}

        assert outside(old) == outside(new), ('unrelated search record changed', path)

    allowed = {parse_page(ROOT / path).canonical for path in shared | {'latest.html'}}
    namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'

    def entries(text):
        return {node.find(namespace + 'loc').text: node.find(namespace + 'lastmod').text
                for node in ET.fromstring(text)}

    before = entries(previous('sitemap.xml'))
    after = entries((ROOT / 'sitemap.xml').read_text())
    assert not set(before) - set(after), 'prior sitemap URLs removed'
    for url, date in before.items():
        if url.startswith('https://nondubito.net/' + prefix) or url in allowed:
            continue
        assert after[url] == date, ('unrelated sitemap date changed', url)
    print(f'PASS {args.series}: unrelated search records and sitemap dates preserved from {args.base}')


if __name__ == '__main__':
    main()
