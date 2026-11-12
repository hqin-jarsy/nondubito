#!/usr/bin/env python3
"""Keep genuine source/Felicity history tests, then current structure and B10 delta."""
import ast,os,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
H=ROOT/'data/hongloumeng/first80-english/history/ch002-ending-before'
# Exact original v0.10 (including Felicity/B9) and source4655 test contexts.
r=subprocess.run([sys.executable,'-B',str(H/'scripts/test_hongloumeng_english_pipeline.py')],cwd=H,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
if r.returncode:sys.exit(r.returncode)
# Every inherited structural and closing-quote test, with only current source
# totals and the three added normative inputs updated. No test is deleted.
old=H/'data/hongloumeng/first80-english/history/source-ch46-ch55-before/scripts/test_hongloumeng_english_pipeline.py'
text=old.read_text();tree=ast.parse(text)
nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom)) or isinstance(n,ast.ClassDef) and n.name in ['PipelineTests','ClosingQuoteTests']]
selected='\n\n'.join(ast.get_source_segment(text,n) for n in nodes)
selected=selected.replace('586224','586240').replace('35513','35525').replace("'english-batch-041-045.json')","'english-batch-041-045.json', 'source-binding-ch46-ch55.json', 'source-binding-ch002-ending.json', 'english-batch-046-050.json')").replace('self.assertEqual(len(names), 13)','self.assertEqual(len(names), 16)')
ns={'__name__':'b10_current_structure'};exec(compile(selected,'<B10 current-source structural tests>','exec'),ns)
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(ns[n]) for n in ['PipelineTests','ClosingQuoteTests'])
from test_hongloumeng_b10_binding import B10BindingTests
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(B10BindingTests))
result=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(0 if result.wasSuccessful() else 1)
