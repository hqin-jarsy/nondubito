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

    def test_complete_scoped_plan_roundtrips_in_temp_tree(self, bilingual=False):
        reader = self.fixture_reader()
        traditional_approval = self.traditional_fixture()[0] if bilingual else None
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
            outputs = refresh.render(self.root, '2026-11-10', self.approval, traditional_approval=traditional_approval)
            self.assertEqual(len(outputs), 18)
            self.assertEqual(sum(r['u'].startswith(refresh.PREFIX) for r in json.loads(outputs[self.root/'data/search/zh-hans.json'])['records']), 82)
            for lang in refresh.search.SEARCH_LANGUAGES:
                if lang == 'zh-Hant' and bilingual:
                    self.assertEqual(sum(r['u'].startswith(refresh.TRADITIONAL_PREFIX) for r in json.loads(outputs[self.root/'data/search/zh-hant.json'])['records']), 82)
                elif lang != 'zh-Hans':
                    self.assertFalse(any(r['u'].startswith(refresh.PREFIX) for r in json.loads(outputs[self.root/f'data/search/{lang.lower()}.json'])['records']))
            for path, source in outputs.items():
                path.write_text(source)
            repeated = refresh.render(self.root, None, self.approval, traditional_approval=traditional_approval)
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
            'https://nondubito.net/classics/hongloumeng/x/../%63h001.html',
            '/data/hongloumeng/first80/../../../classics/hongloumeng/ch001.html',
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


    def test_complete_bilingual_plan_roundtrips_in_temp_tree(self):
        self.test_complete_scoped_plan_roundtrips_in_temp_tree(bilingual=True)
        ledger = json.loads((self.root/'data/site-updates.json').read_text())
        records = [u for u in ledger['updates'] if u['id'] == refresh.UPDATE_ID]
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['languages'], ['zh', 'zh-hant'])
        self.assertEqual(records[0]['date'], '2026-11-10')
        import check_site_updates
        with patch.object(check_site_updates, 'ROOT', self.root):
            # Other fixture cards are intentionally absent; validate ledger fields separately.
            self.assertFalse([e for e in check_site_updates.check() if 'updates[1]:' in e])

    def traditional_fixture(self):
        import build_hongloumeng_reading_traditional as traditional
        from contextlib import ExitStack
        self.write('data/hongloumeng/first80-public/reading.zh-hant.json', '{}')
        self.write('data/hongloumeng/first80-public/manifest.zh-hant.json', json.dumps(self.manifest))
        simplified = self.fixture_reader()
        converted = {name: page(refresh.TRADITIONAL_PREFIX+name, 'zh-Hant') if name.endswith('.html') else value
                     for name, value in simplified.items()}
        for name, value in converted.items():
            self.write(refresh.TRADITIONAL_PREFIX+name, value)
        stack = ExitStack()
        self.addCleanup(stack.close)
        for module, outputs in ((builder, simplified), (traditional, converted)):
            stack.enter_context(patch.object(module, 'load', return_value=({}, self.manifest)))
            stack.enter_context(patch.object(module, 'load_assets', return_value={}))
            stack.enter_context(patch.object(module, 'render', return_value=outputs))
        stack.enter_context(patch.object(traditional, 'source_gate'))
        approval = dict(self.approval, action='publish-hongloumeng-first80-traditional', approved=True)
        return approval, traditional, converted

    def test_bilingual_exact_164_html_and_both_approvals(self):
        approval, traditional, converted = self.traditional_fixture()
        paths = refresh.validate_published_reader(self.root, self.approval, traditional_approval=approval)
        self.assertEqual(len(paths), 164)
        self.assertEqual(sum(p.parent.name == 'zh-hant' for p in paths), 82)
        builder.render.assert_called_with({}, self.manifest, mode='release', assets={}, bilingual=True)
        traditional.render.assert_called_with({}, self.manifest, mode='release', assets={}, bilingual=True)
        traditional.source_gate.assert_called_once_with(self.root/'data/hongloumeng/first80-public')
        for changes in ({'approved': 1}, {'approved': False}, {'action': 'publish-hongloumeng-first80'},
                        {'reading_sha256': '0'*64}, {'body_sha256': '0'*64}, {'assets_sha256': '0'*64},
                        {'text_version': 'wrong'}, {'boundaries_finalized': 1}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                refresh.validate_published_reader(self.root, self.approval, traditional_approval=dict(approval, **changes))
        with patch.object(traditional, 'load', return_value=({}, dict(self.manifest, status='draft'))), self.assertRaisesRegex(ValueError, 'not finalized'):
            refresh.validate_published_reader(self.root, self.approval, traditional_approval=approval)

    def test_bilingual_source_baseline_gate_blocks_before_traditional_render(self):
        approval, traditional, _ = self.traditional_fixture()
        with patch.object(traditional, 'source_gate', side_effect=ValueError('Simplified baseline checksum differs')) as gate:
            with self.assertRaisesRegex(ValueError, 'baseline checksum'):
                refresh.validate_published_reader(self.root, self.approval, traditional_approval=approval)
            gate.assert_called_once_with(self.root/'data/hongloumeng/first80-public')
            traditional.render.assert_not_called()
            traditional.load_assets.assert_not_called()

    def test_bilingual_stale_extra_alias_and_wrong_type_block(self):
        approval, _, converted = self.traditional_fixture()
        chapter = self.root/refresh.TRADITIONAL_PREFIX/'ch080.html'
        chapter.write_text('stale')
        with self.assertRaisesRegex(ValueError, 'stale release'):
            refresh.validate_published_reader(self.root, self.approval, traditional_approval=approval)
        chapter.write_text(converted['ch080.html'])
        extra = self.write(refresh.TRADITIONAL_PREFIX+'review.html', 'PRIVATE')
        with self.assertRaises(ValueError):
            refresh.validate_published_reader(self.root, self.approval, traditional_approval=approval)
        extra.unlink()
        extra.mkdir()
        with self.assertRaises(ValueError):
            refresh.validate_published_reader(self.root, self.approval, traditional_approval=approval)
        extra.rmdir()
        extra.symlink_to(chapter)
        with self.assertRaises(ValueError):
            refresh.validate_published_reader(self.root, self.approval, traditional_approval=approval)

    def test_bilingual_search_isolated_82_entries_per_language_and_repeatable(self):
        sources, keep = self.discovery_fixture()
        for prefix, language in ((refresh.PREFIX, 'zh-Hans'), (refresh.TRADITIONAL_PREFIX, 'zh-Hant')):
            for name in refresh.PUBLIC_HTML:
                relative = prefix+name
                source = page(relative, language)
                sources[self.write(relative, source)] = source
        before = {lang: (self.root/f'data/search/{lang.lower()}.json').read_bytes()
                  for lang in refresh.search.SEARCH_LANGUAGES if lang not in ('zh-Hans', 'zh-Hant', 'en')}
        outputs = refresh.discovery_outputs(self.root, sources, '2026-11-10')
        for lang, prefix in (('zh-Hans', refresh.PREFIX), ('zh-Hant', refresh.TRADITIONAL_PREFIX)):
            records = json.loads(outputs[self.root/f'data/search/{lang.lower()}.json'])['records']
            self.assertEqual(len(records), 83)
            self.assertEqual(records[0], keep)
            self.assertEqual({r['u'] for r in records[1:]}, {prefix+n for n in refresh.PUBLIC_HTML})
            self.assertEqual(sum(r['k'] == 'novel-chapter' for r in records), 80)
        self.assertEqual(outputs[self.root/'sitemap.xml'].count('<url>'), 165)
        for path, value in outputs.items():
            path.write_text(value)
        repeated = refresh.discovery_outputs(self.root, sources, '2026-11-10')
        self.assertTrue(all(p.read_text() == value for p, value in repeated.items()))
        for lang, value in before.items():
            self.assertEqual((self.root/f'data/search/{lang.lower()}.json').read_bytes(), value)
        wrong = self.root/refresh.TRADITIONAL_PREFIX/'ch001.html'
        with self.assertRaisesRegex(ValueError, 'own Chinese language'):
            refresh.search_records(self.root, {wrong: page(refresh.TRADITIONAL_PREFIX+'ch001.html', 'en')})

    def test_bilingual_editorial_updates_same_record_without_false_language_claims(self):
        update = refresh.publication_update('2026-11-10', traditional=True)
        self.assertEqual(update['languages'], ['zh', 'zh-hant'])
        self.assertIn('简体／繁体', update['title']['zh'])
        self.assertIn('簡體／繁體', update['title']['zh-hant'])
        self.assertIn('Simplified and Traditional Chinese', update['title']['en'])
        self.assertEqual(update['id'], refresh.UPDATE_ID)
        self.assertEqual(refresh.resolve_date({'updates': [update]}, None), '2026-11-10')
        self.assertIn('外语翻译尚未发布', update['summary']['zh'])
        card = refresh.latest_card(update)
        self.assertIn(refresh.TRADITIONAL_PREFIX+'index.html', card)
        self.assertEqual(refresh.replace_latest(card, update), card)

    def test_seven_malformed_latest_cases_fail(self):
        update = refresh.publication_update('2026-11-10', traditional=True)
        for source in (refresh.START, refresh.END, refresh.END+refresh.START,
                       refresh.START*2+refresh.END, refresh.START+refresh.END*2,
                       '<article data-update-id="'+refresh.UPDATE_ID+'"></article>', '<main>No insertion point</main>'):
            with self.subTest(source=source), self.assertRaises(ValueError):
                refresh.replace_latest(source, update)

    def test_root_ancestor_alias_rejected_before_existing_file_read_or_write(self):
        # All files exist: this must reach the root-ancestor guard, not fail on
        # missing inputs, approval, or a leaf symlink.
        from contextlib import ExitStack
        real_root = self.root/'real'/'repo'
        real_root.mkdir(parents=True)
        target = real_root/'library.html'
        target.write_text('KEEP EXACTLY')
        alias = self.root/'alias'
        alias.symlink_to(real_root.parent, target_is_directory=True)
        lexical_root = alias/'repo'
        lexical_target = lexical_root/'library.html'
        self.assertTrue(lexical_target.is_file())
        self.assertFalse(lexical_root.is_symlink())
        with ExitStack() as stack:
            reader = stack.enter_context(patch.object(Path, 'read_text', side_effect=AssertionError('Opened aliased input')))
            writer = stack.enter_context(patch.object(Path, 'write_text', side_effect=AssertionError('Wrote aliased output')))
            for operation in (
                lambda: refresh.checked_path(lexical_root, lexical_target),
                lambda: refresh.read_text(lexical_root, lexical_target),
                lambda: refresh.validate_write_paths(lexical_root, {lexical_target: 'replacement'}),
            ):
                with self.assertRaisesRegex(ValueError, 'Unsafe publication path'):
                    operation()
            reader.assert_not_called()
            writer.assert_not_called()
        self.assertEqual(target.read_text(), 'KEEP EXACTLY')
        # A caller using an actual canonical path remains supported.
        self.assertEqual(refresh.checked_path(real_root, target), target)
        self.assertEqual(refresh.read_text(real_root, target), 'KEEP EXACTLY')
        refresh.validate_write_paths(real_root, {target: 'replacement'})

    def test_only_standard_macos_root_ancestor_aliases_are_accepted(self):
        import sys
        if sys.platform != 'darwin':
            self.skipTest('macOS system aliases only')
        with tempfile.TemporaryDirectory(dir='/tmp') as directory:
            root = Path(directory)
            target = root/'library.html'
            target.write_text('SYSTEM TEMP')
            self.assertEqual(refresh.read_text(root, target), 'SYSTEM TEMP')
            refresh.validate_write_paths(root, {target: 'replacement'})
            canonical_root = root.resolve()
            self.assertEqual(refresh.read_text(canonical_root, canonical_root/'library.html'), 'SYSTEM TEMP')

    def test_hardlinked_inputs_outputs_and_nonregular_files_block(self):
        import os
        secret = self.write('data/hongloumeng/first80/secret.txt', 'PRIVATE')
        for relative in ('library.html', 'data/hongloumeng/first80-public/reading.zh-hant.json'):
            target = self.root/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            os.link(secret, target)
            with self.assertRaisesRegex(ValueError, 'Unsafe publication path'):
                refresh.read_text(self.root, target)
            target.unlink()
        target = self.root/'library.html'
        os.mkfifo(target)
        with self.assertRaisesRegex(ValueError, 'Unsafe publication path'):
            refresh.read_text(self.root, target)
        target.unlink()
        target.mkdir()
        with self.assertRaises(ValueError):
            refresh.validate_write_paths(self.root, {target: 'no'})


if __name__ == '__main__':
    unittest.main()
