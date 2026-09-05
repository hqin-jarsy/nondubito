#!/usr/bin/env python3
"""Build the browser-side search index from published HTML pages.

The index deliberately stores titles, descriptions, headings, and explicit
search labels—not complete article bodies.  This keeps the download modest and
makes search useful for finding an essay or series without turning the static
site into a heavyweight full-text application.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from build_content_registry import clean_text, scan_page


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "search-index.json"
CHUNKS_DIR = ROOT / "data" / "search"
SEARCH_LANGUAGES = ("en", "zh-Hans", "zh-Hant", "ja", "fr", "de", "es", "ko")
EXCLUDED_TOP_LEVEL = {".git", ".agents", ".codex", "docs", "prototypes", "reports", "_to_delete"}
EXCLUDED_FILES = {"latest.html", "search.html", "explore.html"}


def collect_pages() -> list[Path]:
    pages: list[Path] = []
    for path in ROOT.rglob("*.html"):
        relative = path.relative_to(ROOT)
        if relative.parts[0] in EXCLUDED_TOP_LEVEL:
            continue
        if len(relative.parts) == 1 and relative.name in EXCLUDED_FILES:
            continue
        pages.append(path)
    return sorted(pages)


def extract_search_text(source: str) -> str:
    values: list[str] = []
    for pattern in (
        r"\bdata-search\s*=\s*(['\"])(.*?)\1",
        r"<(?:h1|h2|h3)\b[^>]*>(.*?)</(?:h1|h2|h3)>",
    ):
        for match in re.finditer(pattern, source, flags=re.I | re.S):
            raw = match.group(2) if match.lastindex == 2 else match.group(1)
            text = clean_text(raw)
            if text:
                values.append(text)
            if sum(map(len, values)) >= 650:
                break
        if sum(map(len, values)) >= 650:
            break
    return " ".join(values)[:700]


def is_redirect(source: str) -> bool:
    return bool(re.search(r'<meta\b[^>]*http-equiv=["\']?refresh', source, flags=re.I))


def build() -> tuple[dict, dict[str, list[dict]]]:
    records: list[dict] = []
    skipped_redirects = 0
    for path in collect_pages():
        source = path.read_text(encoding="utf-8", errors="replace")
        if is_redirect(source) or re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*noindex', source, flags=re.I):
            skipped_redirects += 1
            continue
        page = scan_page(ROOT, path)
        title = page["document_title"] or next(iter(page["titles"].values()), None)
        if not title:
            continue
        languages = page["languages"] or ([page["html_lang"]] if page["html_lang"] else ["und"])
        records.append(
            {
                "id": page["path"].removesuffix(".html").replace("/", "."),
                "url": page["path"],
                "type": page["record_type"],
                "domain": page["domain"],
                "category": page["category"],
                "series": page["series"],
                "sequence": page["sequence"],
                "languages": languages,
                "titles": page["titles"],
                "title": title,
                "description": page["description"] or "",
                "search_text": extract_search_text(source),
            }
        )

    chunks: dict[str, list[dict]] = {language: [] for language in SEARCH_LANGUAGES}
    for item in records:
        for language in SEARCH_LANGUAGES:
            if language not in item["languages"]:
                continue
            chunks[language].append(
                {
                    "u": item["url"],
                    "k": item["type"],
                    "d": item["domain"],
                    "c": item["category"],
                    "s": item["series"],
                    "n": item["sequence"],
                    "t": item["titles"].get(language) or item["title"],
                    "x": item["description"],
                    "q": item["search_text"],
                }
            )

    manifest = {
        "version": 1,
        "scope": "Published HTML titles, descriptions, headings, and explicit search labels",
        "record_count": len(records),
        "languages": {
            language: {
                "count": len(chunks[language]),
                "path": f"data/search/{language.lower()}.json",
            }
            for language in SEARCH_LANGUAGES
        },
        "skipped_redirects_or_noindex": skipped_redirects,
    }
    return manifest, chunks


def serialized(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the tracked index is stale")
    args = parser.parse_args()
    manifest, chunks = build()
    outputs = {OUTPUT: serialized(manifest)}
    outputs.update(
        {
            CHUNKS_DIR / f"{language.lower()}.json": serialized(
                {"version": 1, "language": language, "records": records}
            )
            for language, records in chunks.items()
        }
    )
    if args.check:
        stale = [path for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"ERROR: {path.relative_to(ROOT)} is missing or stale")
            return 1
        print(f"OK: search index is current ({manifest['record_count']} source records)")
        return 0
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    print(f"Wrote search manifest and {len(chunks)} language indexes from {manifest['record_count']} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
