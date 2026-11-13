#!/usr/bin/env python3
"""Bounded reversible navigation additions. Does not write files by itself."""
READERS = tuple(f'classics/hongloumeng/{directory}{filename}' for directory in ('','zh-hant/','en/') for filename in ('index.html','edition.html',*(f'ch{n:03}.html' for n in range(1,81))))
CONTINUATIONS = ('originals/hongloumeng/ja/index.html','originals/hongloumeng/ja/ch081.html')
TARGETS = READERS + CONTINUATIONS
START = '<!-- JAPANESE-NAV:START -->'
END = '<!-- JAPANESE-NAV:END -->'

def additions(relative):
    if relative not in TARGETS: raise ValueError('Outside Japanese navigation scope')
    if relative in READERS:
        filename=relative.rsplit('/',1)[1]
        path='/classics/hongloumeng/ja/'+('' if filename=='index.html' else filename)
        head=f'<link rel="alternate" hreflang="ja" href="https://nondubito.net{path}">'
        body=f'<span class="japanese-reading-entry"><a lang="ja" href="{path}">日本語</a></span>'
        anchor='</nav></header>'
    else:
        head=''
        target='ch080.html' if relative.endswith('ch081.html') else ''
        anchor='<header class="chapter-head">' if target else '<header class="collection-head">'
        body=f'<nav class="chapter-nav japanese-reading-entry" aria-label="原著前八十回"><a href="/classics/hongloumeng/ja/{target}">← 原著・'+('第八十回' if target else '前八十回の回目一覧')+'</a></nav>'
    return [('</head>',head),(anchor,body)] if head else [(anchor,body)]

def transform(relative,payload):
    text=payload.decode('utf-8')
    if START in text or END in text: raise ValueError('Navigation already present or malformed')
    for anchor,addition in additions(relative):
        if text.count(anchor)!=1: raise ValueError('Ambiguous HTML insertion anchor')
        text=text.replace(anchor,START+addition+END+anchor)
    return text.encode('utf-8')

def reverse(relative,payload):
    text=payload.decode('utf-8')
    for anchor,addition in additions(relative):
        block=START+addition+END+anchor
        if text.count(block)!=1: raise ValueError('Modified or missing bounded navigation')
        text=text.replace(block,anchor)
    if START in text or END in text: raise ValueError('Unexpected navigation markers')
    return text.encode('utf-8')
