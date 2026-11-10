"""Exercise release gates and bounded updates only in isolated fixtures."""
from contextlib import redirect_stderr
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build_hongloumeng_reading as builder
import build_hongloumeng_hub as hub
import build_home_updates as home
import refresh_hongloumeng_reading_discovery as refresh


def page(relative, language='zh-Hans', title='Fixture'):
    canonical = refresh.ORIGIN+(relative.removesuffix('index.html') if relative.endswith('index.html') else relative)
    return f'<html lang="{language}"><head><title>{title}</title><meta name="description" content="Fixture description"><link rel="canonical" href="{canonical}"></head><body><h1>{title}</h1></body></html>'


class ReadingDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.manifest = dict(status='finalized', text_version='fixture-v1', reading_sha256='1'*64, body_sha256='2'*64,
                             build={'assets_sha256': '4'*64})
        self.approval = {key: self.manifest[key] for key in ('text_version', 'reading_sha256', 'body_sha256')}
        self.approval['boundaries_finalized'] = True
        self.approval['assets_sha256'] = '4'*64
        self.write('data/hongloumeng/first80-public/reading.zh.json', '{}')
        self.write('data/hongloumeng/first80-public/manifest.json', json.dumps(self.manifest))
        for name in refresh.FONT_ASSETS:
            self.write('data/hongloumeng/first80-public/'+name, 'Fixture asset')
        self.write('data/hongloumeng/characters.json', '[]')
        self.write('data/hongloumeng/readings/01.json', '{}')

    def write(self, relative, value):
        path = self.root/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(refresh.output_bytes(value))
        return path

    def fixture_reader(self, extras=None):
        outputs = {name: page(refresh.PREFIX+name) if name.endswith('.html') else 'fixture' for name in refresh.BASE_FILES}
        outputs.update({'fonts/nd-hlm-24aeb.woff2': b'wOF2fixture', 'fonts/ARPHICPL.TXT': 'Fixture license',
                        'fonts/FONT-NOTICE.txt': 'Fixture notice'})
        outputs.update(extras or {})
        for name, source in outputs.items():
            self.write(refresh.PREFIX+name, source)
        return outputs

    def validate_reader(self, outputs, approval=None):
        with patch.object(builder, 'load', return_value=({}, self.manifest)), patch.object(builder, 'render', return_value=outputs), patch.object(builder, 'load_assets', return_value={}):
            return refresh.validate_published_reader(self.root, self.approval if approval is None else approval)

    def test_draft_and_unresolved_boundaries_block_before_render(self):
        with patch.object(builder, 'load', return_value=({}, dict(self.manifest, status='draft'))), patch.object(builder, 'render') as renderer:
            with self.assertRaisesRegex(ValueError, 'not finalized'):
                refresh.validate_published_reader(self.root, self.approval)
            renderer.assert_not_called()
        for changes in ({'boundaries_finalized': False}, {'boundaries_finalized': 1},
                        {'reading_sha256': '3'*64}, {'body_sha256': '3'*64}, {'assets_sha256': '3'*64}, {'text_version': 'stale'}):
            with patch.object(builder, 'load', return_value=({}, self.manifest)), patch.object(builder, 'render') as renderer:
                with self.assertRaisesRegex(ValueError, 'explicit final hashes'):
                    refresh.validate_published_reader(self.root, dict(self.approval, **changes))
                renderer.assert_not_called()

    def test_exact_reader_outputs_and_licensed_font(self):
        outputs = self.fixture_reader()
        self.assertEqual(len(outputs), 87)
        paths = self.validate_reader(outputs)
        self.assertEqual(len(paths), 82)
        self.assertTrue(all(path.suffix == '.html' for path in paths))

    def test_unexpected_output_names_and_unlicensed_font_block(self):
        base = self.fixture_reader()
        for name in ('../private.html', '/tmp/private.html', 'review.html', 'fonts/private.html',
                     'fonts/../../secret.txt', 'fonts/source.json', 'fonts/license.txt'):
            with self.assertRaisesRegex(ValueError, 'Unexpected reading output'):
                refresh.validate_output_names(dict(base, **{name: 'fixture'}))
        with self.assertRaisesRegex(ValueError, 'Missing required'):
            refresh.validate_output_names({name: value for name, value in base.items() if name != 'fonts/ARPHICPL.TXT'})
        with self.assertRaisesRegex(ValueError, 'Invalid WOFF2'):
            refresh.validate_output_names(dict(base, **{'fonts/nd-hlm-24aeb.woff2': b'not a font'}))

    def test_stale_extra_and_symlinked_reader_files_block(self):
        outputs = self.fixture_reader()
        self.write(refresh.PREFIX+'ch001.html', 'stale')
        with self.assertRaisesRegex(ValueError, 'stale release output'):
            self.validate_reader(outputs)
        self.write(refresh.PREFIX+'ch001.html', outputs['ch001.html'])
        extra = self.write(refresh.PREFIX+'review.html', 'private')
        with self.assertRaisesRegex(ValueError, 'output allowlist'):
            self.validate_reader(outputs)
        extra.unlink()
        extra.symlink_to(self.root/'outside.html')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.validate_reader(outputs)

    def test_publication_claims_and_retained_date(self):
        update = refresh.publication_update('2026-11-10')
        self.assertEqual(update['languages'], ['zh'])
        self.assertIn('外语翻译尚未发布', update['summary']['zh'])
        self.assertEqual(refresh.resolve_date({'updates': [update]}, None), '2026-11-10')
        with self.assertRaisesRegex(ValueError, 'change the publication date'):
            refresh.resolve_date({'updates': [update]}, '2026-11-11')
        with self.assertRaisesRegex(ValueError, 'requires --date'):
            refresh.resolve_date({'updates': []}, None)

    def test_latest_insertion_and_card_replacement_preserve_unrelated_bytes(self):
        update = refresh.publication_update('2026-11-10')
        original = '<header>UNCHANGED</header><!-- OLD START --><section class="updates-section">OLD</section><!-- OLD END -->FOOTER'
        result = refresh.replace_latest(original, update)
        self.assertEqual(result.replace(refresh.latest_card(update)+'\n', ''), original)
        self.assertEqual(refresh.replace_latest(result, update), result)
        card = '<a href="hlm/index.html" class="series-card"><p class="series-card-desc-zh lang-zh">OLD</p><p class="series-card-desc-en lang-en">OLD</p></a>'
        replaced = refresh.replace_project_card('PREFIX'+card+'SUFFIX', 'hlm/index.html')
        self.assertTrue(replaced.startswith('PREFIX') and replaced.endswith('SUFFIX'))
        self.assertIn('第八十一至八十五回', replaced)
        self.assertIn('chapters 86–110 remain unpublished', replaced)
        self.assertEqual(refresh.replace_project_card(replaced, 'hlm/index.html'), replaced)

    def discovery_fixture(self):
        chapter = refresh.PREFIX+'ch001.html'
        source = page(chapter)
        path = self.write(chapter, source)
        manifest = {'version': 1, 'record_count': 2, 'languages': {lang: {'count': 2, 'path': f'data/search/{lang.lower()}.json'} for lang in refresh.search.SEARCH_LANGUAGES}}
        self.write('data/search-index.json', json.dumps(manifest))
        keep = {'u': 'essays/unrelated/ep01.html', 'k': 'essay', 't': 'Keep exactly', 'custom': ['untouched']}
        for lang in refresh.search.SEARCH_LANGUAGES:
            records = [copy.deepcopy(keep)]
            if lang == 'en':
                records.append({'u': chapter, 'k': 'essay', 't': 'Wrong language'})
            self.write(f'data/search/{lang.lower()}.json', json.dumps({'version': 1, 'records': records}))
        self.write('sitemap.xml', refresh.sitemap_xml([(refresh.ORIGIN+'essays/unrelated/ep01.html', '2025-01-01')]))
        return {path: source}, keep

    def test_scoped_search_and_sitemap_are_repeatable(self):
        sources, keep = self.discovery_fixture()
        outputs = refresh.discovery_outputs(self.root, sources, '2026-11-10')
        zh = json.loads(outputs[self.root/'data/search/zh-hans.json'])['records']
        self.assertEqual(zh[0], keep)
        self.assertEqual(zh[1]['k'], 'novel-chapter')
        self.assertEqual(zh[1]['n'], 1)
        self.assertEqual(json.loads(outputs[self.root/'data/search/en.json'])['records'], [keep])
        self.assertNotIn(self.root/'data/search/fr.json', outputs)
        self.assertIn('<lastmod>2025-01-01</lastmod>', outputs[self.root/'sitemap.xml'])
        self.assertIn('<lastmod>2026-11-10</lastmod>', outputs[self.root/'sitemap.xml'])
        for path, value in outputs.items():
            path.write_text(value)
        again = refresh.discovery_outputs(self.root, sources, '2026-11-10')
        self.assertTrue(all(path.read_text() == value for path, value in again.items()))

    def test_private_search_and_unexpected_scope_fail_without_writes(self):
        sources, _ = self.discovery_fixture()
        index = self.root/'data/search/en.json'
        index.write_text(json.dumps({'records': [{'u': 'data/hongloumeng/first80/private.html'}]}))
        before = {path: path.read_bytes() for path in self.root.rglob('*') if path.is_file()}
        with self.assertRaisesRegex(ValueError, 'Source or private data'):
            refresh.discovery_outputs(self.root, sources, '2026-11-10')
        self.assertEqual(before, {path: path.read_bytes() for path in before})
        with self.assertRaisesRegex(ValueError, 'Unexpected path'):
            refresh.discovery_outputs(self.root, {self.root/'unexpected.html': 'x'}, '2026-11-10')

    def test_editorial_plan_uses_existing_home_configuration(self):
        updates = []
        for n in range(6):
            update = refresh.publication_update('2026-11-09')
            update.update(id=f'existing-{n}', url=f'essays/fixture-{n}/index.html')
            updates.append(update)
        ledger = {'updates': updates}
        config = {'feature_id': 'existing-0', 'feature_deck': {'en': 'Keep', 'zh': '保留', 'zh-hant': '保留'}}
        self.write('data/home-updates.json', json.dumps(config))
        self.write('index.html', 'BEFORE'+home.START+'old'+home.END+'AFTER')
        self.write('latest.html', '<section class="updates-section">Older</section>')
        for name, href in (('library.html', 'essays/literature/hlm/index.html'), ('essays/literature/index.html', 'hlm/index.html')):
            self.write(name, f'<a href="{href}" class="series-card"><p class="series-card-desc-zh lang-zh">old</p><p class="series-card-desc-en lang-en">old</p></a>')
        with patch.object(hub, 'ROOT', self.root), patch.object(hub, 'render', return_value={self.root/p: 'hub' for p in refresh.HUBS}):
            outputs = refresh.editorial_outputs(self.root, ledger, '2026-11-10')
        self.assertNotIn(self.root/'data/home-updates.json', outputs)
        self.assertEqual(json.loads((self.root/'data/home-updates.json').read_text()), config)
        result = outputs[self.root/'index.html']
        self.assertTrue(result.startswith('BEFORE') and result.endswith('AFTER'))
        self.assertEqual(result.count('class="home-update-row"'), 4)
        self.assertIn('data-update-id="existing-0"', result)
        self.assertEqual(ledger['updates'], updates)
        self.assertEqual(set(outputs), {self.root/'data/site-updates.json', *(self.root/name for name in refresh.EDITORIAL_HTML)})

    def test_cli_defaults_to_no_writes_and_gates_before_writes(self):
        path = self.write('output.txt', 'unchanged')
        for argv, effect in ((['refresh'], None), (['refresh', '--write'], ValueError('not finalized'))):
            with patch('sys.argv', argv), patch.object(refresh, 'render', return_value={path: 'changed'}, side_effect=effect), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as result:
                    refresh.main()
                self.assertEqual(result.exception.code, 2)
            self.assertEqual(path.read_text(), 'unchanged')

    def test_complete_scoped_plan_roundtrips_in_temp_tree(self):
        reader = self.fixture_reader()
        updates = []
        for n in range(6):
            update = refresh.publication_update('2026-11-09')
            update.update(id=f'existing-{n}', url=f'essays/fixture-{n}/index.html')
            updates.append(update)
        self.write('data/site-updates.json', json.dumps({'updates': updates}))
        self.write('data/home-updates.json', json.dumps({'feature_id': 'existing-0', 'feature_deck': {'en': 'Keep', 'zh': '保留', 'zh-hant': '保留'}}))
        hub_outputs = {}
        for relative in refresh.EDITORIAL_HTML:
            source = page(relative)
            if relative == 'index.html':
                source = source.replace('</body>', home.START+'old'+home.END+'</body>')
            elif relative == 'latest.html':
                source = source.replace('</body>', '<section class="updates-section">Old</section></body>')
            elif relative in ('library.html', 'essays/literature/index.html'):
                href = 'hlm/index.html' if relative.startswith('essays/') else 'essays/literature/hlm/index.html'
                source = source.replace('</body>', f'<a href="{href}" class="series-card"><p class="series-card-desc-zh lang-zh">old</p><p class="series-card-desc-en lang-en">old</p></a></body>')
            self.write(relative, source)
            if relative in refresh.HUBS:
                hub_outputs[self.root/relative] = source.replace('Fixture description', 'New hub fixture')
        for relative in refresh.CONTINUATION:
            parts = Path(relative).parts
            language = {'zh-hant': 'zh-Hant'}.get(parts[2], parts[2]) if len(parts) == 4 else 'zh-Hans'
            self.write(relative, page(relative, language))
        manifest = {'record_count': 0, 'languages': {lang: {'count': 0} for lang in refresh.search.SEARCH_LANGUAGES}}
        self.write('data/search-index.json', json.dumps(manifest))
        for lang in refresh.search.SEARCH_LANGUAGES:
            self.write(f'data/search/{lang.lower()}.json', json.dumps({'records': []}))
        self.write('sitemap.xml', refresh.sitemap_xml([]))
        with patch.object(builder, 'load', return_value=({}, self.manifest)), patch.object(builder, 'load_assets', return_value={}), patch.object(builder, 'render', return_value=reader), patch.object(hub, 'ROOT', self.root), patch.object(hub, 'render', return_value=hub_outputs):
            outputs = refresh.render(self.root, '2026-11-10', self.approval)
            self.assertEqual(len(outputs), 18)
            self.assertEqual(sum(r['u'].startswith(refresh.PREFIX) for r in json.loads(outputs[self.root/'data/search/zh-hans.json'])['records']), 82)
            for lang in refresh.search.SEARCH_LANGUAGES:
                if lang != 'zh-Hans':
                    self.assertFalse(any(r['u'].startswith(refresh.PREFIX) for r in json.loads(outputs[self.root/f'data/search/{lang.lower()}.json'])['records']))
            for path, source in outputs.items():
                path.write_text(source)
            repeated = refresh.render(self.root, None, self.approval)
            self.assertTrue(all(path.read_text() == source for path, source in repeated.items()))

    def test_private_url_aliases_block_search_and_sitemap_merges(self):
        aliases = (
            '/data/hongloumeng/first80/secret.html',
            '//nondubito.net/data/hongloumeng/first80/secret.html',
            'https://nondubito.net/x/../data/hongloumeng/first80/secret.html',
            'https://nondubito.net/%64ata/hongloumeng/first80/secret.html',
            'https://NONdubito.net/%2564ata/hongloumeng/first80/secret.html',
            '/x/%2e%2e/data%2fhongloumeng%2ffirst80/secret.html?view=1#top',
            '\\data\\hongloumeng\\first80\\secret.html',
            'https://www.nondubito.net/data/hongloumeng/first80/secret.html',
            '/classics/hongloumeng/x/../review.html',
        )
        sources, _ = self.discovery_fixture()
        index = self.root/'data/search/en.json'
        sitemap = self.root/'sitemap.xml'
        for alias in aliases:
            with self.subTest(alias=alias):
                index.write_text(json.dumps({'records': [{'u': alias}]}))
                sitemap.write_text(refresh.sitemap_xml([]))
                with self.assertRaises(ValueError):
                    refresh.discovery_outputs(self.root, sources, '2026-11-10')
                self.assertEqual(json.loads(index.read_text())['records'][0]['u'], alias)
                index.write_text(json.dumps({'records': []}))
                sitemap.write_text(refresh.sitemap_xml([(alias, '2025-01-01')]))
                before = sitemap.read_bytes()
                with self.assertRaises(ValueError):
                    refresh.discovery_outputs(self.root, sources, '2026-11-10')
                self.assertEqual(sitemap.read_bytes(), before)
        for url in ('https://nondubito.net/classics/hongloumeng/',
                    '/classics/hongloumeng/ch001.html', '//nondubito.net/classics/hongloumeng/ch080.html',
                    'https://nondubito.net/classics/hongloumeng/x/../%63h001.html',
                    'essays/another/index.html', 'https://other.example/public.html'):
            refresh.reject_private_url(url)

    def test_selected_input_aliases_block_before_their_contents_are_read(self):
        selected = ('library.html', 'index.html', 'data/site-updates.json', 'data/search-index.json',
                    'data/search/en.json', 'sitemap.xml', 'data/home-updates.json',
                    'data/hongloumeng/first80-public/reading.zh.json',
                    'data/hongloumeng/first80-public/fonts/ARPHICPL.TXT')
        secret = self.write('data/hongloumeng/first80/secret.txt', 'PRIVATE_SENTINEL')
        original = Path.read_text
        for relative in selected:
            with self.subTest(relative=relative):
                path = self.root/relative
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.exists():
                    path.unlink()
                path.symlink_to(secret)
                def forbidden_read(candidate, *args, **kwargs):
                    self.assertNotEqual(candidate, path, 'Private alias contents were opened')
                    return original(candidate, *args, **kwargs)
                with patch.object(Path, 'read_text', forbidden_read), self.assertRaisesRegex(ValueError, 'Unsafe publication path'):
                    refresh.read_text(self.root, path)
                path.unlink()
        self.assertEqual(secret.read_text(), 'PRIVATE_SENTINEL')

    def test_selected_output_and_parent_directory_aliases_block(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside)/'target.html'; target.write_text('OUTSIDE_SENTINEL')
            link = self.root/'library.html'; link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, 'Unsafe publication path'):
                refresh.validate_write_paths(self.root, {link: 'replacement'})
            link.unlink()
            link = self.root/'alias-dir'; link.symlink_to(Path(outside), target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'Unsafe publication path'):
                refresh.checked_path(self.root, link/'target.html')
            self.assertEqual(target.read_text(), 'OUTSIDE_SENTINEL')
        unexpected = self.write('unrelated.txt', 'Keep')
        with self.assertRaisesRegex(ValueError, 'Unexpected publication output path'):
            refresh.validate_write_paths(self.root, {unexpected: 'replacement'})

    def test_public_builder_cannot_read_aliased_inputs(self):
        secret = self.write('data/hongloumeng/first80/secret.json', 'PRIVATE_SENTINEL')
        path = self.root/'data/hongloumeng/first80-public/manifest.json'
        path.unlink(); path.symlink_to(secret)
        with patch.object(builder, 'load') as loader, self.assertRaisesRegex(ValueError, 'Unsafe publication path'):
            refresh.validate_published_reader(self.root, self.approval)
        loader.assert_not_called()

    def test_latest_reversed_markers_are_rejected(self):
        update = refresh.publication_update('2026-11-10')
        for source in (refresh.END+'old'+refresh.START, refresh.START+'old', refresh.START+refresh.START+refresh.END):
            with self.assertRaisesRegex(ValueError, 'Invalid Latest marker pair'):
                refresh.replace_latest(source, update)

    def test_discovery_reader_and_cli_reject_aliases_before_io(self):
        sources, _ = self.discovery_fixture()
        secret = self.write('data/hongloumeng/first80/secret.json', 'PRIVATE_SENTINEL')
        index = self.root/'data/search/en.json'
        index.unlink(); index.symlink_to(secret)
        original = Path.read_text
        def guarded_read(path, *args, **kwargs):
            self.assertNotIn(path, (index, secret), 'Private content was read')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', guarded_read), self.assertRaisesRegex(ValueError, 'Unsafe publication path'):
            refresh.discovery_outputs(self.root, sources, '2026-11-10')
        with patch.object(refresh, 'ROOT', self.root), patch('sys.argv', ['refresh', '--write']), patch.object(refresh, 'render', return_value={index: 'changed'}), patch.object(Path, 'write_text', side_effect=AssertionError('Unexpected write')), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                refresh.main()
            self.assertEqual(result.exception.code, 2)
        self.assertEqual(secret.read_text(), 'PRIVATE_SENTINEL')

    def test_hub_and_title_dictionary_aliases_block_before_read(self):
        secret = self.write('data/hongloumeng/first80/secret.json', 'PRIVATE_SENTINEL')
        catalog = self.root/'data/hongloumeng/characters.json'
        catalog.unlink(); catalog.symlink_to(secret)
        with patch.object(hub, 'render') as renderer, self.assertRaisesRegex(ValueError, 'Unsafe publication path'):
            refresh.editorial_outputs(self.root, {'updates': []}, '2026-11-10')
        renderer.assert_not_called()
        sources, _ = self.discovery_fixture()
        dictionary = self.root/'zh-hant.js'; dictionary.symlink_to(secret)
        with patch.object(refresh.registry, 'scan_page') as scanner, self.assertRaisesRegex(ValueError, 'Unsafe publication path'):
            refresh.search_records(self.root, sources)
        scanner.assert_not_called()


if __name__ == '__main__':
    unittest.main()
