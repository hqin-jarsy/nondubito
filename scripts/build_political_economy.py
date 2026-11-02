#!/usr/bin/env python3
"""Build an open real-case shelf, not a parallel retelling of fictional papers."""
from __future__ import annotations

import argparse
import html
import json
import re

from build_language_writing import ROOT, loc, page
from build_cooperation_histories import CooperationTraditionalConverter
from build_state_transitions import prose

DATE = '2026-11-01'
DATA = ROOT / 'data/political-economy'
TARGET = ROOT / 'essays/political-economy'
BASE = 'https://nondubito.net/essays/political-economy/'
TITLE = ('Money, Power, and Room to Move', '钱、权力与我们的路')
DECK = (
    'Training, a marketplace, and the choices around them. Real cases ask what money makes possible, who acquires control, and how a decision can be questioned.',
    '从一项培训、一家平台读起：钱使什么成为可能，谁因此取得了决定权，受到决定影响的人又怎样继续追问。',
)
SLUGS = ('introduction', 'petsmart-training', 'amazon-marketplace')


class PoliticalTraditionalConverter(CooperationTraditionalConverter):
    def convert(self, text):
        return (super().convert(text).replace('籤', '簽').replace('標簽', '標籤').replace('復製', '複製')
                .replace('髮款', '發款').replace('周轉', '週轉').replace('四周', '四週')
                .replace('被系在', '被繫在'))


def load_items():
    items = []
    for i, slug in enumerate(SLUGS, 1):
        d = json.loads((DATA / (slug + '.json')).read_text())
        assert d['id'] == i and d['slug'] == slug and d['date'] == DATE
        assert d['kind'] == ('introduction' if i == 1 else 'case')
        assert [s['id'] for s in d['sources']] == list(range(1, len(d['sources']) + 1))
        for s in d['sources']:
            assert s['url'].startswith('https://')
            assert all(s[k].strip() for k in ('title_en', 'title_zh', 'note_en', 'note_zh'))
        for lang in ('en', 'zh'):
            body = d['body_' + lang]
            assert len(body) >= (16 if i == 1 else 25)
            assert sum(p.startswith('## ') for p in body) == (2 if i == 1 else 3)
            assert all(p.strip() and '<' not in p for p in body)
            text = '\n'.join(body)
            count = len(re.findall(r'[\u3400-\u9fff]', text)) if lang == 'zh' else len(text.split())
            assert count >= ((1400 if lang == 'zh' else 800) if i == 1 else (2300 if lang == 'zh' else 1450)), (slug, lang, count)
            assert set(map(int, re.findall(r'\[(\d+)\]', text))) == {s['id'] for s in d['sources']}
            assert not re.search(r'\b\d{2}DD\b|\b[EFGZ]\d+\b||turn\d+(?:view|search)', text)
        items.append(d)
    return items


def library_card(conv):
    def ll(en, zh, tag='span', css=''):
        return loc(en, zh, conv, tag, css).replace('lang-zh', 'lang-zh cl-zh').replace('lang-hant', 'lang-zh cl-hant')
    return ('<a href="essays/political-economy/index.html" class="series-card"><span class="series-card-count">'
            + ll('Political economy · Introduction + 2 cases · EN / 简 / 繁', '政治经济学 · 导读＋两篇真实案例 · 英简繁')
            + '</span><div class="series-card-title-zh cl-zh">钱、权力与我们的路</div><div class="series-card-title-zh cl-hant">錢、權力與我們的路</div><div class="series-card-title-en">Money, Power, and Room to Move</div>'
            + ll(DECK[0], DECK[1], 'p', 'series-card-desc')
            + ll('Read the cases →', '进入真实案例专题 →', 'span', 'series-card-arrow') + '</a>')


def breadcrumb(conv, article=False):
    extra = '<span aria-hidden="true">/</span><a href="index.html">' + loc(*TITLE, conv) + '</a>' if article else ''
    return '<nav class="lw-crumb" aria-label="Breadcrumb"><a href="../sae/index.html#shared-life">' + loc('Shared life & institutions', '共同生活与制度', conv) + '</a>' + extra + '</nav>'


def related(conv):
    return '<aside class="lw-related">' + loc('Keep exploring', '换一处继续读', conv, 'h2') + ''.join(
        '<a href="' + path + '">' + loc(en, zh, conv) + '</a>' for path, en, zh in (
            ('../econ/index.html', 'SAE Economics · how markets work', 'SAE 经济学 · 经济怎样运行'),
            ('../institution/index.html', 'Institutions', '制度论'),
            ('../cooperation-histories/index.html', 'After the Shared Decision · real histories', '共同决定之后 · 真实历史'),
            ('../sae/index.html#shared-life', 'The SAE reading map', 'SAE 散文阅读地图'),
        )) + '</aside>'


def reading_note(conv, item=None):
    note = loc(
        'The introduction offers a philosophical way of asking; the cases follow public records, not invented participants. Allegations, rulings, agreed remedies, company explanations and the author’s interpretation are distinguished. English is independently written; both Chinese scripts are complete. Case status is checked to 1 November 2026. This is not current legal or business advice.',
        '导读提供哲学提问，案例沿公开文件展开，不虚构人物。指控、裁定、约定救济、企业解释与作者解读分别交代。英文独立重写，简繁中文均为全文。案件状态核对至2026年11月1日，不作现行法律或经营建议。', conv, 'p')
    if item:
        note += '<ol class="st-source-list">' + ''.join('<li><a href="' + html.escape(s['url'], quote=True) + '">' + loc(s['title_en'], s['title_zh'], conv) + '</a>' + loc(s['note_en'], s['note_zh'], conv, 'p') + '</li>' for s in item['sources']) + '</ol>'
    else:
        note += loc('The research report helped select cases; each essay links the original records and states their limits. A useful contribution does not cancel a harmful condition, and a dispute does not erase everything an arrangement made possible.', '研究报告帮助选题，不代替每篇所附原始材料及证据边界。有用的贡献不抵销有问题的条件，发生争议也不抹去一项安排曾使什么成为可能。', conv, 'p')
    if not item or item['kind'] != 'introduction':
        note += '<p><a href="https://self-as-an-end.net/papers/sae-political-economy-prequel.html">' + loc('Optional philosophical background ↗', '可选深读：政治经济学原论文 ↗', conv) + '</a> · ' + loc('Questions to bring to the evidence, not a conclusion the evidence must prove.', '带着问题读证据，不要求证据证明预定结论。', conv) + '</p>'
    return '<details class="lw-sources"><summary>' + loc('Sources & reading note', '来源与阅读说明', conv) + '</summary>' + note + '</details>'


def document(content, title, deck, filename, conv, items, item=None):
    source = item['sources'][0]['url'] if item else None
    text = page(content, title, deck, 'essays/political-economy/' + filename, conv, source, (BASE, TITLE[0]), publication_date=DATE)
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
    schema = json.loads(match[1])
    schema.update(datePublished=DATE, dateModified=DATE)
    if item:
        schema['citation'] = [s['url'] for s in item['sources']]
        if item.get('coverage'):
            schema['temporalCoverage'] = item['coverage']
        schema['about'] = {'@type':'Thing', 'name':item['place_en']}
    else:
        schema['hasPart'] = [{'@type':'Article','name':d['title_en'],'url':BASE + d['slug'] + '.html'} for d in items]
    return (text[:match.start(1)] + json.dumps(schema, ensure_ascii=False).replace('</', '<\\/') + text[match.end(1):]).replace('</head>', '<link rel="stylesheet" href="../state-transitions/reading.css?v=20261029"></head>')


def landing(items, conv):
    intro = items[0]
    cards = ''.join('<a class="lw-card" href="' + d['slug'] + '.html"><p class="lw-kicker">' + loc(d['place_en'], d['place_zh'], conv) + '</p>' + loc(d['title_en'], d['title_zh'], conv, 'h2') + loc(d['deck_en'], d['deck_zh'], conv, 'p') + loc('Read essay →', '阅读全文 →', conv, 'span', 'lw-read') + '</a>' for d in items[1:])
    content = '<main class="lw-wrap">' + breadcrumb(conv) + '<section class="lw-hero"><p class="lw-kicker">Non Dubito · ' + loc('Political economy · Real cases', '政治经济学 · 真实案例', conv) + '</p>' + loc(*TITLE, conv, 'h1') + loc(*DECK, conv, 'p', 'lw-deck lw-search-deck') + loc('An ongoing series · A short introduction + two cases · English, Simplified & Traditional Chinese', '持续展开的专题 · 短导读＋两篇案例 · 英文、简体中文与繁体中文', conv, 'p', 'lw-meta') + '</section><aside class="lw-opening">' + loc(intro['title_en'], intro['title_zh'], conv, 'h2') + loc('Can someone leave? Can they stay and object? Begin with these questions, or go straight to a case below. No prior reading is required.', '走得了，也能留下来提出异议吗？可以先读短导读，也可以直接进入下面任一案例，不必先读论文。', conv, 'p') + '<a href="introduction.html">' + loc('Read the short introduction →', '读短导读 →', conv) + '</a></aside><section class="lw-grid" id="cases" aria-label="Real case readings">' + cards + '</section><section class="lw-note">' + loc('Not a list of guilty companies', '不为公司排一张好坏榜', conv, 'h2') + loc('A course can open a profession and attach an obligation to departure. A marketplace can create demand and shape the alternatives to itself. Follow the particular decisions, benefits, costs and routes to review. The cases can complicate the questions; they are not required to deliver one verdict.', '培训可以打开一种职业，也可能给离开附上条件。平台可以创造需求，也会影响替代之路。逐项读贡献、代价、决定与复核途径；案例可以使问题更复杂，不必得出同一种判词。', conv, 'p') + '</section>' + reading_note(conv) + related(conv) + '</main>'
    return document(content, TITLE[0], DECK[0], 'index.html', conv, items)


def article(item, items, conv):
    bodies = ''.join('<div class="essay-body lw-prose lang-' + lang + '" lang="' + native + '">' + prose([conv.convert(p) for p in item['body_zh']] if lang == 'hant' else item['body_' + lang], item['sources']) + '</div>' for lang, native in (('en','en'),('zh','zh-Hans'),('hant','zh-Hant')))
    nav = ''
    for offset, en, zh in ((-1,'Previous reading','上一篇'),(1,'Next reading','下一篇')):
        position = item['id'] - 1 + offset
        if 0 <= position < len(items):
            other = items[position]
            nav += '<a href="' + other['slug'] + '.html">' + loc(en, zh, conv, 'small') + loc(other['title_en'], other['title_zh'], conv) + '</a>'
        else:
            nav += '<a href="index.html">' + loc('The ongoing series', '持续展开的专题', conv, 'small') + loc(*TITLE, conv) + '</a>'
    note = ('A short introduction · English independently written', '短导读 · 英文独立重写') if item['kind'] == 'introduction' else ('Real-case essay · English independently written', '真实案例散文 · 英文独立重写')
    content = '<main class="lw-wrap">' + breadcrumb(conv, True) + '<article class="lw-article" data-search="' + html.escape(item['search_labels'], quote=True) + '"><div class="lw-head"><p class="lw-kicker">' + loc(item['place_en'], item['place_zh'], conv) + '</p>' + loc(item['title_en'], item['title_zh'], conv, 'h1') + loc(item['deck_en'], item['deck_zh'], conv, 'p', 'lw-deck lw-search-deck') + '<p class="lw-meta">Han Qin · <time datetime="' + DATE + '">' + DATE + '</time> · ' + loc(*note, conv) + '</p></div>' + bodies + reading_note(conv, item) + '<nav class="lw-series-nav" aria-label="Series navigation">' + nav + '</nav>' + related(conv) + '</article></main>'
    return document(content, item['title_en'], item['deck_en'], item['slug'] + '.html', conv, items, item)


def render():
    items = load_items()
    conv = PoliticalTraditionalConverter()
    try:
        return {TARGET/'index.html':landing(items, conv), **{TARGET/(d['slug'] + '.html'):article(d, items, conv) for d in items}}
    finally:
        conv.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, text in render().items():
        if args.check:
            assert path.read_text() == text, f'Stale page: {path}'
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(('Checked' if args.check else 'Wrote') + ' Political Economy · short introduction + two cases · three complete modes')


if __name__ == '__main__':
    main()
