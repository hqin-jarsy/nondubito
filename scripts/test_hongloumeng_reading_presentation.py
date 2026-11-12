"""Real accepted B16 input checks and isolated presentation-state tests.

No first80 English production pages, approval markers or receipts are created.
"""
import ast
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import hongloumeng_english_pipeline as pipeline
import hongloumeng_english_presentation_readiness as successor
import hongloumeng_reading_presentation_binding as binding
import build_hongloumeng_reading_english as english

class PresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=pipeline.ROOT
        cls.bound=binding.binding(cls.root)
        cls.mapping=pipeline.source_map(pipeline.load_source())
        cls.progress=json.loads((pipeline.DATA/'progress.json').read_text())
        cls.notes=json.loads((pipeline.DATA/'reader-notes.json').read_text())
        cls.snapshot=successor.validate_b16_readiness(pipeline,cls.mapping,cls.progress)
    def test_current_state_is_explicit_and_not_publication_authority(self):
        state=binding.validate_state(self.root)
        self.assertIn(state['state'],('prepared','generated'))
        self.assertFalse(state['publicationAuthorized'])
        self.assertFalse(state['sourceMapBytesChanged'])

    def test_original_b16_check_functions_preserved(self):
        old=ast.parse((self.root/'scripts/hongloumeng_b16_binding.py').read_text())
        new=ast.parse((self.root/'scripts/hongloumeng_english_presentation_readiness.py').read_text())
        funcs={n.name:n for n in new.body if isinstance(n,ast.FunctionDef)}
        for node in old.body:
            if not isinstance(node,ast.FunctionDef):continue
            other=copy.deepcopy(funcs['validate_b16_readiness' if node.name=='validate_readiness' else node.name])
            other.name=node.name
            self.assertEqual(ast.dump(node,include_attributes=False),ast.dump(other,include_attributes=False),node.name)
    def test_real_complete_accepted_input_and_projection(self):
        self.assertEqual(pipeline.validate_progress(self.mapping,self.progress,self.snapshot),{'accepted':4475})
        self.assertEqual(pipeline.validate_reader_notes(self.mapping,self.notes),80)
        english.require_complete(self.mapping,self.progress)
        chapters=english.project(self.mapping,self.progress,self.notes,range(1,81))
        self.assertEqual(len(chapters),80)
        projected_notes={c['titleNote']['unitId'] for c in chapters if c.get('titleNote')}
        self.assertTrue({'hlm-c027-title','hlm-c046-title','hlm-c079-title'}<=projected_notes)
        projected_notes.update(b['noteUnitId'] for c in chapters for b in c['blocks'] if 'note' in b)
        self.assertEqual(projected_notes,{n['unitId'] for n in self.notes['notes']})
        self.assertEqual(sum(len(u['segments']) for u in self.progress['units']),14035)
        for c in chapters:
            expected=[s['text'] for source,u in zip(self.mapping['units'],self.progress['units']) if source['chapter']==c['number'] and source['index'] for s in u['segments']]
            self.assertEqual([b['text'] for b in c['blocks']],expected)
    def test_exact_historical_inverses_and_tamper_negatives(self):
        for relative,row in self.bound['changedRootWitnesses'].items():
            before=binding.read_historical(self.root,relative)
            self.assertEqual(binding.sha(before),row['beforeSHA256'])
            if row['kind']=='html':
                after=before.decode()
                after=after.replace('<link rel="alternate" hreflang="x-default"',row['insertions'][0]+'<link rel="alternate" hreflang="x-default"',1)
                marker='<nav class="language-switch" aria-label="Languages">';i=after.index('</nav>',after.index(marker))
                after=(after[:i]+row['insertions'][1]+after[i:]).encode()
            elif row['kind']=='status':after=before.replace(b'"status": "draft"',b'"status": "finalized"',1)
            else:after=(self.root/relative).read_bytes()
            self.assertEqual(binding.historical_bytes(self.root,relative,after,row),before)
            with self.assertRaises(ValueError):binding.historical_bytes(self.root,relative,after+b'\n',row)
            if row['kind']=='html':
                for insertion in row['insertions']:
                    with self.assertRaises(ValueError):binding.historical_bytes(self.root,relative,after.replace(insertion.encode(),b'',1),row)
                    with self.assertRaises(ValueError):binding.historical_bytes(self.root,relative,after.replace(insertion.encode(),insertion.encode()*2,1),row)
    def test_missing_review_does_not_authorize_generation(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises((ValueError,OSError)):binding.require_review(Path(t).resolve())
        with self.assertRaises(ValueError):english.production_plan({'publicationDate':'2026-11-12'})
    def test_directory_cleanup_regenerates_only_two_index_occurrences(self):
        import hongloumeng_translations as translations
        import build_hongloumeng_original as original
        from web_analytics import ensure_analytics
        pages=translations.render_foreign(original.EDITIONS,original.language_menu,original.ORIGIN,original.TARGET)
        changed=[]
        for path,page in pages.items():
            before=path.read_text();after=ensure_analytics(page)
            if before!=after:
                changed.append(path.relative_to(self.root).as_posix())
                self.assertEqual(before.count('## Jia Bao-yu'),2)
                self.assertEqual(after,before.replace('## Jia Bao-yu','Jia Bao-yu'))
        self.assertEqual(changed,['originals/hongloumeng/en/index.html'])
        self.assertEqual(len(pages),36)
    def test_public_retrospective_exact_and_no_private_paths(self):
        for relative,digest in self.bound['publicRetrospectiveHashes'].items():
            raw=(self.root/relative).read_bytes();self.assertEqual(binding.sha(raw),digest)
            text=raw.decode()
            for private in ('/Users/','first80/qa/','verification.private','/agent_notes/'):
                self.assertNotIn(private,text)
    def test_generated_status_fixture_retains_genuine_b16_checks(self):
        # Copy tracked-only candidate, apply only already-proved Chinese/status
        # deltas to this temporary fixture. No first80 English pages or approvals.
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve()/'root';shutil.copytree(self.root,root)
            for relative,row in self.bound['changedRootWitnesses'].items():
                if row['kind']=='script':continue
                path=root/relative;before=binding.read_historical(root,relative)
                if row['kind']=='status':after=before.replace(b'"status": "draft"',b'"status": "finalized"',1)
                else:
                    after=before.decode();after=after.replace('<link rel="alternate" hreflang="x-default"',row['insertions'][0]+'<link rel="alternate" hreflang="x-default"',1)
                    i=after.index('</nav>',after.index('<nav class="language-switch" aria-label="Languages">'))
                    after=(after[:i]+row['insertions'][1]+after[i:]).encode()
                self.assertEqual(binding.sha(after),row['afterSHA256']);path.write_bytes(after)
            row=self.bound['continuationDirectoryDisplay'];path=root/row['path'];path.write_text(path.read_text().replace('## Jia Bao-yu','Jia Bao-yu'))
            self.assertEqual(binding.validate_state(root)['state'],'generated')
            code='import json;import hongloumeng_english_pipeline as p;import hongloumeng_english_presentation_readiness as s;m=p.source_map(p.load_source());x=json.loads((p.DATA/"progress.json").read_text());assert s.validate_b16_readiness(p,m,x)==p.standard_snapshot();assert p.validate_progress(m,x,p.standard_snapshot())=={"accepted":4475};print("PASS_ACTUAL_B16_CHECKS_IN_STATUS_FIXTURE")'
            import os
            env=dict(os.environ,PYTHONPATH=str(root/'scripts'),PYTHONDONTWRITEBYTECODE='1')
            result=subprocess.run([sys.executable,'-B','-c',code],cwd=root,env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('PASS_ACTUAL_B16_CHECKS',result.stdout)
            normative=root/'docs/hongloumeng/translation/english-standard.md'
            normative.write_bytes(normative.read_bytes()+b'\n')
            denied=subprocess.run([sys.executable,'-B','-c',code],cwd=root,env=env,capture_output=True,text=True)
            self.assertNotEqual(denied.returncode,0)
            self.assertIn('changed',denied.stderr)
            # Stale/mixed metadata and unrelated corpus changes still fail closed.
            path=root/'classics/hongloumeng/ch001.html';path.write_bytes(binding.read_historical(root,'classics/hongloumeng/ch001.html'))
            with self.assertRaisesRegex(ValueError,'Mixed'):binding.validate_state(root)

class DiscoveryDateTests(unittest.TestCase):
    def test_exact_display_date_inventory_and_unrelated_dates(self):
        from test_hongloumeng_reading_discovery import ReadingDiscoveryTests
        import refresh_hongloumeng_reading_discovery as refresh
        import xml.etree.ElementTree as ET
        fixture=ReadingDiscoveryTests();fixture.setUp()
        try:
            fixture.test_complete_scoped_plan_roundtrips_in_temp_tree(bilingual=True)
            root=fixture.root
            changed=('classics/hongloumeng/ch001.html','originals/hongloumeng/en/index.html')
            sources={root/p:(root/p).read_text() for p in changed}
            context={'date':'2026-11-12','modifiedPaths':changed}
            outputs=refresh.discovery_outputs(root,sources,'2026-11-10',english=context)
            ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
            def entries(raw):return {u.findtext(ns+'loc'):u.findtext(ns+'lastmod') for u in ET.fromstring(raw)}
            old=entries((root/'sitemap.xml').read_text());new=entries(outputs[root/'sitemap.xml'])
            urls={refresh.ORIGIN+'classics/hongloumeng/ch001.html',refresh.ORIGIN+'originals/hongloumeng/en/'}
            self.assertEqual({u:d for u,d in new.items() if u not in urls},{u:d for u,d in old.items() if u not in urls})
            for url in urls:self.assertEqual(new[url],'2026-11-12')
            for path,value in outputs.items():path.write_text(value)
            again=refresh.discovery_outputs(root,sources,'2026-11-10',english=context)
            self.assertTrue(all(path.read_text()==value for path,value in again.items()))
            with self.assertRaisesRegex(ValueError,'modified presentation date scope'):
                refresh.discovery_outputs(root,sources,'2026-11-10',english={'date':'2026-11-12','modifiedPaths':('originals/hongloumeng/en/ch082.html',)})
        finally:fixture.doCleanups()

if __name__=='__main__':unittest.main()
