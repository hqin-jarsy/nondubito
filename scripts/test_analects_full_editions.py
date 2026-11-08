#!/usr/bin/env python3
"""Complete-copy, source-preservation and route tests; not literary certification."""
import json
import re
import unittest
from urllib.parse import urlsplit, unquote
from unittest.mock import patch
import build_analects_full_editions as b
from test_companion_languages import Parsed, Node

class AnalectsFullEditions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt=b.manifest();cls.copies=b.editions();cls.outputs=b.render()

    def test_immutable_sources_and_complete_coverage(self):
        self.assertEqual(len(self.receipt['essays']),50)
        self.assertEqual(len(self.receipt['snapshots']),306)
        self.assertEqual(len(self.receipt['chinese_sources']),50)
        for group in ('received_files','snapshots','chinese_sources'):
            for path,digest in self.receipt[group].items():
                self.assertEqual(b.digest((b.DATA/path).read_bytes()),digest,path)
        received=[p for p in self.receipt['received_files'] if re.search(r'/(de|fr|es|ja|ko)\.md$',p)]
        self.assertEqual(len(received),250)
        self.assertEqual(len(list((b.DATA/'english').glob('[0-9][0-9].md'))),50)

    def test_all_300_complete_foreign_bodies_match_canonical_manuscripts(self):
        for item in self.receipt['essays']:
            for lang,copy in self.copies[item['slug']].items():
                with self.subTest(essay=item['number'],language=lang):
                    path=b.SERIES/item['file'] if lang=='en' else b.SERIES/lang/item['file']
                    text=path.read_text()
                    if lang=='en':text=b.region(text,'lang-en')
                    tree=Parsed(text)
                    self.assertEqual(tree.nodes('h1')[0].text(),copy['title'])
                    actual=[n for n in tree.nodes('div','article-body')[0].children if isinstance(n,Node)]
                    expected=[n for n in Parsed(b.body_html(copy)).root.children if isinstance(n,Node)]
                    self.assertEqual(actual,expected)
                    self.assertNotIn('**',tree.nodes('div','article-body')[0].text())
                    self.assertIn('<a href="https://doi.org/',b.body_html(copy))
                    self.assertIn('CC BY',b.body_html(copy))
                    self.assertNotIn('\ufffd',text)

    def test_chinese_changes_are_only_explicit_recorded_corrections(self):
        for item in self.receipt['essays']:
            current=(b.SERIES/item['file']).read_text()
            for code in ('zh','hant'):
                self.assertEqual(b.region(current,'lang-'+code),b.approved_chinese(item['file'],code))
        for code in ('zh','hant'):
            self.assertEqual(b.region((b.SERIES/'index.html').read_text(),'lang-'+code),b.region(b.snapshot('index.html').read_text(),'lang-'+code))
        for change in b.chinese_corrections():
            source=(b.DATA/'chinese'/f"{change['episode']:02}.md").read_text()
            self.assertEqual(source.count(change['markdown']['before']),1)
            self.assertTrue(change['evidence'])

    def test_author_decisions_are_exact_and_essay39_remains_unchanged(self):
        receipt=b.read_json(b.DATA/'review/author-decisions-20261108.json')
        self.assertEqual(len(receipt['edits']),24)
        for episode in (19,44):
            edits=[e for e in receipt['edits'] if e['episode']==episode]
            self.assertEqual({e['language'] for e in edits},{'zh','hant',*b.FOREIGN})
            item=next(x for x in self.receipt['essays'] if int(x['number'])==episode)
            for edit in edits:
                lang=edit['language']
                path=b.SERIES/item['file'] if lang in ('en','zh','hant') else b.SERIES/lang/item['file']
                text=path.read_text()
                if lang in ('en','zh','hant'):text=b.region(text,'lang-'+lang)
                visible=Parsed(text).nodes('div','article-body')[0].text()
                self.assertEqual(visible.count(edit['after']),1,(episode,lang))
                self.assertNotIn(edit['before'],visible,(episode,lang))
        self.assertEqual(len(receipt['unchanged_39']),6)
        for rel,digest in receipt['unchanged_39'].items():
            self.assertEqual(b.digest((b.ROOT/rel).read_bytes()),digest,rel)

    def test_renderers_are_portable_and_cannot_restore_abridgments(self):
        import import_analects_series as primary
        import build_analects_languages as foreign
        with patch.object(primary,'source_item',side_effect=AssertionError('External Mac source must not be required')):
            self.assertEqual(len(primary.render()),51)
            self.assertEqual(len(foreign.render()),255)
        with patch.object(b, 'manifest', side_effect=FileNotFoundError('Missing complete input')):
            with self.assertRaises(FileNotFoundError): primary.render()
            with self.assertRaises(FileNotFoundError): foreign.render()
        self.assertEqual(len(self.outputs),306)
        for path,text in self.outputs.items():self.assertEqual(path.read_text(),text,path)

    def test_titles_navigation_alternates_canonicals_and_analytics(self):
        for path,text in self.outputs.items():
            with self.subTest(path=path):
                tree=Parsed(text)
                self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1)
                links=tree.nodes('link')
                canon=[n.attrs['href'] for n in links if n.attrs.get('rel')=='canonical']
                self.assertEqual(canon,['https://nondubito.net/'+str(path.relative_to(b.ROOT)).removesuffix('index.html')])
                self.assertEqual({n.attrs['hreflang'] for n in links if n.attrs.get('rel')=='alternate'}, {'en','zh-Hans','zh-Hant','de','fr','es','ja','ko','x-default'})
                for href in re.findall(r'href="([^"]+)"',text):
                    target=urlsplit(href)
                    if target.scheme or not target.path:continue
                    self.assertTrue((path.parent/unquote(target.path)).resolve().is_file(),(path,href))
                for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S):json.loads(raw)
                if path.name!='index.html':
                    nav=tree.nodes('nav','series-nav')[0]
                    expected=1 if int(path.name[:2]) in (1,50) else 2
                    self.assertEqual(len([n for n in nav.walk() if n.tag=='a']),expected)

    def test_no_received_copy_was_retranslated_or_silently_changed(self):
        for fix in b.corrections():
            item=next(e for e in self.receipt['essays'] if int(e['number'])==int(fix['episode']))
            raw=(b.DATA/'received'/item['slug']/(fix['language']+'.md')).read_text()
            self.assertEqual(raw.count(fix['before']),1)
            self.assertTrue(fix['reason'])
            copy=self.copies[item['slug']][fix['language']]
            self.assertIn(fix['after'],'\n\n'.join(copy['blocks'])+'\n'+copy['title']+'\n'+copy['deck'])

    def test_scoped_search_records_are_fresh_and_manifest_counts_unique_pages(self):
        import build_search_index as search
        original=search.collect_pages
        try:
            search.collect_pages=lambda:list(self.outputs)
            _,fresh=search.build()
        finally:search.collect_pages=original
        unique_urls=set()
        for lang,records in fresh.items():
            actual=b.read_json(b.ROOT/f'data/search/{lang.lower()}.json')['records']
            by_url={r['u']:r for r in actual}
            unique_urls.update(by_url)
            for record in records:self.assertEqual(by_url[record['u']],record)
        self.assertEqual(b.read_json(search.OUTPUT)['record_count'],len(unique_urls))

    def test_discovery_covers_all_languages_and_new_titles(self):
        codes={'en':'en','zh-hans':'zh','zh-hant':'zh-hant','de':'de','fr':'fr','es':'es','ja':'ja','ko':'ko'}
        sitemap=(b.ROOT/'sitemap.xml').read_text()
        for lang in codes:
            records=b.read_json(b.ROOT/f'data/search/{lang}.json')['records']
            by_url={r['u']:r for r in records}
            for item in self.receipt['essays']:
                rel='essays/analects/'+('' if lang in ('en','zh-hans','zh-hant') else lang+'/')+item['file']
                self.assertIn(rel,by_url,(lang,rel))
                self.assertIn('https://nondubito.net/'+rel,sitemap)
                if lang in b.FOREIGN:self.assertTrue(by_url[rel]['t'].startswith(' '.join(self.copies[item['slug']][lang]['title'].split())))

if __name__=='__main__':unittest.main()
