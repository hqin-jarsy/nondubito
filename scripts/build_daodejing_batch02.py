#!/usr/bin/env python3
"""Render reviewed chapters 6–10 without translating or rewriting the prose."""
import argparse
import json

from build_daodejing_batch01 import ROOT, DATA, LANGS, render, replace_div, digest

CHAPTERS = ('ch06', 'ch07', 'ch08', 'ch09', 'ch10')


def updates():
    receipt = json.loads((DATA / 'batch02-review.json').read_text())
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
        print('OK: 25 reviewed chapters 6–10 match their manuscripts')
    else:
        for path, text in pending:
            path.write_text(text)
        print(f'Updated {len(pending)} essay bodies')


if __name__ == '__main__':
    main()
