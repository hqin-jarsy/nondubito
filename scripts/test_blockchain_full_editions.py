#!/usr/bin/env python3
"""Read-only checks of complete Blockchain editions, not semantic review proof."""
import hashlib
import html
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit

import build_blockchain_full_editions as build
from test_companion_languages import Parsed


class FullEditions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records=build.records()
        assert cls.records, 'No reviewed Blockchain batches'

    def test_all_eight_editions_match_complete_records(self):
        for slug,record in self.records.items():
            for lang,edition in record['languages'].items():
                with self.subTest(essay=slug,language=lang):
                    source=build.page_path(lang,slug).read_text()
                    tree=Parsed(source)
                    containers=tree.nodes('article','essay-body') if lang in ('zh','zh-hant','en') else tree.nodes('div','collection-body')
                    self.assertEqual(len(containers),1)
                    body=containers[0]
                    def descendants(node,tag):
                        return [n for n in node.walk() if getattr(n,'tag',None)==tag
                                and not n.has_class('source-note')]
                    headings=descendants(body,'h2')
                    self.assertEqual([n.text() for n in headings],[s['heading'] for s in edition['sections']])
                    self.assertEqual([n.attrs['id'] for n in headings],[f'section-{i}' for i in range(1,9)])
                    # Skip the separately marked note and TOC containers.
                    paras=[]
                    def visit(node):
                        if not hasattr(node,'tag') or node.has_class('source-note') or node.tag=='details':return
                        if node.tag=='p':paras.append(node.text());return
                        for child in node.children:visit(child)
                    visit(body)
                    expected=[build.plain(build.paragraph_html(p)) for s in edition['sections'] for p in s['paragraphs']]
                    self.assertEqual(paras,expected)
                    notes=[n for n in body.walk() if getattr(n,'tag',None)=='div' and n.has_class('source-note')]
                    self.assertEqual(len(notes),1)
                    self.assertIn(build.plain(build.paragraph_html(edition['note'])),notes[0].text())
                    menus=tree.nodes('span','blockchain-language-menu')
                    self.assertEqual(len(menus),1)
                    links=[n for n in menus[0].walk() if getattr(n,'tag',None)=='a']
                    self.assertEqual({n.attrs.get('data-language') for n in links},set(build.LANGS))
                    self.assertNotIn('\ufffd',source)
                    self.assertEqual(source.count('static.cloudflareinsights.com/beacon.min.js'),1)

    def test_source_corrections_are_synchronized_and_chinese_otherwise_preserved(self):
        for slug,record in self.records.items():
            coords={(e['section'],e['paragraph']) for e in record['edits'] if e['lang']=='zh'}
            for section,paragraph in coords:
                found=[e['lang'] for e in record['edits'] if (e['section'],e['paragraph'])==(section,paragraph)]
                self.assertEqual(set(found),set(build.LANGS),(slug,section,paragraph))
                self.assertEqual(len(found),8)
            for lang in ('zh','zh-hant'):
                edition=record['languages'][lang]
                expected=list(edition['source_original_paragraphs'])
                for e in record['edits']:
                    if e['lang']!=lang:continue
                    offset=sum(record['paragraphs_by_section'][:e['section']-1])+e['paragraph']-1
                    self.assertEqual(expected[offset],e['before'])
                    expected[offset]=e['after']
                self.assertEqual(expected,[p for s in edition['sections'] for p in s['paragraphs']])

    def test_review_inputs_and_rebuild_are_current(self):
        for record in self.records.values():
            for name,value in record['review']['reports'].items():
                self.assertEqual(build.digest((build.DATA/'batches'/name).read_bytes()),value)
        outputs={}
        build.upgrade_outputs(outputs)
        for path,text in outputs.items():self.assertEqual(path.read_text(),text,str(path))


if __name__=='__main__':unittest.main()
