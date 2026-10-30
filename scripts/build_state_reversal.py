#!/usr/bin/env python3
"""Build three companion readings to State Theory without extending its numbering."""
from __future__ import annotations
import argparse
import json
import re
from build_language_writing import ROOT,WritingTraditionalConverter,page,loc,prose

DATE='2026-10-29'
DATA=ROOT/'data/state-reversal'
TARGET=ROOT/'essays/state-reversal'
BASE='https://nondubito.net/essays/state-reversal/'
STATE_BASE='https://nondubito.net/essays/state/'
SOURCE='https://self-as-an-end.net/papers/sae-state-reverse-phase-transition.html'
TITLE=('When a State Slides Back','国家怎样往回滑？')
DECK=('The court still sits, the legislature still votes, and every office keeps its sign. Three essays ask what changes when decisions can no longer be challenged—and what returning would really require.','法院照常开庭，议会照常表决，机关的牌子也都还在。三篇散文，问决定怎样渐渐问不动了，又问真正回来，需要做哪些事。')


class ReversalTraditionalConverter(WritingTraditionalConverter):
    def convert(self,text):
        result=super().convert(text)
        for old,new in (('覈實','核實'),('覈對','核對'),('復核','複核'),('賬','帳'),('沈重','沉重'),
                        ('鏈接','連結'),('每周','每週'),('兩周','兩週'),('松口氣','鬆口氣'),
                        ('划出','劃出'),('期限仍系在','期限仍繫在'),('啓動','啟動'),('答復','答覆')):
            result=result.replace(old,new)
        return result


def load_items():
    items=[]
    for i in range(1,4):
        item=json.loads((DATA/f'ep{i:02d}.json').read_text())
        assert item['id']==i and item['slug']==f'ep{i:02d}'
        for lang in ('en','zh'):
            assert item['title_'+lang].strip() and item['deck_'+lang].strip()
            body=item['body_'+lang]
            assert len(body)>=20 and sum(p.startswith('## ') for p in body)==3
            assert all(p.strip() and '<' not in p and not p.startswith('###') for p in body)
            text='\n'.join(body)
            count=len(re.findall(r'[\u3400-\u9fff]',text)) if lang=='zh' else len(text.split())
            assert count>=(2300 if lang=='zh' else 1400),(i,lang,count)
            assert not re.search(r'\b\d{2}DD\b|\bN\d+\b|\bZ\d+\b',text)
        items.append(item)
    return items


def breadcrumb(conv,article=False):
    extra='<span aria-hidden="true">/</span><a href="index.html">'+loc(*TITLE,conv)+'</a>' if article else ''
    return '<nav class="lw-crumb" aria-label="Breadcrumb"><a href="../state/index.html">'+loc('Theory of the State','国家论',conv)+'</a>'+extra+'</nav>'


def related(conv):
    links=''.join(f'<a href="../{slug}/index.html">{loc(en,zh,conv)}</a>' for slug,en,zh in (('state','The original eight State essays','国家论原有八篇'),('institution','Institutions','制度论'),('war','War and its limits','战争及其限度'),('sae','SAE reading map','SAE 散文阅读地图')))
    return '<aside class="lw-related">'+loc('Keep exploring','继续读',conv,'h2')+links+'</aside>'


def reading_note(conv):
    text=loc('A three-essay companion drawn from The Reverse Phase Transition, not an extra numbered paper in the original State series. All countries, votes and events belong to the author’s fictional case. The original route stops before the proposed consolidation threshold; the alternative route in essay three is explicitly counterfactual. Philosophical requirements, suggested institutional rules and judgments in particular cases are distinguished. These readings do not state current law, diagnose an actual state or prescribe an actual diplomatic response. English is independently written.','本组三篇据国家论专论《逆相变》改写，不续原有主线篇号。国家、票数与事件均属作者的虚构案例。原案例在建议的“走成”门槛以前停住；第三篇另写明确标注的设想分支。哲学上的要求、建议的制度规则与具体处境中的判断分开，不作现行法律说明，不给现实国家定性，也不替实际外交决定开处方。英文独立重写。',conv,'p')
    return '<details class="lw-sources"><summary>'+loc('Source & reading note','原论文与阅读说明',conv)+'</summary>'+text+f'<p><a href="{SOURCE}">'+loc('The Reverse Phase Transition · source paper ↗','《逆相变》· 原论文 ↗',conv)+'</a> · <a href="https://doi.org/10.5281/zenodo.23779070">DOI: 10.5281/zenodo.23779070</a></p></details>'


def classics(conv):
    return '<section class="lw-note">'+loc('An old question, a different place to look','一个老问题，换一处去看',conv,'h2')+loc('Plato’s Republic, Book VIII, follows changes in constitutions and the people who govern; Montesquieu’s Spirit of the Laws, Book VIII, examines the corruption of a government’s animating principles and its effects on laws. The source paper joins that conversation without adopting a fixed ranking or inevitable decline of constitutions, or diagnosing a ruler’s inner life. Its question is narrower: can those affected still make a decision answer to a route the decision-maker cannot close? This is a difference of focus, not a claim to have refuted either author.','柏拉图《理想国》第八卷读政体及统治者怎样变化；孟德斯鸠《论法的精神》第八卷追问政体的原则怎样腐坏，又怎样使法律变了作用。原论文接着这个老问题往下想，但不沿用一种固定的政体排序或必然下滑的次序，也不去诊断统治者的内心。这里把目光收在另一处：受影响的人，是否仍能沿着决定者自己关不上的路，让一项决定受到追问？这是重心的分别，不是宣布已经驳倒两位作者。',conv,'p')+'<p><a href="https://www.gutenberg.org/files/1497/1497-h/1497-h.htm">'+loc('Plato · Republic, Book VIII ↗','柏拉图 ·《理想国》第八卷 ↗',conv)+'</a> · <a href="https://www.gutenberg.org/cache/epub/27573/pg27573-images.html">'+loc('Montesquieu · Book VIII in the appendix ↗','孟德斯鸠 · 编本附录所收第八卷 ↗',conv)+'</a></p></section>'


def companion_entry(conv):
    cards=''.join(f'<a href="../state-reversal/ep{i:02d}.html">{loc(en,zh,conv)}</a>' for i,en,zh in ((1,'When the doors no longer open','门还在，为什么问不动了？'),(2,'An election is not a reset','选举回来了，事情却没有回到原点'),(3,'Withdraw cooperation, not the way out','不再配合，不是把门关在人身上')))
    return '<!-- STATE REVERSAL COMPANION START --><section class="state-group state-reversal-entry" id="reverse-phase-transition"><p class="state-kicker">'+loc('New companion · Three essays · EN / 简 / 繁','新增专论 · 三篇 · 英简繁',conv)+'</p>'+loc(*TITLE,conv,'h2')+loc('The original eight essays remain a complete route. This companion follows a slide through institutions that still appear intact, an interrupted slide that leaves tools behind, and a counterfactual question about a neighbor’s response.','原有八篇仍是一条完整主线。这三篇另读：机构仍在时怎样往回滑，滑落停住以后还留下什么，以及设若没有停住，邻国怎样回应。',conv,'p','state-deck')+'<div class="state-related">'+cards+'</div><p class="state-return"><a href="../state-reversal/index.html">'+loc('Open the companion →','进入三篇专论 →',conv)+'</a></p></section><!-- STATE REVERSAL COMPANION END -->'


def landing(items,conv):
    cards=''.join(f'<a class="lw-card" href="{d["slug"]}.html"><p class="lw-kicker">0{d["id"]}</p>{loc(d["title_en"],d["title_zh"],conv,"h2")}{loc(d["deck_en"],d["deck_zh"],conv,"p")}{loc("Read essay →","阅读全文 →",conv,"span","lw-read")}</a>' for d in items)
    content='<main class="lw-wrap">'+breadcrumb(conv)+'<section class="lw-hero"><p class="lw-kicker">Non Dubito · '+loc('A State Theory companion','国家论 · 逆相变专论',conv)+'</p>'+loc(*TITLE,conv,'h1')+loc(*DECK,conv,'p','lw-deck lw-search-deck')+loc('Three essays · English, Simplified & Traditional Chinese','三篇 · 英文、简体中文与繁体中文',conv,'p','lw-meta')+'</section><aside class="lw-opening">'+loc('The original eight essays ask where the last authority must still answer. These three follow what happens when those ways of questioning begin to close. You can begin here; the fictional cases are introduced as needed.','原有八篇问：到了最后一层，仍要向谁作答？这三篇往下追：那些问的路，怎样一条条被挪到决定者手里？可以直接读，所需的虚构案例会随文交代。',conv,'p')+'<a href="ep01.html">'+loc('Begin with the doors →','从那些还在的门读起 →',conv)+'</a></aside><section class="lw-grid">'+cards+'</section><section class="lw-note">'+loc('Two routes, not two historical outcomes','两条路线，不是两段历史',conv,'h2')+loc('In the source’s original case, the slide stops. The first two readings stay with that record. The third explicitly asks what would follow if particular safeguards had failed instead. The distinction matters: what one could judge in spring cannot borrow evidence from the following summer, and a hypothetical government action is not a fact about the original case.','原案例里的滑落停住了。前两篇沿这份记录读；第三篇明确另设：如果几处关口没有守住，会怎样？这一区分也约束判断：春天作决定，不能借用夏天才发生的事；设想分支里的行动，不是原案例里已经发生的事实。',conv,'p')+'</section>'+classics(conv)+reading_note(conv)+related(conv)+'</main>'
    return page(content,TITLE[0]+' · 国家论逆相变专论',DECK[0],'essays/state-reversal/index.html',conv)


def article(item,items,conv):
    bodies=''.join(f'<div class="essay-body lw-prose lang-{lang}" lang="{native}">{prose([conv.convert(p) for p in item["body_zh"]] if lang=="hant" else item["body_"+lang])}</div>' for lang,native in (('en','en'),('zh','zh-Hans'),('hant','zh-Hant')))
    navigation=[]
    for offset,en,zh in ((-1,'Previous essay','上一篇'),(1,'Next essay','下一篇')):
        n=item['id']-1+offset
        if 0<=n<len(items):
            d=items[n]
            navigation.append(f'<a href="{d["slug"]}.html">{loc(en,zh,conv,"small")}{loc(d["title_en"],d["title_zh"],conv)}</a>')
        else:navigation.append('<a href="index.html">'+loc('All three companion essays','全部三篇专论',conv,'small')+loc(*TITLE,conv)+'</a>')
    content=f'<main class="lw-wrap">{breadcrumb(conv,True)}<article class="lw-article"><div class="lw-head"><p class="lw-kicker">{loc("A State Theory companion","国家论 · 逆相变专论",conv)} · 0{item["id"]}</p>{loc(item["title_en"],item["title_zh"],conv,"h1")}{loc(item["deck_en"],item["deck_zh"],conv,"p","lw-deck lw-search-deck")}<p class="lw-meta">Han Qin · <time datetime="{DATE}">{DATE}</time></p></div>{bodies}{reading_note(conv)}<nav class="lw-series-nav" aria-label="Series navigation">'+''.join(navigation)+'</nav>'+related(conv)+'</article></main>'
    return page(content,item['title_en'],item['deck_en'],'essays/state-reversal/'+item['slug']+'.html',conv,SOURCE,(STATE_BASE,'Theory of the State'),publication_date=DATE)


def render():
    items=load_items()
    conv=ReversalTraditionalConverter()
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
    print(('Checked' if args.check else 'Wrote')+' four State Reversal companion pages · three complete reading modes')


if __name__=='__main__':main()
