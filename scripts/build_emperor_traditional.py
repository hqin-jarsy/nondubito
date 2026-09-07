#!/usr/bin/env python3
"""Add and verify the offline Traditional Chinese reading mode for Chinese Emperors."""

from __future__ import annotations

import argparse
import ctypes
import json
import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "essays" / "emperor"
UTF8 = 0x08000100
POST_REPLACEMENTS = {"余項": "餘項", "乾政": "干政"}


class TextCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocked = 0
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.blocked += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.blocked:
            self.blocked -= 1

    def handle_data(self, data: str) -> None:
        if not self.blocked and re.search(r"[\u3400-\u9fff]", data):
            self.text.append(data)


class TraditionalConverter:
    """Use macOS CoreFoundation's offline Hans–Hant transform."""

    def __init__(self) -> None:
        self.cf = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
        self.cf.CFStringCreateMutable.argtypes = [ctypes.c_void_p, ctypes.c_long]
        self.cf.CFStringCreateMutable.restype = ctypes.c_void_p
        self.cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint]
        self.cf.CFStringCreateWithCString.restype = ctypes.c_void_p
        self.cf.CFStringAppend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.cf.CFStringTransform.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ubyte]
        self.cf.CFStringTransform.restype = ctypes.c_ubyte
        self.cf.CFStringGetLength.argtypes = [ctypes.c_void_p]
        self.cf.CFStringGetLength.restype = ctypes.c_long
        self.cf.CFStringGetMaximumSizeForEncoding.argtypes = [ctypes.c_long, ctypes.c_uint]
        self.cf.CFStringGetMaximumSizeForEncoding.restype = ctypes.c_long
        self.cf.CFStringGetCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_uint]
        self.cf.CFStringGetCString.restype = ctypes.c_ubyte
        self.cf.CFRelease.argtypes = [ctypes.c_void_p]
        self.transform = self._string("Hans-Hant")

    def _string(self, value: str) -> int:
        result = self.cf.CFStringCreateWithCString(None, value.encode("utf-8"), UTF8)
        if not result:
            raise ValueError("CoreFoundation could not create a string")
        return result

    def convert(self, value: str) -> str:
        mutable = self.cf.CFStringCreateMutable(None, 0)
        source_ref = self._string(value)
        try:
            self.cf.CFStringAppend(mutable, source_ref)
            if not self.cf.CFStringTransform(mutable, None, self.transform, 0):
                raise ValueError("CoreFoundation Hans-Hant transform failed")
            length = self.cf.CFStringGetLength(mutable)
            capacity = self.cf.CFStringGetMaximumSizeForEncoding(length, UTF8) + 1
            buffer = ctypes.create_string_buffer(capacity)
            if not self.cf.CFStringGetCString(mutable, buffer, capacity, UTF8):
                raise ValueError("CoreFoundation could not export transformed text")
            converted = buffer.value.decode("utf-8")
            for phrase, target in POST_REPLACEMENTS.items():
                converted = converted.replace(phrase, target)
            return converted
        finally:
            self.cf.CFRelease(source_ref)
            self.cf.CFRelease(mutable)

    def close(self) -> None:
        self.cf.CFRelease(self.transform)


def reading_script(variants: dict[str, str], page: Path) -> str:
    data = json.dumps(variants, ensure_ascii=False, sort_keys=True)
    relative = page.relative_to(ROOT)
    return f'''/* Generated offline from {relative}; no runtime service dependency. */
(function() {{
  'use strict';
  var variants = {data};
  var originals = new WeakMap();
  var originalTitle = document.title;

  function updateTraditionalReadingMode() {{
    var mode = document.documentElement.getAttribute('data-lang') || 'zh';
    var traditional = mode === 'zh-hant';
    document.documentElement.lang = traditional ? 'zh-Hant' : (mode === 'zh' ? 'zh-Hans' : 'en');
    document.title = traditional && Object.prototype.hasOwnProperty.call(variants, originalTitle)
      ? variants[originalTitle]
      : originalTitle;
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while ((node = walker.nextNode())) {{
      var parent = node.parentElement;
      if (!parent || parent.closest('.lang-en, .lang-toggle, script, style')) continue;
      if (!originals.has(node)) originals.set(node, node.nodeValue);
      var source = originals.get(node);
      node.nodeValue = traditional && Object.prototype.hasOwnProperty.call(variants, source)
        ? variants[source]
        : source;
    }}
  }}
  document.addEventListener('DOMContentLoaded', function() {{
    updateTraditionalReadingMode();
    new MutationObserver(function(records) {{
      if (records.some(function(record) {{ return record.attributeName === 'data-lang'; }})) updateTraditionalReadingMode();
    }}).observe(document.documentElement, {{attributes:true, attributeFilter:['data-lang']}});
  }});
}})();
'''


def upgrade_html(source: str, stem: str) -> str:
    source = source.replace(
        '[data-lang="zh"] .lang-en { display:none; }',
        '[data-lang="zh"] .lang-en, [data-lang="zh-hant"] .lang-en { display:none; }',
    )
    if '<button class="lang-btn" data-lang="zh-hant">' not in source:
        source = re.sub(
            r'(<button class="lang-btn" data-lang="zh">中文</button>\s*<span class="lang-sep">\|</span>)(\s*)(<button class="lang-btn" data-lang="en">EN</button>)',
            r'\1\2<button class="lang-btn" data-lang="zh-hant">繁體</button>\2<span class="lang-sep">|</span>\2\3',
            source,
            count=1,
        )
    script_tag = f'<script defer src="zh-hant-data/{stem}.js"></script>'
    if script_tag not in source:
        source = source.replace('</body>', f'{script_tag}\n</body>')
    return source


def render() -> dict[Path, str]:
    converter = TraditionalConverter()
    outputs: dict[Path, str] = {}
    pages = [SERIES / "index.html", *sorted(SERIES.glob("ep*.html"))]
    try:
        for page in pages:
            html = upgrade_html(page.read_text(encoding="utf-8"), page.stem)
            collector = TextCollector()
            collector.feed(html)
            variants = {}
            for text in collector.text:
                traditional = converter.convert(text)
                if traditional != text:
                    variants[text] = traditional
            title_match = re.search(r"<title>(.*?)</title>", html, re.S)
            if title_match:
                title = title_match.group(1)
                traditional_title = converter.convert(title)
                if traditional_title != title:
                    variants[title] = traditional_title
            outputs[page] = html
            outputs[SERIES / "zh-hant-data" / f"{page.stem}.js"] = reading_script(variants, page)
    finally:
        converter.close()
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    stale = [path for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
    if args.check:
        if stale:
            raise SystemExit("Stale emperor Traditional Chinese files:\n" + "\n".join(str(path.relative_to(ROOT)) for path in stale))
        print(f"OK: {len(outputs)} emperor Traditional Chinese files")
        return
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"Wrote: {len(outputs)} emperor Traditional Chinese files")


if __name__ == "__main__":
    main()
