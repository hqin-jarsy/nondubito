#!/usr/bin/env python3
"""Upgrade only the navigation and resource links of published blockchain pages.

The shared renderer also serves the two collection/import generators. Running
this module never regenerates article prose or rewrites other collections.
"""

from __future__ import annotations

import argparse
import html
import posixpath
import re
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "essays" / "blockchain"
VERSION = "20260917"
LANGUAGES = ("zh", "en", "zh-hant", "ja", "fr", "de", "es", "ko")
SLUGS = ("index", *(f"ep{i:02d}" for i in range(1, 22)))
LANGUAGE_NAMES = {
    "zh": "简体中文", "en": "English", "zh-hant": "繁體中文",
    "ja": "日本語", "fr": "Français", "de": "Deutsch",
    "es": "Español", "ko": "한국어",
}
LANGUAGE_LABELS = {
    "zh": "语言", "en": "Language", "zh-hant": "語言", "ja": "言語",
    "fr": "Langue", "de": "Sprache", "es": "Idioma", "ko": "언어",
}
_LINK = re.compile(r'<link\b[^>]*>', re.I)
_SCRIPT = re.compile(r'<script\b[^>]*>.*?</script\s*>', re.I | re.S)
_ANCHOR = re.compile(r'<a\b[^>]*>.*?</a\s*>', re.I | re.S)


def _attribute(tag: str, name: str) -> str | None:
    match = re.search(r'\b' + re.escape(name) + r'\s*=\s*([\"\'])(.*?)\1', tag, re.I | re.S)
    return html.unescape(match.group(2)) if match else None


def _validate(language: str, slug: str) -> None:
    if language not in LANGUAGES or slug not in SLUGS:
        raise ValueError(f"Not a blockchain edition: {language}/{slug}")


def page_path(language: str, slug: str) -> Path:
    _validate(language, slug)
    return SERIES / ("" if language == "zh" else language) / f"{slug}.html"


def menu_html(language: str, slug: str) -> str:
    """Every edition is an independent URL, including English and Traditional."""
    _validate(language, slug)
    directory = "." if language == "zh" else language
    links = []
    for code in LANGUAGES:
        target = f"{slug}.html" if code == "zh" else f"{code}/{slug}.html"
        href = posixpath.relpath(target, directory)
        current = ' aria-current="page"' if code == language else ""
        links.append(
            f'<a data-language="{code}" href="{href}"{current}>{LANGUAGE_NAMES[code]}</a>'
        )
    return (
        '<span class="blockchain-language-menu" role="group" '
        f'aria-label="{LANGUAGE_LABELS[language]}">' + "".join(links) + '</span>'
    )


def _navigation_pattern(language: str) -> re.Pattern[str]:
    name = "blockchain-header-tools" if language in ("zh", "en", "zh-hant") else "language-route"
    # The menu deliberately has no nested div: preserve the existing wrapper.
    return re.compile(r'(<div\b[^>]*\bclass="' + name + r'"[^>]*>)(.*?)(</div\s*>)', re.S)


def _replace_navigation(source: str, language: str, slug: str) -> str:
    pattern = _navigation_pattern(language)
    matches = list(pattern.finditer(source))
    if len(matches) != 1:
        raise ValueError(f"{language}/{slug}: expected one navigation wrapper, found {len(matches)}")
    match = matches[0]
    if re.search(r'<div\b', match.group(2), re.I):
        raise ValueError(f"{language}/{slug}: unexpected nested navigation div")
    search = ""
    if language in ("zh", "en", "zh-hant"):
        searches = [
            anchor.group(0) for anchor in _ANCHOR.finditer(match.group(2))
            if posixpath.basename(urlsplit(_attribute(anchor.group(0), "href") or "").path) == "search.html"
        ]
        if len(searches) != 1:
            raise ValueError(f"{language}/{slug}: expected the existing search link")
        search = searches[0]
    replacement = match.group(1) + search + menu_html(language, slug) + match.group(3)
    return source[:match.start()] + replacement + source[match.end():]


def _resource_name(tag: str, attribute: str) -> str:
    return posixpath.basename(urlsplit(_attribute(tag, attribute) or "").path)


def _upsert_resource(source: str, pattern: re.Pattern[str], attribute: str, filename: str, tag: str) -> str:
    matches = [m for m in pattern.finditer(source) if _resource_name(m.group(0), attribute) == filename]
    if len(matches) > 1:
        raise ValueError(f"Duplicate blockchain resource: {filename}")
    if matches:
        match = matches[0]
        return source[:match.start()] + tag + source[match.end():]
    if source.count("</head>") != 1:
        raise ValueError("Expected one document head")
    return source.replace("</head>", tag + "</head>", 1)


def _outside_navigation(source: str, language: str) -> str:
    """Byte-preservation guard: nothing outside menus/resources may change."""
    source = _navigation_pattern(language).sub(lambda m: m.group(1) + m.group(3), source)
    source = _LINK.sub(
        lambda m: "" if _resource_name(m.group(0), "href") in ("blockchain.css", "language-menu.css") else m.group(0),
        source,
    )
    return _SCRIPT.sub(
        lambda m: "" if _resource_name(m.group(0), "src") == "language-menu.js" else m.group(0), source,
    )


def upgrade_page(source: str, language: str, slug: str) -> str:
    _validate(language, slug)
    upgraded = _replace_navigation(source, language, slug)
    prefix = "" if language == "zh" else "../"
    if language in ("zh", "en", "zh-hant"):
        # Normalize this series' stylesheet version without altering other CSS.
        def update_stylesheet(match: re.Match[str]) -> str:
            tag = match.group(0)
            if _resource_name(tag, "href") != "blockchain.css":
                return tag
            return re.sub(r'(\bhref\s*=\s*)([\"\']).*?\2',
                          lambda m: m.group(1) + m.group(2) + prefix + "blockchain.css?v=" + VERSION + m.group(2),
                          tag, count=1, flags=re.I | re.S)
        upgraded = _LINK.sub(update_stylesheet, upgraded)
    upgraded = _upsert_resource(
        upgraded, _LINK, "href", "language-menu.css",
        f'<link rel="stylesheet" href="{prefix}language-menu.css?v={VERSION}">',
    )
    upgraded = _upsert_resource(
        upgraded, _SCRIPT, "src", "language-menu.js",
        f'<script defer src="{prefix}language-menu.js?v={VERSION}"></script>',
    )
    if _outside_navigation(source, language) != _outside_navigation(upgraded, language):
        raise ValueError(f"{language}/{slug}: content outside navigation/resources changed")
    return upgraded


def outputs() -> dict[Path, str]:
    return {
        page_path(language, slug): upgrade_page(
            page_path(language, slug).read_text(encoding="utf-8"), language, slug,
        )
        for language in LANGUAGES for slug in SLUGS
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify all 176 menus/resources without writing")
    args = parser.parse_args()
    rendered = outputs()  # Validate every page before writing any page.
    changed = [path for path, text in rendered.items() if path.read_text(encoding="utf-8") != text]
    if args.check:
        if changed:
            raise SystemExit("Stale blockchain navigation:\n" + "\n".join(str(p.relative_to(ROOT)) for p in changed))
        print(f"OK: {len(rendered)} blockchain pages; navigation is current")
        return
    for path in changed:
        path.write_text(rendered[path], encoding="utf-8")
    print(f"Updated navigation/resources: {len(changed)} of {len(rendered)} blockchain pages; prose preserved")


if __name__ == "__main__":
    main()
