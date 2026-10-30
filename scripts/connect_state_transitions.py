#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Keep the historical shelf discoverable without renumbering existing collections."""
import argparse
import json
import re

from build_state_transitions import ROOT, TITLE, DATE, HistoryTraditionalConverter, loc


def block(source, name, body, anchor):
    start, end = f'<!-- {name} START -->', f'<!-- {name} END -->'
    replacement = start + body + end
    if start in source:
        assert source.count(start) == source.count(end) == 1
        return re.sub(re.escape(start) + '.*?' + re.escape(end), lambda _: replacement, source, flags=re.S)
    assert source.count(anchor) == 1, (name, anchor)
    return source.replace(anchor, replacement + '\n' + anchor, 1)


def render():
    conv = HistoryTraditionalConverter()
    try:
        def library_loc(en, zh, tag='span', css=''):
            return loc(en, zh, conv, tag, css).replace('lang-zh', 'lang-zh cl-zh').replace('lang-hant', 'lang-zh cl-hant')

        lib_card = '<a href="essays/state-transitions/index.html" class="series-card"><span class="series-card-count">' + library_loc('Ongoing series · Four essays · EN / 简 / 繁', '持续专题 · 四篇 · 英简繁') + '</span><div class="series-card-title-zh cl-zh">国家的进退：权力、追问与人的位置</div><div class="series-card-title-zh cl-hant">國家的進退：權力、追問與人的位置</div><div class="series-card-title-en">States in Motion: Power, Questioning, and the Place of Persons</div>' + library_loc('India, South Africa, Germany and South Korea: detention, voting, rule-making and the conditions for organized disagreement. Linked records, not a ranking of countries.', '从印度、南非、德国与韩国读拘留、选票、规则制定，以及让反对仍有作用的条件。附可回查史料，不为国家排名，也不把人的处境平均成一个分数。', 'p', 'series-card-desc') + library_loc('Read the histories →', '进入历史专题 →', 'span', 'series-card-arrow') + '</a>'
        library = block((ROOT/'library.html').read_text(), 'STATE HISTORIES LIBRARY', lib_card, '    <a href="essays/mingren/index.html" class="series-card series-card-flagship">')

        explore_card = '<a class="shelf-link" href="essays/state-transitions/index.html">' + loc('Historical readings · Ongoing', '历史细读 · 持续展开', conv, 'span', 'shelf-label') + loc(*TITLE, conv, 'h3') + loc('Who can question power, and what can a question change?', '谁能追问权力，追问以后又能改变什么？', conv, 'p') + '<span class="shelf-arrow">→</span></a>'
        explore = block((ROOT/'explore.html').read_text(), 'STATE HISTORIES EXPLORE', explore_card, '        <a class="shelf-link" href="essays/mingren/index.html">')

        updates = {u['id']:u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates']}
        latest = (ROOT/'latest.html').read_text()
        for update_id, marker, date_id, en, zh, anchor in (
            ('2026-10-29-state-histories', 'STATE HISTORIES LATEST', 'date-state-histories', 'Historical series · First two essays', '历史专题 · 首发两篇', '    <!-- STATE REVERSAL START -->'),
            ('2026-10-29-state-histories-batch02', 'STATE HISTORIES BATCH02 LATEST', 'date-state-histories-batch02', 'Historical series · Two more essays', '历史专题 · 再添两篇', '<!-- STATE HISTORIES LATEST START -->'),
        ):
            update = updates[update_id]
            deck = loc(update['summary']['en'], update['summary']['zh'], conv, 'p')
            latest_card = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="' + date_id + '"><header class="updates-date"><h2 id="' + date_id + '"><time datetime="' + update['date'] + '">' + update['date'] + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + update['id'] + '"><div class="update-meta"><span class="update-kind">' + loc(en, zh, conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(update['title']['en'], update['title']['zh'], conv, 'h3') + deck + '<a href="essays/state-transitions/index.html">' + loc('Read the histories →', '进入历史专题 →', conv) + '</a></article></div></section></div></section>'
            latest = block(latest, marker, latest_card, anchor)

        home_row = '<a class="home-update-row" href="essays/state-transitions/index.html"><time datetime="' + DATE + '">Oct 29</time><div>' + loc('Historical series · Four essays · EN / 简 / 繁', '历史专题 · 四篇 · 英简繁', conv, 'span', 'home-update-kind') + loc(*TITLE, conv, 'h3') + '</div></a>'
        home = block((ROOT/'index.html').read_text(), 'STATE HISTORIES HOME', home_row, '          <a class="home-update-row" href="essays/state-reversal/index.html">')
        return {ROOT/'library.html': library, ROOT/'explore.html': explore, ROOT/'latest.html': latest, ROOT/'index.html': home}
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
    print(('Checked' if args.check else 'Connected') + ' history shelf · Library / Explore / Latest / Home')


if __name__ == '__main__':
    main()
