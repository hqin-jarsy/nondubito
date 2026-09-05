#!/usr/bin/env python3
"""Audit reader-orientation signals across published essay pages.

This is a structural coverage audit, not a quality score.  It tracks whether a
page exposes the navigation signals introduced during the information-
architecture rollout while keeping legacy URLs and layouts intact.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ESSAYS = ROOT / "essays"
REPORT_JSON = ROOT / "reports" / "reader-context-audit.json"
REPORT_MD = ROOT / "reports" / "reader-context-audit.md"
SNAPSHOT_DATE = "2026-09-05"
LANGUAGE_DIRS = {"de", "es", "fr", "ja", "ko"}
EXCLUDED_PARTS = {"_to_delete"}


def edition_kind(relative: Path) -> str:
    parts = relative.parts[1:-1]
    languages = [part for part in parts if part in LANGUAGE_DIRS]
    return languages[-1] if languages else "canonical-root"


def collection(relative: Path) -> str:
    if len(relative.parts) == 2:
        return "(standalone essays)"
    return relative.parts[1]


def inspect(path: Path) -> dict[str, object]:
    relative = path.relative_to(ROOT)
    source = path.read_text(encoding="utf-8", errors="replace")
    lowered = source.lower()
    is_index = path.name == "index.html"
    return {
        "path": relative.as_posix(),
        "role": "series-or-collection" if is_index else "article",
        "collection": collection(relative),
        "edition": edition_kind(relative),
        "site_shell": "site-shell.css" in lowered,
        "context_styles": "reading-context.css" in lowered,
        "breadcrumbs": 'class="reading-breadcrumbs"' in source,
        "continuation_routes": 'class="reading-next-grid"' in source,
        "language_control": "lang-toggle" in source or "site-language" in source,
        "series_position": any(
            marker in lowered
            for marker in (
                "essay-number",
                "emperor-ep-num",
                "method-num",
                "episode-num",
                "essay-num",
                "article-number",
            )
        ),
        "sequential_navigation": any(
            marker in lowered
            for marker in (
                'class="series-nav',
                'class="essay-nav',
                'class="xiyou-nav',
                'class="method-nav',
                'class="emperor-nav',
                'class="film-nav',
                'class="article-nav',
            )
        ),
    }


def collect() -> list[dict[str, object]]:
    pages: list[dict[str, object]] = []
    for path in sorted(ESSAYS.rglob("*.html")):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        pages.append(inspect(path))
    return pages


def coverage(rows: list[dict[str, object]]) -> dict[str, int]:
    articles = [row for row in rows if row["role"] == "article"]
    indexes = [row for row in rows if row["role"] == "series-or-collection"]
    return {
        "pages": len(rows),
        "articles": len(articles),
        "series_or_collection_pages": len(indexes),
        "site_shell": sum(bool(row["site_shell"]) for row in rows),
        "context_styles": sum(bool(row["context_styles"]) for row in rows),
        "breadcrumbs": sum(bool(row["breadcrumbs"]) for row in rows),
        "continuation_routes": sum(bool(row["continuation_routes"]) for row in rows),
        "articles_with_series_position": sum(bool(row["series_position"]) for row in articles),
        "articles_with_sequential_navigation": sum(bool(row["sequential_navigation"]) for row in articles),
    }


def by_collection(rows: list[dict[str, object]]) -> list[dict[str, int | str]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row["edition"] == "canonical-root" and row["role"] == "article":
            groups[str(row["collection"])].append(row)
    result: list[dict[str, int | str]] = []
    for name, items in groups.items():
        result.append(
            {
                "collection": name,
                "articles": len(items),
                "breadcrumbs": sum(bool(item["breadcrumbs"]) for item in items),
                "continuation_routes": sum(bool(item["continuation_routes"]) for item in items),
                "series_position": sum(bool(item["series_position"]) for item in items),
                "sequential_navigation": sum(bool(item["sequential_navigation"]) for item in items),
            }
        )
    return sorted(result, key=lambda item: (-int(item["articles"]), str(item["collection"])))


def build() -> dict[str, object]:
    pages = collect()
    canonical = [row for row in pages if row["edition"] == "canonical-root"]
    independent = [row for row in pages if row["edition"] != "canonical-root"]
    return {
        "snapshot_date": SNAPSHOT_DATE,
        "scope": "Published HTML below essays/, excluding _to_delete",
        "interpretation": "Structural navigation signals only; presence does not certify editorial quality.",
        "coverage": {
            "all_editions": coverage(pages),
            "canonical_root": coverage(canonical),
            "independent_language_editions": coverage(independent),
        },
        "canonical_articles_by_collection": by_collection(pages),
    }


def markdown(data: dict[str, object]) -> str:
    all_editions = data["coverage"]["all_editions"]
    canonical = data["coverage"]["canonical_root"]
    independent = data["coverage"]["independent_language_editions"]
    lines = [
        "# Reader context rollout audit",
        "",
        f"Snapshot: {data['snapshot_date']}",
        "",
        "This report measures structural orientation signals, not the quality of",
        "the recommendations themselves. A legacy previous/next link counts",
        "separately from the newer three-route continuation pattern.",
        "",
        "## Coverage",
        "",
        "| Scope | Pages | Articles | Series / collection pages | Breadcrumbs | Three-route continuation | New site shell |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| All physical editions | {all_editions['pages']:,} | {all_editions['articles']:,} | {all_editions['series_or_collection_pages']:,} | {all_editions['breadcrumbs']:,} | {all_editions['continuation_routes']:,} | {all_editions['site_shell']:,} |",
        f"| Canonical-root pages | {canonical['pages']:,} | {canonical['articles']:,} | {canonical['series_or_collection_pages']:,} | {canonical['breadcrumbs']:,} | {canonical['continuation_routes']:,} | {canonical['site_shell']:,} |",
        f"| Independent language editions | {independent['pages']:,} | {independent['articles']:,} | {independent['series_or_collection_pages']:,} | {independent['breadcrumbs']:,} | {independent['continuation_routes']:,} | {independent['site_shell']:,} |",
        "",
        "## Existing article navigation",
        "",
        "| Scope | Series position | Legacy previous / next |",
        "| --- | ---: | ---: |",
        f"| All physical editions | {all_editions['articles_with_series_position']:,} | {all_editions['articles_with_sequential_navigation']:,} |",
        f"| Canonical-root pages | {canonical['articles_with_series_position']:,} | {canonical['articles_with_sequential_navigation']:,} |",
        f"| Independent language editions | {independent['articles_with_series_position']:,} | {independent['articles_with_sequential_navigation']:,} |",
        "",
        "## Canonical-root articles by collection",
        "",
        "| Collection | Articles | Breadcrumbs | Three-route continuation | Series position | Legacy previous / next |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in data["canonical_articles_by_collection"]:
        lines.append(
            f"| `{item['collection']}` | {item['articles']:,} | {item['breadcrumbs']:,} | "
            f"{item['continuation_routes']:,} | {item['series_position']:,} | {item['sequential_navigation']:,} |"
        )
    lines.extend(
        [
            "",
            "## How to use this report",
            "",
            "- Prioritize complete reading paths, not the collections with the largest raw deficit.",
            "- Treat breadcrumbs and continuation cards as editorial infrastructure: links must be reviewed in context.",
            "- Roll independent Japanese, French, German, Spanish, and Korean editions into the shared architecture only after the canonical pattern is stable.",
            "- Do not use coverage percentage as a reason to replace a strong existing series map with generic navigation.",
            "",
        ]
    )
    return "\n".join(lines)


def serialized(data: dict[str, object]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the tracked audit is stale")
    args = parser.parse_args()
    data = build()
    outputs = {REPORT_JSON: serialized(data), REPORT_MD: markdown(data)}
    if args.check:
        stale = [path for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"ERROR: {path.relative_to(ROOT)} is missing or stale")
            return 1
        print(f"OK: reader context audit is current ({data['coverage']['all_editions']['pages']} pages)")
        return 0
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")
    print(f"Wrote reader context audit for {data['coverage']['all_editions']['pages']} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
