#!/usr/bin/env python3
"""Build a representative content-registry snapshot for Non Dubito.

The first registry pass is deliberately a prototype.  It scans ten series that
cover the site's main historical layouts, plus root pages and the Library
taxonomy.  It never edits published HTML.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


SITE_URL = "https://nondubito.net"
SNAPSHOT_DATE = "2026-09-05"

LANGUAGE_DIRS = {
    "de": "de",
    "es": "es",
    "fr": "fr",
    "ja": "ja",
    "ko": "ko",
}

LANGUAGE_CODES = {
    "en": "en",
    "zh": "zh-Hans",
    "zh-hans": "zh-Hans",
    "zh_hans": "zh-Hans",
    "zh-hant": "zh-Hant",
    "hant": "zh-Hant",
    "de": "de",
    "es": "es",
    "fr": "fr",
    "ja": "ja",
    "ko": "ko",
}

PROTOTYPE_SERIES = (
    "essays/sae-value",
    "essays/everyday/relationships",
    "essays/ai-human",
    "essays/mingren",
    "essays/literature/kokoro",
    "essays/science-fiction/solaris",
    "essays/anime/neon-genesis-evangelion",
    "essays/wuxia/smiling-proud-wanderer",
    "essays/film/inception",
    "essays/tv/breaking-bad",
)

AI_LEGACY_FILES = {
    "ai_companion.html",
    "ai_crisis.html",
    "ethics.html",
    "introspection.html",
    "inverse_law.html",
    "libido.html",
    "posterior_consciousness.html",
    "turing_test.html",
}

ROOT_PAGES = (
    "index.html",
    "start.html",
    "library.html",
    "about.html",
    "credesivis.html",
)

DOMAIN_PREFIXES = (
    ("essays/everyday/stories/", "stories"),
    ("essays/literature/", "stories"),
    ("essays/science-fiction/", "stories"),
    ("essays/anime/", "stories"),
    ("essays/wuxia/", "stories"),
    ("essays/film/", "stories"),
    ("essays/tv/", "stories"),
    ("essays/games/", "stories"),
    ("essays/everyday/", "everyday"),
    ("essays/ai-human/", "mind-ai"),
    ("essays/ai-consciousness/", "mind-ai"),
    ("essays/consciousness-life/", "mind-ai"),
    ("essays/learning/", "mind-ai"),
    ("essays/mingren/", "history"),
    ("essays/civhist/", "history"),
    ("essays/wwii/", "history"),
    ("essays/emperor/", "history"),
    ("essays/ouya/", "history"),
    ("essays/president/", "history"),
    ("essays/economy/", "history"),
    ("essays/athletics/", "history"),
    ("essays/worldcup/", "history"),
    ("essays/sae-", "sae-philosophy"),
    ("essays/method/", "sae-philosophy"),
    ("essays/epistemology/", "sae-philosophy"),
    ("essays/law/", "sae-philosophy"),
    ("essays/econ/", "sae-philosophy"),
    ("essays/quanli/", "sae-philosophy"),
    ("essays/rights/", "sae-philosophy"),
    ("essays/war/", "sae-philosophy"),
    ("essays/daode/", "sae-philosophy"),
)

MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def clean_text(value: str) -> str:
    value = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def attr_value(tag: str, name: str) -> str | None:
    match = re.search(rf"\b{name}\s*=\s*(['\"])(.*?)\1", tag, flags=re.I | re.S)
    return html.unescape(match.group(2)).strip() if match else None


def extract_meta(source: str, *, name: str | None = None, prop: str | None = None) -> str | None:
    for tag in re.findall(r"<meta\b[^>]*>", source, flags=re.I):
        if name and (attr_value(tag, "name") or "").lower() != name.lower():
            continue
        if prop and (attr_value(tag, "property") or "").lower() != prop.lower():
            continue
        content = attr_value(tag, "content")
        if content:
            return content
    return None


def extract_canonical(source: str) -> str | None:
    for tag in re.findall(r"<link\b[^>]*>", source, flags=re.I):
        rel = (attr_value(tag, "rel") or "").lower().split()
        if "canonical" in rel:
            return attr_value(tag, "href")
    return None


def extract_html_lang(source: str) -> str | None:
    match = re.search(r"<html\b[^>]*>", source, flags=re.I)
    return attr_value(match.group(0), "lang") if match else None


def normalized_lang(raw: str | None) -> str | None:
    if not raw:
        return None
    lowered = raw.lower().replace("_", "-")
    if lowered.startswith("zh-hant"):
        return "zh-Hant"
    if lowered.startswith("zh"):
        return "zh-Hans"
    return LANGUAGE_CODES.get(lowered.split("-")[0])


def extract_document_title(source: str) -> str | None:
    match = re.search(r"<title\b[^>]*>(.*?)</title>", source, flags=re.I | re.S)
    if not match:
        return None
    title = clean_text(match.group(1))
    title = re.sub(r"\s+[—·]\s+Non Dubito$", "", title).strip()
    return title or None


class LocalizedHeadingParser(HTMLParser):
    """Collect H1 text together with a language inherited from ancestors."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str | None]] = []
        self.capture_language: str | None = None
        self.capture_parts: list[str] = []
        self.titles: dict[str, str] = {}

    @staticmethod
    def language_from_attrs(attrs: list[tuple[str, str | None]]) -> str | None:
        attr_map = {key: value or "" for key, value in attrs}
        classes = set(attr_map.get("class", "").split())
        if "lang-hant" in classes or "cl-hant" in classes:
            return "zh-Hant"
        if "lang-en" in classes:
            return "en"
        if "lang-zh" in classes or "cl-zh" in classes:
            return "zh-Hans"
        return None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        own_language = self.language_from_attrs(attrs)
        inherited = own_language or (self.stack[-1][1] if self.stack else None)
        self.stack.append((tag.lower(), inherited))
        if tag.lower() == "h1":
            self.capture_language = inherited
            self.capture_parts = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        return

    def handle_data(self, data: str) -> None:
        if self.capture_language:
            self.capture_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered == "h1" and self.capture_language:
            title = re.sub(r"\s+", " ", "".join(self.capture_parts)).strip()
            if title:
                self.titles.setdefault(self.capture_language, title)
            self.capture_language = None
            self.capture_parts = []

        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == lowered:
                del self.stack[index:]
                break


def extract_localized_titles(source: str) -> dict[str, str]:
    parser = LocalizedHeadingParser()
    try:
        parser.feed(source)
    except Exception:
        # A malformed legacy page should remain auditable, not abort the scan.
        return {}
    return parser.titles


@lru_cache(maxsize=None)
def load_variants(dictionary: Path) -> dict[str, str]:
    if not dictionary.exists():
        return {}
    source = dictionary.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\bvar\s+variants\s*=\s*(\{.*?\});", source, flags=re.S)
    if not match:
        return {}
    try:
        variants = json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}
    return {
        key: value
        for key, value in variants.items()
        if isinstance(key, str) and isinstance(value, str)
    }


def traditional_variant(root: Path, path: Path, simplified: str) -> str | None:
    dictionaries = (
        path.parent / "zh-hant-data" / f"{path.stem}.js",
        root / "zh-hant.js",
    )
    for dictionary in dictionaries:
        value = load_variants(dictionary).get(simplified)
        if value:
            return value
    return None


def language_from_directory(relative: Path, root: Path) -> tuple[str | None, Path | None]:
    parts = list(relative.parts)

    # Early AI pages keep their bilingual originals directly under essays/,
    # while later language editions live under essays/ai-human/<lang>/.
    if (
        len(parts) == 4
        and parts[0] == "essays"
        and parts[1] == "ai-human"
        and parts[2] in LANGUAGE_DIRS
        and parts[3] in AI_LEGACY_FILES
    ):
        candidate = Path("essays", parts[3])
        if (root / candidate).exists():
            return LANGUAGE_DIRS[parts[2]], candidate

    # Great Lives predates series-local language directories.  Its editions
    # live in the old global language hubs, e.g. essays/ja/confucius.html.
    if (
        len(parts) == 3
        and parts[0] == "essays"
        and parts[1] in LANGUAGE_DIRS
    ):
        candidate = Path("essays", "mingren", parts[2])
        if (root / candidate).exists():
            return LANGUAGE_DIRS[parts[1]], candidate

    for index, part in enumerate(parts[:-1]):
        if part not in LANGUAGE_DIRS:
            continue
        candidate = Path(*parts[:index], *parts[index + 1 :])
        if (root / candidate).exists():
            return LANGUAGE_DIRS[part], candidate
    return None, None


def detect_same_page_languages(source: str, path: Path) -> set[str]:
    explicit = re.search(r"<html\b[^>]*\bdata-editions\s*=\s*['\"]([^'\"]+)['\"]", source, flags=re.I)
    if explicit:
        languages = {
            language
            for raw in re.split(r"[\s,]+", explicit.group(1).strip())
            if (language := normalized_lang(raw))
        }
        if languages:
            return languages

    languages: set[str] = set()
    for raw in re.findall(r"data-lang\s*=\s*['\"]([^'\"]+)['\"]", source, flags=re.I):
        language = normalized_lang(raw)
        if language:
            languages.add(language)

    for raw in re.findall(r"\blang-(en|zh|hant|zh-hant)\b", source, flags=re.I):
        language = normalized_lang(raw)
        if language:
            languages.add(language)

    dictionary = path.parent / "zh-hant-data" / f"{path.stem}.js"
    if dictionary.exists():
        languages.add("zh-Hant")

    document_language = normalized_lang(extract_html_lang(source))
    if document_language:
        languages.add(document_language)
    return languages


def extract_date(source: str) -> str | None:
    matches = re.findall(
        r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),\s+(20\d{2})\b",
        source,
    )
    if not matches:
        return None
    month, day, year = matches[0]
    return datetime(int(year), MONTHS[month], int(day)).date().isoformat()


def infer_domain(relative: Path) -> str:
    value = relative.as_posix()
    if not value.startswith("essays/"):
        return "site"
    if relative.name in AI_LEGACY_FILES and len(relative.parts) == 2:
        return "mind-ai"
    for prefix, domain in DOMAIN_PREFIXES:
        if value.startswith(prefix):
            return domain
    return "unmapped"


def infer_record_type(relative: Path) -> str:
    if len(relative.parts) == 1:
        return "site-page"
    if relative.name != "index.html":
        return "essay"
    if len(relative.parts) == 2 and relative.parts[0] == "essays":
        return "language-hub"
    if len(relative.parts) == 3:
        return "collection-index"
    return "series-index"


def infer_taxonomy(relative: Path) -> tuple[str | None, str | None]:
    if not relative.parts or relative.parts[0] != "essays":
        return None, None
    parts = [part for part in relative.parts[1:-1] if part not in LANGUAGE_DIRS]
    if not parts:
        return None, None
    if len(relative.parts) == 2 and relative.name in AI_LEGACY_FILES:
        return "ai-human", "ai-human"
    category = parts[0]
    series = parts[1] if len(parts) > 1 else parts[0]
    return category, series


def infer_sequence(path: Path) -> int | None:
    match = re.match(r"(?:ep)?0*(\d+)(?:[-_.]|$)", path.stem, flags=re.I)
    return int(match.group(1)) if match else None


def make_content_id(relative: Path) -> str:
    parts = list(relative.with_suffix("").parts)
    if parts and parts[-1] == "index":
        parts[-1] = "_index"
    return ".".join(re.sub(r"[^a-zA-Z0-9_-]+", "-", part).strip("-") for part in parts)


def scan_page(root: Path, path: Path) -> dict[str, Any]:
    relative = path.relative_to(root)
    source = path.read_text(encoding="utf-8", errors="replace")
    edition_language, canonical_candidate = language_from_directory(relative, root)
    identity_path = canonical_candidate or relative

    localized_titles = extract_localized_titles(source)
    if "zh-Hans" in localized_titles and "zh-Hant" not in localized_titles:
        translated_title = traditional_variant(root, path, localized_titles["zh-Hans"])
        if translated_title:
            localized_titles["zh-Hant"] = translated_title
    document_title = extract_document_title(source)
    if edition_language and document_title:
        localized_titles.setdefault(edition_language, document_title)

    if edition_language:
        languages = {edition_language}
    else:
        languages = detect_same_page_languages(source, path)
        html_language = normalized_lang(extract_html_lang(source))
        if not languages and html_language:
            languages.add(html_language)

    return {
        "path": relative.as_posix(),
        "identity_path": identity_path.as_posix(),
        "record_type": infer_record_type(identity_path),
        "domain": infer_domain(identity_path),
        "category": infer_taxonomy(identity_path)[0],
        "series": infer_taxonomy(identity_path)[1],
        "sequence": infer_sequence(identity_path),
        "html_lang": normalized_lang(extract_html_lang(source)),
        "languages": sorted(languages),
        "titles": localized_titles,
        "document_title": document_title,
        "description": extract_meta(source, name="description"),
        "canonical": extract_canonical(source),
        "displayed_date": extract_date(source),
    }


def strip_non_title_spans(fragment: str) -> dict[str, str]:
    titles: dict[str, str] = {}
    for tag in re.findall(r"<span\b[^>]*>.*?</span>", fragment, flags=re.I | re.S):
        opening = tag[: tag.find(">") + 1]
        classes = set((attr_value(opening, "class") or "").split())
        text = clean_text(tag)
        if not text:
            continue
        if "en" in classes:
            titles.setdefault("en", text)
        if "zh" in classes or "cl-zh" in classes:
            titles.setdefault("zh-Hans", text)
        if "cl-hant" in classes:
            titles.setdefault("zh-Hant", text)
    return titles


def parse_library_categories(library_path: Path) -> list[dict[str, Any]]:
    source = library_path.read_text(encoding="utf-8", errors="replace")
    starts = list(
        re.finditer(
            r'<span class="lib-section-tag">Category\s+(\d+)</span>',
            source,
            flags=re.I,
        )
    )
    categories: list[dict[str, Any]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(source)
        block = source[start.end() : end]
        name_match = re.search(
            r'<(?:a|div)\b([^>]*)class="[^"]*lib-section-name[^"]*"([^>]*)>(.*?)</(?:a|div)>',
            block,
            flags=re.I | re.S,
        )
        name_fragment = name_match.group(3) if name_match else ""
        opening_attrs = " ".join(name_match.group(1, 2)) if name_match else ""
        category_href = attr_value(f"<x {opening_attrs}>", "href") if name_match else None
        cards = re.findall(
            r'<a\b[^>]*href="([^"]+)"[^>]*class="[^"]*series-card[^"]*"',
            block,
            flags=re.I,
        )
        categories.append(
            {
                "number": int(start.group(1)),
                "titles": strip_non_title_spans(name_fragment),
                "label": clean_text(name_fragment),
                "href": category_href,
                "series_count": len(cards),
                "series_hrefs": cards,
            }
        )
    return categories


def group_pages(pages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for page in pages:
        grouped[page["identity_path"]].append(page)

    records: list[dict[str, Any]] = []
    collisions: list[dict[str, str]] = []
    for identity_path in sorted(grouped):
        members = sorted(grouped[identity_path], key=lambda item: item["path"])
        base = next((member for member in members if member["path"] == identity_path), members[0])
        titles: dict[str, str] = {}
        editions: dict[str, dict[str, Any]] = {}

        for member in members:
            for language, title in member["titles"].items():
                titles.setdefault(language, title)
            for language in member["languages"]:
                edition = {
                    "path": member["path"],
                    "url": member["canonical"] or f"{SITE_URL}/{member['path']}",
                    "displayed_date": member["displayed_date"],
                }
                if language in editions and editions[language]["path"] != member["path"]:
                    collisions.append(
                        {
                            "identity_path": identity_path,
                            "language": language,
                            "first_path": editions[language]["path"],
                            "second_path": member["path"],
                        }
                    )
                else:
                    editions[language] = edition

        if not titles and base["document_title"]:
            fallback_language = base["html_lang"] or "und"
            titles[fallback_language] = base["document_title"]

        record = {
            "content_id": make_content_id(Path(identity_path)),
            "record_type": base["record_type"],
            "canonical_path": identity_path,
            "canonical_url": base["canonical"] or f"{SITE_URL}/{identity_path}",
            "primary_domain": base["domain"],
            "category": base["category"],
            "series": base["series"],
            "sequence": base["sequence"],
            "titles": dict(sorted(titles.items())),
            "description": base["description"],
            "published_at": base["displayed_date"],
            "updated_at": None,
            "update_kind": None,
            "editions": dict(sorted(editions.items())),
            "entry_level": None,
            "tags": [],
            "featured": False,
            "index_status": "candidate",
        }
        records.append(record)

    return records, collisions


def collect_scope(root: Path) -> list[Path]:
    paths = [root / relative for relative in ROOT_PAGES if (root / relative).exists()]
    for relative in PROTOTYPE_SERIES:
        series_root = root / relative
        if not series_root.exists():
            continue
        paths.extend(
            path
            for path in series_root.rglob("*.html")
            if "zh-hant-data" not in path.parts
        )

    # Add the non-localized originals for the legacy AI layout.
    paths.extend(
        root / "essays" / filename
        for filename in AI_LEGACY_FILES
        if (root / "essays" / filename).exists()
    )

    # Add matching Great Lives editions from the old global language hubs.
    for base in (root / "essays" / "mingren").glob("*.html"):
        if base.name == "index.html":
            continue
        for language in LANGUAGE_DIRS:
            edition = root / "essays" / language / base.name
            if edition.exists():
                paths.append(edition)
    return sorted(set(paths))


def build_registry(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    pages = [scan_page(root, path) for path in collect_scope(root)]
    records, collisions = group_pages(pages)
    categories = parse_library_categories(root / "library.html")

    missing_canonical = sorted(page["path"] for page in pages if not page["canonical"])
    missing_date = sorted(
        record["canonical_path"]
        for record in records
        if record["record_type"] == "essay" and not record["published_at"]
    )
    unmapped = sorted(
        record["canonical_path"]
        for record in records
        if record["primary_domain"] == "unmapped"
    )
    edition_counts = Counter(len(record["editions"]) for record in records)
    language_counts = Counter(
        language for record in records for language in record["editions"]
    )
    type_counts = Counter(record["record_type"] for record in records)

    registry = {
        "schema_version": 1,
        "status": "prototype",
        "snapshot_date": SNAPSHOT_DATE,
        "site_url": SITE_URL,
        "scope": {
            "root_pages": list(ROOT_PAGES),
            "representative_series": list(PROTOTYPE_SERIES),
            "note": "Generated candidate data; not yet the source of truth for public pages.",
        },
        "domains": [
            {"id": "sae-philosophy", "label_zh": "SAE 与哲学", "label_en": "SAE & Philosophy"},
            {"id": "everyday", "label_zh": "日常生活", "label_en": "Everyday Life"},
            {"id": "mind-ai", "label_zh": "心灵、AI 与技术", "label_en": "Mind, AI & Technology"},
            {"id": "history", "label_zh": "历史、权力与文明", "label_en": "History, Power & Civilization"},
            {"id": "stories", "label_zh": "文学、影视与叙事", "label_en": "Literature, Screen & Narrative"},
        ],
        "library_categories": categories,
        "records": records,
    }
    audit = {
        "scanned_html_pages": len(pages),
        "canonical_records": len(records),
        "library_category_count": len(categories),
        "library_series_card_count": sum(category["series_count"] for category in categories),
        "record_type_counts": dict(sorted(type_counts.items())),
        "language_record_counts": dict(sorted(language_counts.items())),
        "edition_count_distribution": {
            str(count): total for count, total in sorted(edition_counts.items())
        },
        "missing_canonical": missing_canonical,
        "missing_published_date": missing_date,
        "unmapped_domain": unmapped,
        "edition_collisions": collisions,
    }
    return registry, audit


def markdown_list(
    values: list[str], empty: str = "None in prototype scope.", limit: int = 36
) -> str:
    if not values:
        return empty
    visible = values[:limit]
    lines = [f"- `{value}`" for value in visible]
    if len(values) > limit:
        lines.append(f"- … {len(values) - limit} additional paths in the generated audit JSON")
    return "\n".join(lines)


def render_audit(audit: dict[str, Any]) -> str:
    collisions = audit["edition_collisions"]
    collision_lines = [
        f"- `{item['identity_path']}` / `{item['language']}`: "
        f"`{item['first_path']}` and `{item['second_path']}`"
        for item in collisions
    ]
    type_rows = "\n".join(
        f"| {key} | {value} |" for key, value in audit["record_type_counts"].items()
    )
    language_rows = "\n".join(
        f"| {key} | {value} |" for key, value in audit["language_record_counts"].items()
    )
    edition_rows = "\n".join(
        f"| {key} | {value} |"
        for key, value in audit["edition_count_distribution"].items()
    )
    return f"""# Content registry prototype audit

Generated from the public HTML snapshot dated {SNAPSHOT_DATE}. The scanner is
read-only with respect to published pages.

## Coverage

| Measure | Count |
| --- | ---: |
| Scanned HTML pages | {audit['scanned_html_pages']} |
| Canonical candidate records | {audit['canonical_records']} |
| Library categories parsed | {audit['library_category_count']} |
| Library series cards parsed | {audit['library_series_card_count']} |

## Record types

| Type | Count |
| --- | ---: |
{type_rows}

## Language editions represented

This counts canonical records with an edition in the named language, not raw
HTML files.

| Language | Records |
| --- | ---: |
{language_rows}

## Editions per canonical record

| Edition count | Records |
| ---: | ---: |
{edition_rows}

## Missing canonical links

{markdown_list(audit['missing_canonical'])}

## Essay records without a detected public date

{markdown_list(audit['missing_published_date'])}

## Unmapped primary domains

{markdown_list(audit['unmapped_domain'])}

## Edition collisions

{chr(10).join(collision_lines) if collision_lines else 'None in prototype scope.'}

## Interpretation

- The prototype proves that per-series language directories can be merged into
  one canonical content identity without changing their URLs.
- Same-page English, Simplified Chinese, and Traditional Chinese modes can be
  represented as editions of that same identity.
- Missing dates and canonical links remain explicit audit findings instead of
  being silently guessed.
- A full-site registry will need a reviewed exception map for legacy language
  hubs and older top-level series.
"""


def validate(registry: dict[str, Any], audit: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if audit["library_category_count"] != 13:
        errors.append(
            f"Expected 13 Library categories, found {audit['library_category_count']}."
        )
    if audit["library_series_card_count"] < 1:
        errors.append("No Library series cards were detected.")
    if not registry["records"]:
        errors.append("Registry contains no records.")
    ids = [record["content_id"] for record in registry["records"]]
    if len(ids) != len(set(ids)):
        errors.append("Registry contains duplicate content_id values.")
    known_domains = {domain["id"] for domain in registry["domains"]} | {"site"}
    bad_domains = sorted(
        {
            record["primary_domain"]
            for record in registry["records"]
            if record["primary_domain"] not in known_domains
        }
    )
    if bad_domains:
        errors.append(f"Registry contains unknown domains: {', '.join(bad_domains)}.")
    empty_editions = [
        record["canonical_path"]
        for record in registry["records"]
        if not record["editions"]
    ]
    if empty_editions:
        errors.append(f"Records without editions: {', '.join(empty_editions[:5])}.")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root (defaults to the script's parent repository).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the generated model without writing output files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    registry, audit = build_registry(root)
    errors = validate(registry, audit)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if args.check:
        print(
            f"OK: {audit['canonical_records']} canonical records from "
            f"{audit['scanned_html_pages']} HTML pages; "
            f"{audit['library_category_count']} Library categories."
        )
        return 0

    data_dir = root / "data"
    reports_dir = root / "reports"
    data_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(exist_ok=True)
    (data_dir / "content-registry-prototype.json").write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (reports_dir / "content-registry-prototype-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (reports_dir / "content-registry-prototype-audit.md").write_text(
        render_audit(audit),
        encoding="utf-8",
    )
    print(
        f"Wrote {audit['canonical_records']} canonical records from "
        f"{audit['scanned_html_pages']} HTML pages."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
