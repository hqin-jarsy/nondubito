#!/usr/bin/env python3
"""Run all original B10 tests in exact B10 context, then B11 current tests."""
import ast,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
H=ROOT/'data/hongloumeng/first80-english/history/v012-before'
def materialize_b10(root):
 # Only the authenticated historical runtime is needed, never the whole repo.
 # Read each source through the existing traversal/symlink/hardlink guard before
 # constructing its destination. A TMPDIR under ROOT cannot enter this inventory.
 from hongloumeng_b11_binding import authenticate_history
 from hongloumeng_source4655_binding import regular,sha,require
 history,manifest=authenticate_history(ROOT)
 root=Path(root).resolve();require(not root.exists(),'B10 test destination already exists')
 root.mkdir()
 names=set(manifest['unchangedRootFiles'])|set(manifest['files'])
 for rel in sorted(names):
  archived=rel in manifest['files'];base=history if archived else ROOT
  digest=manifest['files' if archived else 'unchangedRootFiles'][rel]
  payload=regular(base,rel);require(sha(payload)==digest,'B10 test input changed: '+rel)
  target=root/rel;require(root in target.parents,'B10 test output escapes root')
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
  target.chmod((base/rel).stat().st_mode&0o777)
 return names

# Temporary output may live under ROOT; only the finite manifest is copied.
with tempfile.TemporaryDirectory(prefix='b11-original-b10-tests-') as td:
 root=Path(td)/'root';materialize_b10(root)
 result=subprocess.run([sys.executable,'-B',str(root/'scripts/test_hongloumeng_english_pipeline.py')],cwd=root,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 if result.returncode:sys.exit(result.returncode)
old=ROOT/'data/hongloumeng/first80-english/history/source-ch46-ch55-before/scripts/test_hongloumeng_english_pipeline.py'
text=old.read_text();tree=ast.parse(text);nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom)) or isinstance(n,ast.ClassDef) and n.name in ['PipelineTests','ClosingQuoteTests']]
selected='\n\n'.join(ast.get_source_segment(text,n) for n in nodes)
selected=selected.replace('586224','586240').replace('35513','35525').replace("'english-batch-041-045.json')","'english-batch-041-045.json', 'source-binding-ch46-ch55.json', 'source-binding-ch002-ending.json', 'english-batch-046-050.json', 'english-batch-051-055.json')").replace('self.assertEqual(len(names), 13)','self.assertEqual(len(names), 17)')
ns={'__name__':'b11_current_structure'};exec(compile(selected,'<B11 current-source structural tests>','exec'),ns)
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(ns[n]) for n in ['PipelineTests','ClosingQuoteTests'])
from test_hongloumeng_b11_binding import B11BindingTests
suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(B11BindingTests))
result=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(0 if result.wasSuccessful() else 1)
