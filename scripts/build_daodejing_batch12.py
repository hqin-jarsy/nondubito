#!/usr/bin/env python3
"""Publish locally authored, reviewed ch56–60 manuscripts; never write prose.

There is no incoming translation archive for this batch. The receipt freezes
the seven authored editions and the existing HTML baseline; Hant is offline.
"""
import argparse
import html
import json
import re
import subprocess

import markdown
from build_daodejing_full_editions import ROOT, DATA, digest, replace_div
from build_daodejing_batch08 import baseline
from build_emperor_traditional import TextCollector, TraditionalConverter
from test_daodejing_sources import Page

CHAPTERS = tuple(f'ch{i}' for i in range(56, 61))
LANGS = ('zh', 'en', 'ja', 'ko', 'de', 'fr', 'es')
FOREIGN = LANGS[2:]
RECEIPT = DATA / 'batch12-review.json'
SERIES = ROOT / 'essays/daodejing'
SECTIONS = dict(zip(CHAPTERS, (5, 6, 7, 7, 5)))


def page_path(chapter, lang):
    return SERIES / ('' if lang in ('zh', 'en') else lang) / f'{chapter}.html'


def record_review():
    if RECEIPT.exists():
        raise ValueError('Review receipt exists; do not silently reseal manuscripts')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    receipt = dict(batch='ch56-ch60', baseline_commit=commit,
        brief_sha256=digest((DATA / 'batch12-brief.json').read_bytes()),
        source_mode='locally-authored-independent-editions', manuscripts={}, page_edits={},
        editorial_notes=[
          "Five foreign languages independently authored from complete original Chinese and corrected local Chinese; all arguments/examples retained in native prose, no translation service.",
          "Five/six/seven/seven/five sections retained. ZH/EN calibrated together; offline Hant synchronized.",
          "Ch56: six clauses are three pairs; noncapture by intimacy/profit/status is not invulnerability or needing nobody. 可 is not given an unsupported exclusive lexical gloss as extremity.",
          "Ch57: burdensome control can create evasion, not a universal causal theorem against all rules. Protective rules, support and necessary intervention remain; 吾/我 do not prove two psychological structures.",
          "Ch58: adopted 悉/兼/绁 readings distinguished from received 迷/廉/肆. No guarantee that catastrophe yields blessing, all good inevitably reverses, or understanding grants longevity.",
          "Ch59: early restraint is an interpretation, not a definitive 服=伏 etymology. Shared reserves are finite; no blame for constrained overwork, denial of needs or reduction of rest to productivity.",
          "Ch60: cooking metaphor retains necessary care. Adopted rhetorical questions and author's nonenmity reading coexist with received 圣人亦不伤人 and ruler accountability. No supernatural proof, immunity or victim blaming.",
          "Classical panels, source-paper site, stable URLs and previous manuscript receipts unchanged. All seven DOI destinations preserved for every new manuscript.",
          "Author self-review and independent cross-review integrated before freezing; titles, indexes, metadata, navigation and dictionaries synchronized."
        ])
    for chapter in CHAPTERS:
        for lang in LANGS:
            key = f'{chapter}.{lang}'
            text = (DATA / f'{key}.md').read_text()
            body = markdown.markdown(text.split('\n', 1)[1].strip())
            old_page = baseline(page_path(chapter, lang), commit)
            old_title = next(n.text() for n in Page(old_page).nodes if n.tag == 'h1'
                             and (lang in FOREIGN or n.has_class(f'lang-{lang}')))
            if body.count('<h2>') != SECTIONS[chapter]:
                raise ValueError(f'{key}: incomplete chapter structure')
            receipt['manuscripts'][key] = dict(
                published_sha256=digest(text.encode()), title=text.splitlines()[0][2:],
                previous_title=old_title, baseline_page_sha256=digest(old_page.encode()),
                sections=body.count('<h2>'), paragraphs=body.count('<p>'),
                blockquotes=body.count('<blockquote>'))
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


def update_titles(source, records, codes):
    """Change labels/metadata without rewriting quoted titles inside essays."""
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    spans = []
    for node in Page(source).nodes:
        if node.has_class('essay-body'):
            start = offsets[node.start[0] - 1] + node.start[1]
            end = offsets[node.end[0] - 1] + node.end[1]
            spans.append((start, source.index('>', end) + 1))
    def labels(value):
        quotes = str.maketrans({'“': '"', '”': '"', '‘': "'", '’': "'"})
        for chapter in CHAPTERS:
            for code in codes:
                record = records[f'{chapter}.{code}']
                for previous in {record['previous_title'], record['previous_title'].translate(quotes)}:
                    for quote in (False, True):
                        value = value.replace(html.escape(previous, quote=quote),
                                              html.escape(record['title'], quote=quote))
        return value
    parts, cursor = [], 0
    for start, end in sorted(spans):
        parts.extend((labels(source[cursor:start]), source[start:end]))
        cursor = end
    parts.append(labels(source[cursor:]))
    return ''.join(parts)


def updates():
    records = json.loads(RECEIPT.read_text())['manuscripts']
    if set(records) != {f'{ch}.{lang}' for ch in CHAPTERS for lang in LANGS}:
        raise ValueError('Unexpected manuscript scope')
    outputs = {}
    for lang in ('zh', *FOREIGN):
        folder = SERIES / ('' if lang == 'zh' else lang)
        codes = ('zh', 'en') if lang == 'zh' else (lang,)
        for name in ('index', *(f'ch{i}' for i in range(55, 62))):
            path = folder / f'{name}.html'
            new = path.read_text()
            if name in CHAPTERS:
                for code in codes:
                    klass = f'essay-body lang-{code}' if code in ('zh', 'en') else 'essay-body'
                    new = replace_div(new, klass, render(f'{name}.{code}', records[f'{name}.{code}']))
                content = Page(render(f'{name}.{codes[0]}', records[f'{name}.{codes[0]}']))
                deck = next(n.text() for n in content.nodes if n.tag == 'p')
                if len(deck) > 190:
                    deck = deck[:187].rstrip() + '…'
                new = re.sub(r'(<meta name="description" content=")[^"]*(")',
                             lambda m: m[1] + html.escape(deck, quote=True) + m[2], new, count=1)
            new = update_titles(new, records, codes)
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
            outputs[dictionary] = re.sub(r'  var variants = \{.*\};',
                lambda _: '  var variants = ' + json.dumps(variants, ensure_ascii=False, sort_keys=True) + ';',
                dictionary.read_text(), count=1)
    finally:
        converter.close()
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--record-review', action='store_true', help='freeze already-reviewed local manuscripts once')
    args = parser.parse_args()
    if args.record_review:
        record_review()
    outputs = updates()
    pending = {p: text for p, text in outputs.items() if p.read_text() != text}
    if args.check:
        if pending:
            raise SystemExit('Stale batch12 outputs: ' + ', '.join(str(p.relative_to(ROOT)) for p in pending))
        print('OK: 35 reviewed manuscripts, 30 article pages, related titles and offline traditional dictionaries match')
        return
    receipt = json.loads(RECEIPT.read_text())
    for path, text in pending.items():
        rel = path.relative_to(ROOT).as_posix()
        receipt['page_edits'][rel] = dict(before_sha256=digest(baseline(path, receipt['baseline_commit']).encode()),
                                       after_sha256=digest(text.encode()))
        path.write_text(text)
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(f'Updated {len(pending)} batch12 outputs')


if __name__ == '__main__':
    main()
