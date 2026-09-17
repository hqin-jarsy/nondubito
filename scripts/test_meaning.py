#!/usr/bin/env python3
"""Static publishing checks for the same-page Meaning Theory editions."""

import json
import html
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from build_content_registry import scan_page
from build_meaning_traditional import render
from build_meaning_languages import LANGUAGES, LABELS, SLUGS, outputs, load_edition

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "essays" / "meaning"
PAGES = [SERIES / "index.html", *[SERIES / f"ep{i:02}.html" for i in range(1, 9)]]


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links = []
        self.buttons = []
        self.editions = []
        self.english = 0
        self.chinese = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and 'data-edition' in a:
            self.editions.append((a['data-edition'], a['href']))
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
                self.assertEqual({e[0] for e in page.editions}, set(LABELS))
                self.assertEqual(len(page.editions), 8)
                for link in page.links:
                    parsed = urlsplit(link)
                    if parsed.scheme or parsed.netloc or not parsed.path:
                        continue
                    target = ((ROOT if parsed.path.startswith("/") else path.parent) / unquote(parsed.path).lstrip("/")).resolve()
                    self.assertTrue(target.exists(), f"{path.name}: {link}")
                self.assertNotIn("prospect.html", source)
                self.assertIn('src="reading-mode.js?v=20260917-full"', source)
                self.assertIn(f'src="zh-hant-data/{path.stem}.js?v=20260917-full"', source)
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
        for lang in ["en", "zh-hans", "zh-hant", *LANGUAGES]:
            records = json.loads((ROOT / "data" / "search" / f"{lang}.json").read_text())["records"]
            meaning = [r for r in records if r["u"].startswith("essays/meaning/")]
            language_expected = expected if lang not in LANGUAGES else {f'essays/meaning/{lang}/{slug}.html' for slug in SLUGS}
            self.assertEqual({r["u"] for r in meaning}, language_expected)
            self.assertTrue(all(r["d"] == "sae-philosophy" for r in meaning))
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = {node.text for node in ET.parse(ROOT / "sitemap.xml").findall("s:url/s:loc", ns)}
        for path in PAGES + [SERIES / lang / (slug + '.html') for lang in LANGUAGES for slug in SLUGS]:
            self.assertIn(scan_page(ROOT, path)["canonical"], urls)

    def test_update_ledger(self):
        updates = json.loads((ROOT / "data" / "site-updates.json").read_text())["updates"]
        meaning = [entry for entry in updates if entry["url"] == "essays/meaning/index.html"]
        self.assertEqual(len(meaning), 1)
        self.assertEqual(set(meaning[0]["languages"]), set(LABELS))
        self.assertIn(f'data-update-id="{meaning[0]["id"]}"', (ROOT / "latest.html").read_text())

    def test_generated_editions_are_current(self):
        for path, expected in outputs().items():
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertEqual(path.read_text(), expected)

    def test_foreign_pages_and_sources(self):
        for lang in LANGUAGES:
            data = load_edition(lang)
            for slug in SLUGS:
                path = SERIES / lang / (slug + '.html')
                with self.subTest(language=lang, page=slug):
                    source = path.read_text()
                    page = Page(source)
                    self.assertEqual(len(page.editions), 8)
                    self.assertEqual({e[0] for e in page.editions}, set(LABELS))
                    self.assertEqual(source.count('<h1 '), 1 if slug == 'index' else 0)
                    self.assertEqual(source.count('<h1>'), 0 if slug == 'index' else 1)
                    self.assertIn(f'<html lang="{lang}" data-lang="{lang}">', source)
                    for code, href in page.editions:
                        self.assertEqual(Path(urlsplit(href).path).name, slug + '.html')
                    for link in page.links:
                        parsed = urlsplit(link)
                        if not parsed.scheme and not parsed.netloc and parsed.path:
                            self.assertTrue((path.parent / unquote(parsed.path)).resolve().exists(), link)
                    info = scan_page(ROOT, path)
                    self.assertEqual(info['domain'], 'sae-philosophy')
                    self.assertEqual(info['languages'], [lang])
                    if slug != 'index':
                        article = next(a for a in data['articles'] if a['slug'] == slug)
                        for section in article['sections']:
                            for paragraph in section['paragraphs']:
                                self.assertIn('<p>' + html.escape(paragraph) + '</p>', source)
                        base = (SERIES / (slug + '.html')).read_text()
                        for citation in re.findall(r'https://(?:self-as-an-end.net/papers/sae-meaning-[0-4].html|doi.org/10.5281/zenodo.\d+)', base):
                            self.assertIn(citation, source)
                        index = SLUGS.index(slug)
                        nav = re.search(r'<div class="series-nav">(.*?)</div>', source, re.S).group(1)
                        self.assertIn(f'href="{SLUGS[index-1]}.html"', nav)
                        self.assertIn(f'href="{SLUGS[index+1] if index < 8 else "index"}.html"', nav)
                    alternates = re.findall(r'rel="alternate" hreflang="([^"]+)" href="([^"]+)"', source)
                    self.assertEqual({a[0] for a in alternates}, {'x-default', 'zh-Hans', *LANGUAGES})
                    self.assertTrue(all('?' not in a[1] for a in alternates))


if __name__ == "__main__":
    unittest.main()
