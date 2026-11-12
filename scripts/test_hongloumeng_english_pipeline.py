#!/usr/bin/env python3
"""Run all original v0.10 guards in their immutable old context, plus new-source tests."""
import ast,os,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
H=ROOT/'data/hongloumeng/first80-english/history/source-ch46-ch55-before'
# This is the unchanged original full suite, not a copied selection or mocks.
r=subprocess.run([sys.executable,'-B',str(H/'scripts/test_hongloumeng_english_pipeline.py')],cwd=H,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
if r.returncode:sys.exit(r.returncode)
# Re-run every structural/current-source and standalone-quote test with the new
# source. Only the documented total and the appended normative input differ.
text=(H/'scripts/test_hongloumeng_english_pipeline.py').read_text()
tree=ast.parse(text);nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom)) or isinstance(n,ast.ClassDef) and n.name in ['PipelineTests','ClosingQuoteTests']]
selected='\n\n'.join(ast.get_source_segment(text,n) for n in nodes)
selected=selected.replace('586224','586228').replace("'english-batch-041-045.json')", "'english-batch-041-045.json', 'source-binding-ch46-ch55.json')").replace('self.assertEqual(len(names), 13)','self.assertEqual(len(names), 14)')
ns={'__name__':'source4655_current_structural_tests'};exec(compile(selected,'<current-source structural tests>','exec'),ns)
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(ns[n]) for n in ['PipelineTests','ClosingQuoteTests'])
from test_hongloumeng_source4655_binding import SourceBindingTests
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(SourceBindingTests))
result=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(0 if result.wasSuccessful() else 1)
