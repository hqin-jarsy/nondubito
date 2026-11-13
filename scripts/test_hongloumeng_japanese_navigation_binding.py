"""Current navigation tests: exact reversible insertions and verified readers.

The hash-pinned navigation binding was retired on 2026-11-13 (see
data/hongloumeng/first80-english/binding-chain-retirement.json). Its record stays
as historical evidence and is no longer replayed.
"""
from pathlib import Path
import unittest
from unittest.mock import patch
import hongloumeng_japanese_navigation_binding as b
from integrate_hongloumeng_japanese import TARGETS, transform, reverse


class Navigation(unittest.TestCase):
    def test_exact_reversible_scope(self):
        self.assertEqual(len(TARGETS), 248)
        for name in TARGETS:
            raw = (b.ROOT/name).read_bytes()
            self.assertEqual(transform(name, reverse(name, raw)), raw)

    def test_navigation_change_rejected(self):
        name = 'classics/hongloumeng/ch001.html'
        raw = (b.ROOT/name).read_bytes().replace(b'/ja/ch001.html', b'/ja/ch002.html')
        with self.assertRaises(ValueError):
            reverse(name, raw)

    def test_added_marker_rejected(self):
        name = TARGETS[0]
        raw = (b.ROOT/name).read_bytes()
        with self.assertRaises(ValueError):
            reverse(name, raw+b'<!-- JAPANESE-NAV:START -->')

    def test_nonallowlisted_target_rejected(self):
        with self.assertRaises(ValueError):
            transform('data/private.html', b'<html></html>')

    def test_real_current_outputs(self):
        from hongloumeng_english_availability import english_publication
        from hongloumeng_japanese_availability import japanese_publication
        from build_hongloumeng_reading_japanese import PARTIAL
        self.assertEqual(len(english_publication()['paths']), 82)
        ja = japanese_publication()
        self.assertEqual((len(ja['paths']), ja['completeChapters'], ja['partialChapters'],
                          ja['ownerPlaceholders'], ja['literaryAcceptance']),
                         (82, 80-len(PARTIAL), len(PARTIAL), sum(PARTIAL.values()), False))

    def test_english_body_change_rejected(self):
        from hongloumeng_english_availability import english_publication
        read = Path.read_bytes
        target = b.ROOT/'classics/hongloumeng/en/ch001.html'
        def altered(path):
            raw = read(path)
            return raw.replace(b'</main>', b'changed</main>') if path == target else raw
        with patch.object(Path, 'read_bytes', altered):
            with self.assertRaisesRegex(ValueError, 'Stale English reader output'):
                english_publication()

    def test_missing_japanese_reader_rejected(self):
        exists = Path.exists
        def absent(path):
            return False if path == b.ROOT/'classics/hongloumeng/ja' else exists(path)
        with patch.object(Path, 'exists', absent):
            with self.assertRaisesRegex(ValueError, 'verified Japanese reader'):
                b.require_japanese_reader()

    def test_missing_japanese_article_rejected(self):
        read = Path.read_text
        def altered(path, *args, **kwargs):
            raw = read(path, *args, **kwargs)
            return raw.replace('<article>', '<div>') if path == b.ROOT/'classics/hongloumeng/ja/ch001.html' else raw
        with patch.object(Path, 'read_text', altered):
            with self.assertRaisesRegex(ValueError, 'article'):
                b.require_japanese_reader()

    def test_regeneration_preserves_first_publication_date(self):
        from refresh_hongloumeng_reading_discovery import english_launch_date, ENGLISH_UPDATE_ID
        ledger = {'updates': [{'id': ENGLISH_UPDATE_ID, 'date': '2026-11-12'}]}
        self.assertEqual(english_launch_date(ledger, {'date': '2026-11-13'}), '2026-11-12')
        self.assertEqual(ledger['updates'][0]['date'], '2026-11-12')

    def test_first_publication_uses_generation_date(self):
        from refresh_hongloumeng_reading_discovery import english_launch_date
        self.assertEqual(english_launch_date({'updates': []}, {'date': '2026-11-13'}), '2026-11-13')

    def test_four_language_discovery_identity(self):
        from hongloumeng_discovery_scope import excluded, excluded_url
        from build_content_registry import language_from_directory
        self.assertEqual(language_from_directory(Path('classics/hongloumeng/ja/ch001.html'), b.ROOT)[0], 'ja')
        for directory in ('', 'zh-hant/', 'en/', 'ja/'):
            self.assertFalse(excluded(Path('classics/hongloumeng/'+directory+'ch001.html'), root=b.ROOT, english=True))
        self.assertTrue(excluded_url('/classics/hongloumeng/ja/../../data/hongloumeng/first80/private.html', root=b.ROOT, english=True))
        self.assertTrue(excluded(Path('classics/hongloumeng/ja/private.json'), root=b.ROOT, english=True))


if __name__ == '__main__':
    unittest.main()
