#!/usr/bin/env python3
"""Check complete documented-case editions without mistaking alignment for quality."""
import hashlib
import html
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from full_series_languages import ROOT, load_language, profile, render, upgrade_primary
from political_economy_routes import CASE_TO_THEORY
from prepare_original_series_review import prepare, primary_main_hashes
from test_companion_languages import Node, Parsed, plain_markdown
from web_analytics import TOKEN

SERIES = 'political-economy'
BASE = ROOT/'data'/SERIES/'multilingual'


class PoliticalEconomyLanguages(unittest.TestCase):
    def test_preservation_seal_checks_sources_bodies_and_complete_primary_main(self):
        for path, text in prepare(SERIES).items():
            self.assertEqual(path.read_text(), text)
        saved = json.loads((BASE/'preservation.json').read_text())
        before = json.loads((BASE/'primary-before-expansion.json').read_text())
        for key in ('source_data', 'primary_bodies', 'primary_main'):
            self.assertEqual(saved[key], before[key])
        self.assertEqual(primary_main_hashes(profile(SERIES)), saved['primary_main'])
        self.assertEqual(json.loads((BASE/'publication.json').read_text())['new_article_editions'], 50)
        original = Path.read_bytes
        target = ROOT/'data/political-economy/apple-app-store.json'
        def changed(path):
            return original(path) + (b'\n' if path == target else b'')
        with patch.object(Path, 'read_bytes', changed):
            with self.assertRaisesRegex(AssertionError, 'Primary source differs'):
                prepare(SERIES)

    def test_full_independent_reading_and_explicit_approval_are_required(self):
        original = Path.read_text
        target = BASE/'cross-review-ja-ko.json'
        for mutation, error in [('approval', 'not approved'), ('reading', 'incomplete article')]:
            def changed(path, *args, **kwargs):
                text = original(path, *args, **kwargs)
                if path == target:
                    data = json.loads(text)
                    if mutation == 'approval': data['publication_ready'] = False
                    else: data['articles_reviewed'] = data['articles_reviewed'][:-1]
                    return json.dumps(data)
                return text
            with patch.object(Path, 'read_text', changed):
                with self.assertRaisesRegex(AssertionError, error):
                    prepare(SERIES)

    def test_fifty_complete_bodies_citations_and_all_source_notes_are_rendered(self):
        pages = render(SERIES)
        self.assertEqual(len(pages), 55)
        for language in profile(SERIES)['languages']:
            _, data = load_language(SERIES, language)
            self.assertEqual(sum(len(a['sources']) for a in data['articles']), 42)
            for a in data['articles']:
                path = ROOT/profile(SERIES)['directory']/language/(a['slug']+'.html')
                self.assertEqual(path.read_text(), pages[path])
                page = Parsed(pages[path])
                source = json.loads((ROOT/'data/political-economy'/(a['slug']+'.json')).read_text())
                body = page.nodes('div', 'lw-prose')[0]
                nodes = [n for n in body.children if isinstance(n, Node)]
                self.assertEqual(len(nodes), len(source['body_zh']))
                refs = {str(s['id']): s['url'] for s in a['sources']}
                for p, q, node in zip(source['body_zh'], a['body'], nodes):
                    self.assertEqual(node.tag, 'h2' if q.startswith('## ') else 'p')
                    self.assertEqual(node.text(), plain_markdown(q[3:] if q.startswith('## ') else q))
                    self.assertEqual(re.findall(r'\[(\d+)\]', p), re.findall(r'\[(\d+)\]', q))
                    citations = [n for n in node.walk() if n.has_class('st-cite')]
                    self.assertEqual([n.text() for n in citations], re.findall(r'\[\d+\]', q))
                    for citation in citations:
                        link = next(n for n in citation.walk() if n.tag == 'a')
                        self.assertEqual(link.attrs['href'], refs[link.text()[1:-1]])
                source_list = page.nodes('ol', 'st-source-list')[0]
                entries = [n for n in source_list.children if isinstance(n, Node)]
                self.assertEqual(len(entries), len(a['sources']))
                for entry, original in zip(entries, a['sources']):
                    link = next(n for n in entry.walk() if n.tag == 'a')
                    self.assertEqual(link.text(), original['title'])
                    self.assertEqual(link.attrs['href'], original['url'])
                    self.assertIn(plain_markdown(original['note']), entry.text())
                self.assertIn(plain_markdown(a['source_note']), page.nodes('details', 'lw-sources')[0].text())
                schema = json.loads(next(n.text() for n in page.nodes('script') if n.attrs.get('type') == 'application/ld+json'))
                self.assertEqual(schema['citation'], [s['url'] for s in source['sources']])
                if source.get('coverage'):
                    self.assertEqual(schema['temporalCoverage'], source['coverage'])

    def test_loader_rejects_missing_citations_or_replaced_evidence_urls(self):
        original = Path.read_text
        target = BASE/'de.json'
        for mutation in ('citation', 'url'):
            def changed(path, *args, **kwargs):
                text = original(path, *args, **kwargs)
                if path == target:
                    data = json.loads(text)
                    if mutation == 'url': data['articles'][1]['sources'][0]['url'] = 'https://example.org/not-the-source'
                    else: data['articles'][1]['body'][0] = data['articles'][1]['body'][0].replace('[1]', '')
                    return json.dumps(data)
                return text
            with patch.object(Path, 'read_text', changed):
                with self.assertRaises(AssertionError):
                    load_language(SERIES, 'de')

    def test_three_groups_keep_intro_eight_cases_and_closing_interlude_distinct(self):
        spec = profile(SERIES)
        for language in spec['languages']:
            _, data = load_language(SERIES, language)
            page = Parsed((ROOT/spec['directory']/language/'index.html').read_text())
            groups = page.nodes('section', 'lw-collection-group')
            self.assertEqual([g.attrs['id'] for g in groups], ['introduction', 'cases', 'closing'])
            self.assertEqual([sum(n.has_class('lw-card') for n in g.walk()) for g in groups], [1, 8, 1])
            self.assertEqual([n.text() for n in page.nodes('h3')], [a['title'] for a in data['articles']])
            self.assertEqual([n.attrs['href'] for n in page.nodes('a', 'lw-card')], [s+'.html' for s in spec['slugs']])
            self.assertIn(data['series']['count_label'], page.root.text())
            self.assertIn(data['series']['notice'], [n.text() for n in page.nodes('p', 'lw-meta')])

    def test_each_case_has_its_exact_native_theory_companions(self):
        spec = profile(SERIES)
        for language in spec['languages']:
            _, data = load_language(SERIES, language)
            _, theory = load_language('political-economy-theory', language)
            titles = {a['slug']: a['title'] for a in theory['articles']}
            for a in data['articles']:
                page = Parsed((ROOT/spec['directory']/language/(a['slug']+'.html')).read_text())
                route = page.nodes('aside', 'pe-theory-companion')[0]
                links = [n for n in route.walk() if n.tag == 'a']
                wanted = CASE_TO_THEORY[a['slug']]
                self.assertEqual([n.text() for n in links[:-1]], [titles[s] for s in wanted])
                for node, slug in zip(links[:-1], wanted):
                    target = ((ROOT/spec['directory']/language)/node.attrs['href']).resolve()
                    self.assertEqual(target, ROOT/'essays/political-economy/theory'/language/(slug+'.html'))
                self.assertIn(data['ui']['theory_note'], route.text())

    def test_all_local_links_unique_ids_language_controls_and_analytics(self):
        spec = profile(SERIES)
        for path, text in render(SERIES).items():
            page = Parsed(text)
            canonical = 'https://nondubito.net/'+str(path.relative_to(ROOT)).removesuffix('index.html')
            self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel') == 'canonical'], [canonical])
            options = page.nodes('div', 'site-shell-language-options')[0]
            self.assertEqual(len([n for n in options.walk() if n.tag == 'a']), 8)
            self.assertEqual({n.attrs['hreflang'] for n in page.nodes('link') if n.attrs.get('rel') == 'alternate'}, {'x-default', 'zh-Hans', *spec['languages']})
            beacons = [n for n in page.nodes('script') if 'cloudflareinsights.com/beacon.min.js' in n.attrs.get('src', '')]
            self.assertEqual(len(beacons), 1)
            self.assertEqual(json.loads(beacons[0].attrs['data-cf-beacon'])['token'], TOKEN)
            ids = [n.attrs['id'] for n in page.root.walk() if 'id' in n.attrs]
            self.assertEqual(len(ids), len(set(ids)))
            for node in page.root.walk():
                raw = node.attrs.get('href') or node.attrs.get('src')
                if not raw: continue
                url = urlsplit(html.unescape(raw))
                if url.scheme or url.netloc: continue
                target = (ROOT/unquote(url.path.lstrip('/')) if url.path.startswith('/') else path.parent/unquote(url.path)).resolve() if url.path else path
                self.assertTrue(target.is_file(), (path, raw))
                if url.fragment:
                    target_page = Parsed(target.read_text())
                    self.assertIn(url.fragment, {n.attrs['id'] for n in target_page.root.walk() if 'id' in n.attrs})
        for slug in ['index', *spec['slugs']]:
            path = ROOT/spec['directory']/(slug+'.html')
            self.assertEqual(upgrade_primary(path.read_text(), SERIES, slug), path.read_text())

    def test_identifiers_and_document_dates_survive_language_editing(self):
        for language in profile(SERIES)['languages']:
            _, data = load_language(SERIES, language)
            lookup = {a['slug']: a for a in data['articles']}
            thames = json.dumps(lookup['thames-water'], ensure_ascii=False)
            apple = json.dumps(lookup['apple-app-store'], ensure_ascii=False)
            self.assertIn('P30', thames)
            self.assertNotIn('P 30', thames)
            self.assertIn('DMA.100109', apple)
            self.assertNotIn('DMA. 100109', apple)

    def test_mobile_german_heading_uses_hyphenation_and_fresh_styles(self):
        css = (ROOT/'essays/language-writing/reading.css').read_text()
        self.assertRegex(css, r'html\[lang="de"\] \.lw-foreign h1\s*\{\s*hyphens:auto;\s*\}')
        for series in (SERIES, 'political-economy-theory'):
            spec = profile(series)
            page = (ROOT/spec['directory']/'de/index.html').read_text()
            self.assertIn('reading.css?v='+spec['reading_css_version'], page)

    def test_discovery_and_search_contain_both_complete_routes(self):
        entry = json.loads((BASE/'discovery.json').read_text())
        updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        self.assertEqual(sum(u['id'] == entry['id'] for u in updates), 1)
        self.assertEqual(len(entry['languages']), 8)
        self.assertTrue(any(u['id'] == '2026-11-03-political-economy-theory' for u in updates))
        sitemap = (ROOT/'sitemap.xml').read_text()
        for language in profile(SERIES)['languages']:
            records = json.loads((ROOT/'data/search'/(language+'.json')).read_text())['records']
            for series in (SERIES, 'political-economy-theory'):
                spec = profile(series)
                for slug in spec['slugs']:
                    url = spec['directory']+'/'+language+'/'+slug+'.html'
                    self.assertEqual(sum(r['u'] == url for r in records), 1)
                    self.assertIn('https://nondubito.net/'+url, sitemap)


if __name__ == '__main__':
    unittest.main()
