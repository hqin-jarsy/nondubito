#!/usr/bin/env python3
"""Real-publication preservation checks, not a language-quality certification.

Positive tests deliberately require the real independent reviews, seal, generated
pages and discovery outputs.  Mocks below only corrupt inputs to prove rejection;
they never manufacture an approval, receipt, or successful publication.
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
    primary_bodies, profile, render, source_digest, source_file, upgrade_primary)
from prepare_original_series_review import prepare, primary_main_hashes
from test_companion_languages import Node, Parsed, plain_markdown
from web_analytics import TOKEN

SERIES = 'sae-spinoza'
BASE = ROOT/'data'/SERIES/'multilingual'
FOREIGN = ('de', 'fr', 'es', 'ja', 'ko')
COUNTS = (18, 26, 22, 19, 17, 19, 16, 13, 16, 16, 16)
OLD_UPDATE = '2026-10-03-descartes-spinoza'
OLD_UPDATE_SHA = '44cfedc27caa1779d5eb31b886286e58038450a967c3032fd379840bb6d872e1'
# Captured before this expansion, covering all eight original Descartes pages.
DESCARTES_SHA = '935912ad0498a895722919997ecbfc3f7a2fb805c946b69e6cc1cc75663e7058'


def read(path):
    return json.loads(path.read_text())


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def stable(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def children(node):
    return [n for n in node.children if isinstance(n, Node)]


def all_pages():
    """Require a genuine seal before returning any rendered foreign page."""
    spec = profile(SERIES)
    pages = render(SERIES)
    assert len(pages) == 60
    for slug in ['index', *spec['slugs']]:
        path = ROOT/spec['directory']/(slug+'.html')
        pages[path] = path.read_text()
    return spec, pages


class SpinozaLanguages(unittest.TestCase):
    def test_real_reviews_original_sources_reading_modes_and_builder_preserved(self):
        spec = profile(SERIES)
        before = read(BASE/'primary-before-expansion.json')
        for path, text in prepare(SERIES).items():
            self.assertEqual(path.read_text(), text, path)
        receipt = read(BASE/'publication.json')
        self.assertEqual(receipt['new_article_editions'], 55)
        self.assertEqual(receipt['source_units'], list(COUNTS))
        self.assertEqual(receipt['unresolved'], [])
        expected = {(lang, slug) for lang in FOREIGN for slug in spec['slugs']}
        reviewed = []
        for name in ('cross-review-de-fr.json', 'cross-review-ja-ko.json', 'cross-review-es.json'):
            report = read(BASE/name)
            self.assertIs(report['publication_ready'], True)
            self.assertEqual(report['remaining'], [])
            reviewed.extend((a['language'], a['slug']) for a in report['articles_reviewed'])
        self.assertEqual(len(reviewed), 55)
        self.assertEqual(set(reviewed), expected)
        after = read(BASE/'preservation.json')
        for key in ('source_data', 'primary_bodies', 'primary_main'):
            self.assertEqual(before[key], after[key])
        self.assertEqual(primary_main_hashes(spec), before['primary_main'])
        self.assertEqual(len(before['primary_main']), 12)
        for slug in spec['slugs']:
            self.assertEqual(source_digest(SERIES, spec, slug), before['source_data'][slug])
            self.assertEqual(source_file(SERIES, spec, slug).suffix, '.json')
            text = (ROOT/spec['directory']/(slug+'.html')).read_text()
            self.assertEqual(digest(primary_bodies(spec, text)), before['primary_bodies'][slug])
            self.assertEqual(len(Parsed(text).nodes('div', 'western-prose')), 3)
        from build_western_classics import build
        outputs = build()
        self.assertEqual(len(outputs), 20)
        for path, text in outputs.items():
            self.assertEqual(path.read_text(), text, path)
        descartes = sorted((ROOT/'essays/sae-descartes').glob('*.html'))
        self.assertEqual(len(descartes), 8)
        snapshot = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in descartes}
        self.assertEqual(digest(stable(snapshot)), DESCARTES_SHA)

    def test_full_body_optional_asides_notes_and_individual_historical_sources(self):
        spec, pages = all_pages()
        for code in FOREIGN:
            _, data = load_language(SERIES, code)
            units = headings = asides = notes = source_links = 0
            for a in data['articles']:
                path = ROOT/spec['directory']/code/(a['slug']+'.html')
                self.assertEqual(path.read_text(), pages[path], path)
                page = Parsed(pages[path])
                body = page.nodes('div', 'lw-prose')[0]
                blocks = children(body)
                self.assertEqual(len(blocks), len(a['body']))
                for unit, node in zip(a['body'], blocks):
                    self.assertEqual(node.tag, 'h2' if unit.startswith('## ') else 'p')
                    self.assertEqual(node.text(), plain_markdown(unit[3:] if unit.startswith('## ') else unit))
                units += len(blocks)
                headings += sum(n.tag == 'h2' for n in blocks)
                self.assertEqual(page.nodes('h1')[0].text(), a['title'])
                optional = page.nodes('details', 'western-aside')
                self.assertEqual(len(optional), int(bool(a['aside'])))
                if optional:
                    self.assertNotIn('open', optional[0].attrs)
                    self.assertEqual([n.text() for n in children(optional[0]) if n.tag == 'p'],
                                     [plain_markdown(a['aside'])])
                    link = [n for n in optional[0].walk() if n.tag == 'a']
                    self.assertEqual(len(link), 1)
                    target = (path.parent/link[0].attrs['href']).resolve()
                    self.assertEqual(target, (ROOT/spec['aside_routes'][a['slug']].format(language=code)).resolve())
                    asides += 1
                details = [n for n in page.nodes('details', 'lw-sources') if not n.has_class('western-aside')]
                self.assertEqual(len(details), 1)
                self.assertNotIn('open', details[0].attrs)
                direct = children(details[0])
                note_heading = next(i for i, n in enumerate(direct) if n.tag == 'h2')
                self.assertEqual(direct[note_heading].text(), data['ui']['edition_notes'])
                self.assertEqual([n.text() for n in direct[note_heading+1:] if n.tag == 'p'],
                                 [plain_markdown(n) for n in a['notes']])
                refs = [n for n in direct if n.tag == 'ul']
                self.assertEqual(len(refs), 1)
                links = [n for n in refs[0].walk() if n.tag == 'a']
                self.assertEqual([(n.text(), n.attrs['href']) for n in links],
                                 [(s['title'], s['url']) for s in a['sources']])
                self.assertEqual([s['url'] for s in a['sources']],
                                 [s['url'] for s in original_article(SERIES, spec, a['slug'])['sources_zh']])
                self.assertIn(plain_markdown(a['source_note']), details[0].text())
                notes += len(a['notes'])
                source_links += len(links)
            self.assertEqual((units, headings, asides, notes, source_links), (198, 45, 9, 22, 23))

    def test_negative_loader_and_publication_gate_fail_closed(self):
        original_text = Path.read_text
        target = BASE/'de.json'
        for mode in ('note', 'aside', 'invent-aside', 'invent-closing-aside', 'source-url', 'heading'):
            def corrupted(path, *args, **kwargs):
                text = original_text(path, *args, **kwargs)
                if path != target:
                    return text
                data = json.loads(text)
                if mode == 'note': data['articles'][1]['notes'].pop()
                elif mode == 'aside': data['articles'][1]['aside'] = None
                elif mode == 'invent-aside': data['articles'][0]['aside'] = 'Invented marginal note'
                elif mode == 'invent-closing-aside': data['articles'][-1]['aside'] = 'Invented closing comparison'
                elif mode == 'source-url': data['articles'][1]['sources'][0]['url'] = 'https://example.invalid/'
                else:
                    body = data['articles'][1]['body']
                    i = next(i for i, p in enumerate(body) if p.startswith('## '))
                    body[i] = body[i][3:]
                return json.dumps(data)
            with self.subTest(mode=mode), patch.object(Path, 'read_text', corrupted), self.assertRaises(AssertionError):
                load_language(SERIES, 'de')
        # These negative checks deliberately require the real completed report;
        # they must not be made to pass early by inventing a fake review file.
        prepare(SERIES)
        for mode in ('approval', 'reading-record'):
            def corrupted_review(path, *args, **kwargs):
                text = original_text(path, *args, **kwargs)
                if path == BASE/'cross-review-de-fr.json':
                    data = json.loads(text)
                    if mode == 'approval': data['publication_ready'] = False
                    else: data['articles_reviewed'].pop()
                    return json.dumps(data)
                return text
            with self.subTest(mode=mode), patch.object(Path, 'read_text', corrupted_review), self.assertRaises(AssertionError):
                prepare(SERIES)
        original_bytes = Path.read_bytes
        for target in (BASE/'de.json', source_file(SERIES, profile(SERIES), 'intro')):
            def changed_bytes(path):
                return original_bytes(path)+(b'\n' if path == target else b'')
            with patch.object(Path, 'read_bytes', changed_bytes), self.assertRaises(AssertionError):
                render(SERIES)

    def test_indexes_have_eleven_cards_two_entries_and_honest_optional_context(self):
        spec, pages = all_pages()
        for code in FOREIGN:
            _, data = load_language(SERIES, code)
            index = Parsed(pages[ROOT/spec['directory']/code/'index.html'])
            self.assertEqual([n.attrs['href'] for n in index.nodes('a', 'lw-card')],
                             [s+'.html' for s in spec['slugs']])
            self.assertEqual(len(data['series']['index_context']), 1)
            self.assertIn(plain_markdown(data['series']['index_context'][0]), index.root.text())
            entry = [n for n in index.nodes('nav', 'lw-note') if data['ui']['entry_routes'] in n.text()]
            self.assertEqual(len(entry), 1)
            self.assertEqual([(n.text(), n.attrs['href']) for n in entry[0].walk() if n.tag == 'a'],
                             list(zip(data['series']['entry_labels'], ('intro.html', 'ep01.html'))))
            parents = [n for n in index.nodes('a') if n.attrs.get('href', '').endswith('essays/sae-western/index.html')]
            self.assertEqual(len(parents), 1)
            self.assertEqual(parents[0].text(), data['ui']['western'])
            # Native Japanese/Korean name the two real parent languages in
            # their own script; honesty does not require Latin abbreviations.
            parent_languages = {'ja': ('英語', '中国語'),
                                'ko': ('영어', '중국어')}.get(code, ('EN', '中文'))
            for language_name in parent_languages:
                self.assertIn(language_name, parents[0].text())
            self.assertIn(plain_markdown(data['series']['source_note']), index.root.text())

    def test_metadata_eight_language_routes_analytics_and_local_links(self):
        spec, pages = all_pages()
        for path, text in pages.items():
            page = Parsed(text)
            primary = path.parent.name == SERIES
            slug = path.stem
            code = path.parent.name
            canonical = 'https://nondubito.net/'+str(path.relative_to(ROOT)).removesuffix('index.html')
            self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel') == 'canonical'], [canonical])
            schemas = [json.loads(n.text()) for n in page.nodes('script') if n.attrs.get('type') == 'application/ld+json']
            self.assertEqual(len(schemas), 1)
            schema = schemas[0]
            self.assertEqual(schema['url'], canonical)
            self.assertEqual(schema['@type'], 'CollectionPage' if slug == 'index' else 'Article')
            self.assertEqual(schema['datePublished'], '2026-10-03' if primary else spec['date'])
            self.assertEqual(schema['inLanguage'], ['en', 'zh-Hans', 'zh-Hant'] if primary else code)
            if slug != 'index':
                source = original_article(SERIES, spec, slug)
                self.assertEqual(schema['citation'], [s['url'] for s in source['sources_zh']])
                self.assertNotIn(spec['source'], schema['citation'])
            elif not primary:
                self.assertEqual([p['url'] for p in schema['hasPart']],
                                 ['https://nondubito.net/'+spec['directory']+'/'+code+'/'+s+'.html' for s in spec['slugs']])
            suffix = '' if slug == 'index' else slug+'.html'
            origin = 'https://nondubito.net/'+spec['directory']+'/'
            alternate = [n for n in page.nodes('link') if n.attrs.get('rel') == 'alternate']
            self.assertEqual(len(alternate), 7)
            self.assertEqual({n.attrs['hreflang']: n.attrs['href'] for n in alternate},
                             {'x-default': origin+suffix, 'zh-Hans': origin+suffix,
                              **{lang: origin+lang+'/'+suffix for lang in FOREIGN}})
            if not primary:
                options = [n for n in page.nodes('div', 'site-shell-language-options')[0].walk() if n.tag == 'a']
                expected = {lang if lang != 'zh' else 'zh-Hans':
                            ('../'+slug+'.html?lang='+lang if lang in ('en', 'zh', 'zh-hant') else '../'+lang+'/'+slug+'.html')
                            for lang in ('en', 'zh', 'zh-hant', *FOREIGN)}
                self.assertEqual(len(options), 8)
                self.assertEqual({n.attrs['lang']: n.attrs['href'] for n in options}, expected)
                self.assertEqual([n.attrs['lang'] for n in options if n.attrs.get('aria-current') == 'page'], [code])
            else:
                self.assertEqual(upgrade_primary(text, SERIES, slug), text)
                # Desktop and drawer both retain three inline reading modes and
                # link to the corresponding article in each native language.
                for lang in ('en', 'zh', 'zh-hant'):
                    self.assertEqual(sum(n.attrs.get('data-set-language') == lang for n in page.nodes('button')), 2)
                for lang in FOREIGN:
                    self.assertEqual(sum(n.attrs.get('href') == lang+'/'+slug+'.html' for n in page.nodes('a')), 2)
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
                target = ((ROOT/unquote(link.path.lstrip('/')) if link.path.startswith('/') else path.parent/unquote(link.path)).resolve()
                          if link.path else path)
                if target.is_dir(): target /= 'index.html'
                self.assertTrue(target.is_file(), (path, raw))
                if link.fragment:
                    self.assertIn(unquote(link.fragment), {n.attrs.get('id') for n in Parsed(target.read_text()).root.walk()}, (path, raw))

    def test_single_new_discovery_search_sitemap_and_unchanged_old_update(self):
        spec = profile(SERIES)
        entry = read(BASE/'discovery.json')
        ledger = read(ROOT/'data/site-updates.json')['updates']
        self.assertEqual(sum(u['id'] == entry['id'] for u in ledger), 1)
        old = [u for u in ledger if u['id'] == OLD_UPDATE]
        self.assertEqual(len(old), 1)
        self.assertEqual(digest(stable(old[0])), OLD_UPDATE_SHA)
        self.assertEqual([u for u in ledger if u['id'] == entry['id']][0],
                         {k: v for k, v in entry.items() if k not in ('library_count', 'library_url')})
        from connect_full_series_languages import render as connections
        for path, text in connections(SERIES).items():
            self.assertEqual(path.read_text(), text, path)
        locations = [n.text for n in ElementTree.fromstring((ROOT/'sitemap.xml').read_text()).iter()
                     if n.tag.rsplit('}', 1)[-1] == 'loc']
        for code in FOREIGN:
            records = read(ROOT/'data/search'/(code+'.json'))['records']
            native = [r for r in records if r['u'].startswith(spec['directory']+'/'+code+'/')]
            self.assertEqual(len(native), 12)
            for slug in ['index', *spec['slugs']]:
                url = spec['directory']+'/'+code+'/'+slug+'.html'
                self.assertEqual(sum(r['u'] == url for r in records), 1)
                canonical = 'https://nondubito.net/'+url.removesuffix('index.html')
                self.assertEqual(locations.count(canonical), 1)
        # The existing parent shelf must honestly expose the new language count;
        # it is not acceptable merely to add a separate Library/Latest card.
        shelf = Parsed((ROOT/'essays/sae-western/index.html').read_text())
        books = [n for n in shelf.nodes('a', 'western-book') if n.attrs.get('href') == '../sae-spinoza/index.html']
        self.assertEqual(len(books), 1)
        labels = {code: [n.text() for n in books[0].walk()
                         if n.tag == 'p' and n.has_class('western-meta')
                         and n.has_class('lang-'+code)]
                  for code in ('en', 'zh', 'hant')}
        self.assertEqual(labels, {
            'en': ['Introduction + 10 essays · Eight languages'],
            'zh': ['小引＋十篇正文 · 八语全文'],
            'hant': ['小引＋十篇正文 · 八語全文']})



if __name__ == "__main__":
    unittest.main()
