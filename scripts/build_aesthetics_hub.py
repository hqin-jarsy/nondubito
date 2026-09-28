#!/usr/bin/env python3
"""Build the three-language aesthetics hub and opening essay.

Daily posts and log.json remain the author's inputs. After adding a daily post,
run this script instead of inserting cards into the generated index by hand.
This does not generate, convert or edit any daily article or ray essay.
"""
import argparse
import html
import json
from pathlib import Path
import re

from import_fairy_tales import TraditionalConverter

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'essays/aesthetics'
DATA = ROOT / 'data/aesthetics'
DATE = '2026-09-28'
ORIGIN = 'https://nondubito.net/'
PAPERS = 'https://self-as-an-end.net/papers/'
EDITIONS = {'zh': ('', 'zh-Hans', '简体中文'), 'en': ('en/', 'en', 'English'), 'zh-hant': ('zh-hant/', 'zh-Hant', '繁體中文')}
RAYS = [
 ('混沌之美', 'Chaos'), ('哲学之美', 'Philosophy'), ('数学之美', 'Mathematics'),
 ('物理之美', 'Physics'), ('因果之美', 'Causation'), ('生物之美', 'Biology'),
 ('繁殖之美', 'Reproduction'), ('感知之美', 'Perception'), ('认知之美', 'Cognition'),
 ('自我之美', 'Self'), ('目的之美', 'Purpose'), ('不疑之美', 'Non-doubt'), ('双向不疑之美', 'Mutual non-doubt')]


def render_pages():
    entries = json.loads((TARGET / 'log.json').read_text())['entries']
    entries = sorted(entries, key=lambda e: e['date'], reverse=True)
    assert len({e['slug'] for e in entries}) == len(entries)
    for e in entries:
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', e['slug']) and (TARGET / (e['slug']+'.html')).is_file()
    converter = TraditionalConverter()
    outputs = {}
    for lang, (directory, langcode, label) in EDITIONS.items():
        en = lang == 'en'
        base = '../../../' if directory else '../../'
        up = '../' if directory else ''
        folder = TARGET / directory

        def text(zh, english=None):
            value = english if en and english is not None else zh
            if lang == 'zh-hant':
                value = converter.convert(value).replace('“','「').replace('”','」').replace('‘','『').replace('’','』')
                for a,b in {'余項':'餘項', '關系':'關係', '里面':'裡面', '那只已經':'那隻已經', '這只杯子':'這隻杯子', '贊美':'讚美', '一段代碼':'一段程式碼'}.items():
                    value = value.replace(a,b)
            return value

        def t(zh, english=None):
            return html.escape(text(zh,english))

        def a(href, title, extra=''):
            return f'<a href="{html.escape(href)}" {extra}>{title}</a>'

        def legacy(href, title):
            choice = 'en' if en else 'zh'
            return a(up+href+'?lang='+choice, title, f'data-legacy-language="{choice}"')

        def page(filename, title, description, body, guide=False):
            path = folder / filename
            relative = path.relative_to(ROOT).as_posix()
            canonical = ORIGIN + relative.removesuffix('index.html') if filename == 'index.html' else ORIGIN+relative
            alternates = []
            links = []
            for key, (sub, code, name) in EDITIONS.items():
                url = ORIGIN+'essays/aesthetics/'+sub+('' if filename=='index.html' else filename)
                alternates.append(f'<link rel="alternate" hreflang="{code}" href="{url}">')
                target = up+sub+filename+'?lang='+key
                links.append(a(target, name, f'lang="{code}" data-edition="{key}"'+(' aria-current="page"' if key==lang else '')))
            schema = {'@context':'https://schema.org','@type':'Article' if guide else 'CollectionPage',
                      'name':title,'url':canonical,'inLanguage':langcode,'description':description,
                      'isPartOf':{'@type':'WebSite','name':'Non Dubito','url':ORIGIN}}
            if guide:
                schema.update(headline=title,datePublished=DATE,author={'@type':'Person','name':'Han Qin'},
                              citation=PAPERS+'sae-judgment-aesthetics.html')
            else:
                schema['dateModified'] = max(DATE, entries[0]['date'])
            return f'''<!doctype html>
<html lang="{langcode}" data-lang="{lang}" data-editions="{langcode}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — Non Dubito</title><meta name="description" content="{html.escape(description)}">
<meta name="author" content="Han Qin (秦汉)"><link rel="canonical" href="{canonical}">
{''.join(alternates)}<meta property="og:title" content="{html.escape(title)} — Non Dubito"><meta property="og:description" content="{html.escape(description)}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="{'article' if guide else 'website'}"><meta name="twitter:card" content="summary">
<link rel="icon" href="{base}favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{up}aesthetics-hub.css">
<script defer src="{up}aesthetics-hub.js"></script><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('<',chr(92)+'u003c')}</script>
</head><body class="aesthetics-site"><a class="skip" href="#main">{t('跳到正文','Skip to content')}</a>
<header class="aesthetics-header"><a class="brand" href="{base}index.html?lang={lang}">Non <span>Dubito</span></a>
<nav aria-label="{t('网站导航','Site navigation')}">{a(base+'explore.html?lang='+lang,t('探索','Explore'))}{a(base+'library.html?lang='+lang,t('书库','Library'))}{a(base+'search.html?lang='+lang,t('搜索','Search'))}</nav>
<details class="language-menu"><summary>{label} <span aria-hidden="true">⌄</span></summary><nav aria-label="{t('阅读语言','Reading language')}">{''.join(links)}</nav></details></header>
<main id="main" class="{'guide-main' if guide else 'hub-main'}">{body}</main>
<footer class="aesthetics-footer">{a(base+'library.html?lang='+lang,t('回到书库','Back to the library'))}<p>Non Dubito · {t('秦汉','Han Qin')}</p></footer>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script>
</body></html>
'''

        title = text('美学：喜欢之外，还看见了什么？','Beauty: Beyond What We Like')
        desc = text('从喜欢与美的区别开始，读一篇总导读，看看十三条美学射线，再去日常作品中寻找。','An opening essay on liking and beauty, thirteen directions of inquiry, and a journal of daily discoveries.')
        guide_title = text('我不喜欢它，但我看得出它的美','I Don’t Like It. But I Can See Its Beauty.')
        guide_deck = text('一本不想重读的小说，一只已经做好的杯子。喜欢、美与判断，不必挤在同一句话里。','A novel we won’t read again. A cup that is finished. Liking, beauty and judgment need not all fit inside the same verdict.')
        body = f'''<section class="hero"><p class="kicker">NON DUBITO · {t('美学','AESTHETICS')}</p><h1>{html.escape(title)}</h1><p class="deck">{t('我们可以各有所爱，也可以在同一个地方相遇。从作品和生活出发，不必先记住一套术语。','Our tastes can remain our own even when we see something together. Begin with works and ordinary life, not a vocabulary test.')}</p></section>
<nav class="jump" aria-label="{t('本页导航','On this page')}">{a('#begin',t('从这里开始','Start here'))}{a('#rays',t('十三条射线','Thirteen rays'))}{a('#feed',t('日常发现','Daily discoveries'))}</nav>
<section id="begin" class="hub-section"><p class="kicker">01 · {t('总导读 · 简中 / 繁中 / 英文','OPENING ESSAY · THREE LANGUAGES')}</p><h2>{html.escape(guide_title)}</h2><p>{html.escape(guide_deck)}</p>{a('seeing-beauty.html?lang='+lang,t('读总导读 →','Read the opening essay →'),'class="button"')}</section>
<section id="rays" class="hub-section"><p class="kicker">02 · {t('看见美的不同方向','DIRECTIONS OF ATTENTION')}</p><h2>{t('十三条射线，不是一架梯子','Thirteen rays, not a ladder')}</h2><p>{t('同一片星空，可以从不同方向去看。射线不是给事物分箱，也不是把人的趣味分高低。以下是理论地图，不是阅读考试。','The same night sky can be approached in several ways. These rays are not bins for objects or ranks for people’s tastes. They are a map of questions, not a reading test.')}</p><p class="edition-note">{t('十三篇原论文均已发布，中英双语。对应的 Non Dubito 散文将分批制作；本批上线的是上面的总导读。','All thirteen academic papers are available in English and Chinese. Their Non Dubito essay counterparts are still to come; the opening essay above is available now.')}</p>
<details class="paper-map"><summary>{t('展开理论地图与原论文链接','Open the theory map and paper links')}</summary><ol class="ray-list">'''
        for n,(zh,english) in enumerate(RAYS,1):
            body+=f'<li>{a(PAPERS+f"sae-aesthetics-ray-{n}.html", t(zh,english)+" ↗")}<span>{t("原论文","Academic paper")}</span></li>'
        body+=f'''</ol><p>{a(PAPERS+'sae-judgment-aesthetics.html',t('总纲：判断力与美学 · 第二版 ↗','Framework: Judgment and Aesthetics · Second edition ↗'))}</p></details></section>
<section id="feed" class="hub-section"><p class="kicker">03 · {t('日常发现','DAILY DISCOVERIES')}</p><h2>{t('余项之美','Beauty of the Remainder')}</h2><p>{t('这里偏爱还在摸索的作品：代码、工具、手艺，以及计划之外长出来的东西。这是栏目选择停留的地方，不代表已经完成的作品失去了美。','This journal gravitates toward work still finding its way: code, tools, craft and things that grow beyond a plan. That is an editorial interest, not a claim that finished work has lost its beauty.')}</p><p class="edition-note">{t(f'{len(entries)} 篇日常记录 · 原文为简体中文与英文。繁体入口使用繁体标题，点击后进入原有简体页面。',f'{len(entries)} daily entries · Original Simplified Chinese and English editions. These articles retain their existing URLs and text.')}</p><h3>{t('最近六篇','The latest six')}</h3><div class="recent-list">'''

        def daily_card(e):
            return legacy(e['slug']+'.html', f'<time datetime="{e["date"]}">{e["date"]}</time><span>{t(e["zh_title"],e["en_title"])}</span>')
        body+=''.join(daily_card(e) for e in entries[:6])+'</div>'
        body+=f'<details id="archive" class="archive"><summary>{t("全部日常记录 · 按月浏览","All daily entries · Browse by month")}</summary>'
        months = sorted({e['date'][:7] for e in entries},reverse=True)
        for month in months:
            group=[e for e in entries if e['date'].startswith(month)]
            body+=f'<details class="month"><summary>{month} · {len(group)} {t("篇","entries")}</summary><div class="archive-list">'+''.join(daily_card(e) for e in group)+'</div></details>'
        body+=f'''</details></section>
<section class="hub-section related"><h2>{t('另一条入口','Another way in')}</h2><h3>{legacy('../artist_dead.html',t('艺术家已死','The Artist Is Dead'))}</h3><p>{t('一篇较早的长文，从市场、学院和算法讨论创作怎样被收窄。可以单独读；它不是总导读的先修课。原文为简体中文与英文。','An earlier long essay on how markets, academies and algorithms narrow creative work. Read it independently; it is not a prerequisite. Available in English and Simplified Chinese.')}</p></section>'''
        outputs[folder/'index.html']=page('index.html',title,desc,body)

        source=(DATA/('guide-en.md' if en else 'guide-zh.md')).read_text().strip()
        prose=[]; headings=[]
        for block in source.split('\n\n'):
            if block.startswith('## '):
                anchor='section-'+str(len(headings)+1)
                heading=text(block[3:])
                headings.append((anchor,heading))
                prose.append(f'<h2 id="{anchor}">{html.escape(heading)}</h2>')
            else:
                prose.append('<p>'+t(block)+'</p>')
        contents=''.join(a('#'+anchor,html.escape(heading)) for anchor,heading in headings)
        body=f'''<a class="back" href="index.html?lang={lang}">← {t('美学','Aesthetics')}</a><header class="hero"><p class="kicker">{t('美学 · 从这里开始','AESTHETICS · START HERE')}</p><h1>{html.escape(guide_title)}</h1><p class="deck">{html.escape(guide_deck)}</p><p class="byline">{t('秦汉','Han Qin')} · <time datetime="{DATE}">{DATE}</time></p></header>
<details class="contents"><summary>{t('这篇谈什么','In this essay')}</summary><nav aria-label="{t('文章目录','Essay sections')}">{contents}</nav></details>
<article class="prose">{''.join(prose)}</article>
<aside class="source-note"><h2>{t('想再往里读','For a closer look')}</h2><p>{t('本文依据《SAE 判断力与美学》第二版及十三条射线写成。文中的小说、电影、音乐与陶艺场景是为讨论而设的例子，不指向某一部已发表作品或真实事件。','This essay draws on the second edition of SAE Judgment and Aesthetics and its thirteen rays. The scenes involving a novel, a film, music and a pottery class are illustrative, not reports about particular published works or actual events.')}</p><p>{a(PAPERS+'sae-judgment-aesthetics.html',t('读理论总纲 · 第二版 ↗','Read the theoretical framework · Second edition ↗'))}</p><p>{a('index.html?lang='+lang+'#rays',t('查看十三条射线的原论文 →','Explore the thirteen academic papers →'))}</p></aside>
<nav class="end-links" aria-label="{t('继续阅读','Continue reading')}">{a('index.html?lang='+lang+'#feed',t('去日常作品里看看 →','Visit the daily discoveries →'))}{a('#main',t('回到页首','Back to top'))}</nav>'''
        outputs[folder/'seeing-beauty.html']=page('seeing-beauty.html',guide_title,guide_deck,body,True)
    return outputs


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    pages=render_pages()
    if args.check:
        stale=[str(p.relative_to(ROOT)) for p,s in pages.items() if not p.exists() or p.read_text()!=s]
        if stale:raise SystemExit('Stale aesthetics pages: '+', '.join(stale))
    else:
        for p,s in pages.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
    print(f'OK: {len(pages)} aesthetics pages; original daily articles untouched')


if __name__=='__main__':main()
