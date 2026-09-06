#!/usr/bin/env python3
"""Build sitemap.xml from indexable, self-consistent canonical pages."""

from __future__ import annotations

import argparse
import html
import re
import subprocess
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from normalize_canonicals import local_target, normalized_url


ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"
SITE_ORIGIN = "https://nondubito.net"
DATE_MARKER = re.compile(r"^@@(\d{4}-\d{2}-\d{2})$")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.robots = ""
        self.html_lang = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.html_lang = values.get("lang", "").strip()
        if tag == "title":
            self._in_title = True
        if tag == "meta" and values.get("name", "").lower() == "description":
            self.description = values.get("content", "").strip()
        if tag == "meta" and values.get("name", "").lower() == "robots":
            self.robots = values.get("content", "").lower()
        if tag == "link" and values.get("rel", "").lower() == "canonical":
            self.canonical = values.get("href", "").strip()

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def parse_page(page: Path) -> PageParser:
    parser = PageParser()
    parser.feed(page.read_text(encoding="utf-8", errors="replace"))
    parser.title = parser.title.strip()
    return parser


def command_lines(args: list[str]) -> list[str]:
    result = subprocess.run(args, cwd=ROOT, check=True, capture_output=True, text=True)
    return result.stdout.splitlines()


def git_dates() -> tuple[dict[str, str], set[str]]:
    dates: dict[str, str] = {}
    current_date = ""
    for line in command_lines(
        ["git", "-c", "core.quotePath=false", "log", "--format=@@%cs", "--name-only", "--no-renames"]
    ):
        marker = DATE_MARKER.match(line)
        if marker:
            current_date = marker.group(1)
        elif line and current_date:
            dates.setdefault(line, current_date)

    dirty = set(command_lines(["git", "diff", "--name-only", "HEAD", "--"]))
    dirty.update(command_lines(["git", "ls-files", "--others", "--exclude-standard"]))
    return dates, dirty


def sitemap_xml(entries: list[tuple[str, str]]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url, modified in entries:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{html.escape(url)}</loc>",
                f"    <lastmod>{modified}</lastmod>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build() -> tuple[str, list[str], int]:
    parsed_pages: dict[Path, PageParser] = {}
    candidates: set[str] = set()
    ignored_external = 0
    for page in sorted(ROOT.rglob("*.html")):
        if ".git" in page.parts:
            continue
        metadata = parse_page(page)
        parsed_pages[page.resolve()] = metadata
        if "noindex" in metadata.robots or not metadata.canonical:
            continue
        if not metadata.canonical.startswith(SITE_ORIGIN + "/"):
            ignored_external += 1
            continue
        candidates.add(metadata.canonical)

    errors: list[str] = []
    target_by_url: dict[str, Path] = {}
    for url in sorted(candidates):
        if normalized_url(url) != url:
            errors.append(f"canonical is not normalized: {url}")
            continue
        target = local_target(url)
        if target is None or not target.is_file():
            errors.append(f"canonical target is missing: {url}")
            continue
        target = target.resolve()
        metadata = parsed_pages.get(target) or parse_page(target)
        if "noindex" in metadata.robots:
            errors.append(f"canonical target is noindex: {url}")
        if metadata.canonical != url:
            errors.append(f"canonical target does not self-identify: {url} ({metadata.canonical!r})")
        if not metadata.title:
            errors.append(f"canonical target has no title: {url}")
        if not metadata.description:
            errors.append(f"canonical target has no valid meta description: {url}")
        if not metadata.html_lang:
            errors.append(f"canonical target has no html lang: {url}")
        target_by_url[url] = target

    dates, dirty = git_dates()
    today = date.today().isoformat()
    entries: list[tuple[str, str]] = []
    for url in sorted(target_by_url, key=lambda item: (urlsplit(item).path != "/", urlsplit(item).path)):
        relative = target_by_url[url].relative_to(ROOT).as_posix()
        modified = today if relative in dirty else dates.get(relative, today)
        entries.append((url, modified))
    return sitemap_xml(entries), errors, ignored_external


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if sitemap.xml is stale")
    args = parser.parse_args()
    content, errors, ignored_external = build()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    count = content.count("<url>")
    if args.check:
        if not SITEMAP.is_file() or SITEMAP.read_text(encoding="utf-8") != content:
            print("ERROR: sitemap.xml is missing or stale")
            return 1
        print(f"OK: sitemap.xml contains {count} canonical URLs")
        return 0
    SITEMAP.write_text(content, encoding="utf-8")
    suffix = f"; ignored {ignored_external} external canonical(s)" if ignored_external else ""
    print(f"Wrote sitemap.xml with {count} canonical URLs{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
