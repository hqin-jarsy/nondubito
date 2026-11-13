#!/usr/bin/env python3
"""Render explicitly incomplete Japanese drafts only, without loading Chinese sources.
No publication, completion promotion, source fallback, or source-text output.
"""
import argparse
import html
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data/hongloumeng/first80-japanese"


def inspect_partial(draft):
    if (draft.get("schemaVersion") != 1 or draft.get("language") != "ja"
            or type(draft.get("number")) is not int
            or draft.get("complete") is not False
            or draft.get("status") != "partial_owner_translation_needed"):
        raise ValueError("Explicit incomplete Japanese draft required")
    n = draft["number"]
    entries, seen = [], set()
    omitted = draft.get("omittedSourceBlockIndices", [])
    if omitted or draft.get("withheldBlockIndices", []):
        raise ValueError("Whole-block omissions require explicit support")
    for position, block in enumerate(draft["blocks"]):
        index = block.get("sourceIndex", block.get("sourceBlockIndex", position))
        if type(index) is not int or index < 0 or index in seen:
            raise ValueError("Invalid or repeated source block index")
        seen.add(index)
        if "sourceSegments" not in block:
            if not isinstance(block.get("text"), str) or not block["text"].strip():
                raise ValueError("Missing Japanese translation; no source fallback")
            continue
        if "text" in block or "sourceText" in block:
            raise ValueError("Segmented blocks cannot carry whole-block text")
        end = 0
        for segment in block["sourceSegments"]:
            start, stop = segment.get("start"), segment.get("end")
            if type(start) is not int or type(stop) is not int or start != end or stop <= start:
                raise ValueError("Invalid segment coordinates")
            end = stop
            if segment.get("status") == "owner_translation_needed":
                allowed = {"start", "end", "sourceTextSha256", "status", "label"}
                if set(segment) != allowed or not re.fullmatch(r"[0-9a-f]{64}", segment["sourceTextSha256"]):
                    raise ValueError("Owner-only placeholder must contain metadata only")
                marker = f"CH{n:03}-P{len(entries)+1:02}"
                label = f"【日訳未完 {marker}】"
                if segment["label"] != label:
                    raise ValueError("Missing unique ordered placeholder label")
                entries.append({"chapter": n, "id": marker, "label": label,
                                "sourceBlockIndex": index, "start": start, "end": stop,
                                "sourceTextSha256": segment["sourceTextSha256"]})
            elif not isinstance(segment.get("text"), str) or not segment["text"].strip():
                raise ValueError("Missing Japanese segment; no source fallback")
    if not entries:
        raise ValueError("Partial draft must retain at least one placeholder")
    return entries


def render(draft):
    entries = inspect_partial(draft)
    n = draft["number"]
    markers = {(e["sourceBlockIndex"], e["start"], e["end"]): e for e in entries}
    escape = lambda text: html.escape(text).replace(chr(10), "<br>")
    blocks = []
    for position, block in enumerate(draft["blocks"]):
        index = block.get("sourceIndex", block.get("sourceBlockIndex", position))
        parts = []
        if "sourceSegments" in block:
            for segment in block["sourceSegments"]:
                if segment.get("status") == "owner_translation_needed":
                    e = markers[(index, segment["start"], segment["end"])]
                    parts.append("<mark id=\"" + e["id"] + "\">" + escape(e["label"]) + "</mark>")
                else:
                    parts.append(escape(segment["text"]))
        else:
            parts.append(escape(block["text"]))
        blocks.append(f"<section id=\"b{index}\" data-source-block=\"{index}\"><p class=\"label\">Block {index} (0-based)</p><div>" + "".join(parts) + "</div></section>")
    links = " ".join("<a href=\"#" + e["id"] + "\">" + escape(e["id"]) + "</a>" for e in entries)
    return ("<!doctype html><html lang=\"ja\"><meta charset=\"utf-8\"><meta name=\"robots\" content=\"noindex,nofollow\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>第{n}回・日訳未完</title>"
            "<style>body{max-width:46em;margin:2em auto;padding:0 1em;font:18px/1.9 serif;background:#fcfaf4}section{margin:1.5em 0}.label{font-size:.75em;color:#666}mark{background:#ffe99a;padding:.2em;overflow-wrap:anywhere}a{margin-right:1em}</style>"
            f"<h1>第{n}回・日本語部分稿</h1>"
            "<p><strong>未完成・非公開校閲用。作者による補完待ち。公開版・完成版ではありません。</strong></p>"
            "<p>日訳未完の各位置を黄色の一意なマーカーで表示します。中国語原文は表示しません。</p>"
            "<nav>" + links + "</nav>" + "".join(blocks) + "</html>")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapters", type=int, nargs="+",
                        help="Defaults to every chapter that still has a chNNN.partial.json draft")
    args = parser.parse_args()
    if args.chapters is None:
        args.chapters = sorted(int(p.name[2:5]) for p in (DATA / "chapters").glob("ch[0-9][0-9][0-9].partial.json"))
    index = []
    outputs = []
    for n in args.chapters:
        if not 1 <= n <= 80:
            parser.error("Expected chapter numbers within 1–80")
        draft = json.loads((DATA / "chapters" / f"ch{n:03}.partial.json").read_text())
        if draft["number"] != n:
            raise ValueError("Chapter identity mismatch")
        entries = inspect_partial(draft)
        index.extend(entries)
        outputs.append((DATA / "private-review" / f"ch{n:03}.partial.html", render(draft)))
    for path, output in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output)
    report = {"status": "partial_placeholder_structure_checked_not_complete",
              "scope": "Metadata and existing Japanese translation only; Chinese source not loaded. Not source alignment or literary acceptance.",
              "coordinateSystem": "Python Unicode code points, zero-based, end-exclusive",
              "placeholders": index}
    (DATA / "placeholder-index.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Rendered {len(outputs)} incomplete private review pages; {len(index)} unique placeholders")


if __name__ == "__main__":
    main()
