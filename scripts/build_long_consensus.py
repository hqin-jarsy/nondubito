#!/usr/bin/env python3
"""Build five reader essays from Long-τ Consensus, in three reading modes."""
from __future__ import annotations
import argparse
import json
import re

from build_language_writing import ROOT,DATE,WritingTraditionalConverter,page,loc,prose

TARGET=ROOT/'essays/long-consensus'
DATA=ROOT/'data/long-consensus'
SOURCE='https://self-as-an-end.net/papers/sae-long-tau-consensus.html'
BASE='https://nondubito.net/essays/long-consensus/'
TITLE=('What Can Outlast Us?','长存共识')
DECK=('A founder leaves, a manual survives, a reader has no time. Five essays about what lets a shared practice continue—and why lasting is not the same as being right.','创办者离开，一本手册留下，一个读者却没有时间。五篇散文，问一件共同的事怎样有人接着做，也问为什么活得久，不等于它就是对的。')


class ConsensusTraditionalConverter(WritingTraditionalConverter):
    def convert(self,text):
        result=super().convert(text)
        for old,new in (('覈實','核實'),('覈對','核對'),('賬','帳'),('沈到','沉到'),('沈重','沉重'),
                        ('幾只紙箱','幾隻紙箱'),('有點松','有點鬆'),('每周','每週'),('鏈接','連結'),
                        ('硬盤','硬碟'),('文件夾','資料夾'),('工作文檔','工作文件'),('復核','複核'),
                        ('代碼','程式碼'),('模型設置','模型設定'),('詳細設置','詳細設定')):
            result=result.replace(old,new)
        return result


def load_items():
    items=[]
    for i in range(1,6):
        item=json.loads((DATA/f'ep{i:02d}.json').read_text())
        assert item['id']==i and item['slug']==f'ep{i:02d}'
        for lang in ('en','zh'):
            assert item['title_'+lang].strip() and item['deck_'+lang].strip()
            body=item['body_'+lang]
            assert len(body)>=20 and sum(p.startswith('## ') for p in body)==3
            assert all(p.strip() and '<' not in p and not p.startswith('###') for p in body)
            text='\n'.join(body)
            count=len(re.findall(r'[\u3400-\u9fff]',text)) if lang=='zh' else len(text.split())
            assert count >= (2000 if lang=='zh' else 1250),(i,lang,count)
            assert not re.search(r'\b\d{2}DD\b|\b[FT]\d+\b|ψ|ρ|ZFC',text)
        items.append(item)
    return items


def breadcrumb(conv,article=False):
    extra='<span aria-hidden="true">/</span><a href="index.html">'+loc(*TITLE,conv)+'</a>' if article else ''
    return '<nav class="lw-crumb" aria-label="Breadcrumb"><a href="../sae/index.html#shared-life">'+loc('SAE & Philosophy','SAE 与哲学',conv)+'</a>'+extra+'</nav>'


def related(conv):
    links=''.join(f'<a href="../{slug}/index.html">{loc(en,zh,conv)}</a>' for slug,en,zh in (('institution','Institutions','制度论'),('relation','Relations','关系论'),('method','Method','方法论'),('sae','SAE reading map','SAE 散文阅读地图')))
    return '<aside class="lw-related">'+loc('Keep exploring','继续读',conv,'h2')+links+'</aside>'


def reading_note(conv):
    note=loc('Five reader essays drawn from The Four-Phase Structure and Asymmetric Geometry of Long-τ Consensus, not a complete technical translation. Workshops, archives, study rooms and meetings are imagined illustrations, not historical evidence or professional instructions. Four phases and two factors are presented as a proposed lens, not a proven universal law, a group ranking, or a recipe for organizational growth. The paper’s historical interpretations, time ratios, simulations and subjective forecasts remain open to independent testing. Its technical dimension table is not reproduced here. Recognition of a person does not mean endorsing every claim, forbidding departure, or declaring perfect mutual understanding achieved. English is independently written.','本组五篇据《长存共识的四相结构与不对称几何》改写，不是全部技术论证的逐段翻译。作坊、资料室、研习室与聚会等场景为虚构示例，不充当历史证据或专业操作指引。四阶段与两个因素是原论文提出的观察框架，不写成已证实的普遍定律、群体排行榜或组织扩张配方。历史解释、时间比例、模拟结果与主观预测仍待独立检验；本文不复述技术维度表。承认一个人，不等于认同他的全部判断，不限制退出，也不宣称已经达到完美的相互理解。英文独立重写。',conv,'p')
    return '<details class="lw-sources"><summary>'+loc('Source & reading note','原论文与阅读说明',conv)+'</summary>'+note+f'<p><a href="{SOURCE}">'+loc('Read the source paper ↗','阅读原论文 ↗',conv)+'</a> · <a href="https://doi.org/10.5281/zenodo.19984903">DOI: 10.5281/zenodo.19984903</a></p></details>'


def landing(items,conv):
    cards=''.join(f'<a class="lw-card" href="{item["slug"]}.html"><p class="lw-kicker">0{item["id"]}</p>{loc(item["title_en"],item["title_zh"],conv,"h2")}{loc(item["deck_en"],item["deck_zh"],conv,"p")}{loc("Read essay →","阅读全文 →",conv,"span","lw-read")}</a>' for item in items)
    content='<main class="lw-wrap">'+breadcrumb(conv)+'<section class="lw-hero"><p class="lw-kicker">Non Dubito · '+loc('Lasting consensus','长存共识',conv)+'</p>'+loc(*TITLE,conv,'h1')+loc(*DECK,conv,'p','lw-deck lw-search-deck')+loc('Five essays · English, Simplified & Traditional Chinese','五篇 · 英文、简体中文与繁体中文',conv,'p','lw-meta')+'</section><aside class="lw-opening">'+loc('You need not learn a social theory before beginning. Start with a room whose key still belongs to one person.','不必先学社会理论。从一间钥匙仍握在一个人手里的资料室开始。',conv,'p')+'<a href="ep01.html">'+loc('When the founder steps away →','从创办者离开以后读起 →',conv)+'</a></aside><section class="lw-grid">'+cards+'</section><section class="lw-note">'+loc('Continuation, not a promise of eternity','接着做，不是保证永远',conv,'h2')+loc('A name, an audience, an archive and a living practice are different things. This series follows the work of passing understanding to people who can judge for themselves. It also leaves room for questioning, departure and a meaningful undertaking that does not become a tradition. The final essay turns the same questions back on SAE.','一个名字、一群听众、一箱档案和一种活着的实践，不是同一件事。这五篇沿着“后来的人能不能独立理解、判断并接着做”展开，也给质疑、离开，以及没有成为传统却仍有意义的相遇留出位置。最后一篇把这些问题转向 SAE 自己。',conv,'p')+'</section>'+reading_note(conv)+related(conv)+'</main>'
    return page(content,TITLE[0]+' · 长存共识',DECK[0],'essays/long-consensus/index.html',conv)


def article(item,items,conv):
    bodies=''.join(f'<div class="essay-body lw-prose lang-{lang}" lang="{native}">{prose([conv.convert(p) for p in item["body_zh"]] if lang=="hant" else item["body_"+lang])}</div>' for lang,native in (('en','en'),('zh','zh-Hans'),('hant','zh-Hant')))
    neighbors=[]
    for offset,en,zh in ((-1,'Previous essay','上一篇'),(1,'Next essay','下一篇')):
        n=item['id']-1+offset
        if 0<=n<len(items):
            other=items[n]
            neighbors.append(f'<a href="{other["slug"]}.html">{loc(en,zh,conv,"small")}{loc(other["title_en"],other["title_zh"],conv)}</a>')
        else:neighbors.append('<a href="index.html">'+loc('All five essays','全部五篇',conv,'small')+loc(*TITLE,conv)+'</a>')
    content=f'<main class="lw-wrap">{breadcrumb(conv,True)}<article class="lw-article"><div class="lw-head"><p class="lw-kicker">{loc(*TITLE,conv)} · 0{item["id"]}</p>{loc(item["title_en"],item["title_zh"],conv,"h1")}{loc(item["deck_en"],item["deck_zh"],conv,"p","lw-deck lw-search-deck")}<p class="lw-meta">Han Qin · <time datetime="{DATE}">{DATE}</time></p></div>{bodies}{reading_note(conv)}<nav class="lw-series-nav" aria-label="Series navigation">'+''.join(neighbors)+'</nav>'+related(conv)+'</article></main>'
    return page(content,item['title_en'],item['deck_en'],'essays/long-consensus/'+item['slug']+'.html',conv,SOURCE,(BASE,TITLE[0]))


def library_card(conv):
    def t(en,zh,tag='span',css=''):
        return loc(en,zh,conv,tag,css).replace('lang-zh','lang-zh cl-zh').replace('lang-hant','lang-zh cl-hant')
    return '<a href="essays/long-consensus/index.html" class="series-card"><span class="series-card-count">'+t('5 essays · EN / 简 / 繁','5 篇 · 英简繁')+'</span><div class="series-card-title-zh cl-zh">长存共识</div><div class="series-card-title-zh cl-hant">長存共識</div><div class="series-card-title-en">What Can Outlast Us?</div>'+t('A founder leaves, a manual survives, and later people try to understand. Continuation is not immortality, obedience, or proof of being right.','创办者离开，手册留下，后来的人怎样理解、判断并接着做。长存不是永生、服从或正确的证明。','p','series-card-desc')+t('Read series →','阅读系列 →','span','series-card-arrow')+'</a>'


def render():
    items=load_items()
    conv=ConsensusTraditionalConverter()
    try:
        pages={TARGET/'index.html':landing(items,conv)}
        pages.update({TARGET/(i['slug']+'.html'):article(i,items,conv) for i in items})
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
    print(('Checked' if args.check else 'Wrote')+' six Long Consensus pages · three complete reading modes')


if __name__=='__main__':main()
