#!/usr/bin/env python3
"""Publish the author's immutable final manuscript, with a separate script edition."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from import_fairy_tales import TraditionalConverter

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'originals/hongloumeng'
DATE = '2026-10-07'
CHAPTERS = {
    'ch081': {'sha256': '17b576513dcd1b234b8043cf62cf624b376bb9c0e490014d2103941743dca131',
              'published': '2026-10-05', 'number': '第八十一回',
              'verse': ('抛红豆，滴相思。', '任凭风雨误花期。')},
    'ch082': {'sha256': '1fb3f88c945d4e6fea5eabaf7bff1cff01f1c370b968a2c5487d604e175806d0',
              'published': DATE, 'number': '第八十二回',
              'verse': ('淡粉新妆，藕丝衫子迎风软。晚凉初转，相约莲塘玩。',
                        '一棹轻舟，影共莲花乱。回头晚，藕花深浅，只载闲愁返。')},
}


def manuscript(stem):
    raw = (ROOT / f'data/originals/hongloumeng/{stem}.zh.txt').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CHAPTERS[stem]['sha256'], 'Final manuscript changed: obtain author approval first.'
    return raw.decode().splitlines()
ORIGIN = 'https://nondubito.net/originals/hongloumeng/'
EDITIONS = {'zh': ('', 'zh-Hans', '简体中文'), 'zh-hant': ('zh-hant/', 'zh-Hant', '繁體中文')}


def render():
    manuscripts = {stem: manuscript(stem) for stem in CHAPTERS}
    converter = TraditionalConverter()
    pages = {}
    try:
        for lang, (directory, code, label) in EDITIONS.items():
            def t(value):
                if not directory:
                    return value
                value = converter.convert(value)
                # Context-sensitive script choices, never changes to the author's wording.
                choices = {'城東二十裡':'城東二十里', '一乾人':'一干人', '對不准針眼':'對不準針眼', '我系了送給':'我繫了送給'}
                if stem == 'ch081':
                    choices.update({'我系了這幾年了':'我繫了這幾年了', '鄰捨':'鄰舍'})
                if stem == 'ch082':
                    choices.update({'腰系青絲':'腰繫青絲', '系一條淡':'繫一條淡', '帕子松了':'帕子鬆了', '拿不准':'拿不準', '參須':'參鬚'})
                for before, after in choices.items():
                    value = value.replace(before, after)
                return value
            def e(value):
                return html.escape(t(value))
            base = '../../../' if directory else '../../'
            up = '../' if directory else ''
            hub = base + 'essays/literature/hlm/' + directory + 'index.html'
            for filename in ('index.html', *(stem+'.html' for stem in CHAPTERS)):
                story = filename != 'index.html'
                stem = Path(filename).stem
                lines = manuscripts[stem] if story else []
                published = CHAPTERS[stem]['published'] if story else '2026-10-05'
                title = lines[0] if story else '红楼梦·后三十回'
                canonical = ORIGIN + directory + (filename if story else '')
                description = '秦汉原创《红楼梦》续写，第八十一至第一百一十回。目前公开第八十一、八十二回定稿，提供简体原文与繁体阅读版；不是曹雪芹佚稿。'
                alternatives = ''.join(f'<link rel="alternate" hreflang="{c}" href="{ORIGIN+d+(filename if story else "")}">' for d,c,_ in EDITIONS.values())
                alternatives += f'<link rel="alternate" hreflang="x-default" href="{ORIGIN+(filename if story else "")}">'
                languages = ''.join(f'<a href="{up+d+filename}" lang="{c}"'+(' aria-current="page"' if k == lang else '')+f'>{name}</a>' for k,(d,c,name) in EDITIONS.items())
                schema = {'@context':'https://schema.org','@type':'Chapter' if story else 'CollectionPage','name':t(title),'url':canonical,'inLanguage':code,'author':{'@type':'Person','name':'Han Qin (秦汉)'},'datePublished':published,'dateModified':DATE}
                if story:
                    schema['isPartOf'] = {'@type':'CreativeWork','name':t('红楼梦·后三十回'),'url':ORIGIN+directory}
                    schema['position'] = int(stem[2:])
                    paragraphs = []
                    verse_start, verse_end = CHAPTERS[stem]['verse']
                    assert lines.count(verse_start) == lines.count(verse_end) == 1
                    for number, line in enumerate(lines[1:], 2):
                        if not line: continue
                        if line == verse_start: paragraphs.append('<div class="verse">')
                        paragraphs.append(f'<p data-source-line="{number}">{e(line)}</p>')
                        if line == verse_end: paragraphs.append('</div>')
                    keys = list(CHAPTERS)
                    position = keys.index(stem)
                    previous = (f'<a href="{keys[position-1]}.html">{e("← " + CHAPTERS[keys[position-1]]["number"])}</a>' if position else '')
                    following = (f'<a href="{keys[position+1]}.html">{e(CHAPTERS[keys[position+1]]["number"] + " →")}</a>' if position+1 < len(keys) else f'<span>{e("第八十三回 · 待发布")}</span>')
                    title_parts = title.split('　')
                    heading = ''.join(f'<span class="{"chapter-number" if i==0 else "chapter-couplet"}">{e(part)}'+('　' if i<len(title_parts)-1 else '')+'</span>' for i,part in enumerate(title_parts))
                    content = f'<article><header class="chapter-head"><p class="eyebrow">{e("秦汉原创 · 红楼梦后三十回")}</p><h1>{heading}</h1><p class="edition-note">{e("定稿原文" if not directory else "定稿繁体阅读版")} · <time datetime="{published}">{published}</time></p><p class="authorship">{e("本篇是秦汉的原创续写，不是曹雪芹佚稿。")}</p></header><div class="novel-text">'+ '\n'.join(paragraphs) +f'</div></article><nav class="chapter-nav" aria-label="{e("章节导航")}">{previous}<a href="index.html">{e("返回回目")}</a>{following}</nav>'
                else:
                    schema['hasPart'] = [{'@type': 'Chapter', 'name': t(manuscripts[key][0]),
                                          'url': ORIGIN+directory+key+'.html'} for key in CHAPTERS]
                    cards = ''.join(f'<a class="chapter-card" href="{key}.html"><span>{e(manuscripts[key][0])}</span><small>{e("定稿 · 阅读正文 →")}</small></a>' for key in CHAPTERS)
                    content = f'''<header class="collection-head"><p class="eyebrow">{e('秦汉原创 · 第八十一至第一百一十回')}</p><h1>{e(title)}</h1><p class="deck">{e('从八十回以后，接着写这些人的故事。')}</p></header>
<section class="introduction"><h2>{e('关于这部续写')}</h2><p>{e('后三十回已完成，正在逐回打磨与发布。目前可读第八十一、八十二回定稿，提供简体原文与繁体阅读版。第八十三至第一百一十回尚未公开。')}</p><p>{e('这三十回是秦汉的原创小说，不是曹雪芹的佚稿，也不是对已有续书的整理；不声称恢复了曹雪芹原稿。')}</p><p>{e('可以直接开始读小说。若想了解写作背后的阅读与研究，可另访红楼梦专题；其中的论文含后续情节与结局，请按自己的阅读顺序选择。')}</p></section>
<section class="contents"><h2>{e('已发布回目')}</h2>{cards}<p class="edition-note">{e('后续回目将在定稿发布后加入。')}</p></section>'''
                pages[TARGET/directory/filename] = f'''<!DOCTYPE html>
<html lang="{code}" data-lang="{lang}" data-editions="{lang}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)} — Non Dubito</title><meta name="description" content="{e(description)}"><meta name="author" content="Han Qin (秦汉)"><link rel="canonical" href="{canonical}">{alternatives}<meta property="og:type" content="{'article' if story else 'website'}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="{canonical}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary"><link rel="icon" href="{base}favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{up}novel.css?v=20261005"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head><body><a class="skip" href="#main">{e('跳到正文')}</a><header class="site-header"><a class="brand" href="{base}index.html">Non <span>Dubito</span></a><nav aria-label="{e('网站导航')}"><a href="{base}originals/index.html">{e('原创作品')}</a><a href="{hub}">{e('红楼梦专题')}</a><a href="{base}library.html">{e('书库')}</a></nav><nav class="languages" aria-label="{e('阅读版本')}">{languages}</nav></header><main id="main">{content}</main><footer><a href="{hub}">{e('返回红楼梦专题')}</a><p>© 2026 {e('秦汉')} · Non Dubito</p></footer></body></html>
'''
    finally:
        converter.close()
    return pages


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, content in render().items():
        if args.check:
            assert path.exists() and path.read_text() == content, str(path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    print(f'{(len(CHAPTERS)+1)*len(EDITIONS)} original-fiction pages verified' if args.check else f'Built {(len(CHAPTERS)+1)*len(EDITIONS)} original-fiction pages')
