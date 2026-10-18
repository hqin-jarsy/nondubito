#!/usr/bin/env python3
"""Build the theatre collection from reviewed, versioned EN/Hans manuscripts."""
import argparse
import json
import re
from pathlib import Path

from build_recent_fiction import TraditionalConverter, esc, localized, prose, head, navigation, footer
from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-10-13'
UPDATED = '2026-10-18'
EN = 'Theatre & Musicals'
ZH = '戏剧与音乐剧'
DECK_EN = 'Twenty musical-theatre essays, beginning with characters, song, and staging: belonging, work, care, and lives shared without becoming the same.'
DECK_ZH = '二十部音乐剧，从人物、歌声与舞台出发，谈归属、劳动、照顾，以及怎样共同生活而不必活成彼此。'


def catalog():
    return json.loads((ROOT / 'data/theatre/catalog.json').read_text())['works']


def load(language, slug='hamilton'):
    title, notice, body = (ROOT / f'data/theatre/{slug}.{language}.md').read_text().strip().split('\n\n', 2)
    return title.removeprefix('# '), notice.strip('*'), body


def page_head(title, deck, filename, work=None):
    result = head(title, deck, filename, modified=work['published'] if work else UPDATED,
                  collection='theatre', collection_name=EN, collection_published=DATE,
                  asset_prefix='../recent-fiction/')
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', result, re.S)
    schema = json.loads(match.group(1))
    if work:
        schema.update({'@type': 'Article', 'headline': title,
                       'datePublished': work['published'], 'dateModified': work['published'],
                       'about': {'@type': 'CreativeWork', 'name': work['name'], 'genre': 'Musical theatre',
                                 'creator': [{'@type': 'Person', 'name': name} for name in work['creators']]},
                       'isPartOf': {'@type': 'CollectionPage', 'name': EN, 'url': 'https://nondubito.net/essays/theatre/'}})
        result = result.replace('content="website"', 'content="article"')
    return result.replace(match.group(1), json.dumps(schema, ensure_ascii=False))


@tracked_html
def wrap(content, title, deck, filename, converter, work=None):
    names = ' '.join(f"{w['name']} {w['name_zh']} {' '.join(w['creators'])}" for w in ([work] if work else catalog()))
    current = f'<span aria-hidden="true"> / </span><span aria-current="page">{localized(esc(work["name"]), esc(work["name_zh"]), converter)}</span>' if work else ''
    return f'''<!DOCTYPE html>
<html lang="en" data-lang="en" data-editions="en zh zh-hant">
{page_head(title, deck, filename, work)}
<body class="site-shell-page explicit-hant rf-page">{navigation()}
<main class="rf-wrap{' rf-article' if work else ''}" data-search="{esc('Theatre Musicals 戏剧 音乐剧 戲劇 音樂劇 ' + names)}">
<nav class="reading-breadcrumbs" aria-label="Breadcrumb"><a href="../../explore.html#stories">{localized('Books, Screen &amp; Narrative', '书籍、影视与叙事', converter)}</a><span aria-hidden="true"> / </span><a href="index.html">{localized(esc(EN), ZH, converter)}</a>{current}</nav>
{content}
</main>{footer(converter)}</body></html>'''


def render_card(work, c):
    et, _, _ = load('en', work['slug'])
    zt, _, _ = load('zh', work['slug'])
    tr = lambda en, zh, tag='span', classes='': localized(en, zh, c, tag, classes)
    return f'''<a class="rf-book-card" href="{work['slug']}.html"><div class="rf-card-top"><span class="rf-kicker">{tr(esc(work['topic_en']), esc(work['topic_zh']))}</span><span class="rf-year">{work['year']}</span></div>{tr(esc(et), esc(zt), 'h3')}<p class="rf-card-deck">{tr(esc(work['deck_en']), esc(work['deck_zh']))}</p><span class="rf-card-cta">{tr('Read the essay →', '阅读文章 →')}</span></a>'''


def library_block():
    c = TraditionalConverter()
    try:
        cards = []
        for w in catalog():
            et, _, _ = load('en', w['slug'])
            zt, _, _ = load('zh', w['slug'])
            cards.append(f'''<a href="essays/theatre/{w['slug']}.html" class="series-card"><span class="series-card-count">{w['year']} · EN / 简 / 繁</span><div class="series-card-title-en">{esc(et)}</div><div class="series-card-title-zh cl-zh">{esc(zt)}</div><div class="series-card-title-zh cl-hant">{esc(c.convert(zt))}</div><p class="series-card-desc-en lang-en">{esc(w['deck_en'])}</p><p class="series-card-desc-zh lang-zh cl-zh">{esc(w['deck_zh'])}</p><p class="series-card-desc-zh lang-zh cl-hant">{esc(c.convert(w['deck_zh']))}</p><span class="series-card-arrow lang-en">Read essay →</span><span class="series-card-arrow lang-zh cl-zh">阅读文章 →</span><span class="series-card-arrow lang-zh cl-hant">閱讀文章 →</span></a>''')
        return '''<!-- THEATRE CATEGORY START -->
<hr class="lib-divider">
<section class="lib-section" id="theatre"><div class="lib-section-header"><span class="lib-section-tag">Category 18</span><a href="essays/theatre/index.html" class="lib-section-name" style="text-decoration:none"><span class="en">Theatre &amp; Musicals</span><span class="zh cl-zh">戏剧与音乐剧</span><span class="zh cl-hant">戲劇與音樂劇</span></a><p class="lib-section-desc lang-en">Twenty musical-theatre essays on belonging, work, care and shared lives. Complete English, Simplified and Traditional Chinese editions.</p><p class="lib-section-desc lang-zh cl-zh">二十部音乐剧，谈归属、劳动、照顾与共同生活，英、简、繁全文。</p><p class="lib-section-desc lang-zh cl-hant">二十部音樂劇，談歸屬、勞動、照顧與共同生活，英、簡、繁全文。</p></div><div class="series-grid">''' + '\n'.join(cards) + '''</div></section>
<!-- THEATRE CATEGORY END -->'''
    finally:
        c.close()


def outputs():
    works = catalog()
    c = TraditionalConverter()
    try:
        tr = lambda en, zh, tag='span', classes='': localized(en, zh, c, tag, classes)
        cards = '\n'.join(render_card(w, c) for w in works)
        shelf = f'''<section class="rf-shelf-hero"><div><p class="rf-kicker">{tr('Stage &amp; people · 20 works', '舞台与人 · 20部作品')}</p>{tr(esc(EN), ZH, 'h1')}{tr(DECK_EN, DECK_ZH, 'p', 'rf-hero-deck')}</div><div class="rf-editor-note">{tr('These essays attend to what a scene makes possible: who can speak, who must wait, and what changes when another person sings. Plot context accompanies the discussion.', '留意一场戏让谁开口、让谁等待，又怎样通过另一人的歌声改变问题。没有看过作品，也能跟着情节进入。', 'p')}{tr('Each essay identifies its version and spoiler scope. Complete English, Simplified Chinese and Traditional Chinese editions; the original Hamilton essay remains available.', '每篇说明版本与剧透范围，提供英、简、繁全文。《汉密尔顿》原文继续保留。', 'p')}</div></section><section class="rf-year-section"><div class="rf-shelf-heading">{tr('Twenty ways into musical theatre', '从二十部音乐剧开始', 'h2')}</div><div class="rf-book-grid">{cards}</div></section>'''
        result = {ROOT / 'essays/theatre/index.html': wrap(shelf, EN + ' · ' + ZH, DECK_EN, 'index.html', c)}
        for i, w in enumerate(works):
            et, en, eb = load('en', w['slug'])
            zt, zn, zb = load('zh', w['slug'])
            neighbors = []
            if i:
                prev = works[i - 1]
                neighbors.append(f'<a href="{prev["slug"]}.html">← {tr(esc(prev["name"]), esc(prev["name_zh"]))}</a>')
            neighbors.append(f'<a href="index.html">{tr("All Theatre &amp; Musicals", "返回戏剧与音乐剧")}</a>')
            if i + 1 < len(works):
                nxt = works[i + 1]
                neighbors.append(f'<a href="{nxt["slug"]}.html">{tr(esc(nxt["name"]), esc(nxt["name_zh"]))} →</a>')
            source_en = w.get('scope_en', 'Based on licensed synopses, production and educational materials, creator interviews, and signed criticism. This is an introduction and analysis of the stage work, not a firsthand performance review or a claim to have watched a complete recording. Sources and editorial checks are retained in the publication records; no lyrics are reproduced.')
            source_zh = w.get('scope_zh', '依据授权剧情、制作与教育资料、主创访谈及署名评论写作。这是舞台作品介绍与分析，并非现场观剧或完整观看影像后的演出评论。资料与编辑复检另行留档，正文不摘引歌词。')
            article = f'''<section class="rf-article-hero"><p class="rf-kicker">{tr(esc(w['topic_en']), esc(w['topic_zh']))}</p>{tr(esc(et), esc(zt), 'h1')}{tr(esc(w['deck_en']), esc(w['deck_zh']), 'p', 'rf-article-deck')}<p class="rf-guide-meta">Han Qin (秦汉) · {tr('Published', '发布')} <time datetime="{w['published']}">{w['published']}</time></p><div class="rf-notice">{tr(esc(en), esc(zn), 'p')}</div></section>
<article class="rf-prose lang-en" lang="en">{prose(eb)}</article>
<article class="rf-prose lang-zh" lang="zh-Hans">{prose(zb)}</article>
<article class="rf-prose lang-hant" lang="zh-Hant">{prose(c.convert(zb))}</article>
<aside class="rf-sources">{tr('About this introduction', '关于本文', 'h2')}{tr(esc(source_en), esc(source_zh), 'p', 'rf-source-note')}</aside>
<nav class="rf-next" aria-label="More reading">{''.join(neighbors)}</nav>'''
            result[ROOT / f'essays/theatre/{w["slug"]}.html'] = wrap(article, et + ' · ' + zt, w['deck_en'], w['slug'] + '.html', c, w)
        return result
    finally:
        c.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, content in outputs().items():
        if args.check:
            if not path.exists() or path.read_text() != content:
                raise SystemExit(f'Stale: {path.relative_to(ROOT)}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    path = ROOT / 'library.html'
    source = path.read_text()
    updated, count = re.subn(r'<!-- THEATRE CATEGORY START -->.*?<!-- THEATRE CATEGORY END -->', lambda _: library_block(), source, flags=re.S)
    assert count == 1, 'Expected one theatre Library block'
    if args.check:
        assert updated == source, 'Stale theatre Library block'
    elif updated != source:
        path.write_text(updated)
    print(f'OK: theatre collection and {len(catalog())} complete EN/Hans/Hant essays')


if __name__ == '__main__':
    main()
