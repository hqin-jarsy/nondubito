#!/usr/bin/env python3
"""Read-only structure checks against current Chinese HTML, not literary review."""
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
ROOT = Path(__file__).resolve().parents[1]
KINDS = {'prose', 'verse', 'couplet', 'letter', 'diagram'}
class Reader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []; self.current = None; self.links = []; self.lang = None
        self.article = 0; self.articles = 0; self.ids = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang')
        if a.get('id'): self.ids.append(a['id'])
        if tag == 'article': self.article += 1; self.articles += 1
        if tag in ('a', 'link') and a.get('href'): self.links.append(a['href'])
        if tag == 'script' and a.get('src'): self.links.append(a['src'])
        if tag == 'p' and self.article and (KINDS & set(a.get('class', '').split()) or 'data-source-block' in a):
            assert self.current is None, 'Nested source paragraphs'
            self.current = dict(attrs=a, text='')
    def handle_data(self, data):
        if self.current is not None: self.current['text'] += data
    def handle_endtag(self, tag):
        if tag == 'p' and self.current is not None:
            self.blocks.append(self.current); self.current = None
        if tag == 'article': self.article -= 1

def read(path):
    doc = Reader(); doc.feed(path.read_text(encoding='utf-8')); doc.close()
    assert doc.current is None and doc.article == 0, ('Unclosed content', path)
    assert doc.articles == 1, ('Article count', path)
    assert len(doc.ids) == len(set(doc.ids)), ('Duplicate IDs', path)
    return doc

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--through', type=int, required=True)
    args = parser.parse_args()
    assert 1 <= args.through <= 80
    bindings = json.loads((ROOT / 'data/hongloumeng/first80-korean/source-bindings.json').read_text())
    for relative, digest in bindings['sources'].items():
        article = re.search(r'<article\b.*?</article>', (ROOT / relative).read_text(), re.S)
        assert article and hashlib.sha256(article[0].encode()).hexdigest() == digest, ('Source article changed', relative)
    print('PASS: Chinese source and Korean continuation article bindings unchanged')
    total = 0
    for n in range(1, args.through + 1):
        source = read(ROOT / f'classics/hongloumeng/ch{n:03}.html')
        path = ROOT / f'classics/hongloumeng/ko/ch{n:03}.html'
        doc = read(path)
        assert doc.lang == 'ko', (n, 'language')
        assert len(source.blocks) == len(doc.blocks), (n, 'block count', len(source.blocks), len(doc.blocks))
        for i, (s, b) in enumerate(zip(source.blocks, doc.blocks), 1):
            a = b['attrs']; kind = next(k for k in s['attrs']['class'].split() if k in KINDS)
            assert a.get('data-source-block') == str(i), (n, i, 'block order')
            assert a.get('data-kind') == kind and kind in a.get('class', '').split(), (n, i, 'block kind')
            assert set(s['attrs']['class'].split()) <= set(a.get('class', '').split()), (n, i, 'source layout classes')
            assert b['text'].strip(), (n, i, 'empty')
            assert '\ufffd' not in b['text'], (n, i, 'replacement character')
            assert 'translation-placeholder' not in a.get('class', ''), (n, i, 'Unresolved placeholder')
            if kind == 'prose' and len(b['text'].strip()) > 20:
                assert re.search(r'[가-힣]', b['text']), (n, i, 'Prose has no Korean text')
        for link in doc.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path: continue
            target = unquote(url.path)
            dest = ROOT / target.lstrip('/') if target.startswith('/') else path.parent / target
            assert dest.exists(), (n, 'broken local link', link)
        total += len(doc.blocks)
        print(f'Chapter {n}: {len(doc.blocks)} blocks, kinds, order and local links PASS')
    print(f'PASS: {args.through} chapters, {total} blocks. These checks do not certify translation accuracy.')
if __name__ == '__main__': main()
