#!/usr/bin/env python3
"""Static publishing checks for the same-page Meaning Theory editions."""

import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from build_content_registry import scan_page
from build_meaning_traditional import render

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "essays" / "meaning"
PAGES = [SERIES / "index.html", *[SERIES / f"ep{i:02}.html" for i in range(1, 9)]]


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links = []
        self.buttons = []
        self.english = 0
        self.chinese = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in {"a", "link", "script"}:
            url = a.get("href") or a.get("src")
            if url:
                self.links.append(url)
        if tag == "button" and "lang-btn" in a.get("class", "").split():
            self.buttons.append(a.get("data-lang"))
        if tag == "div" and "essay-body" in a.get("class", "").split():
            self.english += "lang-en" in a["class"].split()
            self.chinese += "lang-zh" in a["class"].split()


class MeaningTests(unittest.TestCase):
    def test_pages_and_local_targets(self):
        for path in PAGES:
            with self.subTest(page=path.name):
                source = path.read_text()
                page = Page(source)
                self.assertEqual(source.count("</head>"), 1)
                self.assertEqual(set(page.buttons), {"en", "zh", "zh-hant"})
                self.assertEqual(len(page.buttons), 3)
                for link in page.links:
                    parsed = urlsplit(link)
                    if parsed.scheme or parsed.netloc or not parsed.path:
                        continue
                    target = ((ROOT if parsed.path.startswith("/") else path.parent) / unquote(parsed.path).lstrip("/")).resolve()
                    self.assertTrue(target.exists(), f"{path.name}: {link}")
                self.assertNotIn("prospect.html", source)
                self.assertIn('src="reading-mode.js"', source)
                self.assertIn(f'src="zh-hant-data/{path.stem}.js"', source)
                self.assertIn('data-search="SAE 意义论 意義論 meaning theory meaning of life"', source)
                if path.stem != "index":
                    self.assertEqual((page.english, page.chinese), (1, 1))

    def test_canonical_and_registry(self):
        for path in PAGES:
            with self.subTest(page=path.name):
                page = scan_page(ROOT, path)
                self.assertEqual(page["domain"], "sae-philosophy")
                self.assertEqual(set(page["languages"]), {"en", "zh-Hans", "zh-Hant"})
                self.assertEqual(set(page["titles"]), {"en", "zh-Hans", "zh-Hant"})
                ending = "" if path.stem == "index" else path.name
                self.assertEqual(page["canonical"], "https://nondubito.net/essays/meaning/" + ending)

    def test_traditional_dictionaries_match_current_prose(self):
        for path, expected in render().items():
            with self.subTest(dictionary=path.name):
                self.assertEqual(path.read_text(), expected)

    def test_previous_and_next(self):
        for i, path in enumerate(PAGES[1:], 1):
            source = path.read_text()
            nav = re.search(r'<div class="series-tail">(.*?)</article>', source, re.S).group(1)
            previous = "index.html" if i == 1 else f"ep{i-1:02}.html"
            following = "index.html" if i == 8 else f"ep{i+1:02}.html"
            self.assertIn(f'href="{previous}"', nav)
            self.assertIn(f'href="{following}"', nav)

    def test_search_and_sitemap(self):
        expected = {p.relative_to(ROOT).as_posix() for p in PAGES}
        for lang in ["en", "zh-hans", "zh-hant"]:
            records = json.loads((ROOT / "data" / "search" / f"{lang}.json").read_text())["records"]
            meaning = [r for r in records if r["u"].startswith("essays/meaning/")]
            self.assertEqual({r["u"] for r in meaning}, expected)
            self.assertTrue(all(r["d"] == "sae-philosophy" for r in meaning))
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = {node.text for node in ET.parse(ROOT / "sitemap.xml").findall("s:url/s:loc", ns)}
        for path in PAGES:
            self.assertIn(scan_page(ROOT, path)["canonical"], urls)

    def test_update_ledger(self):
        updates = json.loads((ROOT / "data" / "site-updates.json").read_text())["updates"]
        meaning = [entry for entry in updates if entry["url"] == "essays/meaning/index.html"]
        self.assertEqual(len(meaning), 1)
        self.assertEqual(set(meaning[0]["languages"]), {"en", "zh", "zh-hant"})
        self.assertIn(f'data-update-id="{meaning[0]["id"]}"', (ROOT / "latest.html").read_text())


if __name__ == "__main__":
    unittest.main()
