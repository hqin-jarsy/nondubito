#!/usr/bin/env python3
"""Build the bilingual/traditional flagship reader series on working with AI."""

from __future__ import annotations

import ctypes
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "ai-work"
TARGET = ROOT / "essays" / "ai-work"
UTF8 = 0x08000100


SERIES = {
    "en_title": "Working with AI Without Surrendering the Self",
    "zh_title": "与AI共事，而不把自己交出去",
    "en_deck": "Eight essays for people who already use AI—and do not want convenience to quietly decide what their work, judgment, and life are for.",
    "zh_deck": "写给已经开始使用 AI、却不愿让便利悄悄决定工作、判断与人生方向的人。八篇文章，从会用工具走向仍然能够为自己负责。",
}


HANT_REPLACEMENTS = {
    "軟件": "軟體", "硬件": "硬體", "數據": "資料", "視頻": "影片",
    "網絡": "網路", "用戶": "使用者", "默認": "預設", "鼠標": "滑鼠",
    "打印": "列印", "信息": "資訊", "智能": "智慧", "帳戶": "帳號",
    "文件": "檔案", "反饋": "回饋", "質量": "品質", "博客": "部落格",
    "優化": "最佳化", "項目": "專案", "搜索": "搜尋", "重復": "重複",
    "概率": "機率", "屏幕": "螢幕", "里": "裡", "“": "「", "”": "」",
}


class TraditionalConverter:
    def __init__(self) -> None:
        self.cf = ctypes.cdll.LoadLibrary(
            "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
        )
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
        self.transform = self._string("Hans-Hant")

    def _string(self, value: str) -> int:
        return self.cf.CFStringCreateWithCString(None, value.encode("utf-8"), UTF8)

    def convert(self, value: str) -> str:
        source = self._string(value)
        mutable = self.cf.CFStringCreateMutable(None, 0)
        try:
            self.cf.CFStringAppend(mutable, source)
            if not self.cf.CFStringTransform(mutable, None, self.transform, 0):
                raise RuntimeError("Simplified-to-Traditional conversion failed")
            length = self.cf.CFStringGetLength(mutable)
            size = self.cf.CFStringGetMaximumSizeForEncoding(length, UTF8) + 1
            buffer = ctypes.create_string_buffer(size)
            if not self.cf.CFStringGetCString(mutable, buffer, size, UTF8):
                raise RuntimeError("Traditional Chinese encoding failed")
            result = buffer.value.decode("utf-8")
            for old, new in HANT_REPLACEMENTS.items():
                result = result.replace(old, new)
            return result
        finally:
            self.cf.CFRelease(source)
            self.cf.CFRelease(mutable)

    def close(self) -> None:
        self.cf.CFRelease(self.transform)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_article(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8").strip()
    front, body = raw.split("\n---\n", 1)
    meta: dict[str, str] = {}
    for line in front.splitlines():
        key, value = line.split(":", 1)
        meta[key.strip().replace("-", "_")] = value.strip()
    en, zh = body.split("\n@@ ZH\n", 1)
    en = en.removeprefix("@@ EN\n")
    meta["en_body"] = en.strip()
    meta["zh_body"] = zh.strip()
    return meta


def render_prose(raw: str) -> str:
    blocks = re.split(r"\n\s*\n", raw.strip())
    out: list[str] = []
    in_list = False
    for block in blocks:
        block = block.strip()
        if block.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h2>{esc(block[3:])}</h2>")
        elif block.startswith("### "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h3>{esc(block[4:])}</h3>")
        elif block.startswith("> "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f'<aside class="turning-point">{esc(block[2:])}</aside>')
        elif block.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            for item in block.splitlines():
                out.append(f"<li>{esc(item.removeprefix('- '))}</li>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            cls = ' class="opening"' if not out else ""
            text = esc(" ".join(line.strip() for line in block.splitlines()))
            text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
            out.append(f"<p{cls}>{text}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def alternates(filename: str) -> str:
    url = f"https://nondubito.net/essays/ai-work/{'' if filename == 'index.html' else filename}"
    return "".join(
        f'<link rel="alternate" hreflang="{lang}" href="{url}">'
        for lang in ("en", "zh-Hans", "zh-Hant", "x-default")
    )


def head(title: str, description: str, filename: str, page_type: str) -> str:
    target = "" if filename == "index.html" else filename
    url = f"https://nondubito.net/essays/ai-work/{target}"
    schema = {
        "@context": "https://schema.org",
        "@type": page_type,
        "name": title,
        "description": description,
        "inLanguage": ["en", "zh-Hans", "zh-Hant"],
        "datePublished": "2026-09-10",
        "dateModified": "2026-09-10",
        "author": {"@type": "Person", "name": "Han Qin (秦汉)"},
        "url": url,
    }
    return f'''<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(description)}"><meta name="author" content="Han Qin (秦汉)">
  <meta property="og:type" content="article"><meta property="og:title" content="{esc(title)} — Non Dubito"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Non Dubito"><meta name="twitter:card" content="summary">
  <link rel="canonical" href="{url}">{alternates(filename)}
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg"><link rel="apple-touch-icon" sizes="180x180" href="../../apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&amp;family=Inter:wght@300;400;500&amp;family=Noto+Serif+SC:wght@400;500;600&amp;family=Noto+Serif+TC:wght@400;500;600&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../style.css"><link rel="stylesheet" href="../../site-shell.css?v=20260905b"><link rel="stylesheet" href="../../reading-context.css?v=20260905a"><link rel="stylesheet" href="series.css?v=20260910">
  <script src="../../site-shell.js?v=20260905b"></script><script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, indent=2)}</script>
</head>'''


def language_menu() -> str:
    return '''<details class="site-shell-language"><summary class="site-shell-language-summary"><span data-current-language>EN</span><span aria-hidden="true">⌄</span></summary><div class="site-shell-language-options"><button type="button" data-set-language="en">English</button><button type="button" data-set-language="zh">中文</button><button type="button" data-set-language="zh-hant">繁體中文</button></div></details>'''


def shell_header() -> str:
    return f'''<header class="site-shell-header"><div class="header-inner"><a href="../../index.html" class="site-title" aria-label="Non Dubito home"><span class="title-latin">Non <span>Dubito</span></span><span class="title-sub">A Mind in Many Languages</span></a><nav class="site-shell-nav" aria-label="Primary navigation"><a href="../../start.html"><span class="lang-en">Start Here</span><span class="lang-zh">从这里开始</span><span class="lang-hant">從這裡開始</span></a><a href="../../explore.html"><span class="lang-en">Explore</span><span class="lang-zh">探索</span><span class="lang-hant">探索</span></a><a href="../../latest.html"><span class="lang-en">Latest</span><span class="lang-zh">最近更新</span><span class="lang-hant">最近更新</span></a><a href="../../about.html"><span class="lang-en">About</span><span class="lang-zh">关于</span><span class="lang-hant">關於</span></a></nav><div class="site-shell-tools"><a class="site-shell-tool" href="../../search.html" aria-label="Search"><svg class="site-shell-tool-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="6.5" stroke="currentColor" stroke-width="1.5"/><path d="m16 16 4 4" stroke="currentColor" stroke-width="1.5"/></svg><span class="site-shell-tool-label"><span class="lang-en">Search</span><span class="lang-zh">搜索</span><span class="lang-hant">搜尋</span></span></a>{language_menu()}<button class="site-shell-menu-button" type="button" data-site-shell-menu aria-controls="site-shell-drawer" aria-expanded="false"><span class="site-shell-tool-label"><span class="lang-en">Menu</span><span class="lang-zh">菜单</span><span class="lang-hant">選單</span></span><span aria-hidden="true">☰</span></button></div></div></header><div class="site-shell-drawer" id="site-shell-drawer" data-site-shell-drawer><nav><a href="../../start.html">{tri('Start Here','从这里开始','從這裡開始')}</a><a href="../../explore.html">{tri('Explore','探索','探索')}</a><a href="../../latest.html">{tri('Latest','最近更新','最近更新')}</a><a href="../../about.html">{tri('About','关于','關於')}</a><a href="../../library.html">{tri('Full Library','完整文库','完整文庫')}</a></nav><div class="site-shell-mobile-languages"><button type="button" data-set-language="en">EN</button><button type="button" data-set-language="zh">中文</button><button type="button" data-set-language="zh-hant">繁體</button></div></div>'''


def footer() -> str:
    return '''<footer class="site-shell-footer"><div class="site-shell-footer-inner"><div><div class="site-shell-footer-mark">Non <span>Dubito</span></div><p>A mind in many languages</p></div><div class="site-shell-footer-links"><a href="../../explore.html">Explore</a><a href="../../library.html">Library</a><a href="https://self-as-an-end.net">SAE Theory ↗</a></div></div></footer>'''


def tri(en: str, zh: str, hant: str, tag: str = "span", classes: str = "") -> str:
    base = f" {classes}" if classes else ""
    return f'<{tag} class="lang-en{base}">{en}</{tag}><{tag} class="lang-zh{base}">{zh}</{tag}><{tag} class="lang-hant{base}">{hant}</{tag}>'


def render_index(articles: list[dict], converter: TraditionalConverter) -> str:
    hant_title = converter.convert(SERIES["zh_title"])
    hant_deck = converter.convert(SERIES["zh_deck"])
    cards = []
    for idx, article in enumerate(articles, 1):
        zh_title = article["zh_title"]
        zh_deck = article["zh_deck"]
        cards.append(f'''<a class="series-card{' featured' if idx == 1 else ''}" href="{esc(article['slug'])}.html"><span class="card-number">{idx:02d}</span>{tri(esc(article['en_title']), esc(zh_title), esc(converter.convert(zh_title)), 'h2', 'cjk-switch')}{tri(esc(article['en_deck']), esc(zh_deck), esc(converter.convert(zh_deck)), 'p', 'cjk-switch')}<span class="card-arrow">→</span></a>''')
    description = SERIES["en_deck"]
    return f'''<!DOCTYPE html><html lang="en" data-lang="en" data-editions="en zh zh-hant">{head(SERIES['en_title'] + ' · ' + SERIES['zh_title'], description, 'index.html', 'CollectionPage')}<body class="site-shell-page explicit-hant">{shell_header()}<main class="series-wrap"><nav class="reading-breadcrumbs"><a href="../../explore.html">{tri('Explore','探索','探索')}</a><span>/</span><a href="../../explore.html#mind">{tri('Mind, AI &amp; Technology','心灵、AI 与技术','心靈、AI 與技術')}</a></nav><section class="series-hero"><p class="eyebrow">{tri('New flagship · Eight essays','新旗舰 · 八篇','新旗艦 · 八篇')}</p>{tri(esc(SERIES['en_title']), esc(SERIES['zh_title']), esc(hant_title), 'h1', 'cjk-switch')}{tri(esc(SERIES['en_deck']), esc(SERIES['zh_deck']), esc(hant_deck), 'p', 'series-deck cjk-switch')}<div class="series-promise">{tri('AI can take over tasks. It should not quietly take over the place from which you decide what the task is for.','AI 可以接管任务，却不该悄悄接管那个决定“任务为了什么”的位置。','AI 可以接管任務，卻不該悄悄接管那個決定「任務為了什麼」的位置。','p','cjk-switch')}</div></section><section class="series-map"><div class="map-label">{tri('The route','阅读路线','閱讀路線')}</div><div class="map-steps"><span>Draft</span><i>→</i><span>Judge</span><i>→</i><span>Choose</span><i>→</i><span>Answer</span></div></section><section class="series-grid">{''.join(cards)}</section><aside class="series-afterword">{tri('These are reader essays, not summaries of technical papers. They bring the Self-as-an-End framework into ordinary work without requiring its vocabulary first.','这不是八篇论文摘要，而是一条面向普通读者的入口：先从每天已经发生的工作经验出发，再看见工具与主体之间真正的分界。','這不是八篇論文摘要，而是一條面向普通讀者的入口：先從每天已經發生的工作經驗出發，再看見工具與主體之間真正的分界。','p','cjk-switch')}<a href="https://self-as-an-end.net/papers/sae-methodology-8.html">{tri('Read the theoretical interface ↗','进入理论接口 ↗','進入理論介面 ↗')}</a></aside></main>{footer()}</body></html>'''


def render_article(article: dict, index: int, articles: list[dict], converter: TraditionalConverter) -> str:
    filename = article["slug"] + ".html"
    zh_title = article["zh_title"]
    zh_deck = article["zh_deck"]
    hant_title = converter.convert(zh_title)
    hant_deck = converter.convert(zh_deck)
    en_body = render_prose(article["en_body"])
    zh_body = render_prose(article["zh_body"])
    hant_body = converter.convert(zh_body)
    prev_link = f'<a href="{articles[index-2]["slug"]}.html">← {index-1:02d}</a>' if index > 1 else f'<a href="index.html">{tri("← Index", "← 目录", "← 目錄")}</a>'
    next_link = f'<a href="{articles[index]["slug"]}.html">{index+1:02d} →</a>' if index < len(articles) else f'<a href="index.html">{tri("Series →", "系列 →", "系列 →")}</a>'
    return f'''<!DOCTYPE html><html lang="en" data-lang="en" data-editions="en zh zh-hant">{head(article['en_title'] + ' · ' + zh_title, article['en_deck'], filename, 'Article')}<body class="site-shell-page explicit-hant">{shell_header()}<main class="article-wrap"><nav class="reading-breadcrumbs"><a href="index.html">{tri('Working with AI','与AI共事','與AI共事')}</a><span>/</span><span>{index:02d} / {len(articles):02d}</span></nav><section class="aiw-article-hero"><p class="eyebrow">{tri('Working with AI · Reader essay','与AI共事 · 读者散文','與AI共事 · 讀者散文')}</p>{tri(esc(article['en_title']), esc(zh_title), esc(hant_title), 'h1', 'cjk-switch')}{tri(esc(article['en_deck']), esc(zh_deck), esc(hant_deck), 'p', 'article-deck cjk-switch')}<p class="article-meta">Han Qin (秦汉) · 10 Sep 2026 · {index:02d} / 08</p></section><article class="essay-body lang-en">{en_body}</article><article class="essay-body cjk lang-zh">{zh_body}</article><article class="essay-body cjk tc lang-hant">{hant_body}</article><aside class="source-note">{tri('This reader essay is an independent public-facing application of the Self-as-an-End framework.','本文是自我目的论框架面向普通读者的一次独立应用。','本文是自我目的論框架面向普通讀者的一次獨立應用。')} <a href="https://self-as-an-end.net/papers/sae-methodology-8.html">Human–AI Collaboration ↗</a></aside><nav class="article-nav">{prev_link}<a href="index.html">{tri('All eight essays','全部八篇','全部八篇')}</a>{next_link}</nav></main>{footer()}</body></html>'''


def main() -> None:
    articles = [load_article(path) for path in sorted(SOURCE.glob("*.md"))]
    if len(articles) != 8:
        raise ValueError(f"Expected 8 source essays, found {len(articles)}")
    converter = TraditionalConverter()
    try:
        TARGET.mkdir(parents=True, exist_ok=True)
        (TARGET / "series.css").write_text(CSS.strip() + "\n", encoding="utf-8")
        (TARGET / "index.html").write_text(render_index(articles, converter), encoding="utf-8")
        for index, article in enumerate(articles, 1):
            (TARGET / f"{article['slug']}.html").write_text(
                render_article(article, index, articles, converter), encoding="utf-8"
            )
    finally:
        converter.close()
    print(f"Built {len(articles)} essays in {TARGET.relative_to(ROOT)}")


CSS = r'''
.series-wrap,.article-wrap{width:min(100% - 2.4rem,1080px);margin:0 auto;padding:clamp(7rem,11vw,10rem) 0 6rem}.reading-breadcrumbs{margin-bottom:3.5rem}.series-hero{max-width:930px}.eyebrow{font:500 .7rem/1.2 var(--sans);letter-spacing:.17em;text-transform:uppercase;color:var(--gold);margin:0 0 1.35rem}.series-hero h1,.aiw-article-hero h1{font:400 clamp(3.1rem,7.4vw,6.7rem)/.94 var(--serif);letter-spacing:-.045em;color:var(--ink);margin:0}.series-hero h1.lang-zh,.series-hero h1.lang-hant{font-family:var(--cjk),serif;font-size:clamp(2.7rem,5vw,4.9rem);letter-spacing:.02em;line-height:1.25}.aiw-article-hero h1.lang-zh,.aiw-article-hero h1.lang-hant{font-family:var(--cjk),serif;font-size:clamp(2.5rem,5vw,4.35rem);letter-spacing:.02em;line-height:1.3}.series-deck,.article-deck{font:400 clamp(1.2rem,2.4vw,1.55rem)/1.65 var(--serif);color:var(--ink-light);max-width:800px;margin:1.8rem 0 0}.series-deck.lang-zh,.series-deck.lang-hant,.article-deck.lang-zh,.article-deck.lang-hant{font-family:var(--cjk),serif;line-height:1.95}.series-promise{margin-top:3rem;padding:1.25rem 1.5rem;border-left:3px solid var(--gold);background:var(--cream);max-width:820px}.series-promise p{font:400 1.02rem/1.8 var(--serif);margin:0;color:var(--green)}.series-promise p.lang-zh,.series-promise p.lang-hant{font-family:var(--cjk),serif}.series-map{margin:4rem 0 2rem;border-top:1px solid var(--cream-border);border-bottom:1px solid var(--cream-border);padding:1.1rem 0;display:flex;align-items:center;justify-content:space-between;gap:1rem}.map-label{font:500 .65rem/1 var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}.map-steps{display:flex;gap:.75rem;align-items:center;font:400 .72rem/1 var(--sans);letter-spacing:.09em;text-transform:uppercase;color:var(--ink-light)}.map-steps i{color:var(--gold);font-style:normal}.series-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:var(--cream-border);border:1px solid var(--cream-border)}.series-card{position:relative;display:flex;min-height:300px;padding:2rem;background:var(--paper);text-decoration:none;flex-direction:column;transition:background .2s}.series-card:hover{background:var(--cream)}.series-card.featured{grid-column:1/-1;min-height:350px;background:var(--green)}.series-card.featured:hover{background:#17392d}.card-number{font:500 .67rem/1 var(--sans);letter-spacing:.14em;color:var(--gold)}.series-card h2{font:400 2rem/1.15 var(--serif);margin:auto 0 .8rem;color:var(--ink);max-width:820px}.series-card h2.lang-zh,.series-card h2.lang-hant{font-family:var(--cjk),serif;line-height:1.5}.series-card p{font:400 1rem/1.65 var(--serif);color:var(--ink-light);margin:0;max-width:760px}.series-card p.lang-zh,.series-card p.lang-hant{font-family:var(--cjk),serif;line-height:1.85}.series-card.featured h2{font-size:clamp(2.3rem,4vw,3.7rem);color:var(--cream)}.series-card.featured p{color:rgba(248,243,232,.76)}.card-arrow{position:absolute;right:2rem;top:2rem;color:var(--gold)}.series-afterword{margin:3rem 0 0;padding:2rem;border:1px solid var(--cream-border)}.series-afterword p{font:400 1.02rem/1.8 var(--serif);color:var(--ink-light);margin:0 0 1rem;max-width:820px}.series-afterword p.lang-zh,.series-afterword p.lang-hant{font-family:var(--cjk),serif}.series-afterword a{font:500 .68rem/1 var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--gold)}.article-wrap{max-width:850px}.aiw-article-hero{padding-bottom:2.8rem;border-bottom:1px solid var(--cream-border);margin-bottom:3.5rem}.aiw-article-hero h1{font-size:clamp(2.8rem,6.5vw,5rem)}.article-meta{font:400 .65rem/1.4 var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-muted);margin:1.5rem 0 0}.essay-body{font:400 1.17rem/1.83 var(--serif);color:var(--ink)}.essay-body.cjk{font-family:var(--cjk),serif;font-size:1.05rem;line-height:2.08;letter-spacing:.012em}.essay-body p{margin:0 0 1.55rem}.essay-body .opening{font-size:1.22em;line-height:1.68;color:var(--green)}.essay-body h2{font:400 2.1rem/1.2 var(--serif);color:var(--ink);margin:4rem 0 1.25rem}.essay-body.cjk h2{font-family:var(--cjk),serif;font-size:1.72rem;line-height:1.55;letter-spacing:.035em}.essay-body h3{font:500 1.25rem/1.4 var(--serif);margin:2.6rem 0 1rem;color:var(--green)}.essay-body ul{margin:0 0 1.8rem;padding-left:1.25rem}.essay-body li{margin:.45rem 0}.turning-point{margin:2.3rem 0;padding:1.35rem 1.5rem;background:var(--cream);border-left:3px solid var(--gold);font-size:1.08em;line-height:1.75;color:var(--green)}.source-note{margin-top:4rem;padding:1.4rem 0;border-top:1px solid var(--cream-border);border-bottom:1px solid var(--cream-border);font:400 .72rem/1.7 var(--sans);color:var(--ink-muted)}.source-note a{color:var(--gold)}.article-nav{display:grid;grid-template-columns:1fr auto 1fr;gap:1rem;align-items:center;margin-top:2.5rem}.article-nav a{font:500 .66rem/1.3 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--green);text-decoration:none}.article-nav a:last-child{text-align:right}@media(max-width:720px){.series-wrap,.article-wrap{width:min(100% - 2rem,1080px);padding-top:6.5rem}.series-grid{grid-template-columns:1fr}.series-card.featured{grid-column:auto}.series-card{min-height:270px;padding:1.5rem}.series-map{align-items:flex-start;flex-direction:column}.map-steps{gap:.42rem;flex-wrap:wrap}.article-nav{grid-template-columns:1fr 1fr}.article-nav a:nth-child(2){display:none}.series-hero h1,.aiw-article-hero h1{letter-spacing:-.025em}}
'''


if __name__ == "__main__":
    main()
