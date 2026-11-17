#!/usr/bin/env python3
"""Pure rendering helpers for reader supplements, not another top-level shelf.

Proposed destination: nondubito/scripts/reader_supplements.py.
This module never writes files. Dependencies on the existing reader builder are
lazy, avoiding a cycle when the builder itself imports these helpers.
"""
from __future__ import annotations

import html
import posixpath
import re
from pathlib import PurePosixPath

START = '<!-- READER PARENT EXTENSIONS START -->'
END = '<!-- READER PARENT EXTENSIONS END -->'
BLOCK = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.S)
MODES = (('en', 'en'), ('zh', 'zh'), ('hant', 'zh-hant'))
# Explicitly hide the WHOLE section for unsupported modes. Existing global
# .lang-* rules alone do not hide English when data-lang is de/fr/es/ja/ko.
SCOPED_STYLE = '<style data-reader-extension-style>aside.reader-extensions{display:none!important}' + ''.join(
    f'[data-lang="{mode}"] aside.reader-extensions.lang-{css}' + '{display:block!important}'
    for css, mode in MODES) + '</style>'


def parent_spec(series):
    """Return [root-relative index, Chinese label, English label] or None."""
    value = series.get('parent')
    if value is None:
        return None
    assert isinstance(value, list) and len(value) == 3, series.get('slug')
    path, zh, en = value
    assert all(isinstance(v, str) and v.strip() for v in value)
    parsed = PurePosixPath(path)
    assert not parsed.is_absolute() and '..' not in parsed.parts
    assert path.startswith('essays/') and path.endswith('/index.html')
    assert '?' not in path and '#' not in path and '\\' not in path
    return path, zh, en


def is_standalone(series):
    return parent_spec(series) is None


def parent_discovery_paths(series, root):
    """Additional primary pages needed by scoped search/sitemap refresh."""
    parent = parent_spec(series)
    if not parent:
        return []
    path = root / parent[0]
    assert path.is_file(), f'Unpublished parent: {parent[0]}'
    return [path]


def tri(en, zh, converter, tag='span'):
    assert tag in ('span', 'h2', 'p')
    return ''.join(
        f'<{tag} class="lang-{language}">{html.escape(value)}</{tag}>'
        for language, value in (
            ('en', en), ('zh', zh), ('hant', converter.convert(zh)))
    )


def parent_backlink(series, converter):
    """Link from the depth-two supplement landing/article to its parent."""
    parent = parent_spec(series)
    if not parent:
        return ''
    path, zh, en = parent
    href = posixpath.relpath(path, f'essays/{series["slug"]}')
    # The shared site-shell already updates these edition attributes when the
    # local en/zh/zh-hant mode changes. Explicit query values win over storage.
    attrs = ''.join(f' data-edition-{mode}="{html.escape(href + "?lang=" + mode, quote=True)}"'
                    for _, mode in MODES)
    return f'<a href="{html.escape(href + "?lang=en", quote=True)}"{attrs}>' + tri(en, zh, converter) + '</a>'


def render_parent_extensions(text, parent_path, *, series=None,
                             item_loader=None, converter=None):
    """Add/update only a marked three-language parent-index link block.

    Rendering a parent with no registered child remains a no-op (apart from
    removing an obsolete block bearing our own explicit marker). Other prose,
    cards, scripts, head metadata and five-language editions are untouched.
    Injected dependency arguments make this routine independently testable.
    """
    owned_converter = False
    if series is None or item_loader is None or converter is None:
        import build_reader_series as reader
        if series is None:
            series = reader.registry()
        if item_loader is None:
            item_loader = reader.load_items
        if converter is None:
            converter = reader.ReaderTraditionalConverter()
            owned_converter = True
    try:
        assert text.count(START) == text.count(END) <= 1, 'Malformed extension markers'
        matches = [s for s in series if parent_spec(s) and parent_spec(s)[0] == parent_path]
        assert len({s['slug'] for s in matches}) == len(matches), 'Duplicate supplement'
        if not matches:
            return BLOCK.sub('', text, count=1)
        assert parent_path.startswith('essays/') and parent_path.endswith('/index.html')
        prefix = 'rel' if re.search(r'class="rel-wrap(?:\s|\")', text) else 'lw'
        groups = {mode: [] for _, mode in MODES}
        for child in matches:
            items = item_loader(child)
            assert len(items) == child['count']
            for css, mode in MODES:
                translate = (lambda en, zh: en) if mode == 'en' else \
                            (lambda en, zh: converter.convert(zh)) if mode == 'zh-hant' else \
                            (lambda en, zh: zh)
                links = []
                for item in items:
                    target = f'essays/{child["slug"]}/{item["slug"]}.html'
                    href = posixpath.relpath(target, posixpath.dirname(parent_path)) + '?lang=' + mode
                    label = translate(item['title_en'], item['title_zh'])
                    links.append(f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>')
                deck = translate(child['deck_en'], child['deck_zh'])
                groups[mode].append('<div data-reader-supplement="' + html.escape(child['slug'], quote=True) + '">' +
                                    '<p>' + html.escape(deck) + '</p>' + ''.join(links) + '</div>')
        sections = []
        for css, mode in MODES:
            title = 'Further essays' if mode == 'en' else '延伸專論' if mode == 'zh-hant' else '延伸专论'
            native = 'zh-Hant' if mode == 'zh-hant' else 'zh-Hans' if mode == 'zh' else 'en'
            sections.append(f'<aside class="{prefix}-related reader-extensions lang-{css}" lang="{native}" id="reader-extensions-{css}">' +
                            f'<h2>{title}</h2>' + ''.join(groups[mode]) + '</aside>')
        block = START + SCOPED_STYLE + ''.join(sections) + END
        if START in text:
            return BLOCK.sub(lambda _: block, text, count=1)
        anchor = re.search(r'<aside\b[^>]*\bclass="(?:lw|rel)-related(?:\s[^\"]*)?"', text)
        assert anchor, 'Parent related block not found; do not guess an insertion point'
        return text[:anchor.start()] + block + text[anchor.start():]
    finally:
        if owned_converter:
            converter.close()
