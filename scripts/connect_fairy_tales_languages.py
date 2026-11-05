"""Honest discovery: only Fairy Tales is upgraded, not the entire story shelf."""
import argparse
import re

from connect_full_series_languages import render as render_shared
from full_series_languages import ROOT


def render():
    pages=render_shared('fairy-tales')
    path=ROOT/'essays/everyday/stories/index.html'
    text=path.read_text()
    labels=iter(['30 essays · Eight complete languages','30 篇 · 八语全文','30 篇 · 八語全文'])
    pattern=r'(<a class="collection-card" href="fairy-tales/index.html"><div><span class="count">).*?(</span>)'
    text,n=re.subn(pattern,lambda m:m[1]+next(labels)+m[2],text,flags=re.S)
    assert n==3,'Expected precisely one fairy-tale card in each original reading mode'
    pages[path]=text
    return pages


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    for path,text in render().items():
        if args.check:assert path.read_text()==text,path
        else:path.write_text(text)
    print('fairy-tales: language channels, honest story-shelf card, Library, Latest and Home '+('checked' if args.check else 'connected'))


if __name__=='__main__':main()
