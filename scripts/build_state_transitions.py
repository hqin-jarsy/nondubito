#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build an open-ended historical essay series; keep it distinct from fictional State cases."""
from __future__ import annotations

import argparse
import html
import json
import re

from build_language_writing import ROOT, loc, page
from build_state_reversal import ReversalTraditionalConverter

DATE = '2026-10-29'
DATA = ROOT / 'data/state-transitions'
TARGET = ROOT / 'essays/state-transitions'
BASE = 'https://nondubito.net/essays/state-transitions/'
TITLE = ('States in Motion', '国家的进退')
SUBTITLE = ('Power, questioning, and the place of persons', '权力、追问与人的位置')
DECK = (
    'A detention challenged, a constitution returned, an opposition vote, a street demanding change, a limited crown and displaced judges. Six histories ask who can question power, and what an answer can change. The shelf remains open.',
    '一次拘留的追问，一部被退回的宪法，一张反对票，一条要求改变的街，一个受约束的王位，一批被排除的法官。沿六段历史，看人怎样获得、失去，又重新争取说话的资格。专题仍将继续展开。',
)
SLUGS = ('india-1975-1979', 'south-africa-1990-1997', 'germany-1933', 'south-korea-1987-1988', 'england-1688-1701', 'pakistan-2007-2009')
FRAMEWORK = 'https://self-as-an-end.net/papers/sae-state-reverse-phase-transition.html'


class HistoryTraditionalConverter(ReversalTraditionalConverter):
    def convert(self, text):
        result = super().convert(text)
        for old, new in (('裡貝羅', '里貝羅'), ('划定', '劃定'), ('瞄准', '瞄準'), ('限製', '限制'), ('樸鐘哲', '朴鍾哲'), ('全鬥煥', '全斗煥'), ('喬杜裡', '喬杜里')):
            result = result.replace(old, new)
        return result


def load_items():
    items = []
    for number, slug in enumerate(SLUGS, 1):
        item = json.loads((DATA / (slug + '.json')).read_text())
        assert item['id'] == number and item['slug'] == slug
        assert [s['id'] for s in item['sources']] == list(range(1, len(item['sources']) + 1))
        for source in item['sources']:
            assert source['url'].startswith('https://')
            for key in ('title_en', 'title_zh', 'note_en', 'note_zh'):
                assert source[key].strip()
        for lang in ('en', 'zh'):
            body = item['body_' + lang]
            assert len(body) >= 25 and sum(p.startswith('## ') for p in body) == 3
            assert all(p.strip() and '<' not in p for p in body)
            text = '\n'.join(body)
            count = len(re.findall(r'[\u3400-\u9fff]', text)) if lang == 'zh' else len(text.split())
            assert count >= (2400 if lang == 'zh' else 1400), (slug, lang, count)
            refs = set(map(int, re.findall(r'\[(\d+)\]', text)))
            assert refs == {s['id'] for s in item['sources']}, (slug, lang, refs)
            assert not re.search(r'\b\d{2}DD\b|\bN\d+\b|正相变|逆相变|phase transition', text)
        items.append(item)
    return items


def breadcrumb(conv, article=False):
    tail = '<span aria-hidden="true">/</span><a href="index.html">' + loc(*TITLE, conv) + '</a>' if article else ''
    return '<nav class="lw-crumb" aria-label="Breadcrumb"><a href="../../explore.html#history">' + loc('History, Power & Civilization', '历史、权力与文明', conv) + '</a>' + tail + '</nav>'


def related(conv):
    return '<aside class="lw-related">' + loc('Other ways into the question', '换一处继续读', conv, 'h2') + ''.join(
        '<a href="' + path + '">' + loc(en, zh, conv) + '</a>' for path, en, zh in (
            ('../state/index.html', 'Theory of the State · fictional cases', '国家论 · 虚构案例与哲学讨论'),
            ('../state-reversal/index.html', 'When a State Slides Back · fictional companion', '国家怎样往回滑 · 虚构专论'),
            ('../sae/index.html#shared-life', 'Shared life & institutions', '共同生活与制度'),
        )) + '</aside>'


def history_entry(conv):
    """Used by the original State landing page, without changing its essay count."""
    return '<!-- STATE HISTORIES START --><section class="state-group" id="historical-readings"><p class="state-kicker">' + loc('A separate historical series · six essays', '独立历史专题 · 六篇', conv) + '</p>' + loc(*TITLE, conv, 'h2') + loc('India, South Africa, Germany, South Korea, England and Pakistan: real events, public records and different routes through which decisions can be questioned. These histories do not continue the fictional cases or assign countries a permanent verdict.', '印度、南非、德国、韩国、英格兰与巴基斯坦：沿真实事件与史料，看决定怎样受到追问，哪些路打开，哪些仍受限。不是虚构案例的续篇，也不给国家盖一枚永远不变的章。', conv, 'p', 'state-deck') + '<p class="state-return"><a href="../state-transitions/index.html">' + loc('Read the histories →', '进入历史专题 →', conv) + '</a></p></section><!-- STATE HISTORIES END -->'


def reading_note(conv, item=None):
    opening = loc('These are historical essays, not invented case studies, a current-law guide or a ranking of countries. Recorded events and legal decisions are distinguished from the author’s structural reading. No dialogue, private thoughts or composite participants have been invented. English is independently written; both Chinese scripts carry the complete text.', '本专题写真实历史，不是虚构案例、现行法律指南或国家排名。史料记载、法律判断与作者的结构性解读分开；不虚构对话、内心活动或拼合人物。英文独立重写，简繁中文全文对应。', conv, 'p')
    if item:
        refs = '<ol class="st-source-list">' + ''.join('<li><a href="' + html.escape(s['url'], quote=True) + '">' + loc(s['title_en'], s['title_zh'], conv) + '</a>' + loc(s['note_en'], s['note_zh'], conv, 'p') + '</li>' for s in item['sources']) + '</ol>'
    else:
        refs = loc('Each essay links its factual passages to numbered sources and supplies document sections below the text. The initial research report helped select cases; it is not substituted for the cited records. Dates of proposal, assent, certification and commencement are kept distinct.', '每篇在事实段落附编号来源，文末说明所据文件与段落。初步研究报告用来筛选案例，不代替可回查的史料。提出、批准、认证与生效等日期分别交代。', conv, 'p')
    framework = '<p><a href="' + FRAMEWORK + '">' + loc('Optional philosophical background ↗', '可选阅读：哲学背景论文 ↗', conv) + '</a> · ' + loc('A way of asking, not a substitute for historical evidence.', '提供提问的角度，不代替历史证据。', conv) + '</p>'
    return '<details class="lw-sources"><summary>' + loc('Records & reading note', '史料与阅读说明', conv) + '</summary>' + opening + refs + framework + '</details>'


def document(content, title, deck, filename, conv, item=None):
    source = item['sources'][0]['url'] if item else None
    result = page(content, title, deck, 'essays/state-transitions/' + filename, conv, source,
                  (BASE, TITLE[0]), publication_date=DATE)
    schema_match = re.search(r'<script type="application/ld\+json">(.*?)</script>', result, re.S)
    schema = json.loads(schema_match[1])
    schema.update(datePublished=DATE, dateModified=DATE)
    if item:
        schema['citation'] = [s['url'] for s in item['sources']]
        schema['temporalCoverage'] = item.get('coverage') or {1:'1975/1979', 2:'1990/1997'}[item['id']]
        schema['about'] = {'@type': 'Thing', 'name': item['place_en']}
    else:
        schema['hasPart'] = [{'@type': 'Article', 'name': d['title_en'], 'url': BASE + d['slug'] + '.html'} for d in load_items()]
    result = result[:schema_match.start(1)] + json.dumps(schema, ensure_ascii=False).replace('</', '<\\/') + result[schema_match.end(1):]
    return result.replace('</head>', '<link rel="stylesheet" href="reading.css?v=20261029"></head>')


def landing(items, conv):
    cards = ''.join('<a class="lw-card" href="' + d['slug'] + '.html"><p class="lw-kicker">' + loc(d['place_en'], d['place_zh'], conv) + '</p>' + loc(d['title_en'], d['title_zh'], conv, 'h2') + loc(d['deck_en'], d['deck_zh'], conv, 'p') + loc('Read essay →', '阅读全文 →', conv, 'span', 'lw-read') + '</a>' for d in items)
    content = '<main class="lw-wrap">' + breadcrumb(conv) + '<section class="lw-hero"><p class="lw-kicker">Non Dubito · ' + loc('Historical readings', '历史细读', conv) + '</p>' + loc(*TITLE, conv, 'h1') + loc(*SUBTITLE, conv, 'p', 'lw-deck') + loc(*DECK, conv, 'p', 'lw-deck lw-search-deck') + loc('Six essays · English, Simplified & Traditional Chinese · an ongoing series', '六篇 · 英文、简体中文与繁体中文 · 持续展开的专题', conv, 'p', 'lw-meta') + '</section><aside class="lw-opening">' + loc('Start with a person, not a verdict on a country. Who can ask? Who has to answer? Can the answer change what happens? The histories may enlarge or complicate the questions; they are not required to prove a theory.', '先看一个人的处境，不急着给国家定性。谁能问，谁须回答，回答以后能不能改变什么？历史可以把这些问题改得更细，不必负责证明一套理论。', conv, 'p') + '<a href="india-1975-1979.html">' + loc('Begin in India →', '从印度读起 →', conv) + '</a></aside><section class="lw-grid">' + cards + '</section><section class="lw-note">' + loc('Put the histories beside each other', '把这些历史放在旁边读', conv, 'h2') + loc('Read the pairs alongside each other: India and South Africa follow elections, review and repair; Germany and South Korea examine the conditions of participation; England and Pakistan ask who may consent and who may remain to review. These are comparisons of particular changes, not six positions on one ladder.', '把三组放在旁边读：印度与南非追选举、审查与修复；德国与韩国看参与能不能继续；英格兰与巴基斯坦问，谁的同意算数，谁能留在审查的位置上。对读具体变化，不把六段历史排在同一架阶梯上。', conv, 'p') + '</section>' + reading_note(conv) + related(conv) + '</main>'
    return document(content, TITLE[0] + ' · 国家的进退', DECK[0], 'index.html', conv)


def prose(body, sources):
    lookup = {s['id']: s['url'] for s in sources}
    lines = []
    for p in body:
        heading = p.startswith('## ')
        text = html.escape(p[3:] if heading else p, quote=True)
        text = re.sub(r'\[(\d+)\]', lambda m: '<sup class="st-cite"><a href="' + html.escape(lookup[int(m[1])], quote=True) + '" aria-label="Source ' + m[1] + '">[' + m[1] + ']</a></sup>', text)
        tag = 'h2' if heading else 'p'
        lines.append('<' + tag + '>' + text + '</' + tag + '>')
    return '\n'.join(lines)


def article(item, items, conv):
    bodies = ''.join('<div class="essay-body lw-prose lang-' + lang + '" lang="' + native + '">' + prose([conv.convert(p) for p in item['body_zh']] if lang == 'hant' else item['body_' + lang], item['sources']) + '</div>' for lang, native in (('en', 'en'), ('zh', 'zh-Hans'), ('hant', 'zh-Hant')))
    # Keep previously published pairs byte-for-byte stable when adding a pair.
    partner = item['id'] + (1 if item['id'] % 2 else -1)
    others = [d for d in items if d['id'] == partner]
    nav = '<a href="index.html">' + loc('The ongoing series', '持续展开的专题', conv, 'small') + loc(*TITLE, conv) + '</a>'
    nav += ''.join('<a href="' + d['slug'] + '.html">' + loc('Read alongside this essay', '放在旁边读', conv, 'small') + loc(d['title_en'], d['title_zh'], conv) + '</a>' for d in others)
    content = '<main class="lw-wrap">' + breadcrumb(conv, True) + '<article class="lw-article"><div class="lw-head"><p class="lw-kicker">' + loc(item['place_en'], item['place_zh'], conv) + ' · ' + loc(*TITLE, conv) + '</p>' + loc(item['title_en'], item['title_zh'], conv, 'h1') + loc(item['deck_en'], item['deck_zh'], conv, 'p', 'lw-deck lw-search-deck') + '<p class="lw-meta">Han Qin · <time datetime="' + DATE + '">' + DATE + '</time> · ' + loc('Historical essay · English independently written', '历史散文 · 英文独立重写', conv) + '</p></div>' + bodies + reading_note(conv, item) + '<nav class="lw-series-nav" aria-label="Series navigation">' + nav + '</nav>' + related(conv) + '</article></main>'
    return document(content, item['title_en'], item['deck_en'], item['slug'] + '.html', conv, item)


def render():
    items = load_items()
    conv = HistoryTraditionalConverter()
    try:
        return {TARGET / 'index.html': landing(items, conv), **{TARGET / (d['slug'] + '.html'): article(d, items, conv) for d in items}}
    finally:
        conv.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, text in render().items():
        if args.check:
            assert path.read_text() == text, f'Stale output: {path}'
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(('Checked' if args.check else 'Wrote') + f' State histories · {len(SLUGS)} essays · three complete modes')


if __name__ == '__main__':
    main()
