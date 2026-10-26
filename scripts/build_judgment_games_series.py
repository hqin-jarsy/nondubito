#!/usr/bin/env python3
"""Build four complete reader essays on play and the exercise of judgment."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from build_ai_work_series import TraditionalConverter, shell_header, footer, tri
from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/judgment-games'
TARGET = ROOT / 'essays/judgment-games'
BASE = 'https://nondubito.net/essays/judgment-games/'
DATE = '2026-10-25'
TITLE = ('Play Again', '再来一局')
SUBTITLE = ('Exercises in Judgment & Play', '判断力练习与游戏')
DECK = (
    'A familiar story, a move found alone, an opponent’s good idea, a partner’s unexpected step. Four essays on what remains open when the rules are already known.',
    '听熟的故事，独自看出的一步，对手的好棋，舞伴多带的半步。四篇散文，从规则已经知道、事情却还没有被做完的地方开始。',
)
NOTE = (
    'These are philosophical readings, not a cognitive test or a program promising improvement. The closing invitations are optional: no scores, correct answers, or character grades.',
    '这是哲学散文，不是认知能力测验，也不是保证进步的训练方案。文末的小观察可以不做，不评分，不设标准答案，也不据此评判人格。',
)
KINDS = (('Begin here', '总导读'), ('Playing alone', '独自玩'), ('Competition', '竞争'), ('Cooperation', '合作'))
PAPER_NAMES = (('Overview', '总论'), ('Playing Alone', '一个人的局'), ('Competition', '竞争之局'), ('Cooperation', '合作之局'))


def esc(text: str) -> str:
    return html.escape(text, quote=True)


class GameTraditionalConverter(TraditionalConverter):
    def convert(self, value: str) -> str:
        result = super().convert(value)
        return result.replace('公裡', '公里').replace('千裡', '千里').replace('裡程', '里程')


def loc(en: str, zh: str, converter: TraditionalConverter, tag: str = 'span', css: str = '') -> str:
    return tri(esc(en), esc(zh), esc(converter.convert(zh)), tag, css)


def load_items() -> list[dict]:
    items = []
    for i, slug in enumerate(('overview', 'ep01', 'ep02', 'ep03')):
        path = DATA / (slug + '.json')
        item = json.loads(path.read_text(encoding='utf-8'))
        expected = 'https://self-as-an-end.net/papers/sae-judgment-games-' + ('overview' if i == 0 else str(i)) + '.html'
        if item.get('id') != i or item.get('slug') != slug or item.get('source_url') != expected:
            raise ValueError(f'Incorrect identity/source: {path.name}')
        for language in ('zh', 'en'):
            for key in ('title', 'deck', 'pause'):
                if not isinstance(item.get(f'{key}_{language}'), str) or not item[f'{key}_{language}'].strip():
                    raise ValueError(f'Missing {language} {key}: {path.name}')
            paragraphs = item.get(f'body_{language}')
            if not isinstance(paragraphs, list) or len(paragraphs) < 15 or any(not isinstance(p, str) or not p.strip() or '<' in p or p.startswith('###') for p in paragraphs):
                raise ValueError(f'Incomplete prose: {path.name} {language}')
            if sum(p.startswith('## ') for p in paragraphs) > 3:
                raise ValueError(f'Too many divisions: {path.name} {language}')
            text = '\n'.join(paragraphs)
            size = len(re.findall(r'[\u3400-\u9fff]', text)) if language == 'zh' else len(text.split())
            if size < (1800 if language == 'zh' else 1000):
                raise ValueError(f'Text too brief: {path.name} {language} {size}')
            if re.search(r'\b\d{2}DD\b|[NZGD]\d{1,3}\b', text):
                raise ValueError(f'Unedited technical labels: {path.name}')
        items.append(item)
    return items


def head(title: str, deck: str, name: str, item: dict | None = None) -> str:
    url = BASE + ('' if name == 'index.html' else name)
    schema = {'@context':'https://schema.org', '@type':'Article' if item else 'CollectionPage', 'name':title, 'description':deck,
              'url':url, 'inLanguage':['en','zh-Hans','zh-Hant'], 'author':{'@type':'Person','name':'Han Qin (秦汉)'}, 'datePublished':DATE, 'dateModified':DATE}
    if item:
        schema.update(headline=item['title_en'], mainEntityOfPage=url, citation=item['source_url'],
                      isPartOf={'@type':'CollectionPage','name':TITLE[0] + ': ' + SUBTITLE[0],'url':BASE})
    schema_text = json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')
    return f'''<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(deck)}"><meta name="author" content="Han Qin (秦汉)">
<meta property="og:type" content="{'article' if item else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(deck)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary">
<link rel="canonical" href="{url}"><link rel="icon" type="image/svg+xml" href="../../favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;family=Noto+Serif+TC:wght@400;500;600&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="../../site-shell.css?v=20260905b"><link rel="stylesheet" href="judgment-games.css?v=20261025">
<script src="../../site-shell.js?v=20260905b"></script><script defer src="judgment-games.js?v=20261025"></script><script type="application/ld+json">{schema_text}</script></head>'''


@tracked_html
def shell(content: str, page_head: str, converter: TraditionalConverter) -> str:
    header = shell_header().replace('data-site-shell-menu aria-controls', 'data-site-shell-menu aria-label="Menu" aria-controls')
    foot = footer()
    for en, zh in (('Explore','探索'), ('Library','书架'), ('SAE Theory ↗','SAE 理论 ↗')):
        foot = foot.replace('>' + en + '</a>', '>' + loc(en, zh, converter) + '</a>')
    return '<!DOCTYPE html>\n<html lang="en" data-lang="en" data-editions="en zh zh-hant">' + page_head + '<body class="site-shell-page explicit-hant jg-page">' + header + content + foot + '</body></html>\n'


def breadcrumb(converter: TraditionalConverter, article: bool = False) -> str:
    extra = f'<span aria-hidden="true">/</span><a href="index.html">{loc(*TITLE, converter)}</a>' if article else ''
    return f'<nav class="jg-breadcrumbs" aria-label="Breadcrumb"><a href="../../explore.html#sae">{loc("SAE · Philosophy", "SAE · 哲学", converter)}</a>{extra}</nav>'


def related(converter: TraditionalConverter) -> str:
    links = ''.join(f'<a href="../{path}/index.html">{loc(en, zh, converter)}</a>' for path, en, zh in (
        ('aesthetics','Beauty beyond liking','喜欢之外，看见美'), ('laughter','Judgment and laughter','判断力与笑'), ('games','Readings of video games','电子游戏作品解读')))
    return '<aside class="jg-related">' + loc('Keep exploring', '继续逛逛', converter, 'h2') + links + '</aside>'


def render_index(items: list[dict], converter: TraditionalConverter) -> str:
    cards = []
    for item in items:
        i = item['id']
        cards.append(f'<a class="jg-card" href="{item["slug"]}.html"><p class="jg-kicker">{i:02d} · {loc(*KINDS[i], converter)}</p>{loc(item["title_en"], item["title_zh"], converter, "h2")}{loc(item["deck_en"], item["deck_zh"], converter, "p")}{loc("Read essay →", "阅读全文 →", converter, "span", "jg-read")}</a>')
    content = f'''<main class="jg-wrap" data-search="判断力练习与游戏 判斷力練習與遊戲 play games judgment judgement solo competition cooperation 独自 竞争 合作 再来一局">
{breadcrumb(converter)}<section class="jg-hero"><p class="jg-kicker">Non Dubito · {loc(*SUBTITLE, converter)}</p>{loc(*TITLE, converter, 'h1')}{loc(*DECK, converter, 'p', 'jg-deck jg-search-deck')}
{loc('Four essays · English, Simplified & Traditional Chinese', '四篇 · 英文、简体中文与繁体中文', converter, 'p', 'jg-meta')}</section>
<aside class="jg-opening">{loc('The rules are known. The next step is not.', '规则已经知道，下一步还没有被写完。', converter, 'p')}{loc(*NOTE, converter, 'p', 'jg-note')}</aside>
<section class="jg-grid" aria-label="Four readings">{''.join(cards)}</section>
<section class="jg-map">{loc('Not a ladder to climb', '不是一张升级表', converter, 'h2')}{loc('Alone, you meet rules and materials. In competition, another person wants the result you want. In cooperation, their next step is also part of what you are making together. These arrangements offer possibilities; they do not assign people a level or prove how well they regard one another.', '独自玩，面对规则与材料；竞争时，对面也有人想赢；合作时，他的下一步还是他的，又是一起要做的事的一部分。这些是不同的相遇方式，不是给人分级，也不保证玩过之后一定进步。', converter, 'p')}</section>
{related(converter)}<details class="jg-sources"><summary>{loc('From the source papers', '从散文回到论文', converter)}</summary>{loc('The four essays follow the four papers of SAE Exercises and Games of Judgment. They are complete reader essays, with independently written English and source links on every page. This series belongs to philosophy; the separate Games shelf reads particular video-game works.', '四篇对应《SAE 判断力练习与游戏》的总论与三篇论文，均为完整散文，英文独立重写，每篇附原论文入口。本系列在哲学区；具体电子游戏作品的解读仍在原来的游戏书架。', converter, 'p')}<a href="https://self-as-an-end.net/papers/sae-judgment-games-overview.html">{loc('Read the theoretical overview ↗', '阅读理论总论 ↗', converter)}</a></details></main>'''
    return shell(content, head(TITLE[0] + ': ' + SUBTITLE[0] + ' · 判断力练习与游戏', DECK[0], 'index.html'), converter)


def prose(paragraphs: list[str]) -> str:
    return '\n'.join(f'<h2>{esc(p[3:])}</h2>' if p.startswith('## ') else f'<p>{esc(p)}</p>' for p in paragraphs)


def render_article(item: dict, items: list[dict], converter: TraditionalConverter) -> str:
    i = item['id']
    bodies = []
    for language, native in (('en','en'), ('zh','zh-Hans'), ('hant','zh-Hant')):
        paragraphs = item['body_en' if language == 'en' else 'body_zh']
        if language == 'hant':
            paragraphs = [converter.convert(p) for p in paragraphs]
        bodies.append(f'<div class="essay-body jg-prose lang-{language}" lang="{native}">{prose(paragraphs)}</div>')
    links = []
    for index, en, zh in ((i-1,'Previous essay','上一篇'), (i+1,'Next essay','下一篇')):
        if 0 <= index < len(items):
            other = items[index]
            links.append(f'<a href="{other["slug"]}.html">{loc(en, zh, converter, "small")}{loc(other["title_en"], other["title_zh"], converter)}</a>')
        else:
            links.append(f'<a href="index.html">{loc("All four essays", "全部四篇", converter, "small")}{loc(*TITLE, converter)}</a>')
    content = f'''<main class="jg-wrap">{breadcrumb(converter, True)}<article class="jg-article" data-search="{esc('判断力练习与游戏 判斷力練習與遊戲 Exercises in Judgment Play ' + item['title_en'] + ' ' + item['title_zh'] + ' ' + converter.convert(item['title_zh']))}">
<div class="jg-head"><p class="jg-kicker">{loc(*SUBTITLE, converter)} · {loc(*KINDS[i], converter)}</p>{loc(item['title_en'], item['title_zh'], converter, 'h1')}{loc(item['deck_en'], item['deck_zh'], converter, 'p', 'jg-deck jg-search-deck')}
<p class="jg-meta">Han Qin ({loc('秦汉','秦汉',converter)}) · <time datetime="{DATE}">{DATE}</time></p></div>
{''.join(bodies)}<aside class="jg-pause">{loc('Something to notice, if you like', '愿意的话，下次留意一下', converter, 'h2')}{loc(item['pause_en'], item['pause_zh'], converter, 'p')}{loc(*NOTE, converter, 'p', 'jg-note')}</aside>
<details class="jg-sources"><summary>{loc('Source & reading note','来源与阅读说明',converter)}</summary>{loc('Written from the corresponding SAE paper, not a translation of its full technical argument. English is written independently for English-language readers. A possibility opened by play is not a promise of improvement, a personality test, or an obligation to play.', '本文根据对应论文写成，不是全部技术论证的逐段翻译；英文面向英文读者独立重写。游戏打开的可能，不等于进步保证、人格测试或必须参加的功课。', converter, 'p')}<a href="{item['source_url']}">{loc(PAPER_NAMES[i][0] + ' · source paper ↗', PAPER_NAMES[i][1] + ' · 原论文 ↗', converter)}</a></details>
<nav class="jg-series-nav" aria-label="Series navigation">{''.join(links)}</nav><p class="jg-return"><a href="index.html">{loc('← All four essays', '← 回到全部四篇', converter)}</a></p>{related(converter)}</article></main>'''
    return shell(content, head(item['title_en'] + ' · Play Again', item['deck_en'], item['slug'] + '.html', item), converter)


def render() -> dict[Path,str]:
    items = load_items()
    converter = GameTraditionalConverter()
    try:
        return {TARGET/'index.html':render_index(items, converter), **{TARGET/(item['slug']+'.html'):render_article(item,items,converter) for item in items}}
    finally:
        converter.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    pages = render()
    for path, text in pages.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding='utf-8') != text:
                raise ValueError(f'Stale page: {path.relative_to(ROOT)}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
    print(f'{"Checked" if args.check else "Wrote"} {len(pages)} judgment-and-play pages · three complete reading modes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
