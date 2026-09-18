#!/usr/bin/env python3
"""Build the Western Philosophy shelf and the edited Montaigne series.

Checked-in editorial JSON is the publication source; rebuilding never reads or
changes the author's external manuscript directory. Local character conversion
is followed by editorial review, not used to shorten the Traditional edition.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from build_ai_work_series import shell_header, footer, tri
from import_fairy_tales import TraditionalConverter

ROOT = Path(__file__).resolve().parents[1]
SHELF = ROOT / 'essays/sae-western'
SERIES = ROOT / 'essays/sae-montaigne'
DATE = '2026-09-17'
LABEL = {'en': 'SAE and Montaigne’s Essays', 'zh': 'SAE蒙田随笔集'}
SOURCES = {
    'monloe': ('MONLOE — The Bordeaux Copy: scholarly introduction and editorial method', 'MONLOE：波尔多本的版本与编辑说明', 'https://montaigne.univ-tours.fr/essais-1588-exemplaire-bordeaux/'),
    'ii12': ('Montaigne, Essays II.12 — Apology for Raymond Sebond (1595 text)', '蒙田《随笔集》II.12：雷蒙·塞邦辩护（1595年本文字）', 'https://hyperessays.net/gournay/book/II/chapter/12/'),
    'iii2': ('Montaigne, Essays III.2 — Of Repentance (1595 text)', '蒙田《随笔集》III.2：论悔（1595年本文字）', 'https://hyperessays.net/gournay/book/III/chapter/2/'),
    'iii9': ('Montaigne, Essays III.9 — Of Vanity (1595 text)', '蒙田《随笔集》III.9：论虚妄（1595年本文字）', 'https://hyperessays.net/gournay/book/III/chapter/9/'),
    'artfl': ('University of Chicago — The Montaigne Project', '芝加哥大学：蒙田文本与影像资源', 'https://artfl-project.uchicago.edu/montaigne-project'),
    'office': ('MONLOE — Montaigne and the Parlement of Bordeaux', 'MONLOE：蒙田与波尔多高等法院的档案', 'https://www.bvh.univ-tours.fr/monloe/Arrets.asp'),
    'retreat': ('MONLOE — Inscriptions in Montaigne’s library', 'MONLOE：蒙田书房的铭文', 'https://www.bvh.univ-tours.fr/monloe/Inscriptions.asp'),
}
for leaf in ('0228', '0358v', '0432v', '0433'):
    SOURCES[leaf] = (f'University of Chicago / MONLOE — manuscript changes, leaf {leaf} (digital transcription)', f'芝加哥大学／MONLOE：叶面 {leaf} 手稿改动的数字转录', f'https://artfl-iiif.uchicago.edu/montaigne_manifests/annotation_json/annotation_{leaf}.json')
SOURCE_KEYS = {0: ['monloe', 'office', 'retreat', 'artfl'], 1: ['ii12', '0228', 'monloe'], 2: ['ii12'], 3: ['iii2', '0358v', 'monloe'], 4: ['iii9', '0432v', '0433', 'monloe'], 5: ['iii9', '0433', 'monloe']}


class Converter(TraditionalConverter):
    def convert(self, value: str) -> str:
        text = super().convert(value).replace('“', '「').replace('”', '」')
        for old, new in {
            '亞裡士多德': '亞里士多德', '反復': '反覆', '從頭髮明': '從頭發明',
            '尼採': '尼采', '想象': '想像', '拿不准': '拿不準',
            '乾完活': '幹完活', '它乾的事': '它幹的事', '外頭髮話': '外頭發話',
            '證明瞭蒙田': '證明了蒙田', '數得再准': '數得再準', '看准了': '看準了',
            '划': '劃',
        }.items():
            text = text.replace(old, new)
        return text


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def localized(value: dict, c: Converter, tag='span', css='') -> str:
    return tri(esc(value['en']), esc(value['zh']), esc(c.convert(value['zh'])), tag, css)


def words(en: str, zh: str, c: Converter, tag='span', css='') -> str:
    return localized({'en': en, 'zh': zh}, c, tag, css)


def load_copy() -> list[dict]:
    items = json.loads((ROOT / 'data/sae-montaigne.json').read_text(encoding='utf-8'))['entries']
    if [x['number'] for x in items] != list(range(6)):
        raise ValueError('Montaigne needs introduction 00 and essays 01–05')
    for item in items:
        if item['slug'] != ('intro' if not item['number'] else f"ep{item['number']:02d}"):
            raise ValueError('Unexpected Montaigne filename')
        for lang in ('zh', 'en'):
            copy = item[lang]
            if not copy['title'].strip() or not copy['deck'].strip() or not copy['notes']:
                raise ValueError('Missing title, deck or editorial note')
            paragraphs = [p for s in copy['sections'] for p in s['paragraphs']]
            if len(paragraphs) < 8 or any(not isinstance(p, str) or not p.strip() for p in paragraphs):
                raise ValueError('Incomplete prose')
            text = json.dumps(copy, ensure_ascii=False)
            if any(marker in text for marker in ('[VERIFY', 'TODO', 'PLACEHOLDER', '待核实')) or re.search(r'<\s*(?:script|iframe)', text, re.I):
                raise ValueError('Unfinished editorial text')
            if item['number'] and not copy.get('aside'):
                raise ValueError('Missing optional SAE marginal note')
    return items


def head(title: str, deck: str, relative: str, item: dict | None = None) -> str:
    url = 'https://nondubito.net/' + relative
    schema = {'@context': 'https://schema.org', '@type': 'Article' if item else 'CollectionPage', 'name': title, 'description': deck, 'url': url, 'inLanguage': ['en', 'zh-Hans', 'zh-Hant'], 'author': {'@type': 'Person', 'name': 'Han Qin (秦汉)'}, 'datePublished': DATE, 'dateModified': DATE}
    if item:
        schema.update({'headline': item['en']['title'], 'mainEntityOfPage': url, 'isPartOf': {'@type': 'CollectionPage', 'name': LABEL['en'], 'url': 'https://nondubito.net/essays/sae-montaigne/'}, 'citation': [SOURCES[k][2] for k in SOURCE_KEYS[item['number']]]})
    data = json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')
    return f'''<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(deck)}"><meta name="author" content="Han Qin (秦汉)">
<meta property="og:type" content="{'article' if item else 'website'}"><meta property="og:title" content="{esc(title)} — Non Dubito"><meta property="og:description" content="{esc(deck)}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary">
<link rel="canonical" href="{url}"><link rel="icon" type="image/svg+xml" href="../../favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;family=Noto+Serif+TC:wght@400;500;600&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="../../site-shell.css?v=20260905b"><link rel="stylesheet" href="../sae-western/western.css?v=20260917">
<script src="../sae-western/western.js?v=20260917b"></script><script type="application/ld+json">{data}</script>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script>
</head>'''


def shell(content: str, page_head: str) -> str:
    return '<!DOCTYPE html>\n<html lang="en" data-lang="en" data-editions="en zh zh-hant">' + page_head + '\n<body class="site-shell-page explicit-hant western-page">' + shell_header() + content + footer() + '</body></html>\n'


def crumbs(c: Converter, level: int) -> str:
    links = [f'<a href="../../library.html">{words("Library", "书架", c)}</a>', f'<a href="../../explore.html#sae">{words("SAE & Philosophy", "SAE与哲学", c)}</a>']
    if level:
        links.append(f'<a href="../sae-western/index.html">{words("SAE & Western Philosophy", "SAE西哲", c)}</a>')
    if level > 1:
        links.append(f'<a href="index.html">{localized(LABEL, c)}</a>')
    return '<nav class="western-crumbs" aria-label="Breadcrumb">' + '<span aria-hidden="true">/</span>'.join(links) + '</nav>'


def render_shelf(c: Converter) -> str:
    data = json.loads((ROOT / 'data/sae-western.json').read_text(encoding='utf-8'))
    cards = []
    for n, series in enumerate(data['series'], 1):
        cards.append(f'''<a class="western-book" href="../{series['slug']}/index.html"><p class="western-kicker">{n:02d} · {localized(series['author'], c)}</p>{localized(series['title'], c, 'h2')}{localized(series['question'], c, 'p', 'western-question')}{localized(series['description'], c, 'p')}{localized(series['count'], c, 'p', 'western-meta')}{words('Open series →', '进入系列 →', c, 'span', 'western-read')}</a>''')
    content = f'''<main class="western-wrap">{crumbs(c, 0)}<section class="western-hero"><p class="western-kicker">Non Dubito · {words('Four books, four conversations', '四部经典，四场对话', c)}</p>{localized(data['title'], c, 'h1')}{localized(data['deck'], c, 'p', 'western-deck western-search-deck')}{words('Choose a book or a question. No knowledge of SAE is required to begin.', '从一本书或一个问题进入；不必先学过 SAE。', c, 'p', 'western-meta')}</section><div class="western-book-grid">{''.join(cards)}</div><aside class="western-afterword">{words('Read each book on its own terms. The encounters matter as much for their disagreements as for what they share.', '先让每本书用自己的方式说话。彼此相遇之处值得读，不能互相代替的地方也一样。', c, 'p')}<a href="../sae-foundations/index.html">{words('Want to know more about SAE? Start with the foundations →', '想进一步了解 SAE？从基础系列进入 →', c)}</a></aside></main>'''
    return shell(content, head(data['title']['en'], data['deck']['en'], 'essays/sae-western/'))


def render_index(items: list[dict], c: Converter) -> str:
    deck = {'en': 'A question in place of a motto. A printed rule beside a changed sentence. An author returns to his own words, without claiming that his later self must know better.', 'zh': '一个问号被放进座右铭，一条印成了字的规矩旁边留下改动。蒙田回到自己写过的话前，却没有认定后来的自己一定更明白。'}
    cards = []
    for item in items:
        name = words('Introduction', '小引', c) if not item['number'] else f"{item['number']:02d}"
        cards.append(f'''<a class="western-entry" href="{item['slug']}.html"><span class="western-number">{name}</span><div>{localized({l: item[l]['title'] for l in ('en','zh')}, c, 'h2')}{localized({l: item[l]['deck'] for l in ('en','zh')}, c, 'p')}{words('Read →', '阅读全文 →', c, 'span', 'western-read')}</div></a>''')
    content = f'''<main class="western-wrap">{crumbs(c, 1)}<section class="western-hero"><p class="western-kicker">{words('SAE & Western Philosophy · Montaigne', 'SAE西哲 · 蒙田', c)}</p>{localized(LABEL, c, 'h1')}{words('Returning to What You Wrote', '回到自己写过的话前', c, 'p', 'western-subtitle')}{localized(deck, c, 'p', 'western-deck western-search-deck')}{words('Introduction + five essays · English, Simplified & Traditional Chinese', '一篇小引＋五篇正文 · 简体、繁体与独立英文版', c, 'p', 'western-meta')}<div class="western-actions"><a href="intro.html">{words('Begin with the book →', '先看这册书 →', c)}</a><a href="ep01.html">{words('Go straight to Essay 01', '直接读第一篇', c)}</a></div>{words('Each essay can be read on its own. Optional SAE notes follow the main text; sources and edition notes are also available below.', '各篇可以单独读。SAE旁注放在正文之后，可自行展开；文末另附版本说明与原文入口。', c, 'p', 'western-note')}</section><div class="western-entries">{''.join(cards)}</div><aside class="western-afterword"><a href="../sae-western/index.html">{words('← All Western Philosophy series', '← 回到 SAE西哲', c)}</a></aside></main>'''
    return shell(content, head(LABEL['en'], deck['en'], 'essays/sae-montaigne/'))


def render_article(item: dict, items: list[dict], c: Converter) -> str:
    body = []
    notes = []
    for key, css, lang in (('en','en','en'), ('zh','zh','zh-Hans'), ('zh','hant','zh-Hant')):
        copy = item[key]
        conv = c.convert if css == 'hant' else lambda s: s
        sections = []
        for s in copy['sections']:
            heading = f'<h2>{esc(conv(s["heading"]))}</h2>' if s['heading'] else ''
            paragraphs = ''.join('<p>' + esc(conv(p)).replace('\n','<br>') + '</p>' for p in s['paragraphs'])
            sections.append('<section>' + heading + paragraphs + '</section>')
        body.append(f'<div class="western-prose lang-{css}" lang="{lang}">' + '\n'.join(sections) + '</div>')
        notes.append(f'<div class="lang-{css}" lang="{lang}">' + ''.join(f'<p>{esc(conv(p))}</p>' for p in copy['notes']) + '</div>')
    aside = ''
    if item['number']:
        if item['number'] <= 2:
            further = '<a href="../sae-first-critique/index.html">' + words('Read the SAE First Critique essays →', '进入 SAE第一批判 →', c) + '</a>'
        else:
            further = '<a href="../meaning/index.html">' + words('The SAE essays on meaning →', '进入 SAE意义论 →', c) + '</a>'
        aside = '<details class="western-aside"><summary>' + words('Alongside SAE · an optional marginal note', '与SAE并读 · 可选旁注', c) + '</summary>' + localized({l:item[l]['aside'] for l in ('en','zh')}, c, 'p') + further + '</details>'
    sources = ''.join(f'<li><a href="{esc(SOURCES[k][2])}">{words(SOURCES[k][0], SOURCES[k][1], c)}</a></li>' for k in SOURCE_KEYS[item['number']])
    source_section = '<details class="western-sources"><summary>' + words('Text, editions & sources', '文本、版本与来源', c) + '</summary>' + ''.join(notes) + '<ul>' + sources + '</ul></details>'
    nav = []
    for n, en, zh in ((item['number']-1,'Previous','上一篇'),(item['number']+1,'Next','下一篇')):
        if 0 <= n < len(items):
            other = items[n]
            nav.append(f'<a href="{other["slug"]}.html">{words(en,zh,c,"small")}{localized({l:other[l]["title"] for l in ("en","zh")},c)}</a>')
        else:
            nav.append(f'<a href="index.html">{words("Series contents","系列目录",c,"small")}{localized(LABEL,c)}</a>')
    number = words('Introduction', '小引', c) if not item['number'] else f"{item['number']:02d} / 05"
    content = f'''<main class="western-wrap" data-search="Montaigne Essays 蒙田 随笔集 隨筆集 SAE西哲">{crumbs(c, 2)}<article class="western-article"><div class="western-article-head"><p class="western-kicker">{localized(LABEL,c)} · {number}</p>{localized({l:item[l]['title'] for l in ('en','zh')},c,'h1')}{localized({l:item[l]['deck'] for l in ('en','zh')},c,'p','western-deck western-search-deck')}<p class="western-meta">Han Qin ({words('秦汉','秦汉',c)}) · 2026</p></div>{''.join(body)}{aside}{source_section}<nav class="western-series-nav" aria-label="Series navigation">{''.join(nav)}</nav></article></main>'''
    return shell(content, head(item['en']['title'] + ' · Montaigne', item['en']['deck'], 'essays/sae-montaigne/' + item['slug'] + '.html', item))


def build() -> dict[Path, str]:
    items = load_copy()
    c = Converter()
    try:
        return {SHELF/'index.html': render_shelf(c), SERIES/'index.html': render_index(items,c), **{SERIES/(x['slug']+'.html'): render_article(x,items,c) for x in items}}
    finally:
        c.close()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    outputs = build()
    stale = [str(p.relative_to(ROOT)) for p, value in outputs.items() if not p.exists() or p.read_text(encoding='utf-8') != value]
    if args.check:
        if stale:
            raise SystemExit('Stale western philosophy pages: ' + ', '.join(stale))
        print(f'OK: {len(outputs)} Western Philosophy and Montaigne pages')
    else:
        for path, value in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding='utf-8')
        print(f'Wrote {len(outputs)} Western Philosophy and Montaigne pages')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
