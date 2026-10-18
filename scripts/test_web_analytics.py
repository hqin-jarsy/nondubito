import unittest
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from web_analytics import (TOKEN, SNIPPET, Document, ensure_analytics, issue,
                           public_page, tracked_html, conflict_copies)


class Analytics(unittest.TestCase):
    def test_insert_is_idempotent_and_does_not_change_copy(self):
        source = '<!doctype html><html><body><article>原文 &amp; text</article></body></html>\n'
        result = ensure_analytics(source)
        self.assertEqual(result.replace(SNIPPET, ''), source)
        self.assertEqual(ensure_analytics(result), result)
        self.assertIsNone(issue(Document(result)))

    def test_wrong_duplicate_and_commented_beacons(self):
        wrong = '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{"token":"wrong"}\'></script>'
        for tags in (wrong, wrong * 2):
            result = ensure_analytics('<html><body>copy' + tags + '</body></html>')
            self.assertEqual(len(Document(result).beacons), 1)
            self.assertIsNone(issue(Document(result)))
            self.assertIn('copy', result)
        source = '<html><body><!-- ' + wrong + ' --></body></html>'
        self.assertEqual(issue(Document(source)), 'missing')
        self.assertEqual(len(Document(ensure_analytics(source)).beacons), 1)

    def test_exclusions(self):
        for meta in ('<meta content="0;url=index.html" http-equiv="refresh">',
                     '<meta content="noindex" name="robots">',
                     '<link rel="canonical" href="https://example.org/">'):
            source = '<html><head>' + meta + '</head><body>copy</body></html>'
            self.assertFalse(public_page(Path('essays/a.html'), Document(source)))
            self.assertEqual(ensure_analytics(source), source)
        doc = Document('<html><body></body></html>')
        for name in ('data/a.html', 'prototypes/a.html', 'essays/a 2.html', '.git/a.html'):
            self.assertFalse(public_page(Path(name), doc))
        self.assertTrue(public_page(Path('search.html'), doc))

    def test_renderer_handles_mixed_outputs(self):
        @tracked_html
        def render():
            return {Path('essays/a.html'): '<html><body>copy</body></html>',
                    Path('data/a.html'): '<html><body>template</body></html>',
                    Path('essays/a.js'): 'console.log("copy")'}
        pages = render()
        self.assertIn(TOKEN, pages[Path('essays/a.html')])
        self.assertNotIn(TOKEN, pages[Path('data/a.html')])
        self.assertEqual(pages[Path('essays/a.js')], 'console.log("copy")')

    def test_conflict_copy_guard_does_not_scan_internal_archives(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('essays/a 2.html', 'originals/a 12.html', 'data/a 2.html', 'essays/a.html'):
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.touch()
            self.assertEqual({p.relative_to(root).as_posix() for p in conflict_copies(root)},
                             {'essays/a 2.html', 'originals/a 12.html'})

    def test_frozen_editorial_receipt_allows_only_the_recorded_script_addition(self):
        from web_analytics import ROOT
        receipt = json.loads((ROOT / 'data/daodejing-full/analytics-review-2026-10-18.json').read_text())
        for name, record in receipt['page_edits'].items():
            new = (ROOT / name).read_bytes()
            self.assertEqual(new.count(SNIPPET.encode()), 1)
            old = new.replace(SNIPPET.encode(), b'', 1)
            self.assertEqual(hashlib.sha256(old).hexdigest(), record['before_sha256'])
            self.assertEqual(hashlib.sha256(new).hexdigest(), record['after_sha256'])
            self.assertEqual(ensure_analytics(old.decode()).encode(), new)


if __name__ == '__main__':
    unittest.main()
