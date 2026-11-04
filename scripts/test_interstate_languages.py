#!/usr/bin/env python3
"""Publication checks for nine full Interstate essays in five new languages."""
import hashlib
import html
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from full_series_languages import ROOT, load_language, profile, render, upgrade_primary
from prepare_original_series_review import prepare, primary_main_hashes
from test_companion_languages import Node, Parsed, plain_markdown
from web_analytics import TOKEN


class InterstateLanguages(unittest.TestCase):
    def test_first_seal_cannot_silently_rebaseline_changed_original_data(self):
        original = Path.read_bytes
        target = ROOT/'data/interstate/ep01.json'
        def changed(path):
            data = original(path)
            return data + b'\n' if path == target else data
        with patch.object(Path, 'read_bytes', changed):
            with self.assertRaisesRegex(AssertionError, 'Primary source differs from pre-expansion baseline'):
                prepare('interstate')

    def test_seal_protects_original_bodies_and_all_primary_reading_content(self):
        spec = profile('interstate')
        base = ROOT/'data/interstate/multilingual'
        for path, text in prepare('interstate').items():
            self.assertEqual(path.read_text(), text, path)
        receipt = json.loads((base/'publication.json').read_text())
        self.assertEqual(receipt['new_article_editions'], 45)
        self.assertEqual(receipt['unresolved'], [])
        saved = json.loads((base/'preservation.json').read_text())
        before = json.loads((base/'primary-before-expansion.json').read_text())
        self.assertEqual(before['source_data'], saved['source_data'])
        self.assertEqual(before['primary_bodies'], saved['primary_bodies'])
        self.assertEqual(before['primary_main'], saved['primary_main'])
        self.assertEqual(primary_main_hashes(spec), saved['primary_main'])
        for path, digest in saved['protected_files'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(), digest)
        for slug in ['index', *spec['slugs']]:
            text = (ROOT/spec['directory']/(slug+'.html')).read_text()
            self.assertEqual(upgrade_primary(text, 'interstate', slug), text)

    def test_full_approval_and_actual_reading_records_are_required(self):
        original = Path.read_text
        target = ROOT/'data/interstate/multilingual/cross-review-ja-ko.json'
        for mutation, error in [('unapproved', 'not approved for publication'),
                                ('partial', 'incomplete article reading record')]:
            def changed(path, *args, **kwargs):
                text = original(path, *args, **kwargs)
                if path == target:
                    report = json.loads(text)
                    if mutation == 'unapproved':
                        report['publication_ready'] = False
                    else:
                        report['articles_reviewed'] = report['articles_reviewed'][:-1]
                    return json.dumps(report)
                return text
            with patch.object(Path, 'read_text', changed):
                with self.assertRaisesRegex(AssertionError, error):
                    prepare('interstate')

    def test_actual_foreign_html_keeps_every_source_unit(self):
        pages = render('interstate')
        self.assertEqual(len(pages), 50)
        editions = 0
        for language in profile('interstate')['languages']:
            _, data = load_language('interstate', language)
            for article in data['articles']:
                path = ROOT/'essays/interstate'/language/(article['slug']+'.html')
                page = Parsed(pages[path])
                self.assertEqual(path.read_text(), pages[path])
                source = json.loads((ROOT/'data/interstate'/(article['slug']+'.json')).read_text())['body_zh']
                body = page.nodes('div', 'lw-prose')
                self.assertEqual(len(body), 1)
                units = [n for n in body[0].children if isinstance(n, Node)]
                self.assertEqual(len(units), len(source))
                for original, target, node in zip(source, article['body'], units):
                    heading = original.startswith('## ')
                    self.assertEqual(node.tag, 'h2' if heading else 'p')
                    self.assertEqual(node.text(), plain_markdown(target[3:] if heading else target))
                self.assertEqual([n.text() for n in page.nodes('h1')], [article['title']])
                editions += 1
        self.assertEqual(editions, 45)

    def test_three_complete_groups_keep_numbers_and_working_jump_targets(self):
        spec = profile('interstate')
        for language in spec['languages']:
            _, data = load_language('interstate', language)
            page = Parsed((ROOT/'essays/interstate'/language/'index.html').read_text())
            self.assertEqual([n.attrs['href'] for n in page.nodes('a', 'lw-card')],
                             [slug+'.html' for slug in spec['slugs']])
            groups = page.nodes('section', 'lw-collection-group')
            self.assertEqual([g.attrs['id'] for g in groups], ['agreements', 'protection', 'afterwards'])
            self.assertEqual([sum(n.has_class('lw-card') for n in g.walk()) for g in groups], [4, 3, 2])
            self.assertEqual([n.text() for n in page.nodes('h3')], [a['title'] for a in data['articles']])
            self.assertEqual([n.text() for n in page.nodes('p', 'lw-kicker')][1:], [f'{i:02d}' for i in range(1, 10)])
            ids = {n.attrs['id'] for n in page.root.walk() if 'id' in n.attrs}
            for link in page.nodes('a'):
                href = link.attrs.get('href', '')
                if href.startswith('#'):
                    self.assertIn(href[1:], ids)
            self.assertTrue(any('grouped-reading.css' in n.attrs.get('href', '') for n in page.nodes('link')))

    def test_visible_fiction_scope_does_not_imply_translated_history(self):
        for language in profile('interstate')['languages']:
            _, data = load_language('interstate', language)
            for slug in ['index', *profile('interstate')['slugs']]:
                page = Parsed((ROOT/'essays/interstate'/language/(slug+'.html')).read_text())
                self.assertIn(data['series']['notice'], [n.text() for n in page.nodes('p', 'lw-meta')])
                urls = [n.attrs.get('href', '') for n in page.nodes('a')]
                histories = [url for url in urls if 'cooperation-histories/' in url]
                self.assertEqual(histories, ['https://nondubito.net/essays/cooperation-histories/index.html?lang=en'])
                self.assertTrue(any('essays/state/'+language+'/index.html' in url for url in urls))

    def test_previous_next_and_return_keep_the_nine_article_route(self):
        slugs = profile('interstate')['slugs']
        for language in profile('interstate')['languages']:
            for index, slug in enumerate(slugs):
                page = Parsed((ROOT/'essays/interstate'/language/(slug+'.html')).read_text())
                nav = page.nodes('nav', 'lw-series-nav')[0]
                targets = [n.attrs['href'] for n in nav.walk() if n.tag == 'a']
                expected = [slugs[index-1]+'.html' if index else 'index.html#reading-route',
                            slugs[index+1]+'.html' if index+1 < len(slugs) else 'index.html#reading-route']
                self.assertEqual(targets, expected)

    def test_metadata_language_targets_and_tracking(self):
        spec = profile('interstate')
        for path, text in render('interstate').items():
            page = Parsed(text)
            canonical = 'https://nondubito.net/'+str(path.relative_to(ROOT)).removesuffix('index.html')
            self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel') == 'canonical'], [canonical])
            options = page.nodes('div', 'site-shell-language-options')[0]
            self.assertEqual(len([n for n in options.walk() if n.tag == 'a']), 8)
            self.assertEqual({n.attrs['hreflang'] for n in page.nodes('link') if n.attrs.get('rel') == 'alternate'},
                             {'x-default', 'zh-Hans', *spec['languages']})
            beacons = [n for n in page.nodes('script') if 'cloudflareinsights.com/beacon.min.js' in n.attrs.get('src', '')]
            self.assertEqual(len(beacons), 1)
            self.assertEqual(json.loads(beacons[0].attrs['data-cf-beacon'])['token'], TOKEN)
            ids = [n.attrs['id'] for n in page.root.walk() if 'id' in n.attrs]
            self.assertEqual(len(ids), len(set(ids)))
            for node in page.root.walk():
                raw = node.attrs.get('href') or node.attrs.get('src')
                if not raw:
                    continue
                url = urlsplit(html.unescape(raw))
                if url.scheme or url.netloc or not url.path:
                    continue
                target = (ROOT/unquote(url.path.lstrip('/')) if url.path.startswith('/') else path.parent/unquote(url.path)).resolve()
                self.assertTrue(target.is_file(), (path, raw))

    def test_noncombat_help_is_not_restricted_to_civilian_only_support(self):
        for language, incorrect in [('de', 'nichtmilitär'), ('fr', 'non militaire')]:
            _, data = load_language('interstate', language)
            for slug, paragraph in [('ep06', 10), ('ep06', 28), ('ep06', 29), ('ep07', 29)]:
                article = next(a for a in data['articles'] if a['slug'] == slug)
                self.assertNotIn(incorrect, article['body'][paragraph].lower())
        for language in profile('interstate')['languages']:
            state = Parsed((ROOT/'essays/state'/language/'index.html').read_text())
            self.assertTrue(any('interstate/'+language+'/index.html' in n.attrs.get('href', '')
                                for n in state.nodes('a')))

    def test_discovery_search_and_sitemap_keep_old_entries(self):
        updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        self.assertEqual(sum(u['id'] == '2026-11-03-interstate-eight-languages' for u in updates), 1)
        original = [u for u in updates if u['url'] == 'essays/interstate/index.html' and u['id'] != '2026-11-03-interstate-eight-languages']
        self.assertTrue(original)
        sitemap = (ROOT/'sitemap.xml').read_text()
        for language in profile('interstate')['languages']:
            records = json.loads((ROOT/'data/search'/(language+'.json')).read_text())['records']
            for slug in profile('interstate')['slugs']:
                url = f'essays/interstate/{language}/{slug}.html'
                self.assertEqual(sum(r['u'] == url for r in records), 1)
                self.assertIn('https://nondubito.net/'+url, sitemap)


if __name__ == '__main__':
    unittest.main()
