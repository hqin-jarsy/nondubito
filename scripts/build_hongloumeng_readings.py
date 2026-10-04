#!/usr/bin/env python3
"""Render an open-ended Red Chamber essay series with separate language URLs."""
import argparse
import html
import json
from build_hongloumeng_hub import ROOT, TARGET, ORIGIN, EDITIONS, PAPERS, CATALOG, load_readings
from import_fairy_tales import TraditionalConverter

DATE='2026-10-03'
NOTES={
 1:('场景据前八十回第四十八回香菱学诗；关于“有情”的解释参总篇第1、6节。本文把作品中的生活与本项目的读法分开，不将现代哲学命题追认为曹雪芹原话。','The opening draws on Xiangling learning poetry in chapter 48. The interpretation of qing follows sections 1 and 6 of the overview; it is the project’s reading, not a philosophical formulation attributed to Cao Xueqin.'),
 2:('通行续书的焚稿、中举与家道复初，分别参第九十七、一一九、一二〇回；比较与创作边界见总篇第3节。这里说明本项目为何另写，不声称证明了佚稿的真实结局。','The received continuation’s burning of the poems, examination success and restored family fortunes are discussed through chapters 97, 119 and 120. See section 3 of the overview for the project’s comparison and boundaries. This explains a creative decision, not a recovered historical ending.'),
 3:('参前八十回第五回判词、第四十一回品茶与第四十八回学诗，以及总篇第4、6、9节、专题一。把未来指向文字区分为走向与判语，是本项目的处理方式；不冒充无争议的原作释义。','See the registers in chapter 5, tea in chapter 41 and poetry in chapter 48, alongside sections 4, 6 and 9 of the overview and paper 1. Distinguishing anticipated events from verdicts is the project’s interpretive method, not an uncontested account of the original.'),
 4:('两条批语的来路、取舍与复核方法，参专题一及总篇第6节。靖本批语按项目所用传录引述，原件已佚；不同批语所见可能不是同稿，不等于已证实若干部完整失稿。','The commentary, choices and checking procedure follow paper 1 and section 6 of the overview. The Jing note is reported through the project’s transcription source; the original manuscript is lost. Different possible drafts do not establish the historical existence of several complete lost books.'),
 5:('本文依专题二介绍成书材料与工作假说，尤其第3、6、7节。节气推算及其撤回转述论文中的复核，不宣称本次散文另作了历算。具体历史归属与文学解释的成立条件分别处理。','This essay follows paper 2, especially sections 3, 6 and 7. The calendar recalculation and withdrawal are reported from that paper, not presented as a new calculation performed for this essay. Historical attribution and literary interpretation retain separate evidentiary requirements.'),
 6:('以专题三的限定和修正为准，不沿用总篇把未公开原件笼统称作“抄本”的说法。公开记录、工作假说、写作借鉴和历史旁证各自区分；未将“有来源说明”写成无需进一步处理字句使用。','Paper 3 supplies the current qualifications, including the distinction between a circulating version and an unexamined claimed manuscript. Public records, working hypotheses, creative debts and historical corroboration remain separate. Acknowledgment is not represented as automatically resolving the use of matching wording.')
}
SPOILERS={
 'earlier':('涉及前八十回人物与情节；不揭开原创后三十回的关键转折。','Discusses people and scenes from the first eighty chapters; withholds the new continuation’s crucial turns.'),
 'received-ending':('涉及程高本后四十回的结局；不披露原创后三十回的具体替代情节。','Discusses endings in the received forty-chapter continuation; does not disclose the new fiction’s specific alternatives.'),
 'commentary':('涉及批语对人物后事的提示；不披露原创续写的具体结局。','Discusses the commentary’s hints about later events; does not disclose the new fiction’s particular endings.'),
 'materials':('介绍材料与创作取舍；不展开原创后三十回的关键救援、转折或最终归宿。','Discusses sources and creative choices without revealing crucial rescues, turns or final destinations in the new fiction.')
}

class Converter(TraditionalConverter):
    def convert(self,s):
        result=super().convert(s).replace('“','「').replace('”','」')
        for old,new in {'余項':'餘項','關系':'關係','里面':'裡面','准':'準','反復':'反覆','想象':'想像','贊美':'讚美','贊嘆':'讚嘆','沈默':'沉默'}.items():
            result=result.replace(old,new)
        return result

def build():
    items=load_readings()
    assert items and [i['number'] for i in items]==list(range(1,len(items)+1))
    catalog={e['url']:e for g in json.loads(CATALOG.read_text()) for e in g['essays']}
    converter=Converter(); outputs={}
    try:
        for lang,(directory,code,label) in EDITIONS.items():
            def raw(zh,en): return en if lang=='en' else converter.convert(zh) if lang=='zh-hant' else zh
            def t(zh,en): return html.escape(raw(zh,en),quote=True)
            up='../' if directory else ''; base='../../../../' if directory else '../../../'
            for pos,item in enumerate(items):
                copy=item['en' if lang=='en' else 'zh']
                def tx(value): return html.escape(converter.convert(value) if lang=='zh-hant' else value,quote=True)
                name=item['slug']+'.html'; canonical=ORIGIN+directory+name
                title=raw(item['zh']['title'],item['en']['title']); deck=raw(item['zh']['deck'],item['en']['deck'])
                alternates=''.join(f'<link rel="alternate" hreflang="{c}" href="{ORIGIN+d+name}">' for d,c,_ in EDITIONS.values())
                alternates+=f'<link rel="alternate" hreflang="x-default" href="{ORIGIN+name}">'
                language_links=''.join(f'<a href="{up+d+name}?lang={key}" data-edition="{key}" lang="{c}"'+(' aria-current="page"' if key==lang else '')+'>'+label_+'</a>' for key,(d,c,label_) in EDITIONS.items())
                sections=''.join('<section id="section-'+str(n)+'"><h2>'+tx(s['heading'])+'</h2>'+''.join('<p>'+tx(p)+'</p>' for p in s['paragraphs'])+'</section>' for n,s in enumerate(copy['sections'],1))
                source_links=''.join(f'<li><a href="https://self-as-an-end.net/papers/sae-hongloumeng-{n}.html">'+t(PAPERS[n][0],PAPERS[n][1])+'</a></li>' for n in item['papers'])
                related=''.join('<li><a href="'+up+url+'?lang='+('en' if lang=='en' else 'zh')+'" data-legacy-language="'+('en' if lang=='en' else 'zh')+'">'+t(catalog[url]['zh'],catalog[url]['en'])+'</a></li>' for url in item['related'])
                nav=[]
                for n,zh,en in [(pos-1,'上一篇','Previous'),(pos+1,'下一篇','Next')]:
                    if 0<=n<len(items):
                        other=items[n];url=other['slug']+'.html';caption=t(other['zh']['title'],other['en']['title'])
                    else: url='index.html?lang='+lang+'#readings';caption=t('回到散文目录','Back to the essay list');zh,en='专题','The project'
                    nav.append('<a href="'+url+'"><small>'+t(zh,en)+'</small><span>'+caption+'</span></a>')
                schema={'@context':'https://schema.org','@type':'Article','headline':title,'description':deck,'url':canonical,'mainEntityOfPage':canonical,'inLanguage':code,'author':{'@type':'Person','name':'Han Qin (秦汉)'},'datePublished':DATE,'dateModified':DATE,'isPartOf':{'@type':'CollectionPage','name':raw('人是有情的——重读《红楼梦》','Lives Beyond Their Endings'),'url':ORIGIN+directory},'citation':[f'https://self-as-an-end.net/papers/sae-hongloumeng-{n}.html' for n in item['papers']]}
                body=f'''<nav class="reading-crumbs" aria-label="{t('当前位置','Breadcrumbs')}"><a href="index.html?lang={lang}">{t('红楼梦专题','The Red Chamber project')}</a><span>/</span><a href="index.html?lang={lang}#readings">{t('散文导读','Reader essays')}</a></nav>
<article><header class="reading-head"><p class="eyebrow">{t('人是有情的 · 散文导读','LIVES BEYOND THEIR ENDINGS · READER ESSAYS')} · {item['number']:02}</p><h1>{html.escape(title)}</h1><p class="deck">{html.escape(deck)}</p><p class="reading-byline">{t('秦汉','Han Qin')} · {DATE}</p><p class="reading-scope">{t(*SPOILERS[item['spoiler']])}</p></header>
<div class="reading-prose">{sections}</div>
<details class="reading-sources"><summary>{t('想进一步看依据与论文','Sources and further reading')}</summary><p>{t(*NOTES[item['number']])}</p><aside class="spoiler"><p>{t('以下论文含原创后三十回的详细情节与结局；若想先读小说，可以暂时跳过。','The linked papers contain detailed spoilers for the original continuation. You can leave them until after reading the fiction.')}</p></aside><ul>{source_links}</ul></details>
<aside class="reading-related"><h2>{t('再走近一个人物','Return to the people')}</h2><ul>{related}</ul><p class="edition-note">{t('人物旧文为简中／英文双语；繁体读者点击后暂进入简体原文。','The earlier character essays have Simplified Chinese and English versions; the Traditional edition links to the Simplified original.')}</p></aside>
<nav class="reading-next" aria-label="{t('继续阅读','Continue reading')}">{''.join(nav)}</nav>
<p class="reading-open">{t('这组散文会随后续专题研究继续增补。你不必先读论文，也不必一次读完；从一个问题进入就好。','This essay sequence will grow with the research. No paper is required first, and you need not read everything at once. Begin with a question.')}</p></article>'''
                outputs[TARGET/directory/name]=f'''<!doctype html>
<html lang="{code}" data-lang="{lang}" data-editions="{code}" data-explicit-edition="true"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — Non Dubito</title><meta name="description" content="{html.escape(deck,quote=True)}"><meta name="author" content="Han Qin"><link rel="canonical" href="{canonical}">{alternates}<meta property="og:title" content="{html.escape(title,quote=True)}"><meta property="og:description" content="{html.escape(deck,quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="article"><meta name="twitter:card" content="summary"><link rel="icon" href="{base}favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{up}hongloumeng-hub.css?v=20261003"><script defer src="{up}hongloumeng-hub.js?v=20261003"></script><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head>
<body class="reading-page"><a class="skip" href="#main">{t('跳到正文','Skip to content')}</a><header class="site-header"><a class="brand" href="{base}index.html?lang={lang}">Non <span>Dubito</span></a><nav aria-label="{t('网站导航','Site navigation')}"><a href="index.html?lang={lang}">{t('红楼专题','Red Chamber')}</a><a href="{base}library.html?lang={lang}">{t('书库','Library')}</a><a href="{base}search.html?lang={lang}">{t('搜索','Search')}</a></nav><details class="language-menu"><summary>{label} <span aria-hidden="true">⌄</span></summary><nav aria-label="{t('阅读语言','Reading language')}">{language_links}</nav></details></header><main id="main">{body}</main><footer><a href="index.html?lang={lang}#readings">{t('回到红楼梦散文导读','Back to the Red Chamber reader essays')}</a><p>Non Dubito · {t('秦汉','Han Qin')}</p></footer><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script></body></html>
'''
        return outputs
    finally: converter.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    outputs=build()
    if args.check:
        assert all(p.exists() and p.read_text()==s for p,s in outputs.items()),'Stale Red Chamber readings'
        print(f'OK: {len(outputs)} reproducible reader-essay pages')
    else:
        for p,s in outputs.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
        print(f'Wrote {len(outputs)} reader-essay pages')
