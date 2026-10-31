#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Connect the marriage release without replacing previous update records."""
import argparse
import json

from build_marriage_series import ROOT, DATE, TITLE, MarriageTraditionalConverter, loc
from connect_state_transitions import block


def render():
    conv = MarriageTraditionalConverter()
    try:
        update = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id']=='2026-10-30-marriage-series')
        latest_card = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-marriage-series"><header class="updates-date"><h2 id="date-marriage-series"><time datetime="'+DATE+'">'+DATE+'</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="'+update['id']+'"><div class="update-meta"><span class="update-kind">'+loc('New series · Eight essays','新系列 · 八篇',conv)+'</span><span>EN / 简 / 繁</span></div>'+loc(update['title']['en'],update['title']['zh'],conv,'h3')+loc(update['summary']['en'],update['summary']['zh'],conv,'p')+'<a href="essays/marriage/index.html">'+loc('Read the series →','进入系列 →',conv)+'</a></article></div></section></div></section>'
        latest = block((ROOT/'latest.html').read_text(),'MARRIAGE SERIES LATEST',latest_card,'<!-- COOPERATION HISTORIES BATCH03 LATEST START -->')
        home_card = '<a class="home-update-row" href="essays/marriage/index.html"><time datetime="'+DATE+'">Oct 30</time><div>'+loc('New series · Eight essays · EN / 简 / 繁','新系列 · 八篇 · 英简繁',conv,'span','home-update-kind')+loc('Marriage: '+TITLE[0],'婚姻论：'+TITLE[1],conv,'h3')+'</div></a>'
        home = block((ROOT/'index.html').read_text(),'MARRIAGE SERIES HOME',home_card,'<!-- COOPERATION HISTORIES HOME START -->')
        return {ROOT/'latest.html':latest,ROOT/'index.html':home}
    finally:
        conv.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    for path,text in render().items():
        if args.check:
            assert path.read_text()==text,f'Stale marriage entrance: {path}'
        else:
            path.write_text(text)
    print(('Checked' if args.check else 'Connected')+' marriage · Latest / Home')


if __name__=='__main__':
    main()
