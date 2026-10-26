#!/usr/bin/env python3
"""Render eight public-facing State essays from reviewed Chinese/English JSON.

The checked-in text is the publication source; the paper receipts document the
published versions read, not a build-time dependency on another checkout.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from build_ai_work_series import TraditionalConverter, shell_header, footer, tri
from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/state'
TARGET = ROOT / 'essays/state'
BASE = 'https://nondubito.net/essays/state/'
DATE = '2026-10-25'
TITLE = ('The State Still Has to Answer', '到了国家这一层，还能问吗？')
DECK = (
    'A vote, a judgment, a passport, a river crossing. Eight essays ask what happens when there is no higher authority to appeal to—and why that cannot mean the questions must stop.',
    '一张票，一份判决，一本护照，一次越河。八篇散文问：上面已经没有更高一级时，为什么追问仍不能到此为止。',
)
NOTICE = (
    'The countries, places and events in this series are fictional cases from the source papers. The essays develop a philosophical argument, not an account of current law or a judgment on a particular country. No prior reading is required.',
    '文中的国家、地名与事件均为原论文设置的虚构案例。这里讨论的是哲学上的要求，不是对现行法律的说明，也不替读者评判某个现实国家；无须先读论文。',
)
SOURCE_LABELS = (
    ('What a State Is Not', '国家不是什么'),
    ('The Last Rule', '最后的规则'),
    ('The Last Instance', '最后的审'),
    ('The Last Exit', '最后的退出'),
    ('The Last Force', '最后的强力'),
    ('One Another, with No Superior', '没有上级的彼此'),
    ('The Last Resort', '最后的手段'),
    ('Questioning the Last Layer', '最后一层的追问'),
)
GROUPS = (
    ('voice', 'Who is speaking?', '谁在说“我们”', (0,)),
    ('inside', 'Rules, judgments and leaving', '规则、终审与离开', (1, 2, 3)),
    ('force', 'Force, neighbours and war', '强力、邻国与战争', (4, 5, 6)),
    ('after', 'What remains afterwards', '事情过去以后', (7,)),
)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


class StateTraditionalConverter(TraditionalConverter):
    def convert(self, value: str) -> str:
        text = super().convert(value)
        for wrong, right in (('公裡', '公里'), ('千裡', '千里'), ('英裡', '英里'), ('裡程', '里程')):
            text = text.replace(wrong, right)
        return text


def loc(en: str, zh: str, converter: TraditionalConverter, tag: str = 'span', css: str = '') -> str:
    return tri(esc(en), esc(zh), esc(converter.convert(zh)), tag, css)


def load_items() -> list[dict]:
    names = ['prequel'] + [f'ep{i:02d}' for i in range(1, 8)]
    items = []
    for number, slug in enumerate(names):
        path = DATA / f'{slug}.json'
        item = json.loads(path.read_text(encoding='utf-8'))
        if item.get('id') != number or item.get('slug') != slug:
            raise ValueError(f'Incorrect order/slug: {path.name}')
        expected = f'https://self-as-an-end.net/papers/sae-state-{number if number else "prequel"}.html'
        if item.get('source_url') != expected:
            raise ValueError(f'Incorrect source: {path.name}')
        for language in ('en', 'zh'):
            for key in ('title', 'deck'):
                if not isinstance(item.get(f'{key}_{language}'), str) or not item[f'{key}_{language}'].strip():
                    raise ValueError(f'Missing {language} {key}: {path.name}')
            body = item.get(f'body_{language}')
            if not isinstance(body, list) or len(body) < 15:
                raise ValueError(f'Incomplete {language} text: {path.name}')
            if any(not isinstance(p, str) or not p.strip() or '<' in p or p.startswith('###') for p in body):
                raise ValueError(f'Unexpected prose markup: {path.name}')
            text = '\n'.join(body)
            size = len(re.findall(r'[\u3400-\u9fff]', text)) if language == 'zh' else len(text.split())
            if size < (2000 if language == 'zh' else 1000):
                raise ValueError(f'Text too brief: {path.name}, {language}: {size}')
        items.append(item)
    return items


def head(title: str, deck: str, name: str, item: dict | None = None) -> str:
    url = BASE + ('' if name == 'index.html' else name)
    schema = {
        '@context': 'https://schema.org', '@type': 'Article' if item else 'CollectionPage',
        'name': title, 'description': deck, 'url': url, 'inLanguage': ['en', 'zh-Hans', 'zh-Hant'],
        'author': {'@type': 'Person', 'name': 'Han Qin (秦汉)'},
        'datePublished': DATE, 'dateModified': DATE,
    }
    if item:
        schema.update(headline=item['title_en'], mainEntityOfPage=url,
                      isPartOf={'@type': 'CollectionPage', 'name': TITLE[0], 'url': BASE},
                      citation=item['source_url'])
    schema_json = json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')
    return f'''<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(deck)}"><meta name="author" content="Han Qin (秦汉)">
<meta property="og:type" content="{'article' if item else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(deck)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary">
<link rel="canonical" href="{url}"><link rel="icon" type="image/svg+xml" href="../../favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;family=Noto+Serif+TC:wght@400;500;600&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="../../site-shell.css?v=20260905b"><link rel="stylesheet" href="state.css?v=20261025">
<script src="../../site-shell.js?v=20260905b"></script><script defer src="state.js?v=20261025"></script>
<script type="application/ld+json">{schema_json}</script></head>'''


@tracked_html
def shell(content: str, page_head: str, converter: TraditionalConverter) -> str:
    header = shell_header().replace('data-site-shell-menu aria-controls', 'data-site-shell-menu aria-label="Menu" aria-controls')
    foot = footer()
    for en, zh in (('Explore', '探索'), ('Library', '书架'), ('SAE Theory ↗', 'SAE 理论 ↗')):
        foot = foot.replace('>' + en + '</a>', '>' + loc(en, zh, converter) + '</a>')
    return '<!DOCTYPE html>\n<html lang="en" data-lang="en" data-editions="en zh zh-hant">\n' + page_head + '\n<body class="site-shell-page explicit-hant state-page">' + header + content + foot + '</body></html>\n'


def breadcrumb(converter: TraditionalConverter, article: bool = False) -> str:
    extra = f'<span aria-hidden="true">/</span><a href="index.html">{loc("Theory of the State", "国家论", converter)}</a>' if article else ''
    return f'<nav class="state-breadcrumbs" aria-label="Breadcrumb"><a href="../../explore.html#sae">{loc("SAE · Philosophy", "SAE · 哲学", converter)}</a>{extra}</nav>'


def related(converter: TraditionalConverter) -> str:
    links = ''.join(f'<a href="../{path}/index.html">{loc(en, zh, converter)}</a>' for path, en, zh in (
        ('institution', 'What institutions are for', '制度为了什么'),
        ('government', 'To whom a government answers', '政府向谁作答'),
        ('war', 'War and its limits', '战争及其限度'),
    ))
    return '<aside class="state-related">' + loc('Alongside this series', '与本系列一起读', converter, 'h2') + links + '</aside>'


def render_index(items: list[dict], converter: TraditionalConverter) -> str:
    groups = []
    for key, en, zh, ids in GROUPS:
        cards = []
        for i in ids:
            item = items[i]
            number = '00' if i == 0 else f'{i:02d}'
            cards.append(f'''<a class="state-card" href="{item['slug']}.html"><span class="state-number">{number}</span><div>{loc(item['title_en'], item['title_zh'], converter, 'h3')}{loc(item['deck_en'], item['deck_zh'], converter, 'p')}{loc('Read essay →', '阅读全文 →', converter, 'span', 'state-read')}</div></a>''')
        groups.append(f'<section class="state-group" id="{key}">{loc(en, zh, converter, "h2")}<div class="state-grid">{"".join(cards)}</div></section>')
    navigation = ''.join(f'<a href="#{key}">{loc(en, zh, converter)}</a>' for key, en, zh, ids in GROUPS)
    content = f'''<main class="state-wrap" data-search="SAE 国家论 國家論 Theory of the State 宪法 终审 国籍 退出 战争 constitutional review citizenship sovereignty accountability">
{breadcrumb(converter)}<section class="state-hero"><p class="state-kicker">Non Dubito · {loc('SAE Theory of the State', 'SAE 国家论', converter)}</p>
{loc(*TITLE, converter, 'h1')}{loc(*DECK, converter, 'p', 'state-deck state-search-deck')}
{loc('Eight essays · English, Simplified & Traditional Chinese', '八篇 · 英文、简体中文与繁体中文', converter, 'p', 'state-meta')}
{loc(*NOTICE, converter, 'p', 'state-notice')}</section>
<div class="state-orientation">{loc('Government asks how public decisions answer to the people they affect. This series goes to the places with no higher domestic level: the constitution, final judgment, citizenship, armed force and relations between states. You can start here without reading the earlier series.', '政府论问具体的公共判断向谁作答；国家论走到上面没有更高一级的地方：宪法、终审、国籍、军队，以及国与国之间。可以直接从这里开始，不必先补完前一系列。', converter, 'p')}</div>
<nav class="state-topics" aria-label="Reading route">{navigation}</nav>{''.join(groups)}
<details class="state-context"><summary>{loc('The three fictional neighbours', '先认识这三个虚构的邻国', converter)}</summary>{loc('The United City-States of Ends (UCSE) is the main setting: Apple City, familiar from the government essays, is one of its cities. To the north is the Nation Union of Telos (NUT); to the west, the Democratic Republic of Purposes (DRP). None is a stand-in for a particular country. None gets a moral verdict from its name: each action has to be examined on its own.', '故事主要发生在目的联合城邦（UCSE），政府论里的苹果城就在其中。北邻是目的民族联盟（NUT），西邻是目的民主共和国（DRP）。它们不影射某个现实国家，也不因名字里都有“目的”就自动合格；要看的始终是一件一件做下来的事。', converter, 'p')}</details>
{related(converter)}<aside class="state-sources">{loc('For the full argument', '想深入时，再读论文', converter, 'h2')}{loc('Each essay links to its source paper. The papers set out the definitions, qualifications and engagements with political philosophy; these readings follow the people caught in the decisions.', '每篇文末都通向对应论文。概念界定、完整限定与政治哲学对话留在论文里；这里先跟着被决定影响的人，把问题看清楚。', converter, 'p')}<a href="https://self-as-an-end.net/papers/sae-state-prequel.html">{loc('Begin with the theoretical prequel ↗', '从国家论前置篇进入 ↗', converter)}</a></aside></main>'''
    return shell(content, head(TITLE[0] + ' · SAE 国家论', DECK[0], 'index.html'), converter)


def prose(body: list[str]) -> str:
    return '\n'.join(f'<h2>{esc(p[3:])}</h2>' if p.startswith('## ') else f'<p>{esc(p)}</p>' for p in body)


def render_article(item: dict, items: list[dict], converter: TraditionalConverter) -> str:
    bodies = []
    for language, native in (('en', 'en'), ('zh', 'zh-Hans'), ('hant', 'zh-Hant')):
        paragraphs = item['body_en' if language == 'en' else 'body_zh']
        if language == 'hant':
            paragraphs = [converter.convert(p) for p in paragraphs]
        bodies.append(f'<div class="essay-body state-prose lang-{language}" lang="{native}">{prose(paragraphs)}</div>')
    navigation = []
    i = item['id']
    for target, en, zh in ((i - 1, 'Previous essay', '上一篇'), (i + 1, 'Next essay', '下一篇')):
        if 0 <= target < len(items):
            other = items[target]
            navigation.append(f'<a href="{other["slug"]}.html">{loc(en, zh, converter, "small")}{loc(other["title_en"], other["title_zh"], converter)}</a>')
        else:
            navigation.append(f'<a href="index.html">{loc("All eight essays", "全部八篇", converter, "small")}{loc(*TITLE, converter)}</a>')
    source_label = SOURCE_LABELS[i]
    position = loc('Prequel', '前置篇', converter) if i == 0 else f'{i:02d} / 07'
    content = f'''<main class="state-wrap">{breadcrumb(converter, True)}<article class="state-article" data-search="{esc('SAE 国家论 國家論 Theory of the State ' + item['title_en'] + ' ' + item['title_zh'] + ' ' + converter.convert(item['title_zh']))}">
<div class="state-head"><p class="state-kicker">{loc('SAE Theory of the State', 'SAE 国家论', converter)} · {position}</p>
{loc(item['title_en'], item['title_zh'], converter, 'h1')}{loc(item['deck_en'], item['deck_zh'], converter, 'p', 'state-deck state-search-deck')}
<p class="state-meta">Han Qin ({loc('秦汉', '秦汉', converter)}) · <time datetime="{DATE}">{DATE}</time></p>{loc(*NOTICE, converter, 'p', 'state-notice')}</div>
{''.join(bodies)}<details class="state-sources"><summary>{loc('Source & reading note', '来源与阅读说明', converter)}</summary>{loc('Written from the corresponding SAE Theory of the State paper, with an independently written English edition. The fictional cases and distinctions come from that paper; the essays do not reproduce its full technical apparatus or claim to resolve every case. The three reading modes contain the complete essay.', '本文依据对应的《SAE 国家论》论文写成，英文面向英文读者独立重写。虚构案例与关键区分来自论文，散文不复述全部技术论证，也不声称已经判清每个个案。简中、繁中与英文均为完整正文。', converter, 'p')}<a href="{item['source_url']}">{loc(source_label[0] + ' · source paper ↗', source_label[1] + ' · 原论文 ↗', converter)}</a></details>
<nav class="state-series-nav" aria-label="Series navigation">{''.join(navigation)}</nav><p class="state-return"><a href="index.html">{loc('← All eight essays', '← 回到全部八篇', converter)}</a></p>{related(converter)}</article></main>'''
    return shell(content, head(item['title_en'] + ' · Theory of the State', item['deck_en'], item['slug'] + '.html', item), converter)


def render() -> dict[Path, str]:
    items = load_items()
    converter = StateTraditionalConverter()
    try:
        return {TARGET / 'index.html': render_index(items, converter), **{TARGET / (item['slug'] + '.html'): render_article(item, items, converter) for item in items}}
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
                raise ValueError(f'Stale state page: {path.relative_to(ROOT)}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
    print(f'{"Checked" if args.check else "Wrote"} {len(pages)} state pages · three complete reading modes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
