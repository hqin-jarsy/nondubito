#!/usr/bin/env python3
"""Regenerate Meaning Theory's offline Traditional Chinese reading dictionaries."""

from __future__ import annotations

import argparse
from pathlib import Path

from build_emperor_traditional import TextCollector, TraditionalConverter, reading_script
from build_content_registry import extract_localized_titles

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "essays" / "meaning"


def render() -> dict[Path, str]:
    converter = TraditionalConverter()
    outputs: dict[Path, str] = {}
    try:
        for page in sorted(SERIES.glob("*.html")):
            source = page.read_text(encoding="utf-8")
            collector = TextCollector()
            collector.feed(source)
            variants = {}
            for text in collector.text:
                traditional = converter.convert(text)
                if traditional != text:
                    variants[text] = traditional
            # Some titles use only shared characters (e.g. 仍在他名下).
            # Keep them explicitly so language-aware search can identify them.
            title = extract_localized_titles(source).get("zh-Hans")
            if title:
                variants[title] = converter.convert(title)
            outputs[SERIES / "zh-hant-data" / f"{page.stem}.js"] = reading_script(variants, page)
    finally:
        converter.close()
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    stale = [p for p, content in outputs.items() if not p.exists() or p.read_text(encoding="utf-8") != content]
    if args.check:
        if stale:
            raise SystemExit("Stale Meaning dictionaries: " + ", ".join(p.name for p in stale))
        print(f"OK: {len(outputs)} Meaning Traditional Chinese dictionaries")
    else:
        for path, content in outputs.items():
            path.write_text(content, encoding="utf-8")
        print(f"Wrote {len(outputs)} Meaning Traditional Chinese dictionaries")


if __name__ == "__main__":
    main()
