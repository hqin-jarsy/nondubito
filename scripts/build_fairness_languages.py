#!/usr/bin/env python3
"""Import approved Fairness Markdown and generate its five new site editions.

Expected per language: ep01.md…ep12.md and meta.json. Use --check-inputs
to validate the complete aligned manuscripts before rendering. This script
does not translate, approve, commit, or deploy.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
from pathlib import Path

import build_reader_series as primary
import connect_full_series_languages as connection
import full_series_languages as languages
import refresh_reader_discovery as discovery
from prepare_action_sources import Document, Node, normalize

ROOT = languages.ROOT
KEY = 'fairness'
DIRECTORY = 'essays/' + KEY
BASE = ROOT / 'data' / KEY / 'multilingual'
LOCALES = ['ja', 'fr', 'de', 'es', 'ko']
PRIMARY_CODES = ['en', 'zh', 'zh-hant']
PROTECTED_CLASSES = ('essay-body', 'lw-sources', 'lw-series-nav', 'lw-head',
                     'lw-grid', 'lw-opening', 'lw-related')

UI = {
    'ja': ('ホーム', '全十二篇', '書架', 'メニュー', '検索', '全文を読む', '前の篇', '次の篇',
           '原論文と読解の手引き', 'SAE 理論', 'さらに読む', 'SAE 読書マップ', '原論文'),
    'fr': ('Accueil', 'Les douze essais', 'Bibliothèque', 'Menu', 'Rechercher', 'Lire l’essai',
           'Essai précédent', 'Essai suivant', 'Sources et note de lecture', 'Théorie SAE',
           'À lire aussi', 'Parcours de lecture SAE', 'Article d’origine'),
    'de': ('Startseite', 'Alle zwölf Essays', 'Bibliothek', 'Menü', 'Suche', 'Essay lesen',
           'Vorheriger Essay', 'Nächster Essay', 'Quellen und Lesehinweis', 'SAE-Theorie',
           'Weiterlesen', 'SAE-Lesekarte', 'Zugehörige wissenschaftliche Arbeit'),
    'es': ('Inicio', 'Los doce ensayos', 'Biblioteca', 'Menú', 'Buscar', 'Leer el ensayo',
           'Ensayo anterior', 'Ensayo siguiente', 'Fuentes y nota de lectura', 'Teoría SAE',
           'Seguir leyendo', 'Mapa de lectura SAE', 'Artículo original'),
    'ko': ('홈', '열두 편 전체', '서가', '메뉴', '검색', '본문 읽기', '이전 글', '다음 글',
           '원논문과 읽기 안내', 'SAE 이론', '함께 읽기', 'SAE 읽기 지도', '원논문'),
}
RELATED_RIGHTS = {'ja':'権利論', 'fr':'Théorie des droits', 'de':'Theorie der Rechte',
                  'es':'Teoría de los derechos', 'ko':'권리론'}
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


# The primary route already declares this reading distinction.
SCOPE = {'ja': '通常の読書は第11篇で一区切りです。先人の考えに照らし合わせる最後の一篇は、興味のある方に向けたものです。',
 'fr': 'Le parcours principal s’achève avec le onzième essai. Le dernier, en '
       'dialogue avec les traditions de pensée, reste facultatif.',
 'de': 'Der reguläre Leseweg schließt mit dem elften Essay ab. Der letzte '
       'Essay stellt die eigenen Maßstäbe neben ältere Denkweisen und ist '
       'optional.',
 'es': 'El itinerario principal concluye en el undécimo ensayo. El último, que '
       'pone este enfoque en diálogo con otras tradiciones, es opcional.',
 'ko': '기본 읽기는 열한 번째 글에서 마무리됩니다. 여러 사상 전통과 견주어 읽는 마지막 글은 선택 사항입니다.'}

def master_spec():
    release = read(BASE.parent / 'publication.json')
    row, = (item for item in primary.registry() if item['slug'] == KEY)
    assert release['series'] == KEY and release['date'] == row['date']
    slugs = [f'ep{i:02d}' for i in range(1, row['count'] + 1)]
    assert row['count'] == 12, 'Update the localized twelve-essay UI before changing the count'
    assert set(release['counts']) == set(slugs)
    related = [Path(item[0]).parent.name for item in row['related']]
    assert all(item[0] == f'essays/{target}/index.html' for target, item in zip(related, row['related']))
    return release, slugs, related


def source_body_hashes(slugs):
    result = {}
    for slug in slugs:
        doc = Document((ROOT / DIRECTORY / (slug + '.html')).read_text())
        digests = {}
        for css, locale in (('en','en'), ('zh','zh-Hans'), ('hant','zh-Hant')):
            node, = [n for n in doc.root.walk() if n.has('essay-body', 'lang-'+css)]
            blocks = [n for n in node.children if isinstance(n, Node)]
            assert blocks and all(n.tag in ('p','h2') for n in blocks), (slug, locale)
            payload = '\n'.join(n.tag+'\t'+normalize(n.text()) for n in blocks).encode('utf-8')
            digests[locale] = hashlib.sha256(payload).hexdigest()
        result[slug] = digests
    return result


def verify_source_receipt(receipt, slugs):
    expected = read(receipt)
    actual = source_body_hashes(slugs)
    assert set(expected) == set(actual), 'Source receipt does not cover every Fairness essay'
    for slug, digests in actual.items():
        assert expected[slug] == digests, (slug, 'live source snapshot differs from the Mac checkout')
    return expected


def metadata_value(meta, key):
    value = meta[key]
    assert valid(value), (key, 'missing or invalid localized metadata')
    return value


def manuscript(path):
    lines = re.split(r'\n\s*\n', path.read_text().strip())
    title, *body = [' '.join(x.strip().splitlines()) for x in lines]
    assert title.startswith('# ') and valid(title[2:]), path
    return title[2:], body


def import_data(directory, date, check_inputs=False):
    release, slugs, related = master_spec()
    row, = (item for item in primary.registry() if item['slug'] == KEY)
    assert str(datetime.date.fromisoformat(date)) == date and date >= release['date']
    original = {slug: read(BASE.parent / f'{slug}.json') for slug in slugs}
    assert [r['url'] for r in release['sources']] == [original[s]['source_url'] for s in slugs]
    groups = [{'id': g['id'], 'slugs': [f'ep{i:02d}' for i in g['episodes']]} for g in row['reading_groups']]
    # All translated collections keep the ordinary path (1–11) and optional
    # comparison with earlier thinkers (12), including the three source groups.
    spec = {
        'id': KEY, 'directory': DIRECTORY, 'date': date,
        'source': original['ep01']['source_url'], 'source_format': 'modern-html',
        'slugs': slugs, 'languages': LOCALES, 'reading_css_version': '20261103',
        'primary_editions': {'en': '', 'zh': '', 'zh-hant': ''},
        'related_series': [s for s in related if s != 'rights'],
        # Rights is a reviewed older series with its own renderer.
        'reader_routes': [{'path':'essays/rights/{language}/index.html','label_key':'rights'}],
        'preserve_reader_references': True, 'preserve_block_types': True,
        'index_groups': groups, 'index_group_decks': True,
    }
    pending = {BASE / 'profile.json': dump(spec)}
    receipt_path = directory/'source-body-hashes.json'
    if receipt_path.is_file():
        pending[BASE/receipt_path.name] = dump(verify_source_receipt(receipt_path, slugs))
    for lang in LOCALES:
        loc = directory/lang
        m = read(loc/'meta.json')
        assert set(m['decks']) == set(slugs), (lang, 'incorrect essay deck coverage')
        assert set(m['groups']) == {g['id'] for g in groups}, (lang, 'incorrect reading groups')
        reference_slugs = {slug for slug, i in original.items() if i['references']}
        assert reference_slugs <= set(m['references']) <= set(slugs), (lang, 'incorrect reference coverage')
        front = {'title': metadata_value(m, 'title'), 'deck': metadata_value(m, 'summary'),
                 'intro': metadata_value(m, 'opening'), 'scope': metadata_value({'scope': SCOPE[lang], **m}, 'scope'),
                 'source_note': metadata_value(m, 'note')}
        front['index_groups'] = [
            {'id': g['id'], 'title': metadata_value(m['groups'][g['id']], 'title'),
             'deck': metadata_value(m['groups'][g['id']], 'summary')} for g in groups
        ]
        articles = []
        for slug in slugs:
            item = original[slug]
            title, body = manuscript(loc/(slug + '.md'))
            deck = metadata_value(m['decks'], slug)
            assert len(body) == len(item['body_zh']), (lang, slug, len(body), len(item['body_zh']), 'paragraph coverage')
            for i, (p, q) in enumerate(zip(item['body_zh'], body), 1):
                assert valid(q) and languages.block_kind(p) == languages.block_kind(q), (lang, slug, i)
                # Official sources are in the metadata, not inline. Keep any
                # genuine inline source links but forbid newly introduced ones.
                urls = lambda s: re.findall(r'\]\((https://[^\s)]+)\)', s)
                assert urls(p) == urls(q), (lang, slug, i, 'changed inline links')
            assert len(set(body)) == len(body), (lang, slug, 'repeated paragraphs')
            labels = m['references'].get(slug, [])
            assert isinstance(labels, list) and len(labels) == len(item['references']) and all(map(valid, labels)), (
                lang, slug, 'localized reference labels required in original link order')
            articles.append({
                'slug': slug, 'title': title, 'deck': deck, 'body': body,
                'references': [{'url': r['url'], 'title': label} for r, label in zip(item['references'], labels)],
                'coverage': [f'{slug} · {i:02d}' for i in range(1, len(body)+1)],
                'source_sha256': hashlib.sha256((BASE.parent / f'{slug}.json').read_bytes()).hexdigest(),
            })
        packed = {
            'language': lang, 'ui': dict(zip(UI_KEYS, UI[lang]), series=front['title'], rights=RELATED_RIGHTS[lang]),
            'series': front, 'articles': articles, 'review': {'unresolved': []},
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
    receipt = BASE/'source-body-hashes.json'
    if receipt.is_file():
        verify_source_receipt(receipt, master_spec()[1])
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
    spec = languages.profile(KEY)
    source_id = f"{master_spec()[0]['date']}-{KEY}-reader-series"
    previous, = [u for u in read(ROOT/'data/site-updates.json')['updates'] if u['id'] == source_id]
    assert previous['languages'] == PRIMARY_CODES, 'Do not rewrite the original publication record'
    entry = dict(id=spec['date']+'-fairness-eight-languages', date=spec['date'], kind='expanded',
                 domain='sae', series_key=DIRECTORY, url=DIRECTORY+'/index.html',
                 languages=[*PRIMARY_CODES,*LOCALES], title={
                     'en':'Fairness · Twelve Essays in Eight Languages',
                     'zh':'公平论：十二篇八语全文',
                     'zh-hant':'公平論：十二篇八語全文',
                 }, summary={
                     'en':'All twelve essays are now available in full in Japanese, French, German, Spanish and Korean as well as English and Chinese.',
                     'zh':'十二篇新增日语、法语、德语、西班牙语与韩语全文，原有简繁中文与英文正文保留。',
                     'zh-hant':'十二篇新增日語、法語、德語、西班牙語與韓語全文，原有簡繁中文與英文正文保留。',
                 }, library_count={'en':'12 essays · 8 languages','zh':'12 篇 · 八语','zh-hant':'12 篇 · 八語'})
    output(BASE/'discovery.json', dump(entry), check)
    for path, text in connection.render(KEY).items():
        output(path, text, check)
    for path, text in discovery.render(KEY).items():
        output(path, text, check)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--import-dir', type=Path)
    p.add_argument('--date', help='ISO date of the expansion, required with --import-dir')
    mode = p.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--check-inputs', action='store_true')
    args = p.parse_args()
    if bool(args.import_dir) != bool(args.date) or (args.check_inputs and not args.import_dir) or (args.check and args.import_dir):
        p.error('--import-dir and --date go together; use --check-inputs to validate unpublished inputs')
    if args.import_dir:
        import_data(args.import_dir, args.date, check_inputs=args.check_inputs)
    if args.check_inputs:
        return
    primary_outputs(args.check)
    foreign_outputs(args.check)
    discover_outputs(args.check)
    print(('Checked' if args.check else 'Built') + ' 13 shared reading pages, 65 new-language pages, and scoped discovery.')


if __name__ == '__main__':
    main()
