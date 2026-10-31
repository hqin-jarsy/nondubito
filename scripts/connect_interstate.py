#!/usr/bin/env python3
"""Connect the completed Interstate series while preserving its first announcement."""
import argparse
import json
import re

from build_interstate import ROOT, TITLE, DATE, COMPLETE_DATE, loc, InterstateTraditionalConverter
from connect_state_transitions import block


def render():
    conv = InterstateTraditionalConverter()
    try:
        update = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-10-30-interstate-batch01')
        latest_card = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-interstate-batch01"><header class="updates-date"><h2 id="date-interstate-batch01"><time datetime="' + DATE + '">' + DATE + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + update['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('New series · First three essays', '新系列 · 首发三篇', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(*TITLE, conv, 'h3') + loc(update['summary']['en'], update['summary']['zh'], conv, 'p') + '<a href="essays/interstate/index.html">' + loc('Read the first three →', '先读三篇 →', conv) + '</a></article></div></section></div></section>'
        latest = block((ROOT/'latest.html').read_text(), 'INTERSTATE BATCH01 LATEST', latest_card, '<!-- STATE HISTORIES BATCH03 LATEST START -->')
        complete = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-10-31-interstate-complete')
        complete_card = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-interstate-complete"><header class="updates-date"><h2 id="date-interstate-complete"><time datetime="' + COMPLETE_DATE + '">' + COMPLETE_DATE + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + complete['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('Series completed · Six new essays', '系列补齐 · 新增六篇', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(*TITLE, conv, 'h3') + loc(complete['summary']['en'], complete['summary']['zh'], conv, 'p') + '<a href="essays/interstate/index.html">' + loc('Read all nine →', '阅读全部九篇 →', conv) + '</a></article></div></section></div></section>'
        latest = block(latest, 'INTERSTATE COMPLETE LATEST', complete_card, '<!-- MARRIAGE SERIES LATEST START -->')
        home_row = '<a class="home-update-row" href="essays/interstate/index.html"><time datetime="' + COMPLETE_DATE + '">Oct 31</time><div>' + loc('Six new essays · All nine available · EN / 简 / 繁', '新增六篇 · 九篇补齐 · 英简繁', conv, 'span', 'home-update-kind') + loc(*TITLE, conv, 'h3') + '</div></a>'
        # Keep a single current home row, moving it above the older releases.
        home_source = (ROOT/'index.html').read_text()
        assert home_source.count('<!-- INTERSTATE HOME START -->') == 1
        home_source = re.sub(r'<!-- INTERSTATE HOME START -->.*?<!-- INTERSTATE HOME END -->\n?', '', home_source, flags=re.S)
        home = block(home_source, 'INTERSTATE HOME', home_row, '<!-- MARRIAGE SERIES HOME START -->')
        return {ROOT/'latest.html': latest, ROOT/'index.html': home}
    finally:
        conv.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, text in render().items():
        if args.check:
            assert path.read_text() == text, f'Stale entrance: {path}'
        else:
            path.write_text(text)
    print(('Checked' if args.check else 'Connected') + ' Interstate Cooperation · Latest / Home')


if __name__ == '__main__':
    main()
