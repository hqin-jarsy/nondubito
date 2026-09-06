#!/usr/bin/env python3
"""Validate the hand-curated publication ledger and its rendered Latest page."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = {"en", "zh", "zh-hant", "ja", "fr", "de", "es", "ko"}
KINDS = {"new", "revised", "expanded"}
DOMAINS = {"sae", "everyday", "mind", "history", "stories", "tv", "literature"}


def check() -> list[str]:
    errors: list[str] = []
    source = ROOT / "data" / "site-updates.json"
    page = ROOT / "latest.html"
    data = json.loads(source.read_text(encoding="utf-8"))
    updates = data.get("updates", [])

    ids: list[str] = []
    dates: list[date] = []
    for index, item in enumerate(updates, 1):
        label = f"updates[{index}]"
        update_id = item.get("id")
        if not isinstance(update_id, str) or not update_id:
            errors.append(f"{label}: missing id")
        elif update_id in ids:
            errors.append(f"{label}: duplicate id {update_id}")
        else:
            ids.append(update_id)

        try:
            dates.append(date.fromisoformat(item.get("date", "")))
        except ValueError:
            errors.append(f"{label}: invalid ISO date")

        if item.get("kind") not in KINDS:
            errors.append(f"{label}: invalid kind {item.get('kind')!r}")
        if item.get("domain") not in DOMAINS:
            errors.append(f"{label}: invalid domain {item.get('domain')!r}")

        target = item.get("url", "")
        if not target or target.startswith(("/", "http:", "https:")):
            errors.append(f"{label}: url must be a repository-relative local path")
        elif not (ROOT / target).is_file():
            errors.append(f"{label}: missing target {target}")

        languages = item.get("languages", [])
        if not languages or any(language not in LANGUAGES for language in languages):
            errors.append(f"{label}: invalid language list")
        for field in ("title", "summary"):
            localized = item.get(field, {})
            for language in ("en", "zh", "zh-hant"):
                if not isinstance(localized.get(language), str) or not localized[language].strip():
                    errors.append(f"{label}: {field}.{language} is required")

    if any(a < b for a, b in zip(dates, dates[1:])):
        errors.append("updates must be ordered newest first")

    rendered_ids = re.findall(
        r'data-update-id="([^"]+)"', page.read_text(encoding="utf-8")
    )
    if rendered_ids != ids:
        errors.append("latest.html card order does not match data/site-updates.json")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="kept for consistency with other site scripts")
    parser.parse_args()
    errors = check()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: site update ledger and latest.html agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
