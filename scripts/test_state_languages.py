#!/usr/bin/env python3
"""Full-edition checks for the State route and its three separate companions."""
from __future__ import annotations

import hashlib
import html
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from full_series_languages import ROOT, LABELS, load_language, profile, render, upgrade_primary
from prepare_original_series_review import prepare, primary_main_hashes, require_rebuilt_primary_sources
from test_companion_languages import Node, Parsed, plain_markdown
from web_analytics import TOKEN


SERIES = ('state', 'state-reversal')


class StateLanguages(unittest.TestCase):
    def test_source_correction_cannot_seal_stale_primary_html(self):
        original_text = Path.read_text
        for series in SERIES:
            target = ROOT/'essays'/series/'ep01.html'
            def stale(path, *args, **kwargs):
                text = original_text(path, *args, **kwargs)
                if path == target:
                    changed = text.replace('超过五十人', '五十人以上', 1)
                    self.assertNotEqual(changed, text)
                    return changed
                return text
            with patch.object(Path, 'read_text', stale):
                with self.assertRaisesRegex(AssertionError, 'approved source correction not rebuilt'):
                    require_rebuilt_primary_sources(profile(series))

    def test_partial_reading_records_cannot_receive_a_publication_seal(self):
        original_text=Path.read_text
        for series in SERIES:
            report=ROOT/'data'/series/'multilingual/cross-review-ja-ko.json'
            def incomplete(path,*args,**kwargs):
                text=original_text(path,*args,**kwargs)
                if path==report:
                    data=json.loads(text)
                    data['articles_reviewed']=data['articles_reviewed'][:-1]
                    return json.dumps(data)
                return text
            with patch.object(Path,'read_text',incomplete):
                with self.assertRaisesRegex(AssertionError,'incomplete article reading record'):
                    prepare(series)

    def test_reading_completion_is_not_publication_approval(self):
        original_text=Path.read_text
        for series in SERIES:
            report=ROOT/'data'/series/'multilingual/cross-review-de-fr.json'
            def unapproved(path,*args,**kwargs):
                text=original_text(path,*args,**kwargs)
                if path==report:
                    data=json.loads(text)
                    data['remaining']=[]
                    data['publication_ready']=False
                    return json.dumps(data)
                return text
            with patch.object(Path,'read_text',unapproved):
                with self.assertRaisesRegex(AssertionError,'not approved for publication'):
                    prepare(series)

    def test_review_seals_and_primary_sources_are_current(self):
        total = 0
        for series in SERIES:
            base = ROOT/'data'/series/'multilingual'
            spec = profile(series)
            for path, text in prepare(series).items():
                self.assertEqual(path.read_text(), text, path)
            receipt = json.loads((base/'publication.json').read_text())
            self.assertEqual(receipt['unresolved'], [])
            total += receipt['new_article_editions']
            preservation = json.loads((base/'preservation.json').read_text())
            self.assertEqual(primary_main_hashes(spec), preservation['primary_main'])
            for name, digest in preservation['protected_files'].items():
                self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), digest, name)
            for slug in ['index', *spec['slugs']]:
                path = ROOT/spec['directory']/(slug+'.html')
                text = path.read_text()
                self.assertEqual(upgrade_primary(text, series, slug), text, path)
        self.assertEqual(total, 55)

    def test_every_source_unit_is_visible_in_the_actual_foreign_body(self):
        editions = 0
        for series in SERIES:
            spec = profile(series)
            pages = render(series)
            self.assertEqual(len(pages), (len(spec['slugs'])+1)*5)
            for language in spec['languages']:
                _, data = load_language(series, language)
                for article in data['articles']:
                    slug = article['slug']
                    path = ROOT/spec['directory']/language/(slug+'.html')
                    source = json.loads((ROOT/'data'/series/(slug+'.json')).read_text())['body_zh']
                    text = pages[path]
                    self.assertEqual(path.read_text(), text, path)
                    page = Parsed(text)
                    self.assertEqual([n.text() for n in page.nodes('h1')], [article['title']])
                    body = page.nodes('div', 'lw-prose')
                    self.assertEqual(len(body), 1)
                    units = [n for n in body[0].children if isinstance(n, Node)]
                    self.assertEqual(len(units), len(source), path)
                    for original, draft, node in zip(source, article['body'], units):
                        is_heading = original.startswith('## ')
                        self.assertEqual(node.tag, 'h2' if is_heading else 'p')
                        self.assertEqual(node.text(), plain_markdown(draft[3:] if is_heading else draft))
                    editions += 1
        self.assertEqual(editions, 55)

    def test_fiction_notice_and_companion_context_are_not_hidden_in_sources(self):
        for series in SERIES:
            spec = profile(series)
            for language in spec['languages']:
                _, data = load_language(series, language)
                for slug in ['index', *spec['slugs']]:
                    path = ROOT/spec['directory']/language/(slug+'.html')
                    page = Parsed(path.read_text())
                    visible = [n.text() for n in page.nodes('p', 'lw-meta')]
                    self.assertIn(data['series']['notice'], visible, path)
                if series != 'state-reversal':
                    continue
                page = Parsed((ROOT/spec['directory']/language/'index.html').read_text())
                context = data['series']['index_context']
                self.assertEqual(len(context), 5)
                self.assertEqual(len([p for p in context if p.startswith('## ')]), 2)
                for unit in context:
                    self.assertIn(plain_markdown(unit[3:] if unit.startswith('## ') else unit), page.root.text())
                urls = {n.attrs.get('href') for n in page.nodes('a')}
                self.assertIn('https://www.gutenberg.org/files/1497/1497-h/1497-h.htm', urls)
                self.assertIn('https://www.gutenberg.org/cache/epub/27573/pg27573-images.html', urls)

    def test_routes_never_turn_three_companions_into_main_episodes(self):
        for series in SERIES:
            spec = profile(series)
            for language in spec['languages']:
                base = ROOT/spec['directory']/language
                page = Parsed((base/'index.html').read_text())
                self.assertEqual([n.attrs['href'] for n in page.nodes('a', 'lw-card')],
                                 [slug+'.html' for slug in spec['slugs']])
                for i, slug in enumerate(spec['slugs']):
                    page = Parsed((base/(slug+'.html')).read_text())
                    nav = page.nodes('nav', 'lw-series-nav')[0]
                    targets = [n.attrs['href'] for n in nav.walk() if n.tag == 'a']
                    expected = [spec['slugs'][i-1]+'.html' if i else 'index.html',
                                spec['slugs'][i+1]+'.html' if i+1 < len(spec['slugs']) else 'index.html']
                    self.assertEqual(targets, expected)
                    related = page.nodes('aside', 'lw-related')
                    self.assertTrue(related, base/slug)
                    other = 'state-reversal' if series == 'state' else 'state'
                    self.assertTrue(any(other+'/'+language+'/index.html' in n.attrs.get('href', '')
                                        for n in related[0].walk() if n.tag == 'a'))
        self.assertFalse((ROOT/'essays/state/ep08.html').exists())

    def test_language_targets_metadata_tracking_and_local_assets(self):
        for series in SERIES:
            spec = profile(series)
            for path, text in render(series).items():
                page = Parsed(text)
                self.assertEqual(path.read_text(), text, path)
                canonical = 'https://nondubito.net/'+str(path.relative_to(ROOT)).removesuffix('index.html')
                self.assertEqual([n.attrs['href'] for n in page.nodes('link') if n.attrs.get('rel') == 'canonical'], [canonical])
                self.assertEqual({n.attrs['hreflang'] for n in page.nodes('link') if n.attrs.get('rel') == 'alternate'},
                                 {'x-default', 'zh-Hans', *spec['languages']})
                options = page.nodes('div', 'site-shell-language-options')[0]
                choices = [n for n in options.walk() if n.tag == 'a']
                self.assertEqual(len(choices), 8)
                self.assertEqual([n.text() for n in choices if n.attrs.get('aria-current') == 'page'], [LABELS[path.parent.name]])
                beacons = [n for n in page.nodes('script') if 'cloudflareinsights.com/beacon.min.js' in n.attrs.get('src', '')]
                self.assertEqual(len(beacons), 1)
                self.assertEqual(json.loads(beacons[0].attrs['data-cf-beacon'])['token'], TOKEN)
                for node in page.root.walk():
                    raw = node.attrs.get('href') or node.attrs.get('src')
                    if not raw:
                        continue
                    url = urlsplit(html.unescape(raw))
                    if url.scheme or url.netloc or not url.path:
                        continue
                    target = (ROOT/unquote(url.path.lstrip('/')) if url.path.startswith('/') else path.parent/unquote(url.path)).resolve()
                    self.assertTrue(target.is_file(), (path, raw))

    def test_verified_engineer_correction_is_present_in_all_primary_modes(self):
        source = json.loads((ROOT/'data/state-reversal/ep02.json').read_text())
        self.assertIn('替代服务审查恢复；工程师重新提出离籍申请，后来获准。', source['body_zh'][13])
        self.assertIn('Review of alternative service resumed. Separately, the engineer reapplied to relinquish citizenship', source['body_en'][13])
        page = Parsed((ROOT/'essays/state-reversal/ep02.html').read_text())
        self.assertIn('替代服務審查恢復；工程師重新提出離籍申請，後來獲准。', page.root.text())
        receipt = json.loads((ROOT/'data/state-reversal/multilingual/source-corrections.json').read_text())
        self.assertIn('all three primary', receipt['issues'][0]['status'])
        self.assertNotIn('Rebuild all three', receipt['issues'][0]['status'])
        raw=(ROOT/receipt['primary_body_change']['path']).read_text()
        bodies=dict(re.findall(r'<div class="essay-body lw-prose lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>',raw,re.S))
        self.assertEqual(set(bodies),{'en','zh','hant'})
        for language,body in bodies.items():
            self.assertEqual(hashlib.sha256(body.encode()).hexdigest(),receipt['primary_body_change']['after_sha256'][language])

    def test_paper_verified_assembly_threshold_and_primary_change_proofs(self):
        for series in SERIES:
            receipt=json.loads((ROOT/'data'/series/'multilingual/source-corrections.json').read_text())
            source=json.loads((ROOT/'data'/series/'ep01.json').read_text())
            self.assertIn('超过五十人', ''.join(source['body_zh']))
            path=ROOT/'essays'/series/'ep01.html'
            visible=Parsed(path.read_text()).root.text()
            self.assertIn('超过五十人',visible)
            self.assertIn('超過五十人',visible)
            proofs=[receipt['primary_body_change'],*receipt.get('additional_primary_body_changes',[])]
            for proof in proofs:
                text=(ROOT/proof['path']).read_text()
                css='state-prose' if series=='state' else 'lw-prose'
                bodies=dict(re.findall(r'<div class="essay-body '+css+r' lang-(en|zh|hant)" lang="[^"]+">(.*?)</div>',text,re.S))
                self.assertEqual(set(bodies),{'en','zh','hant'})
                for language,body in bodies.items():
                    self.assertEqual(hashlib.sha256(body.encode()).hexdigest(),proof['after_sha256'][language])
                if proof['path'].endswith('/ep01.html'):
                    # The existing English already followed the original paper.
                    self.assertEqual(proof['before_sha256']['en'],proof['after_sha256']['en'])

    def test_discovery_keeps_original_entries_and_both_full_editions(self):
        updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
        for original in ['2026-10-25-state-series', '2026-10-29-state-reversal']:
            self.assertEqual(sum(u['id'] == original for u in updates), 1)
        sitemap = (ROOT/'sitemap.xml').read_text()
        for series in SERIES:
            spec = profile(series)
            update_id = '2026-11-03-'+series+'-eight-languages'
            self.assertEqual(sum(u['id'] == update_id for u in updates), 1)
            for language in spec['languages']:
                records = json.loads((ROOT/'data/search'/(language+'.json')).read_text())['records']
                for slug in spec['slugs']:
                    url = spec['directory']+'/'+language+'/'+slug+'.html'
                    self.assertEqual(sum(r['u'] == url for r in records), 1)
                    self.assertIn('https://nondubito.net/'+url, sitemap)


if __name__ == '__main__':
    unittest.main()
