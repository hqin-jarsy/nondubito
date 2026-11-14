"""Spanish completed-batch discovery and scoped search regression tests."""
import json
from pathlib import Path
import tempfile
import unittest
from hongloumeng_spanish_availability import spanish_available, PREFIX
from hongloumeng_discovery_scope import excluded, excluded_url
from refresh_hongloumeng_spanish_search import outputs
from build_content_registry import infer_record_type, infer_sequence

class SpanishDiscoveryTests(unittest.TestCase):
    def fixture(self, root):
        target=root/PREFIX; target.mkdir(parents=True)
        progress=root/'data/hongloumeng/first80-spanish/progress.json';progress.parent.mkdir(parents=True)
        progress.write_text('{"reviewed_through":5}')
        for name in ('index.html','edition.html',*(f'ch{n:03}.html' for n in range(1,7))):
            (target/name).write_text('<html lang="es"><head><title>Sueño en el pabellón rojo</title></head><body><article>Texto español.</article></body></html>')
        return target,progress
    def test_only_reviewed_batch_is_discoverable(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); self.fixture(root)
            for name in ('index.html','edition.html','ch001.html','ch005.html'):
                self.assertTrue(spanish_available(name,root)); self.assertFalse(excluded(Path(PREFIX)/name,root=root))
            for name in ('ch006.html','ch080.html','nested/index.html','ch001 2.html'):
                self.assertFalse(spanish_available(name,root)); self.assertTrue(excluded(Path(PREFIX)/name,root=root))
            self.assertFalse(excluded_url('/'+PREFIX,root=root))
            self.assertTrue(excluded_url('/'+PREFIX+'../ch001.html',root=root))
            self.assertEqual(infer_record_type(Path(PREFIX+'ch005.html')),'novel-chapter')
            self.assertEqual(infer_sequence(Path(PREFIX+'ch005.html')),5)
    def test_invalid_batch_or_alias_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); target,progress=self.fixture(root)
            progress.write_text('{"reviewed_through":6}');self.assertFalse(spanish_available('ch001.html',root))
            progress.write_text('{"reviewed_through":5}')
            (target/'ch001.html').unlink();(target/'ch001.html').symlink_to(target/'ch002.html')
            self.assertFalse(spanish_available('ch001.html',root))
    def test_navigation_preserves_older_bounded_insertions(self):
        from integrate_hongloumeng_spanish import addition, transform, reverse
        relative='classics/hongloumeng/ch001.html'
        french='<!-- FRENCH-NAV:START --><a>Français</a><!-- FRENCH-NAV:END -->'
        japanese='<!-- JAPANESE-NAV:START --><a>日本語</a><!-- JAPANESE-NAV:END -->'
        german='<!-- GERMAN-NAV:START --><a>Deutsch</a><!-- GERMAN-NAV:END -->'
        for older in (german+french+japanese, german+french, german+japanese, german, french+japanese, japanese, french, ''):
            original='<header><nav class="language-switch">Existing'+older+'</nav></header>'
            result=transform(relative,original)
            self.assertEqual(reverse(relative,result),original)
            self.assertEqual(transform(relative,result),result)
            previous=original.replace('</nav>',addition(relative)+'</nav>',1)
            self.assertEqual(transform(relative,previous),result)
            if japanese in older:
                self.assertTrue(result.endswith(japanese+'</nav></header>'))
                if french in older:
                    self.assertLess(result.index('SPANISH-NAV:START'),result.index('FRENCH-NAV:START'))
            if german in older:
                self.assertLess(result.index('SPANISH-NAV:START'),result.index('GERMAN-NAV:START'))
            elif french in older:
                self.assertLess(result.index('SPANISH-NAV:START'),result.index('FRENCH-NAV:START'))

    def test_refresh_preserves_other_records_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root);(root/'data/search').mkdir()
            m=root/'data/search-index.json'; c=root/'data/search/es.json'
            m.write_text(json.dumps({'record_count':10,'languages':{'es':{'count':1},'en':{'count':9}}}))
            old={'u':'essays/other/es/index.html','t':'Unchanged'}
            c.write_text(json.dumps({'language':'es','records':[old]}))
            result=outputs(root);self.assertEqual(json.loads(result[m])['record_count'],17)
            self.assertEqual(json.loads(result[c])['records'][0],old)
            self.assertEqual(len(json.loads(result[c])['records']),8)
            for p,s in result.items():p.write_text(s)
            self.assertEqual(outputs(root),result)
if __name__=='__main__':unittest.main()
