#!/usr/bin/env python3
"""Authenticate tracked historical evidence and test current B16 structures."""
import ast,os,subprocess,sys,tempfile,unittest
from pathlib import Path
import hongloumeng_b16_binding as binding
ROOT=Path(__file__).resolve().parents[1]
# Historical validators remain immutable evidence, not falsely replayed without
# their fourteen absent witnesses. Current B16 tests authenticate the complete tracked
# predecessor inventory and exercise the live current binding.
old=ROOT/'data/hongloumeng/first80-english/history/source-ch46-ch55-before/scripts/test_hongloumeng_english_pipeline.py'
text=old.read_text();tree=ast.parse(text);nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom)) or isinstance(n,ast.ClassDef) and n.name in ['PipelineTests','ClosingQuoteTests']]
selected='\n\n'.join(ast.get_source_segment(text,n) for n in nodes)
selected=selected.replace('586224','586250').replace('35513','35525').replace("'english-batch-041-045.json')","'english-batch-041-045.json', 'source-binding-ch46-ch55.json', 'source-binding-ch002-ending.json', 'english-batch-046-050.json', 'english-batch-051-055.json', 'source-binding-ch56-ch65.json', 'english-batch-056-060.json', 'english-binding-056-060.json', 'english-batch-061-065.json', 'english-binding-061-065.json', 'source-binding-ch66-ch80.json', 'english-batch-066-070.json', 'english-binding-066-070.json', 'english-batch-071-075.json', 'english-binding-071-075.json', 'english-batch-076-080.json', 'english-binding-076-080.json')").replace('self.assertEqual(len(names), 13)','self.assertEqual(len(names), 29)')
ns={'__name__':'b16_current_structure'};exec(compile(selected,'<B16 current structural tests>','exec'),ns)
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(ns[n]) for n in ['PipelineTests','ClosingQuoteTests'])
from test_hongloumeng_b16_binding import B16Tests
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(B16Tests))
result=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(0 if result.wasSuccessful() else 1)
