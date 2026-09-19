#!/usr/bin/env python3
"""Render the independently edited 00E introduction (ZH / TC / EN).

The committed JSON editions are the editorial sources. No runtime conversion,
translation service, or rebuild of the earlier methodology essays is needed.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "method-introduction"
PAGE = ROOT / "essays" / "method" / "00e.html"
CANONICAL = "https://nondubito.net/essays/method/00e.html"
SOURCE = "https://self-as-an-end.net/papers/sae-methodology-00e.html"
DOI = "10.5281/zenodo.22849616"
LANGUAGES = {"zh": ("zh-Hans", "lang-zh"), "zh-hant": ("zh-Hant", "lang-hant"), "en": ("en", "lang-en")}
LABELS = {
    "zh": {"series": "方法论系列", "intro": "方法论 00E · 入门散文", "note": "想再读深一点", "paper": "余项：一个可携带的方法", "previous": "上一篇：余之道", "next": "下一篇：人与AI共生的方法论", "essays": "随笔", "start": "从这里开始", "library": "书库", "search": "搜索"},
    "zh-hant": {"series": "方法論系列", "intro": "方法論 00E · 入門散文", "note": "想再讀深一點", "paper": "餘項：一個可攜帶的方法", "previous": "上一篇：餘之道", "next": "下一篇：人與AI共生的方法論", "essays": "隨筆", "start": "從這裡開始", "library": "書庫", "search": "搜尋"},
    "en": {"series": "Methodology Series", "intro": "Methodology 00E · An introduction", "note": "Further reading", "paper": "Remainder: A Portable Method", "previous": "Previous: Via Rho: The Way of the Remainder", "next": "Next: The Methodology of Human–AI Symbiosis", "essays": "Essays", "start": "Start Here", "library": "Library", "search": "Search"},
}

STYLE = '''
    html[data-lang] body.method-intro [data-reading-lang] { display:none; }
    html[data-lang="zh"] body.method-intro [data-reading-lang="zh"],
    html[data-lang="zh-hant"] body.method-intro [data-reading-lang="zh-hant"],
    html[data-lang="en"] body.method-intro [data-reading-lang="en"] { display:block; }
    .method-intro .lang-hant { font-family:var(--tc); }
    .method-intro .essay-titles h1 { line-height:1.3; }
    .method-intro .essay-titles h1.lang-hant { font-size:clamp(1.8rem,4.5vw,2.8rem); }
    .method-intro .back-link { max-width:var(--max-w); margin:0 auto 1.25rem; color:var(--gold-light); font-family:var(--sans); font-size:0.8rem; text-decoration:none; }
    .method-intro .essay-series { font-family:var(--sans); font-size:0.72rem; letter-spacing:0.1em; color:var(--gold-light); margin-bottom:1rem; }
    .method-intro .essay-subtitle { font-style:normal; max-width:40rem; }
    .method-intro .essay-body h2 { font-size:1.4rem; line-height:1.65; }
    .method-intro .essay-body ol { padding-left:1.3em; margin:1.5rem 0 2rem; }
    .method-intro .essay-body li { padding-left:0.3em; margin-bottom:1rem; color:var(--ink-light); font-size:1.05rem; line-height:1.85; }
    .method-intro .method-reading-note { margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--cream-border); }
    .method-intro .method-reading-note h2 { font-size:1.05rem; margin-top:0; }
    .method-intro .method-reading-note p { font-size:0.88rem; line-height:1.8; color:var(--ink-muted); }
    .method-intro .method-nav { display:flex; flex-wrap:wrap; gap:1rem; padding-top:1.5rem; margin-top:2rem; border-top:1px solid var(--cream-border); }
    .method-intro .method-nav a { flex:1 1 12rem; padding:1rem; border:1px solid var(--cream-border); font-size:0.94rem; }
    .method-intro .lang-btn:focus-visible, .method-intro a:focus-visible { outline:2px solid var(--gold); outline-offset:4px; }
    @media (max-width:600px) { .method-intro .essay-body h2 { font-size:1.2rem; } }
'''

SCRIPT = '''
(function () {
  'use strict';
  var codes = {'zh':'zh-Hans', 'zh-hant':'zh-Hant', 'en':'en'};
  var saved = 'zh';
  try { saved = localStorage.getItem('nd_lang') || localStorage.getItem('nondubito-lang') || 'zh'; } catch (error) {}
  if (!Object.prototype.hasOwnProperty.call(codes, saved)) saved = 'zh';
  document.documentElement.setAttribute('data-lang', saved);
  document.documentElement.lang = codes[saved];
  document.addEventListener('DOMContentLoaded', function () {
    var buttons = document.querySelectorAll('.lang-btn[data-lang]');
    function update(lang) {
      document.documentElement.setAttribute('data-lang', lang);
      document.documentElement.lang = codes[lang];
      buttons.forEach(function (button) {
        var active = button.getAttribute('data-lang') === lang;
        button.classList.toggle('active', active);
        button.setAttribute('aria-pressed', String(active));
      });
      document.querySelectorAll('[data-reading-lang]').forEach(function (node) {
        node.setAttribute('aria-hidden', String(node.getAttribute('data-reading-lang') !== lang));
      });
      var heading = document.querySelector('h1[data-reading-lang="' + lang + '"]');
      document.title = heading.textContent + ' — Non Dubito';
    }
    buttons.forEach(function (button) {
      button.addEventListener('click', function () {
        var lang = button.getAttribute('data-lang');
        update(lang);
        try { localStorage.setItem('nd_lang', lang); localStorage.setItem('nondubito-lang', lang); } catch (error) {}
      });
    });
    update(saved);
  });
})();
'''


def load_editions():
    editions = {lang: json.loads((DATA / (lang + ".json")).read_text(encoding="utf-8")) for lang in LANGUAGES}
    for lang, edition in editions.items():
        if len(edition["sections"]) != 7 or not edition["intro"]:
            raise ValueError(f"Incomplete 00E edition: {lang}")
        if len(edition["sections"][-1].get("items", [])) != 5:
            raise ValueError(f"Missing five-question checklist: {lang}")
    return editions


def localized(tag, lang, text, extra=""):
    code, css = LANGUAGES[lang]
    return f'<{tag} class="{css}" lang="{code}" data-reading-lang="{lang}"{extra}>{html.escape(text)}</{tag}>'


def paragraphs(items):
    return "\n".join("<p>" + html.escape(text) + "</p>" for text in items)


def render_body(lang, edition):
    code, css = LANGUAGES[lang]
    labels = LABELS[lang]
    parts = [f'<div class="essay-body {css}" lang="{code}" data-reading-lang="{lang}">', paragraphs(edition["intro"])]
    for section in edition["sections"]:
        parts.extend(["<h2>" + html.escape(section["heading"]) + "</h2>", paragraphs(section["paragraphs"])])
        if section.get("items"):
            parts.append("<ol>" + "".join("<li>" + html.escape(item) + "</li>" for item in section["items"]) + "</ol>")
        parts.append(paragraphs(section.get("after", [])))
    parts.append(f'''<aside class="method-reading-note" aria-label="{html.escape(labels['note'])}">
<h2>{html.escape(labels['note'])}</h2>
<p>{html.escape(edition['reading_note'])}</p>
<p>Han Qin (2026). <a href="{SOURCE}">{html.escape(labels['paper'])}</a> · M-00E · DOI: <a href="https://doi.org/{DOI}">{DOI}</a></p>
</aside>
<nav class="method-nav" aria-label="{html.escape(labels['series'])}">
<a href="00.html">← {html.escape(labels['previous'])}</a>
<a href="viii.html">{html.escape(labels['next'])} →</a>
</nav>
<p class="essay-footer-note"><a href="index.html">{html.escape(labels['series'])}</a> · Han Qin (秦汉) · 2026</p>
</div>''')
    return "\n".join(parts)


def render():
    editions = load_editions()
    title = editions["zh"]["title"] + " — Non Dubito"
    description = editions["zh"]["subtitle"]
    alternates = "\n".join(f'<link rel="alternate" hreflang="{code}" href="{CANONICAL}">' for code in ["x-default", "zh-Hans", "zh-Hant", "en"])
    nav = "\n".join('<a href="../../' + href + '">' + "".join(localized("span", lang, LABELS[lang][key]) for lang in LANGUAGES) + '</a>' for href, key in [("index.html", "essays"), ("start.html", "start"), ("library.html", "library"), ("search.html", "search")])
    titles = "\n".join(localized("h1", lang, editions[lang]["title"]) for lang in LANGUAGES)
    decks = "\n".join('<p class="essay-subtitle method-search-deck ' + LANGUAGES[lang][1] + '" lang="' + LANGUAGES[lang][0] + '" data-reading-lang="' + lang + '">' + html.escape(editions[lang]["subtitle"]) + '</p>' for lang in LANGUAGES)
    back = "\n".join('<a class="back-link ' + LANGUAGES[lang][1] + '" data-reading-lang="' + lang + '" href="index.html">← ' + LABELS[lang]["series"] + '</a>' for lang in LANGUAGES)
    kicker = '<div class="essay-series">' + "".join(localized("span", lang, LABELS[lang]["intro"]) for lang in LANGUAGES) + '</div>'
    bodies = "\n".join(render_body(lang, edition) for lang, edition in editions.items())
    return f'''<!DOCTYPE html>
<!-- Generated by scripts/build_method_introduction.py; edit data/method-introduction/*.json. -->
<html lang="zh-Hans" data-lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="author" content="Han Qin (秦汉)">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:url" content="{CANONICAL}">
  <meta name="twitter:card" content="summary">
  <link rel="canonical" href="{CANONICAL}">
  {alternates}
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
  <link rel="stylesheet" href="../../style.css">
  <style>{STYLE}</style>
  <script>{SCRIPT}</script>
</head>
<body class="method-intro">
  <header>
    <div class="header-inner">
      <a href="../../index.html" class="site-title"><span class="title-latin">Non <span>Dubito</span></span><span class="title-sub">Essays in the Self-as-an-End Tradition</span></a>
      <nav aria-label="Main navigation">{nav}</nav>
    </div>
  </header>
  <main class="essay-main" data-search="SAE 方法论 方法論 余项 餘項 remainder methodology feedback received 排班 练琴 練琴 意见 意見 00E">
    <article>
      <header class="essay-header">
        <div class="lang-toggle" role="group" aria-label="Language">
          <button type="button" class="lang-btn" data-lang="en" aria-pressed="false">EN</button><span class="lang-sep" aria-hidden="true">|</span>
          <button type="button" class="lang-btn active" data-lang="zh" aria-pressed="true">中文</button><span class="lang-sep" aria-hidden="true">|</span>
          <button type="button" class="lang-btn" data-lang="zh-hant" aria-pressed="false">繁體</button>
        </div>
        {back}
        <div class="essay-titles">{kicker}{titles}{decks}</div>
        <div class="essay-meta"><span>Han Qin (秦汉)</span><span class="sep">·</span><time datetime="2026-09-19">2026-09-19</time></div>
      </header>
      {bodies}
    </article>
  </main>
  <script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render()
    if args.check:
        if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != content:
            print("ERROR: methodology 00E is missing or stale")
            return 1
        print("OK: methodology 00E matches its three edited sources")
        return 0
    PAGE.write_text(content, encoding="utf-8")
    print("Wrote essays/method/00e.html (Simplified Chinese, Traditional Chinese, English)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
