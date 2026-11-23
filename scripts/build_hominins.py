#!/usr/bin/env python3
"""Build the complete reviewed hominin history series and eight static editions."""
from pathlib import Path
from functools import cache
import hashlib
import html
import json
import math
import os
import re
import markdown
from web_analytics import tracked_html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/hominins'
TARGET = ROOT / 'essays/hominins'
DATE = json.loads((DATA / 'release.json').read_text())['date']
ARTICLES = tuple(range(1, 25))
UI = json.loads((DATA / 'ui.json').read_text())
LANGS = tuple(UI)
CHECKSUMS = json.loads((DATA / 'release.json').read_text())['checksums']
assert len(CHECKSUMS) == len(LANGS) * len(ARTICLES)
SITE = 'https://nondubito.net/'

def publication_date(ep):
    return DATE

def esc(s):
    return html.escape(str(s), quote=True)

def stem(ep):
    return f'ep{ep:02d}'

def destination(lang, ep=None):
    folder = TARGET if lang == 'zh-Hans' else TARGET / lang.lower()
    return folder / (stem(ep) + '.html' if ep else 'index.html')

def relative(path, current):
    return os.path.relpath(path, current.parent)

def url(path):
    return SITE + path.relative_to(ROOT).as_posix()

def canonical_url(path):
    # Discovery URLs use directory form; ordinary navigation stays unchanged.
    return url(path).removesuffix('index.html') if path.name == 'index.html' else url(path)

@cache
def reviewed(ep, lang):
    item = (DATA / 'sources' / lang / (stem(ep) + '.md')).read_bytes()
    expected = CHECKSUMS[f'{lang}/{stem(ep)}.md']
    assert hashlib.sha256(item).hexdigest() == expected, (ep, lang)
    return item.decode('utf-8')

def display_title(title):
    # A reviewed archive also identifies each file by its series and number.
    # The page already presents those separately in its eyebrow.
    _, separator, tail = re.split(r'([)）])', title, maxsplit=1)
    assert separator and tail
    return tail.lstrip(' :.：.')

@cache
def parts(ep, lang):
    text = reviewed(ep, lang)
    lines = text.splitlines()
    assert lines[0].startswith('# ') and not any(x.startswith('# ') for x in lines[1:])
    title = display_title(lines[0][2:])
    headings = re.findall(r'^## (.+)$', text, re.M)
    assert len(headings) == 8, (ep, lang)
    blocks = text[text.index('\n## ') + 1:]
    for i, heading in enumerate(headings, 1):
        blocks = blocks.replace('## ' + heading, f'<h2 id="section-{i}">{esc(heading)}</h2>', 1)
    return title, headings, markdown.markdown(normalize_prose(blocks, lang), output_format='html5')

def normalize_prose(text, lang):
    # German dates at a paragraph's start are prose, not ordered-list markers.
    if lang == 'de':
        months = ('Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember')
        return re.sub(rf'(?m)^(\d{{1,2}})\.(?= (?:{months}) \d{{4}}\b)',
                      lambda m: m[1]+'&#46;', text)
    return text

def reading_time(ep, lang):
    body = reviewed(ep, lang)
    if lang in ('zh-Hans', 'zh-Hant', 'ja'):
        count = len(re.findall(r'[\u3400-\u9fff\u3040-\u30ff]', body)); rate = 450
    else:
        count = len(body.split()); rate = 180 if lang == 'ko' else 220
    return UI[lang]['minutes'].replace('{n}', str(max(1, math.ceil(count / rate))))

def language_menu(lang, ep, path):
    links = ''.join(f'<a lang="{l}" hreflang="{l}" href="{esc(relative(destination(l, ep), path))}"'
                    + (' aria-current="page"' if l == lang else '') + f'>{esc(UI[l]["label"])}</a>' for l in LANGS)
    return f'<details class="language-menu"><summary aria-label="{esc(UI[lang]["language"])}">{esc(UI[lang]["label"])} <span aria-hidden="true">⌄</span></summary><nav aria-label="{esc(UI[lang]["language"])}">{links}</nav></details>'

@tracked_html
def shell(lang, ep, title, description, content):
    ui = UI[lang]; path = destination(lang, ep); canonical = canonical_url(path)
    aliases = ''.join(f'<link rel="alternate" hreflang="{l}" href="{canonical_url(destination(l, ep))}">\n' for l in LANGS)
    aliases += f'<link rel="alternate" hreflang="x-default" href="{canonical_url(destination("en", ep))}">'
    schema = {'@context': 'https://schema.org', '@type': 'Article' if ep else 'CollectionPage',
              'name': title, 'headline': title, 'description': description, 'url': canonical,
              'inLanguage': lang, 'datePublished': publication_date(ep),
              'dateModified': publication_date(ep) if ep else DATE,
              'author': {'@type': 'Person', 'name': 'Han Qin'},
              'isPartOf': {'@type': 'CreativeWorkSeries', 'name': ui['series'], 'url': url(destination(lang))}}
    if not ep:
        schema['hasPart'] = [{'@type': 'Article', 'url': url(destination(lang, n)), 'name': parts(n, lang)[0]} for n in ARTICLES]
    site_lang = {'zh-Hans': 'zh', 'zh-Hant': 'zh-hant'}.get(lang, lang)
    library = relative(ROOT / 'library.html', path) + '?lang=' + site_lang + '#cycles'
    search = relative(ROOT / 'search.html', path) + '?lang=' + site_lang
    schema_json = json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')
    return f'''<!doctype html>
<html lang="{lang}" data-editions="{lang}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Non Dubito</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">{aliases}
<meta property="og:type" content="{'article' if ep else 'website'}"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta property="og:site_name" content="Non Dubito">
<link rel="stylesheet" href="{relative(TARGET / 'hominins.css', path)}">
<script type="application/ld+json">{schema_json}</script>
</head><body id="top">
<header class="site-header"><a class="wordmark" href="{relative(ROOT / 'index.html', path)}">Non <span>Dubito</span></a>
<nav class="site-nav"><a href="{esc(library)}">{esc(ui['library'])}</a><a href="{esc(search)}">{esc(ui['search'])}</a></nav>{language_menu(lang, ep, path)}</header>
<main>{content}</main>
<footer class="site-footer"><a href="{relative(destination(lang), path)}">{esc(ui['series'])}</a><a href="#top">{esc(ui['top'])} ↑</a><span>© {esc(ui['by'])} · Non Dubito</span></footer>
</body></html>\n'''

def essay(lang, ep):
    ui = UI[lang]; path = destination(lang, ep); title, headings, body = parts(ep, lang)
    toc = ''.join(f'<li><a href="#section-{i}">{esc(h)}</a></li>' for i, h in enumerate(headings, 1))
    nav = f'<a href="{relative(destination(lang), path)}">{esc(ui["back"])}</a>'
    for n, key in ((ep - 1, 'prev'), (ep + 1, 'next')):
        if n in ARTICLES:
            nav += f'<a href="{relative(destination(lang, n), path)}">{esc(ui[key])} · {n:02d}</a>'
    label = f'{ep:02d}'
    description = f"{ui['series']} · {label} · {title}"
    content = f'''<header class="essay-heading"><p class="eyebrow"><a href="{relative(destination(lang), path)}">{esc(ui['series'])}</a> · {esc(label)}</p>
<h1>{esc(title)}</h1>
<p class="meta">{esc(ui['by'])} · {esc(reading_time(ep, lang))} · {esc(ui['published'])} <time datetime="{publication_date(ep)}">{publication_date(ep)}</time></p></header>
<div class="reading-layout"><aside class="contents"><details><summary>{esc(ui['toc'])}</summary><nav aria-label="{esc(ui['toc'])}"><ol>{toc}</ol></nav></details></aside>
<article class="prose" data-search="human evolution ancient hominins 古人类 凿构周期律 {ep:02d}">{body}
<nav class="essay-nav" aria-label="{esc(ui['back'])}">{nav}</nav></article></div>'''
    return shell(lang, ep, title, description, content)

def hub(lang):
    ui = UI[lang]; path = destination(lang)
    sections = []
    for group, (first, last) in zip(ui['groups'], ((1, 5), (6, 10), (11, 15), (16, 20), (21, 24))):
        episodes = [n for n in ARTICLES if first <= n <= last]
        if not episodes:
            continue
        cards = ''.join(f'''<a class="essay-card" href="{relative(destination(lang, n), path)}"><span class="card-number">{n:02d}</span>
<div><h3>{esc(parts(n, lang)[0])}</h3><span class="card-time">{esc(reading_time(n, lang))} →</span></div></a>''' for n in episodes)
        sections.append(f'<section class="published" id="group-{first:02d}"><h2>{esc(group)}</h2><div class="essay-grid">{cards}</div></section>')
    content = f'''<header class="series-heading"><p class="eyebrow">NON DUBITO</p><p class="series-name">{esc(ui['series'])}</p>
<h1>{esc(ui['title'])}</h1><p class="deck">{esc(ui['intro'])}</p><p class="status">{esc(ui['status'])}</p>
<a class="start-link" href="{relative(destination(lang, 1), path)}">{esc(ui['read'])} · 01 →</a></header>
{''.join(sections)}'''
    return shell(lang, None, ui['title'], ui['intro'], content)

def render():
    paths = []
    for lang in LANGS:
        for ep in (None, *ARTICLES):
            path = destination(lang, ep); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(hub(lang) if ep is None else essay(lang, ep))
            paths.append(path)
    return paths

if __name__ == '__main__':
    print(f'Built {len(render())} pages ({len(ARTICLES)} full essays and one hub × {len(LANGS)} languages).')
