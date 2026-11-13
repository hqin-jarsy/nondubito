#!/usr/bin/env python3
"""Connect one reviewed series without rewriting preceding update cards."""
import argparse
import json
import re
from build_reader_series import ROOT, registry, loc, ReaderTraditionalConverter
from build_language_writing import reading_map, WritingTraditionalConverter
from build_home_updates import render_home
from update_sae_navigation import render_library


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('series')
    args = parser.parse_args()
    s = next(s for s in registry() if s['slug'] == args.series)
    conv = ReaderTraditionalConverter()
    try:
        path = ROOT/'data/sae-reading-map.json'
        map_text = path.read_text()
        data = json.loads(map_text)
        target = f'essays/{s["slug"]}/index.html'
        group = next(g for g in data['groups'] if g['id']==s['shelf'])
        if not any(i[0]==target for g in data['groups'] for i in g['items']):
            item = [target,s['zh'],s['en']]
            previous = json.dumps(group['items'][-1],ensure_ascii=False,separators=(',',':'))
            assert map_text.count(previous)==1,'Preserve the existing compact reading-map format'
            map_text = map_text.replace(previous,previous+',\n      '+json.dumps(item,ensure_ascii=False,separators=(',',':')),1)
            group['items'].append(item)
            path.write_text(map_text)
        lib = ROOT/'library.html'
        lib.write_text(render_library(lib.read_text(),data['groups'],conv))
        map_conv = WritingTraditionalConverter()
        try:(ROOT/'essays/sae/index.html').write_text(reading_map(map_conv))
        finally:map_conv.close()
        ledger = ROOT/'data/site-updates.json'
        updates = json.loads(ledger.read_text())
        update_id = f'{s["date"]}-{s["slug"]}-reader-series'
        entry = dict(id=update_id,date=s['date'],kind='new',domain='sae',series_key=f'essays/{s["slug"]}',url=target,languages=['en','zh','zh-hant'],title={'en':s['en'],'zh':s['zh'],'zh-hant':conv.convert(s['zh'])},summary={'en':s['deck_en'],'zh':s['deck_zh'],'zh-hant':conv.convert(s['deck_zh'])})
        updates['updates'] = [entry]+[u for u in updates['updates'] if u['id']!=update_id]
        ledger.write_text(json.dumps(updates,ensure_ascii=False,indent=2)+'\n')
        marker = f'READER SERIES {s["slug"].upper()} LATEST'
        section = f'<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-reader-{s["slug"]}"><header class="updates-date"><h2 id="date-reader-{s["slug"]}"><time datetime="{s["date"]}">{s["date"]}</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="{update_id}"><div class="update-meta"><span class="update-kind">'+loc('New reader series','新增散文系列',conv)+'</span><span>EN / 简 / 繁</span></div>'+loc(s['en'],s['zh'],conv,'h3')+loc(s['deck_en'],s['deck_zh'],conv,'p')+f'<a href="{target}">'+loc('Read the series →','进入系列 →',conv)+'</a></article></div></section></div></section>'
        wrapped = f'<!-- {marker} START -->'+section+f'<!-- {marker} END -->'
        latest_path = ROOT/'latest.html'
        latest = latest_path.read_text()
        pattern = re.compile(r'<!-- '+re.escape(marker)+r' START -->.*?<!-- '+re.escape(marker)+r' END -->\n?',re.S)
        if pattern.search(latest):
            latest = pattern.sub(wrapped+'\n',latest,count=1)
        else:
            first = latest.index('<!--',latest.index('<main class="site-shell-main">'))
            latest = latest[:first]+wrapped+'\n'+latest[first:]
        latest_path.write_text(latest)
        (ROOT/'index.html').write_text(render_home())
    finally:
        conv.close()
    print(f'Connected {s["slug"]}: six shelves preserved; bounded home updates')


if __name__ == '__main__':
    main()
