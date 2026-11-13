#!/usr/bin/env python3
"""Small checks for the editable Japanese reader. Archived JSON is not an input."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit
from hongloumeng_japanese_availability import ROOT, PREFIX, NAMES, ReaderHTML, japanese_publication
import build_hongloumeng_reading_japanese as builder


class JapaneseReaderTests(unittest.TestCase):
    def test_current_inventory_and_placeholders(self):
        result = japanese_publication()
        self.assertEqual(len(result['paths']), 82)
        self.assertEqual(result['partial'], {})

    def test_local_links_and_fragments(self):
        base = ROOT/PREFIX
        for path in japanese_publication()['paths']:
            doc = ReaderHTML(path.read_text())
            for link in doc.links:
                u = urlsplit(link)
                if u.scheme or u.netloc:
                    continue
                target = ROOT/u.path.lstrip('/') if u.path.startswith('/') else base/(u.path or path.name)
                if target.is_dir():
                    target = target/'index.html'
                self.assertTrue(target.is_file(), f'{path.name}: {link}')
                if u.fragment:
                    self.assertIn(u.fragment, ReaderHTML(target.read_text()).ids)

    def test_continuation_return_link(self):
        raw = (ROOT/'originals/hongloumeng/ja/ch081.html').read_text()
        self.assertIn('/classics/hongloumeng/ja/ch080.html', raw)

    def test_no_internal_fields(self):
        for path in japanese_publication()['paths']:
            raw = path.read_text()
            for word in ('sourceText', 'sourceSha256', 'sourceSegments', 'private-review', '/Users/'):
                self.assertNotIn(word, raw)
            self.assertIn('大知校訂庚辰本', raw)

    def test_hand_edit_survives_old_build_command_and_discovery_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root/PREFIX
            shutil.copytree(ROOT/PREFIX, target)
            chapter = target/'ch001.html'
            chapter.write_text(chapter.read_text().replace('<article>', '<article>\n<p>編集の保存テスト。</p>', 1))
            before = {name: (target/name).read_bytes() for name in NAMES}
            # No data/ directory exists here. Publication cannot depend on JSON.
            with patch.object(builder, 'ROOT', root), patch('sys.argv', ['builder']):
                builder.main()
            self.assertEqual(japanese_publication(root)['completeChapters'], 80)
            self.assertEqual(before, {name: (target/name).read_bytes() for name in NAMES})
            with patch.object(builder, 'ROOT', root), patch('sys.argv', ['builder', '--check']):
                builder.main()
            self.assertEqual(before, {name: (target/name).read_bytes() for name in NAMES})

    def test_missing_article_and_language_link_rejected(self):
        read = Path.read_text
        for old, new in [('<article>', '<div>'), ('/en/ch001.html', '/en/ch999.html')]:
            def altered(path, *args, **kwargs):
                raw = read(path, *args, **kwargs)
                return raw.replace(old, new) if path == ROOT/PREFIX/'ch001.html' else raw
            with patch.object(Path, 'read_text', altered), self.assertRaises(ValueError):
                japanese_publication()

    def test_search_uses_edited_html(self):
        from build_content_registry import language_from_directory
        from hongloumeng_discovery_scope import excluded
        path = ROOT/PREFIX/'ch001.html'
        self.assertEqual(language_from_directory(path, ROOT)[0], 'ja')
        self.assertFalse(excluded(path, root=ROOT, english=True))
        from refresh_hongloumeng_reading_discovery import search_records
        # Search is title/heading/description search, not full-text search.
        source = path.read_text().replace('<h1>', '<h1>編集した回目 ', 1)
        records = search_records(ROOT, {path: source})['ja']
        self.assertEqual(len(records), 1)
        self.assertIn('編集した回目', records[0]['q'])


if __name__ == '__main__':
    unittest.main()
