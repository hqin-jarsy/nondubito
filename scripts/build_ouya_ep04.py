#!/usr/bin/env python3
"""Render only reviewed EP04 manuscripts; no translation during builds."""
import argparse
import hashlib
import html
import json
import re

import markdown
import build_ouya_full_editions as shared

ROOT, DATA, SERIES, LANGS = shared.ROOT, shared.DATA, shared.SERIES, shared.LANGS
DECKS = {
    'zh-Hans': '从凯撒遇刺到奥古斯都的权力组合：共和官职与程序仍在运作，最高权力却日益集中。一个名字的延续，如何不同于公民位置的延续？',
    'zh-Hant': '從凱撒遇刺到奧古斯都的權力組合：共和官職與程序仍在運作，最高權力卻日益集中。一個名字的延續，如何不同於公民位置的延續？',
    'en': 'From Caesar’s assassination to Augustus: how republican offices kept working while power concentrated around one man, and why preserving a name did not preserve citizens’ agency.',
    'ja': 'カエサルの暗殺からアウグストゥスへ。共和政の官職と手続きが働き続ける一方、権力は一人に集まる。名前の存続と市民の立場の違いをたどる。',
    'fr': 'De César à Auguste : les magistratures républicaines continuent de fonctionner, mais le pouvoir se concentre. Garder un nom ne suffit pas à préserver la capacité politique des citoyens.',
    'de': 'Von Caesar zu Augustus: Republikanische Ämter arbeiten weiter, während sich Macht bei einem Menschen sammelt. Ein alter Name allein bewahrt nicht die Handlungsmacht der Bürger.',
    'es': 'De César a Augusto: los cargos republicanos siguen funcionando mientras el poder se concentra. Conservar un nombre no basta para proteger la capacidad política de los ciudadanos.',
    'ko': '카이사르의 암살에서 아우구스투스까지. 공화정의 관직과 절차는 남았지만 권력은 한 사람에게 집중되었다. 이름의 지속과 시민의 자리는 어떻게 다른가.',
}
SOURCES = [
    ('Suetonius · Julius Caesar 76–84', 'https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Suetonius/12Caesars/Julius*.html'),
    ('Suetonius · Augustus 27–28, 35, 54', 'https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Suetonius/12Caesars/Augustus*.html'),
    ('Appian · Civil Wars IV.5–11', 'https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Appian/Civil_Wars/4*.html'),
    ('Velleius Paterculus · II.62', 'https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Velleius_Paterculus/2C*.html'),
    ('Plutarch · Antony 54–68', 'https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Antony*.html'),
    ('Augustus · Res Gestae 34–35', 'https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Augustus/Res_Gestae/6*.html'),
    ('Cassius Dio · LIII.12–18, 32', 'https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Cassius_Dio/53*.html'),
    ('Tacitus · Histories IV.48', 'https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Histories/4B*.html'),
]

def manuscripts():
    receipt = json.loads((DATA/'ep04-review.json').read_text())
    result = {}
    for lang in LANGS:
        raw = (DATA/f'ep04.{lang}.md').read_text()
        assert hashlib.sha256(raw.encode()).hexdigest() == receipt['published_sha256'][lang], lang
        blocks = raw.strip().split('\n\n')
        assert blocks[0].startswith('# ') and blocks[1].startswith('Han Qin')
        body = '\n\n'.join(blocks[2:])
        assert len(re.findall(r'^### ', body, re.M)) == 10, lang
        assert len([p for p in blocks[2:] if not p.startswith('### ')]) == 132, lang
        result[lang] = {'title': blocks[0][2:], 'body': body}
    return result

def body_html(lang, copy):
    text = markdown.markdown(re.sub(r'^### ', '## ', copy['body'], flags=re.M))
    sections = iter(range(1, 11))
    text = re.sub(r'<h2>', lambda _: f'<h2 id="{lang.lower()}-section-{next(sections)}">', text)
    label, note = shared.NOTES[lang]
    links = '\n'.join(f'<li><a href="{html.escape(url, quote=True)}">{html.escape(label)}</a></li>' for label, url in SOURCES)
    return f'<div class="ouya-full" data-edition="v0.1-local-20260929">\n{text}\n</div>\n<aside class="ouya-sources"><h2>{html.escape(label)}</h2><p>{html.escape(note)}</p><ul>{links}</ul></aside>'

def menu(lang):
    return shared.language_menu(lang).replace('ep01.html', 'ep04.html')

def outputs():
    copies = manuscripts()
    out = {}
    root = SERIES/'ep04.html'
    s = root.read_text()
    for code, lang in [('zh', 'zh-Hans'), ('en', 'en')]:
        s = shared.replace_div(s, 'essay-body lang-'+code, body_html(lang, copies[lang]))
        s = re.sub(r'(<h1 class="lang-'+code+r'">).*?(</h1>)', lambda m: m[1]+html.escape(copies[lang]['title'])+m[2], s, flags=re.S)
    s = re.sub(r'<div class="lang-toggle">.*?</div>', menu('root'), s, flags=re.S)
    s = re.sub(r'<script(?: id="ouya-inline-language")?>.*?</script>', lambda m: shared.STATE_SCRIPT if ('var saved' in m[0] or 'ouya-inline-language' in m[0]) else m[0], s, flags=re.S)
    s = shared.metadata(s, copies['zh-Hans']['title'], DECKS['zh-Hans'], 'https://nondubito.net/essays/ouya/ep04.html')
    out[root] = shared.resources(s, '../../')
    for lang in ('ja', 'fr', 'de', 'es', 'ko', 'zh-Hant'):
        p = SERIES/lang.lower()/'ep04.html'
        s = p.read_text() if p.exists() else (SERIES/'ja/ep04.html').read_text()
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
            s = re.sub(r'<div class="essay-series-label">.*?</div>', '<div class="essay-series-label">鑿構週期律 · 歐亞帝王系列 — 第04篇／共22篇</div>', s)
            subs = iter(['上一篇', '下一篇（簡體）'])
            titles = iter(['羅馬共和國', '四帝並存的歐亞'])
            s = re.sub(r'<span class="xiyou-nav-sub">.*?</span>', lambda _: f'<span class="xiyou-nav-sub">{next(subs)}</span>', s)
            s = re.sub(r'<span class="xiyou-nav-title">.*?</span>', lambda _: f'<span class="xiyou-nav-title">{next(titles)}</span>', s)
            s = re.sub(r'href="(?:\.\./)?ep05.html(?:\?lang=zh)?"(?: onclick="[^"]*")?', 'href="../ep05.html?lang=zh" onclick="try{localStorage.setItem(\'nd_lang\',\'zh\')}catch(e){}"', s)
        s = shared.metadata(s, copies[lang]['title'], DECKS[lang], f'https://nondubito.net/essays/ouya/{lang.lower()}/ep04.html')
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
    print(('OK' if args.check else 'Wrote')+': 7 EP04 URLs, 8 complete editions')

if __name__ == '__main__':
    main()
