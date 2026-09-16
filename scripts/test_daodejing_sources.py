#!/usr/bin/env python3
"""Read-only regression checks for the adopted Daodejing chapter texts.

Run with: python3 -B scripts/test_daodejing_sources.py
No external checkout, network service, or generated fixture files are needed.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import urlsplit

import build_daodejing_sources as build


EDITIONS = ("", "ja", "fr", "de", "es", "ko")
LANGUAGES = {"zh", "zh-hant", "en", "ja", "fr", "de", "es", "ko"}
TEXT_DIGEST = "ac13f626010f1b83bf94f4fa331ec5256426abdb313c5b71d046eac65307e12a"


class Node:
    def __init__(self, tag, attrs, parent, start):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.start = start
        self.end = None
        self.children = []

    def has_class(self, name):
        return name in self.attrs.get("class", "").split()

    def text(self):
        return "".join(child if isinstance(child, str) else child.text() for child in self.children)

    def descendants(self, tag=None):
        for child in self.children:
            if isinstance(child, Node):
                if tag is None or child.tag == tag:
                    yield child
                yield from child.descendants(tag)


class Page(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node("document", [], None, (1, 0))
        self.stack = [self.root]
        self.nodes = []
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.stack[-1], self.getpos())
        self.stack[-1].children.append(node)
        self.nodes.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                self.stack[index].end = self.getpos()
                del self.stack[index:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


class DaodejingSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chapters, cls.ui = build.load_data()
        cls.by_number = {chapter["number"]: chapter for chapter in cls.chapters}

    def test_data_inventory_and_provenance(self):
        self.assertEqual([chapter["number"] for chapter in self.chapters], list(range(1, 82)))
        self.assertEqual(set(self.ui), LANGUAGES)
        paragraphs = []
        for chapter in self.chapters:
            number = chapter["number"]
            with self.subTest(chapter=number):
                paper = (number - 1) // 9 + 1
                self.assertEqual(chapter["paper"], paper)
                self.assertEqual(chapter["source_url"], f"https://self-as-an-end.net/papers/sae-daodejing-{paper}.html")
                self.assertEqual(len(chapter["paragraphs"]), 4 if number == 28 else 1)
                for paragraph in chapter["paragraphs"]:
                    self.assertEqual(paragraph, paragraph.strip())
                    self.assertNotRegex(paragraph, r"[<>]|&(?:[a-zA-Z]+|#\w+);")
                paragraphs.extend(chapter["paragraphs"])
        self.assertEqual(len(paragraphs), 84)
        # The checksum freezes the audited author-adopted text, not an alleged
        # definitive transcription of either excavated manuscript.
        self.assertEqual(hashlib.sha256("\n".join(paragraphs).encode("utf-8")).hexdigest(), TEXT_DIGEST)

    def test_version_sensitive_readings_are_not_silently_normalized(self):
        expected = {
            1: "无，名万物之始也；有，名万物之母也。",
            14: "听之而弗闻，名之曰希。",
            25: "寂兮寥兮，独立而不改，可以为天地母。",
            42: "故人之所教，夕议而教人。",
            67: "天下皆谓我大，大而不肖，夫唯不肖故能大。",
            80: "使民重死而远徙。",
            81: "人之道，为而弗争。",
        }
        for number, reading in expected.items():
            with self.subTest(chapter=number):
                self.assertIn(reading, "".join(self.by_number[number]["paragraphs"]))
        self.assertNotIn("听之而弗，闻名之曰希", "".join(self.by_number[14]["paragraphs"]))
        self.assertNotIn("重死而不远徙", "".join(self.by_number[80]["paragraphs"]))

    def test_all_486_pages_have_complete_source_text_in_the_correct_place(self):
        count = 0
        for edition in EDITIONS:
            folder = build.SERIES / edition
            self.assertEqual(len(list(folder.glob("ch[0-9][0-9].html"))), 81)
            for chapter in self.chapters:
                path = folder / f"ch{chapter['number']:02d}.html"
                with self.subTest(path=str(path.relative_to(build.ROOT))):
                    source = path.read_text(encoding="utf-8")
                    page = Page(source)
                    self.assertEqual(source.count("<!-- daodejing-source:start -->"), 1)
                    self.assertEqual(source.count("<!-- daodejing-source:end -->"), 1)
                    sections = [node for node in page.nodes if node.has_class("ddj-source")]
                    self.assertEqual(len(sections), 1)
                    section = sections[0]
                    self.assertEqual(section.tag, "section")
                    self.assertEqual(section.attrs.get("data-ddj-chapter"), str(chapter["number"]))
                    self.assertEqual(section.parent.tag, "article")
                    header = next(node for node in page.nodes if node.has_class("essay-header"))
                    body = next(node for node in page.nodes if node.has_class("essay-body"))
                    self.assertIs(header.parent, section.parent)
                    self.assertIs(body.parent, section.parent)
                    self.assertIsNotNone(header.end)
                    self.assertIsNotNone(section.end)
                    self.assertLess(header.end, section.start)
                    self.assertLess(section.end, body.start)

                    quotes = list(section.descendants("blockquote"))
                    self.assertEqual(len(quotes), 1)
                    quote = quotes[0]
                    self.assertTrue(quote.has_class("ddj-source-text"))
                    self.assertEqual(quote.attrs.get("lang"), "lzh")
                    self.assertEqual(quote.attrs.get("translate"), "no")
                    self.assertEqual(quote.attrs.get("cite"), chapter["source_url"])
                    self.assertEqual([node.text() for node in quote.descendants("p")], chapter["paragraphs"])
                    details = list(section.descendants("details"))
                    self.assertEqual(len(details), 1)
                    self.assertNotIn(quote, list(details[0].descendants()))
                    self.assertIn(chapter["source_url"], [node.attrs.get("href") for node in details[0].descendants("a")])

                    ids = Counter(node.attrs["id"] for node in page.nodes if "id" in node.attrs)
                    self.assertEqual(ids["ddj-source-title"], 1)
                    self.assertEqual(section.attrs.get("aria-labelledby"), "ddj-source-title")
                    self.assertEqual([node.attrs.get("id") for node in section.descendants("h2")], ["ddj-source-title"])
                    css = [node for node in page.nodes if node.tag == "link" and urlsplit(node.attrs.get("href", "")).path.endswith("chapter-source.css")]
                    self.assertEqual(len(css), 1)
                    self.assertIn("stylesheet", css[0].attrs.get("rel", "").split())
                    target = (path.parent / urlsplit(css[0].attrs["href"]).path).resolve()
                    self.assertEqual(target, (build.SERIES / "chapter-source.css").resolve())
                    self.assertTrue(target.is_file())
                count += 1
        self.assertEqual(count, 486)

    def test_all_traditional_readers_skip_the_whole_source_section(self):
        readers = sorted((build.SERIES / "zh-hant-data").glob("ch[0-9][0-9].js"))
        self.assertEqual(len(readers), 81)
        for path in readers:
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")
                guard = re.search(r"parent\.closest\((['\"])(.*?)\1\)\)\s*continue;", source)
                self.assertIsNotNone(guard)
                selectors = [selector.strip() for selector in guard.group(2).split(",")]
                self.assertEqual(selectors.count(".ddj-source"), 1)
                self.assertTrue({".lang-en", "script", "style"}.issubset(selectors))
                self.assertLess(guard.start(), source.index("if (!originals.has(node))"))
                self.assertEqual(build.update_guard(source), source)

    def test_introductions_and_indexes_do_not_receive_chapter_blocks(self):
        for edition in EDITIONS:
            for name in ("index.html", "daoyan.html"):
                path = build.SERIES / edition / name
                with self.subTest(path=str(path.relative_to(build.ROOT))):
                    source = path.read_text(encoding="utf-8")
                    self.assertNotIn("<!-- daodejing-source:", source)
                    self.assertFalse(any(node.has_class("ddj-source") for node in Page(source).nodes))
                    self.assertNotIn("chapter-source.css", source)

    def test_page_insertion_and_replacement_are_idempotent(self):
        original = '<html><head><title>Keep title</title></head><body><article><header class="essay-header"><h1>Keep heading</h1></header><div class="essay-body lang-zh"><p>Keep prose &amp; punctuation.</p></div></article></body></html>'
        for edition in EDITIONS:
            with self.subTest(edition=edition):
                once = build.update_page(original, self.by_number[28], self.ui, edition)
                self.assertEqual(build.update_page(once, self.by_number[28], self.ui, edition), once)
                self.assertEqual(once[once.index('<div class="essay-body'):], original[original.index('<div class="essay-body'):])
                replacement = build.update_page(once, self.by_number[1], self.ui, edition)
                self.assertEqual(build.update_page(replacement, self.by_number[1], self.ui, edition), replacement)
                self.assertEqual(replacement.count("<!-- daodejing-source:start -->"), 1)
                section = next(node for node in Page(replacement).nodes if node.has_class("ddj-source"))
                quote = next(section.descendants("blockquote"))
                self.assertEqual([node.text() for node in quote.descendants("p")], self.by_number[1]["paragraphs"])

    def test_broken_or_duplicate_managed_markers_are_rejected(self):
        start = "<!-- daodejing-source:start -->"
        end = "<!-- daodejing-source:end -->"
        for broken in (start, end, end + start, start + start + end, start + end + end, start + end + start + end):
            with self.subTest(markers=broken), self.assertRaises(ValueError):
                build.update_page(f"<html><head></head><body>{broken}</body></html>", self.by_number[1], self.ui, "")

    def test_guard_update_is_narrow_idempotent_and_rejects_unknown_templates(self):
        old = ".lang-en, .lang-card, .lang-toggle, .footer-langs, script, style"
        fixture = "var untouched = 1;\nif (parent.closest('" + old + "')) continue;\nvar alsoUntouched = 2;"
        once = build.update_guard(fixture)
        self.assertEqual(once, fixture.replace(old, old + ", .ddj-source"))
        self.assertEqual(build.update_guard(once), once)
        for unknown in ("no known walker here", fixture + fixture):
            with self.subTest(source=unknown), self.assertRaises(ValueError):
                build.update_guard(unknown)

    def test_loader_rejects_wrong_chapter_order_source_and_unprocessed_text(self):
        original = json.loads(build.DATA.read_text(encoding="utf-8"))
        mutations = (
            lambda data: data["chapters"].reverse(),
            lambda data: data["chapters"][0].update(paper=2),
            lambda data: data["chapters"][0].update(source_url="https://example.com/wrong-source"),
            lambda data: data["chapters"][0].update(paragraphs=[]),
            lambda data: data["chapters"][0].update(paragraphs=[" "]),
            lambda data: data["chapters"][0].update(paragraphs=["> 道可道也"]),
            lambda data: data["chapters"][0].update(paragraphs=["<p>道可道也</p>"]),
        )
        for index, mutate in enumerate(mutations):
            changed = copy.deepcopy(original)
            mutate(changed)
            fake = SimpleNamespace(read_text=lambda **kwargs: json.dumps(changed, ensure_ascii=False))
            with self.subTest(mutation=index), patch.object(build, "DATA", fake), self.assertRaises(ValueError):
                build.load_data()


if __name__ == "__main__":
    unittest.main()
