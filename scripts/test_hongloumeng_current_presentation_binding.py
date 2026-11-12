"""Current presentation successor tests; immutable B16 source remains historical.

Retarget only its binding import. Every B16 test method, mutation and assertion
is preserved exactly. Extra cases exercise the actual current wrapper/state.
"""
import ast
import json
import unittest
from pathlib import Path
from unittest.mock import patch
import hongloumeng_english_pipeline as pipeline
import hongloumeng_english_presentation_readiness as current
import hongloumeng_reading_presentation_binding as presentation

ORIGINAL = pipeline.ROOT/'scripts/test_hongloumeng_b16_binding.py'
SOURCE = ORIGINAL.read_text()
OLD_IMPORT = 'import hongloumeng_b16_binding as b'
NEW_IMPORT = 'import hongloumeng_english_presentation_readiness as b'
assert SOURCE.count(OLD_IMPORT) == 1
CURRENT_SOURCE = SOURCE.replace(OLD_IMPORT, NEW_IMPORT, 1)
old_tree, new_tree = ast.parse(SOURCE), ast.parse(CURRENT_SOURCE)
assert ast.dump(ast.parse(CURRENT_SOURCE.replace(NEW_IMPORT, OLD_IMPORT, 1))) == ast.dump(old_tree)
original_methods = {n.name: ast.dump(n) for c in old_tree.body if isinstance(c, ast.ClassDef) for n in c.body if isinstance(n, ast.FunctionDef)}
current_methods = {n.name: ast.dump(n) for c in new_tree.body if isinstance(c, ast.ClassDef) for n in c.body if isinstance(n, ast.FunctionDef)}
assert original_methods == current_methods
namespace = {'__name__': 'current_presentation_b16_cases', '__file__': str(ORIGINAL)}
exec(compile(CURRENT_SOURCE, str(ORIGINAL)+' [current binding import only]', 'exec'), namespace)
B16Tests = namespace['B16Tests']
assert unittest.defaultTestLoader.loadTestsFromTestCase(B16Tests).countTestCases() == 34

class CurrentWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = pipeline.source_map(pipeline.load_source())
        cls.progress = json.loads((pipeline.DATA/'progress.json').read_text())
    def run_current(self):
        return current.validate_readiness(pipeline, self.mapping, self.progress)
    def changed_bytes(self, target, value):
        original = Path.read_bytes
        return patch.object(Path, 'read_bytes', lambda path: value if path == target else original(path))
    def test_genuine_current_wrapper_and_generated_state(self):
        self.assertEqual(self.run_current(), pipeline.standard_snapshot())
        state = presentation.validate_state(pipeline.ROOT)
        self.assertEqual(state['state'], 'generated')
        self.assertFalse(state['publicationAuthorized'])
    def test_missing_genuine_review_rejected(self):
        target = pipeline.ROOT/presentation.REVIEW_PATH
        original = Path.read_bytes
        def read(path):
            if path == target: raise FileNotFoundError('Missing review negative fixture')
            return original(path)
        with patch.object(Path, 'read_bytes', read):
            with self.assertRaises(FileNotFoundError): self.run_current()
    def test_altered_genuine_review_rejected(self):
        target = pipeline.ROOT/presentation.REVIEW_PATH
        with self.changed_bytes(target, target.read_bytes()+b'\n'):
            with self.assertRaisesRegex(ValueError, '^Unpinned presentation review$'): self.run_current()
    def test_mixed_exact_predecessor_and_generated_state_rejected(self):
        relative = 'classics/hongloumeng/ch001.html'
        before = presentation.read_historical(pipeline.ROOT, relative)
        with self.changed_bytes(pipeline.ROOT/relative, before):
            with self.assertRaisesRegex(ValueError, 'Mixed'): self.run_current()
    def test_unknown_current_presentation_byte_rejected(self):
        relative = 'classics/hongloumeng/ch001.html'
        target = pipeline.ROOT/relative
        with self.changed_bytes(target, target.read_bytes()+b'\n'):
            with self.assertRaisesRegex(ValueError, 'Unapproved current presentation bytes'): self.run_current()
