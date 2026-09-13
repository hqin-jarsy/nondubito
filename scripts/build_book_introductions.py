#!/usr/bin/env python3
"""Build the Book Introductions entrance and the distinct Nonfiction shelf.

Shares typography, safe prose rendering and language behavior with Recent
Fiction, not its novel-specific editorial assumptions or source requirements.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from urllib.parse import urlsplit

import build_recent_fiction as fiction
from build_recent_fiction import TraditionalConverter, esc, localized, prose

ROOT = fiction.ROOT
SOURCE = ROOT / 'data/nonfiction'
TARGET = ROOT / 'essays/nonfiction'
HUB = ROOT / 'essays/books/index.html'
PUBLISHED = '2026-09-13'
ORDER = ('raising-hare', 'small-is-beautiful')
SOURCE_LABELS = {
    'interview': ('Author conversation', '作者访谈'),
    'excerpt': ('Read the original', '阅读原作'),
    'publisher': ('Publication details', '出版资料'),
    'review': ('Another reader’s view', '另一位读者的看法'),
    'research': ('Research & discussion', '研究与讨论'),
    'institution': ('Institutional sources', '机构资料'),
}


def validate_book(book: dict, slug: str) -> None:
    required = ('slug', 'book', 'author', 'book_date', 'guide_date', 'publisher',
                'en_title', 'zh_title', 'en_deck', 'zh_deck', 'en_notice', 'zh_notice',
                'en_body', 'zh_body', 'en_source_note', 'zh_source_note',
                'topic_en', 'topic_zh', 'genre_en', 'genre_zh')
    if any(not isinstance(book.get(key), str) or not book[key].strip() for key in required):
        raise ValueError(f'Incomplete nonfiction data: {slug}')
    if book['slug'] != slug or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError(f'Invalid nonfiction slug: {slug}')
    # Preserve known precision: do not manufacture a day for a 1973 first edition.
    if not re.fullmatch(r'[1-9]\d{3}', book['book_date']):
        date.fromisoformat(book['book_date'])
    published = date.fromisoformat(book['guide_date'])
    if date.fromisoformat(book.get('updated_date', book['guide_date'])) < published:
        raise ValueError(f'Update predates guide publication: {slug}')
    if book.get('book_language', 'en') not in fiction.BOOK_LANGUAGES:
        raise ValueError(f'Unknown book language: {slug}')
    for field in ('book_en', 'book_zh'):
        if field in book and (not isinstance(book[field], str) or not book[field].strip()):
            raise ValueError(f'Invalid book title: {slug}/{field}')
    if not isinstance(book.get('search_aliases', []), list) or any(not isinstance(v, str) or not v.strip() for v in book.get('search_aliases', [])):
        raise ValueError(f'Invalid search aliases: {slug}')
    if book.get('reading_basis', 'excerpt') not in ('excerpt', 'excerpts-and-research', 'excerpts-and-interviews'):
        raise ValueError(f'Unknown reading basis: {slug}')
    sources = book.get('sources')
    if not isinstance(sources, list) or not sources:
        raise ValueError(f'Missing nonfiction sources: {slug}')
    for source in sources:
        if any(not isinstance(source.get(key), str) or not source[key].strip() for key in ('kind', 'url', 'label', 'description_en', 'description_zh')):
            raise ValueError(f'Incomplete source: {slug}')
        url = urlsplit(source['url'])
        if source['kind'] not in SOURCE_LABELS or url.scheme != 'https' or not url.netloc:
            raise ValueError(f'Invalid nonfiction source: {slug}')
    urls = {source['url'] for source in sources}
    if len(urls) != len(sources):
        raise ValueError(f'Duplicate nonfiction sources: {slug}')
    if not any(source['kind'] == 'excerpt' for source in sources):
        raise ValueError(f'These reading bases require an original excerpt: {slug}')
    # A deceased author does not need a manufactured contemporary interview.
    for body in (book['en_body'], book['zh_body']):
        inline_urls = set(re.findall(r'\]\((https://[^\s]+?)\)', body))
        if inline_urls - urls:
            raise ValueError(f'Unlisted inline sources: {slug}: {inline_urls - urls}')


def load_books() -> list[dict]:
    books = []
    for slug in ORDER:
        book = json.loads((SOURCE / f'{slug}.json').read_text(encoding='utf-8'))
        validate_book(book, slug)
        books.append(book)
    if {path.stem for path in SOURCE.glob('*.json')} != set(ORDER):
        raise ValueError('Nonfiction inventory differs from ORDER')
    return books


def head(title: str, description: str, filename: str, book: dict | None = None, *, hub: bool = False, modified: str = PUBLISHED) -> str:
    return fiction.head(title, description, filename, book, modified,
                        collection='books' if hub else 'nonfiction',
                        collection_name='Book Introductions' if hub else 'Nonfiction',
                        collection_published=PUBLISHED, asset_prefix='../recent-fiction/',
                        extra_styles=('../books/books.css?v=20260913',))


def breadcrumbs(converter: TraditionalConverter, book: dict | None = None, *, hub: bool = False) -> str:
    if hub:
        content = f'<a href="../../explore.html#stories">{localized("Books, screen & narrative", "书籍、影视与叙事", converter)}</a><span aria-hidden="true">/</span><span aria-current="page">{localized("Book Introductions", "书籍导读", converter)}</span>'
    else:
        content = f'<a href="../books/index.html">{localized("Book Introductions", "书籍导读", converter)}</a><span aria-hidden="true">/</span>'
        if book:
            content += f'<a href="index.html">{localized("Nonfiction", "非虚构导读", converter)}</a><span aria-hidden="true">/</span><span aria-current="page">{fiction.book_label(book, converter)}</span>'
        else:
            content += f'<span aria-current="page">{localized("Nonfiction", "非虚构导读", converter)}</span>'
    return f'<nav class="reading-breadcrumbs" aria-label="Breadcrumb">{content}</nav>'


def card(book: dict, converter: TraditionalConverter, prefix: str = '') -> str:
    return f'''<a class="rf-book-card" href="{prefix}{book['slug']}.html">
<div class="rf-card-top"><span class="rf-kicker">{localized(esc(book['genre_en']), esc(book['genre_zh']), converter)}</span><span class="rf-year">{book['book_date'][:4]}</span></div>
{localized(esc(book['en_title']), esc(book['zh_title']), converter, 'h3')}
<p class="rf-card-author">{esc(book['author'])}</p>
{localized(esc(book['en_deck']), esc(book['zh_deck']), converter, 'p', 'rf-card-deck')}
<span class="rf-card-cta">{localized('Read the introduction', '读这篇导读', converter)} →</span></a>'''


def source_section(book: dict, converter: TraditionalConverter) -> str:
    cards = []
    for source in sorted(book['sources'], key=lambda item: list(SOURCE_LABELS).index(item['kind'])):
        en, zh = SOURCE_LABELS[source['kind']]
        cards.append(f'''<a class="rf-source-card" href="{esc(source['url'])}"><span class="rf-kicker">{localized(esc(en), esc(zh), converter)}</span><h3>{esc(source['label'])} ↗</h3>{localized(esc(source['description_en']), esc(source['description_zh']), converter, 'p')}</a>''')
    return f'''<section class="rf-sources" id="sources" aria-labelledby="source-heading">
<h2 id="source-heading">{localized('Sources &amp; further reading', '出处与延伸阅读', converter)}</h2>
{localized(esc(book['en_source_note']), esc(book['zh_source_note']), converter, 'p', 'rf-source-note')}
{localized('Follow the links for the original passages and fuller discussions. Distinguish the author’s account, later research, and this introduction’s own questions.', '外链提供原作段落与更完整的讨论。阅读时请区分作者的叙述、后来的研究，以及本文继续提出的问题。', converter, 'p', 'rf-source-spoilers')}
<div class="rf-source-grid">{''.join(cards)}</div></section>'''


def render_article(book: dict, books: list[dict], converter: TraditionalConverter) -> str:
    published = date.fromisoformat(book['guide_date'])
    display_date = f"{published.strftime('%b')} {published.day}, {published.year}"
    aliases = ' '.join([book['book'], *fiction.book_aliases(book), *book.get('search_aliases', []), book['author'], 'Nonfiction 非虚构导读 非虛構導讀'])
    excerpt = next(item for item in book['sources'] if item['kind'] == 'excerpt')
    related = ''.join(f'<a href="{item["slug"]}.html"><span class="rf-kicker">{localized(esc(item["genre_en"]), esc(item["genre_zh"]), converter)}</span><strong>{fiction.book_label(item, converter)}</strong>→</a>' for item in books if item['slug'] != book['slug'])
    return f'''<!DOCTYPE html>
<html lang="en" data-lang="en" data-editions="en zh zh-hant">
{head(book['en_title'] + ' · ' + book['zh_title'], book['en_deck'], book['slug'] + '.html', book)}
<body class="site-shell-page explicit-hant rf-page books-page">{fiction.navigation()}
<main class="rf-wrap rf-article" data-search="{esc(aliases)}">{breadcrumbs(converter, book)}
<section class="rf-article-hero">
<p class="rf-kicker">{localized(esc(book['topic_en']), esc(book['topic_zh']), converter)}</p>
{localized(esc(book['en_title']), esc(book['zh_title']), converter, 'h1')}
{localized(esc(book['en_deck']), esc(book['zh_deck']), converter, 'p', 'rf-article-deck')}
{fiction.original_edition(book, converter)}
<p class="rf-book-meta">{esc(book['author'])} · {localized(esc(book['genre_en']), esc(book['genre_zh']), converter)}</p>
<p class="rf-book-meta">{localized('Original publication', '原作首版', converter)} <time datetime="{book['book_date']}">{book['book_date']}</time> · {esc(book['publisher'])}</p>
<p class="rf-guide-meta">Han Qin (秦汉) · {localized('Guide published', '导读发布', converter)} <time datetime="{book['guide_date']}">{display_date}</time></p>
<div class="rf-notice">{localized(esc(book['en_notice']), esc(book['zh_notice']), converter, 'p')}</div>
<div class="rf-actions"><a href="#sources">{localized('Sources &amp; further reading ↓', '出处与延伸阅读 ↓', converter)}</a><a href="{esc(excerpt['url'])}">{localized('Read the original ↗', '先读一段原作 ↗', converter)}</a></div>
</section>
<article class="rf-prose lang-en" lang="en">{prose(book['en_body'])}</article>
<article class="rf-prose lang-zh" lang="zh-Hans">{prose(book['zh_body'])}</article>
<article class="rf-prose lang-hant" lang="zh-Hant">{prose(converter.convert(book['zh_body']))}</article>
{source_section(book, converter)}
<nav class="rf-next reading-next-grid" aria-label="More reading">{related}<a href="../recent-fiction/index.html"><span class="rf-kicker">{localized('A different shelf', '换一架书看看', converter)}</span><strong>{localized('Recent Fiction', '近年小说导读', converter)}</strong>→</a><a class="rf-return" href="index.html">{localized('All Nonfiction →', '返回非虚构导读 →', converter)}</a></nav>
</main>{fiction.footer(converter)}</body></html>'''


def render_index(books: list[dict], converter: TraditionalConverter) -> str:
    return f'''<!DOCTYPE html>
<html lang="en" data-lang="en" data-editions="en zh zh-hant">
{head('Nonfiction · 非虚构导读', 'Discover memoir, nature writing and books of ideas: introductions that distinguish a book’s claims from the questions we bring to it.', 'index.html', modified=max(book.get('updated_date', book['guide_date']) for book in books))}
<body class="site-shell-page explicit-hant rf-page books-page">{fiction.navigation()}
<main class="rf-wrap">{breadcrumbs(converter)}
<section class="rf-shelf-hero"><div><p class="rf-kicker">Non Dubito · {localized('Lives, ideas, the world', '经验、思想与世界', converter)}</p>
{localized('Nonfiction', '非虚构导读', converter, 'h1')}
{localized('Other ways of looking at the life we share.', '换一个角度，看见我们共同生活的世界。', converter, 'p', 'rf-hero-deck')}</div>
<div class="rf-editor-note">{localized('A memoir can begin with an unexpected visitor. A book of ideas can begin with a question we have stopped asking. This shelf welcomes recent work and older books worth returning to.', '回忆录可以从一位意外来客开始，思想著作可以从一个我们不再追问的问题开始。这里既介绍新作，也重访值得再读的旧书。', converter, 'p')}
{localized('The introductions offer a way in, not a substitute for the book. Sources, the scope of reading, and disagreements remain visible.', '导读提供入口，不代替原作。参考了什么、读到了哪里、哪些观点还值得争论，都尽量说明白。', converter, 'p')}</div></section>
<nav class="rf-shelf-nav" aria-label="Book shelves"><a href="../books/index.html">{localized('All book introductions', '全部书籍导读', converter)}</a><a href="../recent-fiction/index.html">{localized('Recent Fiction', '近年小说', converter)}</a><span class="rf-shelf-count">{localized(f'{len(books)} books · EN / 简 / 繁', f'{len(books)} 部作品 · 英 / 简 / 繁', converter)}</span></nav>
<section class="books-featured" aria-labelledby="nonfiction-books"><h2 id="nonfiction-books">{localized('On this shelf', '这一架上的书', converter)}</h2><p class="books-section-note">{localized('The year on each card is the book’s original publication year, not the date of this introduction.', '卡片年份为原作首版年份，不是导读的发布日期。', converter)}</p><div class="rf-book-grid">{''.join(card(book, converter) for book in books)}</div></section>
<aside class="rf-shelf-afterword"><h2>{localized('A question can lead elsewhere', '一个问题，也可以通向别处', converter)}</h2>{localized('Follow the books back to everyday life, or stay with their questions in the philosophy library. Agreement with an author is not a condition of finding a book worth reading.', '可以把书里的问题带回日常生活，也可以去哲学文库继续追问。一本书值得读，不意味着我们必须赞同作者的一切。', converter, 'p')}<div class="rf-actions"><a href="../../explore.html#everyday">{localized('Everyday Life →', '日常生活 →', converter)}</a><a href="../../explore.html#sae">{localized('SAE & Philosophy →', 'SAE 与哲学 →', converter)}</a></div></aside>
</main>{fiction.footer(converter)}</body></html>'''


def render_hub(books: list[dict], novels: list[dict], converter: TraditionalConverter) -> str:
    count = len(books) + len(novels)
    modified = max(book.get('updated_date', book['guide_date']) for book in books + novels)
    doors = []
    for href, en, zh, n, en_deck, zh_deck in (
        ('../recent-fiction/index.html', 'Recent Fiction', '近年小说', len(novels), 'Enter through a voice, a room, an encounter. Leave the turns and endings for your own reading.', '从一个声音、一间房、一次相遇走进小说。把重要转折与结局留给你的阅读。'),
        ('../nonfiction/index.html', 'Nonfiction', '非虚构', len(books), 'Memoir, nature writing and books of ideas. Recent work and older books, with room to question them.', '回忆录、自然书写与思想著作。介绍新作，也重访经典，保留继续追问的空间。'),
    ):
        doors.append(f'<a class="books-door" href="{href}"><p class="rf-kicker">{localized(f"{n} books · 3 reading modes", f"{n} 部作品 · 英 / 简 / 繁", converter)}</p>{localized(en, zh, converter, "h2")}{localized(en_deck, zh_deck, converter, "p", "books-door-deck")}<span class="rf-card-cta">{localized("Browse the shelf →", "去这架书看看 →", converter)}</span></a>')
    return f'''<!DOCTYPE html>
<html lang="en" data-lang="en" data-editions="en zh zh-hant">
{head('Book Introductions · 书籍导读', 'Find a book worth opening: introductions to fiction and nonfiction, with original excerpts, author conversations and further reading.', 'index.html', hub=True, modified=modified)}
<body class="site-shell-page explicit-hant rf-page books-page">{fiction.navigation()}
<main class="rf-wrap">{breadcrumbs(converter, hub=True)}
<section class="rf-shelf-hero"><div><p class="rf-kicker">Non Dubito · {localized('An invitation to read', '给阅读留一个入口', converter)}</p>
{localized('Book Introductions', '书籍导读', converter, 'h1')}
{localized('Find a book you want to spend time with.', '找到一本，你愿意花时间相处的书。', converter, 'p', 'rf-hero-deck')}</div>
<div class="rf-editor-note">{localized('What might draw you into a book? A person you do not yet understand, a life unlike your own, or a question that changes the way you see an ordinary day.', '一本书为什么值得翻开？也许因为一个尚未理解的人，一种陌生的生活，或一个让寻常日子变得不同的问题。', converter, 'p')}
{localized('These guides introduce rather than replace the books. Each explains its reading scope and offers links outward: to original passages, conversations, research or other readers.', '这里的导读是邀请，不代替原作。每篇说明阅读与参考资料的范围，也提供通向原作节选、访谈、研究或其他读者的外链。', converter, 'p')}</div></section>
<p class="books-total">{localized(f'{count} books · two shelves · English / 简体 / 繁體', f'{count} 部作品 · 两架书 · 英文 / 简体 / 繁体', converter)}</p>
<div class="books-doors">{''.join(doors)}</div>
<section class="books-featured" aria-labelledby="books-featured"><div class="books-section-heading"><h2 id="books-featured">{localized('Begin with nonfiction', '先从这两部非虚构开始', converter)}</h2><a href="../nonfiction/index.html">{localized('Nonfiction shelf →', '非虚构书架 →', converter)}</a></div><div class="rf-book-grid">{''.join(card(book, converter, '../nonfiction/') for book in books[:2])}</div></section>
<aside class="rf-shelf-afterword"><h2>{localized('Looking for a closer reading?', '想读更深入的作品解读？', converter)}</h2>{localized('The longer reading series live elsewhere. If you have read the book and want to stay with its characters, scenes and difficult choices, follow Literary Readings or Science Fiction.', '长篇、成系列的细读另有入口。如果已经读过原作，想继续讨论人物、场景与艰难选择，可以进入文学作品解读或科幻小说解读。', converter, 'p')}<div class="rf-actions"><a href="../literature/index.html">{localized('Literary Readings →', '文学作品解读 →', converter)}</a><a href="../science-fiction/index.html">{localized('Science Fiction →', '科幻小说解读 →', converter)}</a></div></aside>
</main>{fiction.footer(converter)}</body></html>'''


def library_section(books: list[dict], converter: TraditionalConverter) -> str:
    cards = []
    for book in books:
        cards.append(f'''<a href="essays/nonfiction/{book['slug']}.html" class="series-card">
<span class="series-card-count"><span class="lang-en">1 guide · {book['book_date'][:4]} · EN / 简 / 繁</span><span class="lang-zh cl-zh">1 篇导读 · {book['book_date'][:4]} 年首版 · 英 / 简 / 繁</span><span class="lang-zh cl-hant">1 篇導讀 · {book['book_date'][:4]} 年首版 · 英 / 簡 / 繁</span></span>
<div class="series-card-title-zh cl-zh">{esc(book['zh_title'])}</div><div class="series-card-title-zh cl-hant">{esc(converter.convert(book['zh_title']))}</div><div class="series-card-title-en">{esc(book['en_title'])}</div>
<p class="series-card-desc-zh lang-zh cl-zh">{esc(book['zh_deck'])}</p><p class="series-card-desc-zh lang-zh cl-hant">{esc(converter.convert(book['zh_deck']))}</p><p class="series-card-desc-en lang-en">{esc(book['en_deck'])}</p>
<span class="series-card-arrow lang-en">Read introduction</span><span class="series-card-arrow lang-zh cl-zh">阅读导读</span><span class="series-card-arrow lang-zh cl-hant">閱讀導讀</span></a>''')
    return f'''<!-- NONFICTION CATEGORY START -->
<hr class="lib-divider"><section class="lib-section" id="nonfiction"><div class="lib-section-header"><span class="lib-section-tag">Category 08</span>
<a href="essays/nonfiction/index.html" class="lib-section-name" style="text-decoration:none"><span class="zh cl-zh">非虚构导读</span><span class="zh cl-hant">非虛構導讀</span><span class="en">Nonfiction</span></a>
<p class="lib-section-desc lang-en">Memoir, nature writing and books of ideas: recent work and classics, with sources, questions and room for disagreement. <a href="essays/books/index.html">All book introductions →</a></p>
<p class="lib-section-desc lang-zh cl-zh">回忆录、自然书写与思想著作：介绍新作，也重访经典，说明出处，保留疑问与分歧。<a href="essays/books/index.html">全部书籍导读 →</a></p>
<p class="lib-section-desc lang-zh cl-hant">回憶錄、自然書寫與思想著作：介紹新作，也重訪經典，說明出處，保留疑問與分歧。<a href="essays/books/index.html">全部書籍導讀 →</a></p>
</div><div class="series-grid">{''.join(cards)}</div></section>
<!-- NONFICTION CATEGORY END -->'''


def outputs() -> dict:
    books = load_books()
    novels = fiction.load_books()
    converter = TraditionalConverter()
    try:
        result = {TARGET / 'index.html': render_index(books, converter), HUB: render_hub(books, novels, converter)}
        result.update({TARGET / (book['slug'] + '.html'): render_article(book, books, converter) for book in books})
        library = (ROOT / 'library.html').read_text(encoding='utf-8')
        pattern = r'<!-- NONFICTION CATEGORY START -->.*?<!-- NONFICTION CATEGORY END -->'
        if len(re.findall(pattern, library, re.S)) != 1:
            raise ValueError('Expected one Nonfiction Library section')
        result[ROOT / 'library.html'] = re.sub(pattern, lambda _: library_section(books, converter), library, flags=re.S)
        return result
    finally:
        converter.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for path, value in outputs().items():
        content = value.rstrip() + '\n'
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
    if stale:
        print('Stale book introductions: ' + ', '.join(stale))
        return 1
    print(f'{"OK" if args.check else "Built"}: Book Introductions hub and {len(ORDER)} nonfiction guides in English, Simplified and Traditional Chinese.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
