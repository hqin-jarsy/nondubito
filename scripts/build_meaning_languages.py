#!/usr/bin/env python3
"""Publish hand-written Meaning Theory editions; never generate or translate prose."""
import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / 'essays/meaning'
LANGUAGES = ('ja', 'fr', 'de', 'es', 'ko')
LABELS = {'en': 'English', 'zh': '简体中文', 'zh-hant': '繁體中文',
          'ja': '日本語', 'fr': 'Français', 'de': 'Deutsch', 'es': 'Español', 'ko': '한국어'}
SLUGS = ['index'] + [f'ep{i:02}' for i in range(1, 9)]
E = html.escape


def load_edition(language):
    data = json.loads((ROOT / 'data/meaning' / f'{language}.json').read_text())
    def prose(value):
        return isinstance(value, str) and bool(value.strip()) and '<' not in value and '>' not in value
    assert data['language'] == language
    for key in ('series_label', 'series_title', 'description', 'reading_note', 'start_label',
                'source_note', 'edition_note', 'count_label'):
        assert prose(data[key]), (language, key)
    assert data['intro'] and all(prose(p) for p in data['intro'])
    for key in ('home', 'start', 'library', 'about', 'theory', 'language', 'contents',
                'previous', 'next', 'further', 'academic_source'):
        assert prose(data['ui'][key]), (language, key)
    assert [a['slug'] for a in data['articles']] == SLUGS[1:]
    assert len({a['title'] for a in data['articles']}) == 8
    for article in data['articles']:
        assert prose(article['title']) and prose(article['description'])
        assert article['sections']
        paragraphs = []
        for section in article['sections']:
            assert section['heading'] == '' or prose(section['heading'])
            assert section['paragraphs'] and all(prose(p) for p in section['paragraphs'])
            paragraphs += section['paragraphs']
        # Guard against accidentally publishing an outline or partial article.
        assert len(paragraphs) >= 12, (language, article['slug'], 'Incomplete prose')
        assert len(''.join(paragraphs)) >= 2200, (language, article['slug'], 'Incomplete prose')
    return data


def menu(slug, language=None, label='Language / 语言'):
    choices = []
    for code, name in LABELS.items():
        if code in ('en', 'zh', 'zh-hant'):
            href = ('../' if language else '') + f'{slug}.html?lang={code}'
            attr = f' data-lang="{code}"' if language is None else ''
        else:
            href = (f'../{code}/' if language else f'{code}/') + f'{slug}.html'
            attr = ''
        active = ' active' if code == language else ''
        choices.append(f'<a class="lang-btn{active}" data-edition="{code}"{attr} href="{href}">{name}</a>')
    return f'<div class="lang-toggle meaning-languages" role="group" aria-label="{E(label)}">' + ''.join(choices) + '</div>'


def alternates(slug):
    suffix = '' if slug == 'index' else slug + '.html'
    base = 'https://nondubito.net/essays/meaning/'
    # EN and Traditional are reading modes on the Chinese canonical URL, not
    # separate indexable pages. Do not invent hreflang URLs for these modes.
    links = [('x-default', base + suffix), ('zh-Hans', base + suffix)]
    links += [(lang, base + lang + '/' + suffix) for lang in LANGUAGES]
    return '<!-- MEANING ALTERNATES START -->\n' + '\n'.join(
        f'<link rel="alternate" hreflang="{lang}" href="{url}">' for lang, url in links
    ) + '\n<!-- MEANING ALTERNATES END -->'


def citations(slug, data):
    original = (SERIES / f'{slug}.html').read_text()
    body = re.search(r'<div class="method-citations">(.*?)</div>', original, re.S).group(1)
    paragraphs = re.findall(r'<p class="lang-en">(.*?)</p>', body, re.S)
    assert paragraphs, slug
    return '\n'.join('<p>' + p.replace('Academic original:', E(data['ui']['academic_source']) + ':', 1) + '</p>' for p in paragraphs)


def document(data, slug, content):
    lang = data['language']
    title = data['series_title'] if slug == 'index' else next(a['title'] for a in data['articles'] if a['slug'] == slug)
    desc = data['description'] if slug == 'index' else next(a['description'] for a in data['articles'] if a['slug'] == slug)
    url = 'https://nondubito.net/essays/meaning/' + lang + '/' + ('' if slug == 'index' else slug + '.html')
    ui = data['ui']
    structured = {'@context': 'https://schema.org', '@type': 'CollectionPage' if slug == 'index' else 'Article',
                  'name': title, 'headline': title, 'description': desc, 'inLanguage': lang,
                  'url': url, 'author': {'@type': 'Person', 'name': 'Han Qin'},
                  'isPartOf': {'@type': 'CreativeWorkSeries', 'name': data['series_label'],
                               'url': f'https://nondubito.net/essays/meaning/{lang}/'}}
    return f'''<!DOCTYPE html>
<html lang="{lang}" data-lang="{lang}"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{E(title)} — Non Dubito</title>
<meta name="description" content="{E(desc)}"><meta name="author" content="Han Qin (秦汉)">
<meta property="og:type" content="{'website' if slug == 'index' else 'article'}">
<meta property="og:title" content="{E(title)} — Non Dubito"><meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}"><meta name="twitter:card" content="summary">
<link rel="canonical" href="{url}">
{alternates(slug)}
<link rel="icon" type="image/svg+xml" href="../../../favicon.svg">
<link rel="stylesheet" href="../../../style.css"><link rel="stylesheet" href="../meaning.css?v=20260917">
<script defer src="../language-menu.js?v=20260917"></script>
<script type="application/ld+json">{json.dumps(structured, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token":"1c920752456e42b5b5469641245a07c2"}}'></script>
</head><body>
<header><div class="header-inner">
<a href="../../{lang}/index.html" class="site-title"><span class="title-latin">Non <span style="color:var(--gold)">Dubito</span></span></a>
<nav><a href="../../{lang}/index.html">{E(ui['home'])}</a><a href="../../../start.html">{E(ui['start'])}</a><a href="../../../library.html">{E(ui['library'])}</a><a href="https://credesivis.org/index.html">Crede si vis</a><a href="../../../about.html">{E(ui['about'])}</a><a href="https://self-as-an-end.net" target="_blank" rel="noopener">{E(ui['theory'])} ↗</a><a href="https://hqin.substack.com" target="_blank" rel="noopener">Substack ↗</a></nav>
</div></header>
{content}
<footer><div class="footer-inner"><div class="footer-brand"><div class="footer-logo">Non <span>Dubito</span></div></div><div class="footer-links"><a href="../../{lang}/index.html">{E(ui['home'])}</a><a href="../../../library.html">{E(ui['library'])}</a><a href="https://self-as-an-end.net">{E(ui['theory'])}</a></div></div><div class="footer-bottom"><span>© 2026 Han Qin (秦汉) · <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></span><span>nondubito.net</span></div></footer>
</body></html>
'''


def render_index(data):
    rows = []
    for i, a in enumerate(data['articles'], 1):
        further = ' further-reading' if i == 8 else ''
        label = f'{i:02}' + (' · ' + data['ui']['further'] if i == 8 else '')
        rows.append(f'<a class="entry-row{further}" href="{a["slug"]}.html"><span class="entry-num">{E(label)}</span><h2>{E(a["title"])}</h2><p>{E(a["description"])}</p></a>')
    intro = '\n'.join(f'<p>{E(p)}</p>' for p in data['intro'])
    rows_html = '\n'.join(rows)
    content = f'''<main class="series-container meaning-edition" data-search="{E(data['series_label'])} SAE meaning theory">
{menu('index', data['language'], data['ui']['language'])}
<a class="back-link" href="../../{data['language']}/index.html">← {E(data['ui']['home'])}</a>
<p class="series-label">{E(data['series_label'])}</p><h1 class="series-title">{E(data['series_title'])}</h1>
<div class="series-desc">{intro}</div><p class="series-meta">Han Qin · {E(data['count_label'])}</p>
<div class="reading-note"><p>{E(data['reading_note'])}</p><a href="ep01.html">{E(data['start_label'])}</a></div>
<div class="entry-list">{rows_html}</div>
<p class="source-note">{E(data['source_note'])}</p><p class="edition-note">{E(data['edition_note'])}</p>
</main>'''
    return document(data, 'index', content)


def render_article(data, i):
    a = data['articles'][i]
    ui = data['ui']
    parts = []
    for section in a['sections']:
        if section['heading']:
            parts.append('<h2>' + E(section['heading']) + '</h2>')
        parts += ['<p>' + E(p) + '</p>' for p in section['paragraphs']]
    before = data['articles'][i - 1] if i else None
    after = data['articles'][i + 1] if i < 7 else None
    prev_href = before['slug'] + '.html' if before else 'index.html'
    prev_label = ui['previous'] + ': ' + before['title'] if before else ui['contents']
    next_href = after['slug'] + '.html' if after else 'index.html'
    next_label = ui['next'] + ': ' + after['title'] if after else ui['contents']
    prose_html = '\n'.join(parts)
    content = f'''<main class="essay-main meaning-edition" data-search="{E(data['series_label'])} SAE meaning theory"><article>
<header class="essay-header">
{menu(a['slug'], data['language'], ui['language'])}
<a class="back-link" href="index.html">← {E(data['series_label'])}</a>
<div class="essay-titles"><p class="essay-series">{E(data['series_label'])} · {i + 1:02} / 08</p><h1>{E(a['title'])}</h1></div>
<div class="essay-meta"><span class="author">Han Qin (秦汉)</span></div></header>
<div class="essay-body">{prose_html}</div>
<div class="method-citations">{citations(a['slug'], data)}</div>
<div class="series-tail"><p class="edition-note">{E(data['edition_note'])}</p><div class="series-nav"><a href="{prev_href}">← {E(prev_label)}</a><a href="{next_href}">{E(next_label)} →</a></div></div>
</article></main>'''
    return document(data, a['slug'], content)


def replace_block(source, start, end, replacement):
    assert source.count(start) == source.count(end)
    if start in source:
        assert source.count(start) == 1
        return source[:source.index(start)] + replacement + source[source.index(end) + len(end):]
    return None


def outputs(languages=LANGUAGES):
    editions = {lang: load_edition(lang) for lang in languages}
    files = {}
    for lang, data in editions.items():
        files[SERIES / lang / 'index.html'] = render_index(data)
        for i, article in enumerate(data['articles']):
            files[SERIES / lang / (article['slug'] + '.html')] = render_article(data, i)
        hub = ROOT / 'essays' / lang / 'index.html'
        source = hub.read_text()
        start, end = '<!-- MEANING LANGUAGE HUB START -->', '<!-- MEANING LANGUAGE HUB END -->'
        card = f'''{start}<a href="../meaning/{lang}/index.html" class="essay-card" style="text-decoration:none;border-left:3px solid var(--gold);display:block;padding:2rem 2.25rem;margin:1rem 0;"><div style="font-family:var(--sans);font-size:.7rem;color:var(--green-light);margin-bottom:.7rem;">{E(data['series_label'])} · {E(data['count_label'])}</div><h3 style="font-size:1.45rem;font-weight:400;color:var(--ink);margin-bottom:.6rem;">{E(data['series_title'])}</h3><p style="font-size:.95rem;color:var(--ink-light);line-height:1.75;margin:0;">{E(data['description'])}</p></a>{end}'''
        updated = replace_block(source, start, end, card)
        if updated is None:
            marker = '<!-- sae-bridges-language-hub-cards -->'
            assert source.count(marker) == 1, (hub, 'missing theory hub anchor')
            updated = source.replace(marker, marker + card)
        files[hub] = updated
    # An individual edition can be previewed while the other authored files
    # are still in progress. Only a complete build exposes menus on base pages.
    if tuple(languages) != LANGUAGES:
        return files
    for slug in SLUGS:
        path = SERIES / (slug + '.html')
        source = path.read_text()
        source, count = re.subn(r'<div class="lang-toggle[^"\n]*"[^>]*>.*?</div>', menu(slug), source, count=1, flags=re.S)
        assert count == 1, path
        start, end = '<!-- MEANING ALTERNATES START -->', '<!-- MEANING ALTERNATES END -->'
        source = replace_block(source, start, end, alternates(slug)) or source.replace('</head>', alternates(slug) + '</head>')
        if 'src="language-menu.js' not in source:
            source = source.replace('</head>', '<script defer src="language-menu.js?v=20260917"></script></head>')
        if 'href="meaning.css' not in source:
            source = source.replace('</head>', '<link rel="stylesheet" href="meaning.css?v=20260917"></head>')
        source = source.replace('href="meaning.css"', 'href="meaning.css?v=20260917"')
        source = source.replace('src="reading-mode.js"', 'src="reading-mode.js?v=20260917-full"')
        source = source.replace(f'src="zh-hant-data/{slug}.js"', f'src="zh-hant-data/{slug}.js?v=20260917-full"')
        if slug == 'index':
            source = source.replace('English and both Chinese scripts', 'Eight languages')
            source = source.replace('简体、繁体与独立英文版', '八种语言')
        files[path] = source
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--language', choices=LANGUAGES, help='Preview one edition; full build required before release')
    args = parser.parse_args()
    changed = []
    for path, content in outputs((args.language,) if args.language else LANGUAGES).items():
        if not path.exists() or path.read_text() != content:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
    print(('STALE: ' if args.check and changed else 'Updated: ') + str(len(changed)) + ' files')
    if args.check and changed:
        print('\n'.join(changed))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
