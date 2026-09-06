#!/usr/bin/env python3
"""Build the six additional-language editions of Great Lives from edited copy.

The JSON files in data/great-lives are editorial source files, not machine
translations. This builder only handles repetitive HTML, navigation, and
series landing pages.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "essays" / "mingren"
DATA = ROOT / "data" / "great-lives"
LANGS = ("zh-hant", "ja", "fr", "de", "es", "ko")
HTML_LANG = {"zh-hant": "zh-Hant", "ja": "ja", "fr": "fr", "de": "de", "es": "es", "ko": "ko"}
LANG_LABEL = {"zh-hant": "繁體", "ja": "日本語", "fr": "Français", "de": "Deutsch", "es": "Español", "ko": "한국어"}
SERIES_NAME = {
    "zh-hant": "一百零八種人生", "ja": "Great Lives――108の生", "fr": "Grandes vies",
    "de": "Große Lebenswege", "es": "Grandes vidas", "ko": "위대한 삶들",
}
HERO_SUBTITLE = {
    "zh-hant": "一百零八種人生與尚未完成的目的王國",
    "ja": "108の生と、未完の目的の王国",
    "fr": "108 vies et un Royaume des fins inachevé",
    "de": "108 Leben und ein unvollendetes Reich der Zwecke",
    "es": "108 vidas y un Reino de los Fines inconcluso",
    "ko": "108개의 삶과 미완의 목적의 왕국",
}
MANIFESTO = {
    "zh-hant": "這不是名人錄，也不是替人生蓋棺論定的排行榜。一百零八種生命在這裡構成一條共同的路：成為自己，建立世界，遭遇自己所構之物的邊界，並學會為另一個人留下位置。「偉大」指的是尺度，而不是無罪。",
    "ja": "これは偉人を顕彰する名士録でも、人生に最終判決を下す本でもない。108の生を通して、一人の人間がどう自分になり、世界をつくり、その限界に出会い、他者のための場所を残せるのかをたどる。「偉大」とは影響の大きさであり、道徳的な無罪証明ではない。",
    "fr": "Ce n’est ni un panthéon ni un palmarès chargé de prononcer des verdicts définitifs. Cent huit vies dessinent un même trajet : devenir soi, faire un monde, rencontrer les limites de ce monde et apprendre à laisser une place à quelqu’un d’autre. « Grand » indique ici l’échelle, non l’innocence.",
    "de": "Dies ist weder eine Ruhmeshalle noch eine Rangliste abschließender Urteile. Hundertacht Leben bilden einen gemeinsamen Weg: zu sich selbst werden, eine Welt errichten, an deren Grenzen stoßen und einem anderen Menschen Raum lassen. „Groß“ bezeichnet hier den Maßstab, nicht moralische Unschuld.",
    "es": "Esto no es un salón de la fama ni una lista de veredictos definitivos. Ciento ocho vidas trazan un mismo recorrido: llegar a ser uno mismo, construir un mundo, encontrar sus límites y aprender a dejar sitio a otra persona. «Grande» nombra aquí la escala, no la inocencia.",
    "ko": "이것은 위인전도, 삶에 최종 판결을 내리는 순위표도 아니다. 108개의 삶은 하나의 여정을 이룬다. 자기 자신이 되고, 세계를 만들고, 그 세계의 한계를 만나며, 다른 사람을 위한 자리를 남기는 법을 배우는 여정이다. 여기서 ‘위대함’은 무죄가 아니라 규모를 뜻한다.",
}

MOVEMENTS = {
    1: {
        "range": (1, 9),
        "zh-hant": ("成為自己", "從老子到耶穌：當繼承來的答案不再足夠，一個人怎樣找到自己的方向，又不把它強加為所有人的法。"),
        "ja": ("自分になる", "老子からイエスまで。受け継いだ答えでは足りなくなったとき、人はいかに自分の方向を見つけ、それを万人の法として押しつけずにいられるのか。"),
        "fr": ("Devenir soi", "De Laozi à Jésus : trouver sa propre direction lorsque les réponses héritées ne suffisent plus, sans en faire la loi de tous."),
        "de": ("Zu sich selbst werden", "Von Laozi bis Jesus: eine eigene Richtung finden, wenn überlieferte Antworten nicht mehr genügen, ohne sie allen anderen aufzuzwingen."),
        "es": ("Llegar a ser uno mismo", "De Laozi a Jesús: encontrar una dirección propia cuando las respuestas heredadas ya no bastan, sin convertirla en ley para todos."),
        "ko": ("자기 자신이 되기", "노자에서 예수까지. 물려받은 답으로 충분하지 않을 때 자기 방향을 찾되, 그것을 모두의 법으로 강요하지 않는 길."),
    },
    2: {
        "range": (10, 23),
        "zh-hant": ("構成一個世界", "定理、帝國、科學、音樂與詩歌：人留下的世界往往比自己活得更久，也會暴露建造者未曾看見的裂縫。"),
        "ja": ("世界をつくる", "定理、帝国、科学、音楽、詩。人がつくった世界は本人より長く生き、その建設者が見なかった亀裂をさらす。"),
        "fr": ("Faire un monde", "Théorèmes, empires, sciences, musique et poésie : les mondes construits survivent souvent à leurs auteurs et révèlent des fissures qu’ils n’avaient pas vues."),
        "de": ("Eine Welt errichten", "Theoreme, Reiche, Wissenschaften, Musik und Dichtung: Gebaute Welten überleben ihre Urheber und zeigen Risse, die diese nicht sehen konnten."),
        "es": ("Construir un mundo", "Teoremas, imperios, ciencias, música y poesía: lo construido suele sobrevivir a quien lo hizo y revelar grietas que su autor no alcanzó a ver."),
        "ko": ("하나의 세계 만들기", "정리, 제국, 과학, 음악과 시. 사람이 만든 세계는 만든 이보다 오래 살며, 그가 보지 못한 균열까지 드러낸다."),
    },
    3: {
        "range": (24, 41),
        "zh-hant": ("當世界反過來塑造人", "無意識、制度、權力、信仰與語言進入人的內部；有人被吞沒，有人在縫隙裡保住不可取代的位置。"),
        "ja": ("世界が人をつくり返すとき", "無意識、制度、権力、信仰、言語が人の内側に入る。呑み込まれる者もいれば、隙間に代えのきかない場所を守る者もいる。"),
        "fr": ("Quand le monde nous refaçonne", "L’inconscient, les institutions, le pouvoir, la foi et la langue entrent en nous. Certains sont engloutis ; d’autres préservent une place irremplaçable."),
        "de": ("Wenn die Welt den Menschen zurückformt", "Unbewusstes, Institutionen, Macht, Glaube und Sprache dringen in den Menschen ein. Manche werden verschlungen; andere bewahren einen unersetzbaren Ort."),
        "es": ("Cuando el mundo nos rehace", "El inconsciente, las instituciones, el poder, la fe y el lenguaje entran en la persona. Algunos son devorados; otros conservan un lugar irreemplazable."),
        "ko": ("세계가 사람을 되빚을 때", "무의식, 제도, 권력, 신앙과 언어가 사람 안으로 들어온다. 누군가는 삼켜지고, 누군가는 틈에서 대체 불가능한 자리를 지킨다."),
    },
    4: {
        "range": (42, 60),
        "zh-hant": ("真理的邊界畫在哪裡", "從聲音成為文字，到理念、因果、意志、計算與存在：每次劃界都使世界更清楚，也把某些事物留在界外。"),
        "ja": ("真理の線をどこに引くか", "声が文字になる瞬間から、形、因果、意志、計算、存在へ。境界は世界を明瞭にしながら、何かを外に残す。"),
        "fr": ("Tracer les frontières du vrai", "De la voix devenue texte aux formes, aux causes, à la volonté, au calcul et à l’existence : chaque frontière éclaire et laisse quelque chose dehors."),
        "de": ("Die Linien der Wahrheit ziehen", "Von der Stimme als Schrift über Form, Ursache, Wille, Berechnung und Sein: Jede Grenze klärt die Welt und lässt zugleich etwas draußen."),
        "es": ("Trazar los límites de la verdad", "De la voz convertida en texto a la forma, la causa, la voluntad, el cálculo y el ser: cada frontera aclara el mundo y deja algo fuera."),
        "ko": ("진리의 경계 긋기", "목소리가 글이 되는 순간에서 형상, 인과, 의지, 계산과 존재까지. 경계는 세계를 선명하게 만들면서 무엇인가를 밖에 남긴다."),
    },
    5: {
        "range": (61, 78),
        "zh-hant": ("生命之後留下的工作", "手、光、火、夢、顏色與制度：不只看一個人完成了什麼，也看作品離開作者以後繼續做了什麼。"),
        "ja": ("生のあとに残る仕事", "手、光、火、夢、色、制度。何を完成したかだけでなく、作品が作者を離れたあと何をし続けるかを見る。"),
        "fr": ("L’œuvre après la vie", "Mains, lumière, feu, rêves, couleurs et institutions : non seulement ce qu’une personne accomplit, mais ce que son œuvre continue de faire après elle."),
        "de": ("Arbeit, die ein Leben überdauert", "Hände, Licht, Feuer, Träume, Farbe und Institutionen: nicht nur, was jemand schuf, sondern was das Werk nach seinem Urheber weiter tut."),
        "es": ("La obra que sobrevive a una vida", "Manos, luz, fuego, sueños, color e instituciones: no sólo lo que alguien hizo, sino lo que su obra sigue haciendo cuando ya no está."),
        "ko": ("삶 뒤에 남는 작업", "손, 빛, 불, 꿈, 색과 제도. 한 사람이 무엇을 완성했는지뿐 아니라, 작품이 그를 떠난 뒤에도 무엇을 하는지 본다."),
    },
    6: {
        "range": (79, 96),
        "zh-hant": ("我們怎樣知道", "從『只有能說出的才算知識』走到『說不出的是知識的地基』：認知不是封閉判決，而是不斷重開的循環。"),
        "ja": ("私たちはどう知るのか", "「語れるものだけが知識」から「語れないものが知識の地盤」へ。知ることは閉じた判決ではなく、開き直される循環になる。"),
        "fr": ("Comment nous savons", "De « seul l’articulable est savoir » à « l’inarticulé est le sol du savoir » : connaître devient un cycle qui se rouvre, non un verdict fermé."),
        "de": ("Wie wir wissen", "Von „Nur Aussprechbares ist Wissen“ zu „Unaussprechliches ist der Boden des Wissens“: Erkennen wird zum wieder geöffneten Kreislauf statt zum Urteil."),
        "es": ("Cómo sabemos", "De «sólo lo articulable es conocimiento» a «lo inarticulado es su suelo»: conocer es un ciclo que vuelve a abrirse, no un veredicto cerrado."),
        "ko": ("우리는 어떻게 아는가", "‘말할 수 있어야 지식이다’에서 ‘말할 수 없는 것이 지식의 바닥이다’로. 앎은 닫힌 판결이 아니라 다시 열리는 순환이다."),
    },
    7: {
        "range": (97, 108),
        "zh-hant": ("他者與空位", "十二種為他者留下位置的語言匯入橋上的空位；它不屬於名人，而在一個人同時把自己與他者當作目的時出現。"),
        "ja": ("他者と空席", "他者に場所を残す十二の言葉が橋の空席に集まる。名士に与えられる席ではなく、自他を目的として扱う瞬間に現れる。"),
        "fr": ("L’autre et la place vide", "Douze manières de laisser place à autrui convergent vers un siège vide : il apparaît lorsque quelqu’un traite soi et l’autre comme des fins."),
        "de": ("Der Andere und der leere Platz", "Zwölf Sprachen des Raumlassens führen zum leeren Platz auf der Brücke. Er erscheint, wenn jemand sich und den Anderen als Zwecke behandelt."),
        "es": ("El otro y el asiento vacío", "Doce maneras de dejar sitio al otro convergen en un asiento vacío: aparece cuando alguien trata al yo y al otro como fines."),
        "ko": ("타자와 빈자리", "타자에게 자리를 남기는 열두 언어가 다리 위 빈자리로 모인다. 자신과 타자를 모두 목적으로 대하는 순간에 나타나는 자리다."),
    },
}


def canonical_order() -> list[dict[str, object]]:
    text = (SERIES / "index.html").read_text(encoding="utf-8")
    matches = re.findall(
        r'<a href="([^"]+)" class="great-life-card"[^>]*>\s*<span class="life-number">(\d+)</span>',
        text,
    )
    if len(matches) != 108:
        raise ValueError(f"Expected 108 canonical cards, found {len(matches)}")
    return [{"slug": Path(href).stem, "source": href, "number": int(number)} for href, number in matches]


def load_copy() -> dict[str, dict[str, object]]:
    entries: dict[str, dict[str, object]] = {}
    for path in sorted(DATA.glob("movement-*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for entry in payload["entries"]:
            slug = entry["slug"]
            if slug in entries:
                raise ValueError(f"Duplicate Great Lives copy: {slug}")
            missing = set(LANGS) - set(entry["copy"])
            if missing:
                raise ValueError(f"{slug} is missing: {', '.join(sorted(missing))}")
            for lang in LANGS:
                sections = entry["copy"][lang].get("sections", [])
                if len(sections) != 4:
                    raise ValueError(f"{slug}/{lang} needs exactly four sections")
            entries[slug] = entry
    return entries


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def language_switcher(lang: str, slug: str | None = None) -> str:
    links = []
    source = f"../{slug}.html" if slug else "../index.html"
    links.append(f'<a href="{source}">EN / 中文</a>')
    for code in LANGS:
        if code == lang:
            links.append(f'<span class="active">{LANG_LABEL[code]}</span>')
        else:
            target = f"../{code}/{slug}.html" if slug else f"../{code}/index.html"
            links.append(f'<a href="{target}">{LANG_LABEL[code]}</a>')
    return '<span class="sep">|</span>'.join(links)


def source_page_with_languages(path: Path, slug: str) -> str:
    """Add direct links to the six editions without touching essay copy."""
    text = path.read_text(encoding="utf-8")
    links = [
        '<button class="lang-btn" data-lang="zh">中文</button>',
        '<button class="lang-btn" data-lang="en">EN</button>',
    ]
    links.extend(
        f'<a class="lang-btn" href="{lang}/{slug}.html">{LANG_LABEL[lang]}</a>'
        for lang in LANGS
    )
    toggle = '\n          ' + '\n          <span class="lang-sep">|</span>'.join(links) + '\n        '
    updated, count = re.subn(
        r'(?s)(<div class="lang-toggle">).*?(</div>)',
        lambda match: match.group(1) + toggle + match.group(2),
        text,
        count=1,
    )
    if count != 1:
        raise ValueError(f"Could not locate source language toggle in {path}")
    return updated


def extract_title(path: Path) -> str:
    match = re.search(r"<h1>(.*?)</h1>", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise ValueError(f"No h1 in {path}")
    return re.sub(r"<[^>]+>", "", match.group(1)).strip()


def article_html(lang: str, entry: dict[str, object], order: list[dict[str, object]], available: set[str], all_copy: dict[str, dict[str, object]]) -> str:
    slug = str(entry["slug"])
    number = int(entry["number"])
    movement = int(entry["movement"])
    copy = entry["copy"][lang]
    movement_name = MOVEMENTS[movement][lang][0]
    title = copy["title"]
    deck = copy["deck"]
    source = next(item["source"] for item in order if item["slug"] == slug)
    source_href = f"../{Path(str(source)).name}"
    completed = [item for item in order if item["slug"] in available]
    position = next(i for i, item in enumerate(completed) if item["slug"] == slug)
    prev_item = completed[position - 1] if position else None
    next_item = completed[position + 1] if position + 1 < len(completed) else None

    def nav_item(item: dict[str, object] | None, previous: bool) -> str:
        if item is None:
            return "<span></span>"
        item_slug = str(item["slug"])
        if item_slug in all_copy:
            name = all_copy[item_slug]["copy"][lang]["title"]
        else:
            name = extract_title(SERIES / lang / f"{item_slug}.html")
        labels = {
            "zh-hant": ("← 上一篇", "下一篇 →"), "ja": ("← 前の篇", "次の篇 →"),
            "fr": ("← Essai précédent", "Essai suivant →"), "de": ("← Voriger Essay", "Nächster Essay →"),
            "es": ("← Ensayo anterior", "Ensayo siguiente →"), "ko": ("← 이전 글", "다음 글 →"),
        }
        return f'<a href="{item["slug"]}.html"><small>{labels[lang][0 if previous else 1]}</small>{esc(name)}</a>'

    sections = "".join(
        f'<section><h2>{esc(section["heading"])}</h2>'
        + "".join(f'<p>{esc(paragraph)}</p>' for paragraph in section["paragraphs"])
        + "</section>"
        for section in copy["sections"]
    )
    notes = {
        "zh-hant": "依據中英文原作編輯的繁體閱讀版。史料、引文與詳細註釋參見",
        "ja": "中国語・英語版を基に、日本語の読者に向けて独立に再構成したエッセイ。史料と詳注は",
        "fr": "Réécriture française indépendante. Sources, citations et notes détaillées dans l’",
        "de": "Eigenständige deutsche Neufassung. Quellen, Zitate und ausführliche Anmerkungen in der",
        "es": "Reescritura española independiente. Fuentes, citas y notas detalladas en la",
        "ko": "중문·영문 원작을 바탕으로 한국어 독자에게 맞게 독립적으로 재구성한 글이다. 사료와 상세 주석은",
    }
    note_link = {
        "zh-hant": "中英文原版", "ja": "原版", "fr": "édition chinoise et anglaise",
        "de": "chinesisch-englischen Originalausgabe", "es": "edición china e inglesa", "ko": "중문·영문 원판",
    }
    canonical = f"https://nondubito.net/essays/mingren/{lang}/{slug}.html"
    return f'''<!DOCTYPE html>
<html lang="{HTML_LANG[lang]}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{esc(title)} · {esc(SERIES_NAME[lang])} — Non Dubito</title>
<meta name="description" content="{esc(deck)}">
<link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="../../../style.css">
<link rel="stylesheet" href="../great-lives-edition.css?v=20260906">
<link rel="icon" href="../../../favicon.svg" type="image/svg+xml">
</head>
<body>
<header><div class="header-inner"><a href="../../../index.html" class="site-title"><span class="title-latin">Non <span style="color:var(--gold)">Dubito</span></span><span class="title-sub">Essays in the Self-as-an-End Tradition</span></a></div></header>
<main class="great-edition-main">
<div class="great-edition-switcher">{language_switcher(lang, slug)}</div>
<a class="great-edition-back" href="index.html">← {esc(SERIES_NAME[lang])}</a>
<header class="great-edition-header"><p class="great-edition-series">{number:03d} / 108 · {esc(movement_name)}</p><h1>{esc(title)}</h1><p class="great-edition-deck">{esc(deck)}</p></header>
<div class="great-edition-body">{sections}</div>
<nav class="great-edition-nav">{nav_item(prev_item, True)}{nav_item(next_item, False)}</nav>
<p class="great-edition-note">{notes[lang]} <a href="{source_href}">{note_link[lang]}</a>。</p>
</main>
</body>
</html>
'''


def index_html(lang: str, order: list[dict[str, object]], available: set[str], all_copy: dict[str, dict[str, object]]) -> str:
    count = len(available)
    movements = []
    for movement, info in MOVEMENTS.items():
        start, end = info["range"]
        items = [item for item in order if start <= int(item["number"]) <= end and item["slug"] in available]
        if not items:
            continue
        cards_list = []
        for item in items:
            slug = str(item["slug"])
            if slug in all_copy:
                title = all_copy[slug]["copy"][lang]["title"]
            else:
                title = extract_title(SERIES / lang / f"{slug}.html")
            cards_list.append(
                f'<a class="great-edition-card" href="{slug}.html"><span class="num">{int(item["number"]):03d}</span><span class="title">{esc(title)}</span><span class="arrow">→</span></a>'
            )
        cards = "".join(cards_list)
        name, desc = info[lang]
        movements.append(
            f'<section class="great-edition-movement"><span class="great-edition-movement-label">{movement:02d} · {start:03d}–{end:03d}</span><h2>{esc(name)}</h2><p>{esc(desc)}</p><div class="great-edition-grid">{cards}</div></section>'
        )
    next_movement = next((m for m, info in MOVEMENTS.items() if any(item["slug"] not in available for item in order if info["range"][0] <= int(item["number"]) <= info["range"][1])), None)
    status = {
        "zh-hant": f"繁體版依照七個樂章陸續刊行；目前已完成 {count} 篇。",
        "ja": f"日本語版は七つの楽章に沿って刊行する。現在{count}篇を公開済み。",
        "fr": f"L’édition française paraît en sept mouvements ; {count} essais sont désormais disponibles.",
        "de": f"Die deutsche Ausgabe erscheint in sieben Bewegungen; {count} Essays sind jetzt verfügbar.",
        "es": f"La edición española avanza en siete movimientos; ya están disponibles {count} ensayos.",
        "ko": f"한국어판은 일곱 악장에 따라 이어진다. 현재 {count}편을 공개했다.",
    }
    if next_movement:
        nxt = MOVEMENTS[next_movement][lang][0]
        coming = {
            "zh-hant": f"下一樂章：{nxt}", "ja": f"次の楽章：{nxt}", "fr": f"Mouvement suivant : {nxt}",
            "de": f"Nächste Bewegung: {nxt}", "es": f"Siguiente movimiento: {nxt}", "ko": f"다음 악장: {nxt}",
        }[lang]
        tail = f'<div class="great-edition-coming"><strong>{esc(coming)}</strong></div>'
    else:
        complete = {
            "zh-hant": "七個樂章 · 一百零八種人生 · 全部完成", "ja": "全七楽章・108篇 完結",
            "fr": "Sept mouvements · 108 vies · Édition complète", "de": "Sieben Bewegungen · 108 Leben · Vollständige Ausgabe",
            "es": "Siete movimientos · 108 vidas · Edición completa", "ko": "일곱 악장 · 108개의 삶 · 전편 완성",
        }[lang]
        tail = f'<div class="great-edition-coming"><strong>{esc(complete)}</strong></div>'
    canonical = f"https://nondubito.net/essays/mingren/{lang}/"
    alternates = ''.join(
        f'<link rel="alternate" hreflang="{code}" href="{url}">'
        for code, url in [
            ("en", "https://nondubito.net/essays/mingren/"), ("zh-Hans", "https://nondubito.net/essays/mingren/"),
            ("zh-Hant", "https://nondubito.net/essays/mingren/zh-hant/"), ("ja", "https://nondubito.net/essays/mingren/ja/"),
            ("fr", "https://nondubito.net/essays/mingren/fr/"), ("de", "https://nondubito.net/essays/mingren/de/"),
            ("es", "https://nondubito.net/essays/mingren/es/"), ("ko", "https://nondubito.net/essays/mingren/ko/"),
            ("x-default", "https://nondubito.net/essays/mingren/"),
        ]
    )
    return f'''<!DOCTYPE html>
<html lang="{HTML_LANG[lang]}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{esc(SERIES_NAME[lang])} — Non Dubito</title>
<meta name="description" content="{esc(HERO_SUBTITLE[lang])}">
<link rel="canonical" href="{canonical}">{alternates}
<link rel="stylesheet" href="../../../style.css">
<link rel="stylesheet" href="../great-lives-edition.css?v=20260906">
<link rel="icon" href="../../../favicon.svg" type="image/svg+xml">
</head>
<body>
<header><div class="header-inner"><a href="../../../index.html" class="site-title"><span class="title-latin">Non <span style="color:var(--gold)">Dubito</span></span><span class="title-sub">Essays in the Self-as-an-End Tradition</span></a><nav><a href="../../../start.html">Start Here</a><a href="../../../explore.html">Explore</a><a href="../../../latest.html">Latest</a><a href="../../../about.html">About</a></nav></div></header>
<main class="great-edition-main">
<div class="great-edition-switcher">{language_switcher(lang)}</div>
<section class="great-edition-index-hero"><p class="great-edition-series">Non Dubito · 108</p><h1>{esc(SERIES_NAME[lang])}</h1><p class="subtitle">{esc(HERO_SUBTITLE[lang])}</p><p class="manifesto">{esc(MANIFESTO[lang])}</p></section>
<div class="great-edition-progress"><strong>{count:02d} / 108</strong><p>{esc(status[lang])}</p></div>
{''.join(movements)}{tail}
</main>
</body>
</html>
'''


def build() -> dict[Path, str]:
    order = canonical_order()
    copy = load_copy()
    available = {item["slug"] for item in order[:9]} | set(copy)
    expected_prefix = {item["slug"] for item in order[: len(available)]}
    if available != expected_prefix:
        missing = expected_prefix - available
        extra = available - expected_prefix
        raise ValueError(f"Language release must stay contiguous; missing={missing}, extra={extra}")
    outputs: dict[Path, str] = {}
    by_slug = {item["slug"]: item for item in order}
    for slug, entry in copy.items():
        if int(entry["number"]) != int(by_slug[slug]["number"]):
            raise ValueError(f"Canonical number mismatch for {slug}")
        for lang in LANGS:
            outputs[SERIES / lang / f"{slug}.html"] = article_html(lang, entry, order, available, copy)
        source_path = (SERIES / str(by_slug[slug]["source"])).resolve()
        if source_path.parent != SERIES:
            raise ValueError(f"Unexpected source location for generated edition: {source_path}")
        outputs[source_path] = source_page_with_languages(source_path, slug)
    for lang in LANGS:
        outputs[SERIES / lang / "index.html"] = index_html(lang, order, available, copy)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build()
    stale = []
    for path, content in outputs.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            stale.append(path)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    if args.check and stale:
        for path in stale[:20]:
            print(f"ERROR: stale Great Lives page: {path.relative_to(ROOT)}")
        return 1
    print(f"{'OK' if args.check else 'Wrote'}: {len(outputs)} Great Lives language pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
