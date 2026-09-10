#!/usr/bin/env python3
"""Publish game-criticism series 14–17 in English, Simplified, and Traditional Chinese."""
from __future__ import annotations

import html
import re
from pathlib import Path

from import_film_50_59 import TC, footer, head, header, md, split_en, tcjs, toggle


ROOT = Path(__file__).resolve().parents[1]
SRC = Path("/Users/hanqin/Documents/SAE解读/游戏解读")
DATA = ROOT / "data/games-14-17"
OUT = ROOT / "essays/games"

CFG = [
    {
        "n": 14,
        "slug": "frostpunk",
        "source": "冰汽时代",
        "zh": "冰汽时代",
        "en": "Frostpunk",
        "desc_en": "Four essays on the Book of Laws, choices that create the need for further control, the functional symmetry of Order and Faith, and a final line drawn at the abolition of dissent.",
        "desc_zh": "四篇从法典与管理者的视野，读到选择怎样制造下一次选择、秩序与信仰怎样走进同一个房间，以及游戏为何把线画在“人还能不能说不”这里。",
        "files": ["1-the-book-of-laws", "2-every-law-solves-the-last-law", "3-the-same-room", "4-where-the-line-is-drawn"],
        "note_en": "Based on 11 bit studios’ 2018 Frostpunk and its original scenarios, including A New Home and The Fall of Winterhome; later expansions are outside the scope of this series. Full spoilers throughout.",
    },
    {
        "n": 15,
        "slug": "journey",
        "source": "风之旅人",
        "zh": "风之旅人",
        "en": "Journey",
        "desc_en": "Three essays on a language made from one note, the harmful action removed after playtesting, and a mountain where companionship matters without being able to prevent loss.",
        "desc_zh": "三篇从只有一个音的语言，读到开发者为何删掉“推”与第三个人，以及雪山如何让陪伴在无力改变结局时仍然成立。",
        "files": ["1-one-note", "2-he-removed-the-push-button", "3-the-mountain-and-the-credits"],
        "note_en": "Based on thatgamecompany’s 2012 Journey, directed by Jenova Chen with music by Austin Wintory. Development claims draw on public talks and interviews. Full spoilers throughout.",
    },
    {
        "n": 16,
        "slug": "sky-children-of-the-light",
        "source": "光·遇",
        "zh": "光·遇",
        "en": "Sky: Children of the Light",
        "desc_en": "Four essays on social capacities given a price, the trust inside holding hands, exclusion without malice, and an endgame that turns accumulation into something one must give away.",
        "desc_zh": "四篇从被定价的交往与牵手里的信任，读到没有恶意也会形成的排斥，以及献祭怎样把一路积累的能力变成必须交出去的东西。",
        "files": ["1-he-put-a-price-on-it", "2-holding-hands", "3-the-ellipsis", "4-the-sacrifice"],
        "note_en": "Based on thatgamecompany’s evolving live-service game Sky: Children of the Light. Discussion of the friendship tree chiefly concerns the long-running 2019–2026 system before the 2026 tier redesign. Full spoilers throughout.",
    },
    {
        "n": 17,
        "slug": "civilization",
        "source": "文明",
        "zh": "文明",
        "en": "Civilization",
        "desc_en": "Four essays on citizens reduced to assignable output, the resistance preserved as Happiness and Loyalty, the player’s conversion of refusal into a tool, and the historical road drawn by a technology tree.",
        "desc_zh": "四篇从被压成产出的市民，读到快乐度与忠诚度保存的那一点“不肯”、玩家如何把它再变成工具，以及科技树替历史画出的共同道路。",
        "files": ["1-one-settler", "2-happiness-pushes-back", "3-players-learned-to-use-it", "4-the-people-who-have-names"],
        "note_en": "Centered on Civilization V (2010) and Civilization VI (2016), with earlier installments noted where relevant; Civilization VII is outside the scope of this series. Full spoilers for game systems.",
    },
]

ROMAN = ("I", "II", "III", "IV")


def zh_docs(source_name: str) -> list[tuple[str, str]]:
    result = []
    for path in sorted((SRC / source_name).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        first = text.splitlines()[0].removeprefix("# ").strip()
        title = first.split("：", 1)[1] if "：" in first else first
        result.append((title, "\n".join(text.splitlines()[1:]).strip()))
    return result


def first_paragraph(markdown: str) -> str:
    for block in re.split(r"\n\s*\n", markdown.strip()):
        block = block.strip()
        if block and not block.startswith("#"):
            clean = re.sub(r"[*_`]", "", re.sub(r"\s+", " ", block))
            return clean[:220]
    return ""


def series_card(cfg: dict, prefix: str = "") -> str:
    count = len(cfg["files"])
    return (
        f'<a href="{prefix}{cfg["slug"]}/index.html" class="series-card">'
        f'<span class="series-card-count">No. {cfg["n"]:02d} · {count} essays</span>'
        f'<div class="series-card-title-zh">《{cfg["zh"]}》解读</div>'
        f'<div class="series-card-title-en">Reading {html.escape(cfg["en"])}</div>'
        f'<p class="series-card-desc-zh lang-zh">{cfg["desc_zh"]}</p>'
        f'<p class="series-card-desc-en lang-en">{html.escape(cfg["desc_en"])}</p>'
        '<span class="series-card-arrow lang-en">Read series</span>'
        '<span class="series-card-arrow lang-zh">阅读系列</span></a>'
    )


def write_pages(converter: TC) -> None:
    for cfg in CFG:
        english = split_en(DATA / f'{cfg["slug"] if cfg["slug"] != "sky-children-of-the-light" else "sky"}.en.md')
        chinese = zh_docs(cfg["source"])
        assert len(english) == len(chinese) == len(cfg["files"]), (cfg["slug"], len(english), len(chinese))

        folder = OUT / cfg["slug"]
        (folder / "zh-hant-data").mkdir(parents=True, exist_ok=True)
        cards = "".join(
            f'<a href="{cfg["files"][i]}.html" class="essay-card"><span class="card-num">{ROMAN[i]}</span>'
            f'<div class="card-body"><div class="card-lang-tag"><span class="lang-en">English · Simplified / Traditional · Game criticism</span><span class="lang-zh">英文 · 简 / 繁 · 游戏解读</span></div>'
            f'<div class="card-title-en">{html.escape(english[i][0])}</div>'
            f'<div class="card-title-zh" style="font-family:var(--cjk),serif;">{html.escape(chinese[i][0])}</div>'
            '<div class="card-meta"><span>2026</span><span class="card-badge full">Three reading modes</span></div>'
            '</div></a>'
            for i in range(len(cfg["files"]))
        )

        url = f'https://nondubito.net/essays/games/{cfg["slug"]}/'
        hero = (
            toggle()
            + '<a href="../index.html" class="back-link"><span class="lang-en">← Games</span><span class="lang-zh">← 游戏解读</span></a>'
            + f'<div class="essay-page-num"><span class="lang-en">Series · {len(cfg["files"])} essays · Game criticism</span>'
            + f'<span class="lang-zh">系列 · {len(cfg["files"])} 篇解读 · 游戏评论</span></div>'
            + f'<h1 class="essay-page-title lang-en">Reading {html.escape(cfg["en"])}</h1>'
            + f'<h1 class="essay-page-title zh lang-zh" style="font-family:var(--cjk),serif;">《{cfg["zh"]}》解读</h1>'
            + '<div class="essay-page-meta"><span>Sep 9, 2026</span><span>Han Qin (秦汉)</span>'
            + '<span class="lang-en">English · Simplified · Traditional</span><span class="lang-zh">英文 · 简体 · 繁体</span></div>'
        )
        page = (
            '<!DOCTYPE html><html lang="zh-Hans" data-lang="zh"><head>'
            + head(f'Reading {cfg["en"]}', cfg["desc_en"], url, "index.js")
            + '</head><body>' + header()
            + f'<div class="essay-page"><div class="essay-page-hero"><div class="essay-page-inner">{hero}</div></div>'
            + f'<div class="essay-body lang-en"><p style="font-size:1.2rem;line-height:1.9;">{html.escape(cfg["desc_en"])}</p><div class="essay-list" style="margin-top:3rem;">{cards}</div></div>'
            + f'<div class="essay-body lang-zh" style="font-family:var(--cjk),serif;"><p style="font-size:1.2rem;line-height:1.9;">{cfg["desc_zh"]}</p><div class="essay-list" style="margin-top:3rem;">{cards}</div></div>'
            + '</div>' + footer() + '</body></html>'
        )
        (folder / "index.html").write_text(page, encoding="utf-8")
        (folder / "zh-hant-data/index.js").write_text(tcjs(page, converter), encoding="utf-8")

        for i, filename in enumerate(cfg["files"]):
            article_url = url + filename + ".html"
            prev = (
                f'<a href="{cfg["files"][i-1]}.html"><span class="lang-en">← Previous</span><span class="lang-zh">← 上一篇</span></a>'
                if i
                else '<a href="index.html"><span class="lang-en">← Series overview</span><span class="lang-zh">← 系列总览</span></a>'
            )
            nxt = (
                f'<a href="{cfg["files"][i+1]}.html"><span class="lang-en">Next →</span><span class="lang-zh">下一篇 →</span></a>'
                if i + 1 < len(cfg["files"])
                else '<a href="index.html"><span class="lang-en">Series overview →</span><span class="lang-zh">系列总览 →</span></a>'
            )
            article_hero = (
                toggle()
                + f'<a href="index.html" class="back-link"><span class="lang-en">← Reading {html.escape(cfg["en"])}</span><span class="lang-zh">← 《{cfg["zh"]}》解读</span></a>'
                + f'<div class="essay-page-num"><span class="lang-en">Essay {i + 1} of {len(cfg["files"])} · {html.escape(cfg["en"])}</span>'
                + f'<span class="lang-zh">《{cfg["zh"]}》解读 · {i + 1} / {len(cfg["files"])}</span></div>'
                + f'<h1 class="essay-page-title lang-en">{html.escape(english[i][0])}</h1>'
                + f'<h1 class="essay-page-title zh lang-zh" style="font-family:var(--cjk),serif;">{html.escape(chinese[i][0])}</h1>'
                + '<div class="essay-page-meta"><span>Sep 9, 2026</span><span>Han Qin (秦汉)</span>'
                + '<span class="lang-en">Independent English edition</span><span class="lang-zh">中文原作 · 简 / 繁</span></div>'
            )
            description = first_paragraph(english[i][1])
            article = (
                '<!DOCTYPE html><html lang="zh-Hans" data-lang="zh"><head>'
                + head(english[i][0], description, article_url, filename + ".js")
                + '</head><body>' + header()
                + f'<div class="essay-page"><div class="essay-page-hero"><div class="essay-page-inner">{article_hero}</div></div>'
                + '<div class="essay-body lang-en"><p style="font-family:var(--sans);font-size:.72rem;color:var(--ink-muted);border-bottom:1px solid var(--cream-border);padding-bottom:1.25rem;">'
                + '<strong>Edition note:</strong> Independent English rewriting for English-language readers; mechanics and development claims have been checked.</p>'
                + md(english[i][1])
                + f'<p style="font-size:.95rem;color:var(--ink-muted);border-top:1px solid var(--cream-border);padding-top:1.5rem;margin-top:3rem;"><em>{html.escape(cfg["note_en"])}</em></p></div>'
                + '<div class="essay-body lang-zh" style="font-family:var(--cjk),serif;"><p style="font-family:var(--sans);font-size:.72rem;color:var(--ink-muted);border-bottom:1px solid var(--cream-border);padding-bottom:1.25rem;">'
                + '<strong>版本说明：</strong>中文原作；简体与繁体同页切换。机制与开发资料已校订。</p>'
                + md(chinese[i][1]) + '</div>'
                + f'<div style="max-width:700px;margin:0 auto;padding:2rem 2.5rem 4rem;display:flex;justify-content:space-between;gap:1rem;">{prev}{nxt}</div></div>'
                + footer() + '</body></html>'
            )
            (folder / f"{filename}.html").write_text(article, encoding="utf-8")
            (folder / "zh-hant-data" / f"{filename}.js").write_text(tcjs(article, converter), encoding="utf-8")


def update_indexes() -> None:
    path = OUT / "index.html"
    source = path.read_text(encoding="utf-8")
    replacements = {
        "Thirteen series · Fifty-one essays · Three reading modes": "Seventeen series · Sixty-six essays · Three reading modes",
        "十三个系列 · 五十一篇 · 英 / 简 / 繁": "十七个系列 · 六十六篇 · 英 / 简 / 繁",
        "Game library · Series 01–13": "Game library · Series 01–17",
        "游戏目录 · 系列 01–13": "游戏目录 · 系列 01–17",
        "Aug 30, 2026": "Sep 9, 2026",
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    for cfg in CFG:
        if f'href="{cfg["slug"]}/index.html"' not in source:
            source = source.replace('</div></section></div><footer>', series_card(cfg) + '</div></section></div><footer>')
    path.write_text(source, encoding="utf-8")

    library = ROOT / "library.html"
    source = library.read_text(encoding="utf-8")
    start = source.index('<hr class="lib-divider" data-games-channel>')
    end = source.index('<hr class="lib-divider" data-tv-channel>', start)
    block = source[start:end]
    for cfg in CFG:
        if f'essays/games/{cfg["slug"]}/index.html' not in block:
            block = block.replace('\n  </div>\n</section>', '\n    ' + series_card(cfg, "essays/games/") + '\n  </div>\n</section>')
    library.write_text(source[:start] + block + source[end:], encoding="utf-8")

    latest = ROOT / "latest.html"
    source = latest.read_text(encoding="utf-8")
    marker = '<section class="updates-section"><div class="latest-inner">'
    if 'data-update-id="2026-09-09-games-14-17"' not in source:
        section = '''<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-2026-09-09-games"><header class="updates-date"><div><p class="latest-date-label">Publication date</p><h2 id="date-2026-09-09-games"><time datetime="2026-09-09"><span class="lang-en">9 September</span><span class="lang-zh">9 月 9 日</span><span class="lang-hant">9 月 9 日</span></time></h2></div><p class="lang-en">Four game worlds join the shelf through fifteen independently edited readings.</p><p class="lang-zh">游戏区新增四部作品、十五篇独立审校的解读。</p><p class="lang-hant">遊戲區新增四部作品、十五篇獨立審校的解讀。</p></header><div class="updates-grid"><article class="update-card" data-update-id="2026-09-09-games-14-17"><div class="update-meta"><span class="update-kind"><span class="lang-en">Four new series</span><span class="lang-zh">四部新系列</span><span class="lang-hant">四部新系列</span></span><span class="update-languages">15 essays · EN / 简 / 繁</span></div><h3 class="lang-en">Frostpunk, Journey, Sky, and Civilization</h3><h3 class="lang-zh">《冰汽时代》《风之旅人》《光·遇》《文明》</h3><h3 class="lang-hant">《冰汽時代》《風之旅人》《光·遇》《文明》</h3><p class="lang-en">Fifteen essays read laws, movement, social systems, accumulation, and refusal as arguments the player must perform.</p><p class="lang-zh">十五篇把法典、移动、社交系统、积累与拒绝都当成需要玩家亲手完成的论证。</p><p class="lang-hant">十五篇把法典、移動、社交系統、積累與拒絕都當成需要玩家親手完成的論證。</p><a href="essays/games/index.html"><span class="lang-en">Enter Games →</span><span class="lang-zh">进入游戏解读 →</span><span class="lang-hant">進入遊戲解讀 →</span></a></article></div></section></div></section>\n\n    '''
        source = source.replace(marker, section + marker, 1)
        latest.write_text(source, encoding="utf-8")


def refresh_shared_traditional_data() -> None:
    from build_emperor_traditional import TextCollector, TraditionalConverter, reading_script

    converter = TraditionalConverter()
    try:
        for page, target in (
            (OUT / "index.html", OUT / "zh-hant-data/index.js"),
            (ROOT / "library.html", ROOT / "zh-hant-data/index.js"),
        ):
            source = page.read_text(encoding="utf-8")
            collector = TextCollector()
            collector.feed(source)
            variants = {}
            for text in collector.text:
                traditional = converter.convert(text)
                if traditional != text:
                    variants[text] = traditional
            title_match = re.search(r"<title>(.*?)</title>", source, re.S)
            if title_match:
                title = title_match.group(1)
                traditional = converter.convert(title)
                if traditional != title:
                    variants[title] = traditional
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(reading_script(variants, page), encoding="utf-8")
    finally:
        converter.close()


def main() -> None:
    raw_converter = TC()

    def converter(value: str) -> str:
        return raw_converter(value).replace("余項", "餘項").replace("重復", "重複")

    write_pages(converter)
    update_indexes()
    refresh_shared_traditional_data()
    print("Published game series 14–17 / 15 essays")


if __name__ == "__main__":
    main()
