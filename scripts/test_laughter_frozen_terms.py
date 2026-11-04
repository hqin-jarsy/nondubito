"""Narrow authorized term correction, not an audit of all laughter claims."""
import json
import re
import subprocess
import unittest

from prepare_action_sources import Document
from build_emperor_traditional import TextCollector
from full_series_languages import ROOT


class FrozenLaughterTerms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=json.loads((ROOT/'reports/laughter-frozen-definition-20261104.json').read_text())

    def original(self,path):
        # Fixed actual pre-correction commit, not a refreshed expected snapshot.
        return subprocess.check_output(['git','show','585bdc5:'+str(path.relative_to(ROOT))],cwd=ROOT,text=True)

    def test_only_authorized_prose_blocks_and_previews_changed(self):
        for slug in ('index','overview','ep04','ep05'):
            path=ROOT/'essays/laughter'/(slug+'.html')
            old=Document(self.original(path));new=Document(path.read_text())
            def blocks(doc):
                return [n.text() for n in doc.root.walk() if (n.tag in ('p','h1','h2','h3') or n.has('entry-desc')) and not n.has('laughter-definition-note')]
            expected=blocks(old)
            mapping={c['before']:c['after'] for c in self.report['changes'] if c['page']==slug}
            expected=[mapping.get(s,s) for s in expected]
            for i in self.report['metadata_followup']:
                if i['page']==slug:expected=[s.replace(i['before'],i['after']) for s in expected]
            self.assertEqual(blocks(new),expected,slug)
            self.assertEqual([(n.attrs.get('href'),n.attrs.get('target'),n.attrs.get('rel')) for n in new.root.walk() if n.tag=='a'],
                             [(n.attrs.get('href'),n.attrs.get('target'),n.attrs.get('rel')) for n in old.root.walk() if n.tag=='a'])
            notes=[n for n in new.root.walk() if n.has('laughter-definition-note')]
            self.assertEqual([n.text() for n in notes],[self.report['added_notes']['en'],self.report['added_notes']['zh']])

    def test_changed_chinese_text_and_added_notes_have_complete_offline_hant_keys(self):
        for slug in ('index','overview','ep04','ep05'):
            page=ROOT/'essays/laughter'/(slug+'.html');doc=Document(page.read_text())
            script=ROOT/'essays/laughter/zh-hant-data'/(slug+'.js')
            variants=json.loads(re.search(r'var variants = (.*);',script.read_text())[1])
            for change in self.report['changes']:
                if change['page']!=slug or change['language']!='zh':continue
                node=next(n for n in doc.root.walk() if n.tag=='p' and n.text()==change['after'])
                collect=TextCollector();collect.feed(doc.raw(node))
                translated=''.join(variants.get(s,s) for s in collect.text)
                self.assertTrue(translated)
                self.assertNotIn('瞬间',translated)
                self.assertNotIn('校准',translated)
                self.assertNotIn('这里',translated)
                for text in collect.text:
                    # Text fragments already all-Traditional can be unchanged.
                    self.assertTrue(text in variants or text in ('美学系列','的背面。'))
            note=variants[self.report['added_notes']['zh']]
            self.assertIn('所有事情',note)
            self.assertIn('校準',note)
            self.assertIn('連結',note)
            self.assertIn('15DD',note)
            self.assertIn('16DD',note)

    def test_unchanged_hant_keys_and_other_essays_stay_unchanged(self):
        for slug in ('index','overview','ep04','ep05'):
            path=ROOT/'essays/laughter/zh-hant-data'/(slug+'.js')
            old=json.loads(re.search(r'var variants = (.*);',self.original(path))[1])
            new=json.loads(re.search(r'var variants = (.*);',path.read_text())[1])
            for key in old.keys() & new.keys():self.assertEqual(old[key],new[key],(slug,key))
        for slug in ('ep01','ep02','ep03'):
            for path in (ROOT/'essays/laughter'/(slug+'.html'),ROOT/'essays/laughter/zh-hant-data'/(slug+'.js')):
                self.assertEqual(path.read_text(),self.original(path))

    def test_frozen_entry_definitions_and_three_reading_modes_remain(self):
        self.assertEqual(len(self.report['changes']),20)
        for entry in ('about.html','start.html'):
            self.assertEqual((ROOT/entry).read_text(),self.original(ROOT/entry))
        for slug in ('index','overview','ep04','ep05'):
            text=(ROOT/'essays/laughter'/(slug+'.html')).read_text()
            for mode in ('en','zh','zh-hant'):self.assertIn('data-lang="'+mode+'"',text)
            self.assertIn('across every matter',text)
            self.assertIn('两个主体各自的15DD瞬间',text)
            self.assertNotIn('That is 16DD, outside the scope.',text)
            self.assertNotIn('那是 16DD，在辖域之外。',text)
            self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1)


if __name__=='__main__':unittest.main()
