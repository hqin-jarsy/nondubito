#!/usr/bin/env python3
"""Render the reviewed Chapter 1 manuscripts; never translate or rewrite them.

Only the five foreign-language essay bodies are opted in. Existing page shells,
adopted Chinese chapter texts, navigation and Chinese/English editions stay put.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import markdown
from build_emperor_full_editions import replace_div

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/daodejing-full'
LANGS = ('ja', 'fr', 'de', 'es', 'ko')


def digest(value):
    return hashlib.sha256(value).hexdigest()


def render(lang, receipt):
    raw = (DATA / f'ch01.{lang}.md').read_bytes()
    record = receipt['languages'][lang]
    if digest(raw) != record['published_sha256']:
        raise ValueError(f'{lang}: reviewed manuscript checksum differs')
    text = raw.decode('utf-8')
    if not text.startswith('# ') or len(re.findall(r'^# ', text, re.M)) != 1:
        raise ValueError(f'{lang}: expected one manuscript title')
    body = markdown.markdown(text.split('\n', 1)[1].strip())
    for tag, field in [('h2', 'sections'), ('p', 'paragraphs'), ('blockquote', 'blockquotes')]:
        if body.count(f'<{tag}>') != record[field]:
            raise ValueError(f'{lang}: unexpected {field} count')
    return body


def updates():
    receipt = json.loads((DATA / 'ch01-review.json').read_text())
    if set(receipt['languages']) != set(LANGS):
        raise ValueError('Unexpected language scope')
    # Validate every target before writing any output.
    result = []
    for lang in LANGS:
        path = ROOT / f'essays/daodejing/{lang}/ch01.html'
        old = path.read_text()
        result.append((path, old, replace_div(old, 'essay-body', render(lang, receipt))))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    pending = [(path, new) for path, old, new in updates() if old != new]
    if args.check:
        if pending:
            raise SystemExit('Stale pages: ' + ', '.join(str(p.relative_to(ROOT)) for p, _ in pending))
        print('OK: five reviewed Chapter 1 editions match their manuscripts')
    else:
        for path, text in pending:
            path.write_text(text)
        print(f'Updated {len(pending)} Chapter 1 essay bodies')


if __name__ == '__main__':
    main()
