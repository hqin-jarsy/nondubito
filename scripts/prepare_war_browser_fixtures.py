#!/usr/bin/env python3
"""Derive browser expectations from reviewed effective War content, never public HTML.

Final generation runs the renderer's complete release gate. --shape-only inspects
current loader output without approving it or writing a runnable final fixture.
No page, manuscript, dictionary, discovery record or ledger is modified.
"""
from __future__ import annotations
if not __debug__:
    raise RuntimeError('Optimized Python is unsupported: fixture guards require assertions')
import argparse
import hashlib
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import build_war_full_editions as full
import war_effective_texts as effective
from prepare_action_sources import Document, Node

ROOT = full.ROOT
LANGS = ('zh', 'zh-hant', 'en', 'ja', 'fr', 'de', 'es', 'ko')
SLUGS = tuple(full.SLUGS)
FOREIGN = tuple(l for l in LANGS if l not in ('zh', 'zh-hant', 'en'))
WIDTHS = (320, 375, 1440)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def norm(text):
    return re.sub(r'\s+', ' ', text).strip()

def dictionary(slug):
    path = ROOT / 'essays/war/zh-hant-data' / (slug + '.js')
    match = re.search(r'var variants\s*=\s*(\{.*?\});\s*\n', path.read_text(), re.S)
    assert match, ('Traditional dictionary missing', path)
    return json.loads(match[1])

def node_text(node, variants=None):
    # Match the dictionary controller: exact, whole DOM text-node lookup only.
    return ''.join(node_text(c, variants) if isinstance(c, Node)
                   else variants.get(c, c) if variants is not None else c
                   for c in node.children)

def text(fragment, variants=None):
    return norm(node_text(Document(fragment).root, variants))

def plain(value, variants=None):
    return norm(variants.get(value, value) if variants is not None else value)

def body_record(body, variants=None):
    units, tags, tables = [], [], []
    for i, fragment in enumerate(body):
        doc = Document(fragment)
        roots = [n for n in doc.root.children if isinstance(n, Node)]
        assert len(roots) == 1, ('Expected one element per unit', i)
        node = roots[0]
        units.append(norm(node_text(node, variants)))
        tags.append(node.tag)
        for table in [n for n in node.walk() if n.tag == 'table']:
            rows = []
            for row in [n for n in table.walk() if n.tag == 'tr']:
                cells = [n for n in row.children if isinstance(n, Node) and n.tag in ('td', 'th')]
                rows.append([{'text': norm(node_text(c, variants)), 'tag': c.tag,
                              'colspan': int(c.attrs.get('colspan') or 1),
                              'rowspan': int(c.attrs.get('rowspan') or 1)} for c in cells])
            assert rows and all(rows), ('Empty table', i)
            tables.append({'body_index': i, 'table_index': len(tables), 'rows': rows})
    return {'units': units, 'unit_tags': tags, 'tables': tables}

def article(lang, slug):
    source = full.read(full.BASE / 'sources' / (slug + '.json'))
    variants = dictionary(slug) if lang == 'zh-hant' else None
    if lang in ('zh', 'zh-hant'):
        body = effective.source_units(slug)
        metadata = {'title': source['title_zh'], 'deck': source['deck_zh']}
    elif lang == 'en':
        doc = Document(full.english_body(slug))
        body = [doc.raw(n) for n in doc.root.children if isinstance(n, Node)]
        metadata = effective.english_metadata(slug)
    else:
        item = full.load(lang, slug)
        body, metadata = item['body'], item
    assert len(body) == len(source['body_zh']), (lang, slug, 'incomplete effective body')
    return {'title': plain(metadata['title'], variants), 'deck': plain(metadata['deck'], variants),
            **body_record(body, variants)}

def index(lang):
    variants = dictionary('index') if lang == 'zh-hant' else None
    if lang in ('zh', 'zh-hant', 'en'):
        item = full.primary_index_data('zh' if lang == 'zh-hant' else lang)
        notes = item['source_notes']
        cards = item['cards']
    else:
        item = full.load_index(lang)
        notes = ['<p>' + html.escape(item['source_note']) + '</p>']
        cards = {slug: full.load(lang, slug) for slug in SLUGS}
    return {
        'title': plain(item['title'], variants),
        'intro': [text(u, variants) for u in item['intro']],
        'groups': [{key: text(g[key], variants) for key in ('eyebrow', 'title', 'note')}
                   for g in item['groups']],
        'source_notes': [text(u, variants) for u in notes],
        'cards': {slug: {'title': plain(cards[slug]['title'], variants),
                         'deck': plain(cards[slug]['deck'], variants)} for slug in SLUGS},
    }

def support_hashes():
    # Only files consumed by the effective loaders or release gates belong here.
    # Never glob the reviews/QA trees: later browser/visual evidence must not
    # create an unrelated stale-input failure or a receipt/fixture hash cycle.
    files = {full.BASE / name for name in (
        'index-source.json', 'index-baseline.html', 'english-baseline-bodies.json')}
    files.update(full.BASE / 'sources' / (s + '.json') for s in SLUGS)
    for lang in FOREIGN:
        files.update(full.BASE / 'translations' / lang / (s + '.json') for s in ('index', *SLUGS))
    approvals = []
    for lang in (*FOREIGN, 'en'):
        files.update(full.BASE / 'reviews' / (lang + '-' + s + '.json') for s in ('index', *SLUGS))
        approvals.append(full.BASE / 'reviews' / (lang + '.json'))
    files.update(full.BASE / 'reviews/en-second' / (s + '.json') for s in ('index', *SLUGS))
    files.add(effective.ZH_MANIFEST)
    files.update(effective.AUTHOR / (lang + '.json') for lang in (*FOREIGN, 'en', 'zh-hant'))
    approvals += [effective.AUTHOR / 'zh-hant-review.json', effective.AUTHOR / 'integration-review.json']
    files.add(effective.AUTHOR / 'traditional-patches.json')
    for receipt_path in approvals:
        if not receipt_path.exists():
            continue  # shape-only can run before the release receipts arrive.
        files.add(receipt_path)
        receipt = full.read(receipt_path)
        for field in ('input_sha256s', 'supporting_sha256s'):
            for relative in receipt.get(field, {}):
                support = (ROOT / relative).resolve()
                assert support.is_relative_to(ROOT), ('Approval input escapes repository', relative)
                assert support.is_file(), ('Approval support missing', relative)
                files.add(support)
    files.update((ROOT / 'essays/war/zh-hant-data').glob('*.js'))
    for module in list(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            p = Path(name).resolve()
            if p.is_relative_to(ROOT / 'scripts') and p.is_file():
                files.add(p)
    files.add(Path(__file__).resolve())
    return {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in sorted(files) if p.exists()}

def add_head_title_expectations(pages):
    # Reviewed short titles, not old public <title> strings. Traditional Chinese
    # fragments come from the final index dictionary's exact text-node mapping.
    # In particular, a stale per-page whole-title key must NOT make simplified
    # Chinese an acceptable expectation in Traditional reading mode.
    for lang in ('zh', 'zh-hant', 'en'):
        chinese = pages[('zh-hant' if lang == 'zh-hant' else 'zh') + '/index']
        english = pages['en/index']
        for slug in ('index', *SLUGS):
            zh_title = chinese['title'] if slug == 'index' else chinese['cards'][slug]['title']
            en_title = english['title'] if slug == 'index' else english['cards'][slug]['title']
            pages[lang + '/' + slug]['head_title_parts'] = [zh_title, en_title]


def validate_shape(result):
    assert result['languages'] == list(LANGS)
    assert result['slugs'] == list(SLUGS)
    assert result['widths'] == list(WIDTHS)
    assert len(result['pages']) == 136
    for lang in LANGS:
        assert sum(len(result['pages'][lang + '/' + s]['units']) for s in SLUGS) == 1121, lang
        assert sum(len(result['pages'][lang + '/' + s]['tables']) for s in SLUGS) == 12, lang
        if lang in ('zh', 'zh-hant', 'en'):
            for slug in ('index', *SLUGS):
                assert len(result['pages'][lang + '/' + slug]['head_title_parts']) == 2
                assert all(result['pages'][lang + '/' + slug]['head_title_parts'])
        ix = result['pages'][lang + '/index']
        assert len(ix['intro']) == 5 and len(ix['groups']) == 2 and len(ix['cards']) == 16, lang
        assert len(ix['source_notes']) == (1 if lang in FOREIGN else 2), lang
        for s in SLUGS:
            record = result['pages'][lang + '/' + s]
            assert len(record['units']) == len(record['unit_tags']) and all(record['units'])
            for table in record['tables']:
                assert table['rows'] and all(table['rows'])
                assert all(c['colspan'] >= 1 and c['rowspan'] >= 1 for row in table['rows'] for c in row)
    assert len(result['author_changed_units']) == 8
    return {'pages': 136, 'viewport_combinations': 408, 'units_per_language': 1121,
            'tables_per_language': 12, 'mobile_table_checks': 96}

def generate(final=True):
    if final:
        # Do not silently make a final fixture while second review or author
        # integration is incomplete. This reads gates only; it never renders.
        full.verify_reviews()
        for slug in ('index', *SLUGS):
            receipt_path = full.BASE / 'reviews/en-second' / (slug + '.json')
            assert receipt_path.exists(), ('English second review missing', slug)
            assert full.read(receipt_path).get('all_units_read') is True, ('English second read incomplete', slug)
    pages = {}
    for lang in LANGS:
        pages[lang + '/index'] = index(lang)
        for slug in SLUGS:
            pages[lang + '/' + slug] = article(lang, slug)
    add_head_title_expectations(pages)
    result = {
        'schema_version': 1, 'series': 'war',
        'status': 'final_effective_expectations' if final else 'shape_only_not_release_approved',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'languages': list(LANGS), 'slugs': list(SLUGS), 'widths': list(WIDTHS),
        'expected_html_languages': {l: {'zh': 'zh-Hans', 'zh-hant': 'zh-Hant'}.get(l, l) for l in LANGS},
        'pages': pages,
        'author_changed_units': [{'slug': c['slug'], 'body_index': c['body_index']}
                                 for c in full.read(effective.ZH_MANIFEST)['changes']],
        'derivation': {'body': 'source_units / english_body (both review passes plus author) / load',
                       'index': 'primary_index_data / load_index plus reviewed article card metadata',
                       'traditional': 'exact text-node mapping from final local per-page dictionaries',
                       'head_title_parts': 'reviewed primary index short titles; Traditional fragment uses final exact index text-node mapping, not a stale page-title fallback',
                       'public_html_used_as_expectation': False},
        'input_hashes': support_hashes(),
    }
    validate_shape(result)
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New JSON fixture path; existing files are protected')
    parser.add_argument('--shape-only', action='store_true', help='Inspect loader shapes without release approval or output')
    parser.add_argument('--validate', type=Path, help='Validate an existing fixture shape, without running a browser')
    args = parser.parse_args()
    assert not (args.shape_only and args.output), '--shape-only never writes a final fixture'
    if args.validate:
        assert not args.output and not args.shape_only
        result = json.loads(args.validate.read_text())
    else:
        assert args.shape_only or args.output, 'Specify --output or --shape-only'
        if args.output:
            assert not args.output.exists(), 'Protect previous expectations; choose a fresh fixture path'
        result = generate(final=not args.shape_only)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], **validate_shape(result),
                      'support_inputs': len(result['input_hashes']),
                      'output': str(args.output) if args.output else None}))

if __name__ == '__main__':
    main()
