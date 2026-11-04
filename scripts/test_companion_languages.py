#!/usr/bin/env python3
"""Read-only regression checks for append-only language companions.

Run from any directory with Python's standard library only:
    python3 /path/to/nondubito/scripts/test_companion_languages.py

Add a sealed companion to COMPANIONS only after its pages and preservation
receipt have been published locally. Merely defining an optional layout below
does not read that companion's files or require its uncommitted sources.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import unittest
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from companion_languages import route_snapshot, upgrade_companion_primary
from full_series_languages import (
    LABELS, ROOT, load_language, primary_bodies, profile, render,
)
from prepare_original_series_review import prepare
from publish_companion_languages import render as render_connections
from web_analytics import Document, issue as analytics_issue


COMPANIONS = ("method-companion",)
FOREIGN = ("de", "fr", "es", "ja", "ko")
LAYOUTS = {
    "method-companion": {
        "slug": "00e", "units": 60, "headings": 7, "items": 5,
        "quotes": 0, "old_count": 12,
        "old_slugs": ("0", "00", "i", "ii", "iii", "iv", "v", "vi",
                      "vii", "viii", "ix", "x"),
        "source": "https://self-as-an-end.net/papers/sae-methodology-00e.html",
    },
    "foundations-companion": {
        "slug": "remainder-and-subject", "units": 19, "headings": 5,
        "items": 0, "quotes": 1, "old_count": 15,
        "old_slugs": tuple(f"ep{i:02d}" for i in range(1, 16)),
        "source": ("https://nondubito.net/essays/sae-foundations/"
                   "remainder-and-subject.html?lang=zh"),
    },
}


@dataclass
class Node:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def text(self):
        return "".join(child.text() if isinstance(child, Node) else child
                       for child in self.children)

    def has_class(self, name):
        return name in self.attrs.get("class", "").split()


class Parsed(HTMLParser):
    """Enough HTML structure to assert actual nodes, not escaped substrings."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, dict(attrs)))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)

    def nodes(self, tag=None, css=None):
        return [n for n in self.root.walk()
                if (tag is None or n.tag == tag)
                and (css is None or n.has_class(css))]


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes)
                          else value.encode("utf-8")).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def plain_markdown(value):
    """Independent text expectation for the small supported markup subset."""
    value = re.sub(r"\[([^\]]+)\]\(https://[^\s)]+\)", r"\1", value)
    return value.replace("**", "").replace("*", "")


def source_kind(value):
    if value.startswith("## "):
        return "h2", value[3:]
    if value.startswith("> "):
        return "blockquote", value[2:]
    if re.match(r"[1-5]\. ", value):
        return "li", value[3:]
    return "p", value


class CompanionLanguages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {}
        for series in COMPANIONS:
            spec = profile(series)
            layout = LAYOUTS[series]
            base = ROOT / "data" / series / "multilingual"
            source_path = base.parent / (layout["slug"] + ".json")
            preservation_path = base / "preservation.json"
            receipt = read_json(preservation_path)
            # Pure render calls must not write the original pages, data, seals,
            # old routes or Hant dictionary as a side effect of checking them.
            watched = {source_path, preservation_path}
            watched.update(ROOT / p for group in receipt["existing_route"].values()
                           for p in group)
            watched.add(ROOT / spec["directory"] / (layout["slug"] + ".html"))
            before = {p: digest(p.read_bytes()) for p in watched}
            pages = render(series)
            connections = render_connections(series)
            cls.cases[series] = {
                "spec": spec, "layout": layout, "base": base,
                "source_path": source_path, "source": read_json(source_path),
                "receipt": receipt, "pages": pages,
                "connections": connections, "before": before,
            }

    def test_append_only_renders_five_articles_and_preserves_native_indexes(self):
        for series, case in self.cases.items():
            with self.subTest(series=series):
                spec, layout = case["spec"], case["layout"]
                self.assertTrue(spec["append_only"])
                self.assertEqual(spec["languages"], list(FOREIGN))
                self.assertEqual(spec["slugs"], [layout["slug"]])
                directory = ROOT / spec["directory"]
                expected = {directory / lang / (layout["slug"] + ".html")
                            for lang in FOREIGN}
                self.assertEqual(set(case["pages"]), expected)
                self.assertEqual(len(case["pages"]), 5)
                self.assertFalse(any(p.name == "index.html" for p in case["pages"]))
                for lang in FOREIGN:
                    path = directory / lang / "index.html"
                    connected = case["connections"][path]
                    marker = "COMPANION " + series.upper()
                    self.assertEqual(connected.count(f"<!-- {marker} START -->"), 1)
                    self.assertEqual(connected.count(f"<!-- {marker} END -->"), 1)
                    self.assertIn(f'href="{layout["slug"]}.html"', connected)
                    _, data = load_language(series, lang)
                    headings = Parsed(connected).nodes("h1")
                    self.assertEqual(len(headings), 1)
                    self.assertEqual(headings[0].text(), data["series"]["title"])

    def test_actual_html_preserves_every_source_unit_and_block_type(self):
        for series, case in self.cases.items():
            spec, layout = case["spec"], case["layout"]
            source = case["source"]["body_zh"]
            self.assertEqual(len(source), layout["units"])
            for lang in FOREIGN:
                with self.subTest(series=series, language=lang):
                    _, data = load_language(series, lang)
                    article = data["articles"][0]
                    self.assertEqual(len(article["body"]), layout["units"])
                    self.assertEqual(len(article["coverage"]), layout["units"])
                    self.assertTrue(all(isinstance(p, str) and p.strip()
                                        for p in article["coverage"]))
                    path = ROOT / spec["directory"] / lang / (layout["slug"] + ".html")
                    bodies = Parsed(case["pages"][path]).nodes("div", "essay-body")
                    self.assertEqual(len(bodies), 1)
                    body = bodies[0]
                    self.assertEqual(body.attrs.get("lang"), lang)
                    actual = []
                    for node in body.children:
                        if not isinstance(node, Node):
                            self.assertFalse(node.strip())
                            continue
                        if node.tag == "ol":
                            items = [n for n in node.children if isinstance(n, Node)]
                            self.assertTrue(all(n.tag == "li" for n in items))
                            actual.extend(items)
                        else:
                            actual.append(node)
                    self.assertEqual(len(actual), layout["units"])
                    for index, (original, rewritten, node) in enumerate(
                            zip(source, article["body"], actual)):
                        self.assertEqual(source_kind(original)[0], source_kind(rewritten)[0],
                                         (series, lang, index))
                        tag, text = source_kind(rewritten)
                        self.assertEqual(node.tag, tag, (series, lang, index))
                        self.assertEqual(node.text(), plain_markdown(text),
                                         (series, lang, index))
                    counts = {tag: sum(n.tag == tag for n in actual)
                              for tag in ("h2", "p", "blockquote", "li")}
                    self.assertEqual(counts["h2"], layout["headings"])
                    self.assertEqual(counts["blockquote"], layout["quotes"])
                    self.assertEqual(counts["li"], layout["items"])
                    self.assertEqual(counts["p"], layout["units"] - layout["headings"]
                                     - layout["quotes"] - layout["items"])
                    lists = [n for n in body.walk() if n.tag == "ol"]
                    self.assertEqual(len(lists), 1 if layout["items"] else 0)
                    if layout["items"]:
                        numbered = [p[:3] for p in article["body"]
                                    if re.match(r"[1-5]\. ", p)]
                        self.assertEqual(numbered, [f"{i}. " for i in range(1, 6)])
                    if series == "foundations-companion":
                        dd_nodes = [n for n in body.walk() if n.tag == "strong"]
                        self.assertEqual([n.text() for n in dd_nodes],
                                         ["13DD", "14DD", "15DD", "16DD"])

    def test_sources_three_primary_modes_and_preservation_receipts(self):
        for series, case in self.cases.items():
            with self.subTest(series=series):
                spec, layout = case["spec"], case["layout"]
                self.assertEqual(spec["source"], layout["source"])
                self.assertEqual(case["source"]["source_url"], layout["source"])
                self.assertEqual(digest(case["source_path"].read_bytes()),
                                 case["receipt"]["source_data"][layout["slug"]])
                path = ROOT / spec["directory"] / (layout["slug"] + ".html")
                text = path.read_text(encoding="utf-8")
                fragments = primary_bodies(spec, text)
                self.assertEqual(digest(fragments),
                                 case["receipt"]["primary_bodies"][layout["slug"]])
                self.assertEqual(digest(primary_bodies(spec, upgrade_companion_primary(text, series))),
                                 digest(fragments))
                primary_nodes = (Parsed(text).nodes("article", "bridge-body")
                                 if series == "foundations-companion"
                                 else Parsed(text).nodes("div", "essay-body"))
                self.assertEqual(len(primary_nodes), 3)
                self.assertEqual(route_snapshot(series), case["receipt"]["existing_route"])
                if series == "method-companion":
                    for code in ("en", "zh", "zh-hant"):
                        source = ROOT / "data/method-introduction" / (code + ".json")
                        relative = source.relative_to(ROOT).as_posix()
                        self.assertEqual(digest(source.read_bytes()),
                                         case["receipt"]["existing_route"]["primary_sources"][relative])
                    raw = read_json(ROOT / "data/method-introduction/zh.json")
                    units = list(raw["intro"])
                    for section in raw["sections"]:
                        units.extend(["## " + section["heading"], *section["paragraphs"]])
                        units.extend(f"{i}. {item}" for i, item in
                                     enumerate(section.get("items", []), 1))
                        units.extend(section.get("after", []))
                    self.assertEqual(units, case["source"]["body_zh"])
                    self.assertEqual(raw["reading_note"], case["source"]["source_note_zh"])
                    info = case["source"]["source_input"]
                    self.assertEqual(digest((ROOT / info["path"]).read_bytes()), info["sha256"])
                else:
                    chinese = re.search(r'<article class="bridge-body lang-zh">(.*?)</article>',
                                        text, re.S)
                    self.assertIsNotNone(chinese)
                    self.assertEqual(digest(chinese[1]),
                                     case["source"]["source_input"]["chinese_body_sha256"])
                # prepare() checks independent reports, applied local corrections,
                # current language hashes, and both preserved content snapshots.
                # A tracked receipt is mandatory, so it never needs a Git command.
                prepared = prepare(series)
                self.assertNotIn(case["base"] / "preservation.json", prepared)
                publication_path = case["base"] / "publication.json"
                self.assertEqual(prepared[publication_path], publication_path.read_text())
                publication = read_json(publication_path)
                self.assertEqual(publication["new_article_editions"], 5)
                self.assertEqual(publication["source_units"], [layout["units"]])
                self.assertEqual(publication["unresolved"], [])
                for watched, before in case["before"].items():
                    self.assertEqual(digest(watched.read_bytes()), before, watched)

    def test_canonical_hreflang_eight_language_switches_and_source_notes(self):
        for series, case in self.cases.items():
            spec, layout = case["spec"], case["layout"]
            base_url = "https://nondubito.net/" + spec["directory"] + "/"
            expected_alts = {"x-default": base_url + layout["slug"] + ".html",
                             "zh-Hans": base_url + layout["slug"] + ".html"}
            expected_alts.update({lang: base_url + lang + "/" + layout["slug"] + ".html"
                                  for lang in FOREIGN})
            primary_path = ROOT / spec["directory"] / (layout["slug"] + ".html")
            primary = Parsed(primary_path.read_text())
            toggles = primary.nodes("div", "lang-toggle")
            self.assertEqual(len(toggles), 1)
            controls = [n for n in toggles[0].walk() if n.tag in ("a", "button")]
            self.assertEqual(len(controls), 8)
            modes = {n.attrs.get("data-lang", n.attrs.get("data-set-language"))
                     for n in controls if n.tag == "button"}
            self.assertEqual(modes, {"en", "zh", "zh-hant"})
            for lang in FOREIGN:
                self.assertEqual(sum(n.attrs.get("href") == f'{lang}/{layout["slug"]}.html'
                                     for n in controls), 1)
            primary_alts = [n for n in primary.nodes("link")
                            if n.attrs.get("rel") == "alternate"]
            self.assertEqual(len(primary_alts), len(expected_alts))
            self.assertEqual({n.attrs["hreflang"]: n.attrs["href"] for n in primary_alts},
                             expected_alts)
            canonical = [n.attrs["href"] for n in primary.nodes("link")
                         if n.attrs.get("rel") == "canonical"]
            self.assertEqual(canonical, [base_url + layout["slug"] + ".html"])
            for lang in FOREIGN:
                with self.subTest(series=series, language=lang):
                    _, data = load_language(series, lang)
                    article = data["articles"][0]
                    path = ROOT / spec["directory"] / lang / (layout["slug"] + ".html")
                    doc = Parsed(case["pages"][path])
                    canonical = [n.attrs["href"] for n in doc.nodes("link")
                                 if n.attrs.get("rel") == "canonical"]
                    self.assertEqual(canonical, [base_url + lang + "/" + layout["slug"] + ".html"])
                    alts = [n for n in doc.nodes("link") if n.attrs.get("rel") == "alternate"]
                    self.assertEqual(len(alts), len(expected_alts))
                    self.assertEqual({n.attrs["hreflang"]: n.attrs["href"] for n in alts}, expected_alts)
                    # The legacy primary is one canonical with three reading
                    # modes: do not invent separate EN/Hant canonical URLs.
                    self.assertFalse(any("?lang=" in n.attrs["href"] for n in alts))
                    menus = doc.nodes("div", "site-shell-language-options")
                    self.assertEqual(len(menus), 1)
                    anchors = [n for n in menus[0].walk() if n.tag == "a"]
                    self.assertEqual(len(anchors), 8)
                    self.assertEqual(sum(n.attrs.get("aria-current") == "page" for n in anchors), 1)
                    for code, label in LABELS.items():
                        href = (f'../{layout["slug"]}.html?lang={code}'
                                if code in ("en", "zh", "zh-hant")
                                else f'../{code}/{layout["slug"]}.html')
                        matching = [n for n in anchors if n.attrs.get("href") == href]
                        self.assertEqual(len(matching), 1, (series, lang, code))
                        self.assertEqual(matching[0].text(), label)
                        if code == lang:
                            self.assertEqual(matching[0].attrs.get("aria-current"), "page")
                    sources = doc.nodes("details", "lw-sources")
                    self.assertEqual(len(sources), 1)
                    paragraphs = [n for n in sources[0].children
                                  if isinstance(n, Node) and n.tag == "p"]
                    note = article.get("source_note", data["series"]["source_note"])
                    expected_notes = re.split(r"\n\s*\n", note.strip())
                    self.assertEqual([n.text() for n in paragraphs[:-1]],
                                     [plain_markdown(p) for p in expected_notes])
                    source_links = [n for n in paragraphs[-1].walk() if n.tag == "a"]
                    self.assertEqual(len(source_links), 1)
                    self.assertEqual(source_links[0].attrs["href"], layout["source"])
                    self.assertEqual(source_links[0].text(), data["ui"]["paper"] + " ↗")
                    structured = [n for n in doc.nodes("script")
                                  if n.attrs.get("type") == "application/ld+json"]
                    self.assertEqual(len(structured), 1)
                    schema = json.loads(structured[0].text())
                    self.assertEqual(schema["citation"], layout["source"])
                    self.assertEqual(schema["inLanguage"], lang)
                    self.assertEqual(schema["translationOfWork"]["url"],
                                     base_url + layout["slug"] + ".html")
                    self.assertEqual(schema["isPartOf"]["url"], base_url + lang + "/")
                    self.assertNotIn("→", data["ui"]["read"])
                    self.assertNotIn("EN /", data["ui"]["map"])

    def test_old_routes_and_method_navigation_remain_connected(self):
        for series, case in self.cases.items():
            spec, layout = case["spec"], case["layout"]
            directory = ROOT / spec["directory"]
            old_files = case["receipt"]["existing_route"]["old_native_files"]
            self.assertEqual(len(old_files), 5 * layout["old_count"])
            for lang in FOREIGN:
                with self.subTest(series=series, language=lang):
                    actual = {p.stem for p in (directory / lang).glob("*.html")}
                    self.assertEqual(actual, {*layout["old_slugs"], "index", layout["slug"]})
            for lang in ("", *FOREIGN):
                path = directory / lang / "index.html"
                entries = Parsed(path.read_text()).nodes("a", "entry-row")
                old_entries = [n for n in entries
                               if n.attrs.get("href") != layout["slug"] + ".html"]
                expected = (30 if series == "foundations-companion" and not lang
                            else layout["old_count"])
                self.assertEqual(len(old_entries), expected, path)
            if series == "method-companion":
                expected = {"00": ("vii.html", "00e.html"),
                            "00e": ("00.html", "viii.html"),
                            "viii": ("00e.html", "ix.html")}
                for lang in ("", *FOREIGN):
                    for slug, neighbors in expected.items():
                        path = directory / lang / (slug + ".html")
                        doc = Parsed(path.read_text())
                        if lang or slug == "00e":
                            navs = (doc.nodes("nav", "lw-series-nav") if lang and slug == "00e"
                                    else doc.nodes("nav", "method-nav"))
                            self.assertTrue(navs, path)
                            # The primary page repeats its navigation in each
                            # inline reading mode; all copies must have edges.
                            for nav in navs:
                                self.assertEqual([n.attrs["href"] for n in nav.walk() if n.tag == "a"],
                                                 list(neighbors), path)
                        else:
                            prev = doc.nodes("a", "xiyou-nav-prev")
                            following = doc.nodes("a", "xiyou-nav-next")
                            self.assertEqual([n.attrs["href"] for n in prev], [neighbors[0]])
                            self.assertEqual([n.attrs["href"] for n in following], [neighbors[1]])

    def test_checked_in_pages_single_beacon_local_targets_and_no_writes(self):
        for series, case in self.cases.items():
            candidates = {**case["connections"], **case["pages"]}
            primary = ROOT / case["spec"]["directory"] / (case["layout"]["slug"] + ".html")
            candidates.setdefault(primary, primary.read_text())
            for path, text in candidates.items():
                with self.subTest(series=series, path=path.relative_to(ROOT)):
                    self.assertEqual(path.read_text(), text, f"Stale generated page: {path}")
                    if path.suffix != ".html":
                        continue
                    self.assertIsNone(analytics_issue(Document(text)), path)
                    self.assertEqual(text.count("cloudflareinsights.com/beacon.min.js"), 1)
                    for node in Parsed(text).nodes():
                        attribute = "href" if "href" in node.attrs else "src"
                        href = node.attrs.get(attribute)
                        if not href:
                            continue
                        url = urlsplit(html.unescape(href))
                        if url.netloc and url.netloc.lower() not in ("nondubito.net", "www.nondubito.net"):
                            continue
                        if url.scheme and url.scheme not in ("http", "https"):
                            continue
                        if not url.path:
                            continue
                        target = ((ROOT / unquote(url.path).lstrip("/"))
                                  if url.path.startswith("/") else (path.parent / unquote(url.path)))
                        if url.path.endswith("/"):
                            target /= "index.html"
                        target = target.resolve()
                        self.assertTrue(target.is_relative_to(ROOT), (path, href))
                        self.assertTrue(target in candidates or target.is_file(), (path, href))
            for path, before in case["before"].items():
                self.assertEqual(digest(path.read_bytes()), before, f"Read-only check changed {path}")


if __name__ == "__main__":
    unittest.main()
