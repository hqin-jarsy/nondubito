#!/usr/bin/env python3
"""Keep legacy and newly generated library cards on one typographic scale."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LibraryCards(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.cards = []
        self.current = None
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        classes = set(attributes.get('class', '').split())
        if tag == 'a' and 'series-card' in classes:
            self.current = {'href': attributes.get('href'), 'descriptions': []}
        if self.current is not None and any(c.startswith('series-card-desc') for c in classes):
            self.current['descriptions'].append(classes)

    def handle_endtag(self, tag):
        if tag == 'a' and self.current is not None:
            self.cards.append(self.current)
            self.current = None


class LibraryTypographyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / 'library.html').read_text(encoding='utf-8')
        # These card rules are top-level; media queries do not redefine them.
        cls.rules = []
        css = '\n'.join(re.findall(r'<style>(.*?)</style>', cls.source, re.S))
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        for selectors, declarations in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
            cls.rules.append((set(s.strip() for s in selectors.split(',')),
                              dict((k.strip(), v.strip()) for k, v in
                                   (d.split(':', 1) for d in declarations.split(';') if ':' in d))))
        cls.cards = LibraryCards(cls.source).cards

    def shared_rule(self, *selectors):
        matches = [d for s, d in self.rules if set(selectors) <= s]
        self.assertEqual(len(matches), 1, selectors)
        return matches[0]

    def test_chinese_description_aliases_share_all_declarations(self):
        rule = self.shared_rule('.series-card-desc-zh', '.series-card-desc.lang-zh',
                                '.series-card-desc.lang-hant')
        self.assertEqual(rule['font-family'], 'var(--reading-cjk, var(--cjk)), serif')
        self.assertEqual(rule['font-size'], '0.82rem')
        self.assertEqual(rule['line-height'], '1.65')
        self.assertEqual(rule['margin-bottom'], 'auto')

    def test_english_description_aliases_share_all_declarations(self):
        rule = self.shared_rule('.series-card-desc-en', '.series-card-desc.lang-en')
        self.assertEqual(rule['font-family'], 'var(--sans)')
        self.assertEqual(rule['font-size'], '0.8rem')
        self.assertEqual(rule['line-height'], '1.6')
        self.assertEqual(rule['margin-bottom'], 'auto')

    def test_all_card_descriptions_have_a_supported_role_and_language(self):
        self.assertGreater(len(self.cards), 350)
        for card in self.cards:
            with self.subTest(card=card['href']):
                self.assertTrue(card['descriptions'])
                for classes in card['descriptions']:
                    self.assertTrue(classes & {'lang-en', 'lang-zh', 'lang-hant', 'cl-hant'})
                    self.assertTrue(classes & {'series-card-desc-en', 'series-card-desc-zh',
                                               'series-card-desc'})

    def test_recent_generic_cards_are_covered_without_rewriting_their_copy(self):
        generic = {c['href'] for c in self.cards if
                   any('series-card-desc' in d for d in c['descriptions'])}
        self.assertTrue({'essays/language-writing/index.html', 'essays/marriage/index.html',
                         'essays/interstate/index.html', 'essays/cooperation-histories/index.html',
                         'essays/accountability/index.html', 'essays/long-consensus/index.html',
                         'essays/state-transitions/index.html'} <= generic)

    def test_chinese_titles_use_the_active_script_font(self):
        for selector in ('.library-hero-title .zh', '.lib-section-name .zh',
                         '.series-card-title-zh'):
            with self.subTest(selector=selector):
                self.assertEqual(self.shared_rule(selector)['font-family'],
                                 'var(--reading-cjk, var(--cjk)), serif')
        shell = (ROOT / 'site-shell.css').read_text(encoding='utf-8')
        self.assertRegex(shell, r'\[data-lang="zh-hant"\]\s*\{\s*--reading-cjk:\s*var\(--tc\)')
        self.assertRegex(shell, r'\[data-lang="zh"\]\s*\{\s*--reading-cjk:\s*var\(--cjk\)')

    def test_both_chinese_font_families_are_requested(self):
        self.assertIn('family=Noto+Serif+SC:wght@400;500;600', self.source)
        self.assertIn('family=Noto+Serif+TC:wght@400;500;600', self.source)

    def test_flagship_scale_supports_both_card_formats(self):
        rule = self.shared_rule('.series-card-flagship .series-card-desc-zh',
                                '.series-card-flagship .series-card-desc-en',
                                '.series-card-flagship .series-card-desc')
        self.assertEqual(rule['font-size'], '0.9rem')
        self.assertEqual(rule['max-width'], '720px')

    def test_english_mode_keeps_its_sole_title_hierarchy(self):
        self.assertEqual(self.shared_rule('[data-lang="en"] .library-hero-title .zh',
                                         '[data-lang="en"] .lib-section-name .zh',
                                         '[data-lang="en"] .series-card-title-zh')['display'], 'none')
        self.assertEqual(self.shared_rule('[data-lang="en"] .series-card-title-en')['font-size'],
                         '1.05rem')


if __name__ == '__main__':
    unittest.main()
