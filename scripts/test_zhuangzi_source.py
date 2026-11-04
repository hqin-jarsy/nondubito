"""Source-only checks: never approve or render unfinished foreign manuscripts."""
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote

import build_zhuangzi as original
from full_series_languages import (ROOT, original_article, primary_bodies,
                                   profile, source_digest, source_file, upgrade_primary)
from prepare_original_series_review import primary_main_hashes
from zhuangzi_source import reading_units


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


class ZhuangziSource(unittest.TestCase):
    def test_actual_commentary_link_parentheses_survive_narrow_markdown(self):
        from zhuangzi_language_index import apparatus_inline
        from prepare_action_sources import Document
        spec = profile('zhuangzi')
        article = original_article('zhuangzi', spec, '18')
        # A source-only inline fragment, not an unapproved foreign-page render.
        note = article['notes_zh'][2]
        rendered = apparatus_inline(note, article['sources_zh'])
        links = [n for n in Document(rendered).root.walk() if n.tag == 'a']
        self.assertEqual([unquote(n.attrs['href']) for n in links],
                         [s['url'] for s in article['sources_zh'][2:]])
        self.assertIn('%28四庫全書本%29/全覽', rendered)
        self.assertNotIn('</a>/全覽)', rendered)
        for slug in ('guide', '01', '19'):
            a = original_article('zhuangzi', spec, slug)
            for text in a['notes_zh']:
                value = apparatus_inline(text, a['sources_zh'])
                self.assertNotIn('</a>/全覽)', value)

    def test_five_original_non_linear_groups_and_the_original_sequence(self):
        from zhuangzi_language_index import routes
        groups = routes()
        expected = {
            'encounters': list(range(1, 11)), 'inner': list(range(11, 30)),
            'discernment': list(range(30, 42))+list(range(59, 66)),
            'outer': list(range(42, 59)), 'closing': [66, 67],
        }
        self.assertEqual([g[0] for g in groups], list(expected))
        for key, _, slugs in groups:
            self.assertEqual(slugs, [f'{n:02d}' for n in expected[key]])
        all_slugs = [slug for _, _, slugs in groups for slug in slugs]
        self.assertEqual(len(all_slugs), 67)
        self.assertEqual(sorted(all_slugs), [f'{n:02d}' for n in range(1, 68)])

    def test_complete_unique_source_and_original_production_boundaries(self):
        spec = profile('zhuangzi')
        self.assertEqual(spec['slugs'], ['guide']+[f'{n:02d}' for n in range(1, 68)])
        counts = {'p': 0, 'h2': 0, 'quote': 0}
        notes = links = 0
        for slug in spec['slugs']:
            article = original_article('zhuangzi', spec, slug)
            n = 0 if slug == 'guide' else int(slug)
            path = ROOT/'data/zhuangzi/zh'/f'{n:02d}.md'
            self.assertEqual(source_file('zhuangzi', spec, slug), path)
            self.assertEqual(article['body_zh'], reading_units(path.read_text()))
            for unit in article['body_zh']:
                counts['h2' if unit.startswith('## ') else 'quote' if unit.startswith('> ') else 'p'] += 1
            self.assertIsNone(article['aside_zh'])
            self.assertTrue(article['notes_zh'])
            self.assertTrue(article['sources_zh'])
            notes += len(article['notes_zh'])
            links += len(article['sources_zh'])
        self.assertEqual(counts, {'p': 1265, 'h2': 507, 'quote': 129})
        self.assertEqual((notes, links), (175, 178))
        first = [original_article('zhuangzi', spec, s) for s in spec['slugs'][:6]]
        self.assertEqual([len(a['body_zh']) for a in first], [17, 38, 38, 45, 38, 38])
        quote = next(p for p in first[-1]['body_zh'] if p.startswith('> '))
        self.assertIn('\n\n其往也', quote)
        self.assertEqual(len([p for p in first[-1]['body_zh'] if p.startswith('> ')]), 1)

    def test_all_three_canonical_editions_and_complete_reading_areas_unchanged(self):
        spec = profile('zhuangzi')
        before = json.loads((ROOT/spec['primary_baseline']).read_text())
        self.assertEqual(primary_main_hashes(spec), before['primary_main'])
        self.assertEqual(len(before['primary_main']), 69)
        self.assertEqual(len(before['canonical_reading_files']), 204)
        for path, digest in before['canonical_reading_files'].items():
            self.assertEqual(sha((ROOT/path).read_bytes()), digest, path)
        self.assertEqual(sha((ROOT/'data/zhuangzi/manifest.json').read_bytes()),
                         before['canonical_manifest_sha256'])
        for slug in spec['slugs']:
            self.assertEqual(source_digest('zhuangzi', spec, slug), before['source_data'][slug])
            raw = (ROOT/spec['directory']/(slug+'.html')).read_text()
            self.assertEqual(sha(primary_bodies(spec, raw)), before['primary_bodies'][slug])
            self.assertEqual(len(re.findall(r'<article class="essay-body ', raw)), 3)
        for path, digest in before['distinct_legacy_pages'].items():
            self.assertEqual(sha((ROOT/path).read_bytes()), digest, path)

    def test_variable_notes_and_exact_research_and_chapter_routes(self):
        spec = profile('zhuangzi')
        intro = original_article('zhuangzi', spec, 'guide')
        self.assertEqual([s['url'] for s in intro['sources_zh']],
                         ['https://doi.org/10.5281/zenodo.'+r[3] for r in original.RESEARCH])
        for slug in spec['slugs'][1:]:
            article = original_article('zhuangzi', spec, slug)
            self.assertEqual(article['sources_zh'][0]['url'], original.CHAPTERS[int(slug)][3])
            self.assertEqual(article['sources_zh'][1]['url'],
                             'https://nondubito.net/essays/zhuangzi/index.html#research')
        for slug, fragments in {
            '11': ('不是已经证实的古代课程安排',),
            '19': ('郭象', '“其人”所指也有分歧'),
            '30': ('文本层次的假说', '历史作者的归属'),
            '35': ('不是古文', '不是失落原稿的复原'),
            '66': ('“仁义”', '“义士”'),
        }.items():
            text = '\n'.join(original_article('zhuangzi', spec, slug)['notes_zh'])
            for fragment in fragments:
                self.assertIn(fragment, text)
        final_urls = [s['url'] for s in original_article('zhuangzi', spec, '67')['sources_zh']]
        self.assertIn('https://zh.wikisource.org/wiki/漢書/卷030', final_urls)
        self.assertIn('https://www.chineseclassic.com/content/441', final_urls)

    def test_fingerprint_uses_current_source_bytes_manifest_and_actual_apparatus(self):
        spec = profile('zhuangzi')
        baseline = source_digest('zhuangzi', spec, '01')
        read_bytes = Path.read_bytes
        for target in (ROOT/'data/zhuangzi/zh/01.md', ROOT/'data/zhuangzi/manifest.json'):
            def changed_bytes(path):
                return read_bytes(path)+(b'\n' if path == target else b'')
            with self.subTest(path=target), patch.object(Path, 'read_bytes', changed_bytes):
                self.assertNotEqual(source_digest('zhuangzi', spec, '01'), baseline)
        chapters = copy.deepcopy(original.CHAPTERS)
        old = chapters[1]
        chapters[1] = (*old[:3], 'https://example.invalid/changed-chapter')
        with patch.object(original, 'CHAPTERS', chapters):
            self.assertNotEqual(source_digest('zhuangzi', spec, '01'), baseline)
        before = source_digest('zhuangzi', spec, '35')
        render = original.render_article
        def changed_note(item, manifest):
            return render(item, manifest).replace('不是失落原稿的复原', '不是已经找到的原稿')
        with patch.object(original, 'render_article', changed_note):
            self.assertNotEqual(source_digest('zhuangzi', spec, '35'), before)

    def test_new_blocks_and_changed_manifest_scope_fail_closed(self):
        spec = profile('zhuangzi')
        for slug in ('00', '68', '../guide', 'guide.md'):
            with self.subTest(slug=slug), self.assertRaises(AssertionError):
                original_article('zhuangzi', spec, slug)
        read_text = Path.read_text
        target = ROOT/'data/zhuangzi/manifest.json'
        def bad_scope(path, *args, **kwargs):
            text = read_text(path, *args, **kwargs)
            if path == target:
                data = json.loads(text)
                data['published'].pop()
                return json.dumps(data)
            return text
        with patch.object(Path, 'read_text', bad_scope), self.assertRaises(AssertionError):
            original_article('zhuangzi', spec, 'guide')
        with patch.object(original, 'prose', return_value='<ul><li>Unhandled material</li></ul>'), self.assertRaises(AssertionError):
            reading_units('An actual source-shaped argument.')

    def test_new_apparatus_wrapper_heading_or_bibliography_prose_cannot_disappear(self):
        spec = profile('zhuangzi')
        render = original.render_article
        cases = (
            ('01', '<aside class="zz-source">', '<aside class="zz-source"><div><p>New explanatory material</p></div>'),
            ('01', '<aside class="zz-source">', '<aside class="zz-source"><h2>New heading</h2>'),
            ('guide', '<li><a href="https://doi.org/', '<li><p>New bibliography prose</p><a href="https://doi.org/'),
            ('guide', '<span class="lang-zh">想读得更深</span>', '<span class="lang-zh">Changed heading needs review</span>'),
        )
        for slug, before, after in cases:
            def changed(item, manifest):
                text = render(item, manifest)
                assert before in text
                return text.replace(before, after, 1)
            with self.subTest(slug=slug, after=after), patch.object(original, 'render_article', changed):
                with self.assertRaises(AssertionError):
                    original_article('zhuangzi', spec, slug)
                with self.assertRaises(AssertionError):
                    source_digest('zhuangzi', spec, slug)

    def test_primary_only_control_upgrade_preserves_every_main_and_body(self):
        # In-memory primary controls are not an unapproved foreign-page render.
        spec = profile('zhuangzi')
        manifest = json.loads((ROOT/'data/zhuangzi/manifest.json').read_text())
        for slug in ['index', *spec['slugs']]:
            # Exercise the actual unmodified primary rendering functions, not
            # an already-upgraded on-disk page after genuine publication. The
            # independent captured body/main hashes still check saved output.
            if slug == 'index':
                text = original.render_index(manifest)
            else:
                number = 0 if slug == 'guide' else int(slug)
                item = next(a for a in manifest['items'] if a['number'] == number)
                text = original.render_article(item, manifest)
            result = upgrade_primary(text, 'zhuangzi', slug)
            self.assertEqual(upgrade_primary(result, 'zhuangzi', slug), result)
            self.assertEqual(re.findall(r'<main\b[^>]*>.*?</main>', result, re.S),
                             re.findall(r'<main\b[^>]*>.*?</main>', text, re.S))
            self.assertEqual(primary_bodies(spec, result), primary_bodies(spec, text))
            self.assertEqual(len(re.findall(r'<link\b[^>]*rel="alternate"', result)), 7)
            # Reconstruct only the four known removed alternates and strip only
            # the marked inserted controls: every other original byte must match.
            old = re.findall(r'<link\b[^>]*rel="alternate"[^>]*>', text)
            stripped = re.sub(r'<!-- MIXED SERIES LANGUAGE LINKS START -->.*?<!-- MIXED SERIES LANGUAGE LINKS END -->', '', result, flags=re.S)
            stripped = re.sub(r'<!-- MIXED SERIES ALTERNATES START -->.*?<!-- MIXED SERIES ALTERNATES END -->', '', stripped, flags=re.S)
            canonical_end = re.search(r'<link rel="canonical"[^>]*>', stripped).end()
            stripped = stripped[:canonical_end]+''.join(old)+stripped[canonical_end:]
            self.assertEqual(stripped.encode('utf-8'), text.encode('utf-8'))
        bad = text.replace('hreflang="en"', 'hreflang="unexpected"', 1)
        with self.assertRaises(AssertionError):
            upgrade_primary(bad, 'zhuangzi', slug)


if __name__ == '__main__':
    unittest.main()
