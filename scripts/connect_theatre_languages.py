"""Connect the 2026-11-24 theatre edition expansion to existing discovery."""
import argparse
import json
import re

from build_home_updates import localized, render_section, replace_section
from theatre_language_batch import ROOT, DATE, LANGUAGES, CATALOG, E

ID = f'{DATE}-theatre-three-eight-languages'
URL = 'essays/theatre/index.html'
TITLE = {'en':'Theatre & Musicals: three essays now in eight languages',
         'zh':'戏剧与音乐剧：《过去五年》《激情》《拉格泰姆》补齐八语',
         'zh-hant':'戲劇與音樂劇：《過去五年》《激情》《拉格泰姆》補齊八語'}
SUMMARY = {
    'en':'The Last Five Years, Passion and Ragtime now have complete English, Japanese, French, German, Spanish and Korean editions alongside the Chinese originals. Twenty-six of the thirty-five essays are available in all eight languages.',
    'zh':'《过去五年》《激情》《拉格泰姆》在简繁中文版之外，新增英、日、法、德、西、韩全文。三十五篇中已有二十六篇可读八语。',
    'zh-hant':'《過去五年》《激情》《拉格泰姆》在簡繁中文版之外，新增英、日、法、德、西、韓全文。三十五篇中已有二十六篇可讀八語。'
}


def shelf_copy():
    return {
        'en':'Thirty-five essays on characters, songs and shared lives. Twenty-six are in all eight languages; the other nine have Simplified and Traditional Chinese editions.',
        'zh':'三十五部音乐剧，从人物、歌声与舞台谈共同生活。二十六篇提供八语，其余九篇提供简繁中文。',
        'zh-hant':'三十五部音樂劇，從人物、歌聲與舞台談共同生活。二十六篇提供八語，其餘九篇提供簡繁中文。'}


def outputs():
    ledger_path = ROOT/'data/site-updates.json'
    ledger = json.loads(ledger_path.read_text())
    baseline = [u for u in ledger['updates'] if u['id'] != ID]
    index = next(i for i,u in enumerate(baseline) if u['date'] < DATE)
    following = baseline[index]['id']
    item = {'id':ID, 'date':DATE, 'kind':'expanded', 'domain':'stories',
            'url':URL, 'languages':['en','zh','zh-hant',*LANGUAGES], 'title':TITLE, 'summary':SUMMARY}
    updates = baseline[:index] + [item] + baseline[index:]
    ledger['updates'] = updates
    result = {ledger_path:json.dumps(ledger,ensure_ascii=False,indent=2)+'\n'}
    prefix = 'THEATRE 2026-11-24 LATEST'
    section = (f'<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-theatre-languages-20261124">'
               f'<header class="updates-date"><h2 id="date-theatre-languages-20261124"><time datetime="{DATE}">{DATE}</time></h2></header>'
               f'<div class="updates-grid"><article class="update-card" data-update-id="{ID}"><div class="update-meta"><span class="update-kind">'
               +localized({'en':'Expanded','zh':'语言拓展','zh-hant':'語言拓展'})
               +'</span><span>EN · 简 · 繁 · 日本語 · Français · Deutsch · Español · 한국어</span></div>'
               +localized(TITLE,'h3')+localized(SUMMARY,'p')
               +f'<a class="update-link" href="{URL}">'+localized({'en':'Browse the collection →','zh':'进入栏目 →','zh-hant':'進入欄目 →'})
               +'</a></article></div></section></div></section>')
    latest_path = ROOT/'latest.html'
    text = latest_path.read_text()
    marker = f'<!-- {prefix} START -->'
    close = f'<!-- {prefix} END -->'
    if marker not in text:
        next_card = text.index(f'data-update-id="{following}"')
        section_start = text.rfind('<section class="updates-section">',0,next_card)
        assert section_start >= 0
        previous = re.search(r'<!-- [^<>]* START -->\s*$',text[:section_start])
        if previous:
            section_start = previous.start()
        text = text[:section_start]+marker+close+'\n'+text[section_start:]
    pattern = re.escape(marker)+r'.*?'+re.escape(close)
    text, n = re.subn(pattern,lambda _:marker+section+close,text,flags=re.S)
    assert n == 1
    result[latest_path] = text

    home = ROOT/'index.html'
    config = json.loads((ROOT/'data/home-updates.json').read_text())
    result[home] = replace_section(home.read_text(),render_section(updates,config))
    explore = ROOT/'explore.html'
    raw = explore.read_text()
    pattern = r'(<a class="shelf-link" href="'+re.escape(URL)+r'">)(.*?)(</a>)'
    def shelf(m):
        new, count = re.subn(r'<p class="lang-en">.*?</p><p class="lang-zh">.*?</p><p class="lang-hant">.*?</p>',
                              lambda _:localized(shelf_copy(),'p'),m[2],flags=re.S)
        assert count == 1
        return m[1]+new+m[3]
    raw,count = re.subn(pattern,shelf,raw,flags=re.S)
    assert count == 1
    result[explore] = raw

    for lang in LANGUAGES:
        path = ROOT/f'essays/{lang}/index.html'
        title, description, count, *_ = CATALOG[lang]
        card = (f'<section class="essays-section" style="padding:2rem 0"><a href="../theatre/{lang}/index.html" class="essay-card" '
                'style="display:block;text-decoration:none;border-left:3px solid var(--gold);padding:2rem">'
                f'<h2 style="font-size:1.6rem;font-weight:400">{E(title)}</h2><p>{E(description)}</p><p>{E(count)}</p></a></section>')
        from connect_full_series_languages import block
        anchor = '<div id="language-library" class="language-channel-library-anchor" aria-hidden="true"></div>'
        result[path] = block(path.read_text(),'THEATRE 2026-11-22 CHANNEL',card,anchor)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    args = p.parse_args()
    for path,text in outputs().items():
        if args.check:
            assert path.read_text()==text,path
        elif path.read_text()!=text:
            path.write_text(text)
    print('OK: scoped theatre channels, Explore, Home and 2026-11-24 update')


if __name__ == '__main__':
    main()
