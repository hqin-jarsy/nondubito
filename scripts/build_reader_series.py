#!/usr/bin/env python3
"""Render reviewed reader essays, with three complete reading modes.

Only series listed in data/reader-series.json are published. Manuscript drafts
and proposed future series do not enter the public navigation automatically.
"""
from __future__ import annotations
import argparse
import html
import json
import re

from build_language_writing import ROOT, loc, page, prose
from build_long_consensus import ConsensusTraditionalConverter


class ReaderTraditionalConverter(ConsensusTraditionalConverter):
    def convert(self,text):
        result = super().convert(text)
        for old,new in (('啓','啟'),('面館','麵館'),('一碗面','一碗麵'),('下遊人','下游人'),
                        ('上遊資源','上游資源'),('下周','下週'),('上周','上週'),('松一點','鬆一點'),
                        ('幹脆','乾脆'),('咸麵包','鹹麵包'),('看得准','看得準'),('看准','看準'),
                        ('說不准','說不準'),('划了一句','劃了一句'),('燒制','燒製'),('界面','介面'),
                        ('面怎麼醒','麵怎麼醒'),('系好','繫好'),('划線','劃線'),('拿不准','拿不準'),
                        ('瞄准','瞄準'),('判准','判準'),('幾周','幾週'),('會系的鞋','會繫的鞋'),
                        ('土太松','土太鬆'),('樁腳松','樁腳鬆'),('松土','鬆土'),('這周','這週'),
                        ('余下','餘下'),('輓救','挽救'),('准入','準入')):
            result = result.replace(old,new)
        return result


def registry():
    path = ROOT/'data/reader-series.json'
    return json.loads(path.read_text())['series'] if path.exists() else []


def load_items(series):
    items = []
    for n in range(1, series['count']+1):
        item = json.loads((ROOT/f'data/{series["slug"]}/ep{n:02d}.json').read_text())
        assert item['id'] == n and item['slug'] == f'ep{n:02d}'
        assert item['source_url'].startswith('https://self-as-an-end.net/papers/')
        assert item['source_url'].endswith('.html')
        for lang in ('en','zh'):
            assert item[f'title_{lang}'].strip() and item[f'deck_{lang}'].strip()
            body = item[f'body_{lang}']
            assert len(body) >= 18
            assert all(isinstance(p,str) and p.strip() and '<' not in p for p in body)
            assert sum(p.startswith('## ') for p in body) <= 3
            text = '\n'.join(body)
            count = len(re.findall(r'[\u3400-\u9fff]',text)) if lang == 'zh' else len(text.split())
            assert count >= (1800 if lang == 'zh' else 1000), (series['slug'],n,lang,count)
            assert not re.search(r'\b\d{2}DD\b|\b[FTVH]\d+\b|ψ|ρ',text)
            if lang == 'en':
                assert not re.search(r'[\u3400-\u9fff]',text)
        review = item['review']
        assert review['status'] == 'approved'
        assert review['source_read_complete'] and review['zh_en_read_complete']
        assert review['traditional_review_complete']
        assert re.fullmatch(r'[a-f0-9]{64}',item['editorial']['source_sha256'])
        items.append(item)
    return items


def breadcrumb(s,conv,article=False):
    out = f'<nav class="lw-crumb" aria-label="Breadcrumb"><a href="../sae/index.html#{s["shelf"]}">{loc("SAE & Philosophy","SAE 与哲学",conv)}</a>'
    if article:
        out += '<span aria-hidden="true">/</span><a href="index.html">'+loc(s['en'],s['zh'],conv)+'</a>'
    return out+'</nav>'


def related(s,conv):
    links = []
    for target in s.get('related',[]):
        path,zh,en = target
        assert (ROOT/path).is_file(),f'Unpublished related target: {path}'
        links.append(f'<a href="../../{path}">{loc(en,zh,conv)}</a>')
    links.append('<a href="../sae/index.html">'+loc('SAE reading map','SAE 阅读地图',conv)+'</a>')
    return '<aside class="lw-related">'+loc('Keep exploring','继续读',conv,'h2')+''.join(links)+'</aside>'


def reading_note(s,conv,item=None):
    note = loc(s['note_en'],s['note_zh'],conv,'p')
    if item:
        note += f'<p><a href="{html.escape(item["source_url"],quote=True)}">'+loc('Read the source paper ↗','阅读原论文 ↗',conv)+'</a></p>'
        for ref in item.get('references',[]):
            assert ref['url'].startswith('https://')
            note += f'<p><a href="{html.escape(ref["url"],quote=True)}">'+loc(ref['en'],ref['zh'],conv)+' ↗</a></p>'
    return '<details class="lw-sources"><summary>'+loc('Source & reading note','原论文与阅读说明',conv)+'</summary>'+note+'</details>'


def landing(s,items,conv):
    cards = ''.join(f'<a class="lw-card" href="{i["slug"]}.html"><p class="lw-kicker">{i["id"]:02d}</p>{loc(i["title_en"],i["title_zh"],conv,"h2")}{loc(i["deck_en"],i["deck_zh"],conv,"p")}{loc("Read essay →","阅读全文 →",conv,"span","lw-read")}</a>' for i in items)
    content = '<main class="lw-wrap">'+breadcrumb(s,conv)+'<section class="lw-hero"><p class="lw-kicker">Non Dubito · SAE</p>'+loc(s['en'],s['zh'],conv,'h1')+loc(s['deck_en'],s['deck_zh'],conv,'p','lw-deck lw-search-deck')+loc(f'{s["count"]} complete essays · English, Simplified & Traditional Chinese',f'{s["count"]} 篇完整散文 · 英文、简体中文与繁体中文',conv,'p','lw-meta')+'</section><aside class="lw-opening">'+loc(s['opening_en'],s['opening_zh'],conv,'p')+'<a href="ep01.html">'+loc('Begin here →','从第一篇开始 →',conv)+'</a></aside><section class="lw-grid">'+cards+'</section>'+reading_note(s,conv)+related(s,conv)+'</main>'
    return page(content,s['en'],s['deck_en'],f'essays/{s["slug"]}/index.html',conv,publication_date=s['date'])


def article(s,item,items,conv):
    bodies = ''.join(f'<div class="essay-body lw-prose lang-{lang}" lang="{native}">{prose(item["body_hant"] if lang=="hant" else item["body_"+lang])}</div>' for lang,native in (('en','en'),('zh','zh-Hans'),('hant','zh-Hant')))
    neighbors = []
    for offset,en,zh in ((-1,'Previous essay','上一篇'),(1,'Next essay','下一篇')):
        n = item['id']-1+offset
        if 0 <= n < len(items):
            other = items[n]
            neighbors.append(f'<a href="{other["slug"]}.html">'+loc(en,zh,conv,'small')+loc(other['title_en'],other['title_zh'],conv)+'</a>')
        else:
            neighbors.append('<a href="index.html">'+loc('All essays','全部篇目',conv,'small')+loc(s['en'],s['zh'],conv)+'</a>')
    content = '<main class="lw-wrap">'+breadcrumb(s,conv,True)+'<article class="lw-article"><div class="lw-head"><p class="lw-kicker">'+loc(s['en'],s['zh'],conv)+f' · {item["id"]:02d}</p>'+loc(item['title_en'],item['title_zh'],conv,'h1')+loc(item['deck_en'],item['deck_zh'],conv,'p','lw-deck lw-search-deck')+f'<p class="lw-meta">Han Qin · <time datetime="{s["date"]}">{s["date"]}</time></p></div>'+bodies+reading_note(s,conv,item)+'<nav class="lw-series-nav" aria-label="Series navigation">'+''.join(neighbors)+'</nav>'+related(s,conv)+'</article></main>'
    return page(content,item['title_en'],item['deck_en'],f'essays/{s["slug"]}/{item["slug"]}.html',conv,item['source_url'],(f'https://nondubito.net/essays/{s["slug"]}/',s['en']),publication_date=s['date'])


def library_card(s,conv):
    # Match the series' reviewed Traditional typography even when the older
    # navigation builder supplies its own converter. Other cards stay untouched.
    own = ReaderTraditionalConverter()
    try:return _library_card(s,own)
    finally:own.close()


def _library_card(s,conv):
    def t(en,zh,tag='span',css=''):
        return loc(en,zh,conv,tag,css).replace('lang-zh','lang-zh cl-zh').replace('lang-hant','lang-zh cl-hant')
    return f'<a href="essays/{s["slug"]}/index.html" class="series-card"><span class="series-card-count">'+t(f'{s["count"]} essays · EN / 简 / 繁',f'{s["count"]} 篇 · 英 / 简 / 繁')+'</span><div class="series-card-title-zh cl-zh">'+html.escape(s['zh'])+'</div><div class="series-card-title-zh cl-hant">'+html.escape(conv.convert(s['zh']))+'</div><div class="series-card-title-en">'+html.escape(s['en'])+'</div>'+t(s['deck_en'],s['deck_zh'],'p','series-card-desc')+t('Read series →','阅读系列 →','span','series-card-arrow')+'</a>'


def render(slug=None):
    conv = ReaderTraditionalConverter()
    try:
        pages = {}
        for s in registry():
            if slug and s['slug'] != slug:
                continue
            items = load_items(s)
            pages[ROOT/f'essays/{s["slug"]}/index.html'] = landing(s,items,conv)
            pages.update({ROOT/f'essays/{s["slug"]}/{i["slug"]}.html':article(s,i,items,conv) for i in items})
        if slug:
            assert pages,f'Unregistered series: {slug}'
        return pages
    finally:
        conv.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series',nargs='?')
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    pages = render(args.series)
    for path,text in pages.items():
        if args.check:
            assert path.read_text() == text,f'Stale page: {path}'
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text)
    print(('Checked' if args.check else 'Wrote')+f' {len(pages)} reviewed reader pages · three complete editions')


if __name__ == '__main__':
    main()
