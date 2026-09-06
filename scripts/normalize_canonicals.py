#!/usr/bin/env python3
"""Normalize canonical and related discovery URLs without moving pages."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
SITE_HOST = "nondubito.net"
DISCOVERY_TAG_RE = re.compile(r'<(?:link|meta)\b[^>]*>', flags=re.IGNORECASE)
ATTR_RE = re.compile(r'\b([\w:-]+)="([^"]*)"', flags=re.IGNORECASE)


def local_target(url: str) -> Path | None:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != SITE_HOST or parsed.query or parsed.fragment:
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


def normalized_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc != SITE_HOST:
        return url
    route = parsed.path or "/"
    if route.endswith("/index.html"):
        route = route[: -len("index.html")]
    elif route != "/" and not route.endswith("/"):
        possible_index = ROOT / unquote(route.lstrip("/")) / "index.html"
        if possible_index.is_file():
            route += "/"
    return urlunsplit(("https", SITE_HOST, route, "", ""))


def discovery_value(tag: str) -> tuple[str, str] | None:
    attrs = {key.lower(): value for key, value in ATTR_RE.findall(tag)}
    lowered = tag.lower()
    if lowered.startswith("<link") and attrs.get("rel", "").lower() == "canonical":
        return "href", attrs.get("href", "")
    if (
        lowered.startswith("<link")
        and attrs.get("rel", "").lower() == "alternate"
        and attrs.get("hreflang")
    ):
        return "href", attrs.get("href", "")
    if lowered.startswith("<meta") and attrs.get("property", "").lower() == "og:url":
        return "content", attrs.get("content", "")
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if a canonical URL needs normalization")
    args = parser.parse_args()

    changes: list[tuple[Path, str, str, str]] = []
    errors: list[str] = []
    for page in sorted(ROOT.rglob("*.html")):
        if ".git" in page.parts:
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        canonical = ""

        def replace_tag(match: re.Match[str]) -> str:
            nonlocal canonical
            tag = match.group(0)
            result = discovery_value(tag)
            if result is None:
                return tag
            attribute, current = result
            normalized = normalized_url(current)
            if 'rel="canonical"' in tag.lower():
                canonical = normalized
            if normalized == current:
                return tag
            changes.append((page, attribute, current, normalized))
            if args.check:
                return tag
            return tag.replace(f'{attribute}="{current}"', f'{attribute}="{normalized}"', 1)

        updated = DISCOVERY_TAG_RE.sub(replace_tag, text)
        if not args.check and updated != text:
            page.write_text(updated, encoding="utf-8")
        if canonical:
            target = local_target(canonical)
            if target is None or not target.is_file():
                errors.append(f"{page.relative_to(ROOT)}: canonical target is missing or invalid: {canonical}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if args.check and changes:
        for page, attribute, current, normalized in changes[:20]:
            print(f"ERROR: {page.relative_to(ROOT)} {attribute}: {current} -> {normalized}")
        if len(changes) > 20:
            print(f"ERROR: ... and {len(changes) - 20} more discovery URL(s)")
        return 1
    if args.check:
        print("OK: discovery URLs use the preferred HTTPS and directory forms")
    else:
        print(f"Normalized {len(changes)} discovery URL(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
