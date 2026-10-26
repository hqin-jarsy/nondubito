#!/usr/bin/env python3
"""Build a three-essay companion to Rights Theory from On Accountability."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from build_language_writing import ROOT,DATE,WritingTraditionalConverter,page,loc,prose

TARGET = ROOT/'essays/accountability'
DATA = ROOT/'data/accountability'
SOURCE = 'https://self-as-an-end.net/papers/sae-rights-accountability.html'
BASE = 'https://nondubito.net/essays/accountability/'
TITLE = ('What Is Yours to Answer For?', '职责与承担')
DECK = ('An instruction, an appointment, a handover, an ending. Three essays ask how a demand becomes yours, why that does not make it right, and what changes when a position ends.', '一句要求、一次任职、一项交接，以及一次离开。三篇散文，问事情怎样落到自己身上，为什么成立不等于正当，又怎样让一份承担真正走到尽头。')


class AccountabilityTraditionalConverter(WritingTraditionalConverter):
    def convert(self,text):
        result=super().convert(text)
        for old,new in (('復盤','回顧'),('實收斂','實際收斂'),('賬','帳'),('沈重','沉重'),('覈實','核實')):
            result=result.replace(old,new)
        return result


def load_items():
    items=[]
    for i in range(1,4):
        item=json.loads((DATA/f'ep{i:02d}.json').read_text())
        assert item['id']==i and item['slug']==f'ep{i:02d}'
        for lang in ('en','zh'):
            assert item['title_'+lang] and item['deck_'+lang]
            body=item['body_'+lang]
            assert len(body)>=18 and sum(p.startswith('## ') for p in body)==3
            assert all(p.strip() and '<' not in p and not p.startswith('###') for p in body)
            text='\n'.join(body)
            count=len(re.findall(r'[\u3400-\u9fff]',text)) if lang=='zh' else len(text.split())
            assert count>=(1800 if lang=='zh' else 1000),(i,lang,count)
            assert not re.search(r'\b\d{2}DD\b|\b[FT]\d+\b',text)
        items.append(item)
    return items


def breadcrumb(conv,article=False):
    extra=f'<span aria-hidden="true">/</span><a href="index.html">{loc(*TITLE,conv)}</a>' if article else ''
    return f'<nav class="lw-crumb" aria-label="Breadcrumb"><a href="../sae/index.html#shared-life">{loc("SAE & Philosophy","SAE 与哲学",conv)}</a><span aria-hidden="true">/</span><a href="../rights/index.html">{loc("Rights Theory","权利论",conv)}</a>{extra}</nav>'


def related(conv):
    links=''.join(f'<a href="../{slug}/index.html">{loc(en,zh,conv)}</a>' for slug,en,zh in (('rights','The original seven Rights essays','权利论原有七篇'),('institution','Institutions','制度论'),('state','The State','国家论'),('sae','SAE reading map','SAE 散文阅读地图')))
    return '<aside class="lw-related">'+loc('Keep exploring','继续读',conv,'h2')+links+'</aside>'


def reading_note(conv):
    return '<details class="lw-sources"><summary>'+loc('Source & scope','原论文与阅读范围',conv)+'</summary>'+loc('Three reader essays drawn from On Accountability · Wei, not twenty-six propositions translated one by one. The workplace and child examples are imagined. The source uses accountability, liability and duty in explicitly limited senses; these do not redefine every ordinary or legal use of those words. Classification does not confer legitimacy or make coercion disappear. These essays do not decide actual employment terms, continuing confidentiality arrangements, remedies, or the legal responsibilities of minors. English is independently written.','本组三篇据《论职责 · 位》改写，不是把二十六条命题逐条翻译。任职与孩子的场景均为虚构示例。原论文对职责、责任和义务作了特定区分，不用它们替代日常语言与法律中的全部用法。分类不提供正当性，也不使现实强制自行停止；本文不裁断现实劳动安排、持续保密约定、救济办法或未成年人的法定责任。英文独立重写。',conv,'p')+f'<p><a href="{SOURCE}">'+loc('On Accountability · source paper ↗','《论职责 · 位》· 原论文 ↗',conv)+'</a> · <a href="https://doi.org/10.5281/zenodo.22853810">DOI: 10.5281/zenodo.22853810</a></p></details>'


def landing(items,conv):
    cards=''.join(f'<a class="lw-card" href="{item["slug"]}.html"><p class="lw-kicker">0{item["id"]}</p>{loc(item["title_en"],item["title_zh"],conv,"h2")}{loc(item["deck_en"],item["deck_zh"],conv,"p")}{loc("Read essay →","阅读全文 →",conv,"span","lw-read")}</a>' for item in items)
    content=f'<main class="lw-wrap">{breadcrumb(conv)}<section class="lw-hero"><p class="lw-kicker">Non Dubito · '+loc('A Rights Theory companion','权利论 · 专论散文',conv)+f'</p>{loc(*TITLE,conv,"h1")}{loc(*DECK,conv,"p","lw-deck lw-search-deck")}'+loc('Three essays · English, Simplified & Traditional Chinese','三篇 · 英文、简体中文与繁体中文',conv,'p','lw-meta')+'</section><aside class="lw-opening">'+loc('You need not read all of Rights Theory first. Begin with an ordinary instruction that someone calls your responsibility.','不必先读完权利论。从一句“这是你的职责”开始就好。',conv,'p')+'<a href="ep01.html">'+loc('Start with the demand →','先问要求从哪里来 →',conv)+'</a></aside><section class="lw-grid">'+cards+'</section><section class="lw-note">'+loc('A new question beside the original route','在原有主线旁，再补一个问题',conv,'h2')+loc('The original seven essays retain their own route and language editions. This companion develops the later paper’s finer distinction between an external demand attached to a position, one’s own undertaking, the exposure of a position to change, and actual performance. Here, an operative demand is not automatically a moral command. Nor does the end of a role settle every question about its history.','原有七篇及其语言版本保留。本组三篇展开后出的专论，对外部落在位置上的要求、自己愿意承担的方向、位置可以被改变，以及实际兑现，作进一步区分。这里不把一项正在运行的要求直接等同于道德命令，也不以岗位的结束，替全部历史问题结账。',conv,'p')+'</section>'+reading_note(conv)+related(conv)+'</main>'
    return page(content,TITLE[0]+' · 职责与承担',DECK[0],'essays/accountability/index.html',conv)


def article(item,items,conv):
    bodies=''.join(f'<div class="essay-body lw-prose lang-{lang}" lang="{native}">{prose([conv.convert(p) for p in item["body_zh"]] if lang=="hant" else item["body_"+lang])}</div>' for lang,native in (('en','en'),('zh','zh-Hans'),('hant','zh-Hant')))
    neighbors=[]
    for offset,en,zh in ((-1,'Previous essay','上一篇'),(1,'Next essay','下一篇')):
        n=item['id']-1+offset
        if 0<=n<len(items):
            other=items[n]
            neighbors.append(f'<a href="{other["slug"]}.html">{loc(en,zh,conv,"small")}{loc(other["title_en"],other["title_zh"],conv)}</a>')
        else:neighbors.append('<a href="index.html">'+loc('All three essays','全部三篇',conv,'small')+loc(*TITLE,conv)+'</a>')
    content=f'<main class="lw-wrap">{breadcrumb(conv,True)}<article class="lw-article"><div class="lw-head"><p class="lw-kicker">{loc(*TITLE,conv)} · 0{item["id"]}</p>{loc(item["title_en"],item["title_zh"],conv,"h1")}{loc(item["deck_en"],item["deck_zh"],conv,"p","lw-deck lw-search-deck")}<p class="lw-meta">Han Qin · <time datetime="{DATE}">{DATE}</time></p></div>{bodies}{reading_note(conv)}<nav class="lw-series-nav" aria-label="Series navigation">'+''.join(neighbors)+'</nav>'+related(conv)+'</article></main>'
    return page(content,item['title_en'],item['deck_en'],'essays/accountability/'+item['slug']+'.html',conv,SOURCE,(BASE,TITLE[0]))


def library_card(conv):
    def t(en,zh,tag='span',css=''):
        return loc(en,zh,conv,tag,css).replace('lang-zh','lang-zh cl-zh').replace('lang-hant','lang-zh cl-hant')
    return '<a href="essays/accountability/index.html" class="series-card"><span class="series-card-count">'+t('Rights companion · 3 essays · EN / 简 / 繁','权利论专论 · 3 篇 · 英简繁')+'</span><div class="series-card-title-zh cl-zh">职责与承担</div><div class="series-card-title-zh cl-hant">職責與承擔</div><div class="series-card-title-en">What Is Yours to Answer For?</div>'+t('How a demand becomes yours, why an operative requirement can still be wrong, and what ends when you leave.','要求怎样落到自己身上，为什么成立不等于正当，又怎样让一份承担真正结束。','p','series-card-desc')+t('Read companion','阅读专论','span','series-card-arrow')+'</a>'


def rights_entry(conv):
    # Use explicit scripts only inside this added block. The legacy page's
    # text-node dictionary must not reconvert these already localized nodes.
    en='<section class="accountability-entry lang-en"><p class="entry-num">New companion · Three essays · EN / 简 / 繁</p><h2>What Is Yours to Answer For?</h2><p>The original seven essays remain a complete route. A later special study asks where a demand comes from, why its being operative does not make it right, and what changes when an appointment ends.</p><a href="../accountability/index.html?lang=en">Read the three companion essays →</a></section>'
    zh='<section class="accountability-entry lang-zh account-zh"><p class="entry-num">新增专论 · 三篇 · 英简繁</p><h2>职责与承担</h2><p>原有七篇仍是一条完整主线。本组根据后出的《论职责》，追问要求怎样落在身上、为什么成立不等于正当，以及一次任职结束以后，哪些事情需要分开看。</p><a href="../accountability/index.html?lang=zh">阅读三篇专论散文 →</a></section>'
    hant=conv.convert(zh).replace('account-zh','account-hant').replace('?lang=zh"','?lang=zh-hant"')
    return '<!-- ACCOUNTABILITY COMPANION START -->\n'+en+zh+hant+'\n<!-- ACCOUNTABILITY COMPANION END -->'


def render():
    items=load_items()
    conv=AccountabilityTraditionalConverter()
    try:
        pages={TARGET/'index.html':landing(items,conv)}
        pages.update({TARGET/(i['slug']+'.html'):article(i,items,conv) for i in items})
        path=ROOT/'essays/rights/index.html'
        text=path.read_text()
        entry=rights_entry(conv)
        if '<!-- ACCOUNTABILITY COMPANION START -->' in text:
            text=re.sub(r'<!-- ACCOUNTABILITY COMPANION START -->.*?<!-- ACCOUNTABILITY COMPANION END -->',lambda _:entry,text,flags=re.S)
        else:text=text.replace('    <div class="source-note">',entry+'\n    <div class="source-note">',1)
        pages[path]=text
        return pages
    finally:conv.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    for path,text in render().items():
        if args.check:assert path.read_text()==text,f'Stale output: {path}'
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text)
    print(('Checked' if args.check else 'Wrote')+' four Accountability pages and bounded Rights companion entry')


if __name__=='__main__':main()
