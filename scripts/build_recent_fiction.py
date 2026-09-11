#!/usr/bin/env python3
"""Render the Recent Fiction shelf and its independently edited reader guides."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from build_ai_work_series import TraditionalConverter, shell_header, tri


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "recent-fiction"
TARGET = ROOT / "essays" / "recent-fiction"
DATE = "2026-09-10"
ORDER = ("the-dream-hotel", "james", "intermezzo", "all-fours", "the-wedding-people")
TOPICS = {
    "the-dream-hotel": ("Surveillance & private life", "监控与私人生活"),
    "james": ("Voice & freedom", "声音与自由"),
    "intermezzo": ("Grief & intimacy", "失去与亲密"),
    "all-fours": ("Desire & middle age", "欲望与中年"),
    "the-wedding-people": ("Meeting & beginning again", "相遇与重新开始"),
}
KIND_LABELS = {
    "interview": ("Author conversation", "作者访谈"),
    "excerpt": ("Read an excerpt", "公开试读"),
    "publisher": ("Publication details", "出版资料"),
    "review": ("Another reader’s view", "另一位读者的看法"),
}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def inline(text: str) -> str:
    """Render only prose emphasis and explicit HTTPS links; never raw HTML."""
    links: list[str] = []

    def link(match: re.Match[str]) -> str:
        label, url = match.groups()
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(f"Expected an absolute HTTPS source URL: {url}")
        token = f"\x00LINK{len(links)}\x00"
        links.append(f'<a href="{esc(url)}">{esc(label)}</a>')
        return token

    text = re.sub(r"\[([^\]]+)\]\((https://[^\s]+?)\)", link, text)
    text = esc(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    for number, value in enumerate(links):
        text = text.replace(f"\x00LINK{number}\x00", value)
    return text


def prose(text: str) -> str:
    result = []
    for block in re.split(r"\n\s*\n", text.strip()):
        if block.startswith("## "):
            result.append(f"<h2>{inline(block[3:])}</h2>")
        elif block.startswith("### "):
            result.append(f"<h3>{inline(block[4:])}</h3>")
        elif block.startswith("- "):
            result.append("<ul>" + "".join(f"<li>{inline(item[2:])}</li>" for item in block.splitlines()) + "</ul>")
        else:
            attr = ' class="rf-opening"' if not result else ""
            result.append(f"<p{attr}>{inline(' '.join(block.splitlines()))}</p>")
    return "\n".join(result)


def localized(en: str, zh: str, converter: TraditionalConverter, tag: str = "span", classes: str = "") -> str:
    return tri(en, zh, converter.convert(zh), tag, classes)


def head(title: str, description: str, filename: str, book: dict | None = None) -> str:
    url = "https://nondubito.net/essays/recent-fiction/" + ("" if filename == "index.html" else filename)
    schema = {
        "@context": "https://schema.org",
        "@type": "Article" if book else "CollectionPage",
        "name": title,
        "description": description,
        "url": url,
        "inLanguage": ["en", "zh-Hans", "zh-Hant"],
        "datePublished": DATE,
        "dateModified": DATE,
        "author": {"@type": "Person", "name": "Han Qin (秦汉)"},
    }
    if book:
        schema["headline"] = title
        schema["about"] = {"@type": "Book", "name": book["book"], "author": {"@type": "Person", "name": book["author"]}, "datePublished": book["book_date"], "inLanguage": "en"}
        schema["isPartOf"] = {"@type": "CollectionPage", "name": "Recent Fiction", "url": "https://nondubito.net/essays/recent-fiction/"}
    alternates = "".join(f'<link rel="alternate" hreflang="{language}" href="{url}">' for language in ("en", "zh-Hans", "zh-Hant", "x-default"))
    schema_json = json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')
    return f'''<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)} — Non Dubito</title>
  <meta name="description" content="{esc(description)}">
  <meta name="author" content="Han Qin (秦汉)">
  <meta property="og:type" content="{'article' if book else 'website'}">
  <meta property="og:title" content="{esc(title)} — Non Dubito">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="Non Dubito">
  <meta name="twitter:card" content="summary">
  <link rel="canonical" href="{url}">{alternates}
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
  <link rel="apple-touch-icon" href="../../apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&amp;family=Inter:wght@400;500&amp;family=Noto+Serif+SC:wght@400;500&amp;family=Noto+Serif+TC:wght@400;500&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../style.css">
  <link rel="stylesheet" href="../../site-shell.css?v=20260905b">
  <link rel="stylesheet" href="../../reading-context.css?v=20260905a">
  <link rel="stylesheet" href="recent-fiction.css?v=20260910">
  <script src="../../site-shell.js?v=20260905b"></script>
  <script type="application/ld+json">{schema_json}</script>
</head>'''


def footer(converter: TraditionalConverter) -> str:
    return f'''<footer class="site-shell-footer"><div class="site-shell-footer-inner"><div><div class="site-shell-footer-mark">Non <span>Dubito</span></div><p>A mind in many languages</p></div><div class="site-shell-footer-links"><a href="../../explore.html">{localized('Explore', '探索', converter)}</a><a href="../../library.html">{localized('Library', '文库', converter)}</a><a href="https://credesivis.org/index.html">Crede Si Vis ↗</a><a href="https://self-as-an-end.net">SAE Theory ↗</a></div></div></footer>'''


def breadcrumbs(converter: TraditionalConverter, book: dict | None = None) -> str:
    current = f'<span aria-current="page">{esc(book["book"])}</span>' if book else f'<span aria-current="page">{localized("Recent Fiction", "近年小说导读", converter)}</span>'
    shelf = f'<a href="index.html">{localized("Recent Fiction", "近年小说导读", converter)}</a><span aria-hidden="true">/</span>' if book else ""
    return f'<nav class="reading-breadcrumbs" aria-label="Breadcrumb"><a href="../../explore.html#stories">{localized("Literature & narrative", "文学与叙事", converter)}</a><span aria-hidden="true">/</span>{shelf}{current}</nav>'


def card(book: dict, converter: TraditionalConverter) -> str:
    en, zh = TOPICS[book["slug"]]
    return f'''<a class="rf-book-card" href="{book['slug']}.html">
  <div class="rf-card-top"><span class="rf-kicker">{localized(en, zh, converter)}</span><span class="rf-year">{book['book_date'][:4]}</span></div>
  {localized(esc(book['en_title']), esc(book['zh_title']), converter, 'h3')}
  <p class="rf-card-author">{esc(book['author'])}</p>
  {localized(esc(book['en_deck']), esc(book['zh_deck']), converter, 'p', 'rf-card-deck')}
  <span class="rf-card-cta">{localized('Read the introduction', '读这篇导读', converter)} <span aria-hidden="true">→</span></span>
</a>'''


def render_index(books: list[dict], converter: TraditionalConverter) -> str:
    shelf = []
    for year in sorted({book['book_date'][:4] for book in books}, reverse=True):
        items = [book for book in books if book['book_date'].startswith(year)]
        shelf.append(f'''<section class="rf-year-section" id="year-{year}"><div class="rf-shelf-heading"><h2>{year}</h2><p>{localized('Original publication year', '小说首版年份', converter)}</p></div><div class="rf-book-grid{' rf-book-grid-single' if len(items) == 1 else ''}">{''.join(card(book, converter) for book in items)}</div></section>''')
    years = ''.join(f'<a href="#year-{year}">{year}</a>' for year in sorted({book['book_date'][:4] for book in books}, reverse=True))
    return f'''<!DOCTYPE html>
<html lang="en" data-lang="en" data-editions="en zh zh-hant">
{head('Recent Fiction · 近年小说导读', 'Discover recent novels through their people, opening scenes, and questions: introductions with room left for the book, plus author conversations and public excerpts.', 'index.html')}
<body class="site-shell-page explicit-hant rf-page">
{shell_header()}
<main class="rf-wrap">
{breadcrumbs(converter)}
<section class="rf-shelf-hero">
  <div><p class="rf-kicker">Non Dubito · {localized('Books to discover', '发现值得读的小说', converter)}</p>
  {localized('Recent Fiction', '近年小说导读', converter, 'h1')}
  {localized('A life you have not met yet.', '还有一些人，等你翻开书才会遇见。', converter, 'p', 'rf-hero-deck')}</div>
  <div class="rf-editor-note">
  {localized('Begin with a voice, a room, an encounter. These introductions offer a way into recent novels, leaving their turns and endings for your own reading.', '从一个声音、一间房、一次相遇开始。这里介绍近年的小说，带你走到故事的门口，把重要转折与结局留给你的阅读。', converter, 'p')}
  {localized('Each guide also leads outward—to a public excerpt, a conversation with the author, or another reading of the book.', '每篇也留有通向书外的路：公开试读、作者访谈，以及另一位读者的看法。', converter, 'p')}
  </div>
</section>
<nav class="rf-shelf-nav" aria-label="Publication years"><span>{localized('Browse by book year', '按小说年份浏览', converter)}</span>{years}<span class="rf-shelf-count">{localized(f'{len(books)} books · 3 reading modes', f'{len(books)} 部作品 · 英 / 简 / 繁', converter)}</span></nav>
{''.join(shelf)}
<aside class="rf-shelf-afterword"><h2>{localized('Keep following the question', '沿着问题继续读', converter)}</h2>{localized('For longer readings across classics and contemporary literature, visit Literary Readings. For imagined worlds and their consequences, follow Science Fiction. This shelf will keep making room for newer voices.', '想继续读经典与现代文学，可以进入文学作品解读；想走向想象世界及其后果，可以去科幻小说区。这一架会继续为近年的新声音留下位置。', converter, 'p')}<div class="rf-actions"><a href="../literature/index.html">{localized('Literary Readings →', '文学作品解读 →', converter)}</a><a href="../science-fiction/index.html">{localized('Science Fiction →', '科幻小说解读 →', converter)}</a></div></aside>
</main>{footer(converter)}
</body></html>'''


def source_section(book: dict, converter: TraditionalConverter) -> str:
    order = {"interview": 0, "excerpt": 1, "publisher": 2, "review": 3}
    cards = []
    for source in sorted(book["sources"], key=lambda item: order[item["kind"]]):
        en, zh = KIND_LABELS[source["kind"]]
        cards.append(f'''<a class="rf-source-card" href="{esc(source['url'])}"><span class="rf-kicker">{localized(en, zh, converter)}</span><h3>{esc(source['label'])} <span aria-hidden="true">↗</span></h3>{localized(esc(source['description_en']), esc(source['description_zh']), converter, 'p')}</a>''')
    return f'''<section class="rf-sources" id="sources" aria-labelledby="source-heading"><h2 id="source-heading">{localized('Beyond this introduction', '读完这里，还可以去哪里', converter)}</h2>{localized(esc(book['en_source_note']), esc(book['zh_source_note']), converter, 'p', 'rf-source-note')}{localized('The linked conversations and excerpts may discuss more of the story than this introduction does.', '外部访谈与试读可能谈到本文尚未展开的情节。', converter, 'p', 'rf-source-spoilers')}<div class="rf-source-grid">{''.join(cards)}</div></section>'''


def render_article(book: dict, books: list[dict], converter: TraditionalConverter) -> str:
    en_body = prose(book['en_body'])
    zh_body = prose(book['zh_body'])
    hant_body = prose(converter.convert(book['zh_body']))
    topic_en, topic_zh = TOPICS[book['slug']]
    excerpt = next((item for item in book['sources'] if item['kind'] == 'excerpt'), None)
    actions = f'<a href="#sources">{localized("Author conversations & sources ↓", "作者访谈与资料 ↓", converter)}</a>'
    if excerpt:
        actions += f'<a href="{esc(excerpt["url"])}">{localized("Try the book ↗", "先读一段原作 ↗", converter)}</a>'
    related = [candidate for candidate in books if candidate['slug'] != book['slug']]
    # Two nearby themes, without implying a mandatory reading sequence.
    recommended = {
        'the-dream-hotel': ('james', 'intermezzo'),
        'james': ('the-dream-hotel', 'the-wedding-people'),
        'intermezzo': ('all-fours', 'the-wedding-people'),
        'all-fours': ('intermezzo', 'the-wedding-people'),
        'the-wedding-people': ('intermezzo', 'all-fours'),
    }[book['slug']]
    related = [next(item for item in related if item['slug'] == slug) for slug in recommended]
    links = ''.join(f'<a href="{item["slug"]}.html"><span class="rf-kicker">{esc(item["author"])}</span><strong>{esc(item["book"])}</strong><span aria-hidden="true">→</span></a>' for item in related)
    return f'''<!DOCTYPE html>
<html lang="en" data-lang="en" data-editions="en zh zh-hant">
{head(book['en_title'] + ' · ' + book['zh_title'], book['en_deck'], book['slug'] + '.html', book)}
<body class="site-shell-page explicit-hant rf-page">
{shell_header()}
<main class="rf-wrap rf-article" data-search="{esc(book['book'] + ' ' + book['author'] + ' ' + book['book_date'][:4] + ' Recent Fiction 近年小说导读 近年小說導讀')}">
{breadcrumbs(converter, book)}
<section class="rf-article-hero">
  <p class="rf-kicker">{localized(topic_en, topic_zh, converter)}</p>
  {localized(esc(book['en_title']), esc(book['zh_title']), converter, 'h1')}
  {localized(esc(book['en_deck']), esc(book['zh_deck']), converter, 'p', 'rf-article-deck')}
  <p class="rf-book-meta">{esc(book['author'])} · <span>{localized('Original publication', '原作首版', converter)} <time datetime="{book['book_date']}">{book['book_date']}</time></span> · {esc(book['publisher'])}</p>
  <p class="rf-guide-meta">Han Qin (秦汉) · {localized('Guide published', '导读发布', converter)} <time datetime="{DATE}">Sep 10, 2026</time></p>
  <div class="rf-notice">{localized(esc(book['en_notice']), esc(book['zh_notice']), converter, 'p')}</div>
  <div class="rf-actions">{actions}</div>
</section>
<article class="rf-prose lang-en" lang="en">{en_body}</article>
<article class="rf-prose lang-zh" lang="zh-Hans">{zh_body}</article>
<article class="rf-prose lang-hant" lang="zh-Hant">{hant_body}</article>
{source_section(book, converter)}
<nav class="rf-next reading-next-grid" aria-label="More reading">{links}<a class="rf-return" href="index.html">{localized('All Recent Fiction →', '返回近年小说导读 →', converter)}</a></nav>
</main>{footer(converter)}
</body></html>'''


def load_books() -> list[dict]:
    books = []
    required = ('slug', 'book', 'author', 'book_date', 'publisher', 'en_title', 'zh_title', 'en_deck', 'zh_deck', 'en_notice', 'zh_notice', 'en_body', 'zh_body', 'en_source_note', 'zh_source_note')
    for slug in ORDER:
        book = json.loads((SOURCE / f'{slug}.json').read_text(encoding='utf-8'))
        if any(not isinstance(book.get(field), str) or not book[field].strip() for field in required):
            raise ValueError(f'Missing book data: {slug}')
        if book['slug'] != slug:
            raise ValueError(f'Slug mismatch: {slug}')
        for source in book['sources']:
            if source['kind'] not in KIND_LABELS or urlsplit(source['url']).scheme != 'https':
                raise ValueError(f'Invalid source: {slug} / {source}')
        books.append(book)
    return books


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    books = load_books()
    converter = TraditionalConverter()
    try:
        outputs = {TARGET / 'index.html': render_index(books, converter)}
        outputs.update({TARGET / (book['slug'] + '.html'): render_article(book, books, converter) for book in books})
    finally:
        converter.close()
    stale = []
    for path, value in outputs.items():
        content = value.rstrip() + '\n'
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
    if stale:
        print('Stale Recent Fiction pages: ' + ', '.join(stale))
        return 1
    print(f'{"OK" if args.check else "Built"}: {len(books)} Recent Fiction guides in English, Simplified and Traditional Chinese.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
