#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the affirmative theoretical main line alongside unchanged real cases."""
from __future__ import annotations

import argparse
import json
import re

from build_language_writing import page, prose
from build_political_economy import ROOT, DATE, loc, PoliticalTraditionalConverter, load_items as load_cases
from political_economy_routes import theory_data

TARGET = ROOT / 'essays/political-economy/theory'
DATA = ROOT / 'data/political-economy/theory'
BASE = 'https://nondubito.net/essays/political-economy/theory/'
TITLE = ('Understanding SAE Political Economy', '读懂 SAE 政治经济学')
DECK = ('Eight reader essays explain accumulation, chokepoints, checks, conversion, growth and support. Start with the argument, then take it into the real cases.',
        '八篇散文，讲清积累、关口、制衡、兑换、增长与支持。从主张和理由读起，再带回真实案例里。')
PARTS = ('prequel', '1', '2', '3', '4', '5', '6', '0')


class TheoryTraditionalConverter(PoliticalTraditionalConverter):
    def convert(self, text):
        return super().convert(text).replace('合伙', '合夥')


def counts(d):
    return {'zh_han':len(re.findall(r'[\u3400-\u9fff]', ''.join(d['body_zh']))),
            'en_words':len(' '.join(d['body_en']).split())}


def load_items():
    cases = {d['slug'] for d in load_cases()}
    items = []
    for i, part in enumerate(PARTS, 1):
        d = theory_data(f'ep{i:02d}')
        assert (d['id'], d['slug'], d['source_part'], d['date']) == (i, f'ep{i:02d}', part, DATE)
        assert d['source_url'] == f'https://self-as-an-end.net/papers/sae-political-economy-{part}.html'
        assert set(d['case_slugs']) <= cases
        for lang in ('zh', 'en'):
            for key in ('title', 'deck', 'takeaway'):
                assert d[key + '_' + lang].strip()
            body = d['body_' + lang]
            assert len(body) >= 23 and sum(p.startswith('## ') for p in body) >= 3, d['slug']
            assert all(p.strip() and '<' not in p and not re.search(r'\[[^]]+\]\(', p) for p in body)
            assert not re.search(r'\b\d{2}DD\b|\b[EFGZ]\d+\b||turn\d+(?:view|search)', '\n'.join(body))
        n = counts(d)
        assert n['zh_han'] >= 2300 and n['en_words'] >= 1400, (d['slug'], n)
        assert not re.search(r'[\u3400-\u9fff]', ''.join(d['body_en']))
        items.append(d)
    return items


def crumb(conv, article=False):
    result = '<nav class="lw-crumb" aria-label="Breadcrumb"><a href="../index.html">' + loc('Money, Power, and Room to Move', '钱、权力与我们的路', conv) + '</a>'
    if article:
        result += '<span aria-hidden="true">/</span><a href="index.html">' + loc('The theoretical reading path', '理论导读路线', conv) + '</a>'
    return result + '</nav>'


def document(content, title, deck, filename, conv, items, item=None):
    # The shared shell is based two levels down. Adjust only the empty frame,
    # never authored content links, for this three-level nested collection.
    frame = page('__PE_THEORY_CONTENT__', title, deck,
                 'essays/political-economy/theory/' + filename, conv,
                 item['source_url'] if item else None, (BASE, TITLE[0]), publication_date=DATE)
    frame = re.sub(r'((?:href|src)=["\'])(\.\./)', r'\1../\2', frame)
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', frame, re.S)
    schema = json.loads(match[1])
    schema.update(datePublished=DATE, dateModified=DATE)
    if not item:
        schema['hasPart'] = [{'@type':'Article', 'name':d['title_en'], 'url':BASE + d['slug'] + '.html'} for d in items]
        schema['isPartOf'] = {'@type':'CollectionPage', 'name':'Money, Power, and Room to Move', 'url':BASE.removesuffix('theory/')}
    frame = frame[:match.start(1)] + json.dumps(schema, ensure_ascii=False).replace('</', '<\\/') + frame[match.end(1):]
    frame = frame.replace('</head>', '<link rel="stylesheet" href="../../state-transitions/reading.css?v=20261029"></head>')
    return frame.replace('__PE_THEORY_CONTENT__', content)


def source_note(conv, d=None):
    note = loc('These are reader adaptations of eight SAE papers, not their complete technical translations. The argument and principal examples are retained; English is independently written and both Chinese scripts are complete. Crossways, Bluekiln and the other recurring institutions belong to the papers’ fictional world. Real cases are a separate companion route. Normative positions are not statements of current law.',
               '本组由八篇 SAE 论文改写为读者散文，不是技术论文的逐段译本；保留主要论证与具体例子，英文独立重写，简繁中文均为全文。通衢、青窑等贯穿场景属于论文的虚构世界，真实案例另作伴读。规范主张不当作现行法律陈述。', conv, 'p')
    if d:
        note += '<p><a href="' + d['source_url'] + '">' + loc('Read the corresponding original paper ↗', '深入阅读：对应原论文 ↗', conv) + '</a></p>'
    else:
        note += loc('Read essays 1–7 as the main line; essay 8 is optional dialogue with the tradition. You need not complete it before returning to the cases.', '第一至第七篇是主线，第八篇是与思想传统对读的选读；不必读完理论深潜才回到案例。', conv, 'p')
    return '<details class="lw-sources"><summary>' + loc('Sources & reading note', '来源与阅读说明', conv) + '</summary>' + note + '</details>'


def landing(items, conv):
    def featured(d, kicker, link):
        return '<aside class="lw-opening"><p class="lw-kicker">' + loc(*kicker, conv) + '</p>' + loc(d['title_en'], d['title_zh'], conv, 'h2') + loc(d['deck_en'], d['deck_zh'], conv, 'p') + '<a href="' + d['slug'] + '.html">' + loc(*link, conv) + '</a></aside>'
    cards = ''.join('<a class="lw-card" href="' + d['slug'] + '.html"><p class="lw-kicker">' + f'{d["id"]:02d}' + '</p>' + loc(d['title_en'], d['title_zh'], conv, 'h2') + loc(d['deck_en'], d['deck_zh'], conv, 'p') + loc('Read essay →', '阅读全文 →', conv, 'span', 'lw-read') + '</a>' for d in items[1:7])
    content = '<main class="lw-wrap">' + crumb(conv) + '<section class="lw-hero"><p class="lw-kicker">Non Dubito · SAE Political Economy</p>' + loc(*TITLE, conv, 'h1') + loc(*DECK, conv, 'p', 'lw-deck lw-search-deck') + loc('Seven main readings + one optional deeper reading · EN / 简 / 繁', '七篇主线＋一篇选读深潜 · 英文、简体中文与繁体中文', conv, 'p', 'lw-meta') + '</section>'
    content += featured(items[0], ('01 · Start here', '01 · 从这里开始'), ('Read the introduction →', '先读总导读 →'))
    content += '<section class="lw-grid" aria-label="Six core readings">' + cards + '</section>'
    content += featured(items[7], ('08 · Optional deeper reading', '08 · 理论深潜，选读'), ('Open the dialogue →', '进入思想对读 →'))
    content += '<aside class="lw-related">' + loc('Take the argument into the world', '带着理论回到现实', conv, 'h2') + loc('The real cases retain their evidence, uncertainties and different outcomes. They can test or complicate a principle, not merely illustrate a predetermined verdict.', '真实案例保留证据、未知与不同结局。它们可以检验、追问理论，不只是替预定判词作插图。', conv, 'p') + '<a href="../index.html#cases">' + loc('Browse the eight real cases →', '去读八篇真实案例 →', conv) + '</a><a href="../../sae/index.html#shared-life">' + loc('Shared life & institutions →', '共同生活与制度 →', conv) + '</a></aside>' + source_note(conv) + '</main>'
    return document(content, TITLE[0], DECK[0], 'index.html', conv, items)


def article(d, items, conv, cases):
    bodies = ''.join('<div class="essay-body lw-prose lang-' + lang + '" lang="' + native + '">' + prose([conv.convert(p) for p in d['body_zh']] if lang == 'hant' else d['body_' + lang]) + '</div>' for lang, native in (('en','en'), ('zh','zh-Hans'), ('hant','zh-Hant')))
    companion = '<aside class="lw-related pe-case-companion">' + loc('Read alongside the argument', '把真实案例放在旁边读', conv, 'h2') + loc('These documented cases raise related questions; their facts and legal outcomes remain distinct from the fictional examples above.', '以下真实案例提出相邻问题；其事实和法律结论，不与上文虚构场景混同。', conv, 'p')
    companion += ''.join('<a href="../' + slug + '.html">' + loc(cases[slug]['title_en'], cases[slug]['title_zh'], conv) + '</a>' for slug in d['case_slugs']) + '</aside>'
    nav = ''
    for offset, en, zh in ((-1,'Previous essay','上一篇'), (1,'Next essay','下一篇')):
        pos = d['id'] - 1 + offset
        other = items[pos] if 0 <= pos < len(items) else None
        if other:
            nav += '<a href="' + other['slug'] + '.html">' + loc(en, zh, conv, 'small') + loc(other['title_en'], other['title_zh'], conv) + '</a>'
        else:
            nav += '<a href="index.html">' + loc('The complete reading path', '完整阅读路线', conv) + '</a>'
    # Keep the closing principle compact and explicit; not another summary essay.
    takeaway = '<aside class="lw-note pe-takeaway">' + loc('The argument to take away', '读到这里，带走这一句', conv, 'h2') + loc(d['takeaway_en'], d['takeaway_zh'], conv, 'p') + '</aside>'
    content = '<main class="lw-wrap">' + crumb(conv, True) + '<article class="lw-article"><div class="lw-head"><p class="lw-kicker">' + loc('SAE Political Economy · ' + ('Optional deeper reading' if d['id'] == 8 else 'Theoretical reading') + f' {d["id"]:02d}', 'SAE 政治经济学 · ' + ('选读深潜' if d['id'] == 8 else '理论导读') + f' {d["id"]:02d}', conv) + '</p>' + loc(d['title_en'], d['title_zh'], conv, 'h1') + loc(d['deck_en'], d['deck_zh'], conv, 'p', 'lw-deck lw-search-deck') + '<p class="lw-meta">Han Qin · <time datetime="' + DATE + '">' + DATE + '</time> · ' + loc('English independently written', '英文独立重写', conv) + '</p></div>' + bodies + takeaway + companion + source_note(conv, d) + '<nav class="lw-series-nav" aria-label="Series navigation">' + nav + '</nav></article></main>'
    return document(content, d['title_en'], d['deck_en'], d['slug'] + '.html', conv, items, d)


def render():
    items = load_items()
    cases = {d['slug']:d for d in load_cases()}
    conv = TheoryTraditionalConverter()
    try:
        pages = {TARGET/'index.html':landing(items, conv), **{TARGET/(d['slug'] + '.html'):article(d, items, conv, cases) for d in items}}
        multilingual = ROOT/'data/political-economy-theory/multilingual/profile.json'
        if multilingual.exists():
            from full_series_languages import upgrade_primary
            pages = {path:upgrade_primary(text, 'political-economy-theory', path.stem)
                     for path,text in pages.items()}
        return pages
    finally:
        conv.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    for path, text in render().items():
        if args.check:
            assert path.read_text() == text, f'Stale theory page: {path}'
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(('Checked' if args.check else 'Wrote') + ' eight complete political economy reader essays + theory index')


if __name__ == '__main__':
    main()
