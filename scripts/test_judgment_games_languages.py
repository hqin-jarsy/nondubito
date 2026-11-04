#!/usr/bin/env python3
"""Final structural regressions for the reviewed Judgment Games editions.

Run only against the completed, sealed publication. Missing reports, approval,
pages or discovery files are failures, never a reason to bypass the review seal.
These checks detect loss and misrouting; they do not certify natural language,
the completeness of an interpretation, or the quality of independent reading.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

from full_series_languages import (
    ROOT, load_language, primary_bodies, profile, render, upgrade_primary,
)
from prepare_original_series_review import prepare, primary_main_hashes
from test_companion_languages import Node, Parsed, plain_markdown
from web_analytics import TOKEN

SERIES = 'judgment-games'
BASE = ROOT / 'data' / SERIES / 'multilingual'
FOREIGN = ('de', 'fr', 'es', 'ja', 'ko')
PRIMARY = ('en', 'zh', 'zh-hant')
SLUGS = ('overview', 'ep01', 'ep02', 'ep03')
UNITS = {'overview': 28, 'ep01': 27, 'ep02': 26, 'ep03': 34}
HEADINGS = {'overview': [5, 13, 21], 'ep01': [3, 11, 18],
            'ep02': [3, 9, 18], 'ep03': [4, 12, 23]}
SOURCES = {
    slug: 'https://self-as-an-end.net/papers/sae-judgment-games-'
          + ('overview' if slug == 'overview' else slug[-1]) + '.html'
    for slug in SLUGS
}
OLD_UPDATE = '2026-10-25-judgment-games'
# Stable JSON digest of the original editorial record, not a filesystem date.
OLD_UPDATE_SHA = '340c8b5fd2ddab994b45458860d5bc46c30718af42539fa8283c5e115cb5c58f'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes)
                          else value.encode('utf-8')).hexdigest()


def children(node):
    return [child for child in node.children if isinstance(child, Node)]


class JudgmentGamesLanguages(unittest.TestCase):
    def test_final_review_seal_preserves_all_original_reading_content(self):
        spec = profile(SERIES)
        self.assertEqual(spec['languages'], list(FOREIGN))
        self.assertEqual(spec['slugs'], list(SLUGS))
        self.assertTrue(spec['optional_pause'])
        self.assertTrue(spec['visible_notice'])
        self.assertTrue(spec['require_review_seal'])
        self.assertTrue(spec['require_explicit_publication_approval'])
        for path, expected in prepare(SERIES).items():
            self.assertEqual(path.read_text(), expected, path)
        saved = read_json(BASE / 'preservation.json')
        before = read_json(BASE / 'primary-before-expansion.json')
        for key in ('source_data', 'primary_bodies', 'primary_main'):
            self.assertEqual(saved[key], before[key], key)
        self.assertEqual(len(saved['source_data']), 4)
        self.assertEqual(len(saved['primary_main']), 5)
        self.assertEqual(primary_main_hashes(spec), before['primary_main'])
        total_bodies = 0
        for slug in SLUGS:
            source = ROOT / 'data' / SERIES / (slug + '.json')
            self.assertEqual(sha(source.read_bytes()), before['source_data'][slug])
            text = (ROOT / spec['directory'] / (slug + '.html')).read_text()
            self.assertEqual(sha(primary_bodies(spec, text)), before['primary_bodies'][slug])
            bodies = Parsed(text).nodes('div', 'essay-body')
            self.assertEqual(len(bodies), 3)
            self.assertEqual({next(c for c in ('lang-en', 'lang-zh', 'lang-hant')
                                  if b.has_class(c)) for b in bodies},
                             {'lang-en', 'lang-zh', 'lang-hant'})
            total_bodies += len(bodies)
        self.assertEqual(total_bodies, 12)
        receipt = read_json(BASE / 'publication.json')
        self.assertEqual(receipt['new_article_editions'], 20)
        self.assertEqual(receipt['source_units'], list(UNITS.values()))
        original_bytes = Path.read_bytes
        source = ROOT / 'data' / SERIES / 'overview.json'
        def changed_source(path):
            return original_bytes(path) + (b'\n' if path == source else b'')
        with patch.object(Path, 'read_bytes', changed_source):
            with self.assertRaisesRegex(AssertionError, 'Primary source differs'):
                prepare(SERIES)

    def test_incomplete_reading_unapproved_or_changed_drafts_cannot_be_sealed(self):
        # Establish that an unrelated missing final artifact is not the reason
        # either negative control raises. No mock bypasses the normal seal.
        prepare(SERIES)
        original_text = Path.read_text
        target = BASE / 'cross-review-de-fr.json'
        for mutation, error in (('approval', 'not approved'),
                                ('reading', 'incomplete article')):
            def changed(path, *args, **kwargs):
                text = original_text(path, *args, **kwargs)
                if path == target:
                    data = json.loads(text)
                    if mutation == 'approval':
                        data['publication_ready'] = False
                    else:
                        data['articles_reviewed'] = data['articles_reviewed'][:-1]
                    return json.dumps(data)
                return text
            with self.subTest(mutation=mutation), patch.object(Path, 'read_text', changed):
                with self.assertRaisesRegex(AssertionError, error):
                    prepare(SERIES)
        render(SERIES)
        original_bytes = Path.read_bytes
        draft = BASE / 'de.json'
        def changed_bytes(path):
            return original_bytes(path) + (b'\n' if path == draft else b'')
        with patch.object(Path, 'read_bytes', changed_bytes):
            with self.assertRaisesRegex(AssertionError, 'draft changed after review'):
                render(SERIES)

    def test_missing_or_invalid_optional_observations_are_rejected(self):
        # Structural negative controls only; no seal or author approval is
        # fabricated in order to render a draft.
        load_language(SERIES, 'ja')
        original = Path.read_text
        target = BASE / 'ja.json'
        for mutation in ('missing', 'empty', 'html', 'replacement-character',
                         'heading', 'note'):
            def changed(path, *args, **kwargs):
                text = original(path, *args, **kwargs)
                if path == target:
                    data = json.loads(text)
                    article = data['articles'][0]
                    if mutation == 'missing':
                        del article['pause']
                    elif mutation == 'empty':
                        article['pause'] = '  '
                    elif mutation == 'html':
                        article['pause'] = '<input>'
                    elif mutation == 'replacement-character':
                        article['pause'] = '\ufffd'
                    else:
                        data['ui']['pause_' + mutation] = ''
                    return json.dumps(data)
                return text
            with self.subTest(mutation=mutation), patch.object(Path, 'read_text', changed):
                with self.assertRaises(AssertionError):
                    load_language(SERIES, 'ja')

    def test_twenty_complete_bodies_and_all_four_observations_are_rendered(self):
        spec = profile(SERIES)
        pages = render(SERIES)
        self.assertEqual(len(pages), 25)  # 20 essays and five native indexes.
        self.assertEqual(set(pages), {ROOT / spec['directory'] / code / (slug + '.html')
                                     for code in FOREIGN for slug in ('index', *SLUGS)})
        for language in FOREIGN:
            _, data = load_language(SERIES, language)
            self.assertEqual(sum(len(a['body']) for a in data['articles']), 115)
            for article in data['articles']:
                slug = article['slug']
                path = ROOT / spec['directory'] / language / (slug + '.html')
                self.assertEqual(path.read_text(), pages[path], path)
                page = Parsed(pages[path])
                body = page.nodes('div', 'lw-prose')
                self.assertEqual(len(body), 1)
                self.assertEqual(body[0].attrs.get('lang'), language)
                nodes = children(body[0])
                self.assertEqual(len(nodes), UNITS[slug])
                self.assertEqual([i for i, node in enumerate(nodes) if node.tag == 'h2'],
                                 HEADINGS[slug])
                for text, node in zip(article['body'], nodes):
                    self.assertEqual(node.tag, 'h2' if text.startswith('## ') else 'p')
                    self.assertEqual(node.text(), plain_markdown(text[3:] if text.startswith('## ') else text))
                pause = page.nodes('aside', 'jg-pause')
                self.assertEqual(len(pause), 1)
                self.assertEqual([(n.tag, n.text()) for n in children(pause[0])],
                                 [('h2', data['ui']['pause_heading']),
                                  ('p', article['pause']), ('p', data['ui']['pause_note'])])
                # The invitation must be rendered after, not within, the prose.
                article_nodes = children(page.nodes('article', 'lw-article')[0])
                self.assertIs(article_nodes[article_nodes.index(body[0]) + 1], pause[0])
                self.assertEqual(page.nodes('h1')[0].text(), article['title'])
                self.assertEqual(page.nodes('p', 'lw-deck')[0].text(), article['deck'])
                head = page.nodes('div', 'lw-head')[0]
                kicker = next(n.text() for n in head.walk() if n.has_class('lw-kicker'))
                self.assertEqual(kicker.count(data['ui']['series']), 1)
                self.assertIn(data['series']['notice'],
                              [n.text() for n in page.nodes('p', 'lw-meta')])
                details = page.nodes('details', 'lw-sources')
                self.assertEqual(len(details), 1)
                self.assertIn(plain_markdown(article['source_note']), details[0].text())
                links = [n.attrs['href'] for n in details[0].walk() if n.tag == 'a']
                self.assertIn(SOURCES[slug], links)
                schema = self.schema(page)
                self.assertEqual(schema['citation'], SOURCES[slug])
                self.assertEqual(schema['translationOfWork']['url'],
                                 'https://nondubito.net/' + spec['directory'] + '/' + slug + '.html')

    def test_original_nonranking_map_and_four_source_paper_routes_survive(self):
        spec = profile(SERIES)
        source_map = read_json(ROOT / spec['index_context_source'])['body_zh']
        self.assertEqual(len(source_map), 2)
        self.assertEqual(source_map[0], '## 不是一张升级表')
        for slug in SLUGS:
            self.assertEqual(read_json(ROOT / 'data' / SERIES / (slug + '.json'))['source_url'], SOURCES[slug])
        original_receipt = read_json(ROOT / 'data' / SERIES / 'publication.json')
        self.assertEqual({p['url'] for p in original_receipt['papers']}, set(SOURCES.values()))
        for paper in original_receipt['papers']:
            self.assertRegex(paper['sha256'], r'^[0-9a-f]{64}$')
        for language in FOREIGN:
            _, data = load_language(SERIES, language)
            page = Parsed((ROOT / spec['directory'] / language / 'index.html').read_text())
            expected = [('h2', data['series']['index_context'][0][3:]),
                        ('p', data['series']['index_context'][1])]
            matching = [s for s in page.nodes('section', 'lw-note')
                        if [(n.tag, n.text()) for n in children(s)] == expected]
            self.assertEqual(len(matching), 1)
            self.assertEqual([n.attrs['href'] for n in page.nodes('a', 'lw-card')],
                             [s + '.html' for s in SLUGS])
            self.assertEqual([n.text() for n in page.nodes('h2') if n.text() in
                              [a['title'] for a in data['articles']]],
                             [a['title'] for a in data['articles']])
            self.assertFalse(page.nodes(css='lw-collection-group'))
            self.assertIn(plain_markdown(data['series']['source_note']),
                          page.nodes('details', 'lw-sources')[0].text())

    @staticmethod
    def schema(page):
        schemas = [json.loads(n.text()) for n in page.nodes('script')
                   if n.attrs.get('type') == 'application/ld+json']
        if len(schemas) != 1:
            raise AssertionError('Exactly one structured-data document required')
        return schemas[0]

    def test_eight_language_switches_keep_the_same_article_and_reading_modes(self):
        spec = profile(SERIES)
        for path, text in render(SERIES).items():
            page = Parsed(text)
            language = path.parent.name
            slug = path.stem
            dropdowns = page.nodes('div', 'site-shell-language-options')
            self.assertEqual(len(dropdowns), 1)
            links = [n for n in dropdowns[0].walk() if n.tag == 'a']
            expected = {code if code != 'zh' else 'zh-Hans':
                        ('../' + slug + '.html?lang=' + code if code in PRIMARY
                         else '../' + code + '/' + slug + '.html')
                        for code in (*PRIMARY, *FOREIGN)}
            self.assertEqual({n.attrs['lang']: n.attrs['href'] for n in links}, expected)
            self.assertEqual(len(links), 8)
            self.assertEqual([n.attrs['lang'] for n in links
                              if n.attrs.get('aria-current') == 'page'], [language])
        for slug in ('index', *SLUGS):
            path = ROOT / spec['directory'] / (slug + '.html')
            text = path.read_text()
            self.assertEqual(upgrade_primary(text, SERIES, slug), text)
            page = Parsed(text)
            for code in PRIMARY:
                self.assertEqual(sum(n.attrs.get('data-set-language') == code
                                     for n in page.nodes('button')), 2)
            for code in FOREIGN:
                self.assertEqual(sum(n.attrs.get('href') == code + '/' + slug + '.html'
                                     and n.attrs.get('lang') == code
                                     for n in page.nodes('a')), 2)

    def test_canonicals_schemas_analytics_unique_ids_and_no_questionnaire(self):
        spec = profile(SERIES)
        pages = render(SERIES)
        primary_paths = {ROOT / spec['directory'] / (slug + '.html')
                         for slug in ('index', *SLUGS)}
        pages.update({path: path.read_text() for path in primary_paths})
        for path, text in pages.items():
            with self.subTest(path=path.relative_to(ROOT)):
                page = Parsed(text)
                canonical = 'https://nondubito.net/' + str(path.relative_to(ROOT)).removesuffix('index.html')
                self.assertEqual([n.attrs['href'] for n in page.nodes('link')
                                  if n.attrs.get('rel') == 'canonical'], [canonical])
                self.assertEqual([n.attrs['content'] for n in page.nodes('meta')
                                  if n.attrs.get('property') == 'og:url'], [canonical])
                schema = self.schema(page)
                self.assertEqual(schema['url'], canonical)
                self.assertEqual(schema['datePublished'], '2026-10-25' if path in primary_paths else spec['date'])
                self.assertEqual(schema['inLanguage'], ['en', 'zh-Hans', 'zh-Hant']
                                 if path in primary_paths else path.parent.name)
                self.assertEqual(schema['@type'], 'CollectionPage' if path.stem == 'index' else 'Article')
                expected_alternates = {'x-default': 'https://nondubito.net/' + spec['directory'] + '/',
                                       'zh-Hans': 'https://nondubito.net/' + spec['directory'] + '/'}
                suffix = '' if path.stem == 'index' else path.stem + '.html'
                expected_alternates = {code: url + suffix for code, url in expected_alternates.items()}
                expected_alternates.update({code: 'https://nondubito.net/' + spec['directory'] + '/' + code + '/' + suffix
                                            for code in FOREIGN})
                alternates = [n for n in page.nodes('link') if n.attrs.get('rel') == 'alternate']
                self.assertEqual(len(alternates), 7)
                self.assertEqual({n.attrs['hreflang']: n.attrs['href'] for n in alternates}, expected_alternates)
                beacons = [n for n in page.nodes('script')
                           if 'cloudflareinsights.com/beacon.min.js' in n.attrs.get('src', '')]
                self.assertEqual(len(beacons), 1)
                self.assertEqual(json.loads(beacons[0].attrs['data-cf-beacon'])['token'], TOKEN)
                ids = [n.attrs['id'] for n in page.root.walk() if 'id' in n.attrs]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertFalse(page.nodes('form'))
                self.assertFalse(page.nodes('input'))
                # A primary header may eventually use the global language
                # selector. It must not become an answer/assessment control.
                for select in page.nodes('select'):
                    self.assertIn(path, primary_paths)
                    self.assertTrue(select.has_class('lang-select'))
                    self.assertFalse(select.attrs.get('name'))

    def test_all_local_link_and_fragment_targets_exist(self):
        spec = profile(SERIES)
        pages = render(SERIES)
        pages.update({ROOT / spec['directory'] / (slug + '.html'):
                      (ROOT / spec['directory'] / (slug + '.html')).read_text()
                      for slug in ('index', *SLUGS)})
        for path, text in pages.items():
            page = Parsed(text)
            for node in page.root.walk():
                raw = node.attrs.get('href') or node.attrs.get('src')
                if not raw:
                    continue
                url = urlsplit(html.unescape(raw))
                if url.scheme or url.netloc:
                    continue
                target = ((ROOT / unquote(url.path.lstrip('/')) if url.path.startswith('/')
                           else path.parent / unquote(url.path)).resolve()
                          if url.path else path)
                self.assertTrue(target.is_file(), (path, raw))
                if url.fragment:
                    target_page = Parsed(pages[target] if target in pages else target.read_text())
                    self.assertIn(url.fragment, {n.attrs['id'] for n in target_page.root.walk()
                                                 if 'id' in n.attrs}, (path, raw))

    def test_original_update_survives_and_new_editions_are_discoverable(self):
        entry = read_json(BASE / 'discovery.json')
        updates = read_json(ROOT / 'data/site-updates.json')['updates']
        original = [u for u in updates if u['id'] == OLD_UPDATE]
        self.assertEqual(len(original), 1)
        self.assertEqual(sha(json.dumps(original[0], ensure_ascii=False, sort_keys=True,
                                       separators=(',', ':'))), OLD_UPDATE_SHA)
        self.assertNotEqual(entry['id'], OLD_UPDATE)
        self.assertEqual(sum(u['id'] == entry['id'] for u in updates), 1)
        self.assertEqual(next(u for u in updates if u['id'] == entry['id']),
                         {key: value for key, value in entry.items() if key != 'library_count'})
        self.assertEqual(entry['url'], 'essays/judgment-games/index.html')
        self.assertEqual(set(entry['languages']), set((*PRIMARY, *FOREIGN)))
        sitemap = ElementTree.fromstring((ROOT / 'sitemap.xml').read_text())
        urls = [node.text for node in sitemap.iter() if node.tag.rsplit('}', 1)[-1] == 'loc']
        for language in FOREIGN:
            records = read_json(ROOT / 'data/search' / (language + '.json'))['records']
            native_records = [r for r in records if r['u'].startswith('essays/judgment-games/' + language + '/')]
            self.assertEqual(len(native_records), 5)
            self.assertEqual({r['d'] for r in native_records}, {'sae-philosophy'})
            for slug in SLUGS:
                url = f'essays/judgment-games/{language}/{slug}.html'
                self.assertEqual(sum(record['u'] == url for record in records), 1)
                self.assertEqual(urls.count('https://nondubito.net/' + url), 1)
            self.assertEqual(urls.count('https://nondubito.net/essays/judgment-games/' + language + '/'), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
