#!/usr/bin/env python3
"""Build edited Zhuangzi reading editions, not unreviewed source-folder drafts.

Normal builds are portable and read committed Markdown. --refresh-hant is an
explicit macOS-only first pass; its output must receive editorial review.
"""
from __future__ import annotations
import argparse
import html
import json
import re
from pathlib import Path
from build_ai_work_series import shell_header, footer, tri

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/zhuangzi'
TARGET = ROOT / 'essays/zhuangzi'
LANGS = {'en': 'en', 'zh': 'zh-Hans', 'zh-hant': 'zh-Hant'}
CLASS = {'en': 'lang-en', 'zh': 'lang-zh', 'zh-hant': 'lang-hant'}
NAMES = ('The Zhuangzi, Reopened', '大知解庄子', '大知解莊子')
DECK = ('Stories that leave you something to discover. A guide and sixty-seven essays on how the Zhuangzi speaks—and where it stops.', '不只看庄子说了什么，也看他怎样说、在哪里停。一篇导读与六十七篇散文，从熟悉的故事重新走进去。', '不只看莊子說了什麼，也看他怎樣說、在哪裡停。一篇導讀與六十七篇散文，從熟悉的故事重新走進去。')
GROUPS = [
    ('encounters', '01–10', ('Ten Encounters', '先从十个故事开始', '先從十個故事開始')),
    ('inner', '11–29', ('Through the Inner Chapters', '内篇七课', '內篇七課')),
    ('discernment', '30–41 · 59–65', ('Voices, Layers, and Interpretation', '文本辨析：理由与限度', '文本辨析：理由與限度')),
    ('outer', '42–58', ('Lives and Skills in the Outer Chapters', '外篇：技艺与生活', '外篇：技藝與生活')),
    ('closing', '66–67', ('Turning the Reading Back on Itself', '回看这套读法', '回看這套讀法')),
]
RESEARCH = [
    ('Inner Chapters · Forgetting in Rivers and Lakes', '内篇《忘江湖》', '內篇《忘江湖》', '20406836'),
    ('Outer Chapters I · Readings', '外篇上（解读篇）', '外篇上（解讀篇）', '20578136'),
    ('Outer Chapters II · Textual Discernment', '外篇下（鉴别篇）', '外篇下（鑑別篇）', '20579135'),
    ('Miscellaneous Chapters', '杂篇', '雜篇', '20708990'),
]
CHAPTERS = {
    1: ('Chapter 7 · Responding to Rulers', '《应帝王》', '《應帝王》', 'https://zh.wikisource.org/wiki/莊子/應帝王'),
    2: ('Chapter 18 · Perfect Enjoyment', '《至乐》', '《至樂》', 'https://zh.wikisource.org/wiki/莊子/至樂'),
    3: ('Chapter 17 · Autumn Floods', '《秋水》', '《秋水》', 'https://zh.wikisource.org/wiki/莊子/秋水'),
    4: ('Chapter 24 · Xu Wugui', '《徐无鬼》', '《徐無鬼》', 'https://zh.wikisource.org/wiki/莊子/徐無鬼'),
    5: ('Chapter 27 · Borrowed Words', '《寓言》', '《寓言》', 'https://zh.wikisource.org/wiki/莊子/寓言'),
}

def traditional_copy(converter, text):
    text = converter.convert(text)
    for before, after in {
        '沈默':'沉默', '瞭解':'了解', '想象':'想像', '余項':'餘項',
        '反復':'反覆', '硅谷':'矽谷', '這麼乾':'這麼做',
        '校准':'校準', '准不准':'準不準', '很准':'很準', '同樣准':'同樣準',
        '鑒定':'鑑定', '九萬裡':'九萬里', '瞭望洋':'了望洋',
        '那只':'那隻', '這只':'這隻', '捨者':'舍者', '客捨':'客舍',
        '至捨':'至舍', '最難松':'最難鬆',
    }.items(): text = text.replace(before, after)
    return text

def esc(s):
    return html.escape(str(s), quote=True)

def title(item):
    return (item['en_title'], item['zh_title'], item['hant_title'])

def filename(n):
    return 'guide.html' if n == 0 else f'{n:02d}.html'

def prose(raw, language):
    """Narrow Markdown: headings, paragraphs, quotes. Escape source HTML."""
    blocks = re.split(r'\n\s*\n', raw.strip())
    output, pending = [], ''
    def flush():
        nonlocal pending
        if pending:
            output.append('<p>' + esc(pending) + '</p>')
            pending = ''
    for b in blocks:
        b = b.strip()
        if b == '---':
            flush(); continue
        if b.startswith('## '):
            flush(); output.append('<h2>' + esc(b[3:]) + '</h2>')
        elif b.startswith('>'):
            flush()
            q = '\n'.join(line.removeprefix('>').strip() for line in b.splitlines())
            output.append('<blockquote><p>' + esc(q) + '</p></blockquote>')
        else:
            text = (' ' if language == 'en' else '').join(b.splitlines())
            if language != 'en' and len(pending) + len(text) <= 200 and not text.startswith(('第一：', '第二：', '第三：')):
                pending += text
            else:
                flush(); pending = text
    flush()
    return '\n'.join(output)

def head(name, deck, file, kind, date):
    url = 'https://nondubito.net/essays/zhuangzi/' + ('' if file == 'index.html' else file)
    schema = {'@context':'https://schema.org', '@type':kind, 'name':name,
              'description':deck, 'url':url, 'inLanguage':list(LANGS.values()),
              'author':{'@type':'Person','name':'Han Qin (秦汉)'},
              'datePublished':date, 'dateModified':date}
    alternates = ''.join(f'<link rel="alternate" hreflang="{lang}" href="{url}">' for lang in (*LANGS.values(), 'x-default'))
    return f'''<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(name)} — Non Dubito</title><meta name="description" content="{esc(deck)}"><meta name="author" content="Han Qin (秦汉)">
<link rel="canonical" href="{url}">{alternates}
<meta property="og:type" content="{'article' if kind == 'Article' else 'website'}"><meta property="og:title" content="{esc(name)}"><meta property="og:description" content="{esc(deck)}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary">
<link rel="icon" href="../../favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&amp;family=Inter:wght@400;500&amp;family=Noto+Serif+SC:wght@400;500&amp;family=Noto+Serif+TC:wght@400;500&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="../../site-shell.css?v=20260905b"><link rel="stylesheet" href="../../reading-context.css?v=20260905a"><link rel="stylesheet" href="series.css?v=20260920">
<script src="../../site-shell.js?v=20260905b"></script>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>'''

def page(body, name, description, file, date, kind):
    return f'''<!DOCTYPE html>
<html lang="en" data-lang="en" data-editions="en zh zh-hant">
{head(name, description, file, kind, date)}
<body class="site-shell-page explicit-hant">{shell_header()}
<main class="zz-wrap">{body}</main>{footer()}
</body></html>\n'''

def research():
    links = ''.join(f'<li><a href="https://doi.org/10.5281/zenodo.{doi}">{tri(en, zh, hant)} ↗</a></li>' for en, zh, hant, doi in RESEARCH)
    return f'''<aside class="zz-research" id="research"><h2>{tri('For a deeper reading','想读得更深','想讀得更深')}</h2><p>{tri('Four companion volumes by the author. The essays stand on their own; no prior theoretical reading is required.','四卷理论底本放在这里。散文可以独立阅读，不需要先读论文。','四卷理論底本放在這裡。散文可以獨立閱讀，不需要先讀論文。')}</p><ul>{links}</ul></aside>'''

def render_index(manifest):
    items, published = manifest['items'], set(manifest['published'])
    count = len(published - {0})
    cards = []
    for item in items:
        n = item['number']
        if n not in published: continue
        cards.append(f'<a class="zz-card" href="{filename(n)}"><small>{"00 / GUIDE" if n == 0 else f"{n:02d}"}</small>{tri(*map(esc,title(item)),tag="h3")}<span aria-hidden="true">→</span></a>')
    group_nav = ''.join(f'<a href="#{key}">{tri(*labels)}</a>' for key, _, labels in GROUPS)
    def row(item):
        n = item['number']; label = f'<span class="zz-number">{n:02d}</span>' + tri(*map(esc,title(item)))
        return f'<li><a href="{filename(n)}">{label}</a></li>' if n in published else f'<li class="zz-pending">{label}<small>{tri("In preparation","编辑中","編輯中")}</small></li>'
    sections = ''.join(f'<section class="zz-group" id="{key}"><p class="zz-eyebrow">{numbers}</p><h2>{tri(*labels)}</h2><ol class="zz-toc">{"".join(row(i) for i in items if i["group"] == key)}</ol></section>' for key, numbers, labels in GROUPS)
    sequence = ''.join(row(i) for i in items if i['number'])
    body = f'''<nav class="reading-breadcrumbs"><a href="../../library.html">{tri('Library','文库','文庫')}</a><span>/</span><span>{tri('Chinese Classics','中国经典','中國經典')}</span></nav>
<section class="zz-hero"><p class="zz-eyebrow">NON DUBITO · CHINESE CLASSICS</p>{tri(*NAMES,tag='h1')}{tri(*DECK,tag='p',classes='zhuangzi-search-deck zz-deck')}<p class="zz-progress">{tri(f'Available now: the guide + {count} of 67 essays. All completed pages offer English, Simplified and Traditional Chinese.',f'目前可读：导读＋{count}/67 篇正文。已完成页面均提供英文、简体与繁体。',f'目前可讀：導讀＋{count}/67 篇正文。已完成頁面均提供英文、簡體與繁體。')}</p></section>
<section class="zz-entrances"><h2>{tri('Find a way in','从哪儿读','從哪裡讀')}</h2><div class="zz-routes">
<a href="01.html">{tri('Begin with a story →','先读一个故事 →','先讀一個故事 →')}<small>{tri('Hundun, or the person who stood still: essays 1 and 4.','浑沌之死、运斤成风：第 1、4 篇。','渾沌之死、運斤成風：第 1、4 篇。')}</small></a>
<a href="#inner">{tri('Follow the Inner Chapters','走进内篇七课','走進內篇七課')}<small>{tri('See the route · 11–29 · in preparation','查看路线 · 11—29 · 编辑中','查看路線 · 11—29 · 編輯中')}</small></a>
<a href="#discernment">{tri('How do we judge a passage?','怎样辨析一段文字','怎樣辨析一段文字')}<small>{tri('Reasons and limits · begins at 30 · in preparation','理由与限度 · 从 30 起 · 编辑中','理由與限度 · 從 30 起 · 編輯中')}</small></a>
<a href="#outer">{tri('Meet the people who do things','看看那些做事的人','看看那些做事的人')}<small>{tri('Craft, attention, life · begins at 42 · in preparation','技艺、专注与生活 · 从 42 起 · 编辑中','技藝、專注與生活 · 從 42 起 · 編輯中')}</small></a></div></section>
<section><h2>{tri('Ready to read','现在可以读','現在可以讀')}</h2><div class="zz-grid">{''.join(cards)}</div></section>
<section class="zz-map" id="contents"><h2>{tri('The complete reading map','全系列阅读地图','全系列閱讀地圖')}</h2><p>{tri('The original numbers are retained. Essays 59–65 return to textual discernment; 66–67 close the series. Unlinked entries are still being edited.','保留原编号。59—65 回到文本辨析，66—67 收束全系列。未加链接的篇目仍在编辑，不是空白文章。','保留原編號。59—65 回到文本辨析，66—67 收束全系列。未加連結的篇目仍在編輯，不是空白文章。')}</p><nav class="zz-group-nav" aria-label="Reading groups">{group_nav}</nav>{sections}<details class="zz-sequence"><summary>{tri('Or browse in original order, 01–67','按原编号顺读：01—67','按原編號順讀：01—67')}</summary><ol class="zz-toc">{sequence}</ol></details></section>
{research()}<nav class="zz-siblings"><a href="../daodejing/index.html">{tri('The Daodejing','大知道德经解','大知道德經解')} →</a><a href="../analects/index.html">{tri('The Analects, Reopened','大知解论语','大知解論語')} →</a></nav>'''
    return page(body, ' · '.join(NAMES[:2]), DECK[0], 'index.html', manifest['publication_date'], 'CollectionPage')

def render_article(item, manifest):
    n = item['number']; published = sorted(manifest['published']); pos = published.index(n)
    previous = f'<a href="{filename(published[pos-1])}">← {tri("Previous","上一篇","上一篇")}</a>' if pos else '<span></span>'
    following = f'<a href="{filename(published[pos+1])}">{tri("Next","下一篇","下一篇")} →</a>' if pos+1 < len(published) else f'<a href="index.html#contents">{tri("Reading map","阅读地图","閱讀地圖")} →</a>'
    bodies = []
    for lang in LANGS:
        path = DATA / lang / f'{n:02d}.md'
        raw = path.read_text()
        bodies.append(f'<article class="essay-body {CLASS[lang]}" lang="{LANGS[lang]}">{prose(raw,lang)}</article>')
    note = ''
    if n:
        en,zh,hant,url = CHAPTERS[n]
        note = f'<aside class="zz-source"><p>{tri("Passage and reading","原文与读法","原文與讀法")}: <a href="{url}">{tri(en,zh,hant)} ↗</a></p><p>{tri("The Chinese page quotes the classical text. English retellings are written for this edition. Interpretive extensions and contemporary comparisons are the author’s readings, not additional events reported in the original.","中文页保留古文引文；英文叙述为本版重写。文中的当代类比与进一步发挥属于作者的读法，不是原文另有交代的情节。","中文頁保留古文引文；英文敘述為本版重寫。文中的當代類比與進一步發揮屬於作者的讀法，不是原文另有交代的情節。")}</p><a href="index.html#research">{tri("The four companion volumes","查看四卷理论底本","查看四卷理論底本")} →</a></aside>'
    else: note = research()
    description = item['en_title'] + '. A reader essay in The Zhuangzi, Reopened: stories, relationships, and the space left for another person.'
    deck = (description, item['zh_title']+'。从故事与细节出发，重新看见人与人之间留给彼此的空间。', item['hant_title']+'。從故事與細節出發，重新看見人與人之間留給彼此的空間。')
    body = f'''<nav class="reading-breadcrumbs"><a href="index.html">{tri(*NAMES)}</a><span>/</span><span>{'00 / GUIDE' if n == 0 else f'{n:02d} / 67'}</span></nav>
<section class="zz-article-hero"><p class="zz-eyebrow">{tri('The Zhuangzi, Reopened','大知解庄子','大知解莊子')}</p>{tri(*map(esc,title(item)),tag='h1')}<p class="zz-byline">{tri('Han Qin · Dazhi','秦汉（字大知）','秦漢（字大知）')} · 2026</p><div class="zz-search-only">{tri(*map(esc,deck),tag='p',classes='zhuangzi-search-deck')}</div></section>
{''.join(bodies)}{note}<nav class="zz-article-nav" aria-label="Series navigation">{previous}<a href="index.html">{tri('All essays','系列目录','系列目錄')}</a>{following}</nav>'''
    return page(body, item['en_title']+' · '+item['zh_title'], description, filename(n), manifest['publication_date'], 'Article')

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); parser.add_argument('--refresh-hant',action='store_true'); args=parser.parse_args()
    if args.check and args.refresh_hant: parser.error('Do not combine --check and --refresh-hant')
    manifest=json.loads((DATA/'manifest.json').read_text())
    assert [i['number'] for i in manifest['items']] == list(range(68))
    assert set(manifest['published']) <= set(range(68)) and 0 in manifest['published']
    if args.refresh_hant:
        from build_ai_work_series import TraditionalConverter
        c=TraditionalConverter()
        try:
            (DATA/'zh-hant').mkdir(exist_ok=True)
            for n in manifest['published']:
                text=traditional_copy(c,(DATA/'zh'/f'{n:02d}.md').read_text())
                (DATA/'zh-hant'/f'{n:02d}.md').write_text(text)
            for item in manifest['items']: item['hant_title']=traditional_copy(c,item['zh_title'])
            (DATA/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        finally: c.close()
        print('Traditional Chinese draft refreshed; editorial rereading is required.')
    expected={'index.html':render_index(manifest)}
    for item in manifest['items']:
        if item['number'] in manifest['published']: expected[filename(item['number'])]=render_article(item,manifest)
    stale=[name for name,text in expected.items() if not (TARGET/name).exists() or (TARGET/name).read_text()!=text]
    if args.check:
        if stale: raise SystemExit('Stale pages: '+', '.join(stale))
        print(f'OK: {len(expected)} Zhuangzi pages'); return
    TARGET.mkdir(parents=True,exist_ok=True)
    for name,text in expected.items(): (TARGET/name).write_text(text)
    print(f'Built {len(expected)} Zhuangzi pages: index, guide, {len(expected)-2} essays.')

if __name__=='__main__': main()
