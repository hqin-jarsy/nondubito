#!/usr/bin/env python3
"""Render only the reviewed EP02 editions; never translate or rewrite prose."""
import argparse
import hashlib
import html
import json
import re

import markdown
import build_ouya_full_editions as shared

ROOT, DATA, SERIES, LANGS = shared.ROOT, shared.DATA, shared.SERIES, shared.LANGS
DECKS = {
 'zh-Hans':'征服可以很快，新的秩序却不能随军队一同抵达。从亚历山大到继业者，从村口收据到城市议事，追问城邦的构能否走进帝国。',
 'zh-Hant':'征服可以很快，新的秩序卻不能隨軍隊一同抵達。從亞歷山大到繼業者，從村口收據到城市議事，追問城邦的構能否走進帝國。',
 'en':'Conquest can be swift; a lasting order cannot simply march in with an army. From Alexander to his successors, village receipts and civic negotiations reveal the limits of exporting the polis.',
 'ja':'征服は速くても、新しい秩序は軍隊とともには届かない。アレクサンドロスから後継者たちへ。村の受領証や都市の交渉から、ポリスの構を帝国へ移せるのかを考える。',
 'fr':"Une conquête peut être rapide ; un ordre durable ne suit pas au pas de l'armée. D'Alexandre à ses successeurs, reçus villageois et négociations civiques interrogent les limites de la polis à l'échelle impériale.",
 'de':'Eroberung kann schnell gehen; eine dauerhafte Ordnung marschiert nicht einfach mit. Von Alexander zu seinen Nachfolgern zeigen Dorfquittungen und städtische Verhandlungen die Grenzen einer Polis im Reichsmaßstab.',
 'es':'La conquista puede ser rápida; un orden duradero no llega con el ejército. De Alejandro a sus sucesores, los recibos de aldea y las negociaciones cívicas muestran los límites de trasladar la polis al imperio.',
 'ko':'정복은 빠를 수 있지만 새로운 질서가 군대와 함께 도착하지는 않는다. 알렉산드로스와 후계자들, 마을의 영수증과 도시의 협상을 통해 폴리스의 구성체를 제국으로 옮길 수 있는지 묻는다.'
}
NOTES = {
 'zh-Hans':'本文用凿构周期律回看历史，不把这一解释框架当作古人的自述。文化交融不等于权力平等；法规与留存文书也不代表生活的全部。以下材料提供进一步阅读的入口，并非对全文每项判断的逐句证明。',
 'zh-Hant':'本文用鑿構週期律回看歷史，不把這一解釋框架當作古人的自述。文化交融不等於權力平等；法規與留存文書也不代表生活的全部。以下材料提供進一步閱讀的入口，並非對全文每項判斷的逐句證明。',
 'en':'The chisel–construct cycle is this essay’s interpretive lens, not the ancient actors’ own account. Cultural mixing does not imply equal power, and regulations and surviving documents do not encompass all of life. These sources offer further reading, not sentence-by-sentence proof of every interpretation.',
 'ja':'鑿構周期律は本篇が歴史を読むための枠組みであり、古代の人々自身の説明ではない。文化が混ざることは権力の平等を意味せず、法規や残された文書も生活のすべてではない。以下は理解を深めるための資料であり、本文の解釈を一文ずつ証明するものではない。',
 'fr':"Le cycle de sape et de construction est ici une grille de lecture, non le récit que les acteurs antiques faisaient d'eux-mêmes. Le mélange culturel n'implique pas l'égalité du pouvoir ; règlements et documents conservés n'épuisent pas la vie sociale. Ces sources ouvrent des pistes de lecture, sans prouver chaque interprétation phrase par phrase.",
 'de':'Der Zyklus von Aufbrechen und Gefügebildung ist die Deutungsperspektive dieses Essays, nicht die Selbstbeschreibung der antiken Handelnden. Kulturelle Mischung bedeutet keine Machtgleichheit; Vorschriften und erhaltene Dokumente erfassen nicht das ganze Leben. Diese Quellen laden zur weiteren Lektüre ein, ohne jede Deutung Satz für Satz zu beweisen.',
 'es':'El ciclo de desbastado y construcción es la perspectiva interpretativa de este ensayo, no la descripción de los propios actores antiguos. La mezcla cultural no implica igualdad de poder; las normas y los documentos conservados tampoco abarcan toda la vida. Estas fuentes abren caminos de lectura, sin demostrar frase por frase cada interpretación.',
 'ko':'깎기와 구성의 주기는 이 글이 역사를 읽는 틀이지 고대인 자신의 설명이 아니다. 문화가 섞인다고 권력이 평등해지는 것은 아니며, 법규와 남아 있는 문서가 삶의 전부를 담지도 않는다. 아래 자료는 더 읽기 위한 길잡이이지 모든 해석을 문장마다 입증하는 근거 목록은 아니다.'
}
SOURCES = [
 ('Royal Correspondence 36 · Antiochos III and Laodike', 'https://www.attalus.org/docs/rc/s36.html'),
 ('Select Papyri II.203 · Ptolemaic revenue regulations', 'https://www.attalus.org/docs/select2/p203.html'),
 ('Rosetta Stone · Greek text in translation', 'https://www.attalus.org/egypt/rosettastone.html'),
 ('Encyclopaedia Iranica · Greek Art in Central Asia', 'https://www.iranicaonline.org/articles/greece-viii/'),
 ('Encyclopaedia Iranica · Heliocles I', 'https://www.iranicaonline.org/articles/heliocles-i/'),
 ('Encyclopaedia Iranica · Seleucid Era', 'https://www.iranicaonline.org/articles/seleucid-era/'),
 ('University of Giessen · Constitutio Antoniniana', 'https://www.constitutio.de/en/constitutio-antoniniana/the-text-of-the-edict'),
 ('Stanford Encyclopedia of Philosophy · Dignity', 'https://plato.stanford.edu/entries/dignity/')
]

def manuscripts():
    receipt=json.loads((DATA/'ep02-review.json').read_text())
    result={}
    for lang in LANGS:
        raw=(DATA/f'ep02.{lang}.md').read_text()
        assert hashlib.sha256(raw.encode()).hexdigest()==receipt['published_sha256'][lang],lang
        blocks=raw.strip().split('\n\n')
        assert blocks[0].startswith('# ') and blocks[1].startswith('Han Qin')
        body='\n\n'.join(blocks[2:])
        assert len(re.findall(r'^## ',body,re.M))==9,lang
        assert len([p for p in blocks[2:] if not p.startswith('## ')])==131,lang
        result[lang]={'title':blocks[0][2:], 'body':body}
    return result

def body_html(lang,copy):
    text=markdown.markdown(copy['body'])
    sections=iter(range(1,10))
    text=re.sub(r'<h2>',lambda _:f'<h2 id="{lang.lower()}-section-{next(sections)}">',text)
    links='\n'.join(f'<li><a href="{html.escape(url,quote=True)}">{html.escape(label)}</a></li>' for label,url in SOURCES)
    label=shared.NOTES[lang][0]
    return f'<div class="ouya-full" data-edition="v0.1.1-local-20260927">\n{text}\n</div>\n<aside class="ouya-sources"><h2>{label}</h2><p>{html.escape(NOTES[lang])}</p><ul>{links}</ul></aside>'

def menu(lang):
    return shared.language_menu(lang).replace('ep01.html','ep02.html')

def outputs():
    copies=manuscripts();out={}
    root=SERIES/'ep02.html';s=root.read_text()
    for code,lang in [('zh','zh-Hans'),('en','en')]:
        s=shared.replace_div(s,'essay-body lang-'+code,body_html(lang,copies[lang]))
        s=re.sub(r'(<h1 class="lang-'+code+r'">).*?(</h1>)',lambda m:m[1]+html.escape(copies[lang]['title'])+m[2],s,flags=re.S)
    s=re.sub(r'<div class="lang-toggle">.*?</div>',menu('root'),s,flags=re.S)
    s=re.sub(r'<script(?: id="ouya-inline-language")?>.*?</script>',lambda m:shared.STATE_SCRIPT if ('var saved' in m[0] or 'ouya-inline-language' in m[0]) else m[0],s,flags=re.S)
    s=shared.metadata(s,copies['zh-Hans']['title'],DECKS['zh-Hans'],'https://nondubito.net/essays/ouya/ep02.html')
    out[root]=shared.resources(s,'../../')
    for lang in ('ja','fr','de','es','ko','zh-Hant'):
        p=SERIES/lang.lower()/'ep02.html'
        s=p.read_text() if p.exists() else (SERIES/'ja/ep02.html').read_text()
        s=shared.replace_div(s,'essay-body',body_html(lang,copies[lang]))
        s=re.sub(r'<html lang="[^"]*">',f'<html lang="{lang}">',s)
        s=re.sub(r'<div class="lang-toggle">.*?</div>',menu(lang),s,flags=re.S)
        s=re.sub(r'(<h1\b[^>]*>).*?(</h1>)',lambda m:m[1]+html.escape(copies[lang]['title'])+m[2],s,count=1,flags=re.S)
        s=re.sub(r'<p class="essay-subtitle">.*?</p>\s*','',s,flags=re.S)
        s=re.sub(r'<a class="ouya-series-back".*?</a>\s*','',s,flags=re.S)
        label={'ja':'← シリーズ目次','fr':'← Tous les essais','de':'← Zur Reihe','es':'← Índice de la serie','ko':'← 시리즈 목차','zh-Hant':'← 系列目錄（簡體／English）'}[lang]
        href='index.html' if lang!='zh-Hant' else '../index.html'
        s=s.replace('<header class="essay-header">',f'<a class="ouya-series-back" href="{href}">{label}</a>\n<header class="essay-header">',1)
        if lang=='zh-Hant':
            s=re.sub(r'<div class="essay-series-label">.*?</div>','<div class="essay-series-label">鑿構週期律 · 歐亞帝王系列 — 第02篇／共22篇</div>',s)
            subs=iter(['上一篇','下一篇（簡體）'])
            titles=iter(['雅典與斯巴達','羅馬共和國'])
            s=re.sub(r'<span class="xiyou-nav-sub">.*?</span>',lambda _:f'<span class="xiyou-nav-sub">{next(subs)}</span>',s)
            s=re.sub(r'<span class="xiyou-nav-title">.*?</span>',lambda _:f'<span class="xiyou-nav-title">{next(titles)}</span>',s)
            s=re.sub(r'href="(?:\.\./)?ep03.html(?:\?lang=zh)?"','href="../ep03.html?lang=zh" onclick="localStorage.setItem(\'nd_lang\',\'zh\')"',s)
            s=s.replace(' onclick="localStorage.setItem(\'nd_lang\',\'zh\')" onclick="localStorage.setItem(\'nd_lang\',\'zh\')"',' onclick="localStorage.setItem(\'nd_lang\',\'zh\')"')
        s=shared.metadata(s,copies[lang]['title'],DECKS[lang],f'https://nondubito.net/essays/ouya/{lang.lower()}/ep02.html')
        out[p]=shared.resources(s,'../../../')
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for path,text in outputs().items():
        if args.check:
            assert path.exists() and path.read_text()==text,f'Stale: {path}'
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    print(('OK' if args.check else 'Wrote')+': 7 EP02 URLs, 8 complete editions')

if __name__=='__main__':main()
