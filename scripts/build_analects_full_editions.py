#!/usr/bin/env python3
"""Build complete Analects editions from portable, provenance-preserved inputs.

Received v0.2 manuscripts stay immutable. The English files and reviewed explicit
corrections are editable inputs; snapshots preserve the Chinese and site shell.
Both earlier builders delegate here so an ordinary rebuild cannot restore abridgments.
"""
from __future__ import annotations
import argparse
import html
import json
import re
from pathlib import Path
from build_epic_full_editions import digest, div_span, region, within
from import_analects_series import ITEMS, inline

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/analects-full'
SERIES = ROOT / 'essays/analects'
FOREIGN = ('en', 'de', 'fr', 'es', 'ja', 'ko')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def manifest():
    return read_json(DATA / 'manifest.json')


def snapshot(relative):
    return DATA / 'snapshots' / (str(relative) + '.txt')


def corrections():
    path = DATA / 'review/five-language-corrections.json'
    return read_json(path) if path.exists() else []


def chinese_corrections():
    path = DATA / 'source-corrections.json'
    return read_json(path) if path.exists() else []


def replace_once(text, before, after, context):
    assert text.count(before) == 1, ('Correction is not uniquely anchored', context, before)
    return text.replace(before, after, 1)


def manuscript(item, language):
    path = DATA / 'english' / (item['number'] + '.md') if language == 'en' else DATA / 'received' / item['slug'] / (language + '.md')
    text = path.read_text(encoding='utf-8')
    for change in corrections():
        if int(change['episode']) == int(item['number']) and change['language'] == language:
            text = replace_once(text, change['before'], change['after'], (item['slug'], language))
    chunks = [x.strip() for x in re.split(r'\n\s*\n', text.strip()) if x.strip()]
    assert chunks[0].startswith('# '), path
    author = next(i for i, x in enumerate(chunks) if x.startswith('Han Qin'))
    assert author in (1, 2, 3), (path, 'Unexpected front matter', author)
    title = chunks[0][2:]
    deck = ' '.join(chunks[1:author])
    if not deck:
        deck = next(e['deck'] for e in read_json(ROOT / f'data/analects-languages/{language}.json')['entries'] if e['number'] == item['number'])
    body = chunks[author + 1:]
    assert len(body) >= 8, (path, 'Suspected abridgment', len(body))
    assert 'doi.org/' in body[-1] and 'CC BY' in body[-1], (path, 'Source note missing')
    return {'title': title, 'deck': deck, 'blocks': body, 'path': str(path.relative_to(ROOT))}


def body_html(copy):
    rendered = []
    for i, chunk in enumerate(copy['blocks']):
        source = i == len(copy['blocks']) - 1
        if source:
            rendered.append('<p class="source-note">' + inline(' '.join(chunk.splitlines())) + '</p>')
        elif chunk == '---':
            rendered.append('<hr>')
        elif chunk.startswith('>'):
            lines = [inline(x.lstrip('> ')) for x in chunk.splitlines()]
            rendered.append('<blockquote>' + '<br>'.join(lines) + '</blockquote>')
        elif chunk.startswith('## '):
            rendered.append('<h2>' + inline(chunk[3:]) + '</h2>')
        else:
            assert not chunk.startswith('#'), ('Unexpected heading', copy['path'], chunk)
            rendered.append('<p>' + inline(' '.join(chunk.splitlines())) + '</p>')
    return '\n'.join(rendered)


def editions(languages=FOREIGN):
    return {item['slug']: {lang: manuscript(item, lang) for lang in languages} for item in manifest()['essays']}


def approved_chinese(relative, code):
    text = region(snapshot(relative).read_text(), 'lang-' + code)
    for change in chinese_corrections():
        if relative.startswith(f"{int(change['episode']):02}-"):
            edit = change[code]
            text = replace_once(text, edit['before'], edit['after'], (relative, code))
    return text


def labels(text, replacements):
    # JSON is handled separately so quotes in new titles cannot corrupt JSON-LD.
    placeholders = []
    def stash(m):
        marker = f'<!-- ANALECTS SCHEMA {len(placeholders)} -->'
        placeholders.append(json.loads(m[1]))
        return marker
    text = re.sub(r'<script type="application/ld\+json">(.*?)</script>', stash, text, flags=re.S)
    def swap(value):
        if isinstance(value, dict): return {k:swap(v) for k,v in value.items()}
        if isinstance(value, list): return [swap(v) for v in value]
        if isinstance(value, str):
            for old, new in replacements:
                if old: value = value.replace(old, new)
        return value
    # A simultaneous substitution avoids one translated title being replaced again.
    mapping = {html.escape(old, quote=True): html.escape(new, quote=True) for old,new in replacements if old and old != new}
    if mapping:
        pattern = re.compile('|'.join(re.escape(k) for k in sorted(mapping, key=len, reverse=True)))
        text = pattern.sub(lambda m:mapping[m[0]], text)
    for i, schema in enumerate(placeholders):
        text = text.replace(f'<!-- ANALECTS SCHEMA {i} -->', '<script type="application/ld+json">' + json.dumps(swap(schema), ensure_ascii=False, indent=2) + '</script>')
    return text


def render(languages=FOREIGN):
    receipt = manifest()
    for group in ('received_files', 'snapshots', 'chinese_sources'):
        for name, expected in receipt[group].items():
            assert digest((DATA / name).read_bytes()) == expected, ('Immutable input changed', name)
    copies = editions(languages)
    old = {'en': {number:{'title':title, 'deck':deck} for number,slug,title,deck in ITEMS}}
    for lang in FOREIGN[1:]:
        old[lang] = {entry['number']:entry for entry in read_json(ROOT / f'data/analects-languages/{lang}.json')['entries']}
    replacements = {lang: [(old[lang][item['number']][field], copies[item['slug']][lang][field]) for item in receipt['essays'] for field in ('title','deck')] for lang in languages}
    outputs = {}
    for item in receipt['essays']:
        for lang in languages:
            rel = item['file'] if lang == 'en' else f"{lang}/{item['file']}"
            text = snapshot(rel).read_text()
            # Replace the body before labels: body wording must never be globally rewritten.
            body = body_html(copies[item['slug']][lang])
            text = labels(text, replacements[lang])
            if lang == 'en':
                text = within(text, 'lang-en', lambda t:within(t, 'article-body', lambda _:body))
                for code in ('zh','hant'):
                    start,_,_,end = div_span(text, 'lang-' + code)
                    text = text[:start] + approved_chinese(rel, code) + text[end:]
            else:
                text = within(text, 'article-body', lambda _:body)
            if lang == 'en':
                text = text.replace('</head>', '<script src="full-edition.js?v=20261108" defer></script></head>', 1)
            outputs[SERIES / rel] = text
    for lang in languages:
        rel = 'index.html' if lang == 'en' else f'{lang}/index.html'
        text = labels(snapshot(rel).read_text(), replacements[lang])
        if lang == 'en':
            for code in ('zh','hant'):
                assert region(text,'lang-'+code) == region(snapshot(rel).read_text(),'lang-'+code)
        if lang == 'en':
            text = text.replace('</head>', '<script src="full-edition.js?v=20261108" defer></script></head>', 1)
        outputs[SERIES / rel] = text
    previous_path = DATA / 'last-build.json'
    previous = read_json(previous_path) if previous_path.exists() else {}
    for path, text in outputs.items():
        rel = str(path.relative_to(SERIES))
        if path.exists():
            accepted = {digest(snapshot(rel).read_bytes()), digest(text), previous.get(rel)}
            assert digest(path.read_bytes()) in accepted, ('Page changed outside canonical input; preserve edits before rebuilding', rel)
    return outputs


def render_primary():
    return render(('en',))


def render_foreign():
    return render(FOREIGN[1:])


def write_outputs(outputs):
    """Advance receipts for partial and full builds alike, without losing other pages."""
    receipt_path = DATA / 'last-build.json'
    receipt = read_json(receipt_path) if receipt_path.exists() else {}
    for path, text in outputs.items():
        path.write_text(text, encoding='utf-8')
        receipt[str(path.relative_to(SERIES))] = digest(text)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs = render()
    stale = [str(p.relative_to(ROOT)) for p,t in outputs.items() if not p.exists() or p.read_text() != t]
    if args.check:
        if stale: raise SystemExit('Stale complete Analects pages:\n' + '\n'.join(stale))
        print(f'OK: {len(outputs)} complete Analects pages')
        return
    write_outputs(outputs)
    print(f'Wrote {len(outputs)} complete Analects pages')

if __name__ == '__main__': main()
