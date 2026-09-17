#!/usr/bin/env python3
"""Read-only regression checks for the blockchain layout/navigation repair.

Run with ``python3 -B scripts/test_blockchain_layout.py``. Article bodies are
compared byte-for-byte with their inner HTML in git HEAD, not with generated
translations or normalized text. BLOCKCHAIN_BASELINE_REF may name an earlier
commit when checking a committed repair. No builder main function is called;
the old collection renderer is loaded directly from git into memory.
"""

from __future__ import annotations

import copy
import hashlib
import os
import re
import subprocess
import sys
import types
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "essays" / "blockchain"
LANGUAGES = ("zh", "en", "zh-hant", "ja", "fr", "de", "es", "ko")
HTML_LANG = {code: code for code in LANGUAGES}
HTML_LANG.update({"zh": "zh-Hans", "zh-hant": "zh-Hant"})
SLUGS = ("index", *(f"ep{number:02d}" for number in range(1, 22)))
VERSION = "20260917"
VOID = frozenset(
    "area base br col embed hr img input link meta param source track wbr".split()
)


def page_path(language: str, slug: str) -> Path:
    directory = SERIES if language == "zh" else SERIES / language
    return directory / f"{slug}.html"


def git_text(path: Path, revision: str) -> str:
    relative = path.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "show", f"{revision}:{relative}"],
        cwd=ROOT, capture_output=True, check=True,
    )
    return result.stdout.decode("utf-8")


def read_utf8(path: Path) -> str:
    # read_text/text-mode subprocess output would normalize CRLF. Body changes
    # must not disappear during extraction, including changes to line endings.
    return path.read_bytes().decode("utf-8")


def local_target(source_path: Path, href: str) -> Path:
    """Resolve relative, root-relative, and same-origin links without I/O."""
    url = urlsplit(href)
    if url.scheme or url.netloc:
        if url.scheme not in {"http", "https"} or url.netloc != "nondubito.net":
            raise ValueError(f"Not a same-origin URL: {href}")
        base = ROOT
    else:
        base = ROOT if url.path.startswith("/") else source_path.parent
    target = (base / unquote(url.path).lstrip("/")).resolve()
    if not target.is_relative_to(ROOT):
        raise ValueError(f"URL escapes the website: {href}")
    if not url.path or url.path.endswith("/"):
        target = target / "index.html" if url.path else source_path
    return target


class Element:
    def __init__(self, tag, attrs, parent, opening_start, opening_end):
        self.tag = tag
        self.attrs = dict(attrs)
        self.parent = parent
        self.opening_start = opening_start
        self.opening_end = opening_end
        self.closing_start = None

    @property
    def classes(self):
        return set(self.attrs.get("class", "").split())

    def inside(self, ancestor):
        parent = self.parent
        while parent is not None:
            if parent is ancestor:
                return True
            parent = parent.parent
        return False


class Page(HTMLParser):
    """Track element ranges while retaining the original, unnormalized HTML."""

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.line_starts = [0, *(match.end() for match in re.finditer("\n", source))]
        self.elements = []
        self.stack = []
        self.feed(source)
        self.close()

    def source_offset(self):
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self.source_offset()
        node = Element(
            tag, attrs, self.stack[-1] if self.stack else None,
            start, start + len(self.get_starttag_text()),
        )
        self.elements.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop().closing_start = self.source_offset() + len(self.get_starttag_text())

    def handle_endtag(self, tag):
        # The selectors under test have explicit closing tags. Tolerate unrelated
        # optional/malformed tags without letting them swallow a matching body.
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                self.stack[index].closing_start = self.source_offset()
                del self.stack[index:]
                return

    def select(self, tag=None, class_name=None, within=None):
        return [node for node in self.elements
                if (tag is None or node.tag == tag)
                and (class_name is None or class_name in node.classes)
                and (within is None or node.inside(within))]

    def inner_html(self, node):
        if node.closing_start is None:
            raise ValueError(f"Unclosed {node.tag}.{'.'.join(node.classes)}")
        return self.source[node.opening_end:node.closing_start]


def prose_node(page: Page, language: str):
    if language in {"zh", "en", "zh-hant"}:
        matches = page.select("article", "essay-body")
    else:
        matches = page.select(class_name="collection-body")
    if len(matches) != 1:
        raise AssertionError(f"Expected exactly one prose container, found {len(matches)}")
    return matches[0]


def memory_module(name: str, source: str, filename: Path):
    """Use the real __file__ for ROOT, but never write an old script to disk."""
    module = types.ModuleType(name)
    module.__file__ = str(filename)
    sys.modules[name] = module
    exec(compile(source, str(filename), "exec"), module.__dict__)
    return module


def css_declarations(source, selector_pattern):
    """Read declarations from flat rules, including rules inside media blocks.

    This is deliberately not a CSS layout engine. Selectors and property order
    may vary; the assertions below check the agreed scoped reset contract.
    """
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    declarations = {}
    for match in re.finditer(r"([^{}]+)\{([^{}]*)\}", source):
        selectors, body = match.groups()
        if not any(re.search(selector_pattern, selector.strip())
                   for selector in selectors.split(",")):
            continue
        for declaration in body.split(";"):
            if ":" in declaration:
                name, value = declaration.split(":", 1)
                declarations[name.strip().lower()] = re.sub(
                    r"\s*!important\s*$", "", value.strip(), flags=re.I,
                ).lower()
    return declarations


class ExtractionTests(unittest.TestCase):
    def test_nested_prose_keeps_entities_whitespace_and_links(self):
        body = '\r\n<p>A &amp; B<br> C</p><div><div>x</div></div><a href="x">y</a>\r\n'
        source = '<article class="essay-body">' + body + '</article><footer>outside</footer>'
        page = Page(source)
        self.assertEqual(page.inner_html(prose_node(page, "en")), body)

    def test_nested_spans_do_not_truncate_menu(self):
        page = Page('<span class="blockchain-language-menu"><button><span>EN</span></button>'
                    '<span><a data-language="zh" href="ep01.html">中文</a></span></span>')
        menu = page.select("span", "blockchain-language-menu")[0]
        self.assertEqual(len(page.select("a", within=menu)), 1)
        self.assertIn('</a></span>', page.inner_html(menu))


class BlockchainLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reference = os.environ.get("BLOCKCHAIN_BASELINE_REF", "HEAD")
        cls.baseline = subprocess.run(
            ["git", "rev-parse", "--verify", f"{reference}^{{commit}}"],
            cwd=ROOT, text=True, encoding="utf-8", capture_output=True, check=True,
        ).stdout.strip()
        cls.pages = {}
        for language in LANGUAGES:
            for slug in SLUGS:
                path = page_path(language, slug)
                cls.pages[path] = Page(read_utf8(path))

    def test_inventory_and_document_languages(self):
        self.assertEqual(len(self.pages), 8 * 22)
        for language in LANGUAGES:
            expected = {page_path(language, slug) for slug in SLUGS}
            directory = page_path(language, "index").parent
            actual = {path for path in directory.glob("*.html")
                      if path.stem == "index" or re.fullmatch(r"ep\d+", path.stem)}
            self.assertEqual(actual, expected, f"Page inventory for {language}")
            for path in expected:
                with self.subTest(page=path.relative_to(ROOT)):
                    html_nodes = self.pages[path].select("html")
                    self.assertEqual(len(html_nodes), 1)
                    self.assertEqual(html_nodes[0].attrs.get("lang"), HTML_LANG[language])

    def test_all_eight_menu_routes_are_real_same_episode_pages(self):
        for language in LANGUAGES:
            for slug in SLUGS:
                path = page_path(language, slug)
                with self.subTest(language=language, page=slug):
                    page = self.pages[path]
                    menus = page.select("span", "blockchain-language-menu")
                    self.assertEqual(len(menus), 1, "Exactly one server-rendered language menu")
                    links = page.select("a", within=menus[0])
                    self.assertEqual(len(links), 8)
                    codes = [node.attrs.get("data-language") for node in links]
                    self.assertCountEqual(codes, LANGUAGES)
                    self.assertEqual(len(set(codes)), 8)
                    current = [node for node in links if node.attrs.get("aria-current") == "page"]
                    self.assertEqual(len(current), 1)
                    self.assertEqual(current[0].attrs["data-language"], language)
                    for node in links:
                        code = node.attrs["data-language"]
                        href = node.attrs.get("href", "")
                        self.assertTrue(href, f"{code} needs a real href even without JavaScript")
                        parsed = urlsplit(href)
                        self.assertFalse(parsed.query, href)
                        self.assertFalse(parsed.fragment, href)
                        target = local_target(path, href)
                        self.assertEqual(target, page_path(code, slug), href)
                        self.assertTrue(target.is_file(), href)
                        target_html = self.pages[target].select("html")
                        self.assertEqual(len(target_html), 1)
                        self.assertEqual(target_html[0].attrs.get("lang"), HTML_LANG[code], href)
                        if code != language:
                            self.assertNotIn("aria-current", node.attrs, href)

    def test_old_language_blocks_and_query_routes_are_gone(self):
        for path, page in self.pages.items():
            with self.subTest(page=path.relative_to(ROOT)):
                self.assertNotIn("collection-language-links", page.source)
                for node in page.select("a"):
                    href = node.attrs.get("href", "")
                    if "lang" not in parse_qs(urlsplit(href).query, keep_blank_values=True):
                        continue
                    try:
                        target = local_target(path, href)
                    except ValueError:
                        continue
                    self.assertFalse(target.is_relative_to(SERIES), f"Old ?lang route: {href}")

    def test_versioned_menu_assets_and_original_layout_stylesheet(self):
        for language in LANGUAGES:
            for slug in SLUGS:
                path = page_path(language, slug)
                with self.subTest(language=language, page=slug):
                    page = self.pages[path]
                    assets = []
                    for node in page.elements:
                        if node.tag == "script" and node.attrs.get("src"):
                            assets.append(("script", node.attrs["src"]))
                        elif node.tag == "link" and "stylesheet" in node.attrs.get("rel", "").split():
                            assets.append(("style", node.attrs.get("href", "")))
                    required = [("style", "language-menu.css"), ("script", "language-menu.js")]
                    if language in {"zh", "en", "zh-hant"}:
                        required.append(("style", "blockchain.css"))
                    for kind, filename in required:
                        matches = [(tag, href) for tag, href in assets
                                   if tag == kind and Path(urlsplit(href).path).name == filename]
                        self.assertEqual(len(matches), 1, filename)
                        href = matches[0][1]
                        self.assertEqual(parse_qs(urlsplit(href).query), {"v": [VERSION]}, href)
                        target = local_target(path, href)
                        self.assertEqual(target, SERIES / filename, href)
                        self.assertTrue(target.is_file(), href)

    def test_article_inner_html_is_unchanged_from_git(self):
        for language in LANGUAGES:
            for slug in SLUGS[1:]:
                path = page_path(language, slug)
                with self.subTest(language=language, page=slug):
                    current = self.pages[path]
                    original = Page(git_text(path, self.baseline))
                    old_body = original.inner_html(prose_node(original, language))
                    new_body = current.inner_html(prose_node(current, language))
                    self.assertTrue(old_body.strip(), "Baseline prose cannot be empty")
                    self.assertTrue(current.select("p", within=prose_node(current, language)))
                    self.assertEqual(new_body, old_body, "Layout work must not change any body HTML")

    def test_indexes_keep_all_21_article_cards(self):
        for language in LANGUAGES:
            path = page_path(language, "index")
            with self.subTest(language=language):
                class_name = "blockchain-card" if language in {"zh", "en", "zh-hant"} else "collection-card"
                cards = self.pages[path].select("a", class_name)
                self.assertEqual(len(cards), 21)
                targets = [local_target(path, node.attrs.get("href", "")) for node in cards]
                self.assertEqual(targets, [page_path(language, slug) for slug in SLUGS[1:]])

    def test_content_headers_and_prose_have_scoped_layout_resets(self):
        css = read_utf8(SERIES / "blockchain.css")
        reset = css_declarations(css, r"\.blockchain-main(?:\s*>\s*|\s+)header\b")
        for name, expected in {
            "position": "static", "z-index": "auto", "height": "auto",
            "display": "block", "backdrop-filter": "none", "-webkit-backdrop-filter": "none",
        }.items():
            self.assertEqual(reset.get(name), expected, f"Scoped content-header reset: {name}")
        self.assertTrue(
            reset.get("inset") == "auto"
            or all(reset.get(side) == "auto" for side in ("top", "right", "bottom", "left")),
            "Content headers must clear the global header offsets",
        )
        self.assertIn(reset.get("background", reset.get("background-color")),
                      {"none", "transparent", "rgba(0, 0, 0, 0)"})
        site_header = css_declarations(css, r"\.blockchain-site-header\s*$")
        self.assertEqual(site_header.get("position"), "sticky", "Only the site header stays sticky")
        self.assertEqual(site_header.get("display"), "block")
        self.assertEqual(site_header.get("height"), "auto")
        prose = css_declarations(css, r"\.blockchain-page\s+\.essay-body\s*$")
        self.assertEqual(prose.get("max-width"), "none")
        for name in ("margin", "padding"):
            self.assertRegex(prose.get(name, ""), r"^0(?:px|rem|em)?(?:\s+0(?:px|rem|em)?){0,3}$",
                             f"Scoped prose {name} must not inherit generic essay spacing")

    def test_other_collection_renderers_are_byte_identical_to_git(self):
        script = ROOT / "scripts" / "build_collection_languages.py"
        old = memory_module("_blockchain_old_collection_renderer", git_text(script, self.baseline), script)
        current = memory_module("_blockchain_current_collection_renderer", read_utf8(script), script)
        old_specs = {spec["id"]: spec for spec in old.load_specs()
                     if spec["directory"] != "essays/blockchain"}
        current_specs = {spec["id"]: spec for spec in current.load_specs()
                         if spec["directory"] != "essays/blockchain"}
        self.assertEqual(set(current_specs), set(old_specs), "Do not drop unrelated collections")
        checked = 0
        for identifier, spec in current_specs.items():
            expected = old.render(copy.deepcopy(old_specs[identifier]))
            actual = current.render(copy.deepcopy(spec))
            with self.subTest(collection=spec["id"]):
                self.assertEqual(set(actual), set(expected))
            for path in expected.keys() & actual.keys():
                with self.subTest(collection=spec["id"], page=path.relative_to(ROOT)):
                    # Hashes keep a failure readable instead of printing whole articles.
                    self.assertEqual(
                        hashlib.sha256(actual[path].encode("utf-8")).hexdigest(),
                        hashlib.sha256(expected[path].encode("utf-8")).hexdigest(),
                        "A non-blockchain collection render changed",
                    )
                checked += 1
        self.assertGreater(checked, 0, "The unrelated-collection guard must compare real output")

    def test_translated_layout_can_shrink_and_wrap_long_words(self):
        # This stylesheet is loaded only by the blockchain collection. Keeping
        # the main box shrinkable prevents long translated titles from forcing
        # the mobile page wider than the viewport.
        css = read_utf8(SERIES / "language-menu.css")
        collection = css_declarations(css, r"\.collection-page\s*$")
        self.assertEqual(collection.get("box-sizing"), "border-box")
        self.assertEqual(collection.get("width"), "100%")
        self.assertRegex(collection.get("min-width", ""), r"^0(?:px|rem|em)?$")
        self.assertEqual(collection.get("overflow-wrap"), "anywhere")


if __name__ == "__main__":
    unittest.main()
