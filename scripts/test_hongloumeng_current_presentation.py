#!/usr/bin/env python3
"""Current generated-site suite; historical B16 entrypoints remain unchanged.

Run python3 -B scripts/test_hongloumeng_current_presentation.py --suite all.
Core retains all78 cases (44 structural +34 B16), extras add5 current-wrapper
negatives/positive, presentation retains9 cases, site retains54. The preserved
historical aggregate describes the B16 pre-presentation phase, not current HTML.
No runtime validator or production data is replaced by this test adapter.
"""
import argparse
import ast
import copy
import unittest
from pathlib import Path
import hongloumeng_english_pipeline as pipeline
from test_hongloumeng_current_presentation_binding import B16Tests, CurrentWrapperTests

ROOT = pipeline.ROOT
original = ROOT/'scripts/test_hongloumeng_english_pipeline.py'
aggregate = original.read_text()
# Reuse the exact original import/structural extraction and29-name transforms.
assert aggregate.count("ns={'__name__':'b16_current_structure'}") == 1
prefix = aggregate.split("ns={'__name__':'b16_current_structure'}", 1)[0]
setup = {'__file__': str(original), '__name__': 'current_structural_extraction'}
exec(compile(prefix, str(original)+' [unchanged extraction]', 'exec'), setup)
selected = setup['selected']
old = "with self.assertRaisesRegex(ValueError, 'Frozen Chinese source changed'):"
new = "with self.assertRaisesRegex(ValueError, 'Frozen Chinese source changed' if name == 'reading.zh.json' else 'Unknown current finalized manifest hash'):"
assert selected.count(old) == 1
adapted = selected.replace(old, new, 1)
# AST proof: exactly one assertion argument changes, in the identified method.
def methods(source):
    return {(c.name, n.name): n for c in ast.parse(source).body if isinstance(c, ast.ClassDef) for n in c.body if isinstance(n, ast.FunctionDef)}
a, b = methods(selected), methods(adapted)
assert a.keys() == b.keys()
changed = [k for k in a if ast.dump(a[k]) != ast.dump(b[k])]
assert changed == [('ClosingQuoteTests', 'test_modified_actual_source_or_manifest_rejected')]
assert ast.dump(ast.parse(adapted.replace(new, old, 1))) == ast.dump(ast.parse(selected))
ns = {'__name__': 'current_presentation_structural_cases'}
exec(compile(adapted, '<current structural tests: one exact message expectation>', 'exec'), ns)
structural = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(ns[n]) for n in ['PipelineTests','ClosingQuoteTests'])
assert structural.countTestCases() == 44

# Preserve all9 presentation tests; only directory regeneration changes phase.
presentation_path = ROOT/'scripts/test_hongloumeng_reading_presentation.py'
source = presentation_path.read_text()
old_method = ast.get_source_segment(source, methods(source)[('PresentationTests','test_directory_cleanup_regenerates_only_two_index_occurrences')])
new_method = '''def test_directory_cleanup_regenerates_only_two_index_occurrences(self):
        import hongloumeng_translations as translations
        import build_hongloumeng_original as original
        from web_analytics import ensure_analytics
        pages=translations.render_foreign(original.EDITIONS,original.language_menu,original.ORIGIN,original.TARGET)
        self.assertEqual(len(pages),36)
        for path,page in pages.items():
            self.assertEqual(path.read_text(),ensure_analytics(page),str(path))
        row=self.bound['continuationDirectoryDisplay']
        after=(self.root/row['path']).read_text()
        self.assertEqual(binding.sha(after.encode()),row['afterSHA256'])
        self.assertEqual(after.count('Jia Bao-yu'),2)
        before=after.replace('Jia Bao-yu','## Jia Bao-yu')
        self.assertEqual(binding.sha(before.encode()),row['beforeSHA256'])
        self.assertEqual(before.count('## Jia Bao-yu'),2)
        self.assertEqual(after,before.replace('## Jia Bao-yu','Jia Bao-yu'))'''
assert source.count(old_method) == 1
current_source = source.replace(old_method, new_method, 1)
pa,pb=methods(source),methods(current_source)
assert pa.keys()==pb.keys()
assert [k for k in pa if ast.dump(pa[k])!=ast.dump(pb[k])] == [('PresentationTests','test_directory_cleanup_regenerates_only_two_index_occurrences')]
assert ast.dump(ast.parse(current_source.replace(new_method,old_method,1)))==ast.dump(ast.parse(source))
pns={'__name__':'current_presentation_phase_cases','__file__':str(presentation_path)}
exec(compile(current_source,'<current presentation phase: exact directory expectation>','exec'),pns)

def suite(which):
    result=unittest.TestSuite()
    if which in ('core','all'):
        result.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(ns[n]) for n in ['PipelineTests','ClosingQuoteTests'])
        result.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(B16Tests))
    if which in ('extra','all'):result.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(CurrentWrapperTests))
    if which in ('presentation','all'):
        for n in ('PresentationTests','DiscoveryDateTests'):result.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(pns[n]))
    if which in ('site','all'):
        for name in ('test_hongloumeng_reading_english','test_hongloumeng_discovery_scope','test_hongloumeng_reading_discovery'):result.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--suite',choices=('core','extra','presentation','site','all'),default='all');args=parser.parse_args()
    current=suite(args.suite);expected={'core':78,'extra':5,'presentation':9,'site':54,'all':146}[args.suite]
    assert current.countTestCases()==expected
    print('AST parity PASS:34 B16 methods unchanged;44 structural cases with one exact conditional error argument;9 presentation cases with one exact directory-phase method;54 site cases unchanged.',flush=True)
    return 0 if unittest.TextTestRunner(verbosity=2).run(current).wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
