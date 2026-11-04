#!/usr/bin/env python3
"""Post-publication checks requiring real complete reviews and saved pages.

Do not run these positive checks early by manufacturing approvals or receipts.
Source-only, unfinished-work checks live in test_zhuangzi_source.py instead.
These assertions verify preservation and publication, not literary quality.
"""
import hashlib
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

from full_series_languages import (ROOT, load_language, original_article,
    primary_bodies, profile, render, source_digest, upgrade_primary)
from prepare_original_series_review import prepare, primary_main_hashes
from test_companion_languages import Node, Parsed, plain_markdown
from web_analytics import TOKEN
from zhuangzi_language_index import routes

SERIES = 'zhuangzi'
BASE = ROOT/'data'/SERIES/'multilingual'
FOREIGN = ('de', 'fr', 'es', 'ja', 'ko')
# Actually captured from the fourteen existing updates before any new discovery
# entry or public page was changed. Do not replace this after publication.
OLD_UPDATES_SHA = '09e77032fb17987d6c360266ee5f7fe2e7e2cb2b32bf45aa0e958163e408eaa7'


def read(path):
    return json.loads(path.read_text())


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def stable(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def children(node):
    return [n for n in node.children if isinstance(n, Node)]


def note_text(value, sources):
    # Match entire known destinations, independently of the production narrow
    # Markdown parser. Lin Xiyi's actual destination includes parentheses.
    for source in sources:
        value = re.sub(r'\[([^\]]+)\]\('+re.escape(source['url'])+r'\)', r'\1', value)
    return plain_markdown(value)


class ZhuangziLanguages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = profile(SERIES)
        # The genuine complete-series publication seal must exist before this
        # calls the renderer. No mocked approval or partial draft render.
        cls.pages = render(SERIES)
        assert len(cls.pages) == 345
        cls.data = {code: load_language(SERIES, code)[1] for code in FOREIGN}
        for slug in ['index', *cls.spec['slugs']]:
            path = ROOT/cls.spec['directory']/(slug+'.html')
            cls.pages[path] = path.read_text()
        assert len(cls.pages) == 414

    def test_actual_complete_reviews_and_original_baselines(self):
        for path, text in prepare(SERIES).items():
            self.assertEqual(path.read_text(), text, path)
        receipt = read(BASE/'publication.json')
        self.assertEqual(receipt['new_article_editions'], 340)
        self.assertEqual(sum(receipt['source_units']), 1901)
        self.assertEqual(receipt['unresolved'], [])
        reviewed = []
        for name in ('cross-review-de-fr.json', 'cross-review-ja-ko.json', 'cross-review-es.json'):
            report = read(BASE/name)
            self.assertIs(report['publication_ready'], True)
            self.assertEqual(report['remaining'], [])
            reviewed.extend((a['language'], a['slug']) for a in report['articles_reviewed'])
        expected = {(code, slug) for code in FOREIGN for slug in self.spec['slugs']}
        self.assertEqual(len(reviewed), 340)
        self.assertEqual(set(reviewed), expected)
        before = read(BASE/'primary-before-expansion.json')
        after = read(BASE/'preservation.json')
        for key in ('source_data', 'primary_bodies', 'primary_main'):
            self.assertEqual(before[key], after[key])
        self.assertEqual(primary_main_hashes(self.spec), before['primary_main'])
        self.assertEqual(len(before['canonical_reading_files']), 204)
        for path, sha in before['canonical_reading_files'].items():
            self.assertEqual(digest((ROOT/path).read_bytes()), sha, path)
        for path, sha in before['distinct_legacy_pages'].items():
            self.assertEqual(digest((ROOT/path).read_bytes()), sha, path)
        for slug in self.spec['slugs']:
            self.assertEqual(source_digest(SERIES, self.spec, slug), before['source_data'][slug])
            text = (ROOT/self.spec['directory']/(slug+'.html')).read_text()
            self.assertEqual(digest(primary_bodies(self.spec, text)), before['primary_bodies'][slug])
        import build_zhuangzi
        manifest = read(ROOT/'data/zhuangzi/manifest.json')
        outputs = {build_zhuangzi.TARGET/'index.html': build_zhuangzi.render_index(manifest)}
        outputs.update({build_zhuangzi.TARGET/build_zhuangzi.filename(a['number']):
                        build_zhuangzi.render_article(a, manifest) for a in manifest['items']})
        outputs = {p: upgrade_primary(text, SERIES, p.stem) for p, text in outputs.items()}
        self.assertEqual(len(outputs), 69)
        for path, text in outputs.items():
            self.assertEqual(path.read_text(), text, path)

    def test_every_whole_quote_body_note_and_precise_source_survives(self):
        for code, data in self.data.items():
            totals = {'units': 0, 'h2': 0, 'quote': 0, 'notes': 0, 'refs': 0}
            for a in data['articles']:
                path = ROOT/self.spec['directory']/code/(a['slug']+'.html')
                self.assertEqual(path.read_text(), self.pages[path], path)
                page = Parsed(self.pages[path])
                body = children(page.nodes('div', 'lw-prose')[0])
                self.assertEqual(len(body), len(a['body']))
                for value, node in zip(a['body'], body):
                    tag = 'h2' if value.startswith('## ') else 'blockquote' if value.startswith('> ') else 'p'
                    raw = value[3:] if tag == 'h2' else value[2:] if tag == 'blockquote' else value
                    self.assertEqual(node.tag, tag)
                    self.assertEqual(node.text(), plain_markdown(raw))
                    totals['units'] += 1
                    totals['h2'] += tag == 'h2'
                    totals['quote'] += tag == 'blockquote'
                self.assertEqual(page.nodes('h1')[0].text(), a['title'])
                self.assertFalse(page.nodes('details', 'western-aside'))
                details = page.nodes('details', 'lw-sources')
                self.assertEqual(len(details), 1)
                self.assertNotIn('open', details[0].attrs)
                direct = children(details[0])
                heading = next(i for i, node in enumerate(direct) if node.tag == 'h2')
                self.assertEqual(direct[heading].text(), data['ui']['edition_notes'])
                self.assertEqual([n.text() for n in direct[heading+1:] if n.tag == 'p'],
                                 [note_text(n, a['sources']) for n in a['notes']])
                refs = [n for n in direct if n.tag == 'ul']
                self.assertEqual(len(refs), 1)
                links = [n for n in refs[0].walk() if n.tag == 'a']
                self.assertEqual([(n.text(), n.attrs['href']) for n in links],
                                 [(s['title'], s['url']) for s in a['sources']])
                source = original_article(SERIES, self.spec, a['slug'])
                self.assertEqual([s['url'] for s in a['sources']], [s['url'] for s in source['sources_zh']])
                self.assertNotIn('</a>/全覽)', self.pages[path])
                for note in [n for n in direct[heading+1:] if n.tag == 'p']:
                    for link in (n for n in note.walk() if n.tag == 'a'):
                        self.assertIn(unquote(link.attrs['href']), [s['url'] for s in a['sources']])
                self.assertIn(plain_markdown(a['source_note']), details[0].text())
                totals['notes'] += len(a['notes'])
                totals['refs'] += len(links)
            self.assertEqual(totals, {'units': 1901, 'h2': 507, 'quote': 129, 'notes': 175, 'refs': 178})

    def test_native_indexes_keep_non_linear_groups_and_optional_sequence(self):
        for code, data in self.data.items():
            page = Parsed(self.pages[ROOT/self.spec['directory']/code/'index.html'])
            self.assertEqual(len(page.nodes('a', 'lw-card')), 1)
            self.assertEqual(page.nodes('a', 'lw-card')[0].attrs['href'], 'guide.html')
            groups = page.nodes('section', 'zz-native-group')
            self.assertEqual([g.attrs['id'] for g in groups], [g[0] for g in routes()])
            for group, (_, _, slugs) in zip(groups, routes()):
                links = [n for n in group.walk() if n.tag == 'a' and n.attrs['href'].endswith('.html')]
                self.assertEqual([n.attrs['href'] for n in links], [s+'.html' for s in slugs])
            entries = page.nodes('div', 'zz-native-routes')[0]
            self.assertEqual([n.attrs['href'] for n in entries.walk() if n.tag == 'a'],
                             ['01.html', '11.html', '30.html', '42.html', '66.html'])
            sequence = page.nodes('details', 'zz-native-sequence')
            self.assertEqual(len(sequence), 1)
            self.assertNotIn('open', sequence[0].attrs)
            self.assertEqual([n.attrs['href'] for n in sequence[0].walk() if n.tag == 'a'],
                             [f'{n:02d}.html' for n in range(1, 68)])
            research = [n for n in page.nodes('aside') if n.attrs.get('id') == 'research']
            self.assertEqual(len(research), 1)
            self.assertEqual([n.attrs['href'] for n in research[0].walk() if n.tag == 'a'],
                             [s['url'] for s in data['articles'][0]['sources']])
            related = page.nodes('aside', 'lw-related')[0]
            for other in ('daodejing', 'analects'):
                self.assertTrue(any(n.tag == 'a' and n.attrs['href'].endswith(f'essays/{other}/{code}/index.html') for n in related.walk()))

    def test_actual_metadata_routes_analytics_and_local_fragments(self):
        for path, text in self.pages.items():
            page = Parsed(text)
            primary = path.parent.name == SERIES
            slug = path.stem
            code = path.parent.name
            canonical = 'https://nondubito.net/'+str(path.relative_to(ROOT)).removesuffix('index.html')
            self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel') == 'canonical'], [canonical])
            schemas = [json.loads(n.text()) for n in page.nodes('script') if n.attrs.get('type') == 'application/ld+json']
            self.assertEqual(len(schemas), 1)
            self.assertEqual(schemas[0]['url'], canonical)
            self.assertEqual(schemas[0]['inLanguage'], ['en', 'zh-Hans', 'zh-Hant'] if primary else code)
            if not primary and slug != 'index':
                a = next(a for a in self.data[code]['articles'] if a['slug'] == slug)
                self.assertEqual(schemas[0]['citation'], [s['url'] for s in a['sources']])
            alternate = {n.attrs['hreflang']: n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel') == 'alternate'}
            origin = 'https://nondubito.net/'+self.spec['directory']+'/'
            suffix = '' if slug == 'index' else slug+'.html'
            self.assertEqual(alternate, {'x-default': origin+suffix, 'zh-Hans': origin+suffix,
                                        **{c: origin+c+'/'+suffix for c in FOREIGN}})
            if primary:
                self.assertEqual(upgrade_primary(text, SERIES, slug), text)
            else:
                options = [n for n in page.nodes('div', 'site-shell-language-options')[0].walk() if n.tag == 'a']
                self.assertEqual(len(options), 8)
                expected = {c if c != 'zh' else 'zh-Hans': ('../'+slug+'.html?lang='+c if c in ('en', 'zh', 'zh-hant') else '../'+c+'/'+slug+'.html') for c in ('en', 'zh', 'zh-hant', *FOREIGN)}
                self.assertEqual({n.attrs['lang']: n.attrs['href'] for n in options}, expected)
                self.assertEqual([n.attrs['lang'] for n in options if n.attrs.get('aria-current') == 'page'], [code])
            beacons = [n for n in page.nodes('script') if 'cloudflareinsights.com/beacon.min.js' in n.attrs.get('src', '')]
            self.assertEqual(len(beacons), 1)
            self.assertEqual(json.loads(beacons[0].attrs['data-cf-beacon'])['token'], TOKEN)
            ids = [n.attrs['id'] for n in page.root.walk() if 'id' in n.attrs]
            self.assertEqual(len(ids), len(set(ids)))
            for node in page.root.walk():
                raw = node.attrs.get('href') or node.attrs.get('src')
                if not raw:
                    continue
                link = urlsplit(raw)
                if link.scheme or link.netloc:
                    continue
                target = ((ROOT/unquote(link.path.lstrip('/')) if link.path.startswith('/') else path.parent/unquote(link.path)).resolve() if link.path else path)
                if target.is_dir():
                    target /= 'index.html'
                self.assertTrue(target.is_file(), (path, raw))
                if link.fragment:
                    self.assertIn(unquote(link.fragment), {n.attrs.get('id') for n in Parsed(target.read_text()).root.walk()}, (path, raw))

    def test_negative_corruptions_do_not_bypass_real_approval(self):
        original_text = Path.read_text
        target = BASE/'de.json'
        for mode in ('quote', 'note', 'source-url', 'group'):
            def corrupted(path, *args, **kwargs):
                text = original_text(path, *args, **kwargs)
                if path != target:
                    return text
                data = json.loads(text)
                if mode == 'quote':
                    body = data['articles'][5]['body']
                    i = next(i for i, v in enumerate(body) if v.startswith('> '))
                    body[i] = body[i][2:]
                elif mode == 'note':
                    data['articles'][19]['notes'].pop()
                elif mode == 'source-url':
                    data['articles'][18]['sources'][-1]['url'] = 'https://example.invalid/'
                else:
                    data['series']['reading_groups'][2]['id'] = 'invented'
                return json.dumps(data)
            with self.subTest(mode=mode), patch.object(Path, 'read_text', corrupted), self.assertRaises(AssertionError):
                load_language(SERIES, 'de')
        for mode in ('approval', 'reading-record'):
            def bad_review(path, *args, **kwargs):
                text = original_text(path, *args, **kwargs)
                if path == BASE/'cross-review-de-fr.json':
                    data = json.loads(text)
                    if mode == 'approval':
                        data['publication_ready'] = False
                    else:
                        data['articles_reviewed'].pop()
                    return json.dumps(data)
                return text
            with self.subTest(mode=mode), patch.object(Path, 'read_text', bad_review), self.assertRaises(AssertionError):
                prepare(SERIES)
        original_bytes = Path.read_bytes
        for target in (BASE/'de.json', BASE/'code-audit.json',
                       BASE/'cross-review-ja-batch05.json', ROOT/'scripts/zhuangzi_source.py'):
            def changed_bytes(path):
                return original_bytes(path)+(b'\n' if path == target else b'')
            with self.subTest(path=target), patch.object(Path, 'read_bytes', changed_bytes), self.assertRaises(AssertionError):
                render(SERIES)

    def test_discovery_search_sitemap_and_unchanged_fourteen_old_updates(self):
        entry = read(BASE/'discovery.json')
        updates = read(ROOT/'data/site-updates.json')['updates']
        self.assertEqual(sum(u['id'] == entry['id'] for u in updates), 1)
        old = [u for u in updates if u['url'].startswith('essays/zhuangzi/') and u['id'] != entry['id']]
        self.assertEqual(len(old), 14)
        self.assertEqual(digest(stable(old)), OLD_UPDATES_SHA)
        self.assertEqual(next(u for u in updates if u['id'] == entry['id']),
                         {k: v for k, v in entry.items() if k not in ('library_count', 'library_url')})
        from connect_full_series_languages import render as connections
        for path, text in connections(SERIES).items():
            self.assertEqual(path.read_text(), text, path)
        locations = [n.text for n in ElementTree.fromstring((ROOT/'sitemap.xml').read_text()).iter() if n.tag.rsplit('}', 1)[-1] == 'loc']
        for code in FOREIGN:
            records = read(ROOT/'data/search'/(code+'.json'))['records']
            native = [r for r in records if r['u'].startswith(self.spec['directory']+'/'+code+'/')]
            self.assertEqual(len(native), 69)
            for slug in ['index', *self.spec['slugs']]:
                url = self.spec['directory']+'/'+code+'/'+slug+'.html'
                self.assertEqual(sum(r['u'] == url for r in records), 1)
                self.assertEqual(locations.count('https://nondubito.net/'+url.removesuffix('index.html')), 1)


if __name__ == '__main__':
    unittest.main()
