#!/usr/bin/env python3
"""Publish reviewed chapters 31–35; never generate or translate their prose.

The receipt freezes seven authored editions per chapter. Traditional Chinese is
an offline reading dictionary generated from the shared Chinese/English page.
The supplied introductions and glossaries are deliberately not imported.
"""
import argparse
import difflib
import html
import json
import re
import subprocess
from zipfile import ZipFile

import markdown
from build_daodejing_full_editions import ROOT, DATA, digest, replace_div
from build_emperor_traditional import TextCollector, TraditionalConverter
from test_daodejing_sources import Page

CHAPTERS = tuple(f'ch{i}' for i in range(31, 36))
LANGS = ('zh', 'en', 'ja', 'ko', 'de', 'fr', 'es')
FOREIGN = LANGS[2:]
RECEIPT = DATA / 'batch07-review.json'
SERIES = ROOT / 'essays/daodejing'


def page_path(chapter, lang):
    return SERIES / ('' if lang in ('zh', 'en') else lang) / f'{chapter}.html'


def baseline(path, commit):
    return subprocess.check_output(['git', 'show', f'{commit}:{path.relative_to(ROOT)}'], cwd=ROOT, text=True)


def record_review(archive):
    if RECEIPT.exists():
        raise ValueError('Review receipt already exists; do not silently reseal reviewed text')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    receipt = dict(batch='ch31-ch35', baseline_commit=commit,
                   source_archive=archive.name, source_archive_sha256=digest(archive.read_bytes()),
                   manuscripts={}, page_edits={}, editorial_notes=[
        'All original section counts and argument stages retained; repetitive overclaims replaced with concrete explanations and examples.',
        'Chinese and English revised alongside all five supplied languages; traditional Chinese generated offline.',
        'Philological interpretations distinguished from textual facts. No promises of automatic success, permanent loyalty, or human worth conditional on remembrance.',
        'Supplied introductions and glossaries not imported. Existing introduction body and its manuscript-division citation preserved.',
        'Adopted classical source panels, stable URLs, and source-paper website unchanged.'
    ])
    with ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError('Corrupt archive')
        for chapter in CHAPTERS:
            for lang in LANGS:
                key = f'{chapter}.{lang}'
                text = (DATA / f'{key}.md').read_text()
                body = markdown.markdown(text.split('\n', 1)[1].strip())
                old_page = baseline(page_path(chapter, lang), commit)
                headings = [n for n in Page(old_page).nodes if n.tag == 'h1']
                old_title = next(n.text() for n in headings if lang in FOREIGN or n.has_class(f'lang-{lang}'))
                record = dict(published_sha256=digest(text.encode()), title=text.splitlines()[0][2:],
                              previous_title=old_title, sections=body.count('<h2>'),
                              paragraphs=body.count('<p>'), blockquotes=body.count('<blockquote>'))
                if lang in FOREIGN:
                    received = z.read(f'daodejing-batch07/{key}.md').decode()
                    a, b = received.splitlines(keepends=True), text.splitlines(keepends=True)
                    edits = []
                    for tag, i, j, k, l in reversed(difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()):
                        if tag != 'equal':
                            edits.append(dict(offset=len(''.join(a[:i])), before=''.join(a[i:j]), after=''.join(b[k:l])))
                    record.update(received_sha256=digest(received.encode()), length_ratio=round(len(text)/len(received), 3), edits=edits)
                receipt['manuscripts'][key] = record
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')


def render(key, record):
    text = (DATA / f'{key}.md').read_text()
    if digest(text.encode()) != record['published_sha256']:
        raise ValueError(f'{key}: unreviewed manuscript changes')
    if text.splitlines()[0] != '# ' + record['title'] or len(re.findall(r'^# ', text, re.M)) != 1:
        raise ValueError(f'{key}: invalid title')
    body = markdown.markdown(text.split('\n', 1)[1].strip())
    for tag, field in [('h2', 'sections'), ('p', 'paragraphs'), ('blockquote', 'blockquotes')]:
        if body.count(f'<{tag}>') != record[field]:
            raise ValueError(f'{key}: unexpected {field}')
    return body


def updates():
    receipt = json.loads(RECEIPT.read_text())
    records = receipt['manuscripts']
    if set(records) != {f'{ch}.{lang}' for ch in CHAPTERS for lang in LANGS}:
        raise ValueError('Unexpected manuscript scope')
    outputs = {}
    # Limit related title propagation to the index and immediate neighbours.
    # Never replace the separately reviewed introduction with supplied drafts.
    for lang in ('zh', *FOREIGN):
        folder = SERIES / ('' if lang == 'zh' else lang)
        codes = ('zh', 'en') if lang == 'zh' else (lang,)
        for name in ('index', *(f'ch{i}' for i in range(30, 37))):
            path = folder / f'{name}.html'
            old = path.read_text()
            new = old
            if name in CHAPTERS:
                for code in codes:
                    key = f'{name}.{code}'
                    klass = f'essay-body lang-{code}' if code in ('zh', 'en') else 'essay-body'
                    new = replace_div(new, klass, render(key, records[key]))
                # Replace old summaries which could otherwise retain corrected claims.
                main_key = f'{name}.{codes[0]}'
                content = Page(render(main_key, records[main_key]))
                deck = next(n.text() for n in content.nodes if n.tag == 'p')
                if len(deck) > 190:
                    deck = deck[:187].rstrip() + '…'
                new = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m[1] + html.escape(deck, quote=True) + m[2], new, count=1)
            for ch in CHAPTERS:
                for code in codes:
                    r = records[f'{ch}.{code}']
                    if r['previous_title'] != r['title']:
                        for before, after in [(html.escape(r['previous_title'], quote=False), html.escape(r['title'], quote=False)),
                                              (html.escape(r['previous_title'], quote=True), html.escape(r['title'], quote=True))]:
                            new = new.replace(before, after)
            outputs[path] = new
    converter = TraditionalConverter()
    try:
        for path, source in list(outputs.items()):
            if path.parent != SERIES:
                continue
            collector = TextCollector(); collector.feed(source)
            title = html.unescape(re.search(r'<title>(.*?)</title>', source, re.S)[1])
            variants = {}
            for text in [*collector.text, title]:
                traditional = converter.convert(text)
                if traditional != text:
                    variants[text] = traditional
            dictionary = SERIES / 'zh-hant-data' / f'{path.stem}.js'
            # Preserve the source-panel exclusion, language defaults, and other
            # series-specific behaviour of the existing reading-mode script.
            outputs[dictionary] = re.sub(r'  var variants = \{.*\};',
                lambda _: '  var variants = ' + json.dumps(variants, ensure_ascii=False, sort_keys=True) + ';',
                dictionary.read_text(), count=1)
    finally:
        converter.close()
    return outputs


def main():
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--record-review', type=Path, metavar='ARCHIVE', help='one-time receipt for already edited manuscripts')
    args = parser.parse_args()
    if args.record_review:
        record_review(args.record_review)
    outputs = updates()
    pending = {p: text for p, text in outputs.items() if p.read_text() != text}
    if args.check:
        if pending:
            raise SystemExit('Stale batch07 outputs: ' + ', '.join(str(p.relative_to(ROOT)) for p in pending))
        print('OK: 35 manuscripts, 30 article pages, related titles and offline traditional dictionaries match')
        return
    receipt = json.loads(RECEIPT.read_text())
    for path, text in pending.items():
        rel = path.relative_to(ROOT).as_posix()
        receipt['page_edits'][rel] = dict(before_sha256=digest(baseline(path, receipt['baseline_commit']).encode()), after_sha256=digest(text.encode()))
        path.write_text(text)
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(f'Updated {len(pending)} batch07 outputs')


if __name__ == '__main__':
    main()
