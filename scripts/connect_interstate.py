#!/usr/bin/env python3
"""Add the staged Interstate series to updates without replacing older announcements."""
import argparse
import json

from build_interstate import ROOT, TITLE, DATE, loc, InterstateTraditionalConverter
from connect_state_transitions import block


def render():
    conv = InterstateTraditionalConverter()
    try:
        update = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-10-30-interstate-batch01')
        latest_card = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-interstate-batch01"><header class="updates-date"><h2 id="date-interstate-batch01"><time datetime="' + DATE + '">' + DATE + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + update['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('New series · First three essays', '新系列 · 首发三篇', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(*TITLE, conv, 'h3') + loc(update['summary']['en'], update['summary']['zh'], conv, 'p') + '<a href="essays/interstate/index.html">' + loc('Read the first three →', '先读三篇 →', conv) + '</a></article></div></section></div></section>'
        latest = block((ROOT/'latest.html').read_text(), 'INTERSTATE BATCH01 LATEST', latest_card, '<!-- STATE HISTORIES BATCH03 LATEST START -->')
        home_row = '<a class="home-update-row" href="essays/interstate/index.html"><time datetime="' + DATE + '">Oct 30</time><div>' + loc('New series · First three essays · EN / 简 / 繁', '新系列 · 首发三篇 · 英简繁', conv, 'span', 'home-update-kind') + loc(*TITLE, conv, 'h3') + '</div></a>'
        home = block((ROOT/'index.html').read_text(), 'INTERSTATE HOME', home_row, '<!-- STATE HISTORIES HOME START -->')
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
