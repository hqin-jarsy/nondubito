#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Red Chamber project entrance; never rewrite character essays.

The initial --capture-catalog mechanically preserves the old index's links and
titles. Subsequent builds use that checked-in catalog, not generated HTML.
"""
import argparse
import html
import json
import re
from pathlib import Path
from import_fairy_tales import TraditionalConverter

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'essays/literature/hlm'
CATALOG = ROOT / 'data/hongloumeng/characters.json'
EDITIONS = {'zh': ('', 'zh-Hans', '简体中文'), 'en': ('en/', 'en', 'English'), 'zh-hant': ('zh-hant/', 'zh-Hant', '繁體中文')}
ORIGIN = 'https://nondubito.net/essays/literature/hlm/'
PAPERS = [
 ('人是有情的', 'People Have Qing', '缘起、方法与结论', 'Origins, method and conclusions',
  '为什么接着写，以及哪些依据、推断和创作选择需要分别交代。',
  'Why write beyond chapter eighty? The overview distinguishes textual evidence, interpretation and the author’s creative decisions.'),
 ('前八十回脂批前指审计：采与不采', 'An Audit of Forward References in the Zhiyan Zhai Commentary', '批语与取舍', 'Commentary and choices',
  '批语说了什么，本项目采了什么、没有采什么。记录的是自己的处理，不是替批语裁定真伪。',
  'What do the marginal notes anticipate, and what does this project adopt or leave aside? The audit makes its choices inspectable; it does not certify the notes as true or false.'),
 ('《红楼梦》的成书层累：证据与诸说', 'The Layered Composition of Dream of the Red Chamber', '成书与材料', 'Composition and sources',
  '把文本留下的痕迹、研究者的解释和本项目的联想分开。介绍诸说，不把猜测写成已经查明的成书史。',
  'Traces in the text, scholars’ explanations and this project’s conjectures are kept distinct. Theories of composition are presented without turning them into established history.')]


def capture_catalog():
    if CATALOG.exists():
        raise SystemExit('Catalog already exists; refusing to replace it.')
    source = (TARGET / 'index.html').read_text()
    groups = []
    def field(block, cls):
        m = re.search(r'<(?:span|div) class="'+re.escape(cls)+r'(?: [^"]*)?"[^>]*>(.*?)</(?:span|div)>', block, re.S)
        assert m, cls
        return html.unescape(re.sub('<[^>]+>', '', m[1])).strip()
    for anchor, block in re.findall(r'<section class="register-section" id="([^"]+)">(.*?)</section>', source, re.S):
        cards = []
        for href, card in re.findall(r'<a href="([^"]+)" class="essay-card">(.*?)</a>', block, re.S):
            assert (TARGET / href).is_file()
            people={}
            for language in ['zh','en']:
                description=field(card,'essay-card-desc lang-'+language)
                people[language]=description.split(' · ')[0] if ' · ' in description else ''
            cards.append({'url':href, 'zh':field(card,'essay-card-title-zh'), 'en':field(card,'essay-card-title-en'), 'people':people})
        groups.append({'id':anchor,'zh':field(block,'register-name-zh'),'en':field(block,'register-name-en'),'essays':cards})
    assert len(groups) == 10
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(groups, ensure_ascii=False, indent=2)+'\n')
    print('Captured', sum(len(g['essays']) for g in groups), 'existing essay links.')


def render():
    groups = json.loads(CATALOG.read_text())
    count = sum(len(g['essays']) for g in groups)
    converter = TraditionalConverter()
    pages = {}
    for lang, (directory, code, label) in EDITIONS.items():
        en = lang == 'en'
        up = '../' if directory else ''
        base = '../../../../' if directory else '../../../'
        def text(zh, english):
            value = english if en else zh
            if lang == 'zh-hant':
                value = converter.convert(value).replace('“','「').replace('”','」')
                for a,b in {'余項':'餘項','關系':'關係','里面':'裡面'}.items(): value=value.replace(a,b)
            return value
        def t(zh, english): return html.escape(text(zh,english))
        def a(url, title, attrs=''): return f'<a href="{html.escape(url)}" {attrs}>{title}</a>'
        def legacy(url,title):
            choice = 'en' if en else 'zh'
            return a(up+url+'?lang='+choice,title,f'data-legacy-language="{choice}"')
        title = text('人是有情的——重读《红楼梦》', 'Lives Beyond Their Endings: Returning to Dream of the Red Chamber')
        desc = text('从人物回顾到研究论文，再到秦汉原创的后三十回小说。一个从阅读走向创作的红楼梦专题。', 'A Red Chamber project in three parts: character essays, research papers and Han Qin’s original thirty-chapter continuation.')
        canonical = ORIGIN+directory
        alternatives = ''.join(f'<link rel="alternate" hreflang="{c}" href="{ORIGIN+d}">' for d,c,_ in EDITIONS.values())
        alternatives += f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}">'
        language_links = ''.join(a(up+d+'index.html?lang='+key, name, f'data-edition="{key}" lang="{c}"'+(' aria-current="page"' if key==lang else '')) for key,(d,c,name) in EDITIONS.items())
        featured = ''.join(legacy(url,t(zh,english)) for url,zh,english in [
            ('intro.html','从一场酒令开始','Begin with a drinking game'),
            ('z-daiyu.html','走近黛玉','Meet Daiyu'),
            ('gz-baoyu.html','走近宝玉','Meet Baoyu')])
        catalog = []
        for group in groups:
            cards = ''.join('<li>'+legacy(e['url'],('<span class="people">'+t(e['people']['zh'],e['people']['en'])+'</span>' if e['people']['en' if en else 'zh'] else '')+t(e['zh'],e['en']))+'</li>' for e in group['essays'])
            catalog.append(f'<details class="character-group" id="{group["id"]}"><summary>{t(group["zh"],group["en"])} <span>{len(group["essays"])}</span></summary><ul>{cards}</ul></details>')
        papers = []
        for i,(zh,english,tag,entag,summary,ensummary) in enumerate(PAPERS):
            url=f'https://self-as-an-end.net/papers/sae-hongloumeng-{i}.html'
            papers.append(f'<article class="paper"><p class="eyebrow">{i:02d} · {t(tag,entag)}</p><h3>{a(url,t(zh,english))}</h3><p>{t(summary,ensummary)}</p></article>')
        body = f'''<section class="hero"><p class="eyebrow">NON DUBITO · {t('红楼梦大专题','A RED CHAMBER PROJECT')}</p>
<h1>{t('人是有情的','Lives Beyond Their Endings')}<span class="subtitle">{t('重读《红楼梦》','Returning to Dream of the Red Chamber')}</span></h1><p class="deck">{t('我们记得黛玉的眼泪、宝玉的痴，也记得大观园最后散了。但一个人的遭逢，是否就能说尽这个人？从前八十回出发，重读这些人物，也尝试为他们接着写下去。','We remember Daiyu’s tears, Baoyu’s attachments, and the dispersal of a whole household. But does knowing what happens to someone tell us everything about them? This project begins with the first eighty chapters, returns to their people, and ventures to continue their stories.')}</p></section>
<nav class="jump" aria-label="{t('本页导航','On this page')}">{a('#characters',t('红楼人物','The people'))}{a('#research',t('为什么这样接着写','The reasons for continuing'))}{a('#continuation',t('八十回以后','Beyond chapter eighty'))}</nav>
<section class="project-intro"><h2>{t('先认识这些人，再接着写','First meet the people. Then continue their stories.')}</h2><p>{t('这个项目从网站上的人物解读开始：逐一回顾书中人的处境、关系和选择。后来，问题从“怎样读他们”走向了“怎样写他们的后来”。人物回顾、研究论文和原创的后三十回小说，是同一项工作的三个部分；读者不必先读论文，才有资格走进故事。','The character essays on this site were the project’s starting point: a sustained return to the people, relationships and choices in the novel. Reading led to another question—how might their stories continue? The essays, research and Han Qin’s original thirty-chapter continuation belong to one undertaking. The papers are an available path, not an entrance exam.')}</p></section>
<section id="characters"><p class="eyebrow">01 · {t('人物回顾','CHARACTER ESSAYS')}</p><h2>{t('红楼人物','The People of the Red Chamber')}</h2><p>{t(f'现有 {count} 篇解读，是整个项目最初的铺垫。可以先从一场酒令、一个人物开始，不必按次序通读。',f'These {count} essays laid the groundwork for the project. Start with one scene or one person; there is no required order.')}</p>
<div class="featured">{featured}</div>
<p class="edition-note">{t('人物文章目前提供简体中文与英文；繁体入口中的人物链接暂转简体原文。本次整理保留人物正文。','The character essays are available in Simplified Chinese and English. The Traditional Chinese hub links to the Simplified originals. This entrance update leaves the essays themselves unchanged.')}</p>
<details class="reading-note"><summary>{t('关于目录里的册次与称谓','A note on the registers and labels')}</summary><p>{t('下列分组沿用人物回顾写作时的编排，方便寻找旧文。九册、一百零八人的组合及相应关系解释，是本项目当时采用的阅读方案，不是已经考定的曹雪芹情榜全貌，也不是给人物永久定性。后续论文会说明哪些读法保留、哪些发生了变化；不能把我们的编排反过来当作原作的证据。','The groups below retain the arrangement used when these essays were written, so familiar pieces remain easy to find. The nine-register, 108-person scheme and its relational interpretations are this project’s reading framework—not an authenticated reconstruction of Cao Xueqin’s complete roster, nor permanent verdicts on the characters. Later papers explain where the reading develops or changes; our arrangement is not evidence about the original.')}</p></details>
<h3 class="catalog-title">{t('按原有分组找文章','Browse the original groups')}</h3><div class="catalog">{''.join(catalog)}</div></section>
<section id="research"><p class="eyebrow">02 · {t('研究论文','RESEARCH PAPERS')}</p><h2>{t('为什么这样接着写','Why Continue It This Way?')}</h2><p>{t('人物的后来不只关乎情节怎样接上，也关乎每一次选择凭什么成立。论文把原文、批语、推断和创作取舍分开，让读者能追问，也能不同意。','Continuing a story is more than joining one event to the next. Each choice needs reasons. These papers distinguish the novel’s text, its commentary, interpretive inferences and creative decisions, so readers can question the work—and disagree.')}</p>
<aside class="spoiler"><strong>{t('阅读提示','Before you open the papers')}</strong><p>{t('以下三篇为 SAE 网站已发布的论文，含秦汉原创后三十回的重要情节与结局。若想先读小说，可以暂时跳过。本专题的通俗导读散文将另行发布；论文无需当作必读前言。','The three papers below are published on the SAE website and discuss major events and endings in Han Qin’s original continuation. Skip them for now if you would rather encounter the story first. Companion essays for general readers will follow; the papers are not required prefatory reading.')}</p></aside>
<div class="papers">{''.join(papers)}</div><p class="edition-note">{t('论文提供中英文本；材料篇目前标为预发布版，会随核查修订。以论文各自页面的版本说明为准。','The papers contain Chinese and English texts. The source studies are currently marked as pre-releases and may change with further checking; consult each paper’s version notice.')}</p></section>
<section id="continuation"><p class="eyebrow">03 · {t('原创小说 · 后三十回','ORIGINAL FICTION · THIRTY NEW CHAPTERS')}</p>
<h2>{t('八十回以后','Beyond Chapter Eighty')}</h2><p class="status">{t('全文已完成 · 正在打磨 · 尚未公开','Manuscript complete · Revision in progress · Not yet released')}</p>
<p>{t('秦汉原创的第八十一至第一百一十回，共三十回，已经完成。目前继续打磨，待论文系列发布后，将公开全部文本。这里届时会成为逐回阅读的入口。','Han Qin has completed an original continuation comprising chapters 81–110. The complete thirty-chapter manuscript is now being refined. It will be released after the paper series, and this section will become its chapter-by-chapter reading entrance.')}</p>
<p>{t('这三十回是秦汉的原创小说，不是曹雪芹的佚稿，也不是对已有续书的整理。“诠释性复原”说的是这次创作的方法：以前八十回及相关材料为依据，把一种读法写成故事；并不声称恢复了曹雪芹原稿。','These thirty chapters are original fiction by Han Qin, not a recovered manuscript by Cao Xueqin or an edited compilation of existing continuations. “Interpretive reconstruction” describes the creative method: developing a reading of the first eighty chapters and related materials into a story. It is not a claim to have recovered the lost original.')}</p>
</section>'''
        schema={'@context':'https://schema.org','@type':'CollectionPage','name':title,'description':desc,'url':canonical,'inLanguage':code,'dateModified':'2026-09-29','isPartOf':{'@type':'WebSite','name':'Non Dubito','url':'https://nondubito.net/'}}
        pages[TARGET/directory/'index.html']=f'''<!doctype html>
<html lang="{code}" data-lang="{lang}" data-editions="{code}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — Non Dubito</title><meta name="description" content="{html.escape(desc)}"><meta name="author" content="Han Qin">
<link rel="canonical" href="{canonical}">{alternatives}<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="website"><meta name="twitter:card" content="summary">
<link rel="icon" href="{base}favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{up}hongloumeng-hub.css"><script defer src="{up}hongloumeng-hub.js"></script>
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head><body><a class="skip" href="#main">{t('跳到正文','Skip to content')}</a>
<header class="site-header"><a class="brand" href="{base}index.html?lang={lang}">Non <span>Dubito</span></a><nav aria-label="{t('网站导航','Site navigation')}">{a(base+'essays/literature/index.html?lang='+lang,t('文学','Literature'))}{a(base+'library.html?lang='+lang,t('书库','Library'))}{a(base+'search.html?lang='+lang,t('搜索','Search'))}</nav><details class="language-menu"><summary>{label} <span aria-hidden="true">⌄</span></summary><nav aria-label="{t('阅读语言','Reading language')}">{language_links}</nav></details></header>
<main id="main">{body}</main><footer>{a(base+'essays/literature/index.html?lang='+lang,t('回到文学频道','Back to literature'))}<p>Non Dubito · {t('秦汉','Han Qin')}</p></footer>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script></body></html>\n'''
    return pages


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--capture-catalog',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.capture_catalog:
        capture_catalog()
    stale=[]
    for path,content in render().items():
        if args.check:
            if not path.exists() or path.read_text()!=content: stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)
    if stale: raise SystemExit('Stale: '+', '.join(stale))
    print('OK: three Red Chamber project entrances; character articles untouched.')


if __name__=='__main__': main()
