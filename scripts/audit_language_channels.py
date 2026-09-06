#!/usr/bin/env python3
"""Audit the reader-facing contract shared by Non Dubito language channels."""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "language-channel-audit.json"
REPORT_MD = ROOT / "reports" / "language-channel-audit.md"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
SNAPSHOT_DATE = "2026-09-05"

CHANNELS = {
    "zh-hant": {"html_lang": "zh-Hant", "search": "zh-Hant", "ui": None, "og_locale": "zh_TW"},
    "ja": {"html_lang": "ja", "search": "ja", "ui": "ja", "og_locale": "ja_JP"},
    "fr": {"html_lang": "fr", "search": "fr", "ui": "fr", "og_locale": "fr_FR"},
    "de": {"html_lang": "de", "search": "de", "ui": "de", "og_locale": "de_DE"},
    "es": {"html_lang": "es", "search": "es", "ui": "es", "og_locale": "es_ES"},
    "ko": {"html_lang": "ko", "search": "ko", "ui": "ko", "og_locale": "ko_KR"},
}

ALTERNATE_URLS = {
    "en": "https://nondubito.net/",
    "zh-Hant": "https://nondubito.net/essays/zh-hant/",
    "ja": "https://nondubito.net/essays/ja/",
    "fr": "https://nondubito.net/essays/fr/",
    "de": "https://nondubito.net/essays/de/",
    "es": "https://nondubito.net/essays/es/",
    "ko": "https://nondubito.net/essays/ko/",
    "x-default": "https://nondubito.net/",
}

CORE_PAGES = {
    "index.html": "https://nondubito.net/",
    "start.html": "https://nondubito.net/start.html",
    "explore.html": "https://nondubito.net/explore.html",
    "latest.html": "https://nondubito.net/latest.html",
    "search.html": "https://nondubito.net/search.html",
    "library.html": "https://nondubito.net/library.html",
    "about.html": "https://nondubito.net/about.html",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = ""
        self.description = ""
        self.author = ""
        self.canonical = ""
        self.og_type = ""
        self.og_locale = ""
        self.og_url = ""
        self.twitter_card = ""
        self.alternates: dict[str, str] = {}
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.guide_count = 0
        self.guide_cards = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        classes = values.get("class", "").split()
        if tag == "html":
            self.html_lang = values.get("lang", "")
        if tag == "meta" and values.get("name") == "description":
            self.description = values.get("content", "").strip()
        if tag == "meta" and values.get("name") == "author":
            self.author = values.get("content", "").strip()
        if tag == "meta" and values.get("property") == "og:type":
            self.og_type = values.get("content", "").strip()
        if tag == "meta" and values.get("property") == "og:locale":
            self.og_locale = values.get("content", "").strip()
        if tag == "meta" and values.get("property") == "og:url":
            self.og_url = values.get("content", "").strip()
        if tag == "meta" and values.get("name") == "twitter:card":
            self.twitter_card = values.get("content", "").strip()
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href", "")
        if tag == "link" and values.get("rel") == "alternate" and values.get("hreflang"):
            self.alternates[values["hreflang"]] = values.get("href", "")
        if values.get("id"):
            self.ids.append(values["id"])
        if "language-channel-guide" in classes:
            self.guide_count += 1
        if "language-channel-guide-card" in classes:
            self.guide_cards += 1
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])


def local_target(page: Path, href: str) -> Path | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    target = (page.parent / parsed.path).resolve()
    try:
        target.relative_to(ROOT)
    except ValueError:
        return None
    return target


def sitemap_urls() -> list[str]:
    tree = ElementTree.parse(ROOT / "sitemap.xml")
    return [
        node.text.strip()
        for node in tree.findall("sm:url/sm:loc", SITEMAP_NS)
        if node.text
    ]


def page_parser(page: Path) -> PageParser:
    parser = PageParser()
    parser.feed(page.read_text(encoding="utf-8", errors="replace"))
    return parser


def sitemap_target(url: str) -> Path | None:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "nondubito.net":
        return None
    route = unquote(parsed.path)
    relative = route.lstrip("/")
    if not relative or route.endswith("/"):
        relative += "index.html"
    target = (ROOT / relative).resolve()
    try:
        target.relative_to(ROOT)
    except ValueError:
        return None
    return target


def audit_channel(code: str, config: dict[str, str | None], urls: set[str]) -> dict[str, object]:
    page = ROOT / "essays" / code / "index.html"
    errors: list[str] = []
    if not page.is_file():
        return {"language": code, "path": page.relative_to(ROOT).as_posix(), "errors": ["channel page is missing"]}

    parser = page_parser(page)
    expected_canonical = f"https://nondubito.net/essays/{code}/"
    if parser.html_lang != config["html_lang"]:
        errors.append(f"html lang is {parser.html_lang!r}, expected {config['html_lang']!r}")
    if not parser.description:
        errors.append("meta description is missing")
    if parser.author != "Han Qin (秦汉)" and parser.author != "Han Qin (秦漢)":
        errors.append("author metadata is missing or unexpected")
    if parser.canonical != expected_canonical:
        errors.append(f"canonical is {parser.canonical!r}, expected {expected_canonical!r}")
    if parser.og_type != "website":
        errors.append("og:type is not website")
    if parser.og_locale != config["og_locale"]:
        errors.append(f"og:locale is {parser.og_locale!r}, expected {config['og_locale']!r}")
    if parser.og_url != expected_canonical:
        errors.append(f"og:url is {parser.og_url!r}, expected {expected_canonical!r}")
    if parser.twitter_card != "summary":
        errors.append("twitter:card is not summary")
    if parser.alternates != ALTERNATE_URLS:
        errors.append("hreflang cluster is missing or inconsistent")
    if expected_canonical not in urls:
        errors.append("channel canonical is absent from sitemap.xml")
    if parser.guide_count != 1 or parser.guide_cards != 4:
        errors.append(f"reader guide has {parser.guide_count} wrapper(s) and {parser.guide_cards} card(s)")
    if parser.ids.count("language-library") != 1:
        errors.append("full-library anchor is missing or duplicated")

    broken: list[str] = []
    for href in parser.hrefs:
        target = local_target(page, href)
        if target is not None and not target.exists():
            broken.append(href)
    if broken:
        errors.append("missing local targets: " + ", ".join(sorted(set(broken))))

    search_links = [urlsplit(href) for href in parser.hrefs if urlsplit(href).path.endswith("search.html")]
    matching_search = []
    for link in search_links:
        query = parse_qs(link.query)
        edition_ok = query.get("in") == [config["search"]]
        ui_ok = query.get("ui") == [config["ui"]] if config["ui"] else "ui" not in query
        language_ok = query.get("lang") == ["zh-hant" if code == "zh-hant" else "en"]
        if edition_ok and ui_ok and language_ok:
            matching_search.append(link)
    if len(matching_search) < 2:
        errors.append("header and guide do not both preserve the channel search language")

    if code == "zh-hant":
        foundation = ROOT / "essays" / "sae-foundations" / "index.html"
    else:
        foundation = ROOT / "essays" / "sae-foundations" / code / "index.html"
    if not foundation.is_file():
        errors.append("localized SAE Foundations entry is missing")

    return {
        "language": code,
        "path": page.relative_to(ROOT).as_posix(),
        "canonical": parser.canonical,
        "metadata": "ok" if not [error for error in errors if error.startswith(("meta ", "author ", "canonical ", "og:", "twitter:", "hreflang "))] else "error",
        "guide_cards": parser.guide_cards,
        "search_routes": len(matching_search),
        "local_links": len([href for href in parser.hrefs if local_target(page, href) is not None]),
        "errors": errors,
    }


def build() -> dict[str, object]:
    url_list = sitemap_urls()
    urls = set(url_list)
    channels = [audit_channel(code, config, urls) for code, config in CHANNELS.items()]
    errors = [f"{item['language']}: {error}" for item in channels for error in item["errors"]]

    root_parser = page_parser(ROOT / "index.html")
    if root_parser.author != "Han Qin (秦汉)":
        errors.append("root: author metadata is missing or unexpected")
    if root_parser.og_type != "website" or root_parser.og_locale != "en_US":
        errors.append("root: Open Graph type or locale is missing")
    if root_parser.og_url != "https://nondubito.net/" or root_parser.twitter_card != "summary":
        errors.append("root: social discovery metadata is incomplete")
    if root_parser.alternates != ALTERNATE_URLS:
        errors.append("root: hreflang cluster is missing or inconsistent")

    required_site_urls = set(CORE_PAGES.values())
    for missing in sorted(required_site_urls - urls):
        errors.append(f"sitemap: missing {missing}")

    core_pages: list[dict[str, str]] = []
    for relative, expected_canonical in CORE_PAGES.items():
        page = ROOT / relative
        parser = page_parser(page)
        status = "ok"
        if parser.canonical != expected_canonical:
            errors.append(f"core: {relative} canonical is {parser.canonical!r}, expected {expected_canonical!r}")
            status = "error"
        core_pages.append({"path": relative, "canonical": parser.canonical, "status": status})

    duplicate_urls = len(url_list) - len(urls)
    if duplicate_urls:
        errors.append(f"sitemap: {duplicate_urls} duplicate URL(s)")
    missing_targets = sorted(
        url for url in urls if (target := sitemap_target(url)) is None or not target.is_file()
    )
    if missing_targets:
        preview = ", ".join(missing_targets[:5])
        suffix = " ..." if len(missing_targets) > 5 else ""
        errors.append(f"sitemap: {len(missing_targets)} missing file target(s): {preview}{suffix}")

    manifest = json.loads((ROOT / "data" / "search-index.json").read_text(encoding="utf-8"))
    language_indexes = manifest.get("languages", {})
    expected_indexes = {"en", "zh-Hans", "zh-Hant", "ja", "fr", "de", "es", "ko"}
    for language in sorted(expected_indexes - set(language_indexes)):
        errors.append(f"search: missing {language} index")
    for language in sorted(expected_indexes & set(language_indexes)):
        if not isinstance(language_indexes[language].get("count"), int) or language_indexes[language]["count"] <= 0:
            errors.append(f"search: {language} index has no records")

    return {
        "snapshot_date": SNAPSHOT_DATE,
        "channels": channels,
        "core_pages": core_pages,
        "search_languages": {language: language_indexes[language]["count"] for language in sorted(expected_indexes & set(language_indexes))},
        "sitemap": {
            "urls": len(url_list),
            "unique_urls": len(urls),
            "duplicate_urls": duplicate_urls,
            "missing_file_targets": len(missing_targets),
        },
        "errors": errors,
    }


def markdown(data: dict[str, object]) -> str:
    lines = [
        "# Language channel audit",
        "",
        f"Snapshot: {data['snapshot_date']}",
        "",
        "This report verifies the shared reader contract for the six independent",
        "language channels. English and Simplified Chinese share the root home.",
        "",
        "| Channel | Metadata | Guide cards | Preserved search routes | Local links | Status |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for item in data["channels"]:
        status = "OK" if not item["errors"] else "Needs attention"
        lines.append(
            f"| `{item['language']}` | {item.get('metadata', 'error')} | {item.get('guide_cards', 0)} | "
            f"{item.get('search_routes', 0)} | {item.get('local_links', 0)} | {status} |"
        )
    lines.extend(["", "## Search indexes", "", "| Language | Records |", "| --- | ---: |"])
    for language, count in data["search_languages"].items():
        lines.append(f"| `{language}` | {count:,} |")
    sitemap = data["sitemap"]
    lines.extend(
        [
            "",
            "## Public discovery surface",
            "",
            f"- Core pages with verified canonical URLs: {len(data['core_pages'])}",
            f"- Sitemap entries: {sitemap['urls']:,}",
            f"- Unique sitemap entries: {sitemap['unique_urls']:,}",
            f"- Duplicate sitemap entries: {sitemap['duplicate_urls']:,}",
            f"- Missing local sitemap targets: {sitemap['missing_file_targets']:,}",
            "",
        ]
    )
    if data["errors"]:
        lines.extend(["## Errors", ""] + [f"- {error}" for error in data["errors"]] + [""])
    else:
        lines.extend(["All channel contracts pass.", ""])
    return "\n".join(lines)


def serialized(data: dict[str, object]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the tracked audit is stale")
    args = parser.parse_args()
    data = build()
    outputs = {REPORT_JSON: serialized(data), REPORT_MD: markdown(data)}
    if data["errors"]:
        for error in data["errors"]:
            print(f"ERROR: {error}")
        return 1
    if args.check:
        stale = [path for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"ERROR: {path.relative_to(ROOT)} is missing or stale")
            return 1
        print(f"OK: {len(data['channels'])} language channels and {len(data['search_languages'])} search indexes")
        return 0
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    print(f"Wrote language channel audit for {len(data['channels'])} channels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
