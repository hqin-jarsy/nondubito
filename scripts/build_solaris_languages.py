#!/usr/bin/env python3
"""Render the approved Solaris revision, preserving its primary URLs and redirects."""
import argparse
import html
import json
import re
from pathlib import Path

import don_literary_render as layout
from full_series_languages import render_prose
from prepare_action_sources import Document
from web_analytics import ensure_analytics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/solaris/multilingual'
PRIMARY = {'en': 'en', 'zh': 'zh', 'zh-hant': 'hant'}
FULL_LABEL = {'en': '8 languages', 'zh': '八语阅读', 'zh-hant': '八語閱讀'}
BACK = {'en': 'Return to series', 'zh': '返回系列', 'zh-hant': '返回系列'}
COUNTS = {'ja': '3篇 · 8言語', 'fr': '3 essais · 8 langues', 'de': '3 Essays · 8 Sprachen',
          'es': '3 ensayos · 8 idiomas', 'ko': '글 3편 · 8개 언어'}
E = html.escape

# Initial query beats persisted preference. Explicit switches keep a bookmarked or
# refreshed URL, its other query parameters, and same-series navigation in sync.
LANG_SCRIPT = """<script data-solaris-language>
(function () {
  var allowed = ['en', 'zh', 'zh-hant'];
  var requested = new URLSearchParams(location.search).get('lang');
  var saved = localStorage.getItem('nd_lang') || localStorage.getItem('nondubito-lang');
  var initial = allowed.indexOf(requested) >= 0 ? requested : (allowed.indexOf(saved) >= 0 ? saved : 'zh');
  function apply(lang) {
    document.documentElement.setAttribute('data-lang', lang);
    document.documentElement.lang = lang === 'zh-hant' ? 'zh-Hant' : (lang === 'zh' ? 'zh-Hans' : 'en');
  }
  apply(initial);
  document.addEventListener('DOMContentLoaded', function () {
    var buttons = document.querySelectorAll('.lang-btn[data-lang]');
    function update(lang) {
      buttons.forEach(function (button) {
        var active = button.getAttribute('data-lang') === lang;
        button.classList.toggle('active', active);
        button.setAttribute('aria-pressed', String(active));
      });
      document.querySelectorAll('.essay-card[href], .essay-nav a[href], .back-link[href]').forEach(function (link) {
        var url = new URL(link.getAttribute('href'), location.href);
        if (url.origin !== location.origin) return;
        url.searchParams.set('lang', lang);
        link.href = url.href;
      });
    }
    buttons.forEach(function (button) {
      button.addEventListener('click', function () {
        var lang = this.getAttribute('data-lang');
        apply(lang);
        localStorage.setItem('nd_lang', lang);
        localStorage.setItem('nondubito-lang', lang);
        var url = new URL(location.href);
        url.searchParams.set('lang', lang);
        history.replaceState(history.state, '', url.href);
        update(lang);
      });
    });
    update(initial);
  });
})();
</script>"""


def once(pattern, replacement, text, label):
    result, count = re.subn(pattern, replacement, text, flags=re.S)
    assert count == 1, (label, count)
    return result


def article_body(article, series, position, end_note=True):
    prose = render_prose(article['body'])
    if end_note and position > 0:
        prose += '<aside class="edition-note"><p>' + E(series['source_note']) + '</p></aside>'
    return prose


def series_body(payload, lang):
    series = payload['series']
    cards = []
    for numeral, article in zip(('I', 'II', 'III'), payload['articles']):
        label = FULL_LABEL.get(lang, COUNTS.get(lang, '')).split(' · ')[-1]
        cards.append(f'<a href="{article["slug"]}.html" class="essay-card">'
                     f'<span class="card-num">{numeral}</span><div class="card-body">'
                     f'<h2>{E(article["title"])}</h2><p class="card-desc">{E(article["deck"])}</p>'
                     f'<div class="card-meta"><span class="card-badge full">{E(label)}</span></div></div></a>')
    return (f'<p class="sf-intro">{E(series["deck"])}</p><p class="edition-note">{E(series["source_note"])}</p>'
            '<div class="essay-list" style="margin-top:3rem">' + ''.join(cards) + '</div>')


def navigation(articles, lang, position):
    links = []
    if position:
        article = articles[position - 1]
        links.append(f'<a href="{article["slug"]}.html">← {E(article["title"])}</a>')
    if position + 1 < len(articles):
        article = articles[position + 1]
        links.append(f'<a href="{article["slug"]}.html">{E(article["title"])} →</a>')
    else:
        label = BACK[lang] if lang in BACK else layout.ui[lang][0]
        links.append(f'<a href="index.html">{E(label)} →</a>')
    return '<div class="essay-nav">' + ''.join(links) + '</div>'


def primary_page(path, directory, slug, position, data, foreign):
    text = path.read_text()
    doc = Document(text)
    nodes = list(doc.root.walk())
    edits = []
    for language, suffix in PRIMARY.items():
        payload = data[language]
        articles = payload['articles']
        series = payload['series']
        article = None if position is None else articles[position]
        node = next(n for n in nodes if n.has('essay-page-title', 'lang-' + suffix))
        edits.append((node.open_end, node.close_start, E((article or series)['title'])))
        node = next(n for n in nodes if n.has('essay-body', 'lang-' + suffix))
        content = series_body(payload, language) if article is None else (
            article_body(article, series, position) + navigation(articles, language, position))
        edits.append((node.open_end, node.close_start, content))
    for a, b, replacement in sorted(edits, reverse=True):
        text = text[:a] + replacement + text[b:]
    item = data['en']['series'] if position is None else data['en']['articles'][position]
    title = item['title'] + ' — Non Dubito'
    text = once(r'<title>[^<]*</title>', lambda _: '<title>' + E(title) + '</title>', text, slug)
    for key, value in [('description', item['deck']), ('og:description', item['deck']), ('og:title', title)]:
        text = once(r'(<meta (?:name|property)="' + re.escape(key) + r'" content=")[^"]*',
                    lambda m: m[1] + E(value, quote=True), text, key)
    text = once(r'<script data-solaris-language>.*?</script>|<script>\s*\(function\(\)\{var saved=.*?</script>',
                lambda _: LANG_SCRIPT, text, slug + ' language')
    text = re.sub(r'<link rel="alternate"[^>]+>\s*', '', text)
    text = text.replace('</head>', layout.hreflang(directory, slug) + '\n</head>', 1)
    doc = Document(text)
    toggle = next(n for n in doc.root.walk() if n.has('lang-toggle'))
    links = ''.join(f'<span class="lang-sep">|</span><a class="lang-btn" lang="{lang}" '
                    f'href="{lang}/{slug}.html">{layout.names[lang]}</a>' for lang in foreign)
    if 'href="ja/' not in doc.raw(toggle):
        text = text[:toggle.close_start] + links + text[toggle.close_start:]
    text = text.replace('class="lang-toggle" style="margin-bottom:.8rem;"',
                        'class="lang-toggle" style="margin-bottom:.8rem;display:flex;flex-wrap:wrap;"')
    for old, new in (
        ('English · Simplified · Traditional', 'Eight languages'), ('英文 · 简体 · 繁体', '八语阅读'),
        ('英文 · 簡體 · 繁體', '八語閱讀'), ('Independent English edition', 'English translation of the revised Chinese essay'),
        ('中文原作 · 简 / 繁', '中文原作 · 八语阅读'), ('中文原作 · 簡 / 繁', '中文原作 · 八語閱讀')
    ):
        text = text.replace(old, new)
    return ensure_analytics(text)


def parent_cards(path, data):
    text = path.read_text()
    doc = Document(text)
    cards = [n for n in doc.root.walk() if n.tag == 'a' and n.attrs.get('href') == 'solaris/index.html']
    assert len(cards) == 3
    search = ' '.join(data[l]['series']['title'] + ' ' + data[l]['series']['deck'] for l in PRIMARY)
    search += ' Stanisław Lem 斯坦尼斯瓦夫·莱姆 斯坦尼斯瓦夫·萊姆'
    for card, lang in reversed(list(zip(cards, PRIMARY))):
        raw = doc.raw(card)
        series = data[lang]['series']
        raw = once(r'data-search="[^"]*"', lambda _: 'data-search="' + E(search, quote=True) + '"', raw, lang)
        raw = once(r'(<h2[^>]*>).*?(</h2>)', lambda m: m[1] + E(series['title']) + m[2], raw, lang)
        raw = once(r'(<p[^>]*>).*?(</p>)', lambda m: m[1] + E(series['deck']) + m[2], raw, lang)
        raw = raw.replace('EN / 简 / 繁', '8 languages').replace('英 / 简 / 繁', '八语').replace('英 / 簡 / 繁', '八語')
        text = text[:card.start] + raw + text[card.end:]
    return text


def explore_link(path, directory, data, slugs):
    url = directory + '/' + slugs[-1] + '.html'
    old = directory + '/5-where-contact-begins.html'
    def replacement(_):
        labels = ''.join(f'<span class="lang-{suffix}">{E(data[lang]["series"]["title"])}：'
                         f'{E(data[lang]["articles"][-1]["title"])}</span>' if lang != 'en'
                         else f'<span class="lang-en">Solaris: {E(data[lang]["articles"][-1]["title"])}</span>'
                         for lang, suffix in PRIMARY.items())
        return f'<a href="{url}">{labels}</a>'
    return once(r'<a href="(?:' + re.escape(old) + '|' + re.escape(url) + r')">.*?</a>',
                replacement, path.read_text(), 'Explore Solaris')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    profile = json.loads((DATA / 'profile.json').read_text())
    directory = profile['directory']
    folder = ROOT / directory
    slugs = profile['slugs']
    foreign = profile['languages']
    data = {lang: json.loads((DATA / f'{lang}.json').read_text()) for lang in [*PRIMARY, *foreign]}
    for lang, payload in data.items():
        assert [a['slug'] for a in payload['articles']] == slugs, lang
        assert [len(a['body']) for a in payload['articles']] == [6, 6, 6], lang
    outputs = {}
    for pos, slug in enumerate(['index', *slugs]):
        path = folder / (slug + '.html')
        outputs[path] = primary_page(path, directory, slug, pos - 1 if pos else None, data, foreign)
    for lang in foreign:
        payload = data[lang]
        series = payload['series']
        articles = payload['articles']
        dest = folder / lang
        for pos, article in enumerate(articles):
            slug = article['slug']
            outputs[dest / (slug + '.html')] = layout.page(
                directory, lang, slug, article['title'], article['deck'], series['title'],
                article_body(article, series, pos), navigation(articles, lang, pos), f'{pos + 1} / 3')
        outputs[dest / 'index.html'] = layout.page(
            directory, lang, 'index', series['title'], series['deck'], series['title'],
            series_body(payload, lang), count=COUNTS[lang])
    parent = folder.parent / 'index.html'
    outputs[parent] = parent_cards(parent, data)
    explore = ROOT / 'explore.html'
    outputs[explore] = explore_link(explore, directory, data, slugs)
    for path, contents in outputs.items():
        if args.check:
            assert path.read_text() == contents, path
        else:
            path.parent.mkdir(exist_ok=True)
            path.write_text(contents)
    print(f'Solaris: 3 approved essays in eight languages, {len(outputs)-2} physical pages; '
          'historic URLs and two redirects retained.')


if __name__ == '__main__':
    main()
