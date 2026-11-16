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
UPDATED = '2026-11-15'
EN = 'Theatre & Musicals'
ZH = '戏剧与音乐剧'
EXTRA_EDITIONS = {'ja': '日本語', 'fr': 'Français', 'de': 'Deutsch', 'es': 'Español', 'ko': '한국어'}
DECK_EN = 'Thirty-five musical-theatre essays, beginning with characters, song, and staging. All in Chinese; the first twenty also have six complete foreign-language editions.'
DECK_ZH = '三十五部音乐剧，从人物、歌声与舞台出发，谈归属、劳动、照顾与共同生活。全篇提供简繁中文，前二十部另有六种外语全文。'


def catalog():
    return json.loads((ROOT / 'data/theatre/catalog.json').read_text())['works']


def has_english(work):
    return 'en' in work.get('languages', ['en', 'zh', 'zh-hant'])


def editions(work):
    return EXTRA_EDITIONS if work is None or has_english(work) else {}


def title_en(work):
    # Chinese titles on an English discovery shelf are not translated essays.
    return load('en' if has_english(work) else 'zh', work['slug'])[0]


def language_note(work):
    return ('8 languages', '八语全文') if has_english(work) else ('Chinese editions only', '简体 · 繁体')


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
        if not has_english(work):
            schema['inLanguage'] = ['zh-Hans', 'zh-Hant']
            result = re.sub(r'<link rel="alternate" hreflang="en"[^>]*>', '', result)
            result = result.replace('site-shell.js?v=20260905b', 'site-shell.js?v=20261115')
            result = result.replace('recent-fiction.js?v=20260911', 'recent-fiction.js?v=20261115')
    result = result.replace(match.group(1), json.dumps(schema, ensure_ascii=False))
    alternates = ''.join(f'<link rel="alternate" hreflang="{lang}" href="https://nondubito.net/essays/theatre/{lang}/{filename}">' for lang in editions(work))
    return result.replace('</head>', alternates + '</head>')


@tracked_html
def wrap(content, title, deck, filename, converter, work=None):
    names = ' '.join(f"{w['name']} {w['name_zh']} {' '.join(w['creators'])}" for w in ([work] if work else catalog()))
    current = f'<span aria-hidden="true"> / </span><span aria-current="page">{localized(esc(work["name"]), esc(work["name_zh"]), converter)}</span>' if work else ''
    html_language = 'lang="en" data-lang="en" data-editions="en zh zh-hant"'
    if work and not has_english(work):
        html_language = 'lang="zh-Hans" data-lang="zh" data-editions="zh zh-hant" data-reader-languages="zh zh-hant"'
    other_editions = ''.join(f'<a href="{lang}/{filename}" lang="{lang}">{label}</a>' for lang, label in editions(work).items())
    edition_nav = f'<nav aria-label="Other editions" style="display:flex;gap:1rem;flex-wrap:wrap;margin:1rem 0 2rem">{other_editions}</nav>' if other_editions else ''
    return f'''<!DOCTYPE html>
<html {html_language}>
{page_head(title, deck, filename, work)}
<body class="site-shell-page explicit-hant rf-page">{navigation()}
<main class="rf-wrap{' rf-article' if work else ''}" data-search="{esc('Theatre Musicals 戏剧 音乐剧 戲劇 音樂劇 ' + names)}">
<nav class="reading-breadcrumbs" aria-label="Breadcrumb"><a href="../../explore.html#stories">{localized('Books, Screen &amp; Narrative', '书籍、影视与叙事', converter)}</a><span aria-hidden="true"> / </span><a href="index.html">{localized(esc(EN), ZH, converter)}</a>{current}</nav>
{edition_nav}
{content}
</main>{footer(converter)}</body></html>'''


def render_card(work, c):
    et = title_en(work)
    zt, _, _ = load('zh', work['slug'])
    tr = lambda en, zh, tag='span', classes='': localized(en, zh, c, tag, classes)
    return f'''<a class="rf-book-card" href="{work['slug']}.html"><div class="rf-card-top"><span class="rf-kicker">{tr(esc(work['topic_en']), esc(work['topic_zh']))}</span><span class="rf-year">{work['year']}</span></div>{tr(esc(et), esc(zt), 'h3')}<p class="rf-card-deck">{tr(esc(work['deck_en']), esc(work['deck_zh']))}</p><p class="rf-card-author">{tr(*language_note(work))}</p><span class="rf-card-cta">{tr('Read the essay →', '阅读文章 →')}</span></a>'''


def library_block():
    c = TraditionalConverter()
    try:
        cards = []
        for w in catalog():
            et = title_en(w)
            zt, _, _ = load('zh', w['slug'])
            en_languages, zh_languages = language_note(w)
            cards.append(f'''<a href="essays/theatre/{w['slug']}.html" class="series-card"><span class="series-card-count">{w['year']} · {en_languages} / {zh_languages}</span><div class="series-card-title-en">{esc(et)}</div><div class="series-card-title-zh cl-zh">{esc(zt)}</div><div class="series-card-title-zh cl-hant">{esc(c.convert(zt))}</div><p class="series-card-desc-en lang-en">{esc(w['deck_en'])}</p><p class="series-card-desc-zh lang-zh cl-zh">{esc(w['deck_zh'])}</p><p class="series-card-desc-zh lang-zh cl-hant">{esc(c.convert(w['deck_zh']))}</p><span class="series-card-arrow lang-en">Read essay →</span><span class="series-card-arrow lang-zh cl-zh">阅读文章 →</span><span class="series-card-arrow lang-zh cl-hant">閱讀文章 →</span></a>''')
        description_en = 'Thirty-five musical-theatre essays. All have complete Simplified and Traditional Chinese editions; the first twenty also have complete English, Japanese, French, German, Spanish and Korean editions.'
        description_zh = '三十五部音乐剧，全部提供简繁中文全文；前二十部另有英、日、法、德、西、韩全文。新增十五篇暂不提供外语译文。'
        return '''<!-- THEATRE CATEGORY START -->
<hr class="lib-divider">
<section class="lib-section" id="theatre"><div class="lib-section-header"><span class="lib-section-tag">Category 18</span><a href="essays/theatre/index.html" class="lib-section-name" style="text-decoration:none"><span class="en">Theatre &amp; Musicals</span><span class="zh cl-zh">戏剧与音乐剧</span><span class="zh cl-hant">戲劇與音樂劇</span></a>''' + f'''<p class="lib-section-desc lang-en">{description_en}</p><p class="lib-section-desc lang-zh cl-zh">{description_zh}</p><p class="lib-section-desc lang-zh cl-hant">{c.convert(description_zh)}</p></div><div class="series-grid">''' + '\n'.join(cards) + '''</div></section>
<!-- THEATRE CATEGORY END -->'''
    finally:
        c.close()


def render_chinese(work, index, works, converter):
    title, notice, body = load('zh', work['slug'])

    def tr(zh, tag='span', classes=''):
        suffix = (' ' + classes) if classes else ''
        return (f'<{tag} class="lang-zh{suffix}">{zh}</{tag}>'
                f'<{tag} class="lang-hant{suffix}">{converter.convert(zh)}</{tag}>')

    neighbors = []
    if index:
        prev = works[index - 1]
        neighbors.append(f'<a href="{prev["slug"]}.html">← {tr(esc(prev["name_zh"]))}</a>')
    neighbors.append(f'<a href="index.html">{tr("返回戏剧与音乐剧")}</a>')
    if index + 1 < len(works):
        nxt = works[index + 1]
        neighbors.append(f'<a href="{nxt["slug"]}.html">{tr(esc(nxt["name_zh"]))} →</a>')
    source = work.get('scope_zh', '依据授权剧情、制作与教育资料、主创访谈及署名评论写作。这是舞台作品介绍与分析，并非现场观剧或完整观看影像后的演出评论。资料与编辑复检另行留档，正文不摘引歌词。')
    content = f'''<section class="rf-article-hero"><p class="rf-kicker">{tr(esc(work['topic_zh']))}</p>{tr(esc(title), 'h1')}{tr(esc(work['deck_zh']), 'p', 'rf-article-deck')}<p class="rf-guide-meta">Han Qin (秦汉) · {tr('发布')} <time datetime="{work['published']}">{work['published']}</time> · {tr('简体、繁体中文全文')}</p><div class="rf-notice">{tr(esc(notice), 'p')}</div></section>
<article class="rf-prose lang-zh" lang="zh-Hans">{prose(body)}</article>
<article class="rf-prose lang-hant" lang="zh-Hant">{prose(converter.convert(body))}</article>
<aside class="rf-sources">{tr('关于本文', 'h2')}{tr(esc(source), 'p', 'rf-source-note')}</aside>
<nav class="rf-next" aria-label="More reading">{''.join(neighbors)}</nav>'''
    return wrap(content, title, work['deck_zh'], work['slug'] + '.html', converter, work)


def outputs():
    works = catalog()
    c = TraditionalConverter()
    try:
        tr = lambda en, zh, tag='span', classes='': localized(en, zh, c, tag, classes)
        cards = '\n'.join(render_card(w, c) for w in works)
        shelf = f'''<section class="rf-shelf-hero"><div><p class="rf-kicker">{tr(f'Stage &amp; people · {len(works)} works', f'舞台与人 · {len(works)}部作品')}</p>{tr(esc(EN), ZH, 'h1')}{tr(DECK_EN, DECK_ZH, 'p', 'rf-hero-deck')}</div><div class="rf-editor-note">{tr('These essays attend to what a scene makes possible: who can speak, who must wait, and what changes when another person sings. Plot context accompanies the discussion.', '留意一场戏让谁开口、让谁等待，又怎样通过另一人的歌声改变问题。没有看过作品，也能跟着情节进入。', 'p')}{tr('Language availability is marked on each card. The fifteen new essays are in Simplified and Traditional Chinese; the original twenty retain their eight complete editions.', '每张卡片标明可用语言。新增十五篇先提供简繁中文，原有二十篇八语全文保持不变。', 'p')}</div></section><section class="rf-year-section"><div class="rf-shelf-heading">{tr('Ways into musical theatre', '从人物与舞台进入音乐剧', 'h2')}</div><div class="rf-book-grid">{cards}</div></section>'''
        result = {ROOT / 'essays/theatre/index.html': wrap(shelf, EN + ' · ' + ZH, DECK_EN, 'index.html', c)}
        for i, w in enumerate(works):
            if not has_english(w):
                result[ROOT / f'essays/theatre/{w["slug"]}.html'] = render_chinese(w, i, works, c)
                continue
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
    print(f'OK: theatre collection and {len(catalog())} essays; available languages follow each work')


if __name__ == '__main__':
    main()
