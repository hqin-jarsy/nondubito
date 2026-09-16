#!/usr/bin/env python3
"""Add the adopted Chinese chapter texts without rebuilding the existing essays.

The checked-in JSON is the editorial source of truth. No network service or
external checkout is required. Run with --check to audit without writing.
Only marked source blocks, their stylesheet links, and the chapter-local
Traditional Chinese conversion guard are managed here.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "essays" / "daodejing"
DATA = ROOT / "data" / "daodejing-chapter-texts.json"
UI = ROOT / "data" / "daodejing-source-ui.json"
LANGUAGES = ("zh", "zh-hant", "en", "ja", "fr", "de", "es", "ko")
EDITIONS = ("", "ja", "fr", "de", "es", "ko")
START = "<!-- daodejing-source:start -->"
END = "<!-- daodejing-source:end -->"
BLOCK = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
BODY = re.compile(r'<div\b[^>]*class="essay-body(?:\s[^\"]*)?"[^>]*>')
GUARD_OLD = ".lang-en, .lang-card, .lang-toggle, .footer-langs, script, style"
GUARD_NEW = GUARD_OLD + ", .ddj-source"
NOTE_REFERENCES = {
    25: ("https://zh.wikisource.org/zh-hans/老子_(帛書本)#25_-_章二十五", "《老子》（帛書本）· A / B · 25"),
    42: ("https://irlib.pccu.edu.tw/retrieve/58136/gsweb.pdf#page=75", "廖雅慧 · 2010 · p. 68, n. 85 (PDF)"),
    67: ("https://zh.wikisource.org/zh-hans/老子_(帛書本)#67_-_章六十七", "《老子》（帛書本）· A / B · 67"),
}


def load_data() -> tuple[list[dict], dict]:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    chapters = data["chapters"]
    if data["schema_version"] != 1 or [c["number"] for c in chapters] != list(range(1, 82)):
        raise ValueError("Expected chapters 1–81, in received-text order")
    for chapter in chapters:
        paper = (chapter["number"] - 1) // 9 + 1
        if chapter["paper"] != paper or chapter["source_url"] != f"https://self-as-an-end.net/papers/sae-daodejing-{paper}.html":
            raise ValueError(f"Invalid source for chapter {chapter['number']}")
        paragraphs = chapter["paragraphs"]
        if not paragraphs or any(not isinstance(p, str) or not p.strip() or re.search(r"[<>]|&(?:[a-z]+|#\d+);", p) for p in paragraphs):
            raise ValueError(f"Unprocessed text in chapter {chapter['number']}")
    ui = json.loads(UI.read_text(encoding="utf-8"))
    if set(ui) != set(LANGUAGES):
        raise ValueError("Source labels must cover all eight reading languages")
    for lang, copy in ui.items():
        for key in ("title", "edition", "details_label", "method", "source_label"):
            if not isinstance(copy.get(key), str) or not copy[key].strip():
                raise ValueError(f"Missing {lang} {key}")
        if set(copy["chapter_notes"]) != {"1", "4", "25", "42", "67"}:
            raise ValueError(f"Incomplete editorial notes: {lang}")
    return chapters, ui


def localized(ui: dict, edition: str, key: str, chapter: int | None = None) -> str:
    languages = (edition,) if edition else ("zh", "zh-hant", "en")
    spans = []
    for language in languages:
        value = ui[language][key] if chapter is None else ui[language][key][str(chapter)]
        lang = {"zh": "zh-Hans", "zh-hant": "zh-Hant"}.get(language, language)
        attr = f' data-ddj-ui="{language}"' if not edition else ""
        spans.append(f'<span{attr} lang="{lang}">{html.escape(value)}</span>')
    return "".join(spans)


def render_block(chapter: dict, ui: dict, edition: str) -> str:
    number = chapter["number"]
    url = html.escape(chapter["source_url"], quote=True)
    text = "\n".join(f"          <p>{html.escape(p)}</p>" for p in chapter["paragraphs"])
    note = ""
    if str(number) in ui["zh"]["chapter_notes"]:
        note = f'\n          <p class="ddj-source-note">{localized(ui, edition, "chapter_notes", number)}</p>'
    if number in NOTE_REFERENCES:
        ref_url, ref_label = NOTE_REFERENCES[number]
        note += f'\n          <p class="ddj-source-reference"><a href="{html.escape(ref_url, quote=True)}">{html.escape(ref_label)}</a></p>'
    return f'''{START}
      <section class="ddj-source" data-ddj-chapter="{number}" aria-labelledby="ddj-source-title">
        <h2 id="ddj-source-title">{localized(ui, edition, "title")}</h2>
        <p class="ddj-source-edition">{localized(ui, edition, "edition")}</p>
        <blockquote class="ddj-source-text" lang="lzh" translate="no" cite="{url}">
{text}
        </blockquote>
        <details class="ddj-source-details">
          <summary>{localized(ui, edition, "details_label")}</summary>
          <p>{localized(ui, edition, "method")}</p>{note}
          <p><a href="{url}">{localized(ui, edition, "source_label")}</a></p>
        </details>
      </section>
      {END}'''


def update_page(source: str, chapter: dict, ui: dict, edition: str) -> str:
    rendered = render_block(chapter, ui, edition)
    if source.count(START) != source.count(END) or source.count(START) > 1:
        raise ValueError("Duplicate or broken managed source block")
    if START in source:
        source, count = BLOCK.subn(lambda _: rendered, source)
        if count != 1:
            raise ValueError("Could not replace source block")
    else:
        body = BODY.search(source)
        heading = re.search(r'<(?:header|div)\b[^>]*class="essay-header"[^>]*>', source)
        if not body or not heading or not source.find('<article>') < heading.start() < body.start():
            raise ValueError("Cannot locate chapter header/body boundary")
        source = source[:body.start()] + rendered + "\n\n      " + source[body.start():]
    css = ("../" if edition else "") + "chapter-source.css"
    link = f'<link rel="stylesheet" href="{css}">'
    if link not in source:
        if source.count("</head>") != 1:
            raise ValueError("Cannot locate stylesheet insertion point")
        source = source.replace("</head>", "  " + link + "\n</head>", 1)
    return source


def update_guard(source: str) -> str:
    if GUARD_NEW in source:
        return source
    if source.count(GUARD_OLD) != 1:
        raise ValueError("Unknown Traditional Chinese reader; refusing a blind edit")
    return source.replace(GUARD_OLD, GUARD_NEW, 1)


def build(check: bool = False) -> list[Path]:
    chapters, ui = load_data()
    updates = []
    # Validate every page before applying any updates.
    for chapter in chapters:
        name = f'ch{chapter["number"]:02d}'
        for edition in EDITIONS:
            path = SERIES / edition / f"{name}.html"
            before = path.read_text(encoding="utf-8")
            after = update_page(before, chapter, ui, edition)
            if before != after:
                updates.append((path, after))
        path = SERIES / "zh-hant-data" / f"{name}.js"
        before = path.read_text(encoding="utf-8")
        after = update_guard(before)
        if before != after:
            updates.append((path, after))
    if not check:
        for path, after in updates:
            path.write_text(after, encoding="utf-8")
    return [path for path, _ in updates]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report stale output; do not write")
    args = parser.parse_args()
    changed = build(args.check)
    if args.check and changed:
        print(f"Stale output: {len(changed)} files")
        for path in changed[:10]:
            print(path.relative_to(ROOT))
        return 1
    print(f"{'Verified' if args.check else 'Updated'}: 81 chapters × 6 HTML editions; {len(changed)} files changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
