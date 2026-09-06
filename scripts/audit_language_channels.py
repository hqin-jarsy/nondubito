#!/usr/bin/env python3
"""Audit the reader-facing contract shared by Non Dubito language channels."""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "language-channel-audit.json"
REPORT_MD = ROOT / "reports" / "language-channel-audit.md"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
SNAPSHOT_DATE = "2026-09-05"

CHANNELS = {
    "zh-hant": {"html_lang": "zh-Hant", "search": "zh-Hant", "ui": None},
    "ja": {"html_lang": "ja", "search": "ja", "ui": "ja"},
    "fr": {"html_lang": "fr", "search": "fr", "ui": "fr"},
    "de": {"html_lang": "de", "search": "de", "ui": "de"},
    "es": {"html_lang": "es", "search": "es", "ui": "es"},
    "ko": {"html_lang": "ko", "search": "ko", "ui": "ko"},
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = ""
        self.description = ""
        self.canonical = ""
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
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href", "")
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


def sitemap_urls() -> set[str]:
    tree = ElementTree.parse(ROOT / "sitemap.xml")
    return {
        node.text.strip()
        for node in tree.findall("sm:url/sm:loc", SITEMAP_NS)
        if node.text
    }


def audit_channel(code: str, config: dict[str, str | None], urls: set[str]) -> dict[str, object]:
    page = ROOT / "essays" / code / "index.html"
    errors: list[str] = []
    if not page.is_file():
        return {"language": code, "path": page.relative_to(ROOT).as_posix(), "errors": ["channel page is missing"]}

    parser = PageParser()
    parser.feed(page.read_text(encoding="utf-8", errors="replace"))
    expected_canonical = f"https://nondubito.net/essays/{code}/"
    if parser.html_lang != config["html_lang"]:
        errors.append(f"html lang is {parser.html_lang!r}, expected {config['html_lang']!r}")
    if not parser.description:
        errors.append("meta description is missing")
    if parser.canonical != expected_canonical:
        errors.append(f"canonical is {parser.canonical!r}, expected {expected_canonical!r}")
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
        "guide_cards": parser.guide_cards,
        "search_routes": len(matching_search),
        "local_links": len([href for href in parser.hrefs if local_target(page, href) is not None]),
        "errors": errors,
    }


def build() -> dict[str, object]:
    urls = sitemap_urls()
    channels = [audit_channel(code, config, urls) for code, config in CHANNELS.items()]
    errors = [f"{item['language']}: {error}" for item in channels for error in item["errors"]]

    required_site_urls = {
        "https://nondubito.net/",
        "https://nondubito.net/start.html",
        "https://nondubito.net/explore.html",
        "https://nondubito.net/latest.html",
        "https://nondubito.net/search.html",
    }
    for missing in sorted(required_site_urls - urls):
        errors.append(f"sitemap: missing {missing}")

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
        "search_languages": {language: language_indexes[language]["count"] for language in sorted(expected_indexes & set(language_indexes))},
        "sitemap_urls": len(urls),
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
        "| Channel | Guide cards | Preserved search routes | Local links | Status |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for item in data["channels"]:
        status = "OK" if not item["errors"] else "Needs attention"
        lines.append(
            f"| `{item['language']}` | {item.get('guide_cards', 0)} | "
            f"{item.get('search_routes', 0)} | {item.get('local_links', 0)} | {status} |"
        )
    lines.extend(["", "## Search indexes", "", "| Language | Records |", "| --- | ---: |"])
    for language, count in data["search_languages"].items():
        lines.append(f"| `{language}` | {count:,} |")
    lines.extend(["", f"Sitemap entries: {data['sitemap_urls']:,}", ""])
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
