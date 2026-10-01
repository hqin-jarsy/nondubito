#!/usr/bin/env python3
"""Publish explicitly reviewed World Football batches at their existing URLs.

Archive import is opt-in and refuses to overwrite reviewed sources. Ordinary
builds use checked-in Markdown and receipts only; no translation service is used.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile

import markdown
from build_emperor_full_editions import replace_div

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / 'essays/worldcup'
DATA = ROOT / 'data/worldcup-full'
RECEIPT = DATA / 'review.json'
LANGS = ('de', 'fr', 'es', 'ja', 'ko')
TOC = {'de': 'In diesem Essay', 'fr': 'Dans cet essai', 'es': 'En este ensayo', 'ja': 'この篇の目次', 'ko': '이 글의 목차'}
STYLE = '''<style id="worldcup-full-style">
.worldcup-full p{overflow-wrap:anywhere}
.worldcup-full h2{line-height:1.55;scroll-margin-top:90px}
.worldcup-toc{width:calc(100% - 2rem);max-width:var(--max-w);margin:1.5rem auto;padding:1rem 1.5rem;border:1px solid var(--cream-border)}
.worldcup-toc summary{cursor:pointer;font-family:var(--sans);color:var(--ink-muted)}
.worldcup-toc ul{margin:1rem 0 0;padding-left:1.4rem}
.worldcup-toc li{margin:.5rem 0;line-height:1.6;overflow-wrap:anywhere}
.worldcup-toc a{color:var(--ink-light)}
.essay-header h1,.essay-subtitle,.card-title-en,[class$="nav-title"]{overflow-wrap:anywhere}
</style>'''


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def render(text):
    # German dates at the beginning of a paragraph are prose, not numbered lists.
    text = re.sub(r'(?m)^(\d{1,2})\. (?=(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\b)',
                  lambda m: m[1]+'\\. ', text)
    return markdown.markdown(text)


def paragraph_counts(text):
    return [render(s.strip()).count('<p>')
            for s in re.split(r'^## .*$', text, flags=re.M)[1:]]


def import_batch(folder, plan_path):
    plan = json.loads(plan_path.read_text())
    receipt = json.loads(RECEIPT.read_text()) if RECEIPT.exists() else dict(
        baseline_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        protected_files={p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in SERIES.glob('*.html')},
        archives={}, manuscripts={}, batches=[])
    assert plan['batch'] not in [b['batch'] for b in receipt['batches']], 'Batch already imported'
    prepared = {}
    for ep in plan['episodes']:
        assert re.fullmatch(r'ep\d{2}', ep) and 1 <= int(ep[2:]) <= 22
        assert ep not in receipt['archives'], 'Refusing to replace an imported episode'
        archive = folder / f'NonDubito_WorldFootball_{ep.upper()}_DE_FR_ES_JA_KO_v1.0.zip'
        zh = (SERIES/f'{ep}.html').read_text().split('<div class="essay-body lang-zh"', 1)[1].split('<div class="essay-body lang-en"', 1)[0]
        expected = [len(re.findall(r'<p[ >]', s)) for s in re.split(r'<h3[^>]*>.*?</h3>', zh, flags=re.S)[1:]]
        assert expected and all(expected)
        receipt['archives'][ep] = dict(name=archive.name, sha256=digest(archive.read_bytes()))
        with ZipFile(archive) as archive_file:
            assert archive_file.testzip() is None and len(archive_file.namelist()) == 5
            for lang in LANGS:
                key = f'{ep}.{lang}'
                assert not (DATA/f'{key}.md').exists(), key
                names = [n for n in archive_file.namelist() if n.endswith(f'_{lang}.md')]
                assert len(names) == 1
                original_bytes = archive_file.read(names[0])
                original = original_bytes.decode('utf-8-sig')
                body = original[original.index('\n## '):].strip()
                edits = plan.get('edits', {}).get(key, [])
                for edit in edits:
                    assert body.count(edit['before']) == 1, (key, edit['before'])
                    body = body.replace(edit['before'], edit['after'], 1)
                title, deck = plan['titles'][key]
                full_title = title + ('：' if lang == 'ja' else ': ') + deck
                text = f'# {full_title}\n\n{body}\n'
                assert paragraph_counts(text) == expected, (key, paragraph_counts(text), expected)
                receipt['manuscripts'][key] = dict(title=title, deck=deck, full_title=full_title,
                    received_sha256=digest(original_bytes), published_sha256=digest(text.encode()),
                    paragraphs_by_section=expected, edits=edits,
                    removed_preface=original[:original.index('\n## ')].strip())
                prepared[DATA/f'{key}.md'] = text
    receipt['batches'].append(dict(plan, plan_file=plan_path.relative_to(ROOT).as_posix(),
                                 plan_sha256=digest(plan_path.read_bytes())))
    # Archive-to-source import is a mechanical build step; all copyedits are
    # explicit in the reviewed plan, and every input is validated before writes.
    DATA.mkdir(parents=True, exist_ok=True)
    for path, text in prepared.items():
        path.write_text(text)
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print(f'Imported {len(prepared)} reviewed manuscripts')


def manuscripts():
    receipt = json.loads(RECEIPT.read_text())
    out = {}
    for ep in receipt['archives']:
        assert all(f'{ep}.{lang}' in receipt['manuscripts'] for lang in LANGS)
    for key, record in receipt['manuscripts'].items():
        raw = (DATA/f'{key}.md').read_bytes()
        assert digest(raw) == record['published_sha256'], (key, 'Unrecorded edit')
        text = raw.decode()
        assert text.startswith('# '+record['full_title']+'\n')
        assert paragraph_counts(text) == record['paragraphs_by_section'], key
        headings = re.findall(r'^## (.+)$', text, re.M)
        rendered = render(text.split('\n', 1)[1].strip())
        counter = iter(range(1, len(headings)+1))
        rendered = re.sub('<h2>', lambda _: f'<h2 id="section-{next(counter)}">', rendered)
        out[key] = dict(record, body=rendered, headings=headings)
    return out


def update_links(text, copies):
    def anchor(match):
        found = re.search(r'href="(ep\d{2})\.html"', match[0])
        if not found or found[1] not in copies:
            return match[0]
        copy = copies[found[1]]
        return re.sub(r'(<(?:span|div) class="(?P<class>card-title-en|(?:xiyou|series|worldcup)-nav-title)"[^>]*>)(.*?)(</(?:span|div)>)',
                      lambda m: m[1]+html.escape(copy['full_title'] if m['class']=='card-title-en' else copy['title'])+m[4],
                      match[0], flags=re.S)
    return re.sub(r'<a\b[^>]*>.*?</a>', anchor, text, flags=re.S)


def outputs():
    all_copies = manuscripts()
    result = {}
    for lang in LANGS:
        copies = {key.split('.')[0]: value for key, value in all_copies.items() if key.endswith('.'+lang)}
        for path in sorted((SERIES/lang).glob('*.html')):
            text = path.read_text()
            if path.stem in copies:
                if 'src="../../../language-select.js"' not in text:
                    text = text.replace('</head>', '<script defer src="../../../language-select.js"></script>\n</head>',1)
                copy = copies[path.stem]
                text = replace_div(text, 'essay-body', '<div class="worldcup-full">\n'+copy['body']+'\n</div>')
                text = re.sub(r'(<h1\b[^>]*>).*?(</h1>)', lambda m:m[1]+html.escape(copy['title'])+m[2], text, count=1, flags=re.S)
                text = re.sub(r'<p class="essay-subtitle"[^>]*>.*?</p>\s*', '', text, flags=re.S)
                # Old compact templates put the next tag directly after h1.
                # Normalize this boundary before insertion, including first build.
                text = re.sub(r'</h1>\s*', '</h1>\n', text, count=1)
                text = text.replace('</h1>', '</h1>\n<p class="essay-subtitle">'+html.escape(copy['deck'])+'</p>\n', 1)
                text = re.sub(r'<title>.*?</title>', lambda _:'<title>'+html.escape(copy['full_title'])+' — Non Dubito</title>', text, count=1, flags=re.S)
                text = re.sub(r'(<meta property="og:title" content=")[^"]*(">)', lambda m:m[1]+html.escape(copy['full_title']+' — Non Dubito', quote=True)+m[2], text)
                text = re.sub(r'<details class="worldcup-toc">.*?</details>\s*', '', text, flags=re.S)
                toc = '<details class="worldcup-toc"><summary>'+TOC[lang]+'</summary><ul>'
                toc += ''.join(f'<li><a href="#section-{i}">{html.escape(h)}</a></li>' for i,h in enumerate(copy['headings'],1))
                toc += '</ul></details>\n'
                text = text.replace('<div class="essay-body">', toc+'<div class="essay-body">',1)
                text = re.sub(r'<style id="worldcup-full-style">.*?</style>\s*', '', text, flags=re.S)
                text = text.replace('</head>', STYLE+'\n</head>',1)
            text = update_links(text, copies)
            if path.stem in copies or path.stem == 'index' or text != path.read_text():
                if 'src="../../../language-select.js"' not in text:
                    text = text.replace('</head>', '<script defer src="../../../language-select.js"></script>\n</head>',1)
                result[path] = text
    return result


def refresh_indexes(changed):
    import build_search_index as search
    _, chunks = search.build()
    scope = {p.relative_to(ROOT).as_posix() for p in changed}
    for lang in LANGS:
        path = ROOT/f'data/search/{lang}.json'
        current = json.loads(path.read_text())
        fresh = {r['u']:r for r in chunks[lang] if r['u'] in scope}
        assert fresh.keys() <= {r['u'] for r in current['records']}
        current['records'] = [fresh.get(r['u'],r) for r in current['records']]
        path.write_text(search.serialized(current))
    path = ROOT/'sitemap.xml'
    text = path.read_text()
    for rel in scope:
        url = rel.removesuffix('index.html') if rel.endswith('/index.html') else rel
        pattern = r'(<loc>https://nondubito.net/'+re.escape(url)+r'</loc>\s*<lastmod>)[^<]*(</lastmod>)'
        text, count = re.subn(pattern, lambda m:m[1]+date.today().isoformat()+m[2], text)
        assert count == 1, rel
    path.write_text(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-archives',type=Path)
    parser.add_argument('--plan',type=Path)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--refresh-indexes',action='store_true')
    args = parser.parse_args()
    if bool(args.import_archives) != bool(args.plan) or (args.check and (args.import_archives or args.refresh_indexes)):
        parser.error('Import needs a plan; --check is read-only')
    if args.import_archives:
        import_batch(args.import_archives,args.plan.resolve())
    expected = outputs()
    changed = {p:s for p,s in expected.items() if p.read_text()!=s}
    if args.check:
        assert not changed, 'Stale pages: '+', '.join(str(p) for p in changed)
        print(f'OK: {len(manuscripts())} reviewed editions, indexes and neighbor labels are current')
    else:
        for path,text in changed.items():
            path.write_text(text)
        if args.refresh_indexes:
            refresh_indexes(changed)
        print(f'Updated {len(changed)} pages')


if __name__ == '__main__':
    main()
