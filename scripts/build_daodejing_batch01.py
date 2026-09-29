#!/usr/bin/env python3
"""Render the reviewed introduction and chapters 2–5, without rewriting prose."""
import argparse
import json
import re

import markdown
from build_daodejing_full_editions import ROOT, DATA, LANGS, digest, replace_div

CHAPTERS = ('daoyan', 'ch02', 'ch03', 'ch04', 'ch05')


def render(key, record):
    raw = (DATA / f'{key}.md').read_bytes()
    if digest(raw) != record['published_sha256']:
        raise ValueError(f'{key}: reviewed manuscript checksum differs')
    text = raw.decode('utf-8')
    if not text.startswith('# ') or len(re.findall(r'^# ', text, re.M)) != 1:
        raise ValueError(f'{key}: expected one title')
    body = markdown.markdown(text.split('\n', 1)[1].strip())
    for tag, field in [('h2', 'sections'), ('p', 'paragraphs'), ('blockquote', 'blockquotes')]:
        if body.count(f'<{tag}>') != record[field]:
            raise ValueError(f'{key}: unexpected {field} count')
    return body


def updates():
    receipt = json.loads((DATA / 'batch01-review.json').read_text())
    expected = {f'{chapter}.{lang}' for chapter in CHAPTERS for lang in LANGS}
    if set(receipt['manuscripts']) != expected:
        raise ValueError('Unexpected manuscript scope')
    result = []
    for key, record in receipt['manuscripts'].items():
        chapter, lang = key.split('.')
        path = ROOT / f'essays/daodejing/{lang}/{chapter}.html'
        old = path.read_text()
        result.append((path, old, replace_div(old, 'essay-body', render(key, record))))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    pending = [(path, new) for path, old, new in updates() if old != new]
    if args.check:
        if pending:
            raise SystemExit('Stale pages: ' + ', '.join(str(p.relative_to(ROOT)) for p, _ in pending))
        print('OK: 25 reviewed editions match their manuscripts')
    else:
        for path, text in pending:
            path.write_text(text)
        print(f'Updated {len(pending)} essay bodies')


if __name__ == '__main__':
    main()
