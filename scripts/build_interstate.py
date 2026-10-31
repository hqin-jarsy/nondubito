#!/usr/bin/env python3
"""Build nine Interstate Cooperation reader essays, not a historical casebook."""
from __future__ import annotations

import argparse
import html
import json
import re

from build_language_writing import ROOT, loc, page, prose
from build_state_reversal import ReversalTraditionalConverter
from build_cooperation_histories import companion_entry as real_world_entry

DATE = '2026-10-30'
COMPLETE_DATE = '2026-10-31'
DATA = ROOT / 'data/interstate'
TARGET = ROOT / 'essays/interstate'
BASE = 'https://nondubito.net/essays/interstate/'
TITLE = ('Between States, Who Answers?', '国家之间，谁来回答？')
DECK = (
    'A compact signed, an applicant kept waiting, a child without nationality. How can states cooperate without handing their judgment to a common superior—and who can question what they do together?',
    '一份签下的约，一个等待加入的邻国，一个没有国籍的孩子。不设一个共同上级，国家怎样合作；一起作出的决定，又向谁回答？',
)
PAPERS = ('prequel', '1', '2', '3', '4', '5', '6', '7', '8')
PLAN = (
    ('Must Cooperation Have a Boss?', '合作，就一定要有一个共同的上级吗？'),
    ('What Makes an Agreement Count?', '没有上级，约定为什么还算数？'),
    ('An Agreement Is Not the End of Questions', '大家已经同意了，还能继续追问吗？'),
    ('More Than “Trust Me”', '信任不是一句“相信我”'),
    ('Withholding Cooperation or Forcing Obedience?', '不再配合，与逼人服从有什么不同？'),
    ('Who Decides to Send Troops?', '盟友受了攻击，谁来决定出兵？'),
    ('When Someone Reaches the Door', '人已经来到门口，怎么办？'),
    ('Leaving Does Not Erase the Account', '可以退出，为什么不能一笔勾销？'),
    ('Without a World Government', '没有世界政府，事情还能往前走吗？'),
)
GROUPS = (
    ('agreements', 'Agreements, questions & trust', '约定、追问与信任', (1, 2, 3, 4)),
    ('protection', 'Pressure, defence & reception', '牵制、防御与接纳', (5, 6, 7)),
    ('afterwards', 'Leaving & living together', '去留与共同生活', (8, 9)),
)


class InterstateTraditionalConverter(ReversalTraditionalConverter):
    def convert(self, text):
        return super().convert(text).replace('開啓', '開啟').replace('限製', '限制')


def load_items():
    items = []
    for path in sorted(DATA.glob('ep[0-9][0-9].json')):
        item = json.loads(path.read_text())
        n = len(items) + 1
        assert item['id'] == n and item['slug'] == f'ep{n:02d}'
        assert item['source_url'] == f'https://self-as-an-end.net/papers/sae-interstate-{PAPERS[n-1]}.html'
        assert item.get('date', DATE) == (DATE if n <= 3 else COMPLETE_DATE)
        for lang in ('en', 'zh'):
            assert item['title_' + lang].strip() and item['deck_' + lang].strip()
            body = item['body_' + lang]
            assert len(body) >= 25 and sum(p.startswith('## ') for p in body) == 3
            assert all(p.strip() and '<' not in p and not p.startswith('###') for p in body)
            text = '\n'.join(body)
            size = len(re.findall(r'[\u3400-\u9fff]', text)) if lang == 'zh' else len(text.split())
            assert size >= (2300 if lang == 'zh' else 1450), (path, lang, size)
            assert not re.search(r'\b\d{2}DD\b|\bXZ\d+\b|\b[NGZ]\d+\b|\bF6\b', text)
        items.append(item)
    assert len(items) == 9
    return items


def breadcrumb(conv, article=False):
    tail = '<span aria-hidden="true">/</span><a href="index.html">' + loc(*TITLE, conv) + '</a>' if article else ''
    return '<nav class="lw-crumb" aria-label="Breadcrumb"><a href="../sae/index.html#shared-life">' + loc('Shared life & institutions', '共同生活与制度', conv) + '</a>' + tail + '</nav>'


def notice(conv):
    return '<aside class="is-notice">' + loc(
        'Imagined cases, not real history. This series explores cooperation without a common coercive superior; it does not describe all existing international institutions, state current law, or prescribe a response to an actual conflict.',
        '文中国家、事件与票数均为虚构，不是真实历史。本系列探索不设共同强制性上级的协作方式，不描述所有现实国际组织，不作现行法律说明，也不替实际冲突开处方。',
        conv, 'p') + '</aside>'


def related(conv):
    return '<aside class="lw-related">' + loc('Read beside this series', '放在旁边读', conv, 'h2') + ''.join(
        '<a href="../' + path + '/index.html">' + loc(en, zh, conv) + '</a>' for path, en, zh in (
            ('state', 'The State Still Has to Answer', '国家论：到了国家这一层，还能问吗？'),
            ('state-transitions', 'States in Motion · real histories', '国家的进退 · 真实历史细读'),
            ('conflict', 'Conflict', '冲突论'),
            ('sae', 'The SAE reading map', 'SAE 散文阅读地图'),
        )) + '</aside>'


def source_note(conv, item=None):
    note = loc(
        'Drawn from SAE Interstate Cooperation, with independently written English and complete editions in both Chinese scripts. These reader essays select arguments and cases rather than translate every proposition or appendix. The examples are invented; institutional rules illustrate choices, not a uniquely optimal constitution. Questioning, a duty to answer, and coercive enforcement are kept distinct. A later policy change is not automatically attributed to the preceding inquiry.',
        '据《SAE 国家间协作论》改写，英文独立重写，简繁中文均为完整正文。散文选取论证与案例，不逐条翻译全部命题和附录。案例为虚构；制度条文展示一种选择，不是唯一最佳设计。提出追问、负有作答义务与强制执行分开；后来的政策变化，不自动归因为此前的追问。', conv, 'p')
    if item:
        links = '<p><a href="' + item['source_url'] + '">' + loc('Read the corresponding paper ↗', '阅读对应原论文 ↗', conv) + '</a></p>'
    else:
        links = '<p><a href="https://self-as-an-end.net/papers/sae-interstate-prequel.html">' + loc('Begin with the theoretical prequel ↗', '从理论前置篇进入 ↗', conv) + '</a></p>'
    return '<details class="lw-sources"><summary>' + loc('Source & reading note', '原论文与阅读说明', conv) + '</summary>' + note + links + '</details>'


def state_entry(conv):
    return '<!-- INTERSTATE STATE ENTRY START --><section class="state-group" id="interstate-cooperation"><p class="state-kicker">' + loc('A separate series · Nine complete essays', '独立系列 · 九篇完整散文', conv) + '</p>' + loc(*TITLE, conv, 'h2') + loc('From agreements and trust to sanctions, defence, receiving people and leaving. Nine complete readings on cooperation without a common superior; the real histories remain a separate companion.', '从约定与信任，读到制裁、防御、接纳与退出。九篇完整散文，探索不设共同上级的协作；真实历史另设伴读专题，不混入这条虚构主线。', conv, 'p', 'state-deck') + '<p class="state-return"><a href="../interstate/index.html">' + loc('Enter Interstate Cooperation →', '进入国家间协作论散文 →', conv) + '</a></p></section><!-- INTERSTATE STATE ENTRY END -->'


def library_card(conv):
    def ll(en, zh, tag='span', css=''):
        return loc(en, zh, conv, tag, css).replace('lang-zh', 'lang-zh cl-zh').replace('lang-hant', 'lang-zh cl-hant')
    return '<a href="essays/interstate/index.html" class="series-card"><span class="series-card-count">' + ll('Nine complete essays · EN / 简 / 繁', '九篇完整散文 · 英简繁') + '</span><div class="series-card-title-zh cl-zh">国家之间，谁来回答？</div><div class="series-card-title-zh cl-hant">國家之間，誰來回答？</div><div class="series-card-title-en">Between States, Who Answers?</div>' + ll(DECK[0], DECK[1], 'p', 'series-card-desc') + ll('Read all nine →', '阅读全部九篇 →', 'span', 'series-card-arrow') + '</a>'


def document(content, title, deck, filename, conv, items, item=None):
    result = page(content, title, deck, 'essays/interstate/' + filename, conv,
                  item['source_url'] if item else None, (BASE, TITLE[0]), publication_date=item.get('date', DATE) if item else DATE)
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', result, re.S)
    schema = json.loads(match[1])
    if not item:
        schema.update(datePublished=DATE, dateModified=COMPLETE_DATE, hasPart=[
            {'@type': 'Article', 'name': d['title_en'], 'url': BASE + d['slug'] + '.html'} for d in items])
    return (result[:match.start(1)] + json.dumps(schema, ensure_ascii=False).replace('</', '<\\/') + result[match.end(1):]).replace('</head>', '<link rel="stylesheet" href="reading.css?v=20261031"></head>')


def landing(items, conv):
    sections = []
    for key, en, zh, ids in GROUPS:
        cards = ''.join('<a class="lw-card" href="' + d['slug'] + '.html"><p class="lw-kicker">' + f'{d["id"]:02d}' + '</p>' + loc(d['title_en'], d['title_zh'], conv, 'h3') + loc(d['deck_en'], d['deck_zh'], conv, 'p') + loc('Read essay →', '阅读全文 →', conv, 'span', 'lw-read') + '</a>' for d in items if d['id'] in ids)
        sections.append('<section class="is-group" id="' + key + '">' + loc(en, zh, conv, 'h2') + '<div class="lw-grid">' + cards + '</div><a class="lw-read is-back" href="#reading-route">' + loc('↑ Back to reading route', '↑ 回到阅读导航', conv) + '</a></section>')
    jump = '<nav class="is-jump" id="reading-route" aria-label="Reading route">' + ''.join('<a href="#' + key + '">' + loc(en, zh, conv) + '</a>' for key, en, zh, ids in GROUPS) + '</nav>'
    content = '<main class="lw-wrap">' + breadcrumb(conv) + '<section class="lw-hero"><p class="lw-kicker">Non Dubito · ' + loc('Interstate Cooperation', '国家间协作论', conv) + '</p>' + loc(*TITLE, conv, 'h1') + loc(*DECK, conv, 'p', 'lw-deck lw-search-deck') + loc('Nine complete essays · English, Simplified & Traditional Chinese', '九篇完整散文 · 英文、简体中文与繁体中文', conv, 'p', 'lw-meta') + '</section>' + jump + notice(conv) + '<aside class="lw-opening">' + loc('No prerequisite reading. Follow all nine in order, or choose a question above. The State essays are an optional companion, not an entrance examination. The real histories have a separate entrance below.', '不用先读完国家论。可以按顺序读九篇，也可以从上面的一个问题进入。国家论可以放在旁边读，不是先修课；真实历史在下方另设入口。', conv, 'p') + '<a href="ep01.html">' + loc('Begin at the old customs house →', '从旧海关楼读起 →', conv) + '</a></aside>' + ''.join(sections) + source_note(conv) + related(conv) + '</main>'
    content = content.replace(source_note(conv), real_world_entry(conv) + source_note(conv), 1)
    return document(content, TITLE[0] + ' · 国家间协作论', DECK[0], 'index.html', conv, items)


def article(item, items, conv):
    bodies = ''.join('<div class="essay-body lw-prose lang-' + lang + '" lang="' + native + '">' + prose([conv.convert(p) for p in item['body_zh']] if lang == 'hant' else item['body_' + lang]) + '</div>' for lang, native in (('en', 'en'), ('zh', 'zh-Hans'), ('hant', 'zh-Hant')))
    nav = []
    for offset, en, zh in ((-1, 'Previous essay', '上一篇'), (1, 'Next essay', '下一篇')):
        index = item['id'] - 1 + offset
        if 0 <= index < len(items):
            d = items[index]
            nav.append('<a href="' + d['slug'] + '.html">' + loc(en, zh, conv, 'small') + loc(d['title_en'], d['title_zh'], conv) + '</a>')
        else:
            nav.append('<a href="index.html#reading-route">' + loc('Series & reading guide', '系列与阅读导航', conv, 'small') + loc(*TITLE, conv) + '</a>')
    date = item.get('date', DATE)
    content = '<main class="lw-wrap">' + breadcrumb(conv, True) + '<article class="lw-article"><div class="lw-head"><p class="lw-kicker">' + loc('Interstate Cooperation', '国家间协作论', conv) + ' · 0' + str(item['id']) + '</p>' + loc(item['title_en'], item['title_zh'], conv, 'h1') + loc(item['deck_en'], item['deck_zh'], conv, 'p', 'lw-deck lw-search-deck') + '<p class="lw-meta">Han Qin · <time datetime="' + date + '">' + date + '</time> · ' + loc('Reader essay · English independently written', '哲学散文 · 英文独立重写', conv) + '</p></div>' + notice(conv) + bodies + source_note(conv, item) + '<nav class="lw-series-nav" aria-label="Series navigation">' + ''.join(nav) + '</nav>' + related(conv) + '</article></main>'
    return document(content, item['title_en'], item['deck_en'], item['slug'] + '.html', conv, items, item)


def render():
    items = load_items()
    conv = InterstateTraditionalConverter()
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
            assert path.read_text() == text, f'Stale page: {path}'
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(('Checked' if args.check else 'Wrote') + ' Interstate Cooperation · nine essays · three complete modes')


if __name__ == '__main__':
    main()
