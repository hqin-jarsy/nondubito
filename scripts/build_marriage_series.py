#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Eight warm reader essays on marriage; full Chinese editions and independent English."""
from __future__ import annotations

import argparse
import html
import json
import re

from build_language_writing import ROOT, WritingTraditionalConverter, loc, page, prose

DATE = '2026-10-30'
DATA = ROOT / 'data/marriage'
TARGET = ROOT / 'essays/marriage'
BASE = 'https://nondubito.net/essays/marriage/'
TITLE = ('Still Two People', '结婚以后，仍然是两个人')
SUBTITLE = ('A Philosophy of Marriage', 'SAE 婚姻论')
DECK = (
    'A wedding, a shared home, an old arrangement made movable again. Seven essays and a short guide on staying close without losing either person. Parenthood is not a requirement; leaving is not a verdict on the years.',
    '从领证那一天，到共同生活、支持、岁月与去留。七篇散文与一篇短导读，读两个人怎样亲近，又不把其中一个人弄丢。有孩子不是必经一站，分开也不替那些年下总评。',
)
KINDS = (
    ('A short guide', '短导读'), ('The wedding day', '眷属'),
    ('A place for each person', '各自'), ('Making room for growth', '成就'),
    ('Living through the years', '岁月'), ('Preparing for a newcomer', '孕育'),
    ('After a child arrives', '三个人'), ('Different endings', '去留'),
)
SEARCHES = (
    'guide introduction 导读 導讀',
    'wedding promises recognition exclusivity 领证 領證 誓言 承诺 承諾 背书 背書 排他',
    'privacy solitude trust we self 隐私 隱私 独处 獨處 信任 我们 我們 不疑',
    'support growth contributions 成就 支持 成长 成長 付出',
    'years change chores labor arrangements 岁月 歲月 分工 家务 家務 期待 冲突 衝突',
    'preparation newcomer adoption childlessness 孕育 领养 領養 生育 无子女 無子女',
    'parenting care coparenting 共同养育 共同養育 育儿 育兒 为了孩子 為了孩子',
    'separation divorce bereavement grief 离婚 離婚 退出 丧偶 喪偶 告别 告別 悲伤 悲傷',
)


class MarriageTraditionalConverter(WritingTraditionalConverter):
    def convert(self, text):
        result = super().convert(text)
        for old,new in (('咨詢','諮詢'),('開啓','開啟'),('碗面','碗麵'),
                        ('面館','麵館'),('賬','帳'),('復查','複查'),
                        ('乾這個','幹這個'),('鑒定','鑑定')):
            result = result.replace(old,new)
        return result


def load_items():
    items = []
    for i in range(8):
        slug = 'overview' if not i else f'ep{i:02d}'
        d = json.loads((DATA/(slug+'.json')).read_text())
        assert d['id'] == i and d['slug'] == slug
        assert d['source_url'] == f'https://self-as-an-end.net/papers/sae-marriage-theory-{i}.html'
        for lang in ('zh','en'):
            assert d['title_'+lang].strip() and d['deck_'+lang].strip()
            body = d['body_'+lang]
            assert len(body) >= (15 if not i else 24)
            assert all(isinstance(p,str) and p.strip() and '<' not in p and not p.startswith('###') for p in body)
            assert sum(p.startswith('## ') for p in body) == (2 if not i else 3)
            text = '\n'.join(body)
            size = len(re.findall(r'[\u3400-\u9fff]',text)) if lang == 'zh' else len(text.split())
            assert size >= ((1000 if not i else 2000) if lang == 'zh' else (600 if not i else 1100)), (slug,lang,size)
            assert not re.search(r'\b\d{2}DD\b|\bMA\d+\b|操作层|对象层|归属端点|构成归属',text)
        items.append(d)
    return items


def crumb(conv, article=False):
    tail = '<span aria-hidden="true">/</span><a href="index.html">'+loc(*TITLE,conv)+'</a>' if article else ''
    return '<nav class="lw-crumb" aria-label="Breadcrumb"><a href="../sae/index.html#living">'+loc('Value, living & relating','价值与关系',conv)+'</a>'+tail+'</nav>'


def related(conv):
    return '<aside class="lw-related">'+loc('Keep reading, at your own pace','还可以慢慢读',conv,'h2')+''.join(
        '<a href="../'+path+'/index.html">'+loc(en,zh,conv)+'</a>' for path,en,zh in (
            ('love','Love · Why This Person?','爱情论：为什么偏偏是你'),
            ('relation','Relations · What Passes Between Us','关系论：在关系里，仍是自己'),
            ('everyday/relationships','Everyday life · Relationships','日常散文：关系里的结构'),
            ('everyday/parenting','Everyday life · Parenting','日常散文：亲子里的结构'),
        ))+'</aside>'


def reading_note(conv, item=None):
    note = loc(
        'Reader essays drawn from the eight SAE Marriage Theory papers, preserving their central distinctions and everyday examples rather than reproducing every technical proposition or philosophical comparison. English is independently written. The couples and added domestic details are fictional illustrations, not reported cases or advice about a particular marriage. The papers examine one kind of two-adult marriage; this does not deny other forms or rank people outside their scope. Examples often use a woman and a man, but gender combination is not an entrance condition. Formal recognition and dissolution depend on particular rules. These essays are not a current-law guide, a test of inward love, or a substitute for safety and protection.',
        '据婚姻论八篇论文写成，保留主要区分与日常例子，不逐条重述全部技术命题及哲学对读。英文独立重写。夫妻人物及扩写的生活细节均为虚构示例，不是真实案例，也不替一段具体婚姻作处方。论文限定讨论两个成年人之间的一种婚姻，不否认其他形式，也不给范围之外的人分高下。例子多用男女夫妻，性别组合不是讨论门槛。制度承认与解除依具体规则；本文不是现行法律指南，不测验内心的爱，也不代替必要的安全与保护。',conv,'p')
    url = item['source_url'] if item else 'https://self-as-an-end.net/papers/sae-marriage-theory-0.html'
    return '<details class="lw-sources"><summary>'+loc('Source & reading note','来源与阅读说明',conv)+'</summary>'+note+'<a href="'+url+'">'+loc('Read the source paper ↗','阅读对应原论文 ↗' if item else '阅读原论文总导读 ↗',conv)+'</a></details>'


def document(content, title, deck, filename, conv, items, item=None):
    result = page(content,title,deck,'essays/marriage/'+filename,conv,
                  item['source_url'] if item else None,(BASE,TITLE[0]),publication_date=DATE)
    if not item:
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>',result,re.S)
        schema = json.loads(match[1])
        schema.update(datePublished=DATE,dateModified=DATE,hasPart=[{'@type':'Article','name':d['title_en'],'url':BASE+d['slug']+'.html'} for d in items])
        result = result[:match.start(1)]+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+result[match.end(1):]
    return result


def landing(items,conv):
    def cards(selected):
        return '<div class="lw-grid">'+''.join('<a class="lw-card" href="'+d['slug']+'.html"><p class="lw-kicker">'+f'{d["id"]:02d} · '+loc(*KINDS[d['id']],conv)+'</p>'+loc(d['title_en'],d['title_zh'],conv,'h2')+loc(d['deck_en'],d['deck_zh'],conv,'p')+loc('Read essay →','阅读全文 →',conv,'span','lw-read')+'</a>' for d in selected)+'</div>'
    content = '<main class="lw-wrap" data-search="婚姻论 婚姻論 Marriage spouse marriage parenting promises separation bereavement 结婚 結婚 离婚 離婚 丧偶 喪偶"><div>'+crumb(conv)+'</div><section class="lw-hero"><p class="lw-kicker">Non Dubito · '+loc(*SUBTITLE,conv)+'</p>'+loc(*TITLE,conv,'h1')+loc(*DECK,conv,'p','lw-deck lw-search-deck')+loc('Seven essays & a short guide · English, Simplified & Traditional Chinese','七篇正文与一篇短导读 · 英文、简体中文与繁体中文',conv,'p','lw-meta')+'</section><aside class="lw-opening">'+loc('Two keys can open the same door. They need not become one key.','两把钥匙可以开同一扇门，不必熔成一把。',conv,'p')+'<a href="overview.html">'+loc('Begin with the short guide →','从短导读开始 →',conv)+'</a>'+loc('Read wherever a question meets your life. These are not stages every marriage must complete.','从与你有关的那一篇读起。这不是每段婚姻必须走完的路线。',conv,'p','lw-meta')+'</aside>'+cards(items[:1])+'<section class="lw-note">'+loc('Two people, over time','两个人，和日子',conv,'h2')+'</section>'+cards(items[1:5])+'<section class="lw-note">'+loc('A newcomer, and different endings','迎来一个人，也面对不同的结束',conv,'h2')+loc('Parenthood is not an obligation; separation is not a final grade. These questions have their own entrances.','有孩子不是义务，分开不是总评。这几个问题，各有自己的入口。',conv,'p')+'</section>'+cards(items[5:])+reading_note(conv)+related(conv)+'</main>'
    return document(content,TITLE[0]+': A Philosophy of Marriage · 婚姻论',DECK[0],'index.html',conv,items)


def article(item,items,conv):
    bodies = ''.join('<div class="essay-body lw-prose lang-'+lang+'" lang="'+native+'">'+prose([conv.convert(p) for p in item['body_zh']] if lang=='hant' else item['body_'+lang])+'</div>' for lang,native in (('en','en'),('zh','zh-Hans'),('hant','zh-Hant')))
    links = ''
    for n,en,zh in ((item['id']-1,'Previous essay','上一篇'),(item['id']+1,'Next essay','下一篇')):
        other = items[n] if 0 <= n < len(items) else None
        links += '<a href="'+(other['slug']+'.html' if other else 'index.html')+'">'+loc(en if other else 'All eight essays',zh if other else '全部八篇',conv,'small')+loc(other['title_en'] if other else TITLE[0],other['title_zh'] if other else TITLE[1],conv)+'</a>'
    labels = html.escape('婚姻论 婚姻論 marriage '+SEARCHES[item['id']]+' '+item['title_zh']+' '+conv.convert(item['title_zh']),quote=True)
    content = '<main class="lw-wrap">'+crumb(conv,True)+'<article class="lw-article" data-search="'+labels+'"><div class="lw-head"><p class="lw-kicker">'+loc(*SUBTITLE,conv)+' · '+f'{item["id"]:02d} · '+loc(*KINDS[item['id']],conv)+'</p>'+loc(item['title_en'],item['title_zh'],conv,'h1')+loc(item['deck_en'],item['deck_zh'],conv,'p','lw-deck lw-search-deck')+'<p class="lw-meta">Han Qin · <time datetime="'+DATE+'">'+DATE+'</time> · '+loc('English independently written','英文独立重写',conv)+'</p></div>'+bodies+reading_note(conv,item)+'<nav class="lw-series-nav" aria-label="Series navigation">'+links+'</nav>'+related(conv)+'</article></main>'
    return document(content,item['title_en'],item['deck_en'],item['slug']+'.html',conv,items,item)


def library_card(conv):
    def ll(en,zh,tag='span',css=''):
        return loc(en,zh,conv,tag,css).replace('lang-zh','lang-zh cl-zh').replace('lang-hant','lang-zh cl-hant')
    return '<a href="essays/marriage/index.html" class="series-card"><span class="series-card-count">'+ll('8 essays · English & both Chinese scripts','8 篇 · 英文与简繁中文')+'</span><div class="series-card-title-zh cl-zh">婚姻论：结婚以后，仍然是两个人</div><div class="series-card-title-zh cl-hant">婚姻論：結婚以後，仍然是兩個人</div><div class="series-card-title-en">Marriage: Still Two People</div>'+ll(DECK[0],DECK[1],'p','series-card-desc')+ll('Read series →','阅读系列 →','span','series-card-arrow')+'</a>'


def render():
    items=load_items()
    conv=MarriageTraditionalConverter()
    try:
        return {TARGET/'index.html':landing(items,conv),**{TARGET/(d['slug']+'.html'):article(d,items,conv) for d in items}}
    finally:
        conv.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    for path,text in render().items():
        if args.check:
            assert path.read_text()==text,f'Stale marriage page: {path}'
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text)
    print(('Checked' if args.check else 'Wrote')+' marriage · nine pages · three complete reading modes')


if __name__=='__main__':
    main()
