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
    'A detention challenged, an election lost, a constitution returned for revision. Historical essays follow what changes for people when ways of questioning power close or open. Begin with India and South Africa; further histories will join this shelf.',
    '一次拘留的追问，一场败选，一部被退回修改的宪法。从具体历史读人怎样获得、失去，又重新争取说话的资格。先读印度与南非，专题将继续展开。',
)
SLUGS = ('india-1975-1979', 'south-africa-1990-1997')
FRAMEWORK = 'https://self-as-an-end.net/papers/sae-state-reverse-phase-transition.html'


class HistoryTraditionalConverter(ReversalTraditionalConverter):
    def convert(self, text):
        result = super().convert(text)
        for old, new in (('裡貝羅', '里貝羅'), ('划定', '劃定'), ('瞄准', '瞄準'), ('限製', '限制')):
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
    return '<!-- STATE HISTORIES START --><section class="state-group" id="historical-readings"><p class="state-kicker">' + loc('A separate historical series · first two essays', '独立历史专题 · 首发两篇', conv) + '</p>' + loc(*TITLE, conv, 'h2') + loc('India, 1975–1979, and South Africa, 1990–1997: real events, public records and different routes through which decisions can be questioned. These histories do not continue the fictional cases or assign countries a permanent verdict.', '印度1975—1979、南非1990—1997：沿真实事件与史料，看决定怎样受到追问，哪些路打开，哪些仍受限。不是虚构案例的续篇，也不给国家盖一枚永远不变的章。', conv, 'p', 'state-deck') + '<p class="state-return"><a href="../state-transitions/index.html">' + loc('Read the histories →', '进入历史专题 →', conv) + '</a></p></section><!-- STATE HISTORIES END -->'


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
        schema['temporalCoverage'] = '1975/1979' if item['id'] == 1 else '1990/1997'
        schema['about'] = {'@type': 'Thing', 'name': item['place_en']}
    else:
        schema['hasPart'] = [{'@type': 'Article', 'name': d['title_en'], 'url': BASE + d['slug'] + '.html'} for d in load_items()]
    result = result[:schema_match.start(1)] + json.dumps(schema, ensure_ascii=False).replace('</', '<\\/') + result[schema_match.end(1):]
    return result.replace('</head>', '<link rel="stylesheet" href="reading.css?v=20261029"></head>')


def landing(items, conv):
    cards = ''.join('<a class="lw-card" href="' + d['slug'] + '.html"><p class="lw-kicker">' + loc(d['place_en'], d['place_zh'], conv) + '</p>' + loc(d['title_en'], d['title_zh'], conv, 'h2') + loc(d['deck_en'], d['deck_zh'], conv, 'p') + loc('Read essay →', '阅读全文 →', conv, 'span', 'lw-read') + '</a>' for d in items)
    content = '<main class="lw-wrap">' + breadcrumb(conv) + '<section class="lw-hero"><p class="lw-kicker">Non Dubito · ' + loc('Historical readings', '历史细读', conv) + '</p>' + loc(*TITLE, conv, 'h1') + loc(*SUBTITLE, conv, 'p', 'lw-deck') + loc(*DECK, conv, 'p', 'lw-deck lw-search-deck') + loc('First two essays · English, Simplified & Traditional Chinese · an ongoing series', '首发两篇 · 英文、简体中文与繁体中文 · 持续展开的专题', conv, 'p', 'lw-meta') + '</section><aside class="lw-opening">' + loc('Start with a person, not a verdict on a country. Who can ask? Who has to answer? Can the answer change what happens? The histories may enlarge or complicate the questions; they are not required to prove a theory.', '先看一个人的处境，不急着给国家定性。谁能问，谁须回答，回答以后能不能改变什么？历史可以把这些问题改得更细，不必负责证明一套理论。', conv, 'p') + '<a href="india-1975-1979.html">' + loc('Begin in India →', '从印度读起 →', conv) + '</a></aside><section class="lw-grid">' + cards + '</section><section class="lw-note">' + loc('Put the histories beside each other', '把两段历史放在旁边读', conv, 'h2') + loc('In India, access to a judicial remedy narrowed, an election changed the government, and constitutional repair followed. In South Africa, equal political standing expanded while a newly elected majority accepted review of its constitution; victims’ families also challenged the costs of the amnesty settlement. Changes need not move together for every person or every institution.', '印度的一条司法救济受阻，后来选举改变政府，再有修宪接上。南非扩大了平等参与的资格，新多数也接受对制宪的审查；受害者家属同时追问赦免安排的代价。不同的人、不同的机构，不一定朝同一个方向、在同一天改变。', conv, 'p') + '</section>' + reading_note(conv) + related(conv) + '</main>'
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
    others = [d for d in items if d['id'] != item['id']]
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
    print(('Checked' if args.check else 'Wrote') + ' State histories · first two essays · three complete modes')


if __name__ == '__main__':
    main()
