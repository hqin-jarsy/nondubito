#!/usr/bin/env python3
"""Build full, separately addressable editions from immutable supplied texts.

No translation service, runtime content injection, or source-folder mutation.
Only reviewed essays listed in PUBLISHED are exposed as links.
"""
from pathlib import Path
import hashlib
import html
import json
import math
import os
import re
import markdown

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/paleontology'
TARGET = ROOT / 'essays/paleontology'
DATE = '2026-10-06'
PUBLISHED = (1, 2, 3, 4)
UI = json.loads((DATA / 'ui.json').read_text())
EDITS = json.loads((DATA / 'review.json').read_text())['edits']
LANGS = tuple(UI)
SITE = 'https://nondubito.net/'

def esc(s):
    return html.escape(str(s), quote=True)

def destination(lang, ep=None):
    folder = TARGET if lang == 'zh-Hans' else TARGET / lang.lower()
    return folder / (f'ep{ep:02d}.html' if ep else 'index.html')

def relative(path, current):
    return os.path.relpath(path, current.parent)

def url(path):
    return SITE + path.relative_to(ROOT).as_posix()

def original(ep, lang):
    item = json.loads((DATA / 'sources' / f'ep{ep:02d}.{lang}.json').read_text())
    assert hashlib.sha256(item['original'].encode()).hexdigest() == item['sha256']
    return item['original']

def reviewed(ep, lang):
    text = original(ep, lang)
    for edit in EDITS:
        if (edit['ep'], edit['lang']) == (ep, lang):
            assert text.count(edit['before']) == 1, edit
            text = text.replace(edit['before'], edit['after'])
    return text.rstrip() + '\n'

def typography(text, lang):
    if lang not in ('zh-Hans', 'zh-Hant'):
        return text
    # Only touch plain Chinese punctuation, never Markdown links or code spans.
    parts = re.split(r'(`[^`]*`|https?://\S+)', text)
    for i in range(0, len(parts), 2):
        value = re.sub(r'(?<=[\u3400-\u9fff]),\s*', '，', parts[i])
        value = re.sub(r',\s*(?=[\u3400-\u9fff])', '，', value)
        value = re.sub(r';\s*(?=[\u3400-\u9fff])', '；', value)
        parts[i] = value
    return ''.join(parts)

def parts(ep, lang):
    text = typography(reviewed(ep, lang), lang)
    headings = re.findall(r'^### (.+)$', text, re.M)
    assert len(headings) == 8, (ep, lang, headings)
    title = re.search(r'^## (.+)$', text, re.M).group(1)
    body = text[text.index('\n### ') + 1:]
    for i, heading in enumerate(headings, 1):
        body = body.replace('### ' + heading, f'<h2 id="section-{i}">{esc(heading)}</h2>', 1)
    return title, headings, markdown.markdown(body)

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

def shell(lang, ep, title, description, content):
    ui = UI[lang]; path = destination(lang, ep); canonical = url(path)
    aliases = ''.join(f'<link rel="alternate" hreflang="{l}" href="{url(destination(l, ep))}">\n' for l in LANGS)
    aliases += f'<link rel="alternate" hreflang="x-default" href="{url(destination("en", ep))}">'
    schema = {'@context': 'https://schema.org', '@type': 'Article' if ep else 'CollectionPage',
              'name': title, 'headline': title, 'description': description, 'url': canonical,
              'inLanguage': lang, 'datePublished': DATE, 'dateModified': DATE,
              'author': {'@type': 'Person', 'name': 'Han Qin'},
              'isPartOf': {'@type': 'CreativeWorkSeries', 'name': ui['series'], 'url': url(destination(lang))}}
    if not ep:
        schema['hasPart'] = [{'@type': 'Article', 'url': url(destination(lang, n)), 'name': parts(n, lang)[0]} for n in PUBLISHED]
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
<link rel="stylesheet" href="{relative(TARGET / 'paleontology.css', path)}">
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
        if n in PUBLISHED:
            nav += f'<a href="{relative(destination(lang, n), path)}">{esc(ui[key])} · {n:02d}</a>'
    refs = json.loads((DATA / 'references.json').read_text())[str(ep)]
    sources = ''.join(f'<li><a href="{esc(r[1])}">{esc(r[0])}</a></li>' for r in refs)
    content = f'''<header class="essay-heading"><p class="eyebrow"><a href="{relative(destination(lang), path)}">{esc(ui['series'])}</a> · {ep:02d}</p>
<h1>{esc(title)}</h1><p class="deck">{esc(ui['descs'][ep-1])}</p>
<p class="meta">{esc(ui['by'])} · {esc(reading_time(ep, lang))} · {esc(ui['published'])} <time datetime="{DATE}">{DATE}</time></p></header>
<div class="reading-layout"><aside class="contents"><details><summary>{esc(ui['toc'])}</summary><nav aria-label="{esc(ui['toc'])}"><ol>{toc}</ol></nav></details></aside>
<article class="prose" data-search="paleontology 古生物 凿构周期律 EP{ep:02d}">{body}
<details class="research"><summary>{esc(ui['sources'])}</summary><ul>{sources}</ul></details>
<nav class="essay-nav" aria-label="{esc(ui['back'])}">{nav}</nav></article></div>'''
    return shell(lang, ep, title, ui['descs'][ep-1], content)

def hub(lang):
    ui = UI[lang]; path = destination(lang)
    cards = ''.join(f'''<a class="essay-card" href="{relative(destination(lang, n), path)}"><span class="card-number">{n:02d}</span>
<div><h3>{esc(parts(n, lang)[0])}</h3><p>{esc(ui['descs'][n-1])}</p><span class="card-time">{esc(reading_time(n, lang))} →</span></div></a>''' for n in PUBLISHED)
    route = ''.join(f'<li>{esc(g)}</li>' for g in ui['groups'])
    content = f'''<header class="series-heading"><p class="eyebrow">NON DUBITO · PALEONTOLOGY</p><p class="series-name">{esc(ui['series'])}</p>
<h1>{esc(ui['title'])}</h1><p class="deck">{esc(ui['intro'])}</p><p class="status">{esc(ui['status'])}</p>
<a class="start-link" href="{relative(destination(lang, 1), path)}">{esc(ui['read'])} · 01 →</a></header>
<section class="published"><h2>{esc(ui['groups'][0])}</h2><div class="essay-grid">{cards}</div></section>
<section class="future"><h2>{esc(ui['future'])}</h2><p>{esc(ui['futureNote'])}</p><ol>{route}</ol><p>{esc(ui['afterword'])}</p></section>'''
    return shell(lang, None, ui['series'], ui['intro'], content)

def render():
    paths = []
    for lang in LANGS:
        for ep in (None, *PUBLISHED):
            path = destination(lang, ep); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(hub(lang) if ep is None else essay(lang, ep))
            paths.append(path)
    return paths

if __name__ == '__main__':
    print(f'Built {len(render())} pages: {len(PUBLISHED)} full essays × {len(LANGS)} languages, plus their hubs.')
