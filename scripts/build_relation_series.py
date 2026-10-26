#!/usr/bin/env python3
"""Build eight reader essays on relations, with three complete reading modes."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from build_ai_work_series import TraditionalConverter, shell_header, footer, tri
from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/relation'
TARGET = ROOT / 'essays/relation'
BASE = 'https://nondubito.net/essays/relation/'
DATE = '2026-10-25'
TITLE = ('What Passes Between Us', '在关系里，仍是自己')
SUBTITLE = ('A Philosophy of Relations', 'SAE 关系论')
DECK = (
    'A promise, an awaited letter, a lesson that stays with us, a departure. Seven essays follow what passes between people and settles over time, with a guide you can read first or last.',
    '一句答应，一封等着的信，一种多年后还在的习惯，一次离开。七篇正文，加一篇可先读也可回头读的导读，看人与人之间留下了什么，又怎样改变下一次相遇。',
)
NOTE = (
    'Philosophical essays, not a relationship test or a prescription to stay or leave. They do not replace legal requirements, safety support, or the other person’s own account.',
    '这是哲学散文，不是关系测评，也不替读者决定该留还是该走。私人来往的讨论，不替代法律要求、安全支持，或当事人自己的讲述。',
)
KINDS = (
    ('A guide · first or last', '导读 · 可先读，也可回头读'),
    ('Where a relation begins', '关系从哪里开始'),
    ('Ourselves through time', '时间里的自己'),
    ('Promises', '承诺'),
    ('Replies & expectations', '回应与期待'),
    ('What accumulates', '来往的沉积'),
    ('Repair & departure', '修复与离开'),
    ('Why relations still matter', '为什么仍要关系'),
)
PAPER_NAMES = ('关系论的位置', '关系是什么，不是什么', '昨天、今天、明天', '承诺', '来往与期待', '来往的沉积', '不对称、分歧与结束', '为什么仍要关系')


def esc(value: str) -> str:
    return html.escape(value, quote=True)


class RelationTraditionalConverter(TraditionalConverter):
    def convert(self, value: str) -> str:
        # The shared converter includes software vocabulary. Here 默認 means
        # tacit assent, not a default setting; 文件 is a document, not a file.
        protected = value.replace('默认', '__REL_ASSENT__').replace('文件', '__REL_DOCUMENT__')
        result = super().convert(protected)
        for old, new in (
            ('__REL_ASSENT__', '默認'), ('__REL_DOCUMENT__', '文件'),
            ('公裡', '公里'), ('千裡', '千里'), ('裡程', '里程'),
            ('沈默', '沉默'), ('沈積', '沉積'), ('很沈', '很沉'),
            ('回復', '回覆'), ('贊為', '讚為'), ('贊許', '讚許'),
            ('髮現', '發現'), ('乾活', '幹活'), ('多乾', '多幹'), ('復述', '複述'),
            ('那只手', '那隻手'),
        ):
            result = result.replace(old, new)
        return result


def loc(en: str, zh: str, converter: TraditionalConverter, tag: str = 'span', css: str = '') -> str:
    return tri(esc(en), esc(zh), esc(converter.convert(zh)), tag, css)


def load_items() -> list[dict]:
    items = []
    for i in range(8):
        slug = 'overview' if i == 0 else f'ep{i:02d}'
        path = DATA / (slug + '.json')
        item = json.loads(path.read_text(encoding='utf-8'))
        if item.get('id') != i or item.get('slug') != slug or item.get('source_url') != f'https://self-as-an-end.net/papers/sae-relation-theory-{i}.html':
            raise ValueError(f'Incorrect identity/source: {path.name}')
        for language in ('zh', 'en'):
            for key in ('title', 'deck'):
                if not isinstance(item.get(f'{key}_{language}'), str) or not item[f'{key}_{language}'].strip():
                    raise ValueError(f'Missing {language} {key}: {path.name}')
            paragraphs = item.get(f'body_{language}')
            if not isinstance(paragraphs, list) or len(paragraphs) < 15 or any(not isinstance(p, str) or not p.strip() or '<' in p or p.startswith('###') for p in paragraphs):
                raise ValueError(f'Incomplete prose: {path.name} {language}')
            if sum(p.startswith('## ') for p in paragraphs) > 3:
                raise ValueError(f'Too many divisions: {path.name} {language}')
            text = '\n'.join(paragraphs)
            size = len(re.findall(r'[\u3400-\u9fff]', text)) if language == 'zh' else len(text.split())
            if size < (2000 if language == 'zh' else 1100):
                raise ValueError(f'Text too brief: {path.name} {language} {size}')
            if re.search(r'\b\d{2}DD\b|\bH\d{1,3}\b', text):
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
<link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="../../site-shell.css?v=20260905b"><link rel="stylesheet" href="relation.css?v=20261025">
<script src="../../site-shell.js?v=20260905b"></script><script defer src="relation.js?v=20261025"></script><script type="application/ld+json">{schema_text}</script></head>'''


@tracked_html
def shell(content: str, page_head: str, converter: TraditionalConverter) -> str:
    header = shell_header().replace('data-site-shell-menu aria-controls', 'data-site-shell-menu aria-label="Menu" aria-controls')
    for code, label in (('en', 'English'), ('zh', '简体中文'), ('zh-hant', '繁體中文')):
        header = header.replace(f'data-set-language="{code}"', f'data-set-language="{code}" aria-label="{label}"')
    foot = footer()
    for en, zh in (('Explore','探索'), ('Library','书架'), ('SAE Theory ↗','SAE 理论 ↗')):
        foot = foot.replace('>' + en + '</a>', '>' + loc(en, zh, converter) + '</a>')
    return '<!DOCTYPE html>\n<html lang="en" data-lang="en" data-editions="en zh zh-hant">' + page_head + '<body class="site-shell-page explicit-hant relation-page">' + header + content + foot + '</body></html>\n'


def breadcrumb(converter: TraditionalConverter, article: bool = False) -> str:
    extra = f'<span aria-hidden="true">/</span><a href="index.html">{loc(*TITLE, converter)}</a>' if article else ''
    return f'<nav class="rel-breadcrumbs" aria-label="Breadcrumb"><a href="../../explore.html#sae">{loc("SAE · Philosophy", "SAE · 哲学", converter)}</a>{extra}</nav>'


def related(converter: TraditionalConverter) -> str:
    links = ''.join(f'<a href="../{path}/index.html">{loc(en, zh, converter)}</a>' for path, en, zh in (
        ('everyday/relationships','Everyday essays · Relationships','日常散文 · 关系里的结构'),
        ('conflict','On conflict','冲突论'), ('meaning','On meaning','意义论'), ('action','On action','行动论')))
    return '<aside class="rel-related">' + loc('Keep exploring', '继续逛逛', converter, 'h2') + links + '</aside>'


def render_index(items: list[dict], converter: TraditionalConverter) -> str:
    cards = []
    for item in items[1:]:
        i = item['id']
        cards.append(f'<a class="rel-card" href="{item["slug"]}.html"><p class="rel-kicker">{i:02d} · {loc(*KINDS[i], converter)}</p>{loc(item["title_en"], item["title_zh"], converter, "h2")}{loc(item["deck_en"], item["deck_zh"], converter, "p")}{loc("Read essay →", "阅读全文 →", converter, "span", "rel-read")}</a>')
    guide = items[0]
    content = f'''<main class="rel-wrap" data-search="关系论 關係論 在关系里仍是自己 在關係裡仍是自己 relations relationships philosophy promises expectations repair departure time">
{breadcrumb(converter)}<section class="rel-hero"><p class="rel-kicker">Non Dubito · {loc(*SUBTITLE, converter)}</p>{loc(*TITLE, converter, 'h1')}{loc(*DECK, converter, 'p', 'rel-deck rel-search-deck')}
{loc('Eight essays · English, Simplified & Traditional Chinese', '八篇 · 英文、简体中文与繁体中文', converter, 'p', 'rel-meta')}</section>
<aside class="rel-opening">{loc('What happened between us is real. It does not decide everything that follows.', '一起经历过的是真的，接下来谁怎样活，仍不能被它全部决定。', converter, 'p')}<a class="rel-start" href="ep01.html">{loc('Start with the first essay →', '从第一篇开始 →', converter)}</a>{loc(*NOTE, converter, 'p', 'rel-note')}</aside>
<a class="rel-guide" href="overview.html"><p class="rel-kicker">00 · {loc(*KINDS[0], converter)}</p>{loc(guide['title_en'], guide['title_zh'], converter, 'h2')}{loc(guide['deck_en'], guide['deck_zh'], converter, 'p')}{loc('Read the guide →', '阅读导读 →', converter, 'span', 'rel-read')}</a>
<section class="rel-grid" aria-label="Seven main essays">{''.join(cards)}</section>
<section class="rel-map">{loc('Two ways in', '两种入口，各有用处', converter, 'h2')}{loc('For a particular everyday difficulty, try Relationships in the Everyday shelf. Here the questions run deeper across cases: what a promise changes, how expectations accumulate, why repair is not the same as agreement, and what remains after someone leaves. Neither series gives people a score or decides another person’s inner life for them.', '若想先读生活里某一件难事，可以去日常区的《关系里的结构》。这一组则跨过具体处境，追问一句承诺改变了什么、期待怎样积累、和好为什么不等于分歧消失，以及离开后什么还在。两组都不拿来给人打分，也不替当事人判定他内心真正想要什么。', converter, 'p')}</section>
{related(converter)}<details class="rel-sources"><summary>{loc('From the essays to the papers', '从散文回到论文', converter)}</summary>{loc('The seven main essays follow papers 1–7. The guide draws on paper 0, which locates the theory and compares it with other philosophical traditions. These are complete reader essays, not paragraph-by-paragraph translations of all technical arguments; English is independently written. Every essay links to its source.', '七篇正文对应论文一至七；导读根据第零篇，说明这套关系论怎样提出问题，并选取它与哲学传统的几处对话。八篇均为完整散文，不是全部技术论证的逐段翻译，英文独立重写，每篇附原论文。', converter, 'p')}<a href="https://self-as-an-end.net/papers/sae-relation-theory-0.html">{loc('The Place of Relation Theory · source paper ↗', '关系论的位置 · 原论文 ↗', converter)}</a></details></main>'''
    return shell(content, head(TITLE[0] + ': ' + SUBTITLE[0] + ' · 关系论', DECK[0], 'index.html'), converter)


def prose(paragraphs: list[str]) -> str:
    return '\n'.join(f'<h2>{esc(p[3:])}</h2>' if p.startswith('## ') else f'<p>{esc(p)}</p>' for p in paragraphs)


def render_article(item: dict, items: list[dict], converter: TraditionalConverter) -> str:
    i = item['id']
    bodies = []
    for language, native in (('en','en'), ('zh','zh-Hans'), ('hant','zh-Hant')):
        paragraphs = item['body_en' if language == 'en' else 'body_zh']
        if language == 'hant':
            paragraphs = [converter.convert(p) for p in paragraphs]
        bodies.append(f'<div class="essay-body rel-prose lang-{language}" lang="{native}">{prose(paragraphs)}</div>')
    links = []
    for index, en, zh in ((i-1,'Previous essay','上一篇'), (i+1,'Next essay','下一篇')):
        if 0 <= index < len(items):
            other = items[index]
            links.append(f'<a href="{other["slug"]}.html">{loc(en, zh, converter, "small")}{loc(other["title_en"], other["title_zh"], converter)}</a>')
        else:
            links.append(f'<a href="index.html">{loc("All eight essays", "全部八篇", converter, "small")}{loc(*TITLE, converter)}</a>')
    content = f'''<main class="rel-wrap">{breadcrumb(converter, True)}<article class="rel-article" data-search="{esc('关系论 關係論 A Philosophy of Relations ' + item['title_en'] + ' ' + item['title_zh'] + ' ' + converter.convert(item['title_zh']))}">
<div class="rel-head"><p class="rel-kicker">{loc(*SUBTITLE, converter)} · {i:02d} · {loc(*KINDS[i], converter)}</p>{loc(item['title_en'], item['title_zh'], converter, 'h1')}{loc(item['deck_en'], item['deck_zh'], converter, 'p', 'rel-deck rel-search-deck')}
<p class="rel-meta">Han Qin ({loc('秦汉','秦汉',converter)}) · <time datetime="{DATE}">{DATE}</time></p></div>
{''.join(bodies)}<details class="rel-sources"><summary>{loc('Source & reading note', '来源与阅读说明', converter)}</summary>{loc('Written from the corresponding SAE paper for a general reader, rather than translating its full technical argument. English is independently written. The series describes relations without replacing institutional rules or deciding whether someone should stay, leave, or resume contact.', '本文根据对应 SAE 论文面向普通读者写成，不是全部技术论证的逐段翻译；英文独立重写。本系列不替代已经成立的制度规则，也不替读者决定应当留下、离开或恢复联系。', converter, 'p')}<a href="{item['source_url']}">{loc('Paper ' + str(i) + ' · source paper ↗', PAPER_NAMES[i] + ' · 原论文 ↗', converter)}</a></details>
<nav class="rel-series-nav" aria-label="Series navigation">{''.join(links)}</nav><p class="rel-return"><a href="index.html">{loc('← All eight essays', '← 回到全部八篇', converter)}</a></p>{related(converter)}</article></main>'''
    return shell(content, head(item['title_en'] + ' · What Passes Between Us', item['deck_en'], item['slug'] + '.html', item), converter)


def render() -> dict[Path,str]:
    items = load_items()
    converter = RelationTraditionalConverter()
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
    print(f'{"Checked" if args.check else "Wrote"} {len(pages)} relation pages · three complete reading modes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
