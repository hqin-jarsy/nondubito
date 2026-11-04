"""Fail-closed direct-source and reversible original-reader checks."""
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from full_series_languages import ROOT, original_article, profile, source_digest, upgrade_primary
from laughter_primary import strip_additions
from prepare_original_series_review import primary_main_hashes
from published_html_source import index_context


class LaughterSource(unittest.TestCase):
    def test_complete_current_source_and_all_apparatus(self):
        spec = profile('laughter')
        articles = [original_article('laughter', spec, s) for s in spec['slugs']]
        self.assertEqual([len(a['body_zh']) for a in articles], [52,34,38,43,60,83])
        self.assertEqual(sum(p.startswith('## ') for a in articles for p in a['body_zh']), 56)
        self.assertEqual([len(a['notes_zh']) for a in articles], [2,1,1,1,2,2])
        self.assertEqual([len(a['sources_zh']) for a in articles], [2]*6)
        self.assertEqual(len(index_context(spec)), 3)
        self.assertEqual(articles[-1]['source_url'], 'https://self-as-an-end.net/papers/sae-laughter-special.html')
        baseline = json.loads((ROOT/spec['primary_baseline']).read_text())
        self.assertEqual({s:source_digest('laughter',spec,s) for s in spec['slugs']}, baseline['source_data'])
        self.assertEqual(primary_main_hashes(spec), baseline['primary_main'])

    def test_control_additions_do_not_change_source_digest_but_prose_changes_do(self):
        spec = profile('laughter')
        self.assertEqual(spec['source_format'], 'legacy-html')
        baseline = json.loads((ROOT/spec['primary_baseline']).read_text())
        read_text = Path.read_text
        for slug in spec['slugs']:
            path = ROOT/spec['directory']/(slug+'.html')
            original = strip_additions(read_text(path))
            upgraded = upgrade_primary(original, 'laughter', slug)
            # The first existing p is original prose, outside both owned markers.
            changed = upgraded.replace('</p>', ' unauthorized prose edit</p>', 1)
            self.assertNotEqual(changed, upgraded)
            def supplied(value):
                def read(p, *args, **kwargs):
                    return value if p == path else read_text(p, *args, **kwargs)
                return read
            with self.subTest(slug=slug):
                with patch.object(Path, 'read_text', supplied(upgraded)):
                    self.assertEqual(source_digest('laughter', spec, slug), baseline['source_data'][slug])
                with patch.object(Path, 'read_text', supplied(changed)):
                    self.assertNotEqual(source_digest('laughter', spec, slug), baseline['source_data'][slug])

    def test_controls_are_reversible_idempotent_and_do_not_rewrite_primary(self):
        spec = profile('laughter')
        baseline = json.loads((ROOT/spec['primary_baseline']).read_text())
        for slug in ['index', *spec['slugs']]:
            path = ROOT/spec['directory']/(slug+'.html')
            original = strip_additions(path.read_text())
            self.assertEqual(hashlib.sha256(original.encode()).hexdigest(), baseline['primary_html'][str(path.relative_to(ROOT))])
            current = upgrade_primary(original, 'laughter', slug)
            self.assertEqual(strip_additions(current), original)
            self.assertEqual(upgrade_primary(current, 'laughter', slug), current)
            for language in spec['languages']:
                self.assertIn('href="'+language+'/'+slug+'.html"', current)
            self.assertEqual(current.count('cloudflareinsights.com/beacon.min.js'), 1)
        for name,digest in baseline['hant_dictionaries'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), digest)


if __name__ == '__main__': unittest.main()
