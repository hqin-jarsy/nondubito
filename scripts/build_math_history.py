#!/usr/bin/env python3
"""Build the reviewed mathematics-history collection, without translation APIs.

Import is explicit. Rebuilds depend only on checked-in originals, exact Chinese
edits and independent English prose. Incomplete entries never become links.
"""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import html
import json
import re
from pathlib import Path
import markdown
from build_ai_work_series import shell_header, footer, tri, TraditionalConverter as BaseConverter, UTF8

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/math-history'
TARGET = ROOT / 'essays/math-history'
BASE = 'https://nondubito.net/essays/math-history/'
DATE = '2026-10-01'
GROUPS = [
    ('records', 'Numbers, proof and transmission', '数字、证明与传递', range(1, 7)),
    ('outsiders', 'The objects that did not belong', '不被承认的对象', range(7, 13)),
    ('foundations', 'Infinity and foundations', '无穷与基础', range(13, 19)),
    ('makers', 'The people who make mathematics', '谁来做数学', range(19, 23)),
    ('purposes', 'What is it for?', '为了谁', range(23, 26)),
]
TITLES = [
    ('计数、丈量与账目', 'Counting, Measuring, and Keeping Accounts'),
    ('不可通约', 'Incommensurable'), ('公理之构', 'The Architecture of Axioms'),
    ('逼近而不触及', 'Approaching Without Touching'), ('另一种判据', 'Another Way to Establish a Result'),
    ('传递与命名', 'Transmission and Naming'), ('荒谬的数', 'Absurd Numbers'),
    ('想象出来的量', 'Imaginary Quantities'), ('无穷小与不严格', 'Infinitesimals and Rigor'),
    ('追猎的终结', 'The End of the Hunt'), ('第五公设爆开', 'The Fifth Postulate Breaks Open'),
    ('把无穷小赶走', 'Banishing the Infinitesimal'), ('数不完的东西', 'What Cannot Be Counted'),
    ('哥廷根', 'Göttingen'), ('集合论危机', 'The Crisis in Set Theory'),
    ('排中律之争', 'The Dispute over Excluded Middle'), ('让算术谈论算术自身', 'Arithmetic Speaks about Itself'),
    ('闭合可以买到', 'The Price of Closure'), ('清空', 'The Emptying'), ('机器', 'The Machine'),
    ('作者消失', 'The Author Disappears'), ('一个人握不住的证明', 'A Proof Too Large for One Pair of Hands'),
    ('数学与钱', 'Mathematics and Money'), ('拒绝', 'Refusal'), ('人类精神的荣誉', 'For the Honor of the Human Spirit'),
]
KEYWORDS = [
    'Sumer Uruk Babylon Egypt cuneiform Rhind 苏美尔 乌鲁克 巴比伦 埃及 泥板 莱因德',
    'Pythagoras Hippasus Eudoxus 毕达哥拉斯 希帕索斯 欧多克索斯',
    'Euclid Hilbert Pasch geometry 欧几里得 希尔伯特 公理 几何',
    'Archimedes palimpsest exhaustion 阿基米德 重写本 穷竭法',
    'Liu Hui Zu Chongzhi Nine Chapters 刘徽 祖冲之 九章算术 算数书',
    'al-Khwarizmi algebra algorithm 花拉子米 智慧宫 代数 算法',
    'Brahmagupta Bhaskara De Morgan negative numbers 婆罗摩笈多 婆什迦罗 德摩根 负数',
    'Cardano Tartaglia Bombelli complex numbers 卡尔达诺 塔尔塔利亚 邦贝利 复数 虚数',
    'Newton Leibniz Berkeley calculus 牛顿 莱布尼茨 贝克莱 微积分',
    'Galois Abel Ruffini quintic 伽罗瓦 阿贝尔 鲁菲尼 五次方程',
    'Saccheri Gauss Bolyai Lobachevsky Beltrami Riemann 萨凯里 高斯 波约伊 罗巴切夫斯基 贝尔特拉米 黎曼 非欧几何',
    'Cauchy Weierstrass Bolzano Dedekind 柯西 魏尔斯特拉斯 波尔查诺 戴德金 极限 连续',
    'Cantor Dedekind Kronecker infinity 康托尔 戴德金 克罗内克 无穷 超越数',
    'Klein Hilbert Noether Gottingen Göttingen 克莱因 希尔伯特 诺特 哥廷根',
    'Russell Frege Zermelo set theory 罗素 弗雷格 策梅洛 集合论 选择公理',
    'Brouwer Hilbert Weyl intuitionism excluded middle 布劳威尔 希尔伯特 外尔 直觉主义 排中律',
    'Gödel Godel Rosser incompleteness 哥德尔 罗瑟 不完备性 算术',
    'Presburger Tarski Wang Hao Wu Wen-tsun decidability 普雷斯伯格 塔尔斯基 王浩 吴文俊 可判定',
    'Noether Landau Courant exile 诺特 朗道 库朗 流亡 哥廷根',
    'Turing Church computability halting 图灵 丘奇 可计算 停机问题',
    'Bourbaki Weil Cartan 布尔巴基 韦尔 嘉当',
    'Appel Haken Hales four colour color simple groups Kepler 阿佩尔 哈肯 黑尔斯 四色 有限单群 开普勒',
    'Black Scholes Merton RSA Diffie Hellman finance cryptography 布莱克 斯科尔斯 默顿 密码学 金融',
    'Perelman Hamilton Poincare Poincaré Grothendieck 佩雷尔曼 汉密尔顿 庞加莱 格罗滕迪克',
    'Jacobi Fourier AI mathematics formal proof 雅可比 傅里叶 人工智能 数学 形式证明',
]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def esc(value):
    return html.escape(str(value), quote=True)


def normalize_zh(text):
    # Preserve decimal/grouping commas and formula punctuation inside code spans.
    def prose(part):
        part = re.sub(r',\s*(?!\d)', '，', part)
        part = re.sub(r'(?<=[\u3400-\u9fff]),\s*', '，', part)
        part = re.sub(r';\s*', '；', part)
        part = re.sub(r':\s*(?=[\u3400-\u9fff])', '：', part)
        return part
    parts = re.split(r'(`[^`]*`)', text)
    return ''.join(p if i % 2 else prose(p) for i, p in enumerate(parts))


class Converter(BaseConverter):
    def convert(self, value):
        # Use Hans-Hant character conversion, not the AI-work vocabulary map:
        # that map changes all 里, including mathematicians' transliterated names.
        source = self._string(value)
        mutable = self.cf.CFStringCreateMutable(None, 0)
        try:
            self.cf.CFStringAppend(mutable, source)
            assert self.cf.CFStringTransform(mutable, None, self.transform, 0)
            size = self.cf.CFStringGetMaximumSizeForEncoding(self.cf.CFStringGetLength(mutable), UTF8) + 1
            buffer = ctypes.create_string_buffer(size)
            assert self.cf.CFStringGetCString(mutable, buffer, size, UTF8)
            result = buffer.value.decode()
            for old, new in {'周期':'週期', '這里':'這裡', '那里':'那裡', '哪里':'哪裡',
                             '家里':'家裡', '手里':'手裡', '心里':'心裡', '眼里':'眼裡',
                             '屋里':'屋裡', '城里':'城裡', '書里':'書裡', '房子里':'房子裡',
                             '余項':'餘項', '剩余':'剩餘', '其余':'其餘', '余數':'餘數',
                             '軟件':'軟體', '硬件':'硬體', '“':'「', '”':'」'}.items():
                result = result.replace(old, new)
            # Locatives are words, not a global 里 replacement: Euclid, Fourier,
            # Curie, Cayley and place names must retain their established forms.
            locatives = ('系列 數學 數論 算術 定理 公式 方程 幾何 分析 理論 學科 學校 大學 '
                         '法文 漢語 語言 論文 正文 原文 文章 版本 信 筆記 檔案 記錄 傳記 '
                         '材料 文獻 史料 證明 研究 定義 課程 故事 書 書名 標題 題目 引文 '
                         '文本 敘述 世界 領域 範圍 區間 體系 系統 結構 制度 規則 機構 組織 '
                         '問題 條件 歷史 數學史 生活 文化 會場 教室 工作室 辦公室 房間 屋 城 '
                         '水 井 泥板 腦子 手 心 眼 家 抽屜 櫃子 句子 話 盒子 箱子 圈子 格子 '
                         '數字 記憶 賬目 賬簿 賬 數目 目錄 書架 報告 代碼 機器 程序 形式 '
                         '過程 詞 時間 年 月 天 日子 小時 分鐘 世紀 篇 章 節 卷 序 序言 '
                         '前言 集 群 圖 名單 表 網 樓 列 圖書館').split()
            result = re.sub('('+'|'.join(sorted(locatives,key=len,reverse=True))+')里', r'\1裡', result)
            result = result.replace('里面','裡面').replace('往里','往裡').replace('向里','向裡')
            for verb in ('發明','寫明','說明','證明'):
                result = result.replace(verb+'瞭',verb+'了')
            return result
        finally:
            self.cf.CFRelease(source)
            self.cf.CFRelease(mutable)


def import_sources(folder):
    for path in sorted(DATA.glob('[0-9][0-9].json')):
        item = json.loads(path.read_text())
        matches = list(folder.glob(f'数学史系列_{item["id"]:02d}_*.md'))
        assert len(matches) == 1, path
        raw = matches[0].read_bytes()
        target = DATA / f'{item["id"]:02d}-source.json'
        record = dict(filename=matches[0].name, sha256=digest(raw), original=raw.decode('utf-8-sig'))
        if target.exists():
            assert json.loads(target.read_text()) == record, f'External source changed: {target}'
        else:
            target.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')


def load_items():
    out = []
    for path in sorted(DATA.glob('[0-9][0-9].json')):
        item = json.loads(path.read_text())
        assert item['id'] == int(path.stem) and 1 <= item['id'] <= 25
        source_path = DATA/f'{path.stem}-source.json'
        if not source_path.exists():
            continue  # A new authoring file is not a publication decision.
        source = json.loads(source_path.read_text())
        original = source['original']
        # UTF-8 originals currently have no BOM; hash the exact imported bytes.
        assert digest(original.encode()) == source['sha256'], path
        zh = original
        for edit in item['edits']:
            assert zh.count(edit['before']) == 1, (path, edit['before'])
            zh = zh.replace(edit['before'], edit['after'], 1)
        item['body_zh'] = normalize_zh(zh)
        for lang in ('zh','en'):
            assert len(re.findall(r'^## ', item[f'body_{lang}'], re.M)) == 8, (path,lang)
            assert item[f'title_{lang}'] and item[f'deck_{lang}']
        item['title_zh'] = normalize_zh(item['title_zh'])
        item['deck_zh'] = normalize_zh(item['deck_zh'])
        assert len(item['section_coverage']) == 8 and item['sources'] and item['review_notes']
        assert len(re.findall(r'\S+', item['body_en'])) >= len(original)*.35, f'English appears abridged: {path}'
        for s in item['sources']:
            assert re.match(r'https?://[^/]+/', s['url']) and s['label_en'] and s['label_zh'] and s['supports']
        item['source'] = source
        out.append(item)
    assert out and len({x['id'] for x in out}) == len(out)
    return out


def localized(en, zh, converter, tag='span', css=''):
    return tri(esc(en), esc(zh), esc(converter.convert(zh)), tag, css)


def body_html(text, language):
    text = text.split('\n',1)[1].strip() if text.startswith('# ') else text
    # Only headings and prose are expected; Markdown handles inline emphasis,
    # formulas in code, lists and links where the author's text uses them.
    rendered = markdown.markdown(text)
    counter = iter(range(1,9))
    return re.sub('<h2>',lambda _:f'<h2 id="{language}-section-{next(counter)}">',rendered)


def head(title, description, filename, item=None):
    url = BASE + ('' if filename == 'index.html' else filename)
    schema = {'@context':'https://schema.org','@type':'Article' if item else 'CollectionPage',
              'name':title,'description':description,'url':url,'inLanguage':['en','zh-Hans','zh-Hant'],
              'author':{'@type':'Person','name':'Han Qin (秦汉)'},'datePublished':DATE,'dateModified':DATE}
    if item:
        schema.update(headline=item['title_en'],mainEntityOfPage=url,
                      isPartOf={'@type':'CollectionPage','name':'The Chisel–Construct Cycle: Mathematics','url':BASE},
                      citation=[s['url'] for s in item['sources']])
    schema_json = json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
    return f'''<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(description)}"><meta name="author" content="Han Qin (秦汉)">
<meta property="og:type" content="{'article' if item else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary">
<link rel="canonical" href="{url}"><link rel="icon" type="image/svg+xml" href="../../favicon.svg">
<link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="../../site-shell.css?v=20260905b"><link rel="stylesheet" href="math-history.css?v=20261001">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;family=Noto+Serif+TC:wght@400;500;600&amp;display=swap" rel="stylesheet">
<script src="../../site-shell.js?v=20260905b"></script><script defer src="math-history.js?v=20261001"></script>
<script type="application/ld+json">{schema_json}</script>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script></head>'''


def shell(content, page_head):
    header = shell_header().replace('data-site-shell-menu aria-controls','data-site-shell-menu aria-label="Menu" aria-controls')
    return '<!DOCTYPE html>\n<html lang="en" data-lang="en" data-editions="en zh zh-hant">'+page_head+'<body class="site-shell-page explicit-hant math-history-page">'+header+content+footer()+'</body></html>\n'


def breadcrumbs(c, article=False):
    return '<nav class="math-breadcrumbs" aria-label="Breadcrumb"><a href="../../library.html#cycles">'+localized('The Chisel–Construct Cycle','凿构周期律',c)+'</a>'+('<span>/</span><a href="index.html">'+localized('Mathematics','数学',c)+'</a>' if article else '')+'</nav>'


def render_index(items,c):
    ready={i['id']:i for i in items};n=len(ready)
    en_deck='From clay accounts to infinity, computers, and the people who make proofs: a history of what mathematics can settle, and what it leaves to us.'
    zh_deck='从一块记账的泥板，走到无穷、计算机与证明背后的人。数学解决了什么，又把什么留给了我们？'
    groups=[];nav=[]
    for slug,en,zh,ids in GROUPS:
        nav.append(f'<a href="#{slug}">{localized(en,zh,c)}</a>')
        cards=[]
        for i in ids:
            item=ready.get(i);title_zh,title_en=TITLES[i-1]
            if item:
                cards.append(f'<a class="math-card" href="ep{i:02d}.html"><span class="math-number">{i:02d}</span><div>{localized(item["title_en"],item["title_zh"],c,"h3")}{localized(item["deck_en"],item["deck_zh"],c,"p")}{localized("Read essay →","阅读全文 →",c,"span","math-read")}</div></a>')
            else:
                cards.append(f'<div class="math-card pending"><span class="math-number">{i:02d}</span><div>{localized(title_en,title_zh,c,"h3")}{localized("In editorial preparation","正在编辑，尚未发布",c,"p")}</div></div>')
        groups.append(f'<section id="{slug}" class="math-group">{localized(en,zh,c,"h2")}<div class="math-grid">'+''.join(cards)+'</div></section>')
    status_en='25 complete essays · English and both Chinese scripts' if n==25 else f'{n} complete essays available · A 25-part collection in preparation'
    status_zh='全25篇 · 简体中文、繁体中文与英文完整版' if n==25 else f'全系列25篇，已发布{n}篇 · 简体中文、繁体中文与英文'
    content=f'''<main id="main-content" class="math-wrap" data-search="数学史 數學史 数学 凿构周期律 Mathematics history chisel construct">
{breadcrumbs(c)}<section class="math-hero"><p class="math-kicker">NON DUBITO · {localized('THE CHISEL–CONSTRUCT CYCLE','凿构周期律',c)}</p>
{localized('A Human History of Mathematics','数学史：在确定性之外',c,'h1')}{localized(en_deck,zh_deck,c,'p','math-deck math-search-deck')}
{localized(status_en,status_zh,c,'p','math-meta')}
<div class="math-promise">{localized('No advanced mathematics required. Start at the beginning, or choose a question below. The mathematics matters; so do the classrooms, institutions, and lives that made it possible.','不需要高等数学基础。可以从第一篇顺读，也可以从下面一个问题进入。这里写数学，也写课堂、制度，以及让数学成为可能的那些人。',c,'p')}</div></section>
<nav class="math-topics" aria-label="Reading routes">{''.join(nav)}</nav>{''.join(groups)}
<aside class="math-afterword">{localized('These are historical essays, not a textbook or a claim that every open mathematical question has the same cause. Legends, surviving records and the author’s interpretations are kept distinct.','这是一组历史散文，不是教科书，也不是说所有数学难题都有同一个原因。传说、幸存史料与作者的理解，需要分开来读。',c,'p')}</aside></main>'''
    return shell(content,head('A Human History of Mathematics · 凿构周期律：数学',en_deck,'index.html'))


def render_article(item,items,c):
    bodies=[];toc=[]
    for lang,css,text in [('en','en',item['body_en']),('zh','zh',item['body_zh']),('hant','hant',c.convert(item['body_zh']))]:
        headings=re.findall(r'^## (.*)$',text,re.M)
        toc.append(f'<ol class="lang-{css}">'+''.join(f'<li><a href="#{lang}-section-{i}">{esc(h)}</a></li>' for i,h in enumerate(headings,1))+'</ol>')
        code={'en':'en','zh':'zh-Hans','hant':'zh-Hant'}[lang]
        bodies.append(f'<div class="math-prose lang-{css}" lang="{code}">'+body_html(text,lang)+'</div>')
    ids=[x['id'] for x in items];index=ids.index(item['id']);links=[]
    for pos,label_en,label_zh,arrow in [(index-1,'Previous essay','上一篇','←'),(index+1,'Next essay','下一篇','→')]:
        if 0<=pos<len(items):
            x=items[pos];links.append(f'<a href="ep{x["id"]:02d}.html">{localized(label_en,label_zh,c,"small")}{arrow} {localized(x["title_en"],x["title_zh"],c)}</a>')
        else:links.append(f'<a href="index.html">{localized("Series contents","回到系列目录",c)}</a>')
    sources=''.join(f'<li><a href="{esc(s["url"])}">{localized(s["label_en"],s["label_zh"],c)}</a></li>' for s in item['sources'])
    keywords=KEYWORDS[item['id']-1]
    content=f'''<main id="main-content" class="math-wrap" data-search="{esc(keywords+' '+c.convert(keywords))}"><article class="math-article">{breadcrumbs(c,True)}
<section class="math-head"><p class="math-kicker">{localized('A HUMAN HISTORY OF MATHEMATICS','凿构周期律 · 数学',c)} · {item['id']:02d} / 25</p>
{localized(item['title_en'],item['title_zh'],c,'h1')}{localized(item['deck_en'],item['deck_zh'],c,'p','math-deck math-search-deck')}
<p class="math-meta">{localized('Han Qin · Independent English edition','秦汉 · 简繁中文与独立英文版',c)}</p></section>
<details class="math-toc"><summary>{localized('In this essay','篇内目录',c)}</summary>{''.join(toc)}</details>
{''.join(bodies)}<details class="math-sources"><summary>{localized('Sources and further reading','史料与延伸阅读',c)}</summary>
{localized('Selected references for historical details and interpretive disputes. Museum records, ancient literary accounts and modern reconstructions do not carry the same kind of evidence.','以下资料对应文中的历史细节与解释分歧。馆藏记录、古代文学与现代重建，不是同一种证据。',c,'p')}<ul>{sources}</ul></details>
<nav class="math-series-nav" aria-label="Series navigation">{''.join(links)}</nav></article></main>'''
    return shell(content,head(item['title_en'],item['deck_en'],f'ep{item["id"]:02d}.html',item))


def outputs():
    items=load_items();c=Converter()
    try:
        pages={TARGET/'index.html':render_index(items,c)}
        pages.update({TARGET/f'ep{i["id"]:02d}.html':render_article(i,items,c) for i in items})
        return pages
    finally:c.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-zh',type=Path)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--complete',action='store_true',help='require all 25 reviewed essays for release')
    args=parser.parse_args()
    if args.import_zh and args.check:parser.error('--check cannot import')
    if args.import_zh:import_sources(args.import_zh)
    if args.complete:
        assert [i['id'] for i in load_items()] == list(range(1,26)), 'Release requires every essay, 01–25'
    expected=outputs()
    stale={p:s for p,s in expected.items() if not p.exists() or p.read_text()!=s}
    if args.check:
        assert not stale, list(stale)
    else:
        TARGET.mkdir(parents=True,exist_ok=True)
        for p,s in stale.items():p.write_text(s)
    print(f'{"Checked" if args.check else "Built"} {len(expected)-1} complete three-language essays and collection index')


if __name__=='__main__':main()
