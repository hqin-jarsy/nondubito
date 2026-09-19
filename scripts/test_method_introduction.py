#!/usr/bin/env python3
"""Publishing regressions for the accessible M-00E introduction."""

import html
import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

from build_content_registry import scan_page, parse_library_categories
from build_method_introduction import ROOT, PAGE, CANONICAL, SOURCE, LANGUAGES, load_editions, render
from build_search_index import extract_recent_fiction_descriptions
from check_site_updates import check as check_updates


class PageInfo(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.buttons = []
        self.bodies = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"a", "link", "script"}:
            url = attrs.get("href") or attrs.get("src")
            if url:
                self.links.append(url)
        if tag == "button" and "lang-btn" in attrs.get("class", "").split():
            self.buttons.append(attrs["data-lang"])
        if "essay-body" in attrs.get("class", "").split() and "data-reading-lang" in attrs:
            self.bodies.append((attrs["data-reading-lang"], attrs["lang"]))


class MethodIntroductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.editions = load_editions()
        cls.source = PAGE.read_text(encoding="utf-8")

    def test_render_is_reproducible(self):
        self.assertEqual(self.source, render())

    def test_all_authored_prose_is_published(self):
        for lang, edition in self.editions.items():
            with self.subTest(lang=lang):
                texts = [edition["title"], edition["subtitle"], edition["reading_note"], *edition["intro"]]
                self.assertEqual(len(edition["sections"]), 7)
                self.assertEqual(len(edition["sections"][-1]["items"]), 5)
                for section in edition["sections"]:
                    texts += [section["heading"], *section["paragraphs"], *section.get("items", []), *section.get("after", [])]
                for text in texts:
                    self.assertIn(html.escape(text), self.source)

    def test_remainder_is_introduced_early_and_carried_through_examples(self):
        # The first draft named the concept only in section six. Keep it central,
        # not confined to a late glossary or the source note.
        for lang, edition in self.editions.items():
            term = {"zh": "余项", "zh-hant": "餘項", "en": "remainder"}[lang]
            with self.subTest(lang=lang):
                self.assertIn(term, edition["subtitle"].lower())
                for section in edition["sections"][:5]:
                    self.assertIn(term, " ".join(section["paragraphs"]).lower())
                self.assertNotIn("在这里，我们才需要一个稍微专门的词", " ".join(edition["sections"][5]["paragraphs"]))

    def test_only_real_language_editions(self):
        info = PageInfo(self.source)
        self.assertEqual(set(info.buttons), set(LANGUAGES))
        self.assertEqual(len(info.buttons), 3)
        self.assertEqual(dict(info.bodies), {lang: config[0] for lang, config in LANGUAGES.items()})
        alternates = re.findall(r'hreflang="([^"]+)" href="([^"]+)"', self.source)
        self.assertEqual(set(alternates), {(code, CANONICAL) for code in ["en", "zh-Hans", "zh-Hant", "x-default"]})
        for lang in ["ja", "fr", "de", "es", "ko"]:
            self.assertFalse((PAGE.parent / lang / PAGE.name).exists())

    def test_local_targets_and_source(self):
        for filename in ["00e.html", "index.html", "00.html", "viii.html", "x.html"]:
            page = PAGE.parent / filename
            for url in PageInfo(page.read_text()).links:
                parsed = urlsplit(url)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = ((ROOT if parsed.path.startswith("/") else page.parent) / unquote(parsed.path).lstrip("/")).resolve()
                self.assertTrue(target.exists(), f"{filename}: {url}")
        self.assertEqual(self.source.count(f'href="{SOURCE}"'), 3)

    def test_primary_directory_sequence_and_feature(self):
        source = (PAGE.parent / "index.html").read_text()
        listing = re.search(r'<ul class="entry-list">(.*?)</ul>', source, re.S).group(1)
        links = re.findall(r'<a href="([^"]+)"', listing)
        self.assertEqual(links, [slug + ".html" for slug in ["0", "i", "ii", "iii", "iv", "v", "vi", "vii", "00", "00e", "viii", "ix", "x"]])
        self.assertIn('<div class="method-start">', source)
        self.assertIn('introductory essay 00E', source)
        self.assertNotIn('<div class="series-title-en lang-en">方法论系列</div>', source)

    def test_previous_next_and_layer_notes(self):
        for slug in ["00", "viii"]:
            source = (PAGE.parent / (slug + ".html")).read_text()
            nav = re.search(r'<nav class="xiyou-nav">(.*?)</nav>', source, re.S).group(1)
            self.assertIn('href="00e.html"', nav)
        for slug in ["00", "x"]:
            source = (PAGE.parent / (slug + ".html")).read_text()
            self.assertIn('class="method-reading-note lang-zh"', source)
            self.assertIn('class="method-reading-note lang-en"', source)
        for target in ["00.html", "viii.html", "index.html"]:
            self.assertIn(f'href="{target}"', self.source)

    def test_registry_and_localized_search_description(self):
        record = scan_page(ROOT, PAGE)
        self.assertEqual(record["canonical"], CANONICAL)
        self.assertEqual(record["domain"], "sae-philosophy")
        self.assertEqual(set(record["languages"]), {"en", "zh-Hans", "zh-Hant"})
        descriptions = extract_recent_fiction_descriptions(self.source)
        for lang, (code, _) in LANGUAGES.items():
            self.assertEqual(record["titles"][code], self.editions[lang]["title"])
            self.assertEqual(descriptions[code], self.editions[lang]["subtitle"])

    def test_search_indexes_and_sitemap(self):
        relative = PAGE.relative_to(ROOT).as_posix()
        for lang, (code, _) in LANGUAGES.items():
            records = json.loads((ROOT / "data" / "search" / (code.lower() + ".json")).read_text())["records"]
            matches = [record for record in records if record["u"] == relative]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]["t"], self.editions[lang]["title"])
            self.assertEqual(matches[0]["x"], self.editions[lang]["subtitle"])
        for code in ["ja", "fr", "de", "es", "ko"]:
            records = json.loads((ROOT / "data" / "search" / (code + ".json")).read_text())["records"]
            self.assertFalse(any(record["u"] == relative for record in records))
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [node.text for node in ET.parse(ROOT / "sitemap.xml").findall("s:url/s:loc", namespace)]
        self.assertEqual(urls.count(CANONICAL), 1)

    def test_update_and_library_entries(self):
        self.assertEqual(check_updates(), [])
        entries = json.loads((ROOT / "data" / "site-updates.json").read_text())["updates"]
        matching = [entry for entry in entries if entry["url"] == PAGE.relative_to(ROOT).as_posix()]
        self.assertEqual(len(matching), 1)
        self.assertEqual(set(matching[0]["languages"]), set(LANGUAGES))
        library = (ROOT / "library.html").read_text()
        self.assertIn('href="essays/method/index.html" class="series-card"', library)
        self.assertIn('12 papers + 1 introduction', library)
        self.assertEqual(library.count('href="essays/method/index.html" class="series-card"'), 1)
        catalog_links = [url for category in parse_library_categories(ROOT / "library.html") for url in category["series_hrefs"]]
        self.assertEqual(catalog_links.count("essays/method/index.html"), 1)


if __name__ == "__main__":
    unittest.main()
