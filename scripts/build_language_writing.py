#!/usr/bin/env python3
"""Build three complete reader essays, and a six-shelf SAE reading map."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from build_ai_work_series import shell_header, footer, tri
from build_love_series import LoveTraditionalConverter
from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-10-26'
TITLE = ('Finding Words of Our Own', '把话说成自己的')
DECK = ('A name, a message that still feels wrong, a paragraph that begins to sound like its writer. Three essays on language, what words leave unsaid, and learning to write with AI without leaving ourselves behind.', '给一件事起名，写一条总觉得不对的消息，再慢慢写出像自己的文章。三篇散文，读语言、没说完的话，以及 AI 时代写作的成长。')
SOURCES = ('language', 'language-remainder', 'writing-last-mile')


def esc(text: str) -> str:
    return html.escape(text, quote=True)


class WritingTraditionalConverter(LoveTraditionalConverter):
    def convert(self, text: str) -> str:
        # These are ordinary meanings, not the software terms in the shared map.
        protected = text.replace('项目', '__LW_ACTIVITY__').replace('质量', '__LW_QUALITY__')
        result = super().convert(protected)
        for old, new in (('__LW_ACTIVITY__','項目'), ('__LW_QUALITY__','品質'),
                         ('反復','反覆'), ('沈下','沉下'), ('父親沈','父親沉'),
                         ('一髮過去','一發過去'), ('余項','餘項'), ('鄰裡','鄰里'),
                         ('松了腿','鬆了腿'), ('松了口氣','鬆了口氣'), ('划掉','劃掉'),
                         ('說明瞭','說明了'), ('深沈','深沉'), ('贊美','讚美'),
                         ('周日','週日'), ('一周','一週'), ('‘','「'), ('’','」')):
            result = result.replace(old, new)
        return result


def loc(en: str, zh: str, conv, tag: str = 'span', css: str = '') -> str:
    return tri(esc(en), esc(zh), esc(conv.convert(zh)), tag, css)


def load_items() -> list[dict]:
    items = []
    for i, source in enumerate(SOURCES, 1):
        path = ROOT / f'data/language-writing/ep{i:02d}.json'
        item = json.loads(path.read_text())
        assert item['id'] == i and item['slug'] == f'ep{i:02d}'
        assert item['source_url'] == f'https://self-as-an-end.net/papers/{source}.html'
        for lang in ('en','zh'):
            for key in ('title','deck'):
                assert item[f'{key}_{lang}'].strip()
            body = item[f'body_{lang}']
            assert len(body) >= 18 and all(isinstance(p,str) and p.strip() and '<' not in p and not p.startswith('###') for p in body)
            assert sum(p.startswith('## ') for p in body) <= 3
            text = '\n'.join(body)
            assert len(re.findall(r'[\u3400-\u9fff]',text)) >= 2600 if lang == 'zh' else len(text.split()) >= 1500
            assert not re.search(r'\b\d{2}DD\b|\bH\d{1,3}\b',text)
        items.append(item)
    return items


@tracked_html
def page(content: str, title: str, deck: str, path: str, conv, source: str | None = None, collection: tuple[str,str] | None = None, *, publication_date: str = DATE) -> str:
    url = 'https://nondubito.net/' + path.removesuffix('index.html')
    schema = {'@context':'https://schema.org','@type':'Article' if source else 'CollectionPage','name':title,'description':deck,'url':url,'inLanguage':['en','zh-Hans','zh-Hant']}
    if source:
        collection_url,collection_name = collection or ('https://nondubito.net/essays/language-writing/',TITLE[0])
        schema.update(headline=title,author={'@type':'Person','name':'Han Qin (秦汉)'},datePublished=publication_date,dateModified=publication_date,citation=source,mainEntityOfPage=url,isPartOf={'@type':'CollectionPage','url':collection_url,'name':collection_name})
    schema_text = json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    header = shell_header().replace('data-site-shell-menu aria-controls','data-site-shell-menu aria-label="Menu" aria-controls')
    foot = footer()
    for en,zh in (('Explore','探索'),('Library','书架'),('SAE Theory ↗','SAE 理论 ↗')):
        foot = foot.replace('>'+en+'</a>','>'+loc(en,zh,conv)+'</a>')
    return f'''<!DOCTYPE html>
<html lang="en" data-lang="en" data-editions="en zh zh-hant"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(deck)}"><meta name="author" content="Han Qin (秦汉)">
<link rel="canonical" href="{url}"><meta property="og:type" content="{'article' if source else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(deck)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary">
<link rel="icon" href="../../favicon.svg" type="image/svg+xml"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;family=Noto+Serif+TC:wght@400;500;600&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="../../site-shell.css?v=20260905b"><link rel="stylesheet" href="../language-writing/reading.css?v=20261026"><script src="../../site-shell.js?v=20260905b"></script><script defer src="../language-writing/reading.js?v=20261026"></script><script type="application/ld+json">{schema_text}</script></head><body class="site-shell-page explicit-hant lw-page">{header}{content}{foot}</body></html>
'''


def crumb(conv, article=False, hub=False):
    target = '../../explore.html#sae' if hub else '../sae/index.html'
    text = loc('SAE & Philosophy','SAE 与哲学',conv)
    extra = f'<span aria-hidden="true">/</span><a href="index.html">{loc("Language & Writing","语言与写作",conv)}</a>' if article else ''
    return f'<nav class="lw-crumb" aria-label="Breadcrumb"><a href="{target}">{text}</a>{extra}</nav>'


def related(conv):
    links = ''.join(f'<a href="../{path}/index.html">{loc(en,zh,conv)}</a>' for path,en,zh in (('ai-work','Working with AI','与 AI 共事'),('method','Method','方法论'),('sae','SAE reading map','SAE 阅读地图')))
    return '<aside class="lw-related">' + loc('Keep exploring','继续读',conv,'h2') + links + '</aside>'


def index(items,conv):
    cards = ''.join(f'<a class="lw-card" href="{item["slug"]}.html"><p class="lw-kicker">0{item["id"]}</p>{loc(item["title_en"],item["title_zh"],conv,"h2")}{loc(item["deck_en"],item["deck_zh"],conv,"p")}{loc("Read essay →","阅读全文 →",conv,"span","lw-read")}</a>' for item in items)
    content = f'''<main class="lw-wrap">{crumb(conv)}<section class="lw-hero"><p class="lw-kicker">Non Dubito · {loc('Language & Writing','语言与写作',conv)}</p>{loc(*TITLE,conv,'h1')}{loc(*DECK,conv,'p','lw-deck lw-search-deck')}{loc('Three complete essays · English, Simplified & Traditional Chinese','三篇完整散文 · 英文、简体中文与繁体中文',conv,'p','lw-meta')}</section>
<aside class="lw-opening">{loc('You do not have to learn a theory of language before reading. Begin with the thing you want to say.','不必先学一套语言理论。从你想说的一句话开始就好。',conv,'p')}<a href="ep01.html">{loc('Start with a name →','从一个名字开始 →',conv)}</a></aside><section class="lw-grid">{cards}</section><section class="lw-note">{loc('What this series asks','这三篇在问什么',conv,'h2')}{loc('Shared words make thought possible, yet no wording settles every experience. AI can help us compare, revise and discover; whether a sentence is truly what we mean remains a question we have to meet. The examples here are imagined ordinary situations, not documented cases. Technical hypotheses in the papers are not treated as established findings about every model or every writer.','共同的词让想法得以传递，但没有一句话能把经历全说尽。AI 可以帮忙展开、比较与修改，却不能仅凭文字漂亮，就决定那是不是我们真正想说的。本系列使用虚构的日常场景，不当作真实案例；论文里的技术假说也不写成对所有模型、所有写作者都已证实的结论。',conv,'p')}</section>{related(conv)}</main>'''
    return page(content,TITLE[0] + ' · 语言与写作',DECK[0],'essays/language-writing/index.html',conv)


def prose(body):
    return '\n'.join(f'<h2>{esc(p[3:])}</h2>' if p.startswith('## ') else f'<p>{esc(p)}</p>' for p in body)


def article(item,items,conv):
    bodies = ''.join(f'<div class="essay-body lw-prose lang-{lang}" lang="{native}">{prose([conv.convert(p) for p in item["body_zh"]] if lang == "hant" else item["body_"+lang])}</div>' for lang,native in (('en','en'),('zh','zh-Hans'),('hant','zh-Hant')))
    links = []
    for offset,en,zh in ((-1,'Previous essay','上一篇'),(1,'Next essay','下一篇')):
        other = item['id'] - 1 + offset
        if 0 <= other < len(items):
            target = items[other]
            links.append(f'<a href="{target["slug"]}.html">{loc(en,zh,conv,"small")}{loc(target["title_en"],target["title_zh"],conv)}</a>')
        else:
            links.append(f'<a href="index.html">{loc("All three essays","全部三篇",conv,"small")}{loc(*TITLE,conv)}</a>')
    note = loc('A reader essay drawn from the corresponding SAE paper, not its complete technical translation. English is independently written; the Chinese examples are retained in meaning rather than sentence order. Ordinary scenes are imagined illustrations. AI assistance is not mandatory, and accepting a good suggestion is not by itself a loss of authorship.','本文由对应 SAE 论文改写为散文，不是全部技术论证的逐段翻译；英文独立重写，保留论证与例子的意思。日常场景为虚构示例。不要求写作者使用 AI，也不把接受一个好建议本身判作失去自己的声音。',conv,'p')
    references = {1:[('https://arxiv.org/html/1706.03762v7#S3.SS4','Attention Is All You Need · §3.4')],2:[('https://dicionario.priberam.org/saudade','Dicionário Priberam · saudade'),('https://plato.stanford.edu/entries/japanese-aesthetics/','Stanford Encyclopedia · Japanese Aesthetics')]}
    note += ''.join(f'<p><a href="{url}">{esc(label)} ↗</a></p>' for url,label in references.get(item['id'],[]))
    content = f'''<main class="lw-wrap">{crumb(conv,True)}<article class="lw-article"><div class="lw-head"><p class="lw-kicker">{loc('Language & Writing','语言与写作',conv)} · 0{item['id']}</p>{loc(item['title_en'],item['title_zh'],conv,'h1')}{loc(item['deck_en'],item['deck_zh'],conv,'p','lw-deck lw-search-deck')}<p class="lw-meta">Han Qin · <time datetime="{DATE}">{DATE}</time></p></div>{bodies}<details class="lw-sources"><summary>{loc('Source & reading note','来源与阅读说明',conv)}</summary>{note}<a href="{item['source_url']}">{loc('Read the source paper ↗','阅读原论文 ↗',conv)}</a></details><nav class="lw-series-nav" aria-label="Series navigation">{''.join(links)}</nav>{related(conv)}</article></main>'''
    return page(content,item['title_en'],item['deck_en'],'essays/language-writing/'+item['slug']+'.html',conv,item['source_url'])


def reading_map(conv):
    groups = json.loads((ROOT/'data/sae-reading-map.json').read_text())['groups']
    jump = ''.join(f'<a href="#{g["id"]}"><small>0{i}</small>{loc(g["en"],g["zh"],conv)}</a>' for i,g in enumerate(groups,1))
    sections = []
    for i,g in enumerate(groups,1):
        cards = ''.join(f'<a class="sae-item" href="../../{path}">{loc(en,zh,conv)}<span aria-hidden="true">→</span></a>' for path,zh,en in g['items'])
        related_links = ''.join(f'<a href="../../{path}">{loc(en,zh,conv)}</a>' for path,zh,en in g.get('related',[]))
        sections.append(f'<section class="sae-group" id="{g["id"]}"><div class="sae-group-head"><p class="lw-kicker">0{i} · {loc(g["en"],g["zh"],conv)}</p>{loc(g["question_en"],g["question_zh"],conv,"h2")}{loc(g["deck_en"],g["deck_zh"],conv,"p")}<a class="lw-read" href="../../{g["start"]}">{loc("One way in →","可以从这里开始 →",conv)}</a></div><div class="sae-item-grid">{cards}</div>{"<div class=lw-related>"+related_links+"</div>" if related_links else ""}<a class="sae-back" href="#reading-map">{loc("↑ Back to six shelves","↑ 回到六个方向",conv)}</a></section>')
    deck = ('Choose a question, not a syllabus. Six shelves help you find a way through SAE’s reader essays; every existing series keeps its own address.','不必先读完一套课程。挑一个你在关心的问题，沿六个方向找散文；所有原有系列与链接都保留。')
    content = f'''<main class="lw-wrap sae-wrap">{crumb(conv,hub=True)}<section class="lw-hero"><p class="lw-kicker">Non Dubito · SAE</p>{loc('A Reading Map','SAE 散文阅读地图',conv,'h1')}{loc(*deck,conv,'p','lw-deck lw-search-deck')}</section><aside class="lw-opening">{loc('First visit? Five minutes is enough to begin.','第一次来？先用五分钟，认识凿、构与余项。',conv,'p')}<a href="../../start.html">{loc('Start Here →','从这里开始 →',conv)}</a>{loc('Then try Foundations, or enter any question below. The six shelves are reading aids, not divisions of the theory or a required order. Individual series show their own available languages.','然后读基础系列，也可以直接进入下面任何一个问题。六组是找文章的路标，不是理论的六个部门，也不是必修顺序。各系列自己的页面会标明可用语言。',conv,'p','lw-meta')}</aside><nav class="sae-jump" id="reading-map" aria-label="Six reading shelves">{jump}</nav>{''.join(sections)}<aside class="lw-opening">{loc('Theory, ordinary life, or a work you love?','想读理论、日常，还是一部喜欢的作品？',conv,'h2')}{loc('This map gathers the framework’s reader essays. Everyday scenes, stories, film, books and games still have their own entrances in Explore. For a complete directory, use the Library; for a title or concept, use Search.','这张地图整理的是框架散文。日常场景，以及文学、影视与游戏解读，仍各有入口。想看全目录去书架，想找标题或概念可以搜索。',conv,'p')}<div class="lw-related"><a href="../../explore.html">{loc('Explore','探索',conv)}</a><a href="../../library.html#sae-theory">{loc('Full Library','完整书架',conv)}</a><a href="../../search.html">{loc('Search','搜索',conv)}</a></div></aside></main>'''
    # Put the actual choices before the newcomer note, within the first screen.
    navigation = f'<nav class="sae-jump" id="reading-map" aria-label="Six reading shelves">{jump}</nav>'
    content = content.replace(navigation,'').replace('<aside class="lw-opening">',navigation+'<aside class="lw-opening">',1)
    return page(content,'SAE: A Reading Map · 散文阅读地图',deck[0],'essays/sae/index.html',conv)


def render():
    items = load_items()
    conv = WritingTraditionalConverter()
    try:
        pages = {ROOT/'essays/language-writing/index.html':index(items,conv),ROOT/'essays/sae/index.html':reading_map(conv)}
        pages.update({ROOT/f'essays/language-writing/{item["slug"]}.html':article(item,items,conv) for item in items})
        return pages
    finally:
        conv.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    for path,text in render().items():
        if args.check:
            assert path.read_text() == text, f'Stale page: {path}'
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text)
    print(('Checked' if args.check else 'Wrote')+' five pages · three complete reading modes · six reading shelves')


if __name__ == '__main__':
    main()
