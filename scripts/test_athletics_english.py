"""Verify real approved complete English batches and their eight-language fixes."""
import copy
import json
import re
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from athletics_english import DATA,ROOT,SERIES,body_inner,outputs,read_manuscript,section_counts,sha,validate_review
from test_companion_languages import Parsed,Node,plain_markdown


class AthleticsEnglish(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.publication=json.loads((DATA/'publication.json').read_text())
        cls.pages=outputs()

    def test_every_approved_body_is_full_and_saved(self):
        for ep,record in self.publication['articles'].items():
            r,md=read_manuscript(ep);path=SERIES/(ep+'.html')
            self.assertEqual(path.read_text(),self.pages[path])
            self.assertEqual(section_counts(md),r['paragraphs_by_section'])
            node=Parsed(body_inner(path.read_text(),'en')).nodes('div','athletics-english')[0]
            paras=[n.text() for n in node.walk() if n.tag=='p']
            expected=[]
            for body in re.split(r'^## (.+)\n',md,flags=re.M)[2::2]:
                expected.extend(plain_markdown(p) for p in re.split(r'\n\s*\n',body.strip()))
            self.assertEqual(paras,expected)
            self.assertEqual(len(paras),sum(r['paragraphs_by_section']))
            self.assertNotIn('Translation notes for author review',node.text())
            self.assertNotRegex(node.text(),r'\[\d+\]')

    def test_original_readings_and_all_saved_corrections_remain_bound(self):
        legacy=json.loads((ROOT/'data/athletics-full/review.json').read_text())
        for correction in legacy['source_corrections']:
            for edit in correction.get('edits',[]):
                if edit.get('review_report'):
                    self.assertEqual(sha((ROOT/edit['review_report']).read_bytes()),edit['review_report_sha256'])
        for name in {r['review_report'] for r in self.publication['articles'].values()}:
            review=validate_review(ROOT/name)
            self.assertEqual(set(review['articles']),set(review['episodes']))
            for ep,record in review['articles'].items():
                source=subprocess.check_output(['git','show',review['baseline_commit']+':essays/athletics/'+ep+'.html'],cwd=ROOT)
                self.assertEqual(sha(source),record['reading_source_sha256'])

    def test_same_shape_unreviewed_english_cannot_be_rendered(self):
        ep=next(iter(self.publication['articles']));target=DATA/(ep+'.md');read_text=Path.read_text
        def changed(path,*args,**kwargs):
            raw=read_text(path,*args,**kwargs)
            if path==target:raw=raw.replace('the','tHe',1)
            return raw
        with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):outputs()

    def test_same_shape_unreviewed_native_correction_is_rejected(self):
        review=json.loads((ROOT/next(iter(self.publication['articles'].values()))['review_report']).read_text())
        plan=json.loads((ROOT/review['copyedit_plan']).read_text());e=next(e for e in plan['edits'] if e['language']=='fr')
        target=ROOT/'data/athletics-full'/(e['episode']+'.fr.md');read_text=Path.read_text
        def changed(path,*args,**kwargs):
            raw=read_text(path,*args,**kwargs)
            return raw.replace(e['after'],e['after']+'!',1) if path==target else raw
        with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):validate_review(ROOT/next(iter(self.publication['articles'].values()))['review_report'])

    def test_controls_toc_no_duplicate_ids_and_one_beacon(self):
        for path,text in self.pages.items():
            page=Parsed(text);ids=[n.attrs['id'] for n in page.root.walk() if n.attrs.get('id')]
            self.assertEqual(len(ids),len(set(ids)))
            toc=page.nodes('details','athletics-english-toc')[0]
            for a in toc.walk():
                if a.tag=='a':self.assertIn(a.attrs['href'][1:],ids)
            self.assertEqual(len(page.nodes('div','lang-toggle')[0].children),15)
            self.assertEqual(text.count('cloudflareinsights.com/beacon.min.js'),1)
            self.assertEqual(text.count('src="athletics-language.js"'),1)
            self.assertEqual(text.count('src="../../language-select.js"'),1)

    def test_unreviewed_summary_drift_is_rejected(self):
        name=next((r['review_report'] for r in self.publication['articles'].values()
                   if json.loads((ROOT/r['review_report']).read_text()).get('surface_reading_report_sha256')),None)
        if not name:self.skipTest('No summary-edit batch approved yet')
        review=json.loads((ROOT/name).read_text())
        proof=json.loads((ROOT/next(iter(review['surface_reading_report_sha256']))).read_text())
        field=next(f for f in proof['fields'] if 'source_key' not in f)
        target=ROOT/field['path'];read_text=Path.read_text
        def changed(path,*args,**kwargs):
            raw=read_text(path,*args,**kwargs)
            return raw.replace(field['saved_field'],field['saved_field']+'!',1) if path==target else raw
        with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):validate_review(ROOT/name)

    def test_unreviewed_traditional_field_drift_is_rejected(self):
        name=next(iter(self.publication['articles'].values()))['review_report']
        review=json.loads((ROOT/name).read_text())
        plan=json.loads((ROOT/review['copyedit_plan']).read_text())
        edit=next(e for e in plan['edits'] if e['language']=='zh')
        target=SERIES/'zh-hant-data'/(edit['episode']+'.js');read_text=Path.read_text
        from athletics_english import saved_value
        value=saved_value(edit,'zh-hant')
        def changed(path,*args,**kwargs):
            raw=read_text(path,*args,**kwargs)
            return raw.replace(value,value+'!',1) if path==target else raw
        with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):validate_review(ROOT/name)

    def test_failed_reading_requires_explicit_bound_resolution(self):
        name=next((r['review_report'] for r in self.publication['articles'].values()
                   if json.loads((ROOT/r['review_report']).read_text()).get('resolved_saved_readings')),None)
        if not name:self.skipTest('No resolved failed reading in approved batches')
        target=ROOT/name;read_text=Path.read_text
        def changed(path,*args,**kwargs):
            raw=read_text(path,*args,**kwargs)
            if path==target:
                data=json.loads(raw);data.pop('resolved_saved_readings');raw=json.dumps(data)
            return raw
        with patch.object(Path,'read_text',changed),self.assertRaises(AssertionError):validate_review(target)

    def test_unpublished_english_and_urls_are_not_silently_replaced(self):
        base=self.publication['initial_baseline_commit']
        for i in range(1,24):
            ep=f'ep{i:02}';path=SERIES/(ep+'.html');text=path.read_text()
            old=subprocess.check_output(['git','show',base+':essays/athletics/'+ep+'.html'],cwd=ROOT,text=True)
            self.assertEqual(re.search(r'<link rel="canonical"[^>]*>',text)[0],re.search(r'<link rel="canonical"[^>]*>',old)[0])
            if ep not in self.publication['articles']:self.assertEqual(body_inner(text,'en'),body_inner(old,'en'))


if __name__=='__main__':unittest.main()
