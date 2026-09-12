#!/usr/bin/env python3
"""Render the edited Chinese and independent English readings of twenty-three plays.

The checked-in JSON is the publication text. Manuscripts outside the repository
are never modified or required to rebuild the published collection.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from build_ai_work_series import shell_header, footer, tri
from build_recent_fiction import inline
from import_fairy_tales import TraditionalConverter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "drama"
TARGET = ROOT / "essays" / "everyday" / "stories" / "drama"
BASE = "https://nondubito.net/essays/everyday/stories/drama/"
PUBLISHED = "2026-09-11"
SERIES = ("Structures in Drama", "戏剧里的结构")
DECK = (
    "A door closes. A child is taken into someone’s arms. A letter waits to be sent. Twenty-three readings stay with the moments when care, judgment, and reconciliation still need another person’s answer.",
    "一扇门关上，一个孩子被接进怀里，一封信还没有寄出。二十三篇，从这些细小的动作进入戏剧，看看照顾、判断与和解，为什么仍要等另一个人回答。",
)
GROUPS = (
    ("closeness", "Closeness & choice", "亲近与选择", (1, 8, 13, 15, 22)),
    ("speaking", "Who gets to be heard?", "谁能把话说完", (2, 3, 5, 9, 11)),
    ("stories", "Who tells my story?", "谁来讲我的故事", (6, 7, 12, 17)),
    ("care", "Care & its costs", "帮助与代价", (4, 10, 14, 19)),
    ("afterwards", "What reconciliation leaves open", "和解以后，生活继续", (16, 18, 20, 21, 23)),
)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


class DramaTraditionalConverter(TraditionalConverter):
    """Keep place particles traditional without changing transliterated names."""

    def convert(self, value: str) -> str:
        text = super().convert(value).replace("“", "「").replace("”", "」")
        for wrong, right in {
            "普裡姆斯": "普里姆斯", "普裡斯特利": "普里斯特利",
            "特裡普列夫": "特里普列夫", "特裡果林": "特里果林",
            "特裡維蘭": "特里維蘭", "布裡亞科夫": "布里亞科夫",
            "馬裡沃": "馬里沃",
            "贊美": "讚美", "贊賞": "讚賞", "稱贊": "稱讚",
        }.items():
            text = text.replace(wrong, right)
        return text


def localized(en: str, zh: str, converter: DramaTraditionalConverter, tag: str = "span", css: str = "") -> str:
    return tri(esc(en), esc(zh), esc(converter.convert(zh)), tag, css)


def filename(item: dict) -> str:
    return f"{item['id']:02d}-{item['slug']}.html"


def load_items(partial: bool = False) -> list[dict]:
    items = []
    for path in sorted(DATA.glob("[0-9][0-9].json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        required = (
            "source_file", "slug", "work_zh", "work_en", "author_zh", "author_en",
            "title_zh", "title_en", "deck_zh", "deck_en", "source_note_zh", "source_note_en",
        )
        if item.get("id") != int(path.stem) or any(not isinstance(item.get(k), str) or not item[k].strip() for k in required):
            raise ValueError(f"Incomplete metadata: {path.name}")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item["slug"]):
            raise ValueError(f"Unsafe slug: {path.name}")
        for lang in ("zh", "en"):
            paragraphs = item.get(f"body_{lang}", [])
            if len(paragraphs) < 8 or any(not isinstance(p, str) or not p.strip() for p in paragraphs):
                raise ValueError(f"Incomplete {lang} essay: {path.name}")
            if any("[^" in p or re.search(r"<\s*(?:script|iframe)\b", p, re.I) for p in paragraphs):
                raise ValueError(f"Unprocessed markup: {path.name}")
        if not item.get("sources"):
            raise ValueError(f"Missing source: {path.name}")
        for source in item["sources"]:
            parsed = urlsplit(source["url"])
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                raise ValueError(f"Invalid source URL: {path.name}")
            if not source.get("label_en") or not source.get("label_zh"):
                raise ValueError(f"Unlabelled source: {path.name}")
        items.append(item)
    if not items or (not partial and [item["id"] for item in items] != list(range(1, 24))):
        raise ValueError("The complete collection requires essays 01–23; --partial is for local previews only")
    return items


def head(title: str, description: str, name: str, item: dict | None = None) -> str:
    canonical = BASE + ("" if name == "index.html" else name)
    schema = {
        "@context": "https://schema.org", "@type": "Article" if item else "CollectionPage",
        "name": title, "description": description, "url": canonical,
        "inLanguage": ["en", "zh-Hans", "zh-Hant"],
        "author": {"@type": "Person", "name": "Han Qin (秦汉)"},
        "datePublished": PUBLISHED, "dateModified": PUBLISHED,
    }
    if item:
        schema.update({
            "headline": item["title_en"],
            "isPartOf": {"@type": "CollectionPage", "name": SERIES[0], "url": BASE},
            "about": {"@type": "CreativeWork", "name": item["work_en"], "author": {"@type": "Person", "name": item["author_en"]}},
            "citation": [source["url"] for source in item["sources"]],
            "mainEntityOfPage": canonical,
        })
    schema_json = json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')
    return f'''<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(description)}"><meta name="author" content="Han Qin (秦汉)">
<meta property="og:type" content="{'article' if item else 'website'}"><meta property="og:title" content="{esc(title)} — Non Dubito"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary">
<link rel="canonical" href="{canonical}"><link rel="icon" type="image/svg+xml" href="../../../../favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;family=Noto+Serif+TC:wght@400;500;600&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../../../style.css"><link rel="stylesheet" href="../../../../site-shell.css?v=20260905b"><link rel="stylesheet" href="drama.css?v=20260911">
<script src="../../../../site-shell.js?v=20260905b"></script><script defer src="drama.js?v=20260911"></script>
<script type="application/ld+json">{schema_json}</script>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script>
</head>'''


def shell(content: str, page_head: str) -> str:
    header_html = shell_header().replace('../../', '../../../../').replace('data-site-shell-menu aria-controls', 'data-site-shell-menu aria-label="Menu" aria-controls')
    footer_html = footer().replace('../../', '../../../../')
    for en, zh, hant in (("Explore", "探索", "探索"), ("Library", "书架", "書架"), ("SAE Theory ↗", "SAE 理论 ↗", "SAE 理論 ↗")):
        footer_html = footer_html.replace('>' + en + '</a>', '>' + tri(en, zh, hant) + '</a>')
    return '<!DOCTYPE html>\n<html lang="en" data-lang="en" data-editions="en zh zh-hant">\n' + page_head + '\n<body class="site-shell-page explicit-hant drama-page">' + header_html + content + footer_html + '</body></html>\n'


def breadcrumbs(converter: DramaTraditionalConverter, article: bool = False) -> str:
    extra = f'<span aria-hidden="true">/</span><a href="index.html">{localized(*SERIES, converter)}</a>' if article else ''
    return f'<nav class="drama-breadcrumbs" aria-label="Breadcrumb"><a href="../../../../library.html">{localized("Library", "书架", converter)}</a><span aria-hidden="true">/</span><a href="../index.html">{localized("Stories and Structures", "故事里的结构", converter)}</a>{extra}</nav>'


def spoiler_note(converter: DramaTraditionalConverter) -> str:
    return localized("These readings discuss key scenes and endings. They read the plays, not particular stage or screen productions.", "本系列涉及关键剧情与结局，阅读对象是剧本文本，而非某一场舞台演出或影视改编。", converter, "p", "drama-reading-note")


def card(item: dict, converter: DramaTraditionalConverter) -> str:
    return f'''<a class="drama-card" href="{filename(item)}"><span class="drama-number">{item['id']:02d}</span><div>
{localized(item['work_en'] + ' · ' + item['author_en'], item['work_zh'] + ' · ' + item['author_zh'], converter, 'p', 'drama-work')}
{localized(item['title_en'], item['title_zh'], converter, 'h3')}
{localized(item['deck_en'], item['deck_zh'], converter, 'p', 'drama-card-deck')}
{localized('Read essay →', '阅读全文 →', converter, 'span', 'drama-read')}</div></a>'''


def render_index(items: list[dict], converter: DramaTraditionalConverter) -> str:
    by_id = {item['id']: item for item in items}
    nav = []
    sections = []
    for key, en, zh, ids in GROUPS:
        group_items = [by_id[number] for number in ids if number in by_id]
        if not group_items:
            continue
        nav.append(f'<a href="#{key}">{localized(en, zh, converter)}</a>')
        sections.append(f'''<section class="drama-group" id="{key}"><div class="drama-group-head">{localized(en, zh, converter, 'h2')}{localized(f'{len(group_items)} essays', f'{len(group_items)} 篇', converter, 'p')}</div><div class="drama-grid">{''.join(card(item, converter) for item in group_items)}</div></section>''')
    title = SERIES[0] + ' · ' + SERIES[1]
    deck = DECK if len(items) == 23 else (f'{len(items)} completed readings from the forthcoming collection.', f'正在制作的戏剧系列，已有 {len(items)} 篇完整阅读。')
    content = f'''<main class="drama-wrap" data-search="Structures in Drama 戏剧里的结构 戲劇裡的結構 剧本 戲劇 戏剧解读">
{breadcrumbs(converter)}<section class="drama-hero"><p class="drama-kicker">Non Dubito · {localized('Stories and Structures / 05', '故事里的结构 / 05', converter)}</p>
{localized(*SERIES, converter, 'h1')}{localized(*deck, converter, 'p', 'drama-hero-deck drama-search-deck')}
{localized(f'{len(items)} essays · Chinese, English & Traditional Chinese', f'{len(items)} 篇 · 简体中文、英文与繁体中文', converter, 'p', 'drama-meta')}{spoiler_note(converter)}
</section><nav class="drama-topics" aria-label="Reading themes">{''.join(nav)}</nav>{''.join(sections)}
<div class="drama-return"><a href="../index.html">{localized('← More stories and structures', '← 回到“故事里的结构”', converter)}</a></div></main>'''
    return shell(content, head(title, deck[0], 'index.html'))


def render_article(item: dict, items: list[dict], converter: DramaTraditionalConverter) -> str:
    index = items.index(item)
    sources = []
    for source in item['sources']:
        sources.append(f'<li><a href="{esc(source["url"])}">{localized(source["label_en"], source["label_zh"], converter)}</a></li>')
    source_section = f'''<details class="drama-sources"><summary>{localized('Text & sources', '文本与来源', converter)}</summary>{localized(item['source_note_en'], item['source_note_zh'], converter, 'p')}<ul>{''.join(sources)}</ul></details>'''
    bodies = []
    for lang, css, native in (('en', 'en', 'en'), ('zh', 'zh', 'zh-Hans'), ('hant', 'hant', 'zh-Hant')):
        paragraphs = item['body_en' if lang == 'en' else 'body_zh']
        if lang == 'hant':
            paragraphs = [converter.convert(p) for p in paragraphs]
        bodies.append(f'<div class="drama-prose lang-{css}" lang="{native}">' + '\n'.join(f'<p>{inline(p)}</p>' for p in paragraphs) + '</div>')
    navigation = []
    for target_index, label_en, label_zh in ((index - 1, 'Previous essay', '上一篇'), (index + 1, 'Next essay', '下一篇')):
        if 0 <= target_index < len(items):
            target = items[target_index]
            navigation.append(f'<a href="{filename(target)}">{localized(label_en, label_zh, converter, "small")}{localized(target["work_en"], target["work_zh"], converter)}<span aria-hidden="true"> →</span></a>')
        else:
            navigation.append(f'<a href="index.html">{localized("All twenty-three readings", "全部二十三篇", converter, "small")}{localized(*SERIES, converter)}</a>')
    labels = ' '.join((SERIES[0], SERIES[1], converter.convert(SERIES[1]), item['work_en'], item['work_zh'], converter.convert(item['work_zh']), item['author_en'], item['author_zh'], converter.convert(item['author_zh'])))
    content = f'''<main class="drama-wrap" data-search="{esc(labels)}">{breadcrumbs(converter, True)}<article class="drama-article">
<div class="drama-head"><p class="drama-kicker">{localized(*SERIES, converter)} · {item['id']:02d} / 23</p>
{localized(item['title_en'], item['title_zh'], converter, 'h1')}
{localized(item['work_en'] + ' · ' + item['author_en'], item['work_zh'] + ' · ' + item['author_zh'], converter, 'p', 'drama-original-work')}
{localized(item['deck_en'], item['deck_zh'], converter, 'p', 'drama-article-deck drama-search-deck')}
<p class="drama-meta">Han Qin ({localized('秦汉', '秦汉', converter)}) · <time datetime="{PUBLISHED}">2026</time></p>{spoiler_note(converter)}</div>
{''.join(bodies)}{source_section}
<aside class="drama-afterword">{localized('Further reading', '继续阅读', converter, 'p', 'drama-kicker')}<a href="index.html">{localized(*SERIES, converter)}</a><span aria-hidden="true"> · </span><a href="../../../../start.html">{localized('Five minutes to understand Non Dubito', '五分钟读懂 Non Dubito', converter)}</a></aside>
<nav class="drama-series-nav" aria-label="Series navigation">{''.join(navigation)}</nav></article></main>'''
    return shell(content, head(item['title_en'] + ' · ' + SERIES[0], item['deck_en'], filename(item), item))


def render(partial: bool = False) -> dict[Path, str]:
    items = load_items(partial)
    converter = DramaTraditionalConverter()
    try:
        return {TARGET / 'index.html': render_index(items, converter), **{TARGET / filename(item): render_article(item, items, converter) for item in items}}
    finally:
        converter.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--partial', action='store_true', help='local preview only; final validation requires all 23 essays')
    args = parser.parse_args()
    outputs = render(args.partial)
    stale = [path for path, value in outputs.items() if not path.exists() or path.read_text(encoding='utf-8') != value]
    if args.check:
        if stale:
            raise SystemExit('Stale drama pages:\n' + '\n'.join(str(path.relative_to(ROOT)) for path in stale))
        print(f'OK: {len(outputs)} drama pages are current')
        return 0
    for path, value in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding='utf-8')
    print(f'Wrote {len(outputs)} drama pages')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
