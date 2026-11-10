"""Public collectors must never read private review HTML, even without noindex."""
from contextlib import ExitStack, redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build_content_registry as registry
import build_search_index as search
import build_sitemap as sitemap
import normalize_canonicals as canonicals
from hongloumeng_discovery_scope import PUBLIC_HTML, excluded, excluded_file, excluded_url


class DiscoveryScopeTests(unittest.TestCase):
    def test_exact_public_html_names(self):
        self.assertEqual(len(PUBLIC_HTML), 82)
        for name in PUBLIC_HTML:
            self.assertFalse(excluded(Path('classics/hongloumeng')/name))
        for name in ('review.html', 'ch000.html', 'ch081.html', 'ch001 2.html',
                     'en/ch001.html', 'backup/index.html', 'fonts/private.html'):
            self.assertTrue(excluded(Path('classics/hongloumeng')/name))
        self.assertTrue(excluded(Path('data/hongloumeng/first80/report.html')))
        self.assertTrue(excluded(Path('data/hongloumeng/first80/public-preview/index.html')))
        self.assertFalse(excluded(Path('essays/another-series/index.html')))

    def fixture(self, root):
        paths = ['index.html', 'classics/hongloumeng/ch001.html',
                 'data/hongloumeng/first80/secret.html',
                 'data/hongloumeng/first80/public-preview/index.html',
                 'classics/hongloumeng/review.html']
        for relative in paths:
            path = root/relative
            path.parent.mkdir(parents=True, exist_ok=True)
            canonical = 'https://nondubito.net/'+('' if relative == 'index.html' else relative)
            path.write_text(f'<html lang="zh-Hans"><head><title>Public fixture</title><meta name="description" content="Fixture"><link rel="canonical" href="{canonical}"></head><body><h1>Public fixture</h1></body></html>')
        return {root/relative for relative in paths if excluded(Path(relative))}

    def test_collectors_never_read_private_decoys(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            forbidden = self.fixture(root)
            original_read = Path.read_text
            def guarded_read(path, *args, **kwargs):
                if path in forbidden:
                    self.fail(f'Collector read a private decoy: {path}')
                return original_read(path, *args, **kwargs)
            with ExitStack() as stack:
                for module in (search, sitemap, canonicals):
                    stack.enter_context(patch.object(module, 'ROOT', root))
                stack.enter_context(patch.object(Path, 'read_text', guarded_read))
                stack.enter_context(patch.object(sitemap, 'git_dates', return_value=({}, set())))
                stack.enter_context(patch.object(sitemap, 'recorded_dates', return_value={}))
                self.assertEqual(set(search.collect_pages()), {root/'index.html', root/'classics/hongloumeng/ch001.html'})
                manifest, chunks = search.build()
                self.assertEqual(manifest['record_count'], 2)
                self.assertEqual({record['u'] for record in chunks['zh-Hans']}, {'index.html', 'classics/hongloumeng/ch001.html'})
                result, errors, _ = sitemap.build()
                self.assertEqual(errors, [])
                self.assertEqual(result.count('<url>'), 2)
                self.assertNotIn('first80/', result)
                self.assertNotIn('review.html', result)

    def test_canonical_cannot_force_private_target_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            forbidden = self.fixture(root)
            path = root/'index.html'
            path.write_text('<html lang="en"><head><title>Bad pointer</title><meta name="description" content="Fixture"><link rel="canonical" href="https://nondubito.net/data/hongloumeng/first80/secret.html"></head></html>')
            original = sitemap.parse_page
            def guarded_parse(path):
                self.assertNotIn(path, forbidden)
                return original(path)
            with ExitStack() as stack:
                for module in (sitemap, canonicals):
                    stack.enter_context(patch.object(module, 'ROOT', root))
                stack.enter_context(patch.object(sitemap, 'parse_page', guarded_parse))
                stack.enter_context(patch.object(sitemap, 'git_dates', return_value=({}, set())))
                stack.enter_context(patch.object(sitemap, 'recorded_dates', return_value={}))
                result, errors, _ = sitemap.build()
                self.assertEqual(len(errors), 1)
                self.assertIn('outside the public reading allowlist', errors[0])
                self.assertNotIn('first80/', result)

    def test_only_the_exact_existing_continuation_chapters_change_type(self):
        root = Path(__file__).resolve().parents[1]
        editions = ('', 'en/', 'zh-hant/', 'de/', 'fr/', 'es/', 'ja/', 'ko/')
        paths = [Path('originals/hongloumeng')/f'{edition}ch{number:03d}.html'
                 for edition in editions for number in range(81, 86)]
        self.assertEqual(len(paths), 40)
        for relative in paths:
            self.assertTrue((root/relative).is_file(), str(relative))
            self.assertEqual(registry.infer_record_type(relative), 'novel-chapter')
            self.assertIn(registry.infer_sequence(relative), range(81, 86))
        for relative in ('originals/hongloumeng/ch080.html', 'originals/hongloumeng/ch086.html',
                         'originals/hongloumeng/it/ch081.html', 'originals/other/ch081.html'):
            self.assertEqual(registry.infer_record_type(Path(relative)), 'story')
        self.assertEqual(registry.infer_record_type(Path('originals/hongloumeng/index.html')), 'series-index')
        self.assertEqual(registry.infer_record_type(Path('essays/literature/hlm/reading-01.html')), 'essay')

    def test_first80_classification_and_labels(self):
        for number in range(1, 81):
            relative = Path(f'classics/hongloumeng/ch{number:03d}.html')
            self.assertEqual(registry.infer_record_type(relative), 'novel-chapter')
            self.assertEqual(registry.infer_sequence(relative), number)
            self.assertEqual(registry.infer_domain(relative), 'stories')
            self.assertEqual(registry.infer_taxonomy(relative), ('classics', 'hongloumeng'))
        self.assertEqual(registry.infer_record_type(Path('classics/hongloumeng/index.html')), 'series-index')
        self.assertEqual(registry.infer_record_type(Path('classics/hongloumeng/edition.html')), 'site-page')
        js = (Path(__file__).resolve().parents[1]/'search.js').read_text()
        self.assertIn("'novel-chapter': choices('Novel chapter', '小说章回', '小說章回'", js)

    def test_aliases_to_private_or_outside_targets_are_never_read(self):
        for alias in ('index.html', 'essays/alias.html', 'classics/hongloumeng/ch002.html'):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                forbidden = self.fixture(root)
                secret = root/'data/hongloumeng/first80/secret.html'
                secret.write_text('<html><title>PRIVATE_SENTINEL</title><h1>PRIVATE_HEADING</h1></html>')
                link = root/alias
                link.parent.mkdir(parents=True, exist_ok=True)
                if link.exists():
                    link.unlink()
                link.symlink_to(secret)
                forbidden.add(link)
                original = Path.read_text
                def guarded_read(path, *args, **kwargs):
                    self.assertNotIn(path, forbidden, 'A private alias was read')
                    return original(path, *args, **kwargs)
                with ExitStack() as stack:
                    for module in (search, sitemap, canonicals):
                        stack.enter_context(patch.object(module, 'ROOT', root))
                    stack.enter_context(patch.object(Path, 'read_text', guarded_read))
                    stack.enter_context(patch.object(sitemap, 'git_dates', return_value=({}, set())))
                    stack.enter_context(patch.object(sitemap, 'recorded_dates', return_value={}))
                    self.assertNotIn(link, search.collect_pages())
                    manifest, chunks = search.build()
                    self.assertNotIn('PRIVATE_SENTINEL', repr(chunks))
                    result, errors, _ = sitemap.build()
                    self.assertEqual(errors, [])
                    self.assertNotIn('PRIVATE_SENTINEL', result)
                    with patch('sys.argv', ['normalize_canonicals', '--check']), redirect_stdout(io.StringIO()):
                        self.assertEqual(canonicals.main(), 0)
                self.assertEqual(secret.read_text(), '<html><title>PRIVATE_SENTINEL</title><h1>PRIVATE_HEADING</h1></html>')
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory).resolve()
            target = Path(outside)/'outside.html'; target.write_text('OUTSIDE_SENTINEL')
            link = root/'index.html'; link.symlink_to(target)
            self.assertTrue(excluded_file(root, link))
            self.assertTrue(excluded_file(root, target))

    def test_public_alias_and_normalizer_keep_normal_public_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            self.fixture(root)
            link = root/'public-alias.html'
            link.symlink_to(root/'classics/hongloumeng/ch001.html')
            self.assertFalse(excluded_file(root, link))
            with patch.object(search, 'ROOT', root):
                self.assertIn(link, search.collect_pages())
            private = root/'data/hongloumeng/first80/secret.html'
            old_private = private.read_bytes()
            # --check reports a normal public normalization without writing it.
            path = root/'index.html'
            path.write_text(path.read_text().replace('https://nondubito.net/', 'http://nondubito.net/index.html'))
            with patch.object(canonicals, 'ROOT', root), patch('sys.argv', ['normalize_canonicals', '--check']), redirect_stdout(io.StringIO()) as output:
                self.assertEqual(canonicals.main(), 1)
            self.assertIn('index.html href:', output.getvalue())
            self.assertEqual(private.read_bytes(), old_private)

    def test_reverse_private_alias_cannot_become_a_canonical(self):
        for target, url_path in (
            ('data/hongloumeng/first80/alias.html', 'data/hongloumeng/first80/alias.html'),
            ('data/hongloumeng/first80/alias.html', '%64ata/hongloumeng/first80/alias.html'),
            ('data/hongloumeng/first80/alias.html', 'x/../data/hongloumeng/first80/alias.html'),
            ('classics/hongloumeng/review.html', 'classics/hongloumeng/review.html'),
        ):
            with self.subTest(url=url_path), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                page = root/'index.html'
                url = 'https://nondubito.net/'+url_path
                source = f'<html lang="en"><head><title>Public</title><meta name="description" content="Public"><link rel="canonical" href="{url}"></head><body>Public</body></html>'
                page.write_text(source)
                alias = root/target
                alias.parent.mkdir(parents=True, exist_ok=True)
                alias.symlink_to(page)
                original = Path.read_text
                def guarded_read(path, *args, **kwargs):
                    self.assertNotEqual(path, alias, 'Private lexical alias was read')
                    return original(path, *args, **kwargs)
                with ExitStack() as stack:
                    for module in (search, sitemap, canonicals):
                        stack.enter_context(patch.object(module, 'ROOT', root))
                    stack.enter_context(patch.object(Path, 'read_text', guarded_read))
                    stack.enter_context(patch.object(sitemap, 'git_dates', return_value=({}, set())))
                    stack.enter_context(patch.object(sitemap, 'recorded_dates', return_value={}))
                    with patch.object(sitemap, 'local_target', side_effect=AssertionError('Resolved forbidden URL')):
                        result, errors, _ = sitemap.build()
                    self.assertEqual(len(errors), 1)
                    self.assertIn('canonical URL is outside', errors[0])
                    self.assertNotIn('<url>', result)
                    # Search uses the public page path, never its canonical URL.
                    _, chunks = search.build()
                    self.assertEqual([record['u'] for record in chunks['en']], ['index.html'])
                    with patch('sys.argv', ['normalize_canonicals', '--check']), redirect_stdout(io.StringIO()) as output:
                        self.assertEqual(canonicals.main(), 1)
                    self.assertIn('outside the public reading allowlist', output.getvalue())
                self.assertEqual(page.read_text(), source)

    def test_url_guard_accepts_only_actual_public_reading_routes(self):
        for url in ('https://nondubito.net/classics/hongloumeng/',
                    'https://nondubito.net/classics/hongloumeng/index.html',
                    '//nondubito.net/classics/hongloumeng/ch001.html',
                    '/classics/hongloumeng/%63h080.html', 'https://nondubito.net/essays/other/index.html'):
            self.assertFalse(excluded_url(url), url)
        for url in ('//nondubito.net/data/hongloumeng/first80/alias.html',
                    '/%2564ata/hongloumeng/first80/alias.html',
                    'https://nondubito.net/classics/hongloumeng/extra.html',
                    'https://nondubito.net/x/../data/hongloumeng/first80/alias.html'):
            self.assertTrue(excluded_url(url), url)

    def test_global_search_dictionaries_cannot_read_private_aliases(self):
        for dictionary_name in ('zh-hant.js', 'zh-hant-data/index.js'):
            with self.subTest(dictionary=dictionary_name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                page = root/'index.html'
                page.write_text('<html lang="zh-Hans" data-editions="zh-Hans zh-Hant"><head><title>Public</title><meta name="description" content="Public"></head><body><h1 class="lang-zh">PUBLIC_ZH</h1></body></html>')
                secret = root/'data/hongloumeng/first80/secret.html'
                secret.parent.mkdir(parents=True)
                secret.write_text('<script>var variants = {"PUBLIC_ZH":"PRIVATE_TRANSLATED_TITLE"};</script>')
                dictionary = root/dictionary_name
                dictionary.parent.mkdir(parents=True, exist_ok=True)
                dictionary.symlink_to(secret)
                original = Path.read_text
                def guarded_read(path, *args, **kwargs):
                    self.assertNotIn(path, (secret, dictionary), 'Private dictionary was opened')
                    return original(path, *args, **kwargs)
                with patch.object(search, 'ROOT', root), patch.object(Path, 'read_text', guarded_read):
                    _, chunks = search.build()
                self.assertNotIn('PRIVATE_TRANSLATED_TITLE', repr(chunks))
                dictionary.unlink()
                dictionary.write_text('var variants = {"PUBLIC_ZH":"PUBLIC_TRANSLATED_TITLE"};')
                with patch.object(search, 'ROOT', root):
                    _, chunks = search.build()
                self.assertEqual(chunks['zh-Hant'][0]['t'], 'PUBLIC_TRANSLATED_TITLE')


if __name__ == '__main__':
    unittest.main()
