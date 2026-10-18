"""Shared, idempotent Cloudflare Web Analytics support for public HTML.

The token is a public site identifier, not a credential. Internal build inputs,
redirects and noindex pages are deliberately outside the coverage requirement.
"""
from __future__ import annotations

import json
import re
from functools import wraps
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "1c920752456e42b5b5469641245a07c2"
BEACON_URL = "https://static.cloudflareinsights.com/beacon.min.js"
SNIPPET = ('<!-- Cloudflare Web Analytics -->'
           f'<script type="module" src="{BEACON_URL}" '
           f'data-cf-beacon=\'{{"token":"{TOKEN}"}}\'></script>'
           '<!-- End Cloudflare Web Analytics -->')
INTERNAL = {"data", "scripts", "docs", "reports", "prototypes", "_to_delete"}
COLLISION_NAME = re.compile(r" (?:[2-9]|[1-9]\d+)(?=\.html$)", re.I)


class Document(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.offsets = [0]
        self.offsets.extend(m.end() for m in re.finditer("\n", source))
        self.beacons = []
        self.redirect = False
        self.noindex = False
        self.external = False
        self.body_end = None
        self.pending = None
        self.feed(source)
        self.close()

    def source_offset(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            self.redirect |= a.get("http-equiv", "").lower() == "refresh"
            self.noindex |= (a.get("name", "").lower() in ("robots", "googlebot")
                             and "noindex" in a.get("content", "").lower())
        if tag == "link" and "canonical" in a.get("rel", "").lower().split():
            host = urlsplit(a.get("href", "")).netloc.lower()
            self.external |= bool(host and host not in ("nondubito.net", "www.nondubito.net"))
        if tag == "script" and urlsplit(a.get("src", "")).netloc.lower() == "static.cloudflareinsights.com":
            try:
                config = json.loads(a.get("data-cf-beacon", ""))
            except ValueError:
                config = None
            valid = (isinstance(config, dict) and config.get("token") == TOKEN
                     and urlsplit(a.get("src", "")).path == "/beacon.min.js"
                     and ("defer" in a or "async" in a or a.get("type") == "module"))
            self.pending = {"start": self.source_offset(), "end": None, "attrs": a, "valid": valid}
            self.beacons.append(self.pending)

    def handle_endtag(self, tag):
        if tag == "script" and self.pending is not None:
            self.pending["end"] = self.source.index(">", self.source_offset()) + 1
            self.pending = None
        if tag == "body":
            self.body_end = self.source_offset()


def public_page(path: Path, doc: Document) -> bool:
    relative = path.relative_to(ROOT) if path.is_absolute() else path
    return (relative.suffix.lower() == ".html"
            and not any(p.startswith(".") for p in relative.parts)
            and relative.parts[0] not in INTERNAL
            and not COLLISION_NAME.search(relative.name)
            and not (doc.redirect or doc.noindex or doc.external))


def issue(doc: Document) -> str | None:
    if not doc.beacons:
        return "missing"
    if len(doc.beacons) != 1:
        return "duplicate"
    if not doc.beacons[0]["valid"]:
        return "incorrect"
    return None


def ensure_analytics(source: str) -> str:
    """Change analytics only; retain every other byte of a published document."""
    doc = Document(source)
    if doc.redirect or doc.noindex or doc.external or not issue(doc):
        return source
    if doc.body_end is None:
        raise ValueError("Public HTML has no closing body tag")
    if len(doc.beacons) == 1:
        old = doc.beacons[0]
        if old["end"] is None:
            raise ValueError("Unclosed Cloudflare script")
        # Retain the existing location and surrounding comments, if present.
        tag = (f'<script type="module" src="{BEACON_URL}" '
               f'data-cf-beacon=\'{{"token":"{TOKEN}"}}\'></script>')
        return source[:old["start"]] + tag + source[old["end"]:]
    if doc.beacons:
        for old in reversed(doc.beacons):
            if old["end"] is None:
                raise ValueError("Unclosed Cloudflare script")
            source = source[:old["start"]] + source[old["end"]:]
        doc = Document(source)
    return source[:doc.body_end] + SNIPPET + source[doc.body_end:]


def tracked_html(render):
    """Apply to a complete-page renderer (or a path → output dictionary)."""
    @wraps(render)
    def wrapped(*args, **kwargs):
        result = render(*args, **kwargs)
        if isinstance(result, str):
            return ensure_analytics(result)
        return {path: ensure_analytics(text) if public_page(Path(path), Document(text)) else text
                for path, text in result.items()}
    return wrapped


def audit(root: Path = ROOT):
    checked = 0
    errors = []
    for path in sorted(root.rglob("*.html")):
        relative = path.relative_to(root)
        if relative.parts[0] in INTERNAL or any(p.startswith(".") for p in relative.parts):
            continue
        source = path.read_text(encoding="utf-8")
        doc = Document(source)
        if not public_page(relative, doc):
            continue
        checked += 1
        if problem := issue(doc):
            errors.append((path, problem))
    return checked, errors


def conflict_copies(root: Path = ROOT):
    return [p for folder in (root / 'essays', root / 'originals') if folder.is_dir()
            for p in folder.rglob('*.html') if COLLISION_NAME.search(p.name)]
