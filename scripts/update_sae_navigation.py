#!/usr/bin/env python3
"""Regroup existing SAE cards without rewriting them or moving article URLs."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from build_language_writing import WritingTraditionalConverter, loc
from build_accountability import library_card
from build_long_consensus import library_card as consensus_card
from build_interstate import library_card as interstate_card
from build_marriage_series import library_card as marriage_card

ROOT = Path(__file__).resolve().parents[1]
CARD = re.compile(r'<a\b(?=[^>]*\bclass="series-card")[^>]*>.*?</a>',re.S)


def library_block(source):
    category = source.index('<span class="lib-section-tag">Category 02</span>')
    start = source.rfind('<section ',0,category)
    end = source.index('</section>',category)+len('</section>')
    return start,end,source[start:end]


def tri_library(en,zh,conv,tag='span',css=''):
    return loc(en,zh,conv,tag,css).replace('lang-zh','lang-zh cl-zh').replace('lang-hant','lang-zh cl-hant')


def render_library(source,groups,conv):
    start,end,old = library_block(source)
    cards = {re.search(r'href="([^"]+)"',m[0])[1]:m[0] for m in CARD.finditer(old)}
    cards['essays/interstate/index.html'] = interstate_card(conv)
    cards['essays/marriage/index.html'] = marriage_card(conv)
    accountability_path='essays/accountability/index.html'
    if accountability_path not in cards:
        cards[accountability_path]=library_card(conv)
    consensus_path='essays/long-consensus/index.html'
    if consensus_path not in cards:
        cards[consensus_path]=consensus_card(conv)
    path = 'essays/language-writing/index.html'
    if path not in cards:
        cards[path] = f'<a href="{path}" class="series-card"><span class="series-card-count">{tri_library("3 essays · English & both Chinese scripts","3 篇 · 英文与简繁中文",conv)}</span><div class="series-card-title-zh cl-zh">语言与写作：把话说成自己的</div><div class="series-card-title-zh cl-hant">語言與寫作：把話說成自己的</div><div class="series-card-title-en">Language &amp; Writing: Finding Words of Our Own</div>{tri_library("Naming, words that still feel wrong, and a writer’s growing voice: three complete reader essays, with independent English rewrites.","命名、总觉得没说对的话，以及写着写着长出来的声音。三篇完整散文，英文独立重写。",conv,"p","series-card-desc")}{tri_library("Read series →","阅读系列 →",conv,"span","series-card-arrow")}</a>'
    mapped = [item[0] for group in groups for item in group['items'] if item[0] in cards]
    assert len(mapped) == len(set(mapped)) == len(cards), 'Reading map must retain every Category 02 series exactly once'
    jump = ''.join(f'<a href="#sae-{g["id"]}">{tri_library(g["en"],g["zh"],conv)}</a>' for g in groups)
    contents = []
    for i,g in enumerate(groups,1):
        local = [cards[item[0]] for item in g['items'] if item[0] in cards]
        note = ''
        if g['id'] == 'traditions':
            note = f'<p class="sae-library-note">{tri_library("Western philosophy and the Chinese classics keep their topic shelves; the reading map brings their entrances together.","西哲与中国经典仍保留原有专题；阅读地图把这些入口放在一起。",conv)} <a href="essays/sae/index.html#traditions">{tri_library("See the encounters →","去看对读入口 →",conv)}</a></p>'
        contents.append(f'<div class="sae-library-group" id="sae-{g["id"]}">{tri_library("0"+str(i)+" · "+g["en"],"0"+str(i)+" · "+g["zh"],conv,"h2")}{tri_library(g["question_en"],g["question_zh"],conv,"p","sae-library-question")}<div class="series-grid">'+ '\n'.join(local)+f'</div>{note}<a class="sae-library-back" href="#sae-theory">{tri_library("↑ Back to SAE shelves","↑ 回到 SAE 分组",conv)}</a></div>')
    block = f'''<section class="lib-section" id="sae-theory"><div class="lib-section-header"><span class="lib-section-tag">Category 02</span><a href="essays/sae/index.html" class="lib-section-name" style="text-decoration:none"><span class="zh cl-zh">SAE 散文</span><span class="zh cl-hant">SAE 散文</span><span class="en">SAE Reader Essays</span></a>{tri_library("Choose a question, not a syllabus. Six groups keep the complete series list easy to browse; the reading map offers a lighter way in.","先选一个问题，不必把全目录当成课程表。这里按六组保留完整系列；想轻一点地开始，可以先看阅读地图。",conv,"p","lib-section-desc")}<p class="sae-library-map"><a href="essays/sae/index.html">{tri_library("Open the SAE reading map →","打开 SAE 散文阅读地图 →",conv)}</a></p></div><nav class="sae-library-jump" aria-label="SAE reading groups">{jump}</nav>{''.join(contents)}</section>'''
    return source[:start]+block+source[end:]


def render_explore(source,groups,conv):
    start = source.index('<section class="domain-section" id="sae">')
    end = source.index('</section>',start)+len('</section>')
    block = source[start:end]
    grid_start = block.index('<div class="shelf-grid">')+len('<div class="shelf-grid">')
    grid_end = block.index('</div><a class="domain-begin"',grid_start)
    cards = ''.join(f'<a class="shelf-link" href="essays/sae/index.html#{g["id"]}"><span class="shelf-label">0{i}</span>{loc(g["en"],g["zh"],conv,"h3")}{loc(g["question_en"],g["question_zh"],conv,"p")}<span class="shelf-arrow">→</span></a>' for i,g in enumerate(groups,1))
    block = block[:grid_start]+cards+block[grid_end:]
    # One explicit all-shelves link, separate from the novice's Start Here path.
    marker = '<p class="sae-map-link">'
    if marker not in block:
        block = block.replace('<div><div class="shelf-grid">',f'<div><p class="sae-map-link"><a href="essays/sae/index.html">{loc("Open the full SAE reading map →","打开 SAE 散文阅读地图 →",conv)}</a></p><div class="shelf-grid">',1)
    return source[:start]+block+source[end:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    groups = json.loads((ROOT/'data/sae-reading-map.json').read_text())['groups']
    conv = WritingTraditionalConverter()
    try:
        for filename,renderer in (('library.html',render_library),('explore.html',render_explore)):
            path = ROOT/filename
            source = path.read_text()
            result = renderer(source,groups,conv)
            if args.check:
                assert source == result, f'Stale navigation: {filename}'
            else:
                path.write_text(result)
    finally:
        conv.close()
    print(('Checked' if args.check else 'Regrouped')+' SAE navigation · no article moves')


if __name__ == '__main__':
    main()
