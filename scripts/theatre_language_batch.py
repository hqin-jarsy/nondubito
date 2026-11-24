"""Native editions of the three November 2026 theatre essays; retain the earlier shelves."""
import html
import json
import re
from pathlib import Path

from don_literary_render import page, ui, routes
from build_recent_fiction import prose
from web_analytics import ensure_analytics

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'essays/theatre'
SITE = 'https://nondubito.net/'
PRIOR_DATE = '2026-11-22'
DATE = '2026-11-24'
PRIOR_SLUGS = ('billy-elliot','the-great-comet','the-color-purple')
SLUGS = ('the-last-five-years','passion','ragtime')
ALL_SLUGS = PRIOR_SLUGS + SLUGS
NATIVE_DECKS = {
    'ja': ('結婚を反対向きの時間から語る二人。二人の時間が重なるのは結婚式だけだ。','後に生まれた本物の愛は、それ以前に相手へかけた圧力をどう変えるのか。','壊された車を直してほしいという要求から、尊厳と不公正、巻き込まれた人々が見えてくる。'),
    'fr': ('Deux voix traversent leur mariage en sens inverse. Leurs récits ne se rejoignent qu’au mariage.','Un amour devenu réel par la suite règle-t-il la question des pressions qui l’ont précédé ?','Une demande de réparation pour une voiture endommagée met en jeu la dignité, l’injustice et la vie des autres.'),
    'de': ('Zwei Stimmen erzählen eine Ehe in entgegengesetzter Zeitrichtung. An der Hochzeit begegnen sie sich.','Kann eine später erwiderte Liebe den Druck rechtfertigen, der ihr vorausging?','Aus der Forderung, ein Auto wieder instand zu setzen, wird ein Konflikt um Würde, Unrecht und das Leben anderer.'),
    'es': ('Dos voces recorren un matrimonio en direcciones opuestas y solo coinciden en la boda.','¿Un amor que llega a ser correspondido resuelve lo que ocurrió antes, cuando una persona presionaba a la otra?','La exigencia de reparar un coche abre una disputa sobre la dignidad, la injusticia y la vida de otras personas.'),
    'ko': ('두 사람이 결혼 생활을 서로 반대 방향에서 이야기한다. 두 시간이 겹치는 곳은 결혼식뿐이다.','뒤에 찾아온 진실한 사랑은 그전에 상대에게 가했던 압박까지 정당화할 수 있을까?','망가진 자동차를 고쳐 달라는 요구에서 존엄과 부당함, 그 일에 휘말린 사람들의 삶이 드러난다.'),
}
LANGUAGES = ('ja','fr','de','es','ko')
E = html.escape
CATALOG = {
'ja': ('演劇とミュージカル','舞台の物語を読み解く二十六篇を八言語で。残る九篇は中国語の簡体字版・繁体字版で読めます。','26篇 · 8言語','作品について','資料にもとづく舞台作品の紹介と分析。実際に観劇したり、全編の映像を見たりしたうえでの公演評ではありません。歌詞の引用はありません。',
       ('ある子を支えることを学んでいく炭鉱町。その子は踊りを望み、いつか町を出ていくかもしれない。','ナターシャは大きな過ちを犯す。友人たちは彼女を止めなければならないが、その一度の過ちで彼女の人生が決まるわけではない。','手紙と愛と服を仕立てる仕事。生き延びた先で、セリーが自分の暮らしを選ぶ道が少しずつ開く。')),
'fr': ('Théâtre et comédies musicales','Vingt-six essais sur la scène, disponibles en huit langues. Neuf autres sont à lire en chinois simplifié et traditionnel.','26 essais · 8 langues','À propos de cet essai','Une présentation et une analyse de l’œuvre à partir de la documentation disponible, et non le compte rendu d’une représentation vue sur place ou en intégralité. Les paroles des chansons ne sont pas reproduites.',
       ('Une communauté minière apprend à soutenir un enfant dont l’envie de danser pourrait l’emmener loin d’elle.','Natacha se trompe gravement. Ses amis doivent intervenir, sans réduire sa vie à cette seule erreur.','Les lettres, l’amour et la couture ouvrent à Celie de nouveaux choix, bien après qu’elle a appris à survivre.')),
'de': ('Theater und Musicals','Sechsundzwanzig Essays zu Bühnenwerken in acht Sprachen. Neun weitere gibt es auf Chinesisch, in Kurz- und Langzeichen.','26 Essays · 8 Sprachen','Über diesen Essay','Diese Einführung und Analyse stützt sich auf die vorliegenden Materialien zum Bühnenwerk. Sie ist keine Kritik aus eigener Anschauung oder nach Sichtung einer vollständigen Aufzeichnung. Liedtexte werden nicht wiedergegeben.',
       ('Eine Bergbaugemeinde lernt, ein Kind zu unterstützen, dessen Wunsch zu tanzen es von dort fortführen könnte.','Natascha begeht einen schweren Fehler. Ihre Freunde müssen eingreifen, ohne ihr ganzes Leben auf diesen Fehler zu reduzieren.','Briefe, Liebe und das Nähen eröffnen Celie nach dem Überleben nach und nach eigene Entscheidungen.')),
'es': ('Teatro y musicales','Veintiséis ensayos sobre obras escénicas en ocho idiomas. Otros nueve están disponibles en chino simplificado y tradicional.','26 ensayos · 8 idiomas','Acerca de este ensayo','Presentación y análisis de la obra escénica a partir de la documentación disponible. No es la reseña de una función vista en persona ni de una grabación completa. No se reproducen letras de canciones.',
       ('Una comunidad minera aprende a apoyar a un niño cuyo deseo de bailar quizá lo lleve lejos de allí.','Natasha comete un error grave. Sus amigos tienen que intervenir sin reducir toda su vida a ese error.','Las cartas, el amor y el oficio de coser abren para Celie nuevas posibilidades de elegir cómo vivir después de haber sobrevivido.')),
'ko': ('연극과 뮤지컬 읽기','무대 작품을 읽는 스물여섯 편에는 여덟 언어판이 있습니다. 나머지 아홉 편은 중국어 간체와 번체로 읽을 수 있습니다.','글 26편 · 8개 언어','이 글에 대하여','공개 자료에 근거한 무대 작품 소개와 분석이다. 현장에서 관람하거나 전체 영상을 본 뒤 쓴 공연평은 아니다. 노래 가사는 인용하지 않았다.',
       ('광산 마을 사람들은 춤을 추고 싶어 하는 아이를 응원하는 법을 배운다. 춤은 그 아이를 마을 밖으로 이끌 수도 있다.','나타샤는 큰 잘못을 저지른다. 친구들은 나서서 막아야 하지만, 한 번의 잘못으로 그의 삶 전체를 판단할 수는 없다.','편지와 사랑, 옷을 만드는 일이 셀리에게 살아남은 뒤의 삶을 스스로 고를 길을 조금씩 열어 준다.')),
}
START = '<!-- THEATRE 2026-11-22 EDITIONS START -->'
END = '<!-- THEATRE 2026-11-22 EDITIONS END -->'


def alternatives(filename):
    return '<link rel="alternate" hreflang="x-default" href="' + SITE + DIRECTORY + '/' + filename.removesuffix('index.html') + '">' + ''.join(
        f'<link rel="alternate" hreflang="{ {"zh":"zh-Hans","zh-hant":"zh-Hant"}.get(lang,lang) }" href="{url}">'
        for lang, url in routes(DIRECTORY, filename.removesuffix('.html'), absolute=True).items())


def switch_links(text, filename):
    text = re.sub(r'<link rel="alternate"[^>]*>\n?', '', text)
    return text.replace('</head>', alternatives(filename) + '</head>', 1)


def deck_for(lang, slug):
    return (CATALOG[lang][5][PRIOR_SLUGS.index(slug)] if slug in PRIOR_SLUGS
            else NATIVE_DECKS[lang][SLUGS.index(slug)])


def localized_article(lang, work, neighboring, load):
    slug = work['slug']
    title, warning, body = load(lang, slug)
    copy = CATALOG[lang]
    deck = deck_for(lang, slug)
    source = f'<aside class="edition-note"><h2>{E(copy[3])}</h2><p>{E(copy[4])}</p></aside>'
    prev, nxt = neighboring
    nav = '<div class="essay-nav">'
    if prev:
        nav += f'<a href="{prev["slug"]}.html">← {E(ui[lang][1])}: {E(load(lang,prev["slug"])[0])}</a>'
    else:
        nav += f'<a href="index.html">← {E(ui[lang][0])}</a>'
    if nxt:
        nav += f'<a href="{nxt["slug"]}.html">{E(ui[lang][2])}: {E(load(lang,nxt["slug"])[0])} →</a>'
    else:
        nav += f'<a href="index.html">{E(ui[lang][0])} →</a>'
    nav += '</div>'
    release = f'<p style="font-size:.8rem;color:var(--ink-muted)"><time datetime="{work["published"]}">{work["published"]}</time></p>'
    contents = page(DIRECTORY,lang,slug,title,deck,copy[0],release+prose(body)+source,nav,note=warning)
    contents = switch_links(contents, slug+'.html')
    canonical = SITE+f'{DIRECTORY}/{lang}/{slug}.html'
    schema = {"@context":"https://schema.org","@type":"Article","url":canonical,"mainEntityOfPage":canonical,
              "headline":title,"description":deck,"inLanguage":lang,
              "author":{"@type":"Person","name":"Han Qin (秦汉)"},"datePublished":work['published'],
              "dateModified":work['editions_added'],"translationOfWork":{"@type":"Article","url":SITE+f'{DIRECTORY}/{slug}.html'},
              "about":{"@type":"CreativeWork","name":work['name'],"genre":"Musical theatre",
                       "creator":[{"@type":"Person","name":p} for p in work['creators']]},
              "isPartOf":{"@type":"CollectionPage","name":copy[0],"url":SITE+f'{DIRECTORY}/{lang}/index.html'}}
    return contents.replace('</head>','<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script></head>',1)


def localized_shelf(path, lang, works, load):
    before = path.read_text()
    title, deck, count, *_ = CATALOG[lang]
    before = re.sub(re.escape(START)+r'.*?'+re.escape(END),'',before,flags=re.S)
    before, n = re.subn(r'(<div class="essay-page-num">).*?(</div>)',lambda m:m[1]+E(count)+m[2],before,count=1,flags=re.S)
    assert n == 1
    for selector in ('name="description"', 'property="og:description"'):
        before, n = re.subn(r'(<meta '+selector+r' content=")[^"]*(")',lambda m:m[1]+E(deck)+m[2],before,count=1)
        assert n == 1
    before = before.replace('<meta property="og:type" content="article">','<meta property="og:type" content="website">',1)
    before, n = re.subn(r'(<div class="essay-body"><p>).*?(</p>)',lambda m:m[1]+E(deck)+m[2],before,count=1,flags=re.S)
    assert n == 1
    cards = ''.join(
        f'<a class="essay-card" href="{w["slug"]}.html"><span class="card-num">{i}</span>'
        f'<div class="card-body"><h2>{E(load(lang, w["slug"])[0])}</h2><p class="card-desc">{E(deck_for(lang, w["slug"]))}</p></div></a>'
        for i,w in enumerate(works,21))
    assert before.count('</div></div></main>') == 1
    before = re.sub(r'<script type="application/ld\+json">.*?</script>', '', before, flags=re.S)
    canonical = SITE+f'{DIRECTORY}/{lang}/index.html'
    schema = {"@context":"https://schema.org","@type":"CollectionPage","name":title,"description":deck,
              "inLanguage":lang,"url":canonical,"datePublished":"2026-10-13","dateModified":DATE}
    before = before.replace('</head>','<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script></head>',1)
    return switch_links(before.replace('</div></div></main>', START+cards+END+'</div></div></main>',1),'index.html')


def outputs(works, load):
    batch = [w for w in works if w.get('editions_added') == DATE]
    assert [w['slug'] for w in batch] == list(SLUGS), 'incomplete theatre language release'
    prior = [w for w in works if w.get('editions_added') == PRIOR_DATE]
    assert [w['slug'] for w in prior] == list(PRIOR_SLUGS)
    pages = {}
    for lang in LANGUAGES:
        dest = ROOT / DIRECTORY / lang
        for group in (prior, batch):
            for i, work in enumerate(group):
                neighbors = (group[i-1] if i else None, group[i+1] if i+1 < len(group) else None)
                pages[dest / (work['slug'] + '.html')] = localized_article(lang,work,neighbors,load)
        pages[dest/'index.html'] = localized_shelf(dest/'index.html',lang,prior+batch,load)
    return pages
