#!/usr/bin/env python3
"""Render only reviewed EP03 manuscripts; no translation during builds."""
import argparse
import hashlib
import html
import json
import re

import markdown
import build_ouya_full_editions as shared

ROOT, DATA, SERIES, LANGS = shared.ROOT, shared.DATA, shared.SERIES, shared.LANGS
DECKS = {
    'zh-Hans': '罗马如何防止权力落到一个人手里？从执政官、元老院和护民官，到格拉古兄弟与苏拉，追问分散权力的制度如何承受帝国的尺度。',
    'zh-Hant': '羅馬如何防止權力落到一個人手裡？從執政官、元老院和護民官，到格拉古兄弟與蘇拉，追問分散權力的制度如何承受帝國的尺度。',
    'en': 'How did Rome resist one-man rule? From consuls, senators and tribunes to the Gracchi and Sulla, an essay on shared power and the strains of governing a Mediterranean empire.',
    'ja': 'ローマはどう権力の独占を防ごうとしたのか。執政官、元老院、護民官からグラックス兄弟とスッラへ。権力を分ける仕組みが帝国の規模に直面する過程をたどる。',
    'fr': "Comment Rome a-t-elle résisté au pouvoir d'un seul ? Des consuls et tribuns aux Gracques et à Sylla, un essai sur le partage du pouvoir à l'échelle d'un empire méditerranéen.",
    'de': 'Wie wollte Rom die Alleinherrschaft verhindern? Von Konsuln, Senat und Volkstribunen bis zu den Gracchen und Sulla: geteilte Macht unter den Belastungen eines Mittelmeerreichs.',
    'es': '¿Cómo intentó Roma impedir el poder de uno solo? De los cónsules, el Senado y los tribunos a los Graco y Sila: repartir el poder y gobernar un imperio mediterráneo.',
    'ko': '로마는 어떻게 한 사람의 권력 독점을 막으려 했을까? 집정관·원로원·호민관에서 그라쿠스 형제와 술라까지, 권력을 나누는 제도가 지중해 제국의 규모를 감당하는 과정을 따라간다.',
}
SOURCES = [
    ('Plutarch · Tiberius Gracchus (especially 19)', 'https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Tiberius_Gracchus*.html'),
    ('Plutarch · Caius Gracchus (especially 13–14)', 'https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Caius_Gracchus*.html'),
    ('Plutarch · Sulla (especially 31)', 'https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Sulla*.html'),
]

def manuscripts():
    receipt = json.loads((DATA/'ep03-review.json').read_text())
    result = {}
    for lang in LANGS:
        raw = (DATA/f'ep03.{lang}.md').read_text()
        assert hashlib.sha256(raw.encode()).hexdigest() == receipt['published_sha256'][lang], lang
        blocks = raw.strip().split('\n\n')
        assert blocks[0].startswith('# ') and blocks[1].startswith('Han Qin')
        body = '\n\n'.join(blocks[2:])
        assert len(re.findall(r'^## ', body, re.M)) == 10, lang
        assert len([p for p in blocks[2:] if not p.startswith('## ')]) == 128, lang
        result[lang] = {'title': blocks[0][2:], 'body': body}
    return result

def body_html(lang, copy):
    text = markdown.markdown(copy['body'])
    sections = iter(range(1, 11))
    text = re.sub(r'<h2>', lambda _: f'<h2 id="{lang.lower()}-section-{next(sections)}">', text)
    label, note = shared.NOTES[lang]
    links = '\n'.join(f'<li><a href="{html.escape(url, quote=True)}">{html.escape(label)}</a></li>' for label, url in SOURCES)
    return f'<div class="ouya-full" data-edition="v0.1-local-20260928">\n{text}\n</div>\n<aside class="ouya-sources"><h2>{html.escape(label)}</h2><p>{html.escape(note)}</p><ul>{links}</ul></aside>'

def menu(lang):
    return shared.language_menu(lang).replace('ep01.html', 'ep03.html')

def outputs():
    copies = manuscripts()
    out = {}
    root = SERIES/'ep03.html'
    s = root.read_text()
    for code, lang in [('zh', 'zh-Hans'), ('en', 'en')]:
        s = shared.replace_div(s, 'essay-body lang-'+code, body_html(lang, copies[lang]))
        s = re.sub(r'(<h1 class="lang-'+code+r'">).*?(</h1>)', lambda m: m[1]+html.escape(copies[lang]['title'])+m[2], s, flags=re.S)
    s = re.sub(r'<div class="lang-toggle">.*?</div>', menu('root'), s, flags=re.S)
    s = re.sub(r'<script(?: id="ouya-inline-language")?>.*?</script>', lambda m: shared.STATE_SCRIPT if ('var saved' in m[0] or 'ouya-inline-language' in m[0]) else m[0], s, flags=re.S)
    s = shared.metadata(s, copies['zh-Hans']['title'], DECKS['zh-Hans'], 'https://nondubito.net/essays/ouya/ep03.html')
    out[root] = shared.resources(s, '../../')
    for lang in ('ja', 'fr', 'de', 'es', 'ko', 'zh-Hant'):
        p = SERIES/lang.lower()/'ep03.html'
        s = p.read_text() if p.exists() else (SERIES/'ja/ep03.html').read_text()
        s = shared.replace_div(s, 'essay-body', body_html(lang, copies[lang]))
        s = re.sub(r'<html lang="[^"]*">', f'<html lang="{lang}">', s)
        s = re.sub(r'<div class="lang-toggle">.*?</div>', menu(lang), s, flags=re.S)
        s = re.sub(r'(<h1\b[^>]*>).*?(</h1>)', lambda m: m[1]+html.escape(copies[lang]['title'])+m[2], s, count=1, flags=re.S)
        s = re.sub(r'<p class="essay-subtitle">.*?</p>\s*', '', s, flags=re.S)
        s = re.sub(r'<a class="ouya-series-back".*?</a>\s*', '', s, flags=re.S)
        label = {'ja': '← シリーズ目次', 'fr': '← Tous les essais', 'de': '← Zur Reihe', 'es': '← Índice de la serie', 'ko': '← 시리즈 목차', 'zh-Hant': '← 系列目錄（簡體／English）'}[lang]
        href = 'index.html' if lang != 'zh-Hant' else '../index.html'
        s = s.replace('<header class="essay-header">', f'<a class="ouya-series-back" href="{href}">{label}</a>\n<header class="essay-header">', 1)
        if lang == 'zh-Hant':
            s = re.sub(r'<div class="essay-series-label">.*?</div>', '<div class="essay-series-label">鑿構週期律 · 歐亞帝王系列 — 第03篇／共22篇</div>', s)
            subs = iter(['上一篇', '下一篇（簡體）'])
            titles = iter(['亞歷山大與希臘化', '凱撒到奧古斯都'])
            s = re.sub(r'<span class="xiyou-nav-sub">.*?</span>', lambda _: f'<span class="xiyou-nav-sub">{next(subs)}</span>', s)
            s = re.sub(r'<span class="xiyou-nav-title">.*?</span>', lambda _: f'<span class="xiyou-nav-title">{next(titles)}</span>', s)
            s = re.sub(r'href="(?:\.\./)?ep04.html(?:\?lang=zh)?"(?: onclick="[^"]*")?', 'href="../ep04.html?lang=zh" onclick="try{localStorage.setItem(\'nd_lang\',\'zh\')}catch(e){}"', s)
        s = shared.metadata(s, copies[lang]['title'], DECKS[lang], f'https://nondubito.net/essays/ouya/{lang.lower()}/ep03.html')
        out[p] = shared.resources(s, '../../../')
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, text in outputs().items():
        if args.check:
            assert path.exists() and path.read_text() == text, f'Stale: {path}'
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(('OK' if args.check else 'Wrote')+': 7 EP03 URLs, 8 complete editions')

if __name__ == '__main__':
    main()
