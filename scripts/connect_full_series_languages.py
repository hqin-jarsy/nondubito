#!/usr/bin/env python3
"""Publish discovery links for a reviewed full-length multilingual series."""
import argparse
import html
import json
import re

from full_series_languages import ROOT, load_language, profile, edition_count
from build_home_updates import render_section, replace_section


def localized(values, tag='span', css=''):
    return ''.join(f'<{tag} class="lang-{suffix}{" "+css if css else ""}">{html.escape(values[lang])}</{tag}>' for lang,suffix in [('en','en'),('zh','zh'),('zh-hant','hant')])


def block(text, name, content, anchor):
    start, end = f'<!-- {name} START -->', f'<!-- {name} END -->'
    if start in text:
        assert text.count(start) == text.count(end) == 1
        return re.sub(re.escape(start)+r'.*?'+re.escape(end), lambda _:start+content+end, text, flags=re.S)
    assert text.count(anchor) == 1, (name, anchor)
    return text.replace(anchor, start+content+end+'\n'+anchor, 1)


def render(series):
    spec = profile(series)
    entry = json.loads((ROOT/'data'/series/'multilingual/discovery.json').read_text())
    ledger = json.loads((ROOT/'data/site-updates.json').read_text())
    old_ids = [u['id'] for u in ledger['updates']]
    public_entry = {k:v for k,v in entry.items() if k != 'library_count'}
    if entry['id'] in old_ids:
        ledger['updates'][old_ids.index(entry['id'])] = public_entry
    else:
        ledger['updates'].insert(0, public_entry)
        ledger['updates'].sort(key=lambda u:u['date'], reverse=True)
    pages = {ROOT/'data/site-updates.json':json.dumps(ledger,ensure_ascii=False,indent=2)+'\n'}
    mark = 'FULL SERIES '+series.upper()+' LATEST'
    card = f'<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-{series}-languages"><header class="updates-date"><h2 id="date-{series}-languages"><time datetime="{entry["date"]}">{entry["date"]}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{entry["id"]}"><div class="update-meta"><span class="update-kind">'+localized({'en':'Five complete language editions','zh':'新增五语全文','zh-hant':'新增五語全文'})+'</span><span>EN · 简 · 繁 · DE · FR · ES · 日本語 · 한국어</span></div>'+localized(entry['title'],'h3')+localized(entry['summary'],'p')+f'<a href="{entry["url"]}">'+localized({'en':'Read the series →','zh':'阅读系列 →','zh-hant':'閱讀系列 →'})+'</a></article></div></section></div></section>'
    latest = (ROOT/'latest.html').read_text()
    first = latest.index('<section class="updates-section">')
    comment = latest.rfind('<!--', 0, first)
    anchor = latest[comment:first] if comment >= 0 and re.fullmatch(r'<!--[^<>]+-->\s*',latest[comment:first]) else '<section class="updates-section">'
    if anchor == '<section class="updates-section">' and latest.count(anchor)>1:
        # Inserting at the actual offset avoids ambiguous repeated section tags.
        latest = latest[:first]+f'<!-- {mark} START -->'+card+f'<!-- {mark} END -->\n'+latest[first:] if f'<!-- {mark} START -->' not in latest else block(latest,mark,card,'unused')
    else:
        latest = block(latest,mark,card,anchor)
    pages[ROOT/'latest.html'] = latest
    config = json.loads((ROOT/'data/home-updates.json').read_text())
    pages[ROOT/'index.html'] = replace_section((ROOT/'index.html').read_text(), render_section(ledger['updates'],config))
    for language in spec['languages']:
        _, data = load_language(series,language)
        path = ROOT/f'essays/{language}/index.html'
        source = path.read_text()
        anchor = '<div id="language-library" class="language-channel-library-anchor" aria-hidden="true"></div>'
        card = f'<section class="essays-section" style="padding:2rem 0"><a href="../{series}/{language}/index.html" class="essay-card" style="display:block;text-decoration:none;border-left:3px solid var(--gold);padding:2rem"><p style="font-family:var(--sans);font-size:.8rem;color:var(--green)">{html.escape(data["ui"]["series"])}</p><h2 style="font-size:1.6rem;font-weight:400">{html.escape(data["series"]["title"])}</h2><p>{html.escape(data["series"]["deck"])}</p><p>{edition_count(language,len(data["articles"]))}</p></a></section>'
        pages[path] = block(source,'FULL SERIES '+series.upper()+' CHANNEL',card,anchor)
    path = ROOT/'library.html'
    source = path.read_text()
    pattern = r'(<a href="'+re.escape(entry['url'])+r'" class="series-card">\s*<span class="series-card-count">).*?(</span>\s*<div class="series-card-title-zh)'
    def count(match):
        values = entry['library_count']
        labels = ''.join(f'<span class="lang-{suffix}{" cl-"+suffix if suffix in ("zh","hant") else ""}">{html.escape(values[code])}</span>' for code,suffix in [('en','en'),('zh','zh'),('zh-hant','hant')])
        labels = labels.replace('class="lang-hant cl-hant"','class="lang-zh cl-hant"')
        return match[1]+labels+match[2]
    source, n = re.subn(pattern,count,source,flags=re.S)
    assert n == 1, ('Library series card missing or ambiguous',series)
    pages[path] = source
    return pages


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    pages=render(args.series)
    for path,text in pages.items():
        if args.check:
            assert path.read_text()==text, path
        else:
            path.write_text(text)
    print(f'{args.series}: language channels, Library, Latest, ledger and bounded Home '+('checked' if args.check else 'connected'))


if __name__=='__main__':
    main()
