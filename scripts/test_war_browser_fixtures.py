#!/usr/bin/env python3
"""Fixture-only regressions. No browser or public-file writes."""
import sys
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
import prepare_war_browser_fixtures as fixtures

class FixtureTests(unittest.TestCase):
    def test_traditional_mapping_uses_whole_text_nodes(self):
        body = ['<p>A<strong>B</strong>C &amp; D</p>']
        mapping = {'A': '甲', 'B': '乙', 'C & D': '丙', 'ABC & D': 'WRONG', 'C': 'WRONG'}
        result = fixtures.body_record(body, mapping)
        self.assertEqual(result['units'], ['甲乙丙'])
        self.assertEqual(result['unit_tags'], ['p'])

    def test_tables_preserve_every_cell_and_span(self):
        body = ['<div class="table-scroll"><table><thead><tr><th>A</th><th>B</th></tr></thead><tbody><tr><td colspan="2"><strong>C</strong> D</td></tr></tbody></table></div>']
        result = fixtures.body_record(body)
        table = result['tables'][0]
        self.assertEqual(table['body_index'], 0)
        self.assertEqual([len(r) for r in table['rows']], [2, 1])
        self.assertEqual(table['rows'][1][0], {'text': 'C D', 'tag': 'td', 'colspan': 2, 'rowspan': 1})

    def test_release_gate_precedes_expectation_generation(self):
        with patch.object(fixtures.full, 'verify_reviews', side_effect=RuntimeError('release blocked')), patch.object(fixtures, 'article') as article:
            with self.assertRaisesRegex(RuntimeError, 'release blocked'):
                fixtures.generate(final=True)
            article.assert_not_called()

    def test_shape_only_cannot_write_a_final_fixture(self):
        with patch.object(sys, 'argv', ['fixtures', '--shape-only', '--output', '/tmp/must-not-be-written.json']), patch.object(fixtures, 'generate') as generate:
            with self.assertRaisesRegex(AssertionError, 'never writes'):
                fixtures.main()
            generate.assert_not_called()

    def test_ep05_head_quote_exception_is_narrow(self):
        code = r'''const assert = require('node:assert/strict');
const {headContainsPart: contains} = require('./scripts/test_war_full_browser.cjs');
assert.equal(contains('四个不得不 / Four Cannot-Nots｜战争论 — Non Dubito', '四个"不得不"', 'ep05', 0), true);
assert.equal(contains('四個不得不 / Four Cannot-Nots｜戰爭論 — Non Dubito', '四個"不得不"', 'ep05', 0), true);
assert.equal(contains('四个不得不 / Four Cannot-Nots', '四個"不得不"', 'ep05', 0), false);
assert.equal(contains('四個不得不 / Four Cannot-Nots', 'Four Cannot-Nots', 'ep05', 1), true);
assert.equal(contains('四個不得不 / Four Cannot Nots', 'Four Cannot-Nots', 'ep05', 1), false);
assert.equal(contains('A quoted title', 'A "quoted" title', 'ep06', 0), false);
assert.equal(contains('A quoted title', 'A "quoted" title', 'ep05', 1), false);
'''
        result = subprocess.run(['node', '-e', code], cwd=fixtures.ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_browser_capture_helpers_without_starting_browser(self):
        code = r'''const assert = require('node:assert/strict');
const {readControlLabel, isDedicatedFavicon, drainResponseJobs} = require('./scripts/test_war_full_browser.cjs');
(async () => {
  for (const label of ['Français', 'Deutsch', 'Español']) {
    assert.equal(await readControlLabel({textContent: async () => label, innerText() { throw Error('CSS-transformed innerText must not be used'); }}), label);
  }
  const base = 'http://127.0.0.1:8791';
  assert.equal(isDedicatedFavicon(base + '/favicon.svg', base), true);
  assert.equal(isDedicatedFavicon(base + '/style.css', base), false);
  assert.equal(isDedicatedFavicon('https://external.example/favicon.svg', base), false);
  assert.equal(isDedicatedFavicon(base + '/favicon.svg?different', base), false);
  const pending = new Set(), events = [];
  function track(job) { pending.add(job); job.finally(() => pending.delete(job)); }
  track(new Promise(resolve => setTimeout(() => {
    track(new Promise(done => setTimeout(() => {events.push('late body captured'); done();}, 10)));
    resolve();
  }, 5)));
  await drainResponseJobs(pending);
  assert.equal(pending.size, 0);
  assert.deepEqual(events, ['late body captured']);
})().catch(e => {console.error(e); process.exitCode = 1;});
'''
        result = subprocess.run(['node', '-e', code], cwd=fixtures.ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_real_effective_shapes_without_reading_public_html(self):
        read = Path.read_text
        public_reads = []
        def tracked(path, *args, **kwargs):
            if path.is_relative_to(fixtures.ROOT / 'essays/war') and path.suffix == '.html':
                public_reads.append(str(path))
            return read(path, *args, **kwargs)
        with patch.object(Path, 'read_text', tracked):
            result = fixtures.generate(final=False)
        self.assertEqual(public_reads, [])
        self.assertEqual(result['status'], 'shape_only_not_release_approved')
        self.assertEqual(fixtures.validate_shape(result)['viewport_combinations'], 408)
        self.assertFalse(result['derivation']['public_html_used_as_expectation'])
        head = result['pages']['zh-hant/ep06']['head_title_parts']
        self.assertEqual(head, ['勝利、失敗、均勢', 'Victory, Defeat, Balance of Power'])
        self.assertNotIn('Stalemate', ' '.join(head))

if __name__ == '__main__':
    unittest.main()
