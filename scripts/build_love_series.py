#!/usr/bin/env python3
"""Build eight reader essays on love, with three complete reading modes."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from build_ai_work_series import TraditionalConverter, shell_header, footer, tri
from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/love'
TARGET = ROOT / 'essays/love'
BASE = 'https://nondubito.net/essays/love/'
DATE = '2026-10-25'
TITLE = ('Why This Person?', '为什么偏偏是你')
SUBTITLE = ('A Philosophy of Love', 'SAE 爱情论')
DECK = (
    'A face, an absence, a mistake, a promise, a meeting neither person can arrange alone. Six perspectives on love—not stages to climb—with a guide and six enduring stories that test the account.',
    '初见时的一抬头，不在眼前时的想念，看错之后的一回头，许下的话，彼此碰上的那一刻。六种看爱情的角度，不是六级台阶；一篇导读，六篇正文，再让六个经典故事来追问。',
)
NOTE = (
    'Not a compatibility test or a guide to making someone love you. The essays do not grade people, make marriage or sexuality a prerequisite, or replace commitments, institutional requirements, and safety support.',
    '不是恋爱测评，也不是教人怎样换来爱情。不为人分级，不把婚姻、性别组合或性经验当作爱的门槛；这里的讨论也不取消已有的承诺、制度要求与必要的保护。',
)
KINDS = (
    ('A guide · first or last', '导读 · 可先读，也可回头读'),
    ('The first pull', '初见'),
    ('Remembering & expecting', '相思'),
    ('The one who loves', '是我在爱'),
    ('A direction that lasts', '换不掉'),
    ('Without asking it back', '不等你先爱我'),
    ('When two ways of loving meet', '彼此相遇'),
    ('Six stories ask back', '六个故事的追问'),
)
PAPER_NAMES = ('爱情论的位置', '一见', '相思', '是我', '换不掉', '不等你', '那一刻', '故事')


def esc(value: str) -> str:
    return html.escape(value, quote=True)


class LoveTraditionalConverter(TraditionalConverter):
    def convert(self, value: str) -> str:
        # The shared converter includes software vocabulary. Here 默認 means
        # tacit assent, not a default setting; 文件 is a document, not a file.
        protected = value.replace('默认', '__LOVE_ASSENT__').replace('文件', '__LOVE_DOCUMENT__')
        result = super().convert(protected)
        for old, new in (
            ('__LOVE_ASSENT__', '默認'), ('__LOVE_DOCUMENT__', '文件'),
            ('公裡', '公里'), ('千裡', '千里'), ('裡程', '里程'),
            ('沈默', '沉默'), ('沈積', '沉積'), ('很沈', '很沉'),
            ('回復', '回覆'), ('贊為', '讚為'), ('贊許', '讚許'),
            ('髮現', '發現'), ('乾活', '幹活'), ('多乾', '多幹'), ('復述', '複述'),
            ('那只手', '那隻手'),
            ('亞裡士多德', '亞里士多德'), ('捨勒', '舍勒'),
            ('裡克', '里克'), ('發色', '髮色'), ('反復追問', '反覆追問'),
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
        if item.get('id') != i or item.get('slug') != slug or item.get('source_url') != f'https://self-as-an-end.net/papers/sae-love-theory-{i}.html':
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
<link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="../../site-shell.css?v=20260905b"><link rel="stylesheet" href="love.css?v=20261025">
<script src="../../site-shell.js?v=20260905b"></script><script defer src="love.js?v=20261025"></script><script type="application/ld+json">{schema_text}</script></head>'''


@tracked_html
def shell(content: str, page_head: str, converter: TraditionalConverter) -> str:
    header = shell_header().replace('data-site-shell-menu aria-controls', 'data-site-shell-menu aria-label="Menu" aria-controls')
    for code, label in (('en', 'English'), ('zh', '简体中文'), ('zh-hant', '繁體中文')):
        header = header.replace(f'data-set-language="{code}"', f'data-set-language="{code}" aria-label="{label}"')
    foot = footer()
    for en, zh in (('Explore','探索'), ('Library','书架'), ('SAE Theory ↗','SAE 理论 ↗')):
        foot = foot.replace('>' + en + '</a>', '>' + loc(en, zh, converter) + '</a>')
    return '<!DOCTYPE html>\n<html lang="en" data-lang="en" data-editions="en zh zh-hant">' + page_head + '<body class="site-shell-page explicit-hant love-page">' + header + content + foot + '</body></html>\n'


def breadcrumb(converter: TraditionalConverter, article: bool = False) -> str:
    extra = f'<span aria-hidden="true">/</span><a href="index.html">{loc(*TITLE, converter)}</a>' if article else ''
    return f'<nav class="love-breadcrumbs" aria-label="Breadcrumb"><a href="../../explore.html#sae">{loc("SAE · Philosophy", "SAE · 哲学", converter)}</a>{extra}</nav>'


def related(converter: TraditionalConverter) -> str:
    links = ''.join(f'<a href="../{path}/index.html">{loc(en, zh, converter)}</a>' for path, en, zh in (
        ('relation','A Philosophy of Relations','关系论：在关系里，仍是自己'),
        ('everyday/relationships','Everyday essays · Relationships','日常散文 · 关系里的结构'),
        ('aesthetics','Beauty beyond liking','美学：喜欢之外')))
    return '<aside class="love-related">' + loc('Keep exploring', '继续逛逛', converter, 'h2') + links + '</aside>'


def render_index(items: list[dict], converter: TraditionalConverter) -> str:
    cards = []
    for item in items[1:7]:
        i = item['id']
        cards.append(f'<a class="love-card" href="{item["slug"]}.html"><p class="love-kicker">{i:02d} · {loc(*KINDS[i], converter)}</p>{loc(item["title_en"], item["title_zh"], converter, "h2")}{loc(item["deck_en"], item["deck_zh"], converter, "p")}{loc("Read essay →", "阅读全文 →", converter, "span", "love-read")}</a>')
    guide, stories = items[0], items[7]
    content = f'''<main class="love-wrap" data-search="爱情论 愛情論 为什么偏偏是你 為什麼偏偏是你 philosophy love romance longing promises stories">
{breadcrumb(converter)}<section class="love-hero"><p class="love-kicker">Non Dubito · {loc(*SUBTITLE, converter)}</p>{loc(*TITLE, converter, 'h1')}{loc(*DECK, converter, 'p', 'love-deck love-search-deck')}
{loc('Eight essays · English, Simplified & Traditional Chinese', '八篇 · 英文、简体中文与繁体中文', converter, 'p', 'love-meta')}</section>
<aside class="love-opening">{loc('You need not convince the world that this person is irreplaceable. You cannot decide their answer for them either.', '你不必说服全世界也非他不可，却也不能替他回答爱不爱你。', converter, 'p')}<a class="love-start" href="ep01.html">{loc('Start with the first essay →', '从第一篇开始 →', converter)}</a>{loc(*NOTE, converter, 'p', 'love-note')}</aside>
<a class="love-guide" href="overview.html"><p class="love-kicker">00 · {loc(*KINDS[0], converter)}</p>{loc(guide['title_en'], guide['title_zh'], converter, 'h2')}{loc(guide['deck_en'], guide['deck_zh'], converter, 'p')}{loc('Read the guide →', '阅读导读 →', converter, 'span', 'love-read')}</a>
<section class="love-grid" aria-label="Six perspectives, not stages">{''.join(cards)}</section>
<a class="love-guide love-stories" href="ep07.html"><p class="love-kicker">07 · {loc(*KINDS[7], converter)}</p>{loc(stories['title_en'], stories['title_zh'], converter, 'h2')}{loc(stories['deck_en'], stories['deck_zh'], converter, 'p')}{loc('Read the six stories →', '读六个故事怎样追问 →', converter, 'span', 'love-read')}</a>
<section class="love-map">{loc('Not a ladder, not a guarantee', '不是升级，也不是保证', converter, 'h2')}{loc('An encounter after years of friendship can be read through the first pull; a loving person can still try to turn a partner into a mirror. These are aspects of particular moments, not ranks for people or stages every couple must complete. For everyday situations, the Relationships shelf remains a separate way in; the wider Relation series develops the shared questions of promises, expectations and leaving.', '多年相识以后，也可能有初见般的一刻；真心爱着，也仍可能想把对方收成自己的镜子。这里读的是某一次运作的不同方面，不是给人分级，也不是每段爱情必须走完的路线。日常区《关系里的结构》仍从具体难事进入；关系论则展开承诺、期待、离开等共有的问题。', converter, 'p')}</section>
{related(converter)}<details class="love-sources"><summary>{loc('From the essays to the papers', '从散文回到论文', converter)}</summary>{loc('A guide from paper 0, six perspectives from papers 1–6, and a closing reading of six stories from paper 7. These are complete reader essays, not full technical translations. English is independently written. The marriage and sexual dimensions are not settled here; leaving them outside this inquiry does not deny their presence.', '一篇导读对应第零篇，六种角度对应一至六篇，最后以第七篇的六个故事收束。八篇均为完整散文，不是全部技术论证的逐段翻译，英文独立重写。婚姻及性那一面的分析另作讨论，不等于否认它们在爱情中的存在。', converter, 'p')}<a href="https://self-as-an-end.net/papers/sae-love-theory-0.html">{loc('Love Theory · source overview ↗', '爱情论 · 原论文总导读 ↗', converter)}</a></details></main>'''
    marriage = '<section class="love-map">' + loc('After the wedding, still two people', '结婚以后，仍然是两个人', converter, 'h2') + loc('A separate companion follows commitments, recognition, shared years, preparing for a child, and leaving. Marriage is not love’s compulsory next stage; these are further questions when lives are joined in that way.', '另一个专题接着读承诺、制度承认、共同的岁月、孕育与去留。婚姻不是爱情必须升级的下一站；当生活这样交在一起，还有一些值得慢慢说的问题。', converter, 'p') + '<a href="../marriage/index.html">' + loc('Marriage · Read the companion →', '婚姻论 · 进入专题 →', converter) + '</a></section>'
    content = content.replace(related(converter), marriage + related(converter), 1)
    return shell(content, head(TITLE[0] + ': ' + SUBTITLE[0] + ' · 爱情论', DECK[0], 'index.html'), converter)


def prose(paragraphs: list[str]) -> str:
    return '\n'.join(f'<h2>{esc(p[3:])}</h2>' if p.startswith('## ') else f'<p>{esc(p)}</p>' for p in paragraphs)


def render_article(item: dict, items: list[dict], converter: TraditionalConverter) -> str:
    i = item['id']
    bodies = []
    for language, native in (('en','en'), ('zh','zh-Hans'), ('hant','zh-Hant')):
        paragraphs = item['body_en' if language == 'en' else 'body_zh']
        if language == 'hant':
            paragraphs = [converter.convert(p) for p in paragraphs]
        bodies.append(f'<div class="essay-body love-prose lang-{language}" lang="{native}">{prose(paragraphs)}</div>')
    links = []
    for index, en, zh in ((i-1,'Previous essay','上一篇'), (i+1,'Next essay','下一篇')):
        if 0 <= index < len(items):
            other = items[index]
            links.append(f'<a href="{other["slug"]}.html">{loc(en, zh, converter, "small")}{loc(other["title_en"], other["title_zh"], converter)}</a>')
        else:
            links.append(f'<a href="index.html">{loc("All eight essays", "全部八篇", converter, "small")}{loc(*TITLE, converter)}</a>')
    content = f'''<main class="love-wrap">{breadcrumb(converter, True)}<article class="love-article" data-search="{esc('爱情论 愛情論 A Philosophy of Love ' + item['title_en'] + ' ' + item['title_zh'] + ' ' + converter.convert(item['title_zh']))}">
<div class="love-head"><p class="love-kicker">{loc(*SUBTITLE, converter)} · {i:02d} · {loc(*KINDS[i], converter)}</p>{loc(item['title_en'], item['title_zh'], converter, 'h1')}{loc(item['deck_en'], item['deck_zh'], converter, 'p', 'love-deck love-search-deck')}
<p class="love-meta">Han Qin ({loc('秦汉','秦汉',converter)}) · <time datetime="{DATE}">{DATE}</time></p></div>
{''.join(bodies)}<details class="love-sources"><summary>{loc('Source & reading note', '来源与阅读说明', converter)}</summary>{loc('Written from the corresponding SAE paper for a general reader, rather than translating its full technical argument. English is independently written. The perspectives are not developmental stages or tests of another person’s feelings. Commitments and institutional requirements are not erased by this account of love.', '本文根据对应 SAE 论文面向普通读者写成，不是全部技术论证的逐段翻译；英文独立重写。各篇角度不是爱情的发展阶段，也不拿来测验他人的内心。爱情这一面的讨论，不抹去承诺和制度那一面的事情。', converter, 'p')}<a href="{item['source_url']}">{loc('Paper ' + str(i) + ' · source paper ↗', PAPER_NAMES[i] + ' · 原论文 ↗', converter)}</a></details>
<nav class="love-series-nav" aria-label="Series navigation">{''.join(links)}</nav><p class="love-return"><a href="index.html">{loc('← All eight essays', '← 回到全部八篇', converter)}</a></p>{related(converter)}</article></main>'''
    return shell(content, head(item['title_en'] + ' · Why This Person?', item['deck_en'], item['slug'] + '.html', item), converter)


def render() -> dict[Path,str]:
    items = load_items()
    converter = LoveTraditionalConverter()
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
    print(f'{"Checked" if args.check else "Wrote"} {len(pages)} love pages · three complete reading modes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
