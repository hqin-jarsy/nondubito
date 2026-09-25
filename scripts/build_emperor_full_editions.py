#!/usr/bin/env python3
"""Render reviewed Emperor Markdown into existing, stable-URL site templates.

Only episodes with all seven source files are published. Traditional Chinese
continues to use the site's offline reading map, rebuilt after this script.
The compact collection builder calls upgrade_outputs too, so it cannot replace
reviewed full editions with its older three-paragraph records.
"""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
import markdown

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / 'essays/emperor'
DATA = ROOT / 'data/emperor-full'
LANGS = ('zh', 'en', 'ja', 'fr', 'de', 'es', 'ko')
STYLE = '''<style id="emperor-full-style">
.full-edition p{margin:0 0 1.35em;line-height:1.9;overflow-wrap:anywhere}
.full-edition h2{margin:2.5em 0 .85em;line-height:1.4}
.full-edition sup{font-size:.7em;line-height:0}
.full-edition .full-sources{margin-top:3rem;padding-top:1.5rem;border-top:1px solid var(--cream-border)}
.full-edition .full-sources p{font-size:.86rem;line-height:1.75}
.full-edition [id]{scroll-margin-top:110px}
</style>'''

def editions():
    result = {}
    for path in sorted(DATA.glob('ep*.zh.md')):
        slug = path.name.split('.')[0]
        copies = {}
        for lang in LANGS:
            p = DATA / f'{slug}.{lang}.md'
            source = p.read_text(encoding='utf-8')
            heading = re.match(r'# (.+)\n+', source)
            if not heading:
                raise ValueError(f'Missing title: {p}')
            body = source[heading.end():].strip()
            split = list(re.finditer(r'^#{2,3} (.+)$', body, re.M))[-1]
            label = split[1]
            if not re.search(r'Sources|Quellen|Fuentes|史|사료',label):
                raise ValueError(f'Missing source section: {p}')
            main, notes = body[:split.start()].strip(), body[split.end():].strip()
            # The first returned package uses a numbered list, later packages
            # use [n] paragraphs. Both become the same accessible link targets.
            notes = re.sub(r'^(\d+)\. ', r'[\1] ', notes, flags=re.M)
            definitions = set(re.findall(r'^\[(\d+)\]', notes, re.M))
            references = set(re.findall(r'\[(\d+)\](?!\()', main + '\n' + notes))
            if references - definitions:
                raise ValueError(f'Unresolved notes in {p}: {references-definitions}')
            notes = re.sub(r'^\[(\d+)\]\s*', lambda m: f'<a id="note-{lang}-{m[1]}"></a>\n\n**{m[1]}.** ',notes,flags=re.M)
            notes = re.sub(r'(?<!\n)\n(<a id="note-)', r'\n\n\1',notes)
            main_html = markdown.markdown(main)
            main_html = re.sub(r'\[(\d+)\]',lambda m:f'<sup><a href="#note-{lang}-{m[1]}" aria-label="{m[1]}">{m[1]}</a></sup>',main_html)
            notes_html = markdown.markdown(notes)
            notes_html = re.sub(r'\[(\d+)\]', lambda m: f'<a href="#note-{lang}-{m[1]}">{m[1]}</a>', notes_html)
            rendered = f'<div class="full-edition" data-edition="2026-09-24">\n{main_html}\n<section class="full-sources"><h2>{html.escape(label)}</h2>\n{notes_html}\n</section>\n</div>'
            paragraphs = [p for p in main.split('\n\n') if not p.startswith(('#','<','>'))]
            deck = re.sub(r'\[(\d+)\]|[*_]', '', ' '.join(paragraphs[:2])).strip()
            # Unicode character count is only a display bound, not a prose metric.
            deck = deck if len(deck) <= 220 else deck[:217].rsplit(' ',1)[0] + '…'
            copies[lang] = dict(title=heading[1], deck=deck, body=rendered)
        result[slug] = copies
    return result

def replace_div(text, class_name, body):
    start = re.search(r'<div\b[^>]*class="'+re.escape(class_name)+r'"[^>]*>',text)
    if not start:
        raise ValueError('Missing body '+class_name)
    depth = 1
    for tag in re.finditer(r'</?div\b[^>]*>',text[start.end():]):
        depth += -1 if tag[0].startswith('</') else 1
        if depth == 0:
            end = start.end()+tag.start()
            return text[:start.end()]+'\n'+body+'\n'+text[end:]
    raise ValueError('Unclosed body '+class_name)

def article(text, slug, lang, all_editions):
    copies = all_editions[slug]
    if lang == 'zh':
        for code in ('zh','en'):
            text = replace_div(text, f'essay-body lang-{code}', copies[code]['body'])
            text = re.sub(r'(<h1 class="lang-'+code+r'"[^>]*>).*?(</h1>)', lambda m:m[1]+html.escape(copies[code]['title'])+m[2],text,flags=re.S)
    else:
        klass = 'collection-body' if 'class="collection-body"' in text else 'essay-body'
        # The Japanese template nests navigation in its body. Keep it outside
        # the imported prose, rather than dropping the next/previous controls.
        nav = ''
        if klass == 'essay-body':
            found = re.search(r'<nav class="xiyou-nav">.*?</nav>',text,re.S)
            nav = found[0] if found else ''
        text = replace_div(text, klass, copies[lang]['body']+nav)
        text = re.sub(r'(<h1\b[^>]*>).*?(</h1>)',lambda m:m[1]+html.escape(copies[lang]['title'])+m[2],text,count=1,flags=re.S)
        text = re.sub(r'(<p class="(?:collection-deck|essay-subtitle)"[^>]*>).*?(</p>)',lambda m:m[1]+html.escape(copies[lang]['deck'])+m[2],text,count=1,flags=re.S)
    copy = copies[lang]
    text = re.sub(r'<title>.*?</title>',lambda m:'<title>'+html.escape(copy['title'])+' — Non Dubito</title>',text,count=1,flags=re.S)
    for key,value in [('description',copy['deck']),('og:description',copy['deck']),('og:title',copy['title'])]:
        text = re.sub(r'(<meta\b[^>]*(?:name|property)="'+key+r'"[^>]*content=")[^"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],text)
    text = re.sub(r'<style id="emperor-full-style">.*?</style>\n?', '',text,flags=re.S)
    return text.replace('</head>', STYLE+'\n</head>',1)

def navigation(text, lang, all_editions):
    def link(m):
        opening, contents, closing = m[1],m[2],m[3]
        if 'lang-btn' in opening:
            return m[0]
        target = re.search(r'href="(?:\.\./)?(ep\d{2})\.html(?:\?[^"]*)?"',opening)
        if not target or target[1] not in all_editions:
            return m[0]
        slug = target[1]
        copies = all_editions[slug]
        if lang == 'zh':
            for code in ('zh','en'):
                for klass,key in [('card-title-'+code,'title'),('card-desc','deck'),('xiyou-nav-title','title')]:
                    pattern=r'(<(?:div|p|span)\b[^>]*class="[^"\n]*'+klass+r'[^"\n]*lang-'+code+r'[^"\n]*"[^>]*>).*?(</(?:div|p|span)>)'
                    contents=re.sub(pattern,lambda n:n[1]+html.escape(copies[code][key])+n[2],contents,flags=re.S)
        else:
            copy=copies[lang]
            if 'collection-card' in opening:
                contents=re.sub(r'(<h2>).*?(</h2>)',lambda n:n[1]+html.escape(copy['title'])+n[2],contents,flags=re.S)
                contents=re.sub(r'(<p>).*?(</p>)',lambda n:n[1]+html.escape(copy['deck'])+n[2],contents,flags=re.S)
            elif 'essay-card' in opening or 'xiyou-nav' in opening:
                contents=re.sub(r'(<(?:div|span)\b[^>]*class="(?:card-title[^"\n]*|xiyou-nav-title)"[^>]*>).*?(</(?:div|span)>)',lambda n:n[1]+html.escape(copy['title'])+n[2],contents,flags=re.S)
            elif re.match(r'<small>',contents):
                contents=re.sub(r'(</small>).*',lambda n:n[1]+html.escape(copy['title']),contents,flags=re.S)
        return opening+contents+closing
    text=re.sub(r'(<a\b[^>]*>)(.*?)(</a>)',link,text,flags=re.S)
    if lang == 'ja':
        text=re.sub(r'href="\.\./(ep\d{2}\.html)"(?= class="essay-card")',r'href="\1"',text)
        text=text.replace('中英双語版','日本語版')
    return text

def upgrade_outputs(outputs):
    all_editions=editions()
    for path,text in list(outputs.items()):
        if not path.is_relative_to(SERIES):
            continue
        lang='zh' if path.parent==SERIES else path.parent.name
        if lang not in LANGS:
            continue
        if path.stem in all_editions:
            text=article(text,path.stem,lang,all_editions)
        outputs[path]=navigation(text,lang,all_editions)
    return outputs

def render():
    return upgrade_outputs({p:p.read_text(encoding='utf-8') for p in SERIES.rglob('*.html')})

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    outputs=render()
    stale=[p for p,s in outputs.items() if p.read_text(encoding='utf-8')!=s]
    if args.check:
        if stale:
            raise SystemExit('Stale full editions: '+', '.join(str(p.relative_to(ROOT)) for p in stale))
        print(f'OK: {len(editions())} Emperor full editions and series navigation')
        return
    for p in stale:
        p.write_text(outputs[p],encoding='utf-8')
    print(f'Updated {len(stale)} Emperor pages')

if __name__=='__main__':
    main()
