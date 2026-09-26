#!/usr/bin/env python3
"""Build the curated humor shelf, without one thin page per joke.

Editorial input is versioned in data/humor. Originals in Documents are untouched.
Only text is converted to traditional Chinese; URLs and identifiers never are.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from import_fairy_tales import TraditionalConverter

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'essays/humor'
DATA_DIR = ROOT / 'data/humor'
ORIGIN = 'https://nondubito.net/'


def load_data():
    data = {'sources': {}, 'issues': [], 'batches': []}
    for path in sorted(DATA_DIR.glob('selection-*.json')):
        batch = json.loads(path.read_text())
        for key, source in batch['sources'].items():
            if key in data['sources'] and data['sources'][key] != source:
                raise ValueError(f'Conflicting source: {key}')
            data['sources'][key] = source
        issues = [dict(issue, date=batch['date']) for issue in batch['issues']]
        data['batches'].append(issues)
        data['issues'].extend(issues)
    if not data['issues']:
        raise ValueError('No humor selections found')
    data['date'] = min(i['date'] for i in data['issues'])
    data['modified'] = max(i['date'] for i in data['issues'])
    return data


def render_pages():
    data = load_data()
    total = sum(len(i['jokes']) for i in data['issues'])
    description = f"{total} 则来自不同地方的旧笑话，编成 {len(data['issues'])} 个短辑。先笑一会儿；出处与版本收在每则后面。"
    converter = TraditionalConverter()
    outputs = {}
    for lang in ('zh', 'zh-hant'):
        hant = lang == 'zh-hant'
        base = '../../../' if hant else '../../'
        folder = TARGET / 'zh-hant' if hant else TARGET
        language = 'zh-Hant' if hant else 'zh-Hans'

        def t(value):
            if hant:
                value = converter.convert(value).replace('“', '「').replace('”', '」').replace('‘', '『').replace('’', '』')
                value = value.replace('乾活', '幹活').replace('復述', '複述').replace('賬', '帳').replace('不咸', '不鹹')
                value = value.replace('輕輕鬆松', '輕輕鬆鬆').replace('包扎', '包紮').replace('鬥篷', '斗篷').replace('准是', '準是')
            return html.escape(value)

        def page(filename, title, description, content, article=False):
            relative = (folder / filename).relative_to(ROOT).as_posix()
            canonical_file = '' if filename == 'index.html' else filename
            url = ORIGIN + (relative.removesuffix('index.html') if filename == 'index.html' else relative)
            hans_url = ORIGIN + 'essays/humor/' + canonical_file
            hant_url = ORIGIN + 'essays/humor/zh-hant/' + canonical_file
            hans_link = '../' + filename + '?lang=zh' if hant else filename + '?lang=zh'
            hant_link = filename if hant else 'zh-hant/' + filename
            schema = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': html.unescape(t(title)),
                      'url': url, 'inLanguage': language, 'description': html.unescape(t(description)),
                      'datePublished': article['date'] if article else data['date'],
                      'editor': {'@type': 'Person', 'name': 'Han Qin'},
                      'isPartOf': {'@type': 'WebSite', 'name': 'Non Dubito', 'url': ORIGIN}}
            if not article:
                schema['dateModified'] = data['modified']
            if article:
                schema['hasPart'] = [{'@type': 'CreativeWork', 'name': html.unescape(t(j['title'])),
                                      'url': url + '#' + j['id'], 'inLanguage': language,
                                      'citation': data['sources'][j['source']]['url']} for j in article['jokes']]
            return f'''<!doctype html>
<html lang="{language}" data-lang="{lang}" data-editions="{language}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t(title)} — Non Dubito</title>
<meta name="description" content="{t(description)}">
<meta property="og:type" content="website"><meta property="og:title" content="{t(title)} — Non Dubito">
<meta property="og:description" content="{t(description)}"><meta property="og:url" content="{url}">
<meta property="og:locale" content="{'zh_TW' if hant else 'zh_CN'}"><meta name="twitter:card" content="summary">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="zh-Hans" href="{hans_url}"><link rel="alternate" hreflang="zh-Hant" href="{hant_url}">
<link rel="icon" href="{base}favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{base}style.css"><link rel="stylesheet" href="{'../' if hant else ''}humor.css">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<', chr(92)+'u003c')}</script>
<script defer src="{'../' if hant else ''}humor.js"></script>
</head>
<body class="humor-page">
<a class="humor-skip" href="#main">{t('跳到正文')}</a>
<header class="humor-header"><a class="humor-brand" href="{base}index.html?lang={lang}">Non <span>Dubito</span></a>
<nav class="humor-main-nav" aria-label="{t('网站导航')}"><a href="{base}explore.html?lang={lang}">{t('探索')}</a><a href="{base}library.html?lang={lang}">{t('书库')}</a><a href="{base}latest.html?lang={lang}">{t('最近更新')}</a><a href="{base}search.html?lang={lang}">{t('搜索')}</a></nav>
<nav class="humor-languages" aria-label="{t('选择阅读语言')}"><a href="{hans_link}" lang="zh-Hans" data-humor-language="zh" {'aria-current="page"' if not hant else ''}>简体</a><a href="{hant_link}" lang="zh-Hant" data-humor-language="zh-hant" {'aria-current="page"' if hant else ''}>繁體</a></nav></header>
<main id="main" class="humor-main">{content}</main>
<footer class="humor-footer"><a href="{base}essays/everyday/stories/index.html?lang={lang}">{t('也去读读：故事里的结构')} →</a><p>{t('Non Dubito · 笑话选 · 编选与中文译写：秦汉')}</p><p>{t('故事的作者、辑录者与所据版本，见各则出处。')}</p></footer>
</body></html>
'''

        groups, jumps = [], []
        start = 1
        for batch in data['batches']:
            end = start + len(batch) - 1
            anchor = f'issues-{start:02}-{end:02}'
            label = f'{start:02}–{end:02}'
            jumps.append(f'<a href="#{anchor}">{label}</a>')
            cards = []
            for i, issue in enumerate(batch, start):
                cards.append(f'<a class="humor-issue" href="{issue["slug"]}.html"><span class="humor-number">{i:02}</span><div><h3>{t(issue["title"])}</h3><p>{t(issue["deck"])}</p><span class="humor-meta">{t("六则 · 约两三分钟")}</span></div><span aria-hidden="true">↗</span></a>')
            groups.append(f'<section class="humor-group" id="{anchor}" aria-labelledby="{anchor}-title"><h2 id="{anchor}-title">{t("第")} {label} {t("辑")}</h2>{"".join(cards)}</section>')
            start = end + 1
        introduction = f'''<div class="humor-breadcrumb"><a href="{base}library.html?lang={lang}">← {t('书库')}</a></div>
<section class="humor-hero"><p class="humor-kicker">NON DUBITO · {t('笑话选')}</p><h1>{t('笑话选')}</h1><p class="humor-deck">{t('从不同地方传来的笑话，关于我们怎样生活，又怎样把自己绕进去。')}</p><p class="humor-welcome">{t('先笑一会儿。想查来处，每则后面都有；不想查，就接着读。')}</p><p class="humor-meta">{t(f"{len(data['issues'])} 个短辑 · {total} 则 · 简体 / 繁体")}</p><a class="humor-start" href="{data['batches'][-1][0]['slug']}.html">{t('读最新一批')} →</a><p class="humor-meta"><a href="{data['issues'][0]['slug']}.html">{t('也可以从第一辑读起')} →</a></p></section>
<nav class="humor-jump" aria-label="{t('按辑数跳转')}"><span>{t('跳到')}</span>{''.join(jumps)}</nav>
<div class="humor-issues">{''.join(groups)}</div>
<details class="humor-editorial"><summary>{t('关于这份选本')}</summary><div><p>{t('这里收录旧笑话、诙谐轶事和少量带有喜剧意味的故事，不是原创小说，也不把书中轶事当作已证实的历史。中文根据所列版本译述或改写，题目多为编选时另拟。')}</p><p>{t('出处标明我们读到的版本，不声称已经找到了故事最早的源头。工作稿中的理论分类与分析留在编辑档案里；这里不逐则讲道理。')}</p><p>{t('这一批先提供简体与繁体中文。英文将另行打磨，不以机器直译替代笑话的节奏。第三辑末则写到临终与天堂。')}</p></div></details>'''
        outputs[folder / 'index.html'] = page('index.html', '笑话选', description, introduction)
        for index, issue in enumerate(data['issues']):
            articles = []
            for i, joke in enumerate(issue['jokes'], 1):
                source = data['sources'][joke['source']]
                paragraphs = ''.join(f'<p>{t(p)}</p>' for p in joke['paragraphs'])
                articles.append(f'''<article class="humor-joke" id="{joke['id']}" aria-labelledby="title-{joke['id']}"><p class="humor-joke-number">{i:02}</p><h2 id="title-{joke['id']}">{t(joke['title'])}</h2><div class="humor-prose">{paragraphs}</div><details class="humor-source"><summary>{t('出处与版本')}<span class="humor-sr-only">：{t(joke['title'])}</span></summary><div><p><a href="{html.escape(source['url'])}">{t(source['label'])} ↗</a></p><p>{t(joke['locator'])}</p><p>{t(source['note'])} {t(joke['note'])}</p><a class="humor-permalink" href="#{joke['id']}">{t('本则固定链接')}</a></div></details></article>''')
            previous = data['issues'][index-1] if index else None
            following = data['issues'][index+1] if index+1 < len(data['issues']) else None
            prev_link = f'<a rel="prev" href="{previous["slug"]}.html">← {t(previous["title"])}</a>' if previous else '<span></span>'
            next_link = f'<a rel="next" href="{following["slug"]}.html">{t(following["title"])} →</a>' if following else f'<a href="index.html">{t("回到笑话选")} →</a>'
            contents = ''.join(f'<a href="#{j["id"]}">{t(j["title"])}</a>' for j in issue['jokes'])
            content = f'''<div class="humor-breadcrumb"><a href="index.html">← {t('笑话选')}</a><span>{t('第')} {index+1:02} {t('辑 / 六则')}</span></div>
<section class="humor-hero humor-reading-hero"><p class="humor-kicker">{t('笑话选')} · {index+1:02}</p><h1>{t(issue['title'])}</h1><p class="humor-deck">{t(issue['deck'])}</p><p class="humor-meta">{t('编选与中文译写：秦汉 · 约两三分钟')}</p></section>
<details class="humor-contents"><summary>{t('这一辑的六则')}</summary><nav aria-label="{t('本辑目录')}">{contents}</nav></details>
{''.join(articles)}<nav class="humor-next" aria-label="{t('前后短辑')}">{prev_link}{next_link}</nav><p class="humor-end"><a href="index.html">{t('全部短辑')}</a> · <a href="#main">{t('回到页首')}</a></p>'''
            outputs[folder / (issue['slug'] + '.html')] = page(issue['slug'] + '.html', issue['title'] + ' · 笑话选', issue['deck'], content, issue)
    return outputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs = render_pages()
    if args.check:
        stale = [str(p.relative_to(ROOT)) for p, text in outputs.items() if not p.exists() or p.read_text() != text]
        if stale:
            raise SystemExit('Stale humor pages: ' + ', '.join(stale))
    else:
        for path, text in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    data = load_data()
    total = sum(len(i['jokes']) for i in data['issues'])
    print(f'OK: {len(outputs)} humor pages, {total} jokes in two Chinese editions')


if __name__ == '__main__':
    main()
