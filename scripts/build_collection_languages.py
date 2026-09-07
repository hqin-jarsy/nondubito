#!/usr/bin/env python3
"""Build edited multilingual editions for compact Non Dubito collections.

The JSON files in ``data/collection-languages`` contain editorial rewrites.
This script does no translation: it only renders HTML, navigation, language
routes, canonicals, and localized series indexes.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "collection-languages"
LANGS = ("ja", "fr", "de", "es", "ko")
LANG_NAMES = {"ja": "日本語", "fr": "Français", "de": "Deutsch", "es": "Español", "ko": "한국어"}
HTML_LANG = {"ja": "ja", "fr": "fr", "de": "de", "es": "es", "ko": "ko"}
UI = {
    "ja": {"essay": "篇", "read": "読む", "previous": "前の篇", "next": "次の篇", "all": "全篇", "library": "ライブラリー"},
    "fr": {"essay": "essai", "read": "Lire", "previous": "Essai précédent", "next": "Essai suivant", "all": "Tous les essais", "library": "Bibliothèque"},
    "de": {"essay": "Essay", "read": "Lesen", "previous": "Voriger Essay", "next": "Nächster Essay", "all": "Alle Essays", "library": "Bibliothek"},
    "es": {"essay": "ensayo", "read": "Leer", "previous": "Ensayo anterior", "next": "Ensayo siguiente", "all": "Todos los ensayos", "library": "Biblioteca"},
    "ko": {"essay": "편", "read": "읽기", "previous": "이전 글", "next": "다음 글", "all": "전체 글", "library": "라이브러리"},
}


def item_copy(spec: dict[str, object], item: dict[str, object], lang: str) -> dict[str, object]:
    """Return verbose copy; compact specs may use [title, deck, p1, p2, p3]."""
    copy = item["copy"][lang]
    if isinstance(copy, list):
        if len(copy) != 5:
            raise ValueError(f"{spec['id']}: {item['slug']}/{lang} compact copy needs five fields")
        headings = spec.get("section_headings", {}).get(lang)
        if not headings or len(headings) != 3:
            raise ValueError(f"{spec['id']}: compact copy needs three {lang} section headings")
        return {
            "title": copy[0],
            "deck": copy[1],
            "sections": [
                {"heading": headings[i], "paragraph": copy[i + 2]} for i in range(3)
            ],
        }
    return copy


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_specs(selected: set[str] | None = None) -> list[dict[str, object]]:
    specs = []
    for path in sorted(DATA.glob("*.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        if selected and spec["id"] not in selected:
            continue
        spec_langs = tuple(spec.get("languages", LANGS))
        unknown = set(spec_langs) - set(LANGS)
        if unknown:
            raise ValueError(f"{path.name}: unknown languages {sorted(unknown)}")
        missing = set(spec_langs) - set(spec["series"])
        if missing:
            raise ValueError(f"{path.name}: missing series copy for {sorted(missing)}")
        if not spec.get("items"):
            raise ValueError(f"{path.name}: no items")
        slugs: set[str] = set()
        for item in spec["items"]:
            if item["slug"] in slugs:
                raise ValueError(f"{path.name}: duplicate slug {item['slug']}")
            slugs.add(item["slug"])
            for lang in spec_langs:
                copy = item.get("copy", {}).get(lang)
                if not copy:
                    raise ValueError(f"{path.name}: {item['slug']} missing {lang}")
                normalized = item_copy(spec, item, lang)
                if len(normalized.get("sections", [])) != 3:
                    raise ValueError(f"{path.name}: {item['slug']}/{lang} needs three sections")
        specs.append(spec)
    return specs


def root_prefix(directory: str) -> str:
    # One extra level is added by the language directory.
    return "../" * (len(Path(directory).parts) + 1)


def language_route(lang: str, slug: str | None) -> str:
    source = f"../{slug}.html" if slug else "../index.html"
    links = [
        f'<a class="lang-btn" href="{source}?lang=en">EN</a>',
        '<span class="lang-sep">|</span>',
        f'<a class="lang-btn" href="{source}?lang=zh">中文</a>',
        '<span class="lang-sep">|</span>',
        f'<a class="lang-btn" href="{source}?lang=zh-hant">繁體</a>',
    ]
    for code in LANGS:
        links.append('<span class="lang-sep">|</span>')
        if code == lang:
            links.append(f'<span class="lang-btn active">{LANG_NAMES[code]}</span>')
        else:
            target = f"../{code}/{slug}.html" if slug else f"../{code}/index.html"
            links.append(f'<a class="lang-btn" href="{target}">{LANG_NAMES[code]}</a>')
    return "".join(links)


def source_links(slug: str | None) -> str:
    parts = []
    for code in LANGS:
        target = f"{code}/{slug}.html" if slug else f"{code}/index.html"
        parts.append(f'<span class="lang-sep">|</span><a class="lang-btn" href="{target}">{LANG_NAMES[code]}</a>')
    return '<!-- collection-language-links:start -->' + "".join(parts) + '<!-- collection-language-links:end -->'


def inject_source_links(text: str, slug: str | None, path: Path) -> str:
    block = source_links(slug)
    marker = re.compile(r'<!-- collection-language-links:start -->.*?<!-- collection-language-links:end -->', re.S)
    if marker.search(text):
        return marker.sub(block, text, count=1)
    match = re.search(r'(<div class="lang-toggle"[^>]*>)(.*?)(</div>)', text, re.S)
    if not match:
        match = re.search(r'(<div class="blockchain-header-tools"[^>]*>)(.*?)(</div>)', text, re.S)
    if not match:
        raise ValueError(f"No language toggle in {path}")
    return text[:match.start()] + match.group(1) + match.group(2) + block + match.group(3) + text[match.end():]


def article_html(spec: dict[str, object], lang: str, index: int) -> str:
    item = spec["items"][index]
    copy = item_copy(spec, item, lang)
    series = spec["series"][lang]
    directory = str(spec["directory"])
    prefix = root_prefix(directory)
    total = len(spec["items"])
    prev = spec["items"][index - 1] if index else None
    nxt = spec["items"][index + 1] if index + 1 < total else None
    sections = "".join(
        f'<section><h2>{esc(section["heading"])}</h2><p>{esc(section["paragraph"])}</p></section>'
        for section in copy["sections"]
    )
    def nav(target: dict[str, object] | None, previous: bool) -> str:
        if target is None:
            return '<a href="index.html"><small>←</small>' + esc(series["title"]) + '</a>'
        label = UI[lang]["previous" if previous else "next"]
        title = item_copy(spec, target, lang)["title"]
        arrow = "← " if previous else " →"
        return f'<a href="{target["slug"]}.html"><small>{esc(label)}</small>{arrow if previous else ""}{esc(title)}{"" if previous else arrow}</a>'
    canonical = f'https://nondubito.net/{directory}/{lang}/{item["slug"]}.html'
    return f'''<!DOCTYPE html><html lang="{HTML_LANG[lang]}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{esc(copy["title"])} · {esc(series["title"])} — Non Dubito</title><meta name="description" content="{esc(copy["deck"])}"><meta name="author" content="Han Qin (秦汉)"><meta property="og:type" content="article"><meta property="og:title" content="{esc(copy["title"])}"><meta property="og:description" content="{esc(copy["deck"])}"><meta property="og:url" content="{canonical}"><link rel="canonical" href="{canonical}"><link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg"><link rel="stylesheet" href="{prefix}style.css"><style>.collection-page{{max-width:820px;margin:0 auto;padding:92px 2rem 72px}}.language-route{{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem;margin-bottom:2.2rem}}.collection-back{{font-family:var(--sans);font-size:.72rem;color:var(--ink-muted);text-decoration:none}}.collection-kicker{{font-family:var(--sans);font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);margin:2rem 0 .7rem}}.collection-page h1{{font-size:2.35rem;line-height:1.18;margin:.2rem 0 1rem}}.collection-deck{{font-size:1.08rem;color:var(--ink-light);line-height:1.75;margin-bottom:2.4rem}}.collection-body section{{margin:0 0 2.5rem}}.collection-body h2{{font-size:1.28rem;margin-bottom:.8rem}}.collection-body p{{font-size:1.02rem;line-height:1.9;margin:0}}.edition-note{{margin:3rem 0 0;padding-top:1.1rem;border-top:1px solid var(--cream-border);font-size:.8rem;color:var(--ink-muted);line-height:1.7}}.collection-nav{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:2.4rem}}.collection-nav a{{padding:1rem;border:1px solid var(--cream-border);text-decoration:none;color:var(--ink);line-height:1.45}}.collection-nav a:last-child{{text-align:right}}.collection-nav small{{display:block;font-family:var(--sans);font-size:.62rem;color:var(--ink-muted);margin-bottom:.3rem}}@media(max-width:620px){{.collection-page{{padding:76px 1.25rem 54px}}.collection-nav{{grid-template-columns:1fr}}.collection-nav a:last-child{{text-align:left}}}}</style><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script></head><body><header><div class="header-inner"><a href="{prefix}index.html" class="site-title"><span class="title-latin">Non <span>Dubito</span></span><span class="title-sub">Essays in the Self-as-an-End Tradition</span></a><nav><a href="{prefix}index.html">Essays</a><a href="{prefix}start.html">Start Here</a><a href="{prefix}library.html" class="active">Library</a><a href="{prefix}about.html">About</a><a href="https://self-as-an-end.net" target="_blank" rel="noopener">SAE Theory ↗</a></nav></div></header><main class="collection-page"><div class="language-route" aria-label="Language selector">{language_route(lang, str(item["slug"]))}</div><a class="collection-back" href="index.html">← {esc(series["title"])}</a><article><div class="collection-kicker">{esc(series["kicker"])} · {index + 1:02d} / {total:02d}</div><h1>{esc(copy["title"])}</h1><p class="collection-deck">{esc(copy["deck"])}</p><div class="collection-body">{sections}</div><p class="edition-note"><em>{esc(series["note"])}</em></p><nav class="collection-nav">{nav(prev, True)}{nav(nxt, False)}</nav></article></main><footer><div class="footer-inner"><div class="footer-brand"><div class="footer-logo">Non <span>Dubito</span></div><div class="footer-tagline">Thought has no mother tongue</div></div><div class="footer-bottom">© 2026 Han Qin · Non Dubito</div></div></footer></body></html>'''


def index_html(spec: dict[str, object], lang: str) -> str:
    series = spec["series"][lang]
    directory = str(spec["directory"])
    prefix = root_prefix(directory)
    cards = "".join(
        f'<a class="collection-card" href="{item["slug"]}.html"><span>{i + 1:02d}</span><h2>{esc(item_copy(spec, item, lang)["title"])}</h2><p>{esc(item_copy(spec, item, lang)["deck"])}</p><b>{esc(UI[lang]["read"])} →</b></a>'
        for i, item in enumerate(spec["items"])
    )
    canonical = f'https://nondubito.net/{directory}/{lang}/'
    return f'''<!DOCTYPE html><html lang="{HTML_LANG[lang]}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{esc(series["title"])} — Non Dubito</title><meta name="description" content="{esc(series["deck"])}"><meta name="author" content="Han Qin (秦汉)"><meta property="og:type" content="website"><meta property="og:title" content="{esc(series["title"])}"><meta property="og:description" content="{esc(series["deck"])}"><meta property="og:url" content="{canonical}"><link rel="canonical" href="{canonical}"><link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg"><link rel="stylesheet" href="{prefix}style.css"><style>.collection-page{{max-width:1080px;margin:0 auto;padding:92px 2rem 72px}}.language-route{{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem;margin-bottom:2.2rem}}.collection-back{{font-family:var(--sans);font-size:.72rem;color:var(--ink-muted);text-decoration:none}}.collection-hero{{max-width:780px;margin:2rem 0 3rem}}.collection-kicker{{font-family:var(--sans);font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}}.collection-hero h1{{font-size:2.75rem;line-height:1.15;margin:.6rem 0 1rem}}.collection-hero p{{font-size:1.08rem;line-height:1.8;color:var(--ink-light)}}.collection-meta{{font-family:var(--sans);font-size:.72rem;color:var(--ink-muted);margin-top:1.2rem}}.collection-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}}.collection-card{{display:block;border:1px solid var(--cream-border);padding:1.4rem;text-decoration:none;color:var(--ink)}}.collection-card>span{{font-family:var(--sans);font-size:.62rem;color:var(--gold)}}.collection-card h2{{font-size:1.2rem;line-height:1.35;margin:.45rem 0 .7rem}}.collection-card p{{font-size:.9rem;line-height:1.65;color:var(--ink-light);margin:0 0 .8rem}}.collection-card b{{font-family:var(--sans);font-size:.68rem;font-weight:400;color:var(--gold)}}@media(max-width:680px){{.collection-page{{padding:76px 1.25rem 54px}}.collection-grid{{grid-template-columns:1fr}}}}</style><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script></head><body><header><div class="header-inner"><a href="{prefix}index.html" class="site-title"><span class="title-latin">Non <span>Dubito</span></span><span class="title-sub">Essays in the Self-as-an-End Tradition</span></a><nav><a href="{prefix}index.html">Essays</a><a href="{prefix}start.html">Start Here</a><a href="{prefix}library.html" class="active">Library</a><a href="{prefix}about.html">About</a><a href="https://self-as-an-end.net" target="_blank" rel="noopener">SAE Theory ↗</a></nav></div></header><main class="collection-page"><div class="language-route" aria-label="Language selector">{language_route(lang, None)}</div><a class="collection-back" href="{prefix}library.html">← {esc(UI[lang]["library"])}</a><section class="collection-hero"><div class="collection-kicker">{esc(series["kicker"])}</div><h1>{esc(series["title"])}</h1><p>{esc(series["deck"])}</p><div class="collection-meta">Han Qin (秦汉) · 2026 · {len(spec["items"])} {esc(UI[lang]["essay"])} · 8 languages</div></section><section class="collection-grid">{cards}</section></main><footer><div class="footer-inner"><div class="footer-brand"><div class="footer-logo">Non <span>Dubito</span></div><div class="footer-tagline">Thought has no mother tongue</div></div><div class="footer-bottom">© 2026 Han Qin · Non Dubito</div></div></footer></body></html>'''


def render(spec: dict[str, object]) -> dict[Path, str]:
    directory = ROOT / str(spec["directory"])
    outputs: dict[Path, str] = {}
    spec_langs = tuple(spec.get("languages", LANGS))
    for lang in spec_langs:
        outputs[directory / lang / "index.html"] = index_html(spec, lang)
        for i, item in enumerate(spec["items"]):
            outputs[directory / lang / f'{item["slug"]}.html'] = article_html(spec, lang, i)
    source_index = directory / "index.html"
    outputs[source_index] = inject_source_links(source_index.read_text(encoding="utf-8"), None, source_index)
    for item in spec["items"]:
        source = directory / f'{item["slug"]}.html'
        outputs[source] = inject_source_links(source.read_text(encoding="utf-8"), str(item["slug"]), source)
    return outputs


def hub_card(spec: dict[str, object], lang: str) -> str:
    series = spec["series"][lang]
    target = "../" + str(Path(str(spec["directory"])).relative_to("essays")) + f"/{lang}/index.html"
    return (
        f'<!-- collection-hub:{spec["id"]}:start -->'
        f'<a href="{target}" class="essay-card" style="text-decoration:none;border-left:3px solid var(--gold);display:block;padding:2rem 2.25rem;margin-bottom:1rem;">'
        f'<div style="font-family:var(--sans);font-size:.65rem;letter-spacing:.13em;text-transform:uppercase;color:var(--green-light);margin-bottom:.7rem;">{esc(series["kicker"])} · 8 languages</div>'
        f'<div style="font-size:1.45rem;color:var(--ink);margin-bottom:.55rem;">{esc(series["title"])}</div>'
        f'<p style="font-size:.92rem;color:var(--ink-light);line-height:1.72;margin:0;">{esc(series["deck"])}</p></a>'
        f'<!-- collection-hub:{spec["id"]}:end -->'
    )


def inject_hub(text: str, spec: dict[str, object], lang: str, path: Path) -> str:
    anchor = spec.get("hub_marker")
    if not anchor:
        return text
    block = hub_card(spec, lang)
    existing = re.compile(
        rf'<!-- collection-hub:{re.escape(str(spec["id"]))}:start -->.*?<!-- collection-hub:{re.escape(str(spec["id"]))}:end -->',
        re.S,
    )
    if existing.search(text):
        return existing.sub(block, text, count=1)
    if str(anchor) not in text:
        raise ValueError(f"Missing hub marker {anchor!r} in {path}")
    return text.replace(str(anchor), str(anchor) + block, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--only", action="append", default=[])
    args = parser.parse_args()
    specs = load_specs(set(args.only) or None)
    outputs: dict[Path, str] = {}
    for spec in specs:
        outputs.update(render(spec))
    for lang in LANGS:
        hub_path = ROOT / "essays" / lang / "index.html"
        hub_text = outputs.get(hub_path, hub_path.read_text(encoding="utf-8"))
        for spec in specs:
            if lang in tuple(spec.get("languages", LANGS)):
                hub_text = inject_hub(hub_text, spec, lang, hub_path)
        outputs[hub_path] = hub_text
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, text in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != text]
        if stale:
            raise SystemExit("Stale collection pages:\n" + "\n".join(stale))
        print(f"OK: {len(outputs)} collection pages")
        return
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"Wrote: {len(outputs)} collection pages")


if __name__ == "__main__":
    main()
