#!/usr/bin/env python3
"""Build the theatre shelf and full EN/Hans/Hant essays from versioned Markdown."""
import argparse
import json
import re
from pathlib import Path

from build_recent_fiction import TraditionalConverter, esc, localized, prose, head, navigation, footer
from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-10-13'
EN = 'Theatre & Musicals'
ZH = '戏剧与音乐剧'
DECK_EN = 'Begin with characters, dialogue, song, and staging: how a work presents human situations, relationships, and choices.'
DECK_ZH = '从人物、对白、歌声与舞台出发，读懂一部戏怎样呈现人的处境、关系与选择。'
ESSAY_EN = 'A wedding revisited, two different paces of life, and a wife who refuses to remain a footnote to achievement.'
ESSAY_ZH = '从一场重新展开的婚礼出发，听见不同的人生节奏，也听见不愿只为伟业让路的伴侣。'


def load(language):
    title, notice, body = (ROOT / f'data/theatre/hamilton.{language}.md').read_text().strip().split('\n\n', 2)
    return title.removeprefix('# '), notice.strip('*'), body


def page_head(title, deck, filename, article=False):
    result = head(title, deck, filename, collection='theatre', collection_name=EN,
                  collection_published=DATE, asset_prefix='../recent-fiction/')
    if article:
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', result, re.S)
        schema = json.loads(match.group(1))
        schema.update({'@type': 'Article', 'headline': title,
                       'about': {'@type': 'CreativeWork', 'name': 'Hamilton', 'genre': 'Musical theatre',
                                 'creator': {'@type': 'Person', 'name': 'Lin-Manuel Miranda'}},
                       'isPartOf': {'@type': 'CollectionPage', 'name': EN, 'url': 'https://nondubito.net/essays/theatre/'}})
        result = result.replace(match.group(1), json.dumps(schema, ensure_ascii=False))
        result = result.replace('content="website"', 'content="article"')
    return result


@tracked_html
def wrap(content, title, deck, filename, converter, article=False):
    return f'''<!DOCTYPE html>
<html lang="en" data-lang="en" data-editions="en zh zh-hant">
{page_head(title, deck, filename, article)}
<body class="site-shell-page explicit-hant rf-page">{navigation()}
<main class="rf-wrap{' rf-article' if article else ''}" data-search="Theatre Musicals Hamilton 汉密尔顿 漢密爾頓 戏剧 音乐剧 戲劇 音樂劇 Lin-Manuel Miranda">
<nav class="reading-breadcrumbs" aria-label="Breadcrumb"><a href="../../explore.html#stories">{localized('Books, Screen &amp; Narrative', '书籍、影视与叙事', converter)}</a><span aria-hidden="true"> / </span><a href="index.html">{localized(esc(EN), ZH, converter)}</a>{'<span aria-hidden="true"> / </span><span>Hamilton</span>' if article else ''}</nav>
{content}
</main>{footer(converter)}</body></html>'''


def outputs():
    c = TraditionalConverter()
    try:
        et, en, eb = load('en')
        zt, zn, zb = load('zh')
        tr = lambda en, zh, tag='span', classes='': localized(en, zh, c, tag, classes)
        card = f'''<a class="rf-book-card" href="hamilton.html"><p class="rf-kicker">{tr('Musical · Broadway 2015', '音乐剧 · 2015年百老汇公演')}</p>{tr(esc(et), esc(zt), 'h3')}<p class="rf-card-deck">{tr(ESSAY_EN, ESSAY_ZH)}</p><span>{tr('Read the essay →', '阅读文章 →')}</span></a>'''
        shelf = f'''<section class="rf-shelf-hero"><div><p class="rf-kicker">{tr('Stage &amp; people', '舞台与人')}</p>{tr(esc(EN), ZH, 'h1')}{tr(DECK_EN, DECK_ZH, 'p', 'rf-hero-deck')}</div><div class="rf-editor-note">{tr('A work is more than its plot. We attend to who speaks, who sings, and how a scene changes when another person tells it.', '不只介绍故事讲了什么，也留意谁在说话、谁在歌唱，同一个场面换一个人讲述，又会有什么不同。', 'p')}{tr('Begin with Hamilton. Each essay identifies its version and gives a spoiler notice.', '先从《汉密尔顿》开始。每篇注明所谈版本，并提示剧透范围。', 'p')}</div></section><section class="rf-year-section"><div class="rf-shelf-heading">{tr('First on this stage', '从这部作品开始', 'h2')}</div><div class="rf-book-grid" style="grid-template-columns:1fr">{card}</div></section>'''
        article = f'''<section class="rf-article-hero"><p class="rf-kicker">{tr('Ambition, waiting &amp; a shared life', '抱负、等待与共同生活')}</p>{tr(esc(et), esc(zt), 'h1')}{tr(ESSAY_EN, ESSAY_ZH, 'p', 'rf-article-deck')}<p class="rf-guide-meta">Han Qin (秦汉) · {tr('Published', '发布')} <time datetime="{DATE}">{DATE}</time></p><div class="rf-notice">{tr(esc(en), esc(zn), 'p')}</div></section>
<article class="rf-prose lang-en" lang="en">{prose(eb)}</article>
<article class="rf-prose lang-zh" lang="zh-Hans">{prose(zb)}</article>
<article class="rf-prose lang-hant" lang="zh-Hant">{prose(c.convert(zb))}</article>
<aside class="rf-sources">{tr('About this introduction', '关于本文', 'h2')}{tr('This introduction draws on the official synopsis, creator and performer interviews, historical sources, and signed criticism. It concerns the original Broadway production’s narrative and creative choices, not a firsthand review of a live performance or a complete recording.', '本文依据官方剧情介绍、主创与演员访谈、历史资料及署名评论，讨论原版百老汇作品的叙事与创作安排，并非现场观剧或完整观看影像后的演出评论。', 'p', 'rf-source-note')}</aside>
<nav class="rf-next" aria-label="More reading"><a href="index.html">{tr('All Theatre &amp; Musicals →', '返回戏剧与音乐剧 →')}</a></nav>'''
        return {ROOT / 'essays/theatre/index.html': wrap(shelf, EN + ' · ' + ZH, DECK_EN, 'index.html', c),
                ROOT / 'essays/theatre/hamilton.html': wrap(article, et + ' · ' + zt, ESSAY_EN, 'hamilton.html', c, True)}
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
    print('OK: theatre shelf and complete Hamilton essay in EN/Hans/Hant')


if __name__ == '__main__':
    main()
