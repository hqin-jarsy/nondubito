#!/usr/bin/env python3
"""Import reviewed translations and rebuild only the Monopoly routes.

Translations are editorial inputs, never automatically generated here.
Input: DIR/nd_monopoly_<lang>.json. References are a JSON mapping from
language to episode to localized labels in the source order. Validate without
writing with --import-dir DIR [--references FILE] [--front-matter FILE]
--check-inputs; omit --check-inputs only after editorial approval. Subsequently
run normally or with --check. Front matter is a mapping from locale to intro,
scope, and source_note. Inline and separate values must agree if both supplied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import build_reader_series as primary
import connect_full_series_languages as connection
import full_series_languages as languages
import refresh_reader_discovery as discovery
from prepare_action_sources import Document

ROOT = languages.ROOT
KEY = 'monopoly'
DIRECTORY = 'essays/' + KEY
BASE = ROOT / 'data' / KEY / 'multilingual'
LOCALES = ['ja', 'fr', 'de', 'es', 'ko']
PRIMARY_CODES = ['en', 'zh', 'zh-hant']
BADGE = 'EN · 简 · 繁 · 日本語 · Français · Deutsch · Español · 한국어'
PROTECTED_CLASSES = ('essay-body', 'lw-sources', 'lw-series-nav', 'lw-head',
                     'lw-grid', 'lw-opening', 'lw-related')
FRONT_FIELDS = ('intro', 'scope', 'source_note')
UI = {
    'ja': ('ホーム', '全九篇', '書架', 'メニュー', '検索', '全文を読む', '前の篇', '次の篇',
           '原論文と読解の手引き', 'SAE 理論', 'さらに読む', 'SAE 読書マップ', '原論文'),
    'fr': ('Accueil', 'Les neuf essais', 'Bibliothèque', 'Menu', 'Rechercher', 'Lire l’essai',
           'Essai précédent', 'Essai suivant', 'Sources et note de lecture', 'Théorie SAE',
           'À lire aussi', 'Parcours de lecture SAE', 'Article d’origine'),
    'de': ('Startseite', 'Alle neun Essays', 'Bibliothek', 'Menü', 'Suche', 'Essay lesen',
           'Vorheriger Essay', 'Nächster Essay', 'Quellen und Lesehinweis', 'SAE-Theorie',
           'Weiterlesen', 'SAE-Lesekarte', 'Zugehörige wissenschaftliche Arbeit'),
    'es': ('Inicio', 'Los nueve ensayos', 'Biblioteca', 'Menú', 'Buscar', 'Leer el ensayo',
           'Ensayo anterior', 'Ensayo siguiente', 'Fuentes y nota de lectura', 'Teoría SAE',
           'Seguir leyendo', 'Mapa de lectura SAE', 'Artículo original'),
    'ko': ('홈', '아홉 편 전체', '서가', '메뉴', '검색', '본문 읽기', '이전 글', '다음 글',
           '원논문과 읽기 안내', 'SAE 이론', '함께 읽기', 'SAE 읽기 지도', '원논문'),
}
UI_KEYS = ('home', 'contents', 'library', 'menu', 'search', 'read', 'previous', 'next',
           'sources', 'theory', 'related', 'map', 'paper')


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def read(path):
    return json.loads(path.read_text())


def output(path, text, check):
    if check:
        assert path.read_text() == text, f'Stale or missing: {path}'
    elif not path.is_file() or path.read_text() != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def valid(value):
    return isinstance(value, str) and bool(value.strip()) and not re.search(r'<|\ufffd|\b(?:TODO|FIXME)\b', value)


def master_spec():
    release = read(BASE.parent / 'publication.json')
    row, = (item for item in primary.registry() if item['slug'] == KEY)
    assert release['series'] == KEY and release['date'] == row['date']
    slugs = [f'ep{i:02d}' for i in range(1, row['count'] + 1)]
    assert row['count'] == 9, 'Update the localized nine-essay UI before changing the count'
    assert set(release['counts']) == set(slugs)
    related = [Path(item[0]).parent.name for item in row['related']]
    assert all(item[0] == f'essays/{target}/index.html' for target, item in zip(related, row['related']))
    return release, slugs, related


def import_data(directory, ref_path, front_path, check_inputs=False):
    ref_labels = read(ref_path) if ref_path else {}
    front_matter = read(front_path) if front_path else {}
    release, slugs, related = master_spec()
    original = {slug: read(BASE.parent / f'{slug}.json') for slug in slugs}
    assert [r['url'] for r in release['sources']] == [original[s]['source_url'] for s in slugs]
    spec = {
        'id': KEY, 'directory': DIRECTORY, 'date': release['date'],
        'source': original['ep01']['source_url'], 'source_format': 'modern-html',
        'slugs': slugs, 'languages': LOCALES, 'reading_css_version': '20261103',
        'primary_editions': {'en': '', 'zh': '', 'zh-hant': ''},
        'related_series': related,
        'preserve_reader_references': True,
    }
    pending = {BASE / 'profile.json': dump(spec)}
    for lang in LOCALES:
        data = read(directory / f'nd_monopoly_{lang}.json')
        front = {}
        for field in FRONT_FIELDS:
            inline = data.get(field)
            separate = front_matter.get(lang, {}).get(field)
            assert inline is None or separate is None or inline == separate, (lang, field, 'conflicting front matter')
            front[field] = inline if inline is not None else separate
            assert valid(front[field]), (lang, field, 'localized front matter required')
        assert valid(data['title']) and valid(data['deck']), lang
        assert [a['slug'] for a in data['articles']] == slugs, (lang, 'episode order')
        articles = []
        for article in data['articles']:
            slug = article['slug']
            item = original[slug]
            for key in ('title', 'deck'):
                assert valid(article[key]), (lang, slug, key)
            body = article['body']
            assert len(body) == len(item['body_zh']), (lang, slug, 'paragraph coverage')
            for i, (p, q) in enumerate(zip(item['body_zh'], body), 1):
                assert valid(q) and languages.block_kind(p) == languages.block_kind(q), (lang, slug, i)
            assert len(set(body)) == len(body), (lang, slug, 'repeated paragraphs')
            supplied = ref_labels.get(lang, {}).get(slug)
            inline = article.get('reference_labels')
            assert inline is None or supplied is None or inline == supplied, (lang, slug, 'conflicting reference labels')
            labels = inline if inline is not None else supplied
            labels = [] if labels is None and not item['references'] else labels
            assert isinstance(labels, list) and len(labels) == len(item['references']) and all(map(valid, labels)), (
                lang, slug, 'localized reference labels required in original link order')
            # Paragraph locators let an editor navigate the aligned source; they
            # are not proof of semantic review.
            articles.append({
                'slug': slug, 'title': article['title'], 'deck': article['deck'], 'body': body,
                'references': [{'url': r['url'], 'title': label} for r, label in zip(item['references'], labels)],
                'coverage': [f'{slug} · {i:02d}' for i in range(1, len(body)+1)],
                'source_sha256': hashlib.sha256((BASE.parent / f'{slug}.json').read_bytes()).hexdigest(),
            })
        packed = {
            'language': lang, 'ui': dict(zip(UI_KEYS, UI[lang]), series=data['title']),
            'series': {'title': data['title'], 'deck': data['deck'], **front},
            'articles': articles, 'review': {'unresolved': []},
        }
        pending[BASE / f'{lang}.json'] = dump(packed)
    if not check_inputs:
        for path, text in pending.items():
            output(path, text, False)
    print(('Validated' if check_inputs else 'Imported') +
          f' {len(LOCALES)*len(slugs)} essays with aligned source blocks and localized reference labels.')
    return pending


def protected(source, selector, tag=None):
    doc = Document(source)
    return [doc.raw(n) for n in doc.root.walk() if n.has(selector) and (tag is None or n.tag == tag)]


def primary_outputs(check):
    pages = primary.render(KEY)
    for path, text in pages.items():
        before = path.read_text()
        # Existing three text bodies, source blocks, and neighbor navigation must
        # remain byte-for-byte. Only series availability and language chrome change.
        for css in PROTECTED_CLASSES:
            assert protected(before, css) == protected(text, css), (path, css, 'published text changed')
        output(path, text, check)


def foreign_outputs(check):
    for lang in LOCALES:
        _, data = languages.load_language(KEY, lang)
        for row in data['articles']:
            src = BASE.parent / (row['slug'] + '.json')
            assert row['source_sha256'] == hashlib.sha256(src.read_bytes()).hexdigest(), (lang, src, 'source drift')
    pages = languages.render(KEY)
    _, slugs, _ = master_spec()
    assert len(pages) == len(LOCALES)*(1+len(slugs))
    for path, text in pages.items():
        output(path, text, check)


def discover_outputs(check):
    ledger_path = ROOT / 'data/site-updates.json'
    ledger = read(ledger_path)
    release, _, _ = master_spec()
    expected_id = f"{release['date']}-{KEY}-reader-series"
    entry, = (row for row in ledger['updates'] if row['id'] == expected_id)
    assert entry['url'] == DIRECTORY + '/index.html' and entry['date'] == release['date']
    entry['languages'] = [*PRIMARY_CODES, *LOCALES]
    output(ledger_path, dump(ledger), check)
    # Refresh the bounded Home area, channel cards and Library badge with the
    # standard connector, without inserting its separate Latest announcement.
    entry_for_catalog = dict(entry, library_count={
        'en': '9 essays · 8 languages', 'zh': '9 篇 · 八语', 'zh-hant': '9 篇 · 八語',
    })
    output(BASE / 'discovery.json', dump(entry_for_catalog), check)
    public_cards = connection.render(KEY)
    for path in [ROOT/'index.html', ROOT/'library.html', *(ROOT/f'essays/{lang}/index.html' for lang in LOCALES)]:
        output(path, public_cards[path], check)
    latest = ROOT/'latest.html'
    source = latest.read_text()
    marker = f'READER SERIES {KEY.upper()} LATEST'
    expr = re.compile(fr'<!-- {marker} START -->.*?<!-- {marker} END -->', re.S)
    def badge(match):
        block = match[0]
        updated = block.replace('<span>EN / 简 / 繁</span>', f'<span>{BADGE}</span>')
        assert updated.count(BADGE) == 1
        return updated
    result, n = expr.subn(badge, source)
    assert n == 1
    output(latest, result, check)
    for path, text in discovery.render(KEY).items():
        output(path, text, check)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--import-dir', type=Path)
    p.add_argument('--references', type=Path)
    p.add_argument('--front-matter', type=Path)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--check-inputs', action='store_true')
    args = p.parse_args()
    if args.check_inputs and not args.import_dir:
        p.error('--check-inputs requires --import-dir')
    if (args.references or args.front_matter) and not args.import_dir:
        p.error('--references and --front-matter require --import-dir')
    if args.import_dir and args.check:
        p.error('use --check-inputs to validate unpublished editorial inputs')
    if args.import_dir:
        import_data(args.import_dir, args.references, args.front_matter, check_inputs=args.check_inputs)
    if args.check_inputs:
        return
    primary_outputs(args.check)
    foreign_outputs(args.check)
    discover_outputs(args.check)
    print(('Checked' if args.check else 'Built') + ' 10 primary pages, 50 new-language pages, and scoped discovery.')


if __name__ == '__main__':
    main()
