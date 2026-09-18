#!/usr/bin/env python3
"""Regression coverage for the Western-philosophy shelf and stable series URLs."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import build_content_registry as registry


ROOT = Path(__file__).resolve().parents[1]
SERIES = ("sae-republic", "sae-nicomachean", "sae-consolation", "sae-montaigne")
LANGUAGES = ("ja", "fr", "de", "es", "ko")


class WesternPhilosophyNavigationTests(unittest.TestCase):
    def test_editorial_category_preserves_series_identity(self):
        for series in SERIES:
            for page in ("index.html", "ep01.html", "fr/index.html", "fr/ep01.html"):
                path = Path("essays") / series / page
                with self.subTest(path=path):
                    self.assertEqual(registry.infer_taxonomy(path), ("sae-western", series))
                    self.assertEqual(registry.infer_domain(path), "sae-philosophy")
        self.assertEqual(
            registry.infer_taxonomy(Path("essays/sae-foundations/ep01.html")),
            ("sae-foundations", "sae-foundations"),
        )

    def test_western_hub_is_a_collection_not_an_extra_series(self):
        path = Path("essays/sae-western/index.html")
        self.assertEqual(registry.infer_taxonomy(path), ("sae-western", None))
        self.assertEqual(registry.infer_record_type(path), "collection-index")
        self.assertEqual(registry.infer_domain(path), "sae-philosophy")

    def test_library_has_one_category_with_exactly_four_series(self):
        categories = registry.parse_library_categories(ROOT / "library.html")
        self.assertEqual([category["number"] for category in categories], list(range(1, 18)))
        western = next(
            category for category in categories
            if category["href"] == "essays/sae-western/index.html"
        )
        expected = [f"essays/{series}/index.html" for series in SERIES]
        self.assertEqual(western["number"], 3)
        self.assertEqual(western["series_hrefs"], expected)
        all_cards = [href for category in categories for href in category["series_hrefs"]]
        for href in expected:
            self.assertEqual(all_cards.count(href), 1)
        library = (ROOT / "library.html").read_text(encoding="utf-8")
        shelf = re.search(r'<section class="lib-section" id="sae-western">(.*?)</section>', library, re.S).group(1)
        self.assertNotIn("中英双语", shelf)
        self.assertNotIn("Chinese and English", shelf)
        self.assertIn("小引＋5 篇正文 · 英／简／繁", shelf)
        self.assertIn("小引＋5 篇正文 · 英／簡／繁", shelf)

    def test_explore_uses_the_shelf_instead_of_a_single_series(self):
        source = (ROOT / "explore.html").read_text(encoding="utf-8")
        self.assertIn('class="shelf-link" href="essays/sae-western/index.html"', source)
        self.assertNotIn('class="shelf-link" href="essays/sae-republic/index.html"', source)
        self.assertIn('<h3 class="lang-hant">SAE西哲</h3>', source)

    def test_existing_indexes_return_to_the_new_shelf(self):
        for series in SERIES[:3]:
            with self.subTest(series=series, language="root"):
                source = (ROOT / "essays" / series / "index.html").read_text(encoding="utf-8")
                breadcrumb = re.search(r'<nav class="reading-breadcrumbs".*?</nav>', source, re.S).group()
                self.assertIn('href="../sae-western/index.html"', breadcrumb)
                self.assertIn('<span class="context-hant">SAE西哲</span>', breadcrumb)
                self.assertRegex(source, r'<a href="\.\./sae-western/index\.html" class="back-link')
                self.assertNotIn("index.html#sae-western-philosophy", source)
            for language in LANGUAGES:
                with self.subTest(series=series, language=language):
                    source = (ROOT / "essays" / series / language / "index.html").read_text(encoding="utf-8")
                    self.assertIn('href="../../sae-western/index.html?lang=en" class="back-link"', source)
                    self.assertNotRegex(source, r'class="back-link">← Non Dubito</a>')
                    self.assertNotRegex(source, r'href="\.\./\.\./\.\./index.html#sae-')


if __name__ == "__main__":
    unittest.main()
