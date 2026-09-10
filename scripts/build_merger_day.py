#!/usr/bin/env python3
"""Publish the definitive eight-language edition of Merger Day."""

from __future__ import annotations

import argparse
import ctypes
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "originals" / "merger-day"
SERIES = ROOT / "originals" / "short-science-fiction"
LANGS = ("ja", "fr", "de", "es", "ko")
ALL_LANGS = ("en", "zh", "zh-hant", *LANGS)
HTML_LANG = {"en": "en", "zh": "zh-Hans", "zh-hant": "zh-Hant", "ja": "ja", "fr": "fr", "de": "de", "es": "es", "ko": "ko"}
HREFLANG = {"en": "en", "zh": "zh-Hans", "zh-hant": "zh-Hant", "ja": "ja", "fr": "fr", "de": "de", "es": "es", "ko": "ko"}
LANG_LABEL = {"en": "English", "zh": "中文", "zh-hant": "繁體中文", "ja": "日本語", "fr": "Français", "de": "Deutsch", "es": "Español", "ko": "한국어"}
UTF8 = 0x08000100

COPY = {
    "en": {
        "title": "Merger Day",
        "shelf": "Short Science Fiction",
        "deck": "Two women share the same first thirty-three years. Six months apart leave them with memories a merger can carry—and lives it cannot replace.",
        "intro": "Stories set close enough to the present that their technologies feel almost ordinary, and strange enough to reveal what ordinary life has been assuming all along.",
        "back": "Short Science Fiction",
        "read": "Read the story",
        "kicker": "Original short fiction · definitive edition",
        "edition": "English literary edition · 8 languages",
        "date": "5 Sep 2026 · definitive text 9 Sep 2026",
        "note": "An independent English literary edition of Han Qin’s final Chinese manuscript.",
        "nav": ("Start Here", "Explore", "Latest", "About", "Search", "Menu", "Full Library"),
        "channel_tag": "Original fiction · definitive edition · 8 languages",
        "channel_desc": "Two lives begin with the same thirty-three years. A swimming class, a current map, and an eighteen-second video reveal what their planned merger cannot decide for them.",
    },
    "zh": {
        "title": "合并日",
        "shelf": "短篇科幻小说",
        "deck": "两个女人共享最初三十三年的记忆。分开生活半年后，她们发现：合并能够带走两边的记忆，却不能替任何人活完其中一边。",
        "intro": "这些故事离现在足够近，其中的技术几乎寻常；又足够陌生，让日常生活里那些从未说出的前提显出形状。",
        "back": "短篇科幻小说",
        "read": "阅读小说",
        "kicker": "原创短篇小说 · 正式定稿",
        "edition": "中文原作 · 8 种语言",
        "date": "2026 年 9 月 5 日 · 9 月 9 日定稿",
        "note": "秦汉中文原作定稿。",
        "nav": ("从这里开始", "探索", "最近更新", "关于", "搜索", "菜单", "完整书库"),
        "channel_tag": "原创小说 · 正式定稿 · 8 种语言",
        "channel_desc": "两个女人共享最初三十三年的记忆。一堂游泳课、一张海流图和十八秒视频，让她们看见合并无法替任何人作出的决定。",
    },
    "zh-hant": {
        "title": "合併日",
        "shelf": "短篇科幻小說",
        "deck": "兩個女人共享最初三十三年的記憶。分開生活半年後，她們發現：合併能夠帶走兩邊的記憶，卻不能替任何人活完其中一邊。",
        "intro": "這些故事離現在足夠近，其中的技術幾乎尋常；又足夠陌生，讓日常生活裡那些從未說出的前提顯出形狀。",
        "back": "短篇科幻小說",
        "read": "閱讀小說",
        "kicker": "原創短篇小說 · 正式定稿",
        "edition": "中文原作 · 8 種語言",
        "date": "2026 年 9 月 5 日 · 9 月 9 日定稿",
        "note": "秦漢中文原作定稿。",
        "nav": ("從這裡開始", "探索", "最近更新", "關於", "搜尋", "選單", "完整書庫"),
        "channel_tag": "原創小說 · 正式定稿 · 8 種語言",
        "channel_desc": "兩個女人共享最初三十三年的記憶。一堂游泳課、一張海流圖和十八秒影片，讓她們看見合併無法替任何人作出的決定。",
    },
    "ja": {
        "title": "統合の日",
        "shelf": "短篇SF",
        "deck": "最初の三十三年を共有する二人。別々に生きた半年は、統合が運べる記憶と、誰にも代われない人生の違いを露わにする。",
        "intro": "いまから遠すぎない未来。ほとんど日常に見える技術が、日常の中で見過ごしていた前提を浮かび上がらせる短篇SF。",
        "back": "短篇SF",
        "read": "物語を読む",
        "kicker": "オリジナル短篇SF · 決定稿",
        "edition": "日本語文学版 · 8言語",
        "date": "2026年9月5日 · 9月9日決定稿",
        "note": "Han Qin（秦汉）の中国語決定稿をもとに、日本語の小説として独立に再構成した版です。",
        "nav": ("はじめに", "探す", "新着", "このサイトについて", "検索", "メニュー", "全ライブラリ"),
        "channel_tag": "オリジナル短篇SF · 決定稿 · 8言語",
        "channel_desc": "同じ三十三年から始まった二人。水泳教室、海流図、十八秒の動画が、予定されていた統合では決められないことを明らかにする。",
    },
    "fr": {
        "title": "Le Jour de la fusion",
        "shelf": "Science-fiction courte",
        "deck": "Deux femmes partagent leurs trente-trois premières années. Six mois de vies séparées révèlent ce qu’une fusion peut emporter — et ce qu’elle ne peut vivre à la place de personne.",
        "intro": "Des futurs assez proches pour que leur technologie paraisse ordinaire, et assez étranges pour révéler les présupposés cachés de la vie quotidienne.",
        "back": "Science-fiction courte",
        "read": "Lire la nouvelle",
        "kicker": "Nouvelle originale · édition définitive",
        "edition": "Édition littéraire française · 8 langues",
        "date": "5 sept. 2026 · texte définitif le 9 sept. 2026",
        "note": "Une réécriture littéraire française autonome du manuscrit chinois définitif de Han Qin.",
        "nav": ("Commencer", "Explorer", "Nouveautés", "À propos", "Rechercher", "Menu", "Bibliothèque"),
        "channel_tag": "Fiction originale · édition définitive · 8 langues",
        "channel_desc": "Deux vies commencent par les mêmes trente-trois années. Un cours de natation, une carte des courants et une vidéo de dix-huit secondes révèlent ce que leur fusion ne peut décider.",
    },
    "de": {
        "title": "Der Tag der Verschmelzung",
        "shelf": "Kurze Science-Fiction",
        "deck": "Zwei Frauen teilen dieselben ersten dreiunddreißig Jahre. Sechs getrennte Monate zeigen, welche Erinnerungen eine Verschmelzung tragen kann — und welches Leben sie niemandem abnimmt.",
        "intro": "Zukünfte, nah genug, dass ihre Technik beinahe alltäglich wirkt, und fremd genug, um die verborgenen Voraussetzungen des Alltags sichtbar zu machen.",
        "back": "Kurze Science-Fiction",
        "read": "Erzählung lesen",
        "kicker": "Originalerzählung · endgültige Fassung",
        "edition": "Deutsche literarische Fassung · 8 Sprachen",
        "date": "5. Sept. 2026 · endgültige Fassung vom 9. Sept. 2026",
        "note": "Eine eigenständige deutsche literarische Neufassung nach Han Qins endgültigem chinesischem Manuskript.",
        "nav": ("Einstieg", "Entdecken", "Neu", "Über", "Suchen", "Menü", "Bibliothek"),
        "channel_tag": "Originalerzählung · endgültige Fassung · 8 Sprachen",
        "channel_desc": "Zwei Leben beginnen mit denselben dreiunddreißig Jahren. Ein Schwimmkurs, eine Strömungskarte und ein achtzehn Sekunden langes Video zeigen, was ihre geplante Verschmelzung nicht entscheiden kann.",
    },
    "es": {
        "title": "El día de la fusión",
        "shelf": "Ciencia ficción breve",
        "deck": "Dos mujeres comparten los mismos treinta y tres primeros años. Seis meses de vidas separadas revelan qué recuerdos puede llevarse una fusión y qué vida no puede vivir por nadie.",
        "intro": "Futuros lo bastante cercanos para que su tecnología parezca cotidiana y lo bastante extraños para revelar los supuestos ocultos de la vida diaria.",
        "back": "Ciencia ficción breve",
        "read": "Leer el relato",
        "kicker": "Relato original · edición definitiva",
        "edition": "Edición literaria en español · 8 idiomas",
        "date": "5 sept. 2026 · texto definitivo del 9 sept. 2026",
        "note": "Una reescritura literaria autónoma en español del manuscrito chino definitivo de Han Qin.",
        "nav": ("Comenzar", "Explorar", "Novedades", "Acerca de", "Buscar", "Menú", "Biblioteca"),
        "channel_tag": "Ficción original · edición definitiva · 8 idiomas",
        "channel_desc": "Dos vidas comienzan con los mismos treinta y tres años. Una clase de natación, un mapa de corrientes y un vídeo de dieciocho segundos revelan lo que su fusión no puede decidir.",
    },
    "ko": {
        "title": "합쳐지는 날",
        "shelf": "단편 SF",
        "deck": "처음 삼십삼 년을 공유한 두 사람. 따로 살아 낸 반년은 통합이 가져갈 수 있는 기억과 누구도 대신 살 수 없는 삶의 차이를 드러낸다.",
        "intro": "기술이 거의 일상처럼 느껴질 만큼 가까우면서도, 우리가 당연하게 여긴 전제를 드러낼 만큼 낯선 미래를 그린 단편 SF.",
        "back": "단편 SF",
        "read": "소설 읽기",
        "kicker": "오리지널 단편 SF · 최종본",
        "edition": "한국어 문학판 · 8개 언어",
        "date": "2026년 9월 5일 · 9월 9일 최종본",
        "note": "Han Qin(秦汉)의 중국어 최종 원고를 바탕으로 한국어 소설로 독립 재구성한 판본입니다.",
        "nav": ("처음 읽기", "둘러보기", "새 글", "소개", "검색", "메뉴", "전체 서재"),
        "channel_tag": "오리지널 단편 SF · 최종본 · 8개 언어",
        "channel_desc": "같은 삼십삼 년에서 시작한 두 사람. 수영 수업, 해류 지도, 십팔 초짜리 영상이 예정된 통합으로는 결정할 수 없는 것을 보여 준다.",
    },
}


class TraditionalConverter:
    def __init__(self) -> None:
        self.cf = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
        self.cf.CFStringCreateMutable.argtypes = [ctypes.c_void_p, ctypes.c_long]
        self.cf.CFStringCreateMutable.restype = ctypes.c_void_p
        self.cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint]
        self.cf.CFStringCreateWithCString.restype = ctypes.c_void_p
        self.cf.CFStringAppend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.cf.CFStringTransform.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ubyte]
        self.cf.CFStringTransform.restype = ctypes.c_ubyte
        self.cf.CFStringGetLength.argtypes = [ctypes.c_void_p]
        self.cf.CFStringGetLength.restype = ctypes.c_long
        self.cf.CFStringGetMaximumSizeForEncoding.argtypes = [ctypes.c_long, ctypes.c_uint]
        self.cf.CFStringGetMaximumSizeForEncoding.restype = ctypes.c_long
        self.cf.CFStringGetCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_uint]
        self.cf.CFStringGetCString.restype = ctypes.c_ubyte
        self.cf.CFRelease.argtypes = [ctypes.c_void_p]
        self.transform = self._string("Traditional-Simplified")

    def _string(self, value: str) -> int:
        return self.cf.CFStringCreateWithCString(None, value.encode("utf-8"), UTF8)

    def convert(self, value: str) -> str:
        source = self._string(value)
        mutable = self.cf.CFStringCreateMutable(None, 0)
        try:
            self.cf.CFStringAppend(mutable, source)
            if not self.cf.CFStringTransform(mutable, None, self.transform, 1):
                raise RuntimeError("Traditional Chinese conversion failed")
            length = self.cf.CFStringGetLength(mutable)
            size = self.cf.CFStringGetMaximumSizeForEncoding(length, UTF8) + 1
            buffer = ctypes.create_string_buffer(size)
            if not self.cf.CFStringGetCString(mutable, buffer, size, UTF8):
                raise RuntimeError("Traditional Chinese encoding failed")
            return buffer.value.decode("utf-8").replace("視頻", "影片")
        finally:
            self.cf.CFRelease(source)
            self.cf.CFRelease(mutable)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_copy() -> dict[str, list[str]]:
    output: dict[str, list[str]] = {}
    for lang in ("en", "zh", *LANGS):
        path = DATA / f"{lang}.md"
        text = path.read_text(encoding="utf-8").strip()
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
        minimum = 180 if lang in ("en", "fr", "de", "es") else 190
        if len(paragraphs) < minimum:
            raise ValueError(f"{lang}: only {len(paragraphs)} paragraphs")
        if len(text) < 7000:
            raise ValueError(f"{lang}: story is unexpectedly short")
        output[lang] = paragraphs
    converter = TraditionalConverter()
    try:
        output["zh-hant"] = [converter.convert(paragraph) for paragraph in output["zh"]]
    finally:
        self_ref = getattr(converter, "transform", None)
        if self_ref:
            converter.cf.CFRelease(self_ref)
    return output


def page_urls(filename: str) -> list[tuple[str, str]]:
    base = "https://nondubito.net/originals/short-science-fiction/"
    target = "" if filename == "index.html" else filename
    return [
        ("en", base + target),
        ("zh-Hans", base + target),
        ("zh-Hant", base + target),
        *((HREFLANG[lang], f"{base}{lang}/{target}") for lang in LANGS),
        ("x-default", base + target),
    ]


def head(lang: str, filename: str, description: str, localized: bool, page_type: str) -> str:
    if localized:
        target = "" if filename == "index.html" else filename
        canonical = f"https://nondubito.net/originals/short-science-fiction/{lang}/{target}"
        root_prefix = "../../../"
        asset_prefix = "../"
    else:
        target = "" if filename == "index.html" else filename
        canonical = f"https://nondubito.net/originals/short-science-fiction/{target}"
        root_prefix = "../../"
        asset_prefix = ""
    alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="{url}">' for code, url in page_urls(filename))
    title = COPY[lang]["title"] if filename != "index.html" else COPY[lang]["shelf"]
    if not localized:
        title = "Merger Day · 合并日" if filename != "index.html" else "Short Science Fiction · 短篇科幻小说"
    return f'''<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(description)}"><meta name="author" content="Han Qin (秦汉)"><meta property="og:type" content="{page_type}"><meta property="og:title" content="{esc(title)} — Non Dubito"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary"><link rel="canonical" href="{canonical}">{alternates}<link rel="icon" type="image/svg+xml" href="{root_prefix}favicon.svg"><link rel="apple-touch-icon" sizes="180x180" href="{root_prefix}apple-touch-icon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;family=Noto+Serif+TC:wght@400;500;600&amp;family=Noto+Serif+JP:wght@400;500;600&amp;family=Noto+Serif+KR:wght@400;500;600&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="{root_prefix}style.css"><link rel="stylesheet" href="{root_prefix}site-shell.css?v=20260905b"><link rel="stylesheet" href="{asset_prefix}merger-day.css?v=20260909"><script src="{asset_prefix}merger-day.js?v=20260909"></script></head>'''


def language_options(lang: str, filename: str, localized: bool, mobile: bool = False) -> str:
    labels = {"en": "EN" if mobile else "English", "zh": "中文", "zh-hant": "繁體" if mobile else "繁體中文"}
    items: list[str] = []
    if localized:
        for code in ("en", "zh", "zh-hant"):
            items.append(f'<a href="../{filename}?lang={code}">{labels[code]}</a>')
        for code in LANGS:
            display = LANG_LABEL[code] if not mobile or code in ("ja", "ko") else code.upper()
            if code == lang:
                items.append(f'<button type="button" disabled aria-current="page">{display}</button>')
            else:
                items.append(f'<a href="../{code}/{filename}">{display}</a>')
    else:
        for code in ("en", "zh", "zh-hant"):
            items.append(f'<button type="button" data-set-language="{code}">{labels[code]}</button>')
        for code in LANGS:
            display = LANG_LABEL[code] if not mobile or code in ("ja", "ko") else code.upper()
            items.append(f'<a href="{code}/{filename}">{display}</a>')
    return "".join(items)


def shell(lang: str, filename: str, localized: bool) -> str:
    prefix = "../../../" if localized else "../../"
    start, explore, latest, about, search, menu, library = COPY[lang]["nav"]
    if not localized:
        def tri(index: int) -> str:
            en = COPY["en"]["nav"][index]
            zh = COPY["zh"]["nav"][index]
            hant = COPY["zh-hant"]["nav"][index]
            return f'<span class="lang-en">{en}</span><span class="lang-zh">{zh}</span><span class="lang-hant">{hant}</span>'

        start, explore, latest, about, search, menu, library = (tri(index) for index in range(7))
    current = LANG_LABEL[lang] if localized else '<span data-current-language>中文</span>'
    options = language_options(lang, filename, localized)
    mobile_options = language_options(lang, filename, localized, True)
    search_aria = COPY[lang]["nav"][4] if localized else "Search / 搜索"
    query = f"?lang=en&amp;ui={lang}&amp;in={lang}" if localized else ""
    return f'''<header class="site-shell-header"><div class="header-inner"><a href="{prefix}index.html" class="site-title" aria-label="Non Dubito home"><span class="title-latin">Non <span>Dubito</span></span><span class="title-sub">A Mind in Many Languages</span></a><nav class="site-shell-nav" aria-label="Primary navigation"><a href="{prefix}start.html">{start}</a><a href="{prefix}explore.html{query}">{explore}</a><a href="{prefix}latest.html{query}">{latest}</a><a href="{prefix}about.html{query}">{about}</a></nav><div class="site-shell-tools"><a class="site-shell-tool" href="{prefix}search.html{query}" aria-label="{search_aria}"><svg class="site-shell-tool-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="6.5" stroke="currentColor" stroke-width="1.5"/><path d="m16 16 4 4" stroke="currentColor" stroke-width="1.5"/></svg><span class="site-shell-tool-label">{search}</span></a><details class="site-shell-language"><summary class="site-shell-language-summary">{current}<span aria-hidden="true">⌄</span></summary><div class="site-shell-language-options">{options}</div></details><button class="site-shell-menu-button" type="button" data-site-shell-menu aria-controls="site-shell-drawer" aria-expanded="false"><span class="site-shell-tool-label">{menu}</span><span aria-hidden="true">☰</span></button></div></div></header><div class="site-shell-drawer" id="site-shell-drawer" data-site-shell-drawer><nav aria-label="Mobile navigation"><a href="{prefix}start.html">{start}</a><a href="{prefix}explore.html{query}">{explore}</a><a href="{prefix}latest.html{query}">{latest}</a><a href="{prefix}about.html{query}">{about}</a><a href="{prefix}library.html{query}">{library}</a></nav><div class="site-shell-mobile-languages" aria-label="Languages">{mobile_options}</div></div>'''


def body_class(lang: str) -> str:
    if lang in ("zh", "zh-hant"):
        return "fiction-body cjk" + (" tc" if lang == "zh-hant" else "")
    if lang == "ja":
        return "fiction-body jp"
    if lang == "ko":
        return "fiction-body kr"
    return "fiction-body"


def title_class(lang: str) -> str:
    if lang in ("zh", "zh-hant"):
        return "fiction-title cjk" + (" tc" if lang == "zh-hant" else "")
    if lang == "ja":
        return "fiction-title jp"
    if lang == "ko":
        return "fiction-title kr"
    return "fiction-title"


def paragraphs_html(paragraphs: list[str]) -> str:
    return "".join(f"<p>{esc(paragraph)}</p>" for paragraph in paragraphs)


def footer(prefix: str, lang: str) -> str:
    return f'''<footer class="site-shell-footer"><div class="site-shell-footer-inner"><div><div class="site-shell-footer-mark">Non <span>Dubito</span></div><p>A mind in many languages</p></div><div class="site-shell-footer-links"><a href="{prefix}originals/index.html">Original Writing</a><a href="{prefix}library.html">Library</a><a href="https://self-as-an-end.net">SAE Theory ↗</a></div></div></footer>'''


def story_schema(lang: str, url: str) -> str:
    language = [HTML_LANG[code] for code in ("en", "zh", "zh-hant")] if lang == "zh" else HTML_LANG[lang]
    name = "Merger Day · 合并日" if lang == "zh" else COPY[lang]["title"]
    return json.dumps({"@context": "https://schema.org", "@type": "CreativeWork", "name": name, "description": COPY[lang]["deck"], "genre": "Science fiction", "inLanguage": language, "datePublished": "2026-09-05", "dateModified": "2026-09-09", "author": {"@type": "Person", "name": "Han Qin (秦汉)"}, "url": url}, ensure_ascii=False, indent=2)


def base_story(copy: dict[str, list[str]]) -> str:
    heroes = []
    bodies = []
    for lang in ("en", "zh", "zh-hant"):
        local = "hant" if lang == "zh-hant" else lang
        heroes.append(f'''<div class="lang-{local}"><p class="fiction-kicker">{esc(COPY[lang]["kicker"])}</p><h1 class="{title_class(lang)}">{esc(COPY[lang]["title"])}</h1><p class="fiction-deck">{esc(COPY[lang]["deck"])}</p><div class="fiction-meta"><span>Han Qin (秦汉)</span><span>{esc(COPY[lang]["date"])}</span><span>{esc(COPY[lang]["edition"])}</span></div></div>''')
        bodies.append(f'''<article class="{body_class(lang)} lang-{local}">{paragraphs_html(copy[lang])}<p class="fiction-end" aria-hidden="true">◆</p></article>''')
    schema = story_schema("zh", "https://nondubito.net/originals/short-science-fiction/merger-day.html")
    return f'''<!DOCTYPE html><html lang="zh-Hans" data-lang="zh" data-editions="en zh zh-hant">{head("zh", "merger-day.html", COPY["en"]["deck"], False, "article")}<body class="site-shell-page explicit-hant">{shell("zh", "merger-day.html", False)}<main class="fiction-wrap"><section class="fiction-hero"><a class="fiction-back" href="index.html"><span class="lang-en">← {COPY["en"]["back"]}</span><span class="lang-zh">← {COPY["zh"]["back"]}</span><span class="lang-hant">← {COPY["zh-hant"]["back"]}</span></a>{''.join(heroes)}</section>{''.join(bodies)}</main>{footer("../../", "zh")}<script type="application/ld+json">{schema}</script></body></html>'''


def localized_story(lang: str, paragraphs: list[str]) -> str:
    url = f"https://nondubito.net/originals/short-science-fiction/{lang}/merger-day.html"
    schema = story_schema(lang, url)
    return f'''<!DOCTYPE html><html lang="{HTML_LANG[lang]}">{head(lang, "merger-day.html", COPY[lang]["deck"], True, "article")}<body class="site-shell-page">{shell(lang, "merger-day.html", True)}<main class="fiction-wrap"><section class="fiction-hero"><a class="fiction-back" href="index.html">← {esc(COPY[lang]["back"])}</a><p class="fiction-kicker">{esc(COPY[lang]["kicker"])}</p><h1 class="{title_class(lang)}">{esc(COPY[lang]["title"])}</h1><p class="fiction-deck">{esc(COPY[lang]["deck"])}</p><div class="fiction-meta"><span>Han Qin (秦汉)</span><span>{esc(COPY[lang]["date"])}</span><span>{esc(COPY[lang]["edition"])}</span></div></section><article class="{body_class(lang)}">{paragraphs_html(paragraphs)}<p class="fiction-end" aria-hidden="true">◆</p><p class="fiction-note">{esc(COPY[lang]["note"])}</p></article></main>{footer("../../../", lang)}<script type="application/ld+json">{schema}</script></body></html>'''


def shelf_body(lang: str, localized: bool) -> str:
    title_style = " cjk" if lang in ("zh", "zh-hant") else (" jp" if lang == "ja" else (" kr" if lang == "ko" else ""))
    href = "merger-day.html"
    return f'''<section class="shelf-intro"><p class="fiction-kicker">Non Dubito · Original Writing</p><h1 class="{title_style.strip()}">{esc(COPY[lang]["shelf"])}</h1><p>{esc(COPY[lang]["intro"])}</p></section><a class="story-card" href="{href}"><span class="story-card-no">01</span><div><h2 class="{title_style.strip()}">{esc(COPY[lang]["title"])}</h2><p>{esc(COPY[lang]["deck"])}</p><span>{esc(COPY[lang]["read"])} →</span></div></a>'''


def base_shelf() -> str:
    sections = []
    for lang in ("en", "zh", "zh-hant"):
        local = "hant" if lang == "zh-hant" else lang
        sections.append(f'<div class="lang-{local}">{shelf_body(lang, False)}</div>')
    description = "Original short science fiction by Han Qin, available in eight complete language editions."
    return f'''<!DOCTYPE html><html lang="zh-Hans" data-lang="zh" data-editions="en zh zh-hant">{head("zh", "index.html", description, False, "website")}<body class="site-shell-page explicit-hant">{shell("zh", "index.html", False)}<main class="shelf-wrap">{''.join(sections)}</main>{footer("../../", "zh")}</body></html>'''


def localized_shelf(lang: str) -> str:
    return f'''<!DOCTYPE html><html lang="{HTML_LANG[lang]}">{head(lang, "index.html", COPY[lang]["intro"], True, "website")}<body class="site-shell-page">{shell(lang, "index.html", True)}<main class="shelf-wrap">{shelf_body(lang, True)}</main>{footer("../../../", lang)}</body></html>'''


def serialize_updates(data: dict) -> str:
    lines = ["{", f'  "version": {json.dumps(data["version"], ensure_ascii=False)},', f'  "policy": {json.dumps(data["policy"], ensure_ascii=False)},', '  "updates": [']
    for index, item in enumerate(data["updates"]):
        comma = "," if index + 1 < len(data["updates"]) else ""
        lines.extend(["    {", f'      "id": {json.dumps(item["id"], ensure_ascii=False)},', f'      "date": {json.dumps(item["date"], ensure_ascii=False)},', f'      "kind": {json.dumps(item["kind"], ensure_ascii=False)},', f'      "domain": {json.dumps(item["domain"], ensure_ascii=False)},', f'      "url": {json.dumps(item["url"], ensure_ascii=False)},', f'      "languages": {json.dumps(item["languages"], ensure_ascii=False)},', f'      "title": {json.dumps(item["title"], ensure_ascii=False)},', f'      "summary": {json.dumps(item["summary"], ensure_ascii=False)}', f"    }}{comma}"])
    lines.extend(["  ]", "}"])
    return "\n".join(lines) + "\n"


def update_block(text: str, start: str, end: str, block: str, marker: str) -> str:
    if start in text:
        updated, count = re.subn(re.escape(start) + r".*?" + re.escape(end), block, text, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f"Could not refresh {start}")
        return updated
    if marker not in text:
        raise ValueError(f"Could not find insertion marker: {marker}")
    return text.replace(marker, block + "\n" + marker, 1)


def supporting_pages() -> dict[Path, str]:
    outputs: dict[Path, str] = {}
    originals_path = ROOT / "originals" / "index.html"
    originals = originals_path.read_text(encoding="utf-8")
    originals = originals.replace("Original fiction by Han Qin, beginning with short science fiction in English, Simplified Chinese, and Traditional Chinese.", "Original fiction by Han Qin, beginning with short science fiction in eight complete language editions.")
    originals = originals.replace("English · Simplified · Traditional", "8 complete language editions")
    originals = originals.replace("英文 · 简体 · 繁体", "8 种完整语言版本")
    originals = originals.replace("英文 · 簡體 · 繁體", "8 種完整語言版本")
    originals = originals.replace("Original fiction · EN / 简 / 繁", "Original fiction · 8 languages")
    originals = originals.replace("原创小说 · 英 / 简 / 繁", "原创小说 · 8 种语言")
    originals = originals.replace("原創小說 · 英 / 簡 / 繁", "原創小說 · 8 種語言")
    outputs[originals_path] = originals

    library_path = ROOT / "library.html"
    library = library_path.read_text(encoding="utf-8")
    library = library.replace("1 story · 3 reading modes", "1 story · 8 languages")
    library = library.replace("1 篇 · 英 / 简 / 繁", "1 篇 · 8 种语言")
    library = library.replace("1 篇 · 英 / 簡 / 繁", "1 篇 · 8 種語言")
    outputs[library_path] = library

    for lang in LANGS:
        path = ROOT / "essays" / lang / "index.html"
        text = path.read_text(encoding="utf-8")
        start = "<!-- MERGER DAY ORIGINAL START -->"
        end = "<!-- MERGER DAY ORIGINAL END -->"
        card = f'''{start}<a href="../../originals/short-science-fiction/{lang}/merger-day.html" class="essay-card" style="text-decoration:none;border-left:3px solid var(--gold);background:rgba(196,157,97,.04);display:block;padding:2rem 2.25rem;margin:2rem 0 1rem;"><div style="font-family:var(--sans);font-size:.65rem;letter-spacing:.13em;text-transform:uppercase;color:var(--gold);margin-bottom:.7rem;">{esc(COPY[lang]["channel_tag"])}</div><div style="font-size:1.55rem;color:var(--ink);margin-bottom:.6rem;">{esc(COPY[lang]["title"])}</div><p style="font-size:.94rem;color:var(--ink-light);line-height:1.75;max-width:700px;margin:0;">{esc(COPY[lang]["channel_desc"])}</p></a>{end}'''
        marker = '<div id="language-library" class="language-channel-library-anchor" aria-hidden="true"></div>'
        outputs[path] = update_block(text, start, end, card, marker)

    updates_path = ROOT / "data" / "site-updates.json"
    data = json.loads(updates_path.read_text(encoding="utf-8"))
    update = {"id": "2026-09-09-merger-day-definitive", "date": "2026-09-09", "kind": "expanded", "domain": "stories", "url": "originals/short-science-fiction/merger-day.html", "languages": list(ALL_LANGS), "title": {"en": "Merger Day · Definitive Edition", "zh": "《合并日》正式定稿", "zh-hant": "《合併日》正式定稿"}, "summary": {"en": "The first Non Dubito original story reaches its definitive text and eight complete literary editions; the expanded ending turns shared memory into a relationship that must be asked for, not merely transferred.", "zh": "Non Dubito 首篇原创小说完成正式定稿与八种语言版本；扩展后的结尾让共同记忆不再只是可传输的数据，而成为必须向另一个人询问的生活。", "zh-hant": "Non Dubito 首篇原創小說完成正式定稿與八種語言版本；擴展後的結尾讓共同記憶不再只是可傳輸的資料，而成為必須向另一個人詢問的生活。"}}
    found = next((i for i, item in enumerate(data["updates"]) if item["id"] == update["id"]), None)
    if found is None:
        data["updates"].insert(0, update)
    else:
        data["updates"][found] = update
    outputs[updates_path] = serialize_updates(data)

    latest_path = ROOT / "latest.html"
    latest = latest_path.read_text(encoding="utf-8")
    start = "<!-- MERGER DAY DEFINITIVE UPDATE START -->"
    end = "<!-- MERGER DAY DEFINITIVE UPDATE END -->"
    block = f'''{start}<section class="updates-day" aria-labelledby="date-2026-09-09-merger"><header class="updates-date"><div><p class="latest-date-label">Publication date</p><h2 id="date-2026-09-09-merger"><time datetime="2026-09-09"><span class="lang-en">9 September</span><span class="lang-zh">9 月 9 日</span><span class="lang-hant">9 月 9 日</span></time></h2></div><p class="lang-en">Non Dubito’s first original story reaches its definitive form.</p><p class="lang-zh">Non Dubito 的第一篇原创小说完成正式定稿。</p><p class="lang-hant">Non Dubito 的第一篇原創小說完成正式定稿。</p></header><div class="updates-grid"><article class="update-card" data-update-id="2026-09-09-merger-day-definitive"><div class="update-meta"><span class="update-kind"><span class="lang-en">Definitive edition</span><span class="lang-zh">正式定稿</span><span class="lang-hant">正式定稿</span></span><span class="update-languages">EN / 简 / 繁 / 日本語 / FR / DE / ES / 한국어</span></div><h3 class="lang-en">Merger Day</h3><h3 class="lang-zh">合并日</h3><h3 class="lang-hant">合併日</h3><p class="lang-en">The expanded final text and seven literary editions preserve the same quiet question: can shared memory replace a life another person actually lived?</p><p class="lang-zh">扩展后的定稿与七种文学重写共同留下同一个问题：共享的记忆，能否替代另一个人真正活过的生活？</p><p class="lang-hant">擴展後的定稿與七種文學重寫共同留下同一個問題：共享的記憶，能否替代另一個人真正活過的生活？</p><a href="originals/short-science-fiction/merger-day.html"><span class="lang-en">Read the story →</span><span class="lang-zh">阅读小说 →</span><span class="lang-hant">閱讀小說 →</span></a></article></div></section>{end}'''
    marker = '<section class="updates-day" aria-labelledby="date-2026-09-09">'
    outputs[latest_path] = update_block(latest, start, end, block, marker)
    return outputs


def render() -> dict[Path, str]:
    copy = load_copy()
    outputs = supporting_pages()
    outputs[SERIES / "merger-day.html"] = base_story(copy)
    outputs[SERIES / "index.html"] = base_shelf()
    for lang in LANGS:
        outputs[SERIES / lang / "merger-day.html"] = localized_story(lang, copy[lang])
        outputs[SERIES / lang / "index.html"] = localized_shelf(lang)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    stale = [path for path, text in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != text]
    if args.check:
        if stale:
            raise SystemExit("Stale Merger Day files:\n" + "\n".join(str(path.relative_to(ROOT)) for path in stale))
        print(f"OK: {len(outputs)} Merger Day files")
        return 0
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"Wrote: {len(outputs)} Merger Day files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
