#!/usr/bin/env python3
"""Read-only regressions for every published World Football full-edition batch."""
import html
import json
import re
import subprocess
import unittest
from urllib.parse import unquote, urlsplit

import build_worldcup_full_editions as build
from test_daodejing_sources import Page


class WorldcupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(build.RECEIPT.read_text())
        cls.copies = build.manuscripts()
        cls.outputs = build.outputs()

    def test_complete_batches_and_protected_sources(self):
        self.assertEqual(len(self.copies),len(self.receipt['archives'])*5)
        for rel,expected in self.receipt['protected_files'].items():
            self.assertEqual(build.digest((build.ROOT/rel).read_bytes()),expected,rel)
        for batch in self.receipt['batches']:
            self.assertEqual(build.digest((build.ROOT/batch['plan_file']).read_bytes()),batch['plan_sha256'])
        for key,copy in self.copies.items():
            self.assertEqual(len(copy['headings']),len(copy['paragraphs_by_section']),key)
            self.assertEqual(copy['body'].count('<p>'),sum(copy['paragraphs_by_section']),key)
            self.assertNotIn('<ol>',copy['body'],key)

    def test_current_idempotent_pages(self):
        for path,expected in self.outputs.items():
            self.assertEqual(path.read_text(),expected,str(path))

    def test_source_corrections_are_exact_and_authorized(self):
        current = {}
        for correction in self.receipt.get('source_corrections', []):
            rel = correction['path']
            if rel not in current:
                current[rel] = subprocess.check_output(['git','show',self.receipt['baseline_commit']+':'+rel],cwd=build.ROOT).decode()
            self.assertEqual(build.digest(current[rel].encode()),correction['before_sha256'])
            for edit in correction['edits']:
                self.assertEqual(current[rel].count(edit['before']),1)
                current[rel] = current[rel].replace(edit['before'],edit['after'],1)
            self.assertEqual(build.digest(current[rel].encode()),correction['after_sha256'])
        for rel,expected in current.items():
            self.assertEqual((build.ROOT/rel).read_text(),expected)

    def test_exact_rendered_text(self):
        for key,copy in self.copies.items():
            ep,lang=key.split('.')
            page=Page((build.SERIES/lang/f'{ep}.html').read_text())
            body=next(n for n in page.nodes if n.has_class('worldcup-full'))
            expected=Page(copy['body'])
            self.assertEqual([n.text() for n in body.descendants('p')],
                             [n.text() for n in expected.nodes if n.tag=='p'],key)
            self.assertEqual([n.text() for n in body.descendants('h2')],copy['headings'])
            self.assertEqual([n.text() for n in page.nodes if n.tag=='h1'],[copy['title']])
            self.assertEqual([n.text() for n in page.nodes if n.has_class('essay-subtitle')],[copy['deck']])
            self.assertEqual(sum(n.has_class('worldcup-full') for n in page.nodes),1)
            self.assertEqual(sum(n.has_class('worldcup-toc') for n in page.nodes),1)
            for edit in copy['edits']:
                self.assertIn(edit['after'],(build.DATA/f'{key}.md').read_text())

    def test_ep16_headings_do_not_overstate_errors(self):
        if 'ep16' not in self.receipt['archives']:
            self.skipTest('EP16 not yet imported')
        obsolete = {
            'de': 'Drei Szenen, drei Fehlentscheidungen',
            'fr': 'Trois actions, trois erreurs d’arbitrage',
            'es': 'Tres jugadas, tres decisiones equivocadas',
            'ja': '三つとも誤った判定',
            'ko': '셋 다 잘못 판정한 장면',
        }
        for lang, phrase in obsolete.items():
            self.assertNotIn(phrase, (build.SERIES/lang/'ep16.html').read_text())
        source = (build.SERIES/'ep16.html').read_text()
        self.assertNotIn('三个都判错了的球', source)
        self.assertNotIn('Three Calls, All of Them Wrong', source)

    def test_links_metadata_and_unique_ids(self):
        for path,source in self.outputs.items():
            page=Page(source)
            ids=[n.attrs['id'] for n in page.nodes if 'id' in n.attrs]
            self.assertEqual(len(ids),len(set(ids)),str(path))
            canonical=path.relative_to(build.ROOT).as_posix()
            if path.name=='index.html': canonical=canonical.removesuffix('index.html')
            self.assertEqual([n.attrs.get('href') for n in page.nodes if n.tag=='link' and n.attrs.get('rel')=='canonical'],
                             ['https://nondubito.net/'+canonical])
            for node in page.nodes:
                if node.tag!='a': continue
                href=node.attrs.get('href','');url=urlsplit(href)
                if url.scheme or url.netloc: continue
                target=(build.ROOT/unquote(url.path).lstrip('/') if url.path.startswith('/') else path.parent/unquote(url.path)) if url.path else path
                self.assertTrue(target.exists(),(path,href))
                if target==path and url.fragment:
                    self.assertIn(unquote(url.fragment),ids)
            self.assertEqual(source.count('src="../../../language-select.js"'),1)

    def test_index_and_neighbor_titles(self):
        for lang in build.LANGS:
            for path in (build.SERIES/lang).glob('*.html'):
                page=Page(path.read_text())
                for anchor in (n for n in page.nodes if n.tag=='a'):
                    match=re.fullmatch(r'(ep\d{2})\.html',anchor.attrs.get('href',''))
                    if not match: continue
                    copy=self.copies.get(match[1]+'.'+lang)
                    if not copy: continue
                    for n in anchor.descendants():
                        if n.has_class('card-title-en'):
                            self.assertEqual(n.text(),copy['full_title'],str(path))
                        if any(n.has_class(p+'-nav-title') for p in ('series','worldcup','xiyou')):
                            self.assertEqual(n.text(),copy['title'],str(path))

    def test_unpublished_bodies_unchanged(self):
        for lang in build.LANGS:
            for path in (build.SERIES/lang).glob('ep*.html'):
                if path.stem+'.'+lang in self.copies: continue
                original=subprocess.check_output(['git','show',self.receipt['baseline_commit']+':'+path.relative_to(build.ROOT).as_posix()],cwd=build.ROOT,text=True)
                def body(source):
                    page=Page(source)
                    return next(n.text() for n in page.nodes if n.has_class('essay-body'))
                self.assertEqual(body(original),body(path.read_text()),str(path))

    def test_search_and_sitemap(self):
        sitemap=(build.ROOT/'sitemap.xml').read_text()
        for lang in build.LANGS:
            rows={r['u']:r for r in json.loads((build.ROOT/f'data/search/{lang}.json').read_text())['records']}
            for key,copy in self.copies.items():
                ep,code=key.split('.')
                if code!=lang: continue
                url=f'essays/worldcup/{lang}/{ep}.html'
                self.assertIn(copy['title'],html.unescape(rows[url]['t']))
                self.assertIn('<loc>https://nondubito.net/'+url+'</loc>',sitemap)

    def test_date_is_not_a_list(self):
        self.assertEqual(build.render('30. Juli 1930, Montevideo.'),'<p>30. Juli 1930, Montevideo.</p>')


if __name__=='__main__':
    unittest.main()
