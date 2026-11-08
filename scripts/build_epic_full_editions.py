#!/usr/bin/env python3
"""Overlay received complete Epic translations at the existing reading URLs.

Chinese regions change only at five explicitly approved source points. Received
ordered blocks and
review receipts are canonical inputs; the older compact builder calls this
overlay so an ordinary rebuild cannot restore its abbreviated prose.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/epic-full'
SERIES = ROOT / 'essays/everyday/stories/epic-traditions'
LANGS = ('zh-Hans', 'zh-Hant', 'en', 'ja', 'fr', 'de', 'es', 'ko')
FOREIGN = ('en', 'ja', 'fr', 'de', 'es', 'ko')
CORRECTIONS = DATA / 'author-corrections-20261108.json'
APPROVED_SOURCE_POINTS = {(1, 174), (2, 34), (8, 2), (8, 132), (16, 219)}
RESTORED_WORDING_POINTS = {(14, 0), (14, 212), (15, 0)}
NOTES = {
    'ja': '中国語全文に基づく完全翻訳。本文の全段落、区切り、末尾のテキスト根拠を収録しています。',
    'fr': 'Traduction intégrale du texte chinois, comprenant tous les paragraphes, les séparations et la note finale sur les sources.',
    'de': 'Vollständige Übersetzung des chinesischen Textes mit sämtlichen Absätzen, Abschnittstrennungen und dem abschließenden Quellenhinweis.',
    'es': 'Traducción íntegra del texto chino, con todos sus párrafos, separaciones y la nota final sobre las fuentes.',
    'ko': '중국어 전문을 바탕으로 한 완역입니다. 본문의 모든 문단과 구분, 마지막 텍스트 근거를 포함합니다.',
}
STYLE = """<style id="epic-full-style">
.collection-body.full-edition p{margin:0 0 1.55em;line-height:1.95}
.collection-body.full-edition hr{border:0;border-top:1px solid var(--cream-border);margin:2.6rem 0}
.collection-body.full-edition em{color:var(--ink-muted);font-size:.9em}
.collection-page,.story-wrap{overflow-wrap:anywhere}
.collection-page h1,.collection-card h2,.collection-nav a{min-width:0}
html[lang="ko"] .collection-body{word-break:keep-all}
html[lang="ja"] .collection-body,html[lang="ko"] .collection-body{font-family:var(--cjk),var(--serif),serif}
</style>"""

def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()

def plain(value):
    return html.unescape(re.sub(r'<[^>]+>', '', value)).strip()

def inline(value):
    # The verified input format contains only plain text, *emphasis* and
    # **strong emphasis**. Escape first; never execute supplier HTML.
    assert not any(c in value for c in ('<', '>', '[', ']')), ('Unsupported inline syntax', value)
    value = html.escape(value, quote=False)
    value = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', value)
    value = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', value)
    assert '*' not in value, ('Unbalanced emphasis', value)
    return value

def div_span(text, cls):
    for m in re.finditer(r'<div\b[^>]*>', text):
        classes = re.search(r'class="([^"]*)"', m[0])
        if classes and cls in classes[1].split():
            depth = 1
            for n in re.finditer(r'</?div\b[^>]*>', text[m.end():]):
                depth += -1 if n[0].startswith('</') else 1
                if depth == 0:
                    return m.start(), m.end(), m.end() + n.start(), m.end() + n.end()
            raise AssertionError(('Unclosed div', cls))
    raise AssertionError(('Missing div', cls))

def within(text, cls, fn):
    _, a, b, _ = div_span(text, cls)
    return text[:a] + fn(text[a:b]) + text[b:]

def region(text, cls):
    a, _, _, b = div_span(text, cls)
    return text[a:b]

def author_edits():
    if not CORRECTIONS.exists():
        return []
    receipt = json.loads((DATA / 'received.json').read_text())
    assert digest(CORRECTIONS.read_bytes()) == receipt['correction_receipts'][CORRECTIONS.name], 'Author correction receipt changed'
    record = json.loads(CORRECTIONS.read_text())
    edits = record['edits']
    source = [e for e in edits if e['kind'] == 'approved_source']
    expected = {(ep, lang, block) for ep, block in APPROVED_SOURCE_POINTS for lang in LANGS}
    assert {(e['episode'], e['lang'], e['block']) for e in source} == expected
    assert len(source) == len(expected), 'Duplicate approved source edit'
    for e in edits:
        assert e['before'].strip() and e['after'].strip()
        if e['kind'] == 'restore_source_wording':
            assert e['lang'] in FOREIGN and (e['episode'], e['block']) in RESTORED_WORDING_POINTS
        else:
            assert e['kind'] == 'approved_source'
    return edits

def approved_chinese_region(filename, code):
    baseline = json.loads((DATA / 'chinese-baseline.json').read_text())
    source = (SERIES / filename) if filename == 'index.html' else DATA / 'received/source-snapshots' / (filename + '.txt')
    original = region(source.read_text(), 'lang-' + code)
    assert digest(original) == baseline[filename][code], ('Original Chinese baseline changed', filename, code)
    if filename == 'index.html':
        return original
    episode = int(filename[:2])
    lang = {'zh': 'zh-Hans', 'hant': 'zh-Hant'}[code]
    expected = original
    for e in author_edits():
        if (e['episode'], e['lang']) != (episode, lang):
            continue
        assert e['kind'] == 'approved_source'
        before = '<p>' + inline(e['before']) + '</p>'
        after = '<p>' + inline(e['after']) + '</p>'
        assert expected.count(before) == 1, ('Original Chinese paragraph mismatch', episode, lang, e['block'])
        expected = expected.replace(before, after, 1)
    return expected

def editions():
    receipt = json.loads((DATA / 'received.json').read_text())
    edits = []
    for p in sorted((DATA / 'reviews').glob('*.json')):
        edits.extend(json.loads(p.read_text()).get('edits', []))
    assert all(e['lang'] in FOREIGN for e in edits), 'Source edits need explicit author receipt'
    edits.extend(author_edits())
    used = set()
    result = {}
    for item in receipt['essays']:
        copies = {}
        for lang in LANGS:
            p = DATA / 'received/alignment' / f"{item['episode']:02}.{lang}.json"
            raw = p.read_bytes()
            assert digest(raw) == receipt['files'][str(p.relative_to(DATA))], ('Received input changed', p)
            blocks = json.loads(raw)
            assert blocks[0]['tag'] == 'h1' and all(b['tag'] in ('p', 'hr') for b in blocks[1:])
            assert all(b['text'].strip() for b in blocks if b['tag'] != 'hr')
            for e in edits:
                if (e['episode'], e['lang']) != (item['episode'], lang):
                    continue
                key = (e['episode'], lang, e['block'])
                assert key not in used, ('Duplicate edit', key)
                used.add(key)
                assert blocks[e['block']]['text'] == e['before'], ('Stale edit', key)
                blocks[e['block']]['text'] = e['after']
            copies[lang] = blocks
        assert len({tuple(b['tag'] for b in bs) for bs in copies.values()}) == 1
        result[item['slug']] = copies
    assert len(result) == 20 and len(used) == len(edits)
    return result

def body(blocks):
    return '\n'.join('<hr />' if b['tag'] == 'hr' else '<p>' + inline(b['text']) + '</p>' for b in blocks[1:])

def title(blocks):
    return plain(inline(blocks[0]['text']))

def navigation(text, lang, all_editions, current_slug):
    def link(m):
        opening, content, closing = m.groups()
        href = re.search(r'href="([^"]+)"', opening)
        if not href or 'lang-btn' in opening:
            return m[0]
        url = urlsplit(html.unescape(href[1]))
        if url.scheme or url.netloc or url.path.startswith('../'):
            return m[0]
        slug = Path(url.path).stem
        if slug not in all_editions:
            return m[0]
        name = html.escape(title(all_editions[slug][lang]), quote=False)
        if 'collection-card' in opening:
            content = re.sub(r'(<h2[^>]*>).*?(</h2>)', lambda n:n[1]+name+n[2], content, flags=re.S)
        elif 'essay-card' in opening:
            content = re.sub(r'(<h3[^>]*>).*?(</h3>)', lambda n:n[1]+name+n[2], content, flags=re.S)
        elif 'series-nav-btn' in opening:
            content = re.sub(r'(</small>).*?(</span>)', lambda n:n[1]+name+n[2], content, count=1, flags=re.S)
        elif re.match(r'<span>\d{2}</span>', content):
            content = re.sub(r'(</span>).*', lambda n:n[1]+name, content, count=1, flags=re.S)
        elif content.startswith('<small>'):
            previous = current_slug in all_editions and int(slug[:2]) < int(current_slug[:2])
            content = re.sub(r'(</small>).*', lambda n:n[1]+('← ' if previous else '')+name+('' if previous else ' →'), content, flags=re.S)
        return opening + content + closing
    return re.sub(r'(<a\b[^>]*>)(.*?)(</a>)', link, text, flags=re.S)

def metadata(text, name):
    text = re.sub(r'<title>.*?</title>', lambda m:'<title>'+html.escape(name)+' — Non Dubito</title>', text, count=1, flags=re.S)
    return re.sub(r'(<meta property="og:title" content=")[^"]*(">)', lambda m:m[1]+html.escape(name, quote=True)+m[2], text, count=1)

def style(text):
    text = re.sub(r'<style id="epic-full-style">.*?</style>\n?', '', text, flags=re.S)
    return text.replace('</head>', STYLE + '\n</head>', 1)

def protect_existing_foreign_prose(paths, all_editions):
    # A compact builder may supply freshly rendered summaries, but never use
    # that as permission to discard unrelated edits in the actual checkout.
    # Accept either the received full edition or this approved corrected one.
    for path in paths:
        if not path.is_relative_to(SERIES) or path.stem not in all_editions:
            continue
        lang = 'en' if path.parent == SERIES else path.parent.name
        if lang not in FOREIGN or not path.exists():
            continue
        current = path.read_text()
        if lang == 'en':
            current = region(current, 'lang-en')
        current_body = within_body(current, 'article-body' if lang == 'en' else 'collection-body')
        original = json.loads((DATA / 'received/alignment' / f'{int(path.stem[:2]):02}.{lang}.json').read_text())
        corrected = all_editions[path.stem][lang]
        assert current_body.strip() in (body(original).strip(), body(corrected).strip()), (
            'Foreign HTML prose changed; preserve intentional edits in canonical input before rebuilding', path)
        heading = re.search(r'<h1[^>]*>(.*?)</h1>', current, re.S)
        assert heading and plain(heading[1]) in (title(original), title(corrected)), (
            'Foreign HTML title changed; preserve intentional edits in canonical input before rebuilding', path)

def within_body(text, cls):
    _, a, b, _ = div_span(text, cls)
    return text[a:b]

def upgrade_outputs(outputs):
    all_editions = editions()
    protect_existing_foreign_prose(outputs, all_editions)
    baseline = json.loads((DATA / 'chinese-baseline.json').read_text())
    for path, text in list(outputs.items()):
        if not path.is_relative_to(SERIES):
            continue
        lang = 'en' if path.parent == SERIES else path.parent.name
        if lang not in FOREIGN:
            continue
        slug = path.stem
        if lang == 'en':
            for code in ('zh', 'hant'):
                expected = approved_chinese_region(path.name, code)
                current = region(text, 'lang-' + code)
                assert digest(current) in (baseline[path.name][code], digest(expected)), ('Chinese source drift', path, code)
                a, _, _, z = div_span(text, 'lang-' + code)
                text = text[:a] + expected + text[z:]
            def upgrade_english(part):
                if slug in all_editions:
                    part = within(part, 'article-body', lambda _:body(all_editions[slug]['en']))
                    part = re.sub(r'(<h1[^>]*>).*?(</h1>)', lambda m:m[1]+html.escape(title(all_editions[slug]['en']))+m[2], part, count=1, flags=re.S)
                return navigation(part, 'en', all_editions, slug)
            text = within(text, 'lang-en', upgrade_english)
            if slug in all_editions:
                text = metadata(text, title(all_editions[slug]['en']))
            for code in ('zh', 'hant'):
                assert region(text, 'lang-'+code) == approved_chinese_region(path.name, code)
        else:
            if slug in all_editions:
                text = within(text, 'collection-body', lambda _:body(all_editions[slug][lang]))
                text = re.sub(r'class="collection-body(?: full-edition)?"', 'class="collection-body full-edition"', text, count=1)
                text = re.sub(r'(<h1[^>]*>).*?(</h1>)', lambda m:m[1]+html.escape(title(all_editions[slug][lang]))+m[2], text, count=1, flags=re.S)
                text = re.sub(r'(<p class="edition-note"><em>).*?(</em></p>)', lambda m:m[1]+NOTES[lang]+m[2], text, count=1, flags=re.S)
                text = metadata(text, title(all_editions[slug][lang]))
            text = navigation(text, lang, all_editions, slug)
        outputs[path] = style(text)
    return outputs

def render():
    return upgrade_outputs({p:p.read_text() for p in SERIES.rglob('*.html')})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs = render()
    stale = [p for p, text in outputs.items() if p.read_text() != text]
    if args.check:
        assert not stale, ('Stale Epic editions', stale)
        print(f'OK: 20 complete eight-language essays; {len(outputs)} pages up to date')
    else:
        for p in stale:
            p.write_text(outputs[p])
        print(f'Updated {len(stale)} Epic pages')

if __name__ == '__main__':
    main()
