#!/usr/bin/env python3
"""Verify the eight-edition coverage advertised by Run with the Wind labels.

Structural/content-presence regression, not a claim of translation-quality review.
"""
import json
from pathlib import Path
import re
from prepare_action_sources import Document

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'essays/literature/run-with-the-wind'
LANGS = ('ja', 'fr', 'de', 'es', 'ko')
PAGES = sorted(BASE.glob('*.html'))
assert len(PAGES) == 6
for p in PAGES:
    source = p.read_text()
    doc = Document(source)
    nodes = list(doc.root.walk())
    toggle = next(n for n in nodes if n.has('lang-toggle'))
    buttons = [n for n in toggle.walk() if n.has('lang-btn')]
    assert len(buttons) == 8, p
    for code in ('en', 'zh'):
        body = next(n for n in nodes if n.has('essay-body', 'lang-' + code))
        assert len(body.text().strip()) > 500, (p, code)
    dictionary = (BASE / 'zh-hant-data' / (p.stem + '.js')).read_text()
    variants = json.loads(re.search(r'var variants = (\{.*?\});', dictionary, re.S)[1])
    assert len(variants) > 20, p
    assert '8 種語言' in variants.values() or '中文原作 · 8 種語言' in variants.values(), p
    assert '8 languages' in source and '8 种语言' in source, p
    assert all(s not in source for s in ('Three reading modes', 'English · Simplified · Traditional', '英 · 简 · 繁')), p
    template = ROOT / 'data/anime-full/templates/run-with-the-wind' / p.name
    assert '8 languages' in template.read_text(), template
    for lang in LANGS:
        target = BASE / lang / p.name
        assert any(n.attrs.get('href') == lang + '/' + p.name for n in buttons), (p, lang)
        translated = Document(target.read_text())
        tn = list(translated.root.walk())
        assert next(n for n in tn if n.tag == 'html').attrs['lang'] == lang
        menu = next(n for n in tn if n.has('lang-toggle'))
        assert len([n for n in menu.walk() if n.has('lang-btn')]) == 8, target
        for link in menu.walk():
            if link.tag == 'a':
                assert (target.parent / link.attrs['href']).resolve().is_file(), (target, link.attrs)
        if p.name == 'index.html':
            assert len([n for n in tn if n.has('entry-row')]) == 5, target
        else:
            body = next(n for n in tn if n.has('essay-body'))
            assert len(body.text()) > 1000, target
            assert len([n for n in body.walk() if n.tag == 'p']) > 10, target
for file in ('library.html', 'essays/anime/index.html'):
    doc = Document((ROOT / file).read_text())
    cards = [n for n in doc.root.walk() if n.tag == 'a' and 'run-with-the-wind/index.html' in (n.attrs.get('href') or '')]
    assert len(cards) == 1
    assert '5 essays · 8 languages' in cards[0].text() and '5 篇 · 8 种语言' in cards[0].text()
library = Document((ROOT / 'library.html').read_text())
stat = next(n for n in library.root.walk() if n.has('stat-item') and 'Languages' in n.text())
assert next(n for n in stat.walk() if n.has('stat-num')).text() == '8'
print('PASS: 6 root pages + 30 translated pages; eight-way selectors, live targets, content, Traditional assets, templates, library/category labels, site coverage stat.')
