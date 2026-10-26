#!/usr/bin/env python3
"""Build the standalone action special study and its bounded landing-page entry."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from build_ai_work_series import TraditionalConverter, shell_header, footer, tri
from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'essays/action'
DATA = ROOT / 'data/action/adversity.json'
URL = 'https://nondubito.net/essays/action/adversity.html'


class AdversityTraditionalConverter(TraditionalConverter):
    def convert(self, text: str) -> str:
        result = super().convert(text.replace('文件', '__ADV_DOCUMENT__').replace('默认', '__ADV_ASSENT__'))
        for old, new in (('__ADV_DOCUMENT__','文件'), ('__ADV_ASSENT__','默認'),
                         ('沈默','沉默'), ('反復','反覆'), ('髮現','發現'),
                         ('回復','回覆'), ('亞裡','亞里'),
                         ('公裡','公里'), ('那只手','那隻手'), ('多乾','多幹'),
                         ('乾活','幹活'), ('復述','複述'), ('克裡米亞','克里米亞'),
                         ('覈實','核實'), ('合伙','合夥'), ('一周','一週')):
            result = result.replace(old, new)
        return result


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def load_item() -> dict:
    item = json.loads(DATA.read_text())
    assert item['slug'] == 'adversity'
    assert item['source_url'] == 'https://self-as-an-end.net/papers/sae-action-adversity.html'
    assert re.fullmatch(r'[0-9a-f]{64}', item['source_sha256'])
    for language in ('zh','en'):
        paragraphs = item['body_' + language]
        assert len(paragraphs) >= 30
        assert sum(p.startswith('## ') for p in paragraphs) == 3
        assert all('<' not in p and not p.startswith('###') for p in paragraphs)
        text = '\n'.join(paragraphs)
        assert not re.search(r'\bD\d{1,3}\b|\b\d{2}DD\b', text)
        assert len(re.findall(r'[\u3400-\u9fff]',text)) >= 3000 if language == 'zh' else len(text.split()) >= 1600
    return item


@tracked_html
def render_article(item: dict, converter: TraditionalConverter) -> str:
    def loc(en, zh, tag='span', css=''):
        return tri(esc(en), esc(zh), esc(converter.convert(zh)), tag, css)

    bodies = []
    for code, native in (('en','en'), ('zh','zh-Hans'), ('hant','zh-Hant')):
        paragraphs = item['body_en' if code == 'en' else 'body_zh']
        if code == 'hant':
            paragraphs = [converter.convert(p) for p in paragraphs]
        body = '\n'.join(f'<h2>{esc(p[3:])}</h2>' if p.startswith('## ') else f'<p>{esc(p)}</p>' for p in paragraphs)
        bodies.append(f'<div class="essay-body adversity-prose lang-{code}" lang="{native}">{body}</div>')
    schema = {'@context':'https://schema.org','@type':'Article','headline':item['title_en'],
              'description':item['deck_en'],'url':URL,'mainEntityOfPage':URL,
              'inLanguage':['en','zh-Hans','zh-Hant'], 'datePublished':item['date'],'dateModified':item['date'],
              'author':{'@type':'Person','name':'Han Qin (秦汉)'},'citation':item['source_url'],
              'isPartOf':{'@type':'CollectionPage','name':'SAE Action Theory','url':'https://nondubito.net/essays/action/'}}
    title = esc(item['title_en'] + ' / ' + item['title_zh'])
    deck = esc(item['deck_zh'] + ' ' + item['deck_en'])
    head = f'''<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} — Non Dubito</title><meta name="description" content="{deck}"><meta name="author" content="Han Qin (秦汉)">
<meta property="og:type" content="article"><meta property="og:title" content="{title}"><meta property="og:description" content="{deck}"><meta property="og:url" content="{URL}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary">
<link rel="canonical" href="{URL}"><link rel="icon" type="image/svg+xml" href="../../favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;family=Noto+Serif+TC:wght@400;500;600&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="../../site-shell.css?v=20260905b"><link rel="stylesheet" href="adversity.css?v=20261026">
<script src="../../site-shell.js?v=20260905b"></script><script defer src="adversity.js?v=20261026"></script><script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script></head>'''
    header = shell_header().replace('data-site-shell-menu aria-controls', 'data-site-shell-menu aria-label="Menu" aria-controls')
    for code, label in (('en','English'), ('zh','简体中文'), ('zh-hant','繁體中文')):
        header = header.replace(f'data-set-language="{code}"', f'data-set-language="{code}" aria-label="{label}"')
    content = f'''<main class="adversity-wrap"><nav class="adversity-breadcrumbs" aria-label="Breadcrumb"><a href="../../explore.html#sae">{loc('SAE · Philosophy','SAE · 哲学')}</a><span aria-hidden="true">/</span><a href="index.html">{loc('Action Theory','行动论')}</a></nav>
<article class="adversity-article" data-search="逆境 逆境专论 逆境專論 那条路走不通以后 adversity action theory purpose persistence stopping">
<div class="adversity-head"><p class="adversity-kicker">{loc('SAE Action Theory · Special study · Can be read on its own','SAE 行动论 · 逆境专论 · 可独立阅读')}</p>{loc(item['title_en'],item['title_zh'],'h1')}{loc(item['deck_en'],item['deck_zh'],'p','adversity-deck adversity-search-deck')}<p class="adversity-meta">Han Qin ({loc('秦汉','秦汉')}) · <time datetime="{item['date']}">{item['date']}</time></p></div>
{''.join(bodies)}
<details class="adversity-sources"><summary>{loc('Source & reading note','来源与阅读说明')}</summary>{loc('A reader essay based on Adversity, the special study in SAE Action Theory; English is independently written. It returns to the report-maker in the original series without extending its numbered sequence. It does not prescribe endurance, diagnose distress or promise that hardship produces growth. The paper’s discussion excludes the extremity in which a person cannot sustain themself.','本文据《SAE 行动论》专论《逆境》写成，英文独立重写。故事回到原系列中做报表的那个人，不延长九篇正文的编号。它不规定人应当忍多久，不诊断痛苦，也不保证苦难使人成长。论文讨论的范围不包括连自身维持都保不住的绝境。','p')}<p><a href="{item['source_url']}">{loc('Adversity · source paper ↗','逆境 · 原论文 ↗')}</a> · <a href="https://doi.org/{item['source_doi']}">DOI: {item['source_doi']}</a></p>
{loc('The two historical examples are checked against the autobiographies and letters below; they concern recorded acts, not complete judgments of the people. Other historical examples in the paper are deliberately not reproduced here.','文中两处史例据下列自传与书信核对；说的是有记录的事，不给人物作完整断语。论文中的其余史例没有逐一搬入本文。','p')}
<p><a href="https://www.gutenberg.org/cache/epub/23031/pg23031-images.html">Mary Seacole · Wonderful Adventures · Chapter VIII ↗</a><br><a href="https://www.gutenberg.org/files/2397/2397-h/2397-h.htm">Anne Sullivan · Letter of April 10, 1887 · The Story of My Life ↗</a></p></details>
<aside class="adversity-related">{loc('Continue reading','继续阅读','h2')}<a href="index.html">{loc('← The original eleven-essay route','← 回到原有十一篇主线')}</a><a href="ep07.html">{loc('I Will Not Write That Name','这个名字我不写')}</a><a href="ep04.html">{loc('The Email He Never Sent','那封邮件没有发出去')}</a><a href="../meaning/index.html">{loc('On meaning','意义论')}</a></aside>
</article></main>'''
    foot = footer()
    for en, zh in (('Explore','探索'), ('Library','书架'), ('SAE Theory ↗','SAE 理论 ↗')):
        foot = foot.replace('>' + en + '</a>', '>' + loc(en,zh) + '</a>')
    return '<!DOCTYPE html>\n<html lang="en" data-lang="en" data-editions="en zh zh-hant">' + head + '<body class="site-shell-page explicit-hant adversity-page">' + header + content + foot + '</body></html>\n'


def index_entries(item: dict, converter: TraditionalConverter) -> tuple[list[str],dict]:
    pairs = [
        ('New special study · Adversity · Read independently','新增专论 · 逆境 · 可独立阅读'),
        (item['title_en'],item['title_zh']), (item['deck_en'],item['deck_zh']),
        ('The original eleven essays remain a complete route below. This separate essay returns to the difficult years in that story; it is not a tenth numbered chapter.','下面原有十一篇仍是一条完整路线。本篇单独回到故事里那几年的难处，不另接成第十篇正文。'),
        ('Read the special study →','阅读逆境专论 →')]
    entries = []
    for n,code in enumerate(('EN','ZH')):
        def block(i, tag, css=''):
            attr = f' class="{css}"' if css else ''
            return f'<{tag}{attr}>{esc(pairs[i][n])}</{tag}>'
        entries.append(f'<!-- ACTION ADVERSITY {code} START -->\n<section class="adversity-entry">' + block(0,'p','adversity-kicker') + block(1,'h2') + block(2,'p') + block(3,'p') + '<a href="adversity.html">' + block(4,'span') + f'</a></section>\n<!-- ACTION ADVERSITY {code} END -->\n')
    return entries, {zh:converter.convert(zh) for en,zh in pairs}


def render() -> dict[Path,str]:
    item = load_item()
    converter = AdversityTraditionalConverter()
    try:
        entries, variants = index_entries(item,converter)
        index_path = TARGET / 'index.html'
        index = index_path.read_text()
        # Keep the main series title and introduction first. Each language gets
        # its own special-study entry before the unchanged eleven-item route.
        index = re.sub(r'<!-- ACTION ADVERSITY(?: EN| ZH)? START -->.*?<!-- ACTION ADVERSITY(?: EN| ZH)? END -->\n?', '',index,flags=re.S)
        parts = index.split('<div class="entry-list">')
        assert len(parts) == 3
        index = parts[0] + entries[0] + '<div class="entry-list">' + parts[1] + entries[1] + '<div class="entry-list">' + parts[2]
        if 'href="adversity.css?v=20261026"' not in index:
            index = index.replace('<link rel="icon"', '<link rel="stylesheet" href="adversity.css?v=20261026"><link rel="icon"',1)
        suffix = ' 另有可独立阅读的逆境专论《那条路走不通以后》。 Also includes the standalone special study When That Way Is Closed.'
        def description(match):
            value = match[2]
            return match[1] + value + ('' if suffix in value else suffix) + match[3]
        index = re.sub(r'(<meta (?:name="description"|property="og:description") content=")(.*?)(">)',description,index)
        js_path = TARGET / 'zh-hant-data/index.js'
        js = js_path.read_text()
        match = re.search(r'  var variants = (\{.*?\});',js)
        assert match
        old_variants = json.loads(match[1])
        old_variants.update(variants)
        js = js[:match.start(1)] + json.dumps(old_variants,ensure_ascii=False) + js[match.end(1):]
        return {TARGET/'adversity.html':render_article(item,converter),index_path:index,js_path:js}
    finally:
        converter.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    for path, text in render().items():
        if args.check:
            if path.read_text() != text:
                raise ValueError(f'Stale output: {path.relative_to(ROOT)}')
        else:
            path.write_text(text,encoding='utf-8')
    print(('Checked' if args.check else 'Wrote') + ' adversity essay, separate series entry and Traditional landing map')


if __name__ == '__main__':
    main()
