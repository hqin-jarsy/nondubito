#!/usr/bin/env python3
"""Publish locally authored, reviewed ch71–81 manuscripts; never write prose.

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

CHAPTERS = tuple(f'ch{i}' for i in range(71, 82))
LANGS = ('zh', 'en', 'ja', 'ko', 'de', 'fr', 'es')
FOREIGN = LANGS[2:]
RECEIPT = DATA / 'batch14-review.json'
SERIES = ROOT / 'essays/daodejing'
SECTIONS = dict(zip(CHAPTERS, (7, 8, 7, 7, 8, 7, 8, 8, 7, 8, 9)))


def page_path(chapter, lang):
    return SERIES / ('' if lang in ('zh', 'en') else lang) / f'{chapter}.html'


def record_review():
    if RECEIPT.exists():
        raise ValueError('Review receipt exists; do not silently reseal manuscripts')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    receipt = dict(batch='ch71-ch81', baseline_commit=commit,
        brief_sha256=digest((DATA / 'batch14-brief.json').read_bytes()),
        source_mode='locally-authored-independent-editions', manuscripts={}, page_edits={},
        editorial_notes=[
          "Fifty-five complete foreign essays independently authored from all eleven Chinese originals and corrected Chinese, with substantive arguments and examples retained; no translation service.",
          "Seventy-seven manuscripts in seven authored languages, with offline Traditional Chinese; section counts 7/8/7/7/8/7/8/8/7/8/9.",
          "Author self-review and independent full cross-review completed before freezing; manual corrections are not replaced by word-count checks.",
          "Classical source panels, source-paper site, stable URLs, intro and previous receipts remain unchanged. Eight original DOI destinations for 71–72, nine for 73–81.",
          "Titles, indexes, metadata, navigation through the final chapter, dictionaries, search and sitemap synchronized.",
          *[f"Ch{number}: {record['corrections']}" for number, record in
            json.loads((DATA / 'batch14-brief.json').read_text())['chapters'].items()]
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


def description(key, record):
    content = Page(render(key, record))
    deck = next(n.text() for n in content.nodes if n.tag == 'p')
    if len(deck) <= 190:
        return deck
    excerpt = deck[:187].rstrip()
    if key.split('.')[-1] not in ('zh', 'ja') and ' ' in excerpt:
        excerpt = excerpt.rsplit(' ', 1)[0]
    return excerpt + '…'


def update_index(source, records, codes):
    """Use chapter links, since legacy card titles may differ from page H1s."""
    page = Page(source)
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    edits = []
    def replace_content(node, value):
        start = offsets[node.start[0] - 1] + node.start[1]
        end = offsets[node.end[0] - 1] + node.end[1]
        edits.append((source.index('>', start) + 1, end, html.escape(value, quote=False)))
    for chapter in CHAPTERS:
        cards = [n for n in page.nodes if n.tag == 'a' and n.attrs.get('href') == chapter + '.html']
        if len(cards) != 1:
            raise ValueError(f'{chapter}: expected one index card')
        card = cards[0]
        for code in codes:
            if code in FOREIGN:
                titles = [n for n in card.descendants() if n.tag == 'h2' or n.has_class('card-title-en')]
            else:
                titles = [n for n in card.descendants() if n.has_class(f'entry-title-{code}')]
            if len(titles) != 1:
                raise ValueError(f'{chapter}.{code}: expected one card title')
            replace_content(titles[0], records[f'{chapter}.{code}']['title'])
        for node in card.descendants('p'):
            key = f'{chapter}.{codes[0]}'
            replace_content(node, description(key, records[key]))
    for start, end, value in sorted(edits, reverse=True):
        source = source[:start] + value + source[end:]
    return source


def updates():
    records = json.loads(RECEIPT.read_text())['manuscripts']
    if set(records) != {f'{ch}.{lang}' for ch in CHAPTERS for lang in LANGS}:
        raise ValueError('Unexpected manuscript scope')
    outputs = {}
    for lang in ('zh', *FOREIGN):
        folder = SERIES / ('' if lang == 'zh' else lang)
        codes = ('zh', 'en') if lang == 'zh' else (lang,)
        for name in ('index', *(f'ch{i}' for i in range(70, 82))):
            path = folder / f'{name}.html'
            new = path.read_text()
            if name in CHAPTERS:
                for code in codes:
                    klass = f'essay-body lang-{code}' if code in ('zh', 'en') else 'essay-body'
                    new = replace_div(new, klass, render(f'{name}.{code}', records[f'{name}.{code}']))
                deck = description(f'{name}.{codes[0]}', records[f'{name}.{codes[0]}'])
                new = re.sub(r'(<meta name="description" content=")[^"]*(")',
                             lambda m: m[1] + html.escape(deck, quote=True) + m[2], new, count=1)
            new = update_titles(new, records, codes)
            if name == 'index':
                new = update_index(new, records, codes)
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
            raise SystemExit('Stale batch14 outputs: ' + ', '.join(str(p.relative_to(ROOT)) for p in pending))
        print('OK: 77 reviewed manuscripts, 66 article pages, related titles and offline traditional dictionaries match')
        return
    receipt = json.loads(RECEIPT.read_text())
    for path, text in pending.items():
        rel = path.relative_to(ROOT).as_posix()
        receipt['page_edits'][rel] = dict(before_sha256=digest(baseline(path, receipt['baseline_commit']).encode()),
                                       after_sha256=digest(text.encode()))
        path.write_text(text)
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print(f'Updated {len(pending)} batch14 outputs')


if __name__ == '__main__':
    main()
