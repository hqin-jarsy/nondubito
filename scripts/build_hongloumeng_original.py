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
SOURCE = ROOT / 'data/originals/hongloumeng/ch081.zh.txt'
SHA256 = '474d903fa5d252b20a6fc6c859d165addbaff9b3037aaa24f1019016e90c3437'
DATE = '2026-10-05'
ORIGIN = 'https://nondubito.net/originals/hongloumeng/'
EDITIONS = {'zh': ('', 'zh-Hans', '简体中文'), 'zh-hant': ('zh-hant/', 'zh-Hant', '繁體中文')}


def render():
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA256, 'Final manuscript changed: obtain author approval first.'
    lines = raw.decode().splitlines()
    converter = TraditionalConverter()
    pages = {}
    try:
        for lang, (directory, code, label) in EDITIONS.items():
            def t(value):
                if not directory:
                    return value
                value = converter.convert(value)
                # Context-sensitive script choices, never changes to the author's wording.
                for before, after in {'城東二十裡':'城東二十里', '一乾人':'一干人', '對不准針眼':'對不準針眼', '我系了送給':'我繫了送給'}.items():
                    value = value.replace(before, after)
                return value
            def e(value):
                return html.escape(t(value))
            base = '../../../' if directory else '../../'
            up = '../' if directory else ''
            hub = base + 'essays/literature/hlm/' + directory + 'index.html'
            for filename in ('index.html', 'ch081.html'):
                story = filename != 'index.html'
                title = lines[0] if story else '红楼梦·后三十回'
                canonical = ORIGIN + directory + (filename if story else '')
                description = '秦汉原创《红楼梦》续写，第八十一至第一百一十回。目前公开第八十一回定稿，提供简体原文与繁体阅读版；不是曹雪芹佚稿。'
                alternatives = ''.join(f'<link rel="alternate" hreflang="{c}" href="{ORIGIN+d+(filename if story else "")}">' for d,c,_ in EDITIONS.values())
                alternatives += f'<link rel="alternate" hreflang="x-default" href="{ORIGIN+(filename if story else "")}">'
                languages = ''.join(f'<a href="{up+d+filename}" lang="{c}"'+(' aria-current="page"' if k == lang else '')+f'>{name}</a>' for k,(d,c,name) in EDITIONS.items())
                schema = {'@context':'https://schema.org','@type':'Chapter' if story else 'CollectionPage','name':t(title),'url':canonical,'inLanguage':code,'author':{'@type':'Person','name':'Han Qin (秦汉)'},'datePublished':DATE,'dateModified':DATE}
                if story:
                    schema['isPartOf'] = {'@type':'CreativeWork','name':t('红楼梦·后三十回'),'url':ORIGIN+directory}
                    paragraphs = []
                    for number, line in enumerate(lines[1:], 2):
                        if not line: continue
                        if number == 94: paragraphs.append('<div class="verse">')
                        paragraphs.append(f'<p data-source-line="{number}">{e(line)}</p>')
                        if number == 101: paragraphs.append('</div>')
                    assert lines[93] == '抛红豆，滴相思。' and lines[100] == '任凭风雨误花期。'
                    title_parts = title.split('　')
                    heading = ''.join(f'<span class="{"chapter-number" if i==0 else "chapter-couplet"}">{e(part)}'+('　' if i<len(title_parts)-1 else '')+'</span>' for i,part in enumerate(title_parts))
                    content = f'<article><header class="chapter-head"><p class="eyebrow">{e("秦汉原创 · 红楼梦后三十回")}</p><h1>{heading}</h1><p class="edition-note">{e("定稿原文" if not directory else "定稿繁体阅读版")} · <time datetime="{DATE}">{DATE}</time></p><p class="authorship">{e("本篇是秦汉的原创续写，不是曹雪芹佚稿。")}</p></header><div class="novel-text">'+ '\n'.join(paragraphs) +f'</div></article><nav class="chapter-nav" aria-label="{e("章节导航")}"><a href="index.html">{e("← 返回回目")}</a><span>{e("第八十二回 · 待发布")}</span></nav>'
                else:
                    content = f'''<header class="collection-head"><p class="eyebrow">{e('秦汉原创 · 第八十一至第一百一十回')}</p><h1>{e(title)}</h1><p class="deck">{e('从八十回以后，接着写这些人的故事。')}</p></header>
<section class="introduction"><h2>{e('关于这部续写')}</h2><p>{e('后三十回已完成，正在逐回打磨与发布。目前可读第八十一回定稿，提供简体原文与繁体阅读版。第八十二至第一百一十回尚未公开。')}</p><p>{e('这三十回是秦汉的原创小说，不是曹雪芹的佚稿，也不是对已有续书的整理；不声称恢复了曹雪芹原稿。')}</p><p>{e('可以直接开始读小说。若想了解写作背后的阅读与研究，可另访红楼梦专题；其中的论文含后续情节与结局，请按自己的阅读顺序选择。')}</p></section>
<section class="contents"><h2>{e('已发布回目')}</h2><a class="chapter-card" href="ch081.html"><span>{e(lines[0])}</span><small>{e('定稿 · 阅读正文 →')}</small></a><p class="edition-note">{e('后续回目将在定稿发布后加入。')}</p></section>'''
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
    print('Four original-fiction pages verified' if args.check else 'Built four original-fiction pages')
