"""Workspace-only tests: no repository import, reads or writes required."""
import unittest
from pathlib import Path
from reader_supplements import (START, END, parent_spec, parent_backlink,
                                parent_discovery_paths, is_standalone,
                                render_parent_extensions)


class Converter:
    def convert(self, text):
        return text.replace('论', '論').replace('扩', '擴')


class Supplements(unittest.TestCase):
    def setUp(self):
        self.child = dict(slug='political-economy-choices', count=3,
                          parent=['essays/political-economy/theory/index.html', '政治经济学', 'Political Economy'],
                          deck_zh='三篇延伸专论', deck_en='Three further essays')
        self.items = [dict(slug=f'ep{i:02d}', title_zh=f'专论{i}', title_en=f'Essay {i}') for i in range(1, 4)]
        self.source = '<main class="lw-wrap"><section>OLD PROSE &amp; CARDS</section><aside class="lw-related">OLD LINKS</aside></main>'

    def render(self, source, parent=None):
        return render_parent_extensions(source, parent or self.child['parent'][0],
                                        series=[self.child], item_loader=lambda _: self.items,
                                        converter=Converter())

    def test_rendering_and_relative_depths(self):
        rendered = self.render(self.source)
        self.assertIn('href="../../political-economy-choices/ep01.html?lang=en"', rendered)
        self.assertEqual(rendered.count('<a href='), 9)
        for css, mode in (('en', 'en'), ('zh', 'zh'), ('hant', 'zh-hant')):
            self.assertIn('reader-extensions lang-' + css, rendered)
            self.assertIn('ep03.html?lang=' + mode, rendered)
            self.assertIn(f'[data-lang="{mode}"] aside.reader-extensions.lang-{css}' + '{display:block!important}', rendered)
        self.assertIn('aside.reader-extensions{display:none!important}', rendered)
        for foreign in ('de', 'fr', 'es', 'ja', 'ko'):
            self.assertNotIn(f'[data-lang="{foreign}"]', rendered)
        self.assertNotIn('series-card', rendered)
        self.assertNotIn('lw-card', rendered)
        backlink = parent_backlink(self.child, Converter())
        self.assertIn('href="../political-economy/theory/index.html?lang=en"', backlink)
        self.assertIn('data-edition-zh-hant="../political-economy/theory/index.html?lang=zh-hant"', backlink)

    def test_idempotence_and_outside_bytes(self):
        rendered = self.render(self.source)
        self.assertEqual(self.render(rendered), rendered)
        before, rest = rendered.split(START)
        _, after = rest.split(END)
        self.assertEqual(before + after, self.source)

    def test_relation_css_and_depth(self):
        self.child['slug'] = 'positive-sum'
        self.child['parent'][0] = 'essays/relation/index.html'
        rendered = self.render(self.source.replace('lw-wrap', 'rel-wrap').replace('lw-related', 'rel-related'))
        self.assertIn('class="rel-related reader-extensions lang-en"', rendered)
        self.assertIn('href="../positive-sum/ep03.html?lang=zh-hant"', rendered)
        self.assertIn('href="../relation/index.html?lang=en"', parent_backlink(self.child, Converter()))

    def test_scope_and_normal_series(self):
        self.assertFalse(is_standalone(self.child))
        self.assertTrue(is_standalone(dict(slug='own-faith')))
        self.assertEqual(self.render(self.source, 'essays/unrelated/index.html'), self.source)
        self.assertEqual(parent_discovery_paths(dict(slug='own-faith'), Path('/not-used')), [])

    def test_bad_metadata_and_markers_fail_closed(self):
        for path in ('/essays/x/index.html', 'essays/../x/index.html', 'essays/x/index.html?lang=en'):
            with self.assertRaises(AssertionError):
                parent_spec(dict(parent=[path, '中', 'English']))
        with self.assertRaises(AssertionError):
            self.render(self.source + START)


if __name__ == '__main__':
    unittest.main(verbosity=2)
