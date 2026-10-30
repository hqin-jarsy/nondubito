#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build an open historical companion without treating institutions as one model."""
from __future__ import annotations

import argparse
import html
import json
import re

from build_language_writing import ROOT, loc, page
from build_state_transitions import HistoryTraditionalConverter, prose

DATE = '2026-10-30'
DATA = ROOT / 'data/cooperation-histories'
TARGET = ROOT / 'essays/cooperation-histories'
BASE = 'https://nondubito.net/essays/cooperation-histories/'
TITLE = ('After the Shared Decision', '共同决定之后')
DECK = (
    'Water crosses a border. Food passes through sanctions. A name enters a list. Real histories of shared decisions, their consequences, and the routes by which people can ask for another look.',
    '水流越过国界，食品穿过制裁，一个名字进入名单。沿真实历史，看共同决定怎样改变生活，又有没有一条路，让受到影响的人要求再看一次。',
)
SLUGS = ('rhine-sandoz', 'haiti-cholera', 'iraq-sanctions', 'kadi-listing')
FRAMEWORK = 'https://self-as-an-end.net/papers/sae-interstate-prequel.html'


class CooperationTraditionalConverter(HistoryTraditionalConverter):
    def convert(self, text):
        return (super().convert(text).replace('開啓', '開啟')
                .replace('寫准', '寫準').replace('稱贊', '稱讚')
                .replace('啓用', '啟用').replace('阿裡', '阿里')
                .replace('復審', '複審'))


def load_items():
    items = []
    for number, slug in enumerate(SLUGS, 1):
        d = json.loads((DATA / (slug + '.json')).read_text())
        assert d['id'] == number and d['slug'] == slug
        assert [s['id'] for s in d['sources']] == list(range(1, len(d['sources']) + 1))
        for s in d['sources']:
            assert s['url'].startswith('https://')
            assert all(s[k].strip() for k in ('title_en', 'title_zh', 'note_en', 'note_zh'))
        for lang in ('en', 'zh'):
            body = d['body_' + lang]
            assert len(body) >= 25 and sum(p.startswith('## ') for p in body) == 3
            assert all(p.strip() and '<' not in p for p in body)
            text = '\n'.join(body)
            count = len(re.findall(r'[\u3400-\u9fff]', text)) if lang == 'zh' else len(text.split())
            assert count >= (2400 if lang == 'zh' else 1400), (slug, lang, count)
            assert set(map(int, re.findall(r'\[(\d+)\]', text))) == {s['id'] for s in d['sources']}
            assert not re.search(r'\b\d{2}DD\b|\bXZ\d+\b|\b[NGZ]\d+\b|\bF6\b', text)
        items.append(d)
    return items


def breadcrumb(conv, article=False):
    tail = '<span aria-hidden="true">/</span><a href="index.html">' + loc(*TITLE, conv) + '</a>' if article else ''
    return '<nav class="lw-crumb" aria-label="Breadcrumb"><a href="../../explore.html#history">' + loc('History, Power & Civilization', '历史、权力与文明', conv) + '</a>' + tail + '</nav>'


def related(conv):
    return '<aside class="lw-related">' + loc('Other ways into the question', '放在旁边读', conv, 'h2') + ''.join(
        '<a href="' + path + '">' + loc(en, zh, conv) + '</a>' for path, en, zh in (
            ('../interstate/index.html', 'Between States, Who Answers? · fictional cases', '国家之间，谁来回答？· 虚构案例与哲学讨论'),
            ('../state-transitions/index.html', 'States in Motion · real histories', '国家的进退 · 真实历史细读'),
            ('../sae/index.html#shared-life', 'Shared life & institutions', '共同生活与制度'),
        )) + '</aside>'


def source_note(conv, item=None):
    note = loc(
        'Historical readings, not invented scenes or a current-law guide. Documented facts, contemporaneous legal decisions, institutional self-assessments, and the author’s interpretation are kept distinct. No private thoughts, dialogue, or composite victims are invented. English is independently written; both Chinese scripts are complete. The source research report helped select cases but does not replace the linked records. Different organizations do not automatically fit the theory’s non-coercive model.',
        '本专题写真实历史，不虚构场景，也不作现行法律指南。史料事实、当时法律判断、机构自我总结与作者的解读分开，不虚构内心、对话或拼合受害者。英文独立重写，简繁中文均为完整正文。初步研究报告帮助选题，不代替下列可回查的原始材料；不同组织不自动属于理论定义的无共同强制性上级的协作。', conv, 'p')
    if item:
        note += '<ol class="st-source-list">' + ''.join('<li><a href="' + html.escape(s['url'], quote=True) + '">' + loc(s['title_en'], s['title_zh'], conv) + '</a>' + loc(s['note_en'], s['note_zh'], conv, 'p') + '</li>' for s in item['sources']) + '</ol>'
    note += '<p><a href="' + FRAMEWORK + '">' + loc('Optional philosophical background ↗', '可选阅读：哲学背景论文 ↗', conv) + '</a> · ' + loc('Questions to test against history, not conclusions history must prove.', '把问题交给历史检验，不要求历史证明理论。', conv) + '</p>'
    return '<details class="lw-sources"><summary>' + loc('Records & reading note', '史料与阅读说明', conv) + '</summary>' + note + '</details>'


def companion_entry(conv):
    """For the fictional series landing only; leave its three essays untouched."""
    return '<!-- COOPERATION HISTORIES COMPANION START --><section class="lw-note" id="real-world-readings">' + loc('A separate shelf of real histories', '另读真实世界 · 独立专题', conv, 'p', 'lw-kicker') + loc(*TITLE, conv, 'h2') + loc('From the Rhine and Haiti to comprehensive sanctions on Iraq and Kadi’s challenges to his listing. Different powers, responsibilities and routes to review—not continuations of Three Borders, not a ranking of successful and failed cooperation.', '从莱茵河、海地，到伊拉克全面制裁与卡迪的名单复审。真实机构的权限、责任和追问途径分别交代，不是三界镇的续篇，也不把案例排成合作成功与失败的榜单。', conv, 'p') + '<a class="lw-read" href="../cooperation-histories/index.html">' + loc('Read the histories →', '进入真实案例专题 →', conv) + '</a></section><!-- COOPERATION HISTORIES COMPANION END -->'


def document(content, title, deck, filename, conv, items, item=None):
    result = page(content, title, deck, 'essays/cooperation-histories/' + filename, conv,
                  item['sources'][0]['url'] if item else None, (BASE, TITLE[0]), publication_date=DATE)
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', result, re.S)
    schema = json.loads(match[1])
    schema.update(datePublished=DATE, dateModified=DATE)
    if item:
        schema.update(citation=[s['url'] for s in item['sources']], temporalCoverage=item['coverage'], about={'@type':'Thing', 'name':item['place_en']})
    else:
        schema['hasPart'] = [{'@type':'Article', 'name':d['title_en'], 'url':BASE+d['slug']+'.html'} for d in items]
    return (result[:match.start(1)] + json.dumps(schema, ensure_ascii=False).replace('</', '<\\/') + result[match.end(1):]).replace('</head>', '<link rel="stylesheet" href="../state-transitions/reading.css?v=20261029"></head>')


def landing(items, conv):
    cards = ''
    for pair, en, zh, deck_en, deck_zh in (
        (items[:2], 'Water, harm, and a request', '水流、损害与请求', 'The Rhine and Haiti: different sources of responsibility, different routes to repair.', '莱茵河与海地：不同的责任来源，不同的修复道路。'),
        (items[2:], 'Sanctions, names, and review', '制裁、名字与复审', 'Iraq and Kadi: a broad restriction and a named target do not ask the same question.', '伊拉克与卡迪：全面限制与直接列名，带来的不是同一道问题。'),
    ):
        cards += '<section class="lw-note">' + loc(en, zh, conv, 'h2') + loc(deck_en, deck_zh, conv, 'p') + '</section><section class="lw-grid">' + ''.join('<a class="lw-card" href="' + d['slug'] + '.html"><p class="lw-kicker">' + loc(d['place_en'], d['place_zh'], conv) + '</p>' + loc(d['title_en'], d['title_zh'], conv, 'h3') + loc(d['deck_en'], d['deck_zh'], conv, 'p') + loc('Read essay →', '阅读全文 →', conv, 'span', 'lw-read') + '</a>' for d in pair) + '</section>'
    content = '<main class="lw-wrap">' + breadcrumb(conv) + '<section class="lw-hero"><p class="lw-kicker">Non Dubito · ' + loc('Historical readings of cooperation', '协作的真实历史细读', conv) + '</p>' + loc(*TITLE, conv, 'h1') + loc(*DECK, conv, 'p', 'lw-deck lw-search-deck') + loc('An ongoing series · Four essays · English, Simplified & Traditional Chinese', '持续展开的专题 · 四篇 · 英文、简体中文与繁体中文', conv, 'p', 'lw-meta') + '</section><aside class="lw-opening">' + loc('Begin with a river, a request for a hearing, a food delivery or a name on a list. No theory is required before reading. Who decides, who implements, who is affected, and who can initiate another look?', '可以从水流、听证请求、食品到货或一个被列名的人读起。不必先补理论。谁决定，谁实施，谁受到影响，又由谁来启动再一次审查？', conv, 'p') + '<a href="rhine-sandoz.html">' + loc('Follow the river →', '先跟着河水走 →', conv) + '</a></aside>' + cards + '<section class="lw-note">' + loc('Different responsibilities, not opposite grades', '责任来源不同，不是两个相反的评分', conv, 'h2') + loc('A company accident, an international operation implicated in harm, a comprehensive trade regime and a targeted asset freeze. These do not confer identical powers or offer identical remedies. Improvements do not retrospectively justify every earlier decision; a gap does not erase useful work. The differences are why the histories belong together.', '企业事故、国际行动自身被指带来的伤害、全面贸易限制与针对个人的财产冻结，权限和救济不能揉成一团。后来的改进不追认此前每项决定，存在缺口也不抹去真实工作。保留不同，才值得并列阅读。', conv, 'p') + '</section>' + source_note(conv) + related(conv) + '</main>'
    return document(content, TITLE[0] + ' · 共同决定之后', DECK[0], 'index.html', conv, items).replace('</head>', '<link rel="stylesheet" href="reading.css?v=20261030"></head>')


def article(item, items, conv):
    bodies = ''.join('<div class="essay-body lw-prose lang-' + lang + '" lang="' + native + '">' + prose([conv.convert(p) for p in item['body_zh']] if lang == 'hant' else item['body_' + lang], item['sources']) + '</div>' for lang, native in (('en','en'),('zh','zh-Hans'),('hant','zh-Hant')))
    partner = item['id'] + (1 if item['id'] % 2 else -1)
    nav = '<a href="index.html">' + loc('The ongoing series', '持续展开的专题', conv, 'small') + loc(*TITLE, conv) + '</a>'
    nav += ''.join('<a href="' + d['slug'] + '.html">' + loc('Read alongside this essay', '放在旁边读', conv, 'small') + loc(d['title_en'], d['title_zh'], conv) + '</a>' for d in items if d['id'] == partner)
    content = '<main class="lw-wrap">' + breadcrumb(conv, True) + '<article class="lw-article"><div class="lw-head"><p class="lw-kicker">' + loc(item['place_en'], item['place_zh'], conv) + ' · ' + loc(*TITLE, conv) + '</p>' + loc(item['title_en'], item['title_zh'], conv, 'h1') + loc(item['deck_en'], item['deck_zh'], conv, 'p', 'lw-deck lw-search-deck') + '<p class="lw-meta">Han Qin · <time datetime="' + DATE + '">' + DATE + '</time> · ' + loc('Historical essay · English independently written', '历史散文 · 英文独立重写', conv) + '</p></div>' + bodies + source_note(conv, item) + '<nav class="lw-series-nav" aria-label="Series navigation">' + nav + '</nav>' + related(conv) + '</article></main>'
    return document(content, item['title_en'], item['deck_en'], item['slug'] + '.html', conv, items, item)


def render():
    items = load_items()
    conv = CooperationTraditionalConverter()
    try:
        return {TARGET/'index.html': landing(items, conv), **{TARGET/(d['slug']+'.html'):article(d,items,conv) for d in items}}
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
    print(('Checked' if args.check else 'Wrote') + ' After the Shared Decision · four histories · three complete modes')


if __name__ == '__main__':
    main()
