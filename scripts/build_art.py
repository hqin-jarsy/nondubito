#!/usr/bin/env python3
"""Build the expandable eight-edition art shelf from reviewed manuscripts.

Add published works to data/art/works.json; do not edit generated HTML.
Run --image-work ID --originals-dir /path/to/offline/images --previews-dir
/path/to/upload/art to prepare WebP previews, upload and verify them, then build.
The offline directory contains ID/filename.jpg (or .png). No translation service is used.
"""
import argparse
import html
import hashlib
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
 'zh': ['艺术作品细读','绘画 · 西方绘画','先看作品，再谈它为什么打动我们。从细节、材料与观看经验出发，每篇都可以独立阅读。','美学导读','简体中文、繁体中文与英文','书库','搜索','阅读文章 →','这篇谈什么','前往馆方作品页查看原图 ↗','想了解背后的问题，可以先读本站的美学导读，再按兴趣走向原论文。','参考资料','图像来源与使用说明','回到页首'],
 'zh-hant': ['藝術作品細讀','繪畫 · 西方繪畫','先看作品，再談它為什麼打動我們。從細節、材料與觀看經驗出發，每篇都可以獨立閱讀。','美學導讀','簡體中文、繁體中文與英文','書庫','搜尋','閱讀文章 →','這篇談什麼','前往館方作品頁查看原圖 ↗','想了解背後的問題，可以先讀本站的美學導讀，再按興趣走向原論文。','參考資料','圖像來源與使用說明','回到頁首'],
 'en': ['Looking Closely at Art','Painting · Western painting','Look at the work first. Then ask what moves us. Each essay begins with details, materials and the experience of looking, and can be read on its own.','A guide to aesthetics','English and both Chinese editions','Library','Search','Read the essay →','In this essay','View images on the museum’s artwork page ↗','For the questions behind this reading, start with our accessible guide to aesthetics; the academic papers are further reading.','References','Image credits and usage','Back to top'],
 'ja': ['美術作品をじっくり見る','絵画 · 西洋絵画','まず作品を見て、心を動かされる理由を考える。細部や素材、見る経験から始まる、一篇ずつ読める鑑賞の手引き。','美学の入門エッセイ','英語・簡体字中国語・繁体字中国語','ライブラリ','検索','本文を読む →','この記事の内容','美術館の作品ページで画像を見る ↗','背景にある問いを知りたくなったら、まず当サイトの美学入門へ。原論文は、さらに詳しく読みたい方のために。','参考資料（英語）','画像の出典と利用条件（英語）','ページの先頭へ'],
 'fr': ['Regarder l’art de près','Peinture · Peinture occidentale','Regarder l’œuvre avant de chercher ce qui nous touche. Chaque essai part des détails, des matières et de l’expérience du regard, et peut se lire seul.','Introduction à l’esthétique','En anglais et en chinois simplifié ou traditionnel','Bibliothèque','Rechercher','Lire l’essai →','Dans cet essai','Voir les images sur la page de l’œuvre au musée ↗','Pour explorer les questions derrière cette lecture, commencez par notre introduction à l’esthétique ; les articles théoriques permettent d’aller plus loin.','Références (en anglais)','Crédits et utilisation des images (en anglais)','Haut de page'],
 'de': ['Kunst genau betrachtet','Malerei · Westliche Malerei','Erst das Werk betrachten, dann fragen, was uns berührt. Jeder Essay geht von Einzelheiten, Materialien und der Erfahrung des Sehens aus und lässt sich für sich lesen.','Einführung in die Ästhetik','Auf Englisch und in beiden chinesischen Schriftformen','Bibliothek','Suche','Essay lesen →','In diesem Essay','Bilder auf der Werkseite des Museums ansehen ↗','Wer den Fragen hinter dieser Betrachtung nachgehen möchte, kann mit unserer Einführung in die Ästhetik beginnen. Die wissenschaftlichen Texte führen weiter.','Quellen (auf Englisch)','Bildnachweise und Nutzung (auf Englisch)','Nach oben'],
 'es': ['Mirar el arte de cerca','Pintura · Pintura occidental','Primero mirar la obra; después, preguntarnos qué nos conmueve. Cada ensayo parte de los detalles, los materiales y la experiencia de mirar, y puede leerse por separado.','Introducción a la estética','En inglés y en chino simplificado o tradicional','Biblioteca','Buscar','Leer el ensayo →','En este ensayo','Ver imágenes en la página de la obra del museo ↗','Para explorar las preguntas que hay detrás de esta lectura, empieza por nuestra introducción a la estética; los artículos académicos permiten profundizar.','Referencias (en inglés)','Créditos y uso de imágenes (en inglés)','Volver arriba'],
 'ko': ['미술 작품 자세히 보기','회화 · 서양 회화','먼저 작품을 보고, 무엇이 마음을 움직이는지 묻는다. 세부와 재료, 바라보는 경험에서 출발하며 각 글은 따로 읽어도 좋다.','미학 입문 에세이','영어·중국어 간체·번체 제공','서재','검색','글 읽기 →','이 글의 구성','미술관 작품 페이지에서 이미지 보기 ↗','이 감상 뒤에 놓인 질문이 궁금하다면, 먼저 이 사이트의 미학 입문을 읽어 보자. 원논문은 더 깊이 읽고 싶은 독자를 위한 자료다.','참고 자료 (영어)','이미지 출처와 이용 안내 (영어)','맨 위로']
}


CATEGORIES = {
    'western-painting': {lang: UI[lang][1] for lang in LANGS},
    'western-sculpture': dict(zip(LANGS, [
        '雕塑 · 西方雕塑', '雕塑 · 西方雕塑', 'Sculpture · Western sculpture',
        '彫刻 · 西洋彫刻', 'Sculpture · Sculpture occidentale',
        'Skulptur · Westliche Skulptur', 'Escultura · Escultura occidental', '조각 · 서양 조각'
    ])),
}

# The museum page is more stable than an image CDN URL. Hosted detail crops and
# alternate views remain available as WebP; originals are kept in offline archives.
IMAGE_LINK_LABELS = dict(zip(LANGS, [
    '前往馆方作品页查看原图 ↗', '前往館方作品頁查看原圖 ↗',
    'View images on the museum’s artwork page ↗', '美術館の作品ページで画像を見る ↗',
    'Voir les images sur la page de l’œuvre au musée ↗',
    'Bilder auf der Werkseite des Museums ansehen ↗',
    'Ver imágenes en la página de la obra del museo ↗', '미술관 작품 페이지에서 이미지 보기 ↗',
]))
IMAGE_STORAGE_NOTES = dict(zip(LANGS, [
    '本站保留适合阅读的 WebP 配图，包括局部与不同角度。点击配图可前往馆方作品页；完整原图不再随网站发布。以下尺寸、文件名、裁切坐标与校验值为原始素材的存档记录，并非网页预览图的规格。',
    '本站保留適合閱讀的 WebP 配圖，包括局部與不同角度。點擊配圖可前往館方作品頁；完整原圖不再隨網站發布。以下尺寸、檔名、裁切座標與校驗值為原始素材的存檔記錄，並非網頁預覽圖的規格。',
    'The site retains reading-size WebP images, including details and alternate views. Clicking an image opens the museum’s artwork page; full-resolution originals are not hosted here. The dimensions, filenames, crop coordinates and hashes below describe the archived source files, not the web previews.',
    '本サイトでは、細部や別角度の写真も含め、閲覧用の WebP 画像を掲載しています。画像をクリックすると美術館の作品ページが開きます。原寸の元画像は本サイトでは配信していません。以下の寸法、ファイル名、切り抜き座標、ハッシュ値は元資料の保存記録であり、表示画像の仕様ではありません。',
    'Le site conserve des images WebP adaptées à la lecture, y compris les détails et les autres vues. Un clic ouvre la page de l’œuvre au musée ; les originaux en pleine résolution ne sont pas hébergés ici. Les dimensions, noms de fichiers, coordonnées de recadrage et empreintes ci-dessous décrivent les sources archivées, non les aperçus web.',
    'Die Website enthält WebP-Bilder in einer für die Lektüre geeigneten Größe, auch Details und weitere Ansichten. Ein Klick öffnet die Werkseite des Museums; die Originaldateien in voller Auflösung werden hier nicht bereitgestellt. Maße, Dateinamen, Ausschnittkoordinaten und Prüfsummen unten dokumentieren die archivierten Quelldateien, nicht die Webvorschaubilder.',
    'El sitio conserva imágenes WebP adecuadas para la lectura, incluidos detalles y otras vistas. Al pulsarlas se abre la página de la obra del museo; los originales a resolución completa no se alojan aquí. Las dimensiones, nombres de archivo, coordenadas de recorte y hashes que figuran abajo corresponden a las fuentes archivadas, no a las vistas web.',
    '이 사이트에는 세부와 다른 각도를 포함해 읽기에 적합한 크기의 WebP 이미지를 제공합니다. 이미지를 누르면 미술관 작품 페이지로 이동하며, 전체 해상도 원본은 이 사이트에서 제공하지 않습니다. 아래 크기, 파일명, 자르기 좌표와 해시는 보관된 원본 자료의 기록으로, 웹 미리보기의 사양이 아닙니다.',
]))


def preview_filename(work, name, width=1280):
    return work['id']+'--'+Path(name).stem+f'-{width}.webp'


def preview_url(work, name, width=1280):
    hosting=json.loads((DATA/'image-hosting.json').read_text())
    return hosting['base_url'].rstrip('/')+'/'+hosting['prefix'].strip('/')+'/'+preview_filename(work,name,width)


def preview_record(original, work, previews_dir):
    """Record source provenance and the exact lightweight files being published."""
    from PIL import Image
    with Image.open(original) as im:
        size = list(im.size)
    previews = {}
    for width in (640, 1280):
        path = Path(previews_dir)/preview_filename(work, original.name, width)
        with Image.open(path) as im:
            dimensions = list(im.size)
        previews[str(width)] = dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                   bytes=path.stat().st_size, dimensions=dimensions)
    return dict(original_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                original_bytes=original.stat().st_size, dimensions=size, previews=previews)


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


def plain_title(work, lang):
    return load(work, lang)[0].removeprefix('# ').replace('*', '')


def inline(text, local_links=None):
    """Escaped prose plus the reviewed Markdown's links and emphasis."""
    parts = re.split(r'(\[[^\]]+\]\([^\s)]+\))', text)
    result = []
    for part in parts:
        match = re.fullmatch(r'\[([^\]]+)\]\(([^\s)]+)\)', part)
        if match:
            label, url = match.groups()
            url = {'REFERENCES.md':'#references','IMAGE_CREDITS.md':'#image-credits','IMAGE_LINKS.md':'#image-credits'}.get(url,url)
            if local_links and url in local_links:
                url=local_links[url]
            else:
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
    src=preview_url(work,name,640)
    larger=preview_url(work,name,1280)
    candidates=f'{src} {min(640,info[0])}w'
    if info[0]>640: candidates+=f', {larger} {min(1280,info[0])}w'
    return f'<img src="{src}" srcset="{candidates}" sizes="(max-width: 600px) calc(100vw - 46px), 760px" width="{info[0]}" height="{info[1]}" alt="{esc(alt)}" loading="{"lazy" if lazy else "eager"}" decoding="async">'


def documents(work, lang):
    blocks=[]
    image_doc='IMAGE_CREDITS.md' if work.get('image') else 'IMAGE_LINKS.md'
    for filename, anchor, label in [('REFERENCES.md','references',UI[lang][11]),(image_doc,'image-credits',UI[lang][12])]:
        source=(DATA/work['id']/'source'/filename).read_text()
        if work.get('restored_images'):
            # Keep package delivery instructions in the archive, not on the reader's page.
            source='\n\n'.join(block for block in source.split('\n\n') if not block.startswith(('R1文字更新说明：','Text-update R1:')))
        marker='## English'
        bilingual = marker not in source
        if not bilingual:
            source = source.split(marker)[0] if lang in ('zh','zh-hant') else marker+source.split(marker,1)[1]
        elif lang not in ('zh','zh-hant'):
            # Later source dossiers interleave Chinese and English rather than
            # providing two separate sections. Label them honestly; keep both.
            label = label.split(' (')[0].split('（')[0] + ' · 中文 / English'
        rendered=[]
        if filename=='IMAGE_CREDITS.md':
            rendered.append('<p lang="'+LANGS[lang][0]+'">'+esc(IMAGE_STORAGE_NOTES[lang])+'</p>')
        for block in source.strip().split('\n\n'):
            if block.startswith('#'):
                rendered.append('<h3>'+esc(block.lstrip('# '))+'</h3>')
            else:
                local_links={p.name:rel(location(lang,work),p) for p in (DATA/work['id']/'source').iterdir() if p.is_file()}
                rendered.append('<p>'+inline(block,local_links).replace('\n','<br>')+'</p>')
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
                if n==optional+1 and work.get('archival_image_note'):
                    body.append('<aside class="image-publication-note">'+esc(IMAGE_STORAGE_NOTES[lang])+'</aside>')
        elif b.startswith('### '):
            body.append('<h3>'+esc(b[4:])+'</h3>')
        elif b.startswith('!['):
            m=re.fullmatch(r'!\[([^\]]*)\]\(images/([^)]+)\)',b); assert m,b
            alt,name=m.groups(); caption=blocks[i+1]; assert not caption.startswith(('#','!'))
            body.append(f'<figure><a href="{esc(work["about"])}" target="_blank" rel="noopener noreferrer" aria-label="{esc(IMAGE_LINK_LABELS[lang])}">{image_tag(path,work,name,alt,name!=work["image"])}</a><figcaption>{inline(caption)}<a class="image-hint" href="{esc(work["about"])}" target="_blank" rel="noopener noreferrer">{esc(IMAGE_LINK_LABELS[lang])}</a></figcaption></figure>')
            i+=1
        else: body.append('<p>'+inline(b)+'</p>')
        i+=1
    assert n==heading_count
    toc='<details class="contents"><summary>'+esc(UI[lang][8])+'</summary><nav>'+''.join(f'<a href="#{a}">{esc(h)}</a>' for a,h in headings)+'</nav></details>'
    viewing=''
    if not work.get('image'):
        viewing=f'<aside class="art-viewing"><a href="{esc(work["about"])}" target="_blank" rel="noopener noreferrer">{esc(IMAGE_LINK_LABELS[lang])}</a></aside>'
    return viewing+toc+'<article class="prose">'+''.join(body)+'</article>'+documents(work,lang)


def page(lang, path, title, deck, content, work=None):
    code, directory, label=LANGS[lang]; u=UI[lang]; url=canonical(path)
    alternates=''.join(f'<link rel="alternate" hreflang="{c}" href="{canonical(location(k,work))}">' for k,(c,_,_) in LANGS.items())
    alternates+=f'<link rel="alternate" hreflang="x-default" href="{canonical(location("zh",work))}">'
    switch=''.join(f'<a href="{rel(path,location(k,work))}?lang={k}" lang="{c}" data-edition="{k}"'+(' aria-current="page"' if k==lang else '')+f'>{esc(name)}</a>' for k,(c,_,name) in LANGS.items())
    schema={'@context':'https://schema.org','@type':'Article' if work else 'CollectionPage','name':title,'description':deck,'url':url,'inLanguage':code,'isPartOf':{'@type':'WebSite','name':'Non Dubito','url':ORIGIN}}
    if work:
        schema.update(headline=title,datePublished=work['date'],dateModified=work['date'],author={'@type':'Person','name':'Han Qin'})
        if work.get('image'): schema['image']=preview_url(work,work['image'])
        schema['about']={'@type':work['schema_type'],'name':work['work_name'],'creator':{'@type':'Person','name':work['artist']},'sameAs':work['about']}
    search_lang=lang if lang in ('zh','en','zh-hant') else 'en'
    home=rel(path,ROOT/'index.html')+'?lang='+search_lang
    if lang in ('ja','fr','de','es','ko'):
        home=rel(path,ROOT/f'essays/{lang}/index.html')
    search_url=rel(path,ROOT/'search.html')+'?lang='+search_lang+'&amp;in='+code
    if lang in ('ja','fr','de','es','ko'): search_url+='&amp;ui='+lang
    back=rel(path,location(lang))+'?lang='+lang+'#'+work['category'] if work else guide(lang,path)
    backlabel=u[0] if work else u[3]+(' · '+u[4] if lang not in ('zh','zh-hant','en') else '')
    heroimage=f'<meta property="og:image" content="{schema["image"]}">' if 'image' in schema else ''
    return f'''<!doctype html>
<html lang="{code}" data-lang="{lang}" data-editions="{code}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(deck)}"><meta name="author" content="Han Qin (秦汉)">
<link rel="canonical" href="{url}">{alternates}<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(deck)}"><meta property="og:type" content="{'article' if work else 'website'}"><meta property="og:url" content="{url}">{heroimage}<meta name="twitter:card" content="{'summary_large_image' if heroimage else 'summary'}">
<link rel="icon" href="{rel(path,ROOT/'favicon.svg')}"><link rel="stylesheet" href="{rel(path,ROOT/'essays/aesthetics/aesthetics-hub.css')}"><link rel="stylesheet" href="{rel(path,TARGET/'art.css')}">
<script defer src="{rel(path,ROOT/'essays/aesthetics/aesthetics-hub.js')}"></script><script defer src="{rel(path,TARGET/'art.js')}"></script>
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('<',chr(92)+'u003c')}</script></head>
<body class="aesthetics-site art-page"><a class="skip" href="#main">↓ {esc(title)}</a>
<header class="aesthetics-header"><a class="brand" href="{home}">Non <span>Dubito</span></a><nav aria-label="{esc(u[5])}"><a href="{rel(path,ROOT/'library.html')}?lang={search_lang}">{esc(u[5])}</a><a href="{search_url}">{esc(u[6])}</a></nav><details class="language-menu"><summary>{label} <span aria-hidden="true">⌄</span></summary><nav aria-label="Language">{switch}</nav></details></header>
<main id="main" class="{'guide-main' if work else 'hub-main'}"><a class="back" href="{back}">← {esc(backlabel)}</a><header class="hero"><p class="kicker">NON DUBITO · {esc(CATEGORIES[work['category']][lang] if work else u[0])}</p><h1>{esc(title)}</h1><p class="deck">{esc(deck)}</p>{f'<p class="byline">Han Qin · <time datetime="{work["date"]}">{work["date"]}</time></p>' if work else ''}</header>{content}<nav class="end-links"><a href="{back}">← {esc(backlabel)}</a><a href="#main">{esc(u[13])}</a></nav></main>
<footer class="aesthetics-footer">Non Dubito · Han Qin</footer><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script></body></html>
'''


def outputs():
    works=json.loads((DATA/'works.json').read_text()); out={}
    for lang in LANGS:
        index=location(lang); cards=[]
        categories=list(dict.fromkeys(w['category'] for w in works))
        assert set(categories) <= CATEGORIES.keys()
        cards.append('<nav class="jump" aria-label="'+esc(UI[lang][0])+'">'+''.join(
            f'<a href="#{category}">{esc(CATEGORIES[category][lang])}</a>' for category in categories
        )+'</nav>')
        for category in categories:
            cards.append(f'<section class="hub-section" id="{category}"><h2>{esc(CATEGORIES[category][lang])}</h2>')
            for work in [w for w in works if w['category']==category]:
                title=plain_title(work,lang); path=location(lang,work)
                out[path]=page(lang,path,title,work['deck'][lang],article(work,lang,path),work)
                href=rel(index,path)+'?lang='+lang
                thumbnail=f'<a href="{href}">{image_tag(index,work,work["image"],title,work!=works[0])}</a>' if work.get('image') else ''
                viewing='' if thumbnail else f'<p class="image-hint"><a href="{esc(work["about"])}" target="_blank" rel="noopener noreferrer">{esc(IMAGE_LINK_LABELS[lang])}</a></p>'
                cardclass='art-card' if thumbnail else 'art-card art-card-text'
                cards.append(f'<article class="{cardclass}">{thumbnail}<div><p class="kicker">{esc(work["artist"])} · {esc(work["year"])}</p><h3><a href="{href}">{esc(title)}</a></h3><p class="deck">{esc(work["deck"][lang])}</p><a href="{href}">{esc(UI[lang][7])}</a>{viewing}<p class="edition-note">简 · 繁 · EN · 日本語 · FR · DE · ES · 한국어</p></div></article>')
            cards.append('</section>')
        out[index]=page(lang,index,UI[lang][0],UI[lang][2],''.join(cards)+bridge(lang,index))
    return out


def prepare_images(only=None, originals_dir=None, previews_dir=None):
    from PIL import Image
    if originals_dir is None:
        raise ValueError('Supply --originals-dir with the offline archive directory (containing work-ID folders).')
    info=json.loads((DATA/'images.json').read_text())
    ledger_path=DATA/'web-images.json'
    ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    selected=[w for w in json.loads((DATA/'works.json').read_text()) if not only or w['id']==only]
    inputs=[]
    # Validate every input before writing, so a missing archive cannot erase metadata.
    for work in selected:
        names={re.fullmatch(r'!\[[^\]]*\]\(images/([^)]+)\)', b)[1]
               for lang in LANGS for b in load(work,lang) if b.startswith('![')}
        sums=DATA/work['id']/'source/SHA256SUMS.txt'
        if sums.exists():
            names.update(line.split(maxsplit=1)[1].removeprefix('images/') for line in sums.read_text().splitlines()
                         if line.split(maxsplit=1)[1].startswith('images/'))
        for name in sorted(names):
            path=Path(originals_dir)/work['id']/name
            if not path.is_file(): raise FileNotFoundError(path)
            inputs.append((work,path))
    if previews_dir is None:
        raise ValueError('Supply --previews-dir outside the repository; upload previews to R2 before publishing.')
    previews_dir=Path(previews_dir).resolve()
    if previews_dir.is_relative_to(ROOT):
        raise ValueError('The preview upload directory must be outside the repository.')
    previews_dir.mkdir(parents=True,exist_ok=True)
    for work,path in inputs:
        with Image.open(path) as im:
            info[work['id']+'/'+path.name]=list(im.size)
            for width in (640,1280):
                copy=im.copy(); copy.thumbnail((width,10000),Image.Resampling.LANCZOS)
                copy.save(previews_dir/preview_filename(work,path.name,width),format='WEBP',quality=88,icc_profile=im.info.get('icc_profile',b''))
        ledger[work['id']+'/'+path.name]=preview_record(path,work,previews_dir)
    (DATA/'images.json').write_text(json.dumps(info,indent=2)+'\n')
    ledger_path.write_text(json.dumps(ledger,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); parser.add_argument('--images',action='store_true'); parser.add_argument('--image-work',help='Generate previews only for this work ID'); parser.add_argument('--originals-dir',type=Path,help='Offline originals directory, containing work-ID folders'); parser.add_argument('--previews-dir',type=Path,help='Outside-repository upload directory for R2 art/ objects'); parser.add_argument('--prepare-only',action='store_true',help='Prepare images and metadata without rebuilding HTML'); args=parser.parse_args()
    if args.prepare_only and not (args.images or args.image_work): parser.error('--prepare-only requires --images or --image-work')
    if args.image_work:
        assert args.image_work in {w['id'] for w in json.loads((DATA/'works.json').read_text())}, args.image_work
    if args.images or args.image_work: prepare_images(args.image_work,args.originals_dir,args.previews_dir)
    if args.prepare_only:
        print('Previews prepared. Upload to R2 art/ and run verify_art_images.py before building pages.')
        return
    pages=outputs()
    for path, content in pages.items():
        if args.check: assert path.exists() and path.read_text()==content, path
        else: path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content)
    print(f'OK: {len(pages)} art pages in eight editions')


if __name__=='__main__': main()
