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
    6: ('Chapter 3 · Nourishing Life', '《养生主》', '《養生主》', 'https://zh.wikisource.org/wiki/莊子/養生主'),
    7: ('Chapter 21 · Tian Zifang', '《田子方》', '《田子方》', 'https://zh.wikisource.org/wiki/莊子/田子方'),
    8: ('Chapter 17 · Autumn Floods', '《秋水》', '《秋水》', 'https://zh.wikisource.org/wiki/莊子/秋水'),
    9: ('Chapter 32 · Lie Yukou', '《列御寇》', '《列禦寇》', 'https://zh.wikisource.org/wiki/莊子/列禦寇'),
    10: ('Chapter 32 · Lie Yukou', '《列御寇》', '《列禦寇》', 'https://zh.wikisource.org/wiki/莊子/列禦寇'),
    11: ('The seven Inner Chapters · reading map', '内篇七篇：阅读路线', '內篇七篇：閱讀路線', 'https://zh.wikisource.org/wiki/莊子'),
    12: ('Chapter 1 · Free and Easy Wandering', '《逍遥游》', '《逍遙遊》', 'https://zh.wikisource.org/wiki/莊子/逍遙遊'),
    13: ('Chapter 1 · Free and Easy Wandering', '《逍遥游》', '《逍遙遊》', 'https://zh.wikisource.org/wiki/莊子/逍遙遊'),
    14: ('Chapter 1 · Free and Easy Wandering', '《逍遥游》', '《逍遙遊》', 'https://zh.wikisource.org/wiki/莊子/逍遙遊'),
    15: ('Chapter 2 · Discussion on Making All Things Equal', '《齐物论》', '《齊物論》', 'https://zh.wikisource.org/wiki/莊子/齊物論'),
    16: ('Chapter 2 · Discussion on Making All Things Equal', '《齐物论》', '《齊物論》', 'https://zh.wikisource.org/wiki/莊子/齊物論'),
    17: ('Chapter 2 · Discussion on Making All Things Equal', '《齐物论》', '《齊物論》', 'https://zh.wikisource.org/wiki/莊子/齊物論'),
    18: ('Chapter 3 · Nourishing Life', '《养生主》', '《養生主》', 'https://zh.wikisource.org/wiki/莊子/養生主'),
    19: ('Chapter 3 · Nourishing Life', '《养生主》', '《養生主》', 'https://zh.wikisource.org/wiki/莊子/養生主'),
    20: ('Chapter 4 · In the Human World', '《人间世》', '《人間世》', 'https://zh.wikisource.org/wiki/莊子/人間世'),
    21: ('Chapter 4 · In the Human World', '《人间世》', '《人間世》', 'https://zh.wikisource.org/wiki/莊子/人間世'),
    22: ('Chapter 4 · In the Human World', '《人间世》', '《人間世》', 'https://zh.wikisource.org/wiki/莊子/人間世'),
    23: ('Chapter 5 · Signs of Complete Virtue', '《德充符》', '《德充符》', 'https://zh.wikisource.org/wiki/莊子/德充符'),
    24: ('Chapter 5 · Signs of Complete Virtue', '《德充符》', '《德充符》', 'https://zh.wikisource.org/wiki/莊子/德充符'),
    25: ('Chapter 6 · The Great Ancestral Teacher', '《大宗师》', '《大宗師》', 'https://zh.wikisource.org/wiki/莊子/大宗師'),
    26: ('Chapter 6 · The Great Ancestral Teacher', '《大宗师》', '《大宗師》', 'https://zh.wikisource.org/wiki/莊子/大宗師'),
    27: ('Chapter 6 · The Great Ancestral Teacher', '《大宗师》', '《大宗師》', 'https://zh.wikisource.org/wiki/莊子/大宗師'),
    28: ('Chapter 7 · Responding to Rulers', '《应帝王》', '《應帝王》', 'https://zh.wikisource.org/wiki/莊子/應帝王'),
    29: ('Chapter 7 · Responding to Rulers', '《应帝王》', '《應帝王》', 'https://zh.wikisource.org/wiki/莊子/應帝王'),
    30: ('Su Shi · Memorial for a Shrine to Zhuangzi', '苏轼《庄子祠堂记》', '蘇軾《莊子祠堂記》', 'https://zh.wikisource.org/wiki/莊子祠堂記'),
    31: ('Chapter 13 · The Way of Heaven', '《天道》', '《天道》', 'https://zh.wikisource.org/wiki/莊子/天道'),
    32: ('Chapter 14 · The Turning of Heaven', '《天运》', '《天運》', 'https://zh.wikisource.org/wiki/莊子/天運'),
    33: ('Chapter 13 · The Way of Heaven', '《天道》', '《天道》', 'https://zh.wikisource.org/wiki/莊子/天道'),
    34: ("Chapter 9 · Horses’ Hooves", '《马蹄》', '《馬蹄》', 'https://zh.wikisource.org/wiki/莊子/馬蹄'),
    35: ('Chapter 29 · Robber Zhi', '《盗跖》', '《盜跖》', 'https://zh.wikisource.org/wiki/莊子/盜跖'),
    36: ('Chapter 28 · Yielding Kingship', '《让王》', '《讓王》', 'https://zh.wikisource.org/wiki/莊子/讓王'),
    37: ('Chapter 28 · Yielding Kingship', '《让王》', '《讓王》', 'https://zh.wikisource.org/wiki/莊子/讓王'),
    38: ('Chapter 30 · Speaking of Swords', '《说剑》', '《說劍》', 'https://zh.wikisource.org/wiki/莊子/說劍'),
    39: ('Chapter 31 · The Fisherman', '《渔父》', '《漁父》', 'https://zh.wikisource.org/wiki/莊子/漁父'),
    40: ('Chapter 24 · Xu Wugui', '《徐无鬼》', '《徐無鬼》', 'https://zh.wikisource.org/wiki/莊子/徐無鬼'),
    41: ('Chapter 23 · Gengsang Chu', '《庚桑楚》', '《庚桑楚》', 'https://zh.wikisource.org/wiki/莊子/庚桑楚'),
    42: ('Chapter 19 · Understanding Life', '《达生》', '《達生》', 'https://zh.wikisource.org/wiki/莊子/達生'),
    43: ('Chapter 19 · Understanding Life', '《达生》', '《達生》', 'https://zh.wikisource.org/wiki/莊子/達生'),
    44: ('Chapter 19 · Understanding Life', '《达生》', '《達生》', 'https://zh.wikisource.org/wiki/莊子/達生'),
    45: ('Chapter 19 · Understanding Life', '《达生》', '《達生》', 'https://zh.wikisource.org/wiki/莊子/達生'),
    46: ('Chapter 19 · Understanding Life', '《达生》', '《達生》', 'https://zh.wikisource.org/wiki/莊子/達生'),
    47: ('Chapter 17 · Autumn Floods', '《秋水》', '《秋水》', 'https://zh.wikisource.org/wiki/莊子/秋水'),
    48: ('Chapter 17 · Autumn Floods', '《秋水》', '《秋水》', 'https://zh.wikisource.org/wiki/莊子/秋水'),
    49: ('Chapter 17 · Autumn Floods', '《秋水》', '《秋水》', 'https://zh.wikisource.org/wiki/莊子/秋水'),
    50: ('Chapter 21 · Tian Zifang', '《田子方》', '《田子方》', 'https://zh.wikisource.org/wiki/莊子/田子方'),
    51: ('Chapter 21 · Tian Zifang', '《田子方》', '《田子方》', 'https://zh.wikisource.org/wiki/莊子/田子方'),
    52: ('Chapter 18 · Perfect Enjoyment', '《至乐》', '《至樂》', 'https://zh.wikisource.org/wiki/莊子/至樂'),
    53: ('Chapter 18 · Perfect Enjoyment', '《至乐》', '《至樂》', 'https://zh.wikisource.org/wiki/莊子/至樂'),
    54: ('Chapter 20 · The Mountain Tree', '《山木》', '《山木》', 'https://zh.wikisource.org/wiki/莊子/山木'),
    55: ('Chapter 20 · The Mountain Tree', '《山木》', '《山木》', 'https://zh.wikisource.org/wiki/莊子/山木'),
    56: ('Chapter 22 · Knowledge Wandered North', '《知北游》', '《知北遊》', 'https://zh.wikisource.org/wiki/莊子/知北遊'),
    57: ('Chapter 22 · Knowledge Wandered North', '《知北游》', '《知北遊》', 'https://zh.wikisource.org/wiki/莊子/知北遊'),
    58: ('Chapter 22 · Knowledge Wandered North', '《知北游》', '《知北遊》', 'https://zh.wikisource.org/wiki/莊子/知北遊'),
    59: ('Chapter 25 · Zeyang', '《则阳》', '《則陽》', 'https://zh.wikisource.org/wiki/莊子/則陽'),
    60: ('Chapter 25 · Zeyang', '《则阳》', '《則陽》', 'https://zh.wikisource.org/wiki/莊子/則陽'),
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

def head(name, deck, file, kind, date, modified=None):
    url = 'https://nondubito.net/essays/zhuangzi/' + ('' if file == 'index.html' else file)
    schema = {'@context':'https://schema.org', '@type':kind, 'name':name,
              'description':deck, 'url':url, 'inLanguage':list(LANGS.values()),
              'author':{'@type':'Person','name':'Han Qin (秦汉)'},
              'datePublished':date, 'dateModified':modified or date}
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

def page(body, name, description, file, date, kind, modified=None):
    return f'''<!DOCTYPE html>
<html lang="en" data-lang="en" data-editions="en zh zh-hant">
{head(name, description, file, kind, date, modified)}
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
<a href="11.html">{tri('Follow the Inner Chapters →','走进内篇七课 →','走進內篇七課 →')}<small>{tri('Begin at 11 · essays 11–29 available · this route is complete','从 11 开始 · 11—29 已可读 · 本辑完整','從 11 開始 · 11—29 已可讀 · 本輯完整')}</small></a>
<a href="30.html">{tri('How do we judge a passage? →','怎样辨析一段文字 →','怎樣辨析一段文字 →')}<small>{tri('Reasons and limits · essays 30–41 and 59–60 available · more to come','理由与限度 · 30—41、59—60 已可读 · 后续编辑中','理由與限度 · 30—41、59—60 已可讀 · 後續編輯中')}</small></a>
<a href="42.html">{tri('Meet the people who do things →','看看那些做事的人 →','看看那些做事的人 →')}<small>{tri('Craft, attention, life · essays 42–58 available · this route is complete','技艺、专注与生活 · 42—58 已可读 · 本辑完整','技藝、專注與生活 · 42—58 已可讀 · 本輯完整')}</small></a></div></section>
<section><h2>{tri('Ready to read','现在可以读','現在可以讀')}</h2><div class="zz-grid">{''.join(cards)}</div></section>
<section class="zz-map" id="contents"><h2>{tri('The complete reading map','全系列阅读地图','全系列閱讀地圖')}</h2><p>{tri('The original numbers are retained. Essays 59–65 return to textual discernment; 66–67 close the series. Unlinked entries are still being edited.','保留原编号。59—65 回到文本辨析，66—67 收束全系列。未加链接的篇目仍在编辑，不是空白文章。','保留原編號。59—65 回到文本辨析，66—67 收束全系列。未加連結的篇目仍在編輯，不是空白文章。')}</p><nav class="zz-group-nav" aria-label="Reading groups">{group_nav}</nav>{sections}<details class="zz-sequence"><summary>{tri('Or browse in original order, 01–67','按原编号顺读：01—67','按原編號順讀：01—67')}</summary><ol class="zz-toc">{sequence}</ol></details></section>
{research()}<nav class="zz-siblings"><a href="../daodejing/index.html">{tri('The Daodejing','大知道德经解','大知道德經解')} →</a><a href="../analects/index.html">{tri('The Analects, Reopened','大知解论语','大知解論語')} →</a></nav>'''
    return page(body, ' · '.join(NAMES[:2]), DECK[0], 'index.html', manifest['publication_date'], 'CollectionPage', manifest.get('updated_date'))

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
    if n == 11:
        note = f'''<aside class="zz-source"><p>{tri('Reading route','阅读路线','閱讀路線')}: <a href="{CHAPTERS[11][3]}">{tri('The seven Inner Chapters','《庄子》内篇七篇','《莊子》內篇七篇')} ↗</a></p><p>{tri('The seven lessons are the author’s interpretive route, not an established ancient syllabus. Each essay can also be read independently.','“内篇七课”是作者提出的连读路线，不是已经证实的古代课程安排；各篇仍可独立阅读。','「內篇七課」是作者提出的連讀路線，不是已經證實的古代課程安排；各篇仍可獨立閱讀。')}</p><a href="index.html#research">{tri('The four companion volumes','查看四卷理论底本','查看四卷理論底本')} →</a></aside>'''
    if n in (18,19):
        references = f'''<p>{tri('Commentaries compared','参读注本','參讀注本')}: <a href="https://www.chineseclassic.com/content/445">{tri('Zhuangzi Jishi · Nourishing Life','《庄子集释·养生主》','《莊子集釋・養生主》')} ↗</a> · <a href="https://zh.wikisource.org/zh-hant/莊子口義_(四庫全書本)/全覽">{tri('Lin Xiyi’s Zhuangzi Kouyi','林希逸《庄子口义》','林希逸《莊子口義》')} ↗</a></p>'''
        if n == 19:
            references += f'''<p>{tri('This essay follows the reading that the disciple challenges insufficient mourning. Guo Xiang instead reads the question as surprise that Qin Shi mourned at all. The referent of “that person” also differs across commentaries; the essay follows the reading directed toward Lao Dan.','本文沿着弟子嫌吊唁不够尽情的读法展开；郭象则把追问读成对秦失竟然号哭的惊讶。“其人”所指也有分歧，本文采用指向老聃的读法。','本文沿著弟子嫌弔唁不夠盡情的讀法展開；郭象則把追問讀成對秦失竟然號哭的驚訝。「其人」所指也有分歧，本文採用指向老聃的讀法。')}</p>'''
        note = note.replace('</aside>',references+'</aside>')
    if n == 22:
        references = f'''<p>{tri('Commentary on Shu’s work and the shrine oak','参读支离疏营生与社树的注释','參讀支離疏營生與社樹的注釋')}: <a href="https://www.chineseclassic.com/content/446">{tri('Zhuangzi Jishi · In the Human World','《庄子集释·人间世》','《莊子集釋・人間世》')} ↗</a></p>'''
        note = note.replace('</aside>',references+'</aside>')
    if n == 30:
        references = f'''<p>{tri('Records of the transmitted text','传本记录','傳本記錄')}: <a href="https://zh.wikisource.org/wiki/漢書/卷030">{tri('History of the Han · Bibliographic Treatise','《汉书·艺文志》','《漢書・藝文志》')} ↗</a> · <a href="https://www.chineseclassic.com/content/441">{tri('Lu Deming · Preface to the Jingdian Shiwen','陆德明《经典释文序录》','陸德明《經典釋文序錄》')} ↗</a></p><p>{tri('An interpretation of a passage, a hypothesis about textual layers, and an attribution to a historical author require different kinds and degrees of evidence.','段落的解释、文本层次的假说、历史作者的归属，需要分别说明证据，不能自动互相代替。','段落的解釋、文本層次的假說、歷史作者的歸屬，需要分別說明證據，不能自動互相代替。')}</p>'''
        note = note.replace('</aside>',references+'</aside>')
    if n == 31:
        references = f'''<p>{tri('Commentary on the wheelwright and the limits of transmission','参读轮扁与言传限度的注释','參讀輪扁與言傳限度的注釋')}: <a href="https://www.chineseclassic.com/content/477">{tri('Zhuangzi Jishi · The Way of Heaven','《庄子集释·天道》','《莊子集釋・天道》')} ↗</a></p>'''
        note = note.replace('</aside>',references+'</aside>')
    if n == 32:
        references = f'''<p>{tri('Commentary identifying Shang with Song','参读“商”即宋的旧注','參讀「商」即宋的舊注')}: <a href="https://www.chinulture.com/ebook/read/341562/514497?lang=zh">{tri('Zhuangzi Jishi · The Turning of Heaven','《庄子集释·天运》','《莊子集釋・天運》')} ↗</a></p>'''
        note = note.replace('</aside>',references+'</aside>')
    if n in (36,38):
        references = f'''<p>{tri('Su Shi’s different objections to the four chapters','参读苏轼对四篇的不同疑问','參讀蘇軾對四篇的不同疑問')}: <a href="https://zh.wikisource.org/wiki/莊子祠堂記">{tri('Memorial for a Shrine to Zhuangzi','《庄子祠堂记》','《莊子祠堂記》')} ↗</a></p>'''
        note = note.replace('</aside>',references+'</aside>')
    if n == 35:
        references = f'''<p>{tri('This essay concerns the chapter’s first encounter. The imagined continuation is the essayist’s exercise, not an ancient passage or a reconstruction of a lost original.','本文讨论本篇第一场相见。另写的后续只是散文作者的写作尝试，不是古文，也不是失落原稿的复原。','本文討論本篇第一場相見。另寫的後續只是散文作者的寫作嘗試，不是古文，也不是失落原稿的復原。')}</p>'''
        note = note.replace('</aside>',references+'</aside>')
    if 41 <= n <= 45:
        commentary_id = 487 if n == 41 else 483
        commentary_name = ('Gengsang Chu','庚桑楚','庚桑楚') if n == 41 else ('Understanding Life','达生','達生')
        references = f'''<p>{tri('Commentaries compared','参读注本','參讀注本')}: <a href="https://www.chineseclassic.com/content/{commentary_id}">{tri('Zhuangzi Jishi · '+commentary_name[0],'《庄子集释·'+commentary_name[1]+'》','《莊子集釋・'+commentary_name[2]+'》')} ↗</a></p>'''
        note = note.replace('</aside>',references+'</aside>')
    if 47 <= n <= 50:
        commentary_id = 485 if n == 50 else 481
        commentary_name = ('Tian Zifang','田子方','田子方') if n == 50 else ('Autumn Floods','秋水','秋水')
        references = f'''<p>{tri('Commentaries compared','参读注本','參讀注本')}: <a href="https://www.chineseclassic.com/content/{commentary_id}">{tri('Zhuangzi Jishi · '+commentary_name[0],'《庄子集释·'+commentary_name[1]+'》','《莊子集釋・'+commentary_name[2]+'》')} ↗</a></p>'''
        note = note.replace('</aside>',references+'</aside>')
    if 51 <= n <= 55:
        commentary_id, commentary_name = (485, ('Tian Zifang','田子方','田子方')) if n == 51 else ((482, ('Perfect Enjoyment','至乐','至樂')) if n <= 53 else (484, ('The Mountain Tree','山木','山木')))
        references = f'''<p>{tri('Commentaries compared','参读注本','參讀注本')}: <a href="https://www.chineseclassic.com/content/{commentary_id}">{tri('Zhuangzi Jishi · '+commentary_name[0],'《庄子集释·'+commentary_name[1]+'》','《莊子集釋・'+commentary_name[2]+'》')} ↗</a></p>'''
        note = note.replace('</aside>',references+'</aside>')
    if 56 <= n <= 60:
        commentary_id, commentary_name = (486, ('Knowledge Wandered North','知北游','知北遊')) if n <= 58 else (489, ('Zeyang','则阳','則陽'))
        references = f'''<p>{tri('Commentaries compared','参读注本','參讀注本')}: <a href="https://www.chineseclassic.com/content/{commentary_id}">{tri('Zhuangzi Jishi · '+commentary_name[0],'《庄子集释·'+commentary_name[1]+'》','《莊子集釋・'+commentary_name[2]+'》')} ↗</a></p>'''
        if n == 59:
            references += f'''<p>{tri('Related passages on the ring, the butterfly, and losing oneself','参读环中、梦蝶与吾丧我的相关段落','參讀環中、夢蝶與吾喪我的相關段落')}: <a href="https://zh.wikisource.org/wiki/莊子/齊物論">{tri('Discussion on Making All Things Equal','《齐物论》','《齊物論》')} ↗</a></p>'''
        note = note.replace('</aside>',references+'</aside>')
    description = item['en_title'] + '. A reader essay in The Zhuangzi, Reopened: stories, relationships, and the space left for another person.'
    deck = (description, item['zh_title']+'。从故事与细节出发，重新看见人与人之间留给彼此的空间。', item['hant_title']+'。從故事與細節出發，重新看見人與人之間留給彼此的空間。')
    body = f'''<nav class="reading-breadcrumbs"><a href="index.html">{tri(*NAMES)}</a><span>/</span><span>{'00 / GUIDE' if n == 0 else f'{n:02d} / 67'}</span></nav>
<section class="zz-article-hero"><p class="zz-eyebrow">{tri('The Zhuangzi, Reopened','大知解庄子','大知解莊子')}</p>{tri(*map(esc,title(item)),tag='h1')}<p class="zz-byline">{tri('Han Qin · Dazhi','秦汉（字大知）','秦漢（字大知）')} · 2026</p><div class="zz-search-only">{tri(*map(esc,deck),tag='p',classes='zhuangzi-search-deck')}</div></section>
{''.join(bodies)}{note}<nav class="zz-article-nav" aria-label="Series navigation">{previous}<a href="index.html">{tri('All essays','系列目录','系列目錄')}</a>{following}</nav>'''
    return page(body, item['en_title']+' · '+item['zh_title'], description, filename(n), item.get('publication_date', manifest['publication_date']), 'Article')

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
