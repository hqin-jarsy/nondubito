#!/usr/bin/env python3
"""Keep full prior suites in authentic history; run current structural and amendment tests."""
import ast,os,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
H=ROOT/'data/hongloumeng/first80-english/history/ch002-ending-before'
r=subprocess.run([sys.executable,'-B',str(H/'scripts/test_hongloumeng_english_pipeline.py')],cwd=H,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
if r.returncode:sys.exit(r.returncode)
# The whole parent runner above retains all older v0.10 and source4655 guards.
# Current-source structure starts from the exact original pre-overlay test code.
old=H/'data/hongloumeng/first80-english/history/source-ch46-ch55-before/scripts/test_hongloumeng_english_pipeline.py'
text=old.read_text();tree=ast.parse(text)
nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom)) or isinstance(n,ast.ClassDef) and n.name in ['PipelineTests','ClosingQuoteTests']]
selected='\n\n'.join(ast.get_source_segment(text,n) for n in nodes)
selected=selected.replace('586224','586240').replace('35513','35525').replace("'english-batch-041-045.json')","'english-batch-041-045.json', 'source-binding-ch46-ch55.json', 'source-binding-ch002-ending.json')").replace('self.assertEqual(len(names), 13)','self.assertEqual(len(names), 15)')
ns={'__name__':'chapter2_current_structure'};exec(compile(selected,'<chapter2 current-source structural tests>','exec'),ns)
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(ns[n]) for n in ['PipelineTests','ClosingQuoteTests'])
from test_hongloumeng_ch002_ending_binding import Chapter2BindingTests
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(Chapter2BindingTests))
result=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(0 if result.wasSuccessful() else 1)
