#!/usr/bin/env python3
"""Build the Japanese, French, German, Spanish, and Korean Analects editions.

The JSON files under ``data/analects-languages`` are edited reader-facing
rewrites.  This script only assembles pages, navigation, language alternates,
and the five language-channel cards.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from import_analects_series import ITEMS, MOVEMENTS, RESEARCH, serialize_updates


ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "essays" / "analects"
DATA = ROOT / "data" / "analects-languages"
LANGS = ("ja", "fr", "de", "es", "ko")
HTML_LANG = {"ja": "ja", "fr": "fr", "de": "de", "es": "es", "ko": "ko"}
LANG_LABEL = {
    "en": "English", "zh": "中文", "zh-hant": "繁體中文", "ja": "日本語",
    "fr": "Français", "de": "Deutsch", "es": "Español", "ko": "한국어",
}

UI = {
    "ja": {
        "title": "『論語』をひらき直す",
        "subtitle": "「子曰」の前に、名と場面を戻す五十篇。",
        "manifesto": "これは孔子を聖人の座から引きずり下ろす本でも、もう一度そこへ戻す本でもない。誰が問い、誰に答え、どこで言い直し、いつ黙ったのか。名と場面を戻すことで、格言集の奥にいた一人の教師に会い直す。",
        "method_title": "この読み方について",
        "method": "文献学や成立史に最終判決を下す試みではない。人物、場面、応答を戻したとき、どのような教師が見えてくるかを問う、一つの構造的な読解である。",
        "route_title": "まず読む八篇",
        "route_desc": "教えること、権威、誤読、反論、そして記録の限界をたどる短い入口。",
        "research_title": "理論的な底本",
        "research_desc": "五本のSAE論文に詳細な論証を収めた。ここまでの五十篇は一般読者のための独立した再構成であり、論文を先に読む必要はない。",
        "read": "読む", "essay": "第{number}篇・全50篇", "previous": "← 前の篇", "next": "次の篇 →",
        "back": "『論語』をひらき直す", "door": "この篇は全五十篇の再構成の一部です。四部構成の目次へ戻ることも、次の篇へ進むこともできます。",
        "source": "中国語・英語版を基に、日本語の読者に向けて独立に書き直したエッセイ。詳細な論証はシリーズ末尾の研究版を参照。",
        "nav": ("はじめに", "探す", "新着", "このサイトについて", "検索", "メニュー", "全ライブラリー"),
        "channel_tag": "旗艦シリーズ · 全50篇 · 日本語独立再構成版",
        "channel_desc": "「子曰」の前に名と場面を戻し、格言集の奥にいた教師へ会い直す。教え方、誤読、異論、弟子、記録の限界をたどる五十篇。",
    },
    "fr": {
        "title": "Les Entretiens, rouverts",
        "subtitle": "Cinquante rencontres avec Confucius, en remettant les noms avant « Le Maître dit ».",
        "manifesto": "Il ne s’agit ni de déboulonner un sage ni de le replacer sur son socle. Qui pose la question ? À qui répond-il ? Quand se corrige-t-il, quand se tait-il ? En rendant aux phrases leurs noms et leurs scènes, on retrouve derrière le recueil de maximes un professeur parmi ses élèves.",
        "method_title": "À propos de cette lecture",
        "method": "Cette lecture ne prétend pas trancher la philologie ni l’histoire du texte. Elle pose une question plus étroite : quel maître apparaît lorsque l’on restitue les personnes, les circonstances et le mouvement des réponses ?",
        "route_title": "Huit portes d’entrée",
        "route_desc": "Un parcours bref à travers l’enseignement, l’autorité, les contresens, le désaccord et les limites du livre.",
        "research_title": "Édition de recherche",
        "research_desc": "Cinq articles SAE développent l’argument complet. Les cinquante essais constituent une réécriture autonome pour le grand public ; nul besoin de commencer par les articles académiques.",
        "read": "Lire", "essay": "Essai {number} sur 50", "previous": "← Essai précédent", "next": "Essai suivant →",
        "back": "Les Entretiens, rouverts", "door": "Cet essai appartient à une reconstruction en cinquante textes. Revenez aux quatre mouvements ou poursuivez vers l’essai suivant.",
        "source": "Réécriture française indépendante à partir des éditions chinoise et anglaise. L’argument détaillé figure dans l’édition de recherche présentée à la fin de la série.",
        "nav": ("Commencer", "Explorer", "Nouveautés", "À propos", "Rechercher", "Menu", "Bibliothèque"),
        "channel_tag": "Série phare · 50 essais · Réécriture française",
        "channel_desc": "Remettre les noms et les scènes avant « Le Maître dit » pour retrouver un professeur derrière le recueil de maximes : cinquante essais sur sa manière d’enseigner, ses lecteurs et les limites du livre.",
    },
    "de": {
        "title": "Die Gespräche des Konfuzius neu gelesen",
        "subtitle": "Fünfzig Begegnungen mit Konfuzius – die Namen kehren vor „Der Meister sprach“ zurück.",
        "manifesto": "Hier wird weder ein Heiliger vom Sockel gestoßen noch wieder hinaufgestellt. Wer fragt? Wem antwortet Konfuzius? Wann nimmt er etwas zurück, wann schweigt er? Sobald Namen und Situationen zurückkehren, erscheint hinter der Spruchsammlung ein Lehrer unter seinen Schülern.",
        "method_title": "Zu dieser Lektüre",
        "method": "Diese strukturelle Lesart beansprucht kein letztes Urteil über Philologie oder Textgeschichte. Sie fragt enger: Was für ein Lehrer wird sichtbar, wenn Personen, Anlässe und der Verlauf einer Antwort wieder an ihren Platz kommen?",
        "route_title": "Acht Einstiege",
        "route_desc": "Ein kurzer Weg durch Lehren, Autorität, Fehllektüre, Widerspruch und die Grenzen der Aufzeichnung.",
        "research_title": "Forschungsgrundlage",
        "research_desc": "Fünf SAE-Aufsätze führen das Argument vollständig aus. Die fünfzig Essays sind eine eigenständige Fassung für ein breites Publikum; die Fachtexte sind keine Voraussetzung.",
        "read": "Lesen", "essay": "Essay {number} von 50", "previous": "← Voriger Essay", "next": "Nächster Essay →",
        "back": "Die Gespräche des Konfuzius neu gelesen", "door": "Dieser Essay gehört zu einer Rekonstruktion in fünfzig Teilen. Zurück zu den vier Bewegungen oder weiter zum nächsten Text.",
        "source": "Eigenständige deutsche Neufassung auf Grundlage der chinesischen und englischen Edition. Die ausführliche Argumentation steht in der Forschungsedition am Ende der Reihe.",
        "nav": ("Einstieg", "Entdecken", "Neu", "Über uns", "Suchen", "Menü", "Bibliothek"),
        "channel_tag": "Flaggschiff · 50 Essays · Deutsche Neufassung",
        "channel_desc": "Namen und Situationen kehren vor „Der Meister sprach“ zurück. Fünfzig Essays begegnen dem Lehrer hinter den Lehrsätzen – in seinem Unterricht, seinen Widersprüchen und der offenen Überlieferung.",
    },
    "es": {
        "title": "Reabrir las Analectas",
        "subtitle": "Cincuenta encuentros con Confucio: devolver los nombres a lo que precede a «El Maestro dijo».",
        "manifesto": "Este libro no pretende derribar a un sabio ni devolverlo a su pedestal. ¿Quién pregunta? ¿A quién responde? ¿Cuándo se corrige y cuándo calla? Al devolver nombres y escenas a las frases, reaparece detrás del repertorio de máximas un maestro entre sus discípulos.",
        "method_title": "Sobre esta lectura",
        "method": "Esta lectura estructural no busca zanjar la filología ni la historia textual. Hace una pregunta más limitada: ¿qué clase de maestro aparece cuando devolvemos a cada frase sus personas, su ocasión y el movimiento de la respuesta?",
        "route_title": "Ocho puertas de entrada",
        "route_desc": "Un recorrido breve por la enseñanza, la autoridad, las malas lecturas, el desacuerdo y los límites del registro.",
        "research_title": "Edición de investigación",
        "research_desc": "Cinco artículos de SAE contienen el argumento completo. Los cincuenta ensayos son una reescritura autónoma para el lector general; no hace falta empezar por los textos académicos.",
        "read": "Leer", "essay": "Ensayo {number} de 50", "previous": "← Ensayo anterior", "next": "Ensayo siguiente →",
        "back": "Reabrir las Analectas", "door": "Este ensayo forma parte de una reconstrucción en cincuenta textos. Puedes volver a los cuatro movimientos o continuar con el siguiente.",
        "source": "Reescritura española independiente a partir de las ediciones china e inglesa. El desarrollo completo se encuentra en la edición de investigación al final de la serie.",
        "nav": ("Comenzar", "Explorar", "Novedades", "Acerca de", "Buscar", "Menú", "Biblioteca"),
        "channel_tag": "Serie insignia · 50 ensayos · Reescritura española",
        "channel_desc": "Devolver nombres y escenas a lo que precede a «El Maestro dijo» para reencontrar al maestro detrás de las máximas: cincuenta ensayos sobre su enseñanza, sus lectores y los límites del libro.",
    },
    "ko": {
        "title": "논어를 다시 열다",
        "subtitle": "‘공자가 말했다’ 앞에 이름과 장면을 돌려놓는 쉰 번의 만남.",
        "manifesto": "성인을 끌어내리거나 다시 받들기 위한 책이 아니다. 누가 물었고, 공자는 누구에게 답했는가. 언제 말을 고쳤고 언제 멈추었는가. 이름과 장면을 돌려놓으면 격언집 뒤에 가려졌던 한 교사와 제자들이 다시 보인다.",
        "method_title": "이 독해에 대하여",
        "method": "문헌학이나 성립사를 최종 판정하려는 시도가 아니다. 사람과 상황, 대답의 오고 감을 원래 자리에 놓았을 때 어떤 교사가 나타나는지를 묻는 하나의 구조적 독해다.",
        "route_title": "먼저 읽을 여덟 편",
        "route_desc": "가르침과 권위, 오독과 반론, 기록의 한계를 따라가는 짧은 입구.",
        "research_title": "이론적 바탕",
        "research_desc": "다섯 편의 SAE 논문에 전체 논증을 담았다. 앞의 쉰 편은 일반 독자를 위한 독립적인 재구성이므로 논문부터 읽을 필요는 없다.",
        "read": "읽기", "essay": "전체 50편 중 {number}편", "previous": "← 이전 글", "next": "다음 글 →",
        "back": "논어를 다시 열다", "door": "이 글은 쉰 편으로 이루어진 재구성의 일부다. 네 부의 목차로 돌아가거나 다음 글로 이어갈 수 있다.",
        "source": "중문·영문판을 바탕으로 한국어 독자를 위해 독립적으로 다시 쓴 글이다. 자세한 논증은 시리즈 끝의 연구판에서 볼 수 있다.",
        "nav": ("처음 읽기", "탐색", "새 글", "소개", "검색", "메뉴", "전체 서재"),
        "channel_tag": "대표 시리즈 · 총 50편 · 한국어 독립 재구성판",
        "channel_desc": "‘공자가 말했다’ 앞에 이름과 장면을 돌려놓고 격언 뒤의 교사를 다시 만난다. 가르침, 오독, 이견, 제자, 기록의 한계를 따라가는 쉰 편.",
    },
}

MOVEMENT_COPY = {
    "ja": (("部屋にいた一人の人", "話し、聞き、言い直し、立ち止まる仕方から孔子に会う。"), ("読み違えられた真実", "切り取られ、逆向きにされ、場面を失った名句を元へ戻す。"), ("この読解が退けるもの", "崇拝にも断罪にも逃げず、どの材料が現場の代わりにならないかを示す。"), ("弟子たちと記録の限界", "弟子が受け継ぎ、変え、争い、凍らせきれなかった師を記録する。")),
    "fr": (("Un homme dans la pièce", "Rencontrer Confucius dans sa manière d’écouter, de répondre, de se corriger et de s’arrêter."), ("Des paroles vraies, mal lues", "Rendre leur place aux formules découpées, inversées ou vidées de leur situation."), ("Ce que cette lecture refuse", "Résister au culte comme au rejet, sans prétendre régler l’histoire du texte."), ("Les disciples et les limites du livre", "Voir les disciples hériter, transformer, contester et préserver un maître qu’ils ne pouvaient figer.")),
    "de": (("Der Mensch im Raum", "Konfuzius begegnet uns darin, wie er zuhört, antwortet, sich korrigiert und innehält."), ("Wahre Sätze, falsch gelesen", "Berühmte Worte kehren in die Sätze, Situationen und Konflikte zurück, aus denen man sie löste."), ("Was diese Lektüre zurückweist", "Weder Verehrung noch Verwerfung ersetzt die genaue Lektüre des jeweiligen Falls."), ("Die Schüler und die Grenzen der Aufzeichnung", "Die Schüler erben, verändern und bestreiten einen Lehrer, den ihr Buch nicht endgültig festhalten kann.")),
    "es": (("La persona en la habitación", "Conocer a Confucio por su manera de escuchar, responder, rectificar y detenerse."), ("Palabras verdaderas, mal leídas", "Devolver a su frase y a su escena las máximas recortadas, invertidas o vaciadas de contexto."), ("Lo que esta lectura rechaza", "Resistir tanto la veneración como el descarte sin fingir que la historia textual queda resuelta."), ("Los discípulos y los límites del registro", "Observar cómo los discípulos heredan, cambian, discuten y conservan a un maestro que no pudieron inmovilizar.")),
    "ko": (("방 안에 있던 사람", "말하고 듣고, 고쳐 말하고 멈추는 방식에서 공자를 만난다."), ("잘못 읽힌 참말", "잘려 나가고 거꾸로 걸리고 장면을 잃은 유명한 문장을 제자리로 돌려놓는다."), ("이 독해가 거부하는 것", "숭배와 단죄를 모두 피하면서 무엇이 현장을 대신할 수 없는지 살핀다."), ("제자들과 기록의 한계", "제자들이 스승을 잇고 바꾸고 다투며, 끝내 얼려 두지 못한 흔적을 본다.")),
}

RESEARCH_COPY = {
    "ja": ("涵育する人", "器", "聖人になろうとしなかった人", "その部屋で", "彼の名のもとに築かれたもの"),
    "fr": ("Celui qui cultive", "L’instrument", "L’homme qui refusait d’être un sage", "Dans la pièce", "Ce qui fut bâti en son nom"),
    "de": ("Der Kultivierende", "Das Instrument", "Der Mann, der kein Weiser sein wollte", "Im Raum", "Was in seinem Namen errichtet wurde"),
    "es": ("Quien cultiva", "El instrumento", "El hombre que no quiso ser sabio", "En la habitación", "Lo que se construyó en su nombre"),
    "ko": ("기르는 사람", "도구", "성인이 되기를 거부한 사람", "그 방 안에서", "그의 이름으로 세워진 것"),
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def load_copy() -> dict[str, dict[str, dict[str, object]]]:
    expected = {(number, slug) for number, slug, _, _ in ITEMS}
    result: dict[str, dict[str, dict[str, object]]] = {}
    for lang in LANGS:
        path = DATA / f"{lang}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("language") != lang:
            raise ValueError(f"Wrong language marker in {path}")
        entries = {(entry["number"], entry["slug"]): entry for entry in payload["entries"]}
        if set(entries) != expected:
            missing = expected - set(entries)
            extra = set(entries) - expected
            raise ValueError(f"{lang}: missing={sorted(missing)}, extra={sorted(extra)}")
        for (number, slug), entry in entries.items():
            paragraphs = entry.get("paragraphs", [])
            if not 3 <= len(paragraphs) <= 6:
                raise ValueError(f"{lang}/{number}-{slug}: expected 3–6 paragraphs")
            size = len("".join(paragraphs)) if lang in ("ja", "ko") else sum(len(p.split()) for p in paragraphs)
            minimum = 260 if lang in ("ja", "ko") else 90
            if size < minimum:
                raise ValueError(f"{lang}/{number}-{slug}: copy too short ({size} < {minimum})")
        result[lang] = {slug: entry for (_, slug), entry in entries.items()}
    return result


def page_urls(filename: str) -> list[tuple[str, str]]:
    source = f"https://nondubito.net/essays/analects/{'' if filename == 'index.html' else filename}"
    if filename == "index.html":
        source = "https://nondubito.net/essays/analects/"
    localized_tail = "" if filename == "index.html" else filename
    return [
        ("en", source), ("zh-Hans", source), ("zh-Hant", source),
        *[(lang, f"https://nondubito.net/essays/analects/{lang}/{localized_tail}") for lang in LANGS],
        ("x-default", source),
    ]


def head(lang: str, filename: str, title: str, description: str, kind: str = "article") -> str:
    canonical_tail = "" if filename == "index.html" else filename
    canonical = f"https://nondubito.net/essays/analects/{lang}/{canonical_tail}"
    alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="{url}">' for code, url in page_urls(filename))
    return f'''<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(description)}"><meta name="author" content="Han Qin (秦汉)"><meta property="og:type" content="{kind}"><meta property="og:title" content="{esc(title)} — Non Dubito"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta name="twitter:card" content="summary"><link rel="canonical" href="{canonical}">{alternates}<link rel="icon" type="image/svg+xml" href="../../../favicon.svg"><link rel="apple-touch-icon" sizes="180x180" href="../../../apple-touch-icon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+JP:wght@400;500;600&amp;family=Noto+Serif+KR:wght@400;500;600&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="../../../style.css"><link rel="stylesheet" href="../../../site-shell.css?v=20260905b"><link rel="stylesheet" href="../analects.css?v=20260909"><script src="../locale-shell.js?v=20260909"></script></head>'''


def language_options(lang: str, filename: str, mobile: bool = False) -> str:
    links = []
    source_labels = (("en", "EN" if mobile else "English"), ("zh", "中文"), ("zh-hant", "繁體" if mobile else "繁體中文"))
    for code, label in source_labels:
        links.append(f'<a href="../{filename}?lang={code}">{label}</a>')
    for code in LANGS:
        label = LANG_LABEL[code] if not mobile or code in ("ja", "ko") else code.upper()
        if code == lang:
            links.append(f'<button type="button" disabled aria-current="page">{label}</button>')
        else:
            links.append(f'<a href="../{code}/{filename}">{label}</a>')
    return "".join(links)


def shell_header(lang: str, filename: str) -> str:
    start, explore, latest, about, search, menu, library = UI[lang]["nav"]
    search_href = f"../../../search.html?lang=en&amp;ui={lang}&amp;in={lang}"
    return f'''<header class="site-shell-header"><div class="header-inner"><a href="../../../index.html" class="site-title" aria-label="Non Dubito"><span class="title-latin">Non <span>Dubito</span></span><span class="title-sub">Essays in the Self-as-an-End Tradition</span></a><nav class="site-shell-nav" aria-label="Primary navigation"><a href="../../sae-foundations/{lang}/index.html">{start}</a><a href="../../../explore.html?lang=en">{explore}</a><a href="../../../latest.html?lang=en">{latest}</a><a href="../../../about.html?lang=en">{about}</a></nav><div class="site-shell-tools"><a class="site-shell-tool" href="{search_href}" aria-label="{search}"><svg class="site-shell-tool-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="6.5" stroke="currentColor" stroke-width="1.5"/><path d="m16 16 4 4" stroke="currentColor" stroke-width="1.5"/></svg><span class="site-shell-tool-label">{search}</span></a><details class="site-shell-language"><summary class="site-shell-language-summary"><span>{LANG_LABEL[lang]}</span><span aria-hidden="true">⌄</span></summary><div class="site-shell-language-options">{language_options(lang, filename)}</div></details><button class="site-shell-menu-button" type="button" data-site-shell-menu aria-controls="site-shell-drawer" aria-expanded="false"><span class="site-shell-tool-label">{menu}</span><span aria-hidden="true">☰</span></button></div></div></header><div class="site-shell-drawer" id="site-shell-drawer" data-site-shell-drawer><nav aria-label="Mobile navigation"><a href="../../sae-foundations/{lang}/index.html">{start}</a><a href="../../../explore.html?lang=en">{explore}</a><a href="../../../latest.html?lang=en">{latest}</a><a href="../../../about.html?lang=en">{about}</a><a href="../../../library.html?lang=en">{library}</a><a href="https://credesivis.org/index.html">Crede si vis</a></nav><div class="site-shell-mobile-languages" aria-label="Languages">{language_options(lang, filename, True)}</div></div>'''


def article_html(lang: str, item: tuple[str, str, str, str], position: int, copy: dict[str, dict[str, object]]) -> str:
    number, slug, _, _ = item
    entry = copy[slug]
    filename = f"{number}-{slug}.html"
    title = str(entry["title"])
    deck = str(entry["deck"])
    body = "".join(f"<p>{esc(str(paragraph))}</p>" for paragraph in entry["paragraphs"])
    move_index = next(i for i, m in enumerate(MOVEMENTS) if m[0] <= position + 1 <= m[1])
    movement = MOVEMENT_COPY[lang][move_index][0]
    previous = ITEMS[position - 1] if position else None
    following = ITEMS[position + 1] if position + 1 < len(ITEMS) else None
    nav = []
    if previous:
        nav.append(f'<a href="{previous[0]}-{previous[1]}.html"><small>{UI[lang]["previous"]}</small>{esc(str(copy[previous[1]]["title"]))}</a>')
    if following:
        nav.append(f'<a class="next" href="{following[0]}-{following[1]}.html"><small>{UI[lang]["next"]}</small>{esc(str(copy[following[1]]["title"]))}</a>')
    schema = json.dumps({"@context":"https://schema.org","@type":"Article","headline":title,"description":deck,"inLanguage":HTML_LANG[lang],"author":{"@type":"Person","name":"Han Qin (秦汉)"},"isPartOf":{"@type":"CreativeWorkSeries","name":UI[lang]["title"]},"position":position + 1,"url":f"https://nondubito.net/essays/analects/{lang}/{filename}"}, ensure_ascii=False, indent=2)
    return f'''<!DOCTYPE html><html lang="{HTML_LANG[lang]}">{head(lang, filename, title + " · " + UI[lang]["title"], deck)}<body class="site-shell-page analects-locale-{lang}">{shell_header(lang, filename)}<main class="analects-wrap"><div class="article-top"><a href="index.html">← {esc(UI[lang]["back"])}</a></div><article class="analects-article"><header class="article-head"><p class="article-kicker">{esc(movement)}</p><p class="article-number">{esc(UI[lang]["essay"].format(number=number))}</p><h1>{esc(title)}</h1><p class="article-deck">{esc(deck)}</p><p class="article-byline">Han Qin (秦汉) · 2026</p></header><div class="article-body">{body}<p class="source-note">{esc(UI[lang]["source"])}</p></div></article><nav class="series-nav">{"".join(nav)}</nav><aside class="reader-door">{esc(UI[lang]["door"])}</aside></main><footer class="site-shell-footer"><div class="site-shell-footer-inner"><div><div class="site-shell-footer-mark">Non <span>Dubito</span></div><p>A mind in many languages</p></div><div class="site-shell-footer-links"><a href="../../../about.html">About</a><a href="../../../library.html">Library</a><a href="https://self-as-an-end.net">SAE Theory ↗</a></div></div></footer><script type="application/ld+json">{schema}</script></body></html>'''


def index_html(lang: str, copy: dict[str, dict[str, object]]) -> str:
    route_numbers = ("01", "02", "05", "25", "32", "37", "47", "50")
    routes = []
    for number in route_numbers:
        item = next(item for item in ITEMS if item[0] == number)
        routes.append(f'<a href="{number}-{item[1]}.html"><span>{number}</span>{esc(str(copy[item[1]]["title"]))}</a>')
    movements = []
    for movement_index, (start, end, _, _, _) in enumerate(MOVEMENTS):
        title, desc = MOVEMENT_COPY[lang][movement_index]
        cards = []
        for number, slug, _, _ in ITEMS[start - 1:end]:
            entry = copy[slug]
            cards.append(f'<a class="essay-card" href="{number}-{slug}.html"><span class="essay-no">{number}</span><h3>{esc(str(entry["title"]))}</h3><p>{esc(str(entry["deck"]))}</p><span class="read-arrow">{esc(UI[lang]["read"])} →</span></a>')
        movements.append(f'<section class="movement"><header><span>{start:02d}—{end:02d}</span><h2>{esc(title)}</h2><p>{esc(desc)}</p></header><div class="essay-grid">{"".join(cards)}</div></section>')
    research_cards = "".join(f'<a href="{url}" target="_blank" rel="noopener"><small>{"Introduction" if i == 0 else f"Part {i}"}</small><strong>{esc(RESEARCH_COPY[lang][i])}</strong><span>{esc(english)} ↗</span></a>' for i, (_, english, _, url) in enumerate(RESEARCH))
    schema = json.dumps({"@context":"https://schema.org","@type":"CollectionPage","name":UI[lang]["title"],"description":UI[lang]["subtitle"],"inLanguage":HTML_LANG[lang],"url":f"https://nondubito.net/essays/analects/{lang}/","author":{"@type":"Person","name":"Han Qin (秦汉)"},"mainEntity":{"@type":"ItemList","numberOfItems":50,"itemListElement":[{"@type":"ListItem","position":i,"name":copy[item[1]]["title"],"url":f"https://nondubito.net/essays/analects/{lang}/{item[0]}-{item[1]}.html"} for i, item in enumerate(ITEMS, 1)]}}, ensure_ascii=False, indent=2)
    return f'''<!DOCTYPE html><html lang="{HTML_LANG[lang]}">{head(lang, "index.html", UI[lang]["title"], UI[lang]["subtitle"], "website")}<body class="site-shell-page analects-locale-{lang}">{shell_header(lang, "index.html")}<main class="analects-wrap"><section class="series-hero"><p class="series-kicker">Non Dubito · Analects</p><h1>{esc(UI[lang]["title"])}</h1><p class="series-deck">{esc(UI[lang]["subtitle"])}</p><p class="series-manifesto">{esc(UI[lang]["manifesto"])}</p><div class="series-meta">Han Qin (秦汉) · 2026 · 4 · 50 · 8 languages</div></section><aside class="method-note"><strong>{esc(UI[lang]["method_title"])}</strong><p>{esc(UI[lang]["method"])}</p></aside><section class="reading-route"><h2>{esc(UI[lang]["route_title"])}</h2><p>{esc(UI[lang]["route_desc"])}</p><div class="route-grid">{"".join(routes)}</div></section>{"".join(movements)}<section class="research"><header><p>SAE · Analects</p><h2>{esc(UI[lang]["research_title"])}</h2><span>{esc(UI[lang]["research_desc"])}</span></header><div class="research-grid">{research_cards}</div></section></main><footer class="site-shell-footer"><div class="site-shell-footer-inner"><div><div class="site-shell-footer-mark">Non <span>Dubito</span></div><p>A mind in many languages</p></div><div class="site-shell-footer-links"><a href="../../../about.html">About</a><a href="../../../library.html">Library</a><a href="https://self-as-an-end.net">SAE Theory ↗</a></div></div></footer><script type="application/ld+json">{schema}</script></body></html>'''


def channel_hub(lang: str, text: str) -> str:
    marker = f'<a href="../daodejing/{lang}/index.html"'
    start = "<!-- ANALECTS LANGUAGE HUB START -->"
    end = "<!-- ANALECTS LANGUAGE HUB END -->"
    card = f'''{start}<a href="../analects/{lang}/index.html" class="essay-card" style="text-decoration:none;border-left:3px solid var(--gold);background:rgba(196,157,97,.04);display:block;padding:2rem 2.25rem;margin-bottom:1rem;"><div style="font-family:var(--sans);font-size:.65rem;letter-spacing:.13em;text-transform:uppercase;color:var(--gold);margin-bottom:.7rem;">{esc(UI[lang]["channel_tag"])}</div><div style="font-size:1.55rem;color:var(--ink);margin-bottom:.6rem;">{esc(UI[lang]["title"])}</div><p style="font-size:.94rem;color:var(--ink-light);line-height:1.75;max-width:700px;margin:0;">{esc(UI[lang]["channel_desc"])}</p></a>{end}\n  '''
    if start in text:
        updated, count = re.subn(re.escape(start) + r".*?" + re.escape(end) + r"\s*", card, text, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f"Could not refresh Analects card in {lang} channel")
        return updated
    if marker not in text:
        raise ValueError(f"Could not find Daodejing card in {lang} channel")
    return text.replace(marker, card + marker, 1)


def shared_hubs() -> dict[Path, str]:
    library_path = ROOT / "library.html"
    updates_path = ROOT / "data" / "site-updates.json"
    latest_path = ROOT / "latest.html"
    library = library_path.read_text(encoding="utf-8")
    library = library.replace("50 essays · 3 reading modes", "50 essays · 8 languages")
    library = library.replace("50 篇 · 英 / 简 / 繁", "50 篇 · 8 种语言")
    library = library.replace("50 篇 · 英 / 簡 / 繁", "50 篇 · 8 種語言")

    data = json.loads(updates_path.read_text(encoding="utf-8"))
    update = {
        "id": "2026-09-09-analects-languages",
        "date": "2026-09-09",
        "kind": "expanded",
        "domain": "literature",
        "url": "essays/analects/index.html",
        "languages": ["ja", "fr", "de", "es", "ko"],
        "title": {"en": "The Analects, Reopened", "zh": "大知解论语", "zh-hant": "大知解論語"},
        "summary": {
            "en": "The fifty-essay flagship is now complete in Japanese, French, German, Spanish, and Korean, bringing the series to eight languages.",
            "zh": "五十篇旗舰系列完成日、法、德、西、韩五种独立重写，正式扩展为八语言版本。",
            "zh-hant": "五十篇旗艦系列完成日、法、德、西、韓五種獨立重寫，正式擴展為八語言版本。",
        },
    }
    existing = next((index for index, item in enumerate(data["updates"]) if item["id"] == update["id"]), None)
    if existing is None:
        data["updates"].insert(0, update)
    else:
        data["updates"][existing] = update

    latest = latest_path.read_text(encoding="utf-8")
    update_id = 'data-update-id="2026-09-09-analects-languages"'
    marker = '<section class="updates-section"><div class="latest-inner">'
    section = '''<section class="updates-day" aria-labelledby="date-2026-09-09"><header class="updates-date"><div><p class="latest-date-label">Publication date</p><h2 id="date-2026-09-09"><time datetime="2026-09-09"><span class="lang-en">9 September</span><span class="lang-zh">9 月 9 日</span><span class="lang-hant">9 月 9 日</span></time></h2></div><p class="lang-en">The Analects flagship now speaks through eight complete reading editions.</p><p class="lang-zh">《大知解论语》完成五种新增语言，正式成为八语言旗舰。</p><p class="lang-hant">《大知解論語》完成五種新增語言，正式成為八語言旗艦。</p></header><div class="updates-grid"><article class="update-card" data-update-id="2026-09-09-analects-languages"><div class="update-meta"><span class="update-kind"><span class="lang-en">Language expansion</span><span class="lang-zh">全语言拓展</span><span class="lang-hant">全語言拓展</span></span><span class="update-languages">日本語 / FR / DE / ES / 한국어</span></div><h3 class="lang-en">The Analects, Reopened</h3><h3 class="lang-zh">大知解论语</h3><h3 class="lang-hant">大知解論語</h3><p class="lang-en">All fifty essays were independently rewritten for Japanese, French, German, Spanish, and Korean readers, completing the eight-language edition.</p><p class="lang-zh">五十篇全部完成日、法、德、西、韩独立重写，四辑与八篇入口也在各语言中完整保留。</p><p class="lang-hant">五十篇全部完成日、法、德、西、韓獨立重寫，四輯與八篇入口也在各語言中完整保留。</p><a href="essays/analects/index.html"><span class="lang-en">Enter the series →</span><span class="lang-zh">进入系列 →</span><span class="lang-hant">進入系列 →</span></a></article></div></section>'''
    if update_id not in latest:
        if marker not in latest:
            raise ValueError("Could not locate latest feed")
        latest = latest.replace(marker, marker + section, 1)
    else:
        latest, count = re.subn(r'<section class="updates-day" aria-labelledby="date-2026-09-09">.*?</section>', section, latest, count=1, flags=re.S)
        if count != 1:
            raise ValueError("Could not refresh Analects language update")
    return {
        library_path: library,
        updates_path: serialize_updates(data),
        latest_path: latest,
    }


def render() -> dict[Path, str]:
    copy = load_copy()
    outputs: dict[Path, str] = shared_hubs()
    for lang in LANGS:
        outputs[SERIES / lang / "index.html"] = index_html(lang, copy[lang])
        for position, item in enumerate(ITEMS):
            outputs[SERIES / lang / f"{item[0]}-{item[1]}.html"] = article_html(lang, item, position, copy[lang])
        channel = ROOT / "essays" / lang / "index.html"
        outputs[channel] = channel_hub(lang, channel.read_text(encoding="utf-8"))
    return {
        path: text.replace("analects.css?v=20260909", "analects.css?v=20260909b")
        for path, text in outputs.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    stale = [path for path, text in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != text]
    if args.check:
        if stale:
            raise SystemExit("Stale Analects language pages:\n" + "\n".join(str(path.relative_to(ROOT)) for path in stale))
        print(f"OK: {len(outputs)} Analects language files")
        return
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"Wrote: {len(outputs)} Analects language files")


if __name__ == "__main__":
    main()
