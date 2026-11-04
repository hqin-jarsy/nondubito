#!/usr/bin/env python3
"""Inventory published Library content, not drafts or legacy unlisted aliases.

This checks edition presence, NOT translation quality. A review is required
before any pending series is marked editorially complete.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

from build_content_registry import extract_canonical, language_from_directory, parse_library_categories

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ('en', 'zh-hans', 'zh-hant', 'ja', 'fr', 'de', 'es', 'ko')
FOREIGN_LANGUAGES = ('ja', 'fr', 'de', 'es', 'ko')
OUTPUT = ROOT/'reports/multilingual-coverage.json'
WORK_COLLECTIONS = {'literature', 'science-fiction', 'anime', 'tv', 'wuxia', 'games', 'everyday', 'art'}


def active_roots():
    roots = set()
    for category in parse_library_categories(ROOT/'library.html'):
        for href in category['series_hrefs']:
            path = Path(unquote(urlsplit(href).path))
            if not path.suffix:
                path /= 'index.html'
            if not (ROOT/path).is_file():
                continue
            # Library has a few preserved old links to relocated collections.
            url = urlsplit(extract_canonical((ROOT/path).read_text()))
            if url.netloc == 'nondubito.net':
                candidate = Path(unquote(url.path).lstrip('/'))
                if not candidate.suffix:
                    candidate /= 'index.html'
                if (ROOT/candidate).is_file():
                    path = candidate
            roots.add(path.as_posix())
    return roots


def group_key(path):
    parts = Path(path).parts
    depth = 3 if len(parts) > 3 and parts[1] in WORK_COLLECTIONS else 2
    return '/'.join(parts[:depth])


def build():
    roots = active_roots()
    prefixes = {str(Path(p).parent) + '/' for p in roots if Path(p).name == 'index.html'}
    editions = defaultdict(dict)
    titles = {}
    for language in LANGUAGES:
        chunk = json.loads((ROOT/'data/search'/f'{language}.json').read_text())
        for record in chunk['records']:
            if record['k'] not in ('essay', 'story'):
                continue
            path = Path(record['u'])
            _, original = language_from_directory(path, ROOT)
            identity = (original or path).as_posix()
            if identity not in roots and not any(identity.startswith(prefix) for prefix in prefixes):
                continue
            editions[identity][language] = record['u']
            if language == 'zh-hans':
                titles[identity] = record['t']
    groups = defaultdict(list)
    for identity, languages in sorted(editions.items()):
        # The Chinese publication is the editorial source for this expansion.
        if 'zh-hans' not in languages:
            continue
        groups[group_key(identity)].append({
            'source': identity, 'title_zh': titles[identity],
            'available_languages': list(languages),
            'missing': [language for language in FOREIGN_LANGUAGES if language not in languages],
            # Some older English/Hant modes are implemented by JS rather than
            # separate HTML. Absence from a search chunk is NOT proof of absence.
            'primary_modes_needing_manual_verification': [language for language in ('en', 'zh-hant') if language not in languages],
        })
    rows = []
    for name, articles in sorted(groups.items()):
        missing = sum(len(a['missing']) for a in articles)
        rows.append({'series': name, 'article_count': len(articles),
                     'missing_editions': missing,
                     'route_status': 'foreign-editions-incomplete' if missing else 'five-foreign-editions-present',
                     'quality_status': 'not_assessed_by_this_inventory',
                     'articles': articles})
    return {
        'date': '2026-11-03',
        'scope': 'Published Chinese-source articles discoverable through the current Library; index pages are not counted as articles.',
        'method': 'Current search language chunks, normalized edition identities, active Library roots and canonical relocation links. Missing counts cover JA/FR/DE/ES/KO only; English/Hant reading modes not recognized by search require manual verification, not automatic rewriting. Route presence is not an editorial quality verdict.',
        'excluded': ['unlisted legacy URLs', 'drafts and unpublished continuation chapters', 'navigation-only pages'],
        'series_count': len(rows),
        'incomplete_series_count': sum(bool(r['missing_editions']) for r in rows),
        'article_count': sum(r['article_count'] for r in rows),
        'articles_with_gaps': sum(bool(a['missing']) for r in rows for a in r['articles']),
        'missing_editions': sum(r['missing_editions'] for r in rows),
        'series': rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = build()
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.check:
        assert OUTPUT.read_text() == text, 'Multilingual coverage inventory is stale'
    else:
        OUTPUT.write_text(text)
    print(json.dumps({k: v for k, v in report.items() if k.endswith('_count') or k in ('article_count', 'articles_with_gaps', 'missing_editions')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
