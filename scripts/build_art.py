#!/usr/bin/env python3
"""Build the expandable eight-edition art shelf from reviewed manuscripts.

Add published works to data/art/works.json; do not edit generated HTML.
Run --images once after importing an artwork's originals (requires Pillow),
then run normally or use --check. No translation service is used.
"""
import argparse
import html
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/art'
TARGET = ROOT / 'essays/art'
ORIGIN = 'https://nondubito.net/'
LANGS = {'zh': ('zh-Hans', '', '简体中文'), 'zh-hant': ('zh-Hant', 'zh-hant/', '繁體中文'),
         'en': ('en', 'en/', 'English'), 'ja': ('ja', 'ja/', '日本語'),
         'fr': ('fr', 'fr/', 'Français'), 'de': ('de', 'de/', 'Deutsch'),
         'es': ('es', 'es/', 'Español'), 'ko': ('ko', 'ko/', '한국어')}
# shelf, category, introduction, guide, fallback note, library, search,
# read, contents, full image, optional bridge, references, credits, top
UI = {
 'zh': ['艺术作品细读','绘画 · 西方绘画','先看作品，再谈它为什么打动我们。从细节、材料与观看经验出发，每篇都可以独立阅读。','美学导读','简体中文、繁体中文与英文','书库','搜索','阅读文章 →','这篇谈什么','点击查看高清图','想了解背后的问题，可以先读本站的美学导读，再按兴趣走向原论文。','参考资料','图像来源与使用说明','回到页首'],
 'zh-hant': ['藝術作品細讀','繪畫 · 西方繪畫','先看作品，再談它為什麼打動我們。從細節、材料與觀看經驗出發，每篇都可以獨立閱讀。','美學導讀','簡體中文、繁體中文與英文','書庫','搜尋','閱讀文章 →','這篇談什麼','點擊查看高解析度圖片','想了解背後的問題，可以先讀本站的美學導讀，再按興趣走向原論文。','參考資料','圖像來源與使用說明','回到頁首'],
 'en': ['Looking Closely at Art','Painting · Western painting','Look at the work first. Then ask what moves us. Each essay begins with details, materials and the experience of looking, and can be read on its own.','A guide to aesthetics','English and both Chinese editions','Library','Search','Read the essay →','In this essay','Open the full-resolution image','For the questions behind this reading, start with our accessible guide to aesthetics; the academic papers are further reading.','References','Image credits and usage','Back to top'],
 'ja': ['美術作品をじっくり見る','絵画 · 西洋絵画','まず作品を見て、心を動かされる理由を考える。細部や素材、見る経験から始まる、一篇ずつ読める鑑賞の手引き。','美学の入門エッセイ','英語・簡体字中国語・繁体字中国語','ライブラリ','検索','本文を読む →','この記事の内容','高解像度画像を開く','背景にある問いを知りたくなったら、まず当サイトの美学入門へ。原論文は、さらに詳しく読みたい方のために。','参考資料（英語）','画像の出典と利用条件（英語）','ページの先頭へ'],
 'fr': ['Regarder l’art de près','Peinture · Peinture occidentale','Regarder l’œuvre avant de chercher ce qui nous touche. Chaque essai part des détails, des matières et de l’expérience du regard, et peut se lire seul.','Introduction à l’esthétique','En anglais et en chinois simplifié ou traditionnel','Bibliothèque','Rechercher','Lire l’essai →','Dans cet essai','Ouvrir l’image en haute résolution','Pour explorer les questions derrière cette lecture, commencez par notre introduction à l’esthétique ; les articles théoriques permettent d’aller plus loin.','Références (en anglais)','Crédits et utilisation des images (en anglais)','Haut de page'],
 'de': ['Kunst genau betrachtet','Malerei · Westliche Malerei','Erst das Werk betrachten, dann fragen, was uns berührt. Jeder Essay geht von Einzelheiten, Materialien und der Erfahrung des Sehens aus und lässt sich für sich lesen.','Einführung in die Ästhetik','Auf Englisch und in beiden chinesischen Schriftformen','Bibliothek','Suche','Essay lesen →','In diesem Essay','Bild in voller Auflösung öffnen','Wer den Fragen hinter dieser Betrachtung nachgehen möchte, kann mit unserer Einführung in die Ästhetik beginnen. Die wissenschaftlichen Texte führen weiter.','Quellen (auf Englisch)','Bildnachweise und Nutzung (auf Englisch)','Nach oben'],
 'es': ['Mirar el arte de cerca','Pintura · Pintura occidental','Primero mirar la obra; después, preguntarnos qué nos conmueve. Cada ensayo parte de los detalles, los materiales y la experiencia de mirar, y puede leerse por separado.','Introducción a la estética','En inglés y en chino simplificado o tradicional','Biblioteca','Buscar','Leer el ensayo →','En este ensayo','Abrir la imagen en alta resolución','Para explorar las preguntas que hay detrás de esta lectura, empieza por nuestra introducción a la estética; los artículos académicos permiten profundizar.','Referencias (en inglés)','Créditos y uso de imágenes (en inglés)','Volver arriba'],
 'ko': ['미술 작품 자세히 보기','회화 · 서양 회화','먼저 작품을 보고, 무엇이 마음을 움직이는지 묻는다. 세부와 재료, 바라보는 경험에서 출발하며 각 글은 따로 읽어도 좋다.','미학 입문 에세이','영어·중국어 간체·번체 제공','서재','검색','글 읽기 →','이 글의 구성','고해상도 이미지 보기','이 감상 뒤에 놓인 질문이 궁금하다면, 먼저 이 사이트의 미학 입문을 읽어 보자. 원논문은 더 깊이 읽고 싶은 독자를 위한 자료다.','참고 자료 (영어)','이미지 출처와 이용 안내 (영어)','맨 위로']
}


def esc(value): return html.escape(str(value), quote=True)


def rel(path, target):
    return os.path.relpath(target, path.parent).replace(os.sep, '/')


def canonical(path):
    return ORIGIN + path.relative_to(ROOT).as_posix().removesuffix('index.html')


def location(lang, work=None):
    base = TARGET / LANGS[lang][1]
    return base / work['category'] / (work['slug']+'.html') if work else base/'index.html'


def load(work, lang):
    return re.split(r'\n\s*\n', (DATA/work['id']/f"{work['source_prefix']}_{LANGS[lang][0]}.md").read_text().strip())


def inline(text):
    """Escaped prose plus the reviewed Markdown's links and emphasis."""
    parts = re.split(r'(\[[^\]]+\]\([^\s)]+\))', text)
    result = []
    for part in parts:
        match = re.fullmatch(r'\[([^\]]+)\]\(([^\s)]+)\)', part)
        if match:
            label, url = match.groups()
            url = {'REFERENCES.md':'#references','IMAGE_CREDITS.md':'#image-credits'}.get(url,url)
            assert url.startswith(('https://','#')), url
            result.append(f'<a href="{esc(url)}">{esc(label)}</a>')
        else:
            value = esc(part)
            value = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', value)
            value = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', value)
            result.append(value)
    return ''.join(result)


def guide(lang, path):
    choice = lang if lang in ('zh','zh-hant','en') else 'en'
    folder = '' if choice=='zh' else choice+'/'
    return rel(path, ROOT/f'essays/aesthetics/{folder}seeing-beauty.html')+'?lang='+choice


def bridge(lang, path):
    u=UI[lang]
    return f'<aside class="source-note"><p>{esc(u[10])}</p><a href="{guide(lang,path)}">{esc(u[3])} →</a><p class="edition-note">{esc(u[4])}</p></aside>'


def image_tag(path, work, name, alt, lazy=True):
    info=json.loads((DATA/'images.json').read_text())[work['id']+'/'+name]
    original=TARGET/'images'/work['id']/name
    stem=original.with_suffix('')
    src=rel(path,Path(str(stem)+'-640.webp'))
    larger=rel(path,Path(str(stem)+'-1280.webp'))
    return f'<img src="{src}" srcset="{src} 640w, {larger} {min(1280,info[0])}w" sizes="(max-width: 600px) calc(100vw - 46px), 760px" width="{info[0]}" height="{info[1]}" alt="{esc(alt)}" loading="{"lazy" if lazy else "eager"}" decoding="async">'


def documents(work, lang):
    blocks=[]
    for filename, anchor, label in [('REFERENCES.md','references',UI[lang][11]),('IMAGE_CREDITS.md','image-credits',UI[lang][12])]:
        source=(DATA/work['id']/'source'/filename).read_text()
        marker='## English'
        bilingual = marker not in source
        if not bilingual:
            source = source.split(marker)[0] if lang in ('zh','zh-hant') else marker+source.split(marker,1)[1]
        elif lang not in ('zh','zh-hant'):
            # Later source dossiers interleave Chinese and English rather than
            # providing two separate sections. Label them honestly; keep both.
            label = label.split(' (')[0].split('（')[0] + ' · 中文 / English'
        rendered=[]
        for block in source.strip().split('\n\n'):
            if block.startswith('#'):
                rendered.append('<h3>'+esc(block.lstrip('# '))+'</h3>')
            else:
                rendered.append('<p>'+inline(block).replace('\n','<br>')+'</p>')
        # Source records are archival Chinese or English, not silently translated.
        code='mul' if bilingual else ('zh-Hans' if lang in ('zh','zh-hant') else 'en')
        blocks.append(f'<details class="source-details" id="{anchor}"><summary>{esc(label)}</summary><div lang="{code}">'+''.join(rendered)+'</div></details>')
    return ''.join(blocks)


def article(work, lang, path):
    blocks=load(work,lang); body=[]; headings=[]; i=2; n=0
    heading_count=sum(block.startswith('## ') for block in blocks)
    # Every manuscript ends in an optional reading and image/source notes;
    # the number of preceding close-reading sections belongs to the essay.
    optional=work.get('main_sections', 5)+1
    assert heading_count == optional+1, (work['id'],lang,heading_count)
    while i<len(blocks):
        b=blocks[i]
        if b.startswith('## '):
            n+=1; label=b[3:]; anchor='section-'+str(n); headings.append((anchor,label))
            if n==optional:
                body.append(f'<details class="optional-reading" id="{anchor}"><summary>{esc(label)}</summary>{bridge(lang,path)}<div>')
            else:
                if n==optional+1: body.append('</div></details>')
                body.append(f'<h2 id="{anchor}">{esc(label)}</h2>')
        elif b.startswith('!['):
            m=re.fullmatch(r'!\[([^\]]*)\]\(images/([^)]+)\)',b); assert m,b
            alt,name=m.groups(); caption=blocks[i+1]; assert not caption.startswith(('#','!'))
            body.append(f'<figure><a href="{rel(path,TARGET/"images"/work["id"]/name)}">{image_tag(path,work,name,alt,name!=work["image"])}</a><figcaption>{inline(caption)}<span class="image-hint">{esc(UI[lang][9])}</span></figcaption></figure>')
            i+=1
        else: body.append('<p>'+inline(b)+'</p>')
        i+=1
    assert n==heading_count
    toc='<details class="contents"><summary>'+esc(UI[lang][8])+'</summary><nav>'+''.join(f'<a href="#{a}">{esc(h)}</a>' for a,h in headings)+'</nav></details>'
    return toc+'<article class="prose">'+''.join(body)+'</article>'+documents(work,lang)


def page(lang, path, title, deck, content, work=None):
    code, directory, label=LANGS[lang]; u=UI[lang]; url=canonical(path)
    alternates=''.join(f'<link rel="alternate" hreflang="{c}" href="{canonical(location(k,work))}">' for k,(c,_,_) in LANGS.items())
    alternates+=f'<link rel="alternate" hreflang="x-default" href="{canonical(location("zh",work))}">'
    switch=''.join(f'<a href="{rel(path,location(k,work))}?lang={k}" lang="{c}" data-edition="{k}"'+(' aria-current="page"' if k==lang else '')+f'>{esc(name)}</a>' for k,(c,_,name) in LANGS.items())
    schema={'@context':'https://schema.org','@type':'Article' if work else 'CollectionPage','name':title,'description':deck,'url':url,'inLanguage':code,'isPartOf':{'@type':'WebSite','name':'Non Dubito','url':ORIGIN}}
    if work:
        schema.update(headline=title,datePublished=work['date'],dateModified=work['date'],author={'@type':'Person','name':'Han Qin'},image=ORIGIN+'essays/art/images/'+work['id']+'/'+work['image'],about={'@type':work['schema_type'],'name':work['work_name'],'creator':{'@type':'Person','name':work['artist']},'sameAs':work['about']})
    search_lang=lang if lang in ('zh','en','zh-hant') else 'en'
    home=rel(path,ROOT/'index.html')+'?lang='+search_lang
    if lang in ('ja','fr','de','es','ko'):
        home=rel(path,ROOT/f'essays/{lang}/index.html')
    search_url=rel(path,ROOT/'search.html')+'?lang='+search_lang+'&amp;in='+code
    if lang in ('ja','fr','de','es','ko'): search_url+='&amp;ui='+lang
    back=rel(path,location(lang))+'?lang='+lang if work else guide(lang,path)
    backlabel=u[0] if work else u[3]+(' · '+u[4] if lang not in ('zh','zh-hant','en') else '')
    heroimage=f'<meta property="og:image" content="{schema["image"]}">' if work else ''
    return f'''<!doctype html>
<html lang="{code}" data-lang="{lang}" data-editions="{code}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(deck)}"><meta name="author" content="Han Qin (秦汉)">
<link rel="canonical" href="{url}">{alternates}<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(deck)}"><meta property="og:type" content="{'article' if work else 'website'}"><meta property="og:url" content="{url}">{heroimage}<meta name="twitter:card" content="{'summary_large_image' if work else 'summary'}">
<link rel="icon" href="{rel(path,ROOT/'favicon.svg')}"><link rel="stylesheet" href="{rel(path,ROOT/'essays/aesthetics/aesthetics-hub.css')}"><link rel="stylesheet" href="{rel(path,TARGET/'art.css')}">
<script defer src="{rel(path,ROOT/'essays/aesthetics/aesthetics-hub.js')}"></script><script defer src="{rel(path,TARGET/'art.js')}"></script>
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('<',chr(92)+'u003c')}</script></head>
<body class="aesthetics-site art-page"><a class="skip" href="#main">↓ {esc(title)}</a>
<header class="aesthetics-header"><a class="brand" href="{home}">Non <span>Dubito</span></a><nav aria-label="{esc(u[5])}"><a href="{rel(path,ROOT/'library.html')}?lang={search_lang}">{esc(u[5])}</a><a href="{search_url}">{esc(u[6])}</a></nav><details class="language-menu"><summary>{label} <span aria-hidden="true">⌄</span></summary><nav aria-label="Language">{switch}</nav></details></header>
<main id="main" class="{'guide-main' if work else 'hub-main'}"><a class="back" href="{back}">← {esc(backlabel)}</a><header class="hero"><p class="kicker">NON DUBITO · {esc(u[1] if work else u[0])}</p><h1>{esc(title)}</h1><p class="deck">{esc(deck)}</p>{f'<p class="byline">Han Qin · <time datetime="{work["date"]}">{work["date"]}</time></p>' if work else ''}</header>{content}<nav class="end-links"><a href="{back}">← {esc(backlabel)}</a><a href="#main">{esc(u[13])}</a></nav></main>
<footer class="aesthetics-footer">Non Dubito · Han Qin</footer><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script></body></html>
'''


def outputs():
    works=json.loads((DATA/'works.json').read_text()); out={}
    for lang in LANGS:
        index=location(lang); cards=[]
        categories=list(dict.fromkeys(w['category'] for w in works))
        # Add localized category names here when the first work in a new medium is ready.
        assert set(categories)<= {'western-painting'}
        for category in categories:
            cards.append(f'<section class="hub-section" id="{category}"><h2>{esc(UI[lang][1])}</h2>')
            for work in [w for w in works if w['category']==category]:
                title=load(work,lang)[0].removeprefix('# '); path=location(lang,work)
                out[path]=page(lang,path,title,work['deck'][lang],article(work,lang,path),work)
                href=rel(index,path)+'?lang='+lang
                cards.append(f'<article class="art-card"><a href="{href}">{image_tag(index,work,work["image"],title,work!=works[0])}</a><div><p class="kicker">{esc(work["artist"])} · {esc(work["year"])}</p><h3><a href="{href}">{esc(title)}</a></h3><p class="deck">{esc(work["deck"][lang])}</p><a href="{href}">{esc(UI[lang][7])}</a><p class="edition-note">简 · 繁 · EN · 日本語 · FR · DE · ES · 한국어</p></div></article>')
            cards.append('</section>')
        out[index]=page(lang,index,UI[lang][0],UI[lang][2],''.join(cards)+bridge(lang,index))
    return out


def prepare_images():
    from PIL import Image
    info={}
    for work in json.loads((DATA/'works.json').read_text()):
        for path in sorted((TARGET/'images'/work['id']).iterdir()):
            if path.suffix not in ('.jpg','.png'): continue
            with Image.open(path) as im:
                info[work['id']+'/'+path.name]=list(im.size)
                for width in (640,1280):
                    copy=im.copy(); copy.thumbnail((width,10000),Image.Resampling.LANCZOS)
                    copy.save(path.with_name(path.stem+f'-{width}.webp'),format='WEBP',quality=88,icc_profile=im.info.get('icc_profile',b''))
    (DATA/'images.json').write_text(json.dumps(info,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); parser.add_argument('--images',action='store_true'); args=parser.parse_args()
    if args.images: prepare_images()
    pages=outputs()
    for path, content in pages.items():
        if args.check: assert path.exists() and path.read_text()==content, path
        else: path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content)
    print(f'OK: {len(pages)} art pages in eight editions')


if __name__=='__main__': main()
