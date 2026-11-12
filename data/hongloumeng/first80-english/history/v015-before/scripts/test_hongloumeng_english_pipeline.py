#!/usr/bin/env python3
"""Run finite authentic B13 regressions, then current source6680 structures."""
import ast,os,subprocess,sys,tempfile,unittest
from pathlib import Path
import hongloumeng_source6680_binding as binding
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='source6680-authentic-B13-') as td:
 root=binding.materialize_predecessor(ROOT,Path(td)/'root')
 for command in [['hongloumeng_english_pipeline.py','validate'],['test_hongloumeng_english_pipeline.py']]:
  result=subprocess.run([sys.executable,'-B',str(root/'scripts'/command[0]),*command[1:]],cwd=root,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  if result.returncode:sys.exit(result.returncode)
old=ROOT/'data/hongloumeng/first80-english/history/source-ch46-ch55-before/scripts/test_hongloumeng_english_pipeline.py'
text=old.read_text();tree=ast.parse(text);nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom)) or isinstance(n,ast.ClassDef) and n.name in ['PipelineTests','ClosingQuoteTests']]
selected='\n\n'.join(ast.get_source_segment(text,n) for n in nodes)
selected=selected.replace('586224','586250').replace('35513','35525').replace("'english-batch-041-045.json')","'english-batch-041-045.json', 'source-binding-ch46-ch55.json', 'source-binding-ch002-ending.json', 'english-batch-046-050.json', 'english-batch-051-055.json', 'source-binding-ch56-ch65.json', 'english-batch-056-060.json', 'english-binding-056-060.json', 'english-batch-061-065.json', 'english-binding-061-065.json', 'source-binding-ch66-ch80.json')").replace('self.assertEqual(len(names), 13)','self.assertEqual(len(names), 23)')
ns={'__name__':'b13_current_structure'};exec(compile(selected,'<B13 current structural tests>','exec'),ns)
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(ns[n]) for n in ['PipelineTests','ClosingQuoteTests'])
from test_hongloumeng_source6680_binding import Source6680Tests
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(Source6680Tests))
result=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(0 if result.wasSuccessful() else 1)
