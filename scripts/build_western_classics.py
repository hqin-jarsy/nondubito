#!/usr/bin/env python3
"""Build complete trilingual Descartes and Spinoza readings from editorial JSON."""
import argparse
import html
import json
import re
from pathlib import Path

import build_sae_western as shared

ROOT = shared.ROOT
DATE = '2026-10-03'

class Converter(shared.Converter):
    def convert(self, value):
        text = super().convert(value)
        for old,new in {'分明瞭嗎':'分明了嗎', '講明瞭':'講明了', '說明瞭':'說明了',
                        '注明瞭':'註明了', '替自己乾活':'替自己幹活', '意思乾的':'意思幹的',
                        '准下雨':'準下雨', '對不太准':'對不太準'}.items():
            text = text.replace(old,new)
        return text

SERIES = {
    'sae-descartes': {
        'title': {'zh': 'SAE笛卡尔沉思集', 'en': 'SAE and Descartes’ Meditations'},
        'author': {'zh': '笛卡尔', 'en': 'René Descartes'},
        'deck': {'zh': '反对是他自己请来的。六篇正文，沿着反驳、答辩与不同版本，读一个人怎样接受检验，又怎样报告自己的胜利。', 'en': 'He invited the objections himself. Six essays follow the arguments, replies, and changing editions of a book whose author put his critics between its covers.'},
        'count': 7,
    },
    'sae-spinoza': {
        'title': {'zh': 'SAE斯宾诺莎伦理学', 'en': 'SAE and Spinoza’s Ethics'},
        'author': {'zh': '斯宾诺莎', 'en': 'Baruch Spinoza'},
        'deck': {'zh': '一部从定义推起的书，作者在哪些地方重新开口？十篇正文，从那个“我理解为”读到附释、情感与自由。', 'en': 'A book built from definitions and proofs still has someone speaking inside it. Ten essays listen for that voice—in the definitions, the scholia, and the difficult passage toward freedom.'},
        'count': 11,
    },
}

def load(slug):
    paths = sorted((ROOT/'data'/slug).glob('[0-9][0-9].json'))
    items = [json.loads(p.read_text()) for p in paths]
    assert [i['number'] for i in items] == list(range(SERIES[slug]['count']))
    for i in items:
        assert i['slug'] == ('intro' if i['number'] == 0 else f'ep{i["number"]:02}')
        for lang in ('zh', 'en'):
            copy = i[lang]
            assert all(copy.get(k) for k in ('title', 'deck', 'sections', 'notes'))
            assert all(s['paragraphs'] for s in copy['sections'])
            assert all(isinstance(p, str) and p.strip() for s in copy['sections'] for p in s['paragraphs'])
        assert i['sources'] and i['editorial']['coverage']
        assert bool(i['zh'].get('aside')) == bool(i['en'].get('aside'))
    return items

def header(slug, title, deck, filename, sources=None):
    relative = f'essays/{slug}/' + filename
    page = shared.head(title, deck, relative)
    schema = {
        '@context': 'https://schema.org', '@type': 'Article' if filename else 'CollectionPage',
        'name': title, 'description': deck, 'url': 'https://nondubito.net/'+relative,
        'inLanguage': ['en', 'zh-Hans', 'zh-Hant'],
        'author': {'@type': 'Person', 'name': 'Han Qin (秦汉)'},
        'datePublished': DATE, 'dateModified': DATE,
    }
    if filename:
        schema.update(headline=title, mainEntityOfPage=schema['url'],
            isPartOf={'@type':'CollectionPage', 'name':SERIES[slug]['title']['en'], 'url':f'https://nondubito.net/essays/{slug}/'},
            citation=[s['url'] for s in sources])
    page = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">'+json.dumps(schema, ensure_ascii=False).replace('</','<\\/')+'</script>', page)
    return page

def crumbs(slug, c, article=False):
    out = shared.crumbs(c, 1)
    if article:
        out = out.replace('</nav>', '<span aria-hidden="true">/</span><a href="index.html">'+shared.localized(SERIES[slug]['title'],c)+'</a></nav>')
    return out

def index(slug, items, c):
    info = SERIES[slug]
    cards = []
    for i in items:
        n = f'{i["number"]:02}'
        cards.append('<a class="western-entry" href="'+i['slug']+'.html"><span class="western-number">'+n+'</span><div>'+shared.localized({l:i[l]['title'] for l in ('en','zh')},c,'h2')+shared.localized({l:i[l]['deck'] for l in ('en','zh')},c,'p')+shared.words('Read →','阅读全文 →',c,'span','western-read')+'</div></a>')
    body = '<main class="western-wrap">'+crumbs(slug,c)+'<section class="western-hero"><p class="western-kicker">'+shared.words('SAE & Western Philosophy','SAE西哲',c)+'</p>'+shared.localized(info['title'],c,'h1')+shared.localized(info['deck'],c,'p','western-deck western-search-deck')+shared.words(f'Introduction + {len(items)-1} essays · English, Simplified & Traditional Chinese',f'小引＋{len(items)-1}篇正文 · 简体、繁体与独立英文版',c,'p','western-meta')+'<div class="western-actions"><a href="intro.html">'+shared.words('Start with the book →','先认识这本书 →',c)+'</a><a href="ep01.html">'+shared.words('Read Essay 01','直接读第一篇',c)+'</a></div>'+shared.words('Read each essay on its own. Optional SAE asides and source notes can be opened after the complete text.','各篇可以单独读。正文完整呈现，SAE旁注与版本来源放在文末，可自行展开。',c,'p','western-note')+'</section><div class="western-entries">'+''.join(cards)+'</div><aside class="western-afterword"><a href="../sae-western/index.html">'+shared.words('← All Western Philosophy series','← 回到 SAE西哲',c)+'</a></aside></main>'
    return shared.shell(body,header(slug,info['title']['en'],info['deck']['en'],''))

def article(slug, item, items, c):
    info = SERIES[slug]
    body, notes = [], []
    for lang, css, tag in [('en','en','en'),('zh','zh','zh-Hans'),('zh','hant','zh-Hant')]:
        copy = item[lang]
        conv = c.convert if css == 'hant' else lambda s:s
        sections = []
        for section in copy['sections']:
            h = '<h2>'+shared.esc(conv(section['heading']))+'</h2>' if section['heading'] else ''
            sections.append('<section>'+h+''.join('<p>'+shared.esc(conv(p))+'</p>' for p in section['paragraphs'])+'</section>')
        body.append(f'<div class="western-prose lang-{css}" lang="{tag}">'+''.join(sections)+'</div>')
        notes.append(f'<div class="lang-{css}" lang="{tag}">'+''.join('<p>'+shared.esc(conv(p))+'</p>' for p in copy['notes'])+'</div>')
    aside = ''
    if item['zh'].get('aside'):
        aside = '<details class="western-aside"><summary>'+shared.words('Alongside SAE · an optional marginal note','与SAE并读 · 可选旁注',c)+'</summary>'+shared.localized({l:item[l]['aside'] for l in ('en','zh')},c,'p')+'<a href="../sae-first-critique/index.html">'+shared.words('The SAE First Critique essays →','进入 SAE第一批判 →',c)+'</a></details>'
        if '意义论' in item['zh']['aside']:
            aside = aside.replace('../sae-first-critique/index.html','../meaning/index.html').replace('The SAE First Critique essays →','The SAE essays on meaning →').replace('进入 SAE第一批判 →','进入 SAE意义论 →').replace('進入 SAE第一批判 →','進入 SAE意義論 →')
    sources = ''.join('<li><a href="'+shared.esc(s['url'])+'">'+shared.localized(s['title'],c)+'</a></li>' for s in item['sources'])
    source_section = '<details class="western-sources"><summary>'+shared.words('Text, editions & sources','文本、版本与来源',c)+'</summary>'+''.join(notes)+'<ul>'+sources+'</ul></details>'
    nav = []
    for n,en,zh in [(item['number']-1,'Previous','上一篇'),(item['number']+1,'Next','下一篇')]:
        if 0 <= n < len(items):
            other = items[n]; url = other['slug']+'.html'; title = {l:other[l]['title'] for l in ('en','zh')}
        else:
            url = 'index.html'; title = info['title']; en,zh = 'Series contents','系列目录'
        nav.append('<a href="'+url+'">'+shared.words(en,zh,c,'small')+shared.localized(title,c)+'</a>')
    number = shared.words('Introduction','小引',c) if not item['number'] else f'{item["number"]:02} / {len(items)-1:02}'
    main = '<main class="western-wrap">'+crumbs(slug,c,True)+'<article class="western-article"><div class="western-article-head"><p class="western-kicker">'+shared.localized(info['title'],c)+' · '+number+'</p>'+shared.localized({l:item[l]['title'] for l in ('en','zh')},c,'h1')+shared.localized({l:item[l]['deck'] for l in ('en','zh')},c,'p','western-deck western-search-deck')+'<p class="western-meta">Han Qin ('+shared.words('秦汉','秦汉',c)+') · 2026</p></div>'+''.join(body)+aside+source_section+'<nav class="western-series-nav" aria-label="Series navigation">'+''.join(nav)+'</nav></article></main>'
    return shared.shell(main,header(slug,item['en']['title']+' · '+info['author']['en'],item['en']['deck'],item['slug']+'.html',item['sources']))

def build():
    c = Converter(); outputs = {}
    try:
        for slug in SERIES:
            items = load(slug); path = ROOT/'essays'/slug
            outputs[path/'index.html'] = index(slug,items,c)
            for item in items:
                outputs[path/(item['slug']+'.html')] = article(slug,item,items,c)
        return outputs
    finally:
        c.close()

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    outputs=build()
    if args.check:
        assert all(p.exists() and p.read_text()==text for p,text in outputs.items()), 'Stale classics pages'
        print('OK: 20 reproducible trilingual pages')
    else:
        for path,text in outputs.items():
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        print('Wrote 20 complete trilingual classics pages')
