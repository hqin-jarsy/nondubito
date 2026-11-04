#!/usr/bin/env python3
"""Full-edition checks; structural coverage does not replace prose review."""
import hashlib
import html
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from full_series_languages import ROOT, profile, source_directory, load_language, render, upgrade_primary
from prepare_original_series_review import prepare, primary_main_hashes
from test_companion_languages import Node, Parsed, plain_markdown
from web_analytics import TOKEN

SERIES = 'political-economy-theory'
BASE = ROOT/'data'/SERIES/'multilingual'


class PoliticalEconomyTheoryLanguages(unittest.TestCase):
    def test_source_alias_does_not_copy_or_escape_published_sources(self):
        self.assertEqual(source_directory(SERIES), ROOT/'data/political-economy/theory')
        self.assertFalse((ROOT/'data'/SERIES/'ep01.json').exists())
        with self.assertRaises(AssertionError):
            source_directory(SERIES, {'source_directory':'../outside'})

    def test_first_seal_preserves_nested_sources_bodies_and_complete_main(self):
        for path, text in prepare(SERIES).items():
            self.assertEqual(path.read_text(), text)
        saved = json.loads((BASE/'preservation.json').read_text())
        before = json.loads((BASE/'primary-before-expansion.json').read_text())
        for key in ('source_data', 'primary_bodies', 'primary_main'):
            self.assertEqual(saved[key], before[key])
        self.assertEqual(primary_main_hashes(profile(SERIES)), saved['primary_main'])
        self.assertEqual(json.loads((BASE/'publication.json').read_text())['new_article_editions'], 40)
        original = Path.read_bytes
        target = ROOT/'data/political-economy/theory/ep01.json'
        def changed(path):
            return original(path) + (b'\n' if path == target else b'')
        with patch.object(Path, 'read_bytes', changed):
            with self.assertRaisesRegex(AssertionError, 'Primary source differs'):
                prepare(SERIES)

    def test_independent_full_reading_and_explicit_approval_required(self):
        original = Path.read_text
        target = BASE/'cross-review-ja-ko.json'
        for mutation, error in [('approval', 'not approved'), ('reading', 'incomplete article')]:
            def changed(path, *args, **kwargs):
                text = original(path, *args, **kwargs)
                if path == target:
                    d = json.loads(text)
                    if mutation == 'approval': d['publication_ready'] = False
                    else: d['articles_reviewed'] = d['articles_reviewed'][:-1]
                    return json.dumps(d)
                return text
            with patch.object(Path, 'read_text', changed):
                with self.assertRaisesRegex(AssertionError, error):
                    prepare(SERIES)

    def test_forty_full_bodies_and_takeaways_are_actually_rendered(self):
        pages = render(SERIES)
        self.assertEqual(len(pages), 45)
        for language in profile(SERIES)['languages']:
            _, data = load_language(SERIES, language)
            for a in data['articles']:
                path = ROOT/profile(SERIES)['directory']/language/(a['slug']+'.html')
                self.assertEqual(path.read_text(), pages[path])
                page = Parsed(pages[path])
                body = page.nodes('div', 'lw-prose')
                self.assertEqual(len(body), 1)
                nodes = [n for n in body[0].children if isinstance(n, Node)]
                source = json.loads((source_directory(SERIES)/(a['slug']+'.json')).read_text())
                self.assertEqual(len(nodes), len(source['body_zh']))
                for p, node in zip(a['body'], nodes):
                    self.assertEqual(node.tag, 'h2' if p.startswith('## ') else 'p')
                    self.assertEqual(node.text(), plain_markdown(p[3:] if p.startswith('## ') else p))
                takeaway = page.nodes('aside', 'pe-takeaway')
                self.assertEqual(len(takeaway), 1)
                self.assertIn(a['takeaway'], takeaway[0].text())
                self.assertEqual([n.text() for n in page.nodes('h1')], [a['title']])

    def test_optional_deeper_reading_is_separate_and_order_is_preserved(self):
        spec = profile(SERIES)
        for language in spec['languages']:
            _, data = load_language(SERIES, language)
            page = Parsed((ROOT/spec['directory']/language/'index.html').read_text())
            groups = page.nodes('section', 'lw-collection-group')
            self.assertEqual([g.attrs['id'] for g in groups], ['reading-main', 'deeper'])
            self.assertEqual([sum(n.has_class('lw-card') for n in g.walk()) for g in groups], [7, 1])
            self.assertEqual([n.text() for n in page.nodes('h3')], [a['title'] for a in data['articles']])
            self.assertEqual([n.attrs['href'] for n in page.nodes('a', 'lw-card')], [s+'.html' for s in spec['slugs']])
            self.assertIn(data['series']['notice'], [n.text() for n in page.nodes('p', 'lw-meta')])

    def test_documented_cases_remain_distinct_and_honestly_labeled(self):
        spec = profile(SERIES)
        for language in spec['languages']:
            _, data = load_language(SERIES, language)
            index = Parsed((ROOT/spec['directory']/language/'index.html').read_text())
            route = index.nodes('aside', 'pe-case-route')[0]
            self.assertNotIn('EN / 中文', route.text())
            self.assertEqual([n.attrs['href'] for n in route.walk() if n.tag == 'a'], ['../../'+language+'/index.html#cases'])
            _, cases = load_language('political-economy', language)
            titles = {a['slug']: a['title'] for a in cases['articles']}
            for a in data['articles']:
                page = Parsed((ROOT/spec['directory']/language/(a['slug']+'.html')).read_text())
                companion = page.nodes('aside', 'pe-case-companion')[0]
                links = [n for n in companion.walk() if n.tag == 'a']
                source = json.loads((source_directory(SERIES)/(a['slug']+'.json')).read_text())
                self.assertEqual([n.attrs['href'] for n in links], ['../../'+language+'/'+s+'.html' for s in source['case_slugs']])
                self.assertEqual([n.text() for n in links], [titles[s] for s in source['case_slugs']])
                self.assertIn(data['ui']['case_note'], companion.text())
                self.assertEqual([x['slug'] for x in a['case_links']], source['case_slugs'])

    def test_local_links_metadata_language_switches_and_analytics(self):
        spec = profile(SERIES)
        for path, text in render(SERIES).items():
            page = Parsed(text)
            canonical = 'https://nondubito.net/'+str(path.relative_to(ROOT)).removesuffix('index.html')
            self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel') == 'canonical'], [canonical])
            self.assertEqual(len([n for n in page.nodes('div', 'site-shell-language-options')[0].walk() if n.tag == 'a']), 8)
            self.assertEqual({n.attrs['hreflang'] for n in page.nodes('link') if n.attrs.get('rel') == 'alternate'}, {'x-default','zh-Hans',*spec['languages']})
            beacons = [n for n in page.nodes('script') if 'cloudflareinsights.com/beacon.min.js' in n.attrs.get('src', '')]
            self.assertEqual(len(beacons), 1)
            self.assertEqual(json.loads(beacons[0].attrs['data-cf-beacon'])['token'], TOKEN)
            ids = [n.attrs['id'] for n in page.root.walk() if 'id' in n.attrs]
            self.assertEqual(len(ids), len(set(ids)))
            for n in page.root.walk():
                raw = n.attrs.get('href') or n.attrs.get('src')
                if not raw: continue
                url = urlsplit(html.unescape(raw))
                if url.scheme or url.netloc: continue
                target = (ROOT/unquote(url.path.lstrip('/')) if url.path.startswith('/') else path.parent/unquote(url.path)).resolve() if url.path else path
                self.assertTrue(target.is_file(), (path, raw))
                if url.fragment:
                    target_page = Parsed(target.read_text())
                    self.assertIn(url.fragment, {x.attrs['id'] for x in target_page.root.walk() if 'id' in x.attrs})
        for slug in ['index', *spec['slugs']]:
            path = ROOT/spec['directory']/(slug+'.html')
            self.assertEqual(upgrade_primary(path.read_text(), SERIES, slug), path.read_text())

    def test_single_parent_discovery_covers_both_routes_and_previous_entries_survive(self):
        entry = json.loads((ROOT/'data/political-economy/multilingual/discovery.json').read_text())
        updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        self.assertEqual(sum(x['id'] == entry['id'] for x in updates), 1)
        self.assertTrue(any(x['id'] == '2026-11-03-political-economy-theory' for x in updates))
        self.assertEqual(entry['url'], 'essays/political-economy/index.html')
        sitemap = (ROOT/'sitemap.xml').read_text()
        for language in profile(SERIES)['languages']:
            records = json.loads((ROOT/'data/search'/(language+'.json')).read_text())['records']
            for slug in profile(SERIES)['slugs']:
                url = f'essays/political-economy/theory/{language}/{slug}.html'
                self.assertEqual(sum(r['u'] == url for r in records), 1)
                self.assertIn('https://nondubito.net/'+url, sitemap)


if __name__ == '__main__':
    unittest.main()
