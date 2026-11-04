#!/usr/bin/env python3
"""Connect a fully reviewed append-only companion; never replace its old index."""
import argparse

from companion_languages import ROOT, availability, native_indexes, primary_index, upgrade_companion_primary
from full_series_languages import profile


def render(series):
    spec=profile(series)
    pages=native_indexes(series)
    pages.update(primary_index(series))
    if series=='foundations-companion':
        path=ROOT/spec['directory']/(spec['slugs'][0]+'.html')
        pages[path]=upgrade_companion_primary(path.read_text(),series)
    if series=='method-companion':
        path=ROOT/'library.html'
        pages[path]=availability(path.read_text())
    return pages


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series',choices=['method-companion','foundations-companion'])
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    for path,text in render(args.series).items():
        if args.check:assert path.read_text()==text,path
        else:path.write_text(text)
    print(args.series+': original routes preserved; companion entries '+('checked' if args.check else 'connected'))


if __name__=='__main__':main()
