#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Connect the real-history companion while preserving existing shelves and updates."""
import argparse
import json
import re

from build_cooperation_histories import ROOT, DATE, UPDATE_DATE, TITLE, DECK, loc, CooperationTraditionalConverter
from connect_state_transitions import block


def render():
    conv = CooperationTraditionalConverter()
    try:
        def ll(en, zh, tag='span', css=''):
            return loc(en, zh, conv, tag, css).replace('lang-zh', 'lang-zh cl-zh').replace('lang-hant', 'lang-zh cl-hant')

        card = '<a href="essays/cooperation-histories/index.html" class="series-card"><span class="series-card-count">' + ll('Ongoing historical series · Fourteen essays · EN / 简 / 繁', '持续历史专题 · 十四篇 · 英简繁') + '</span><div class="series-card-title-zh cl-zh">共同决定之后</div><div class="series-card-title-zh cl-hant">共同決定之後</div><div class="series-card-title-en">After the Shared Decision</div>' + ll(DECK[0], DECK[1], 'p', 'series-card-desc') + ll('Read the histories →', '进入真实案例专题 →', 'span', 'series-card-arrow') + '</a>'
        library = block((ROOT/'library.html').read_text(), 'COOPERATION HISTORIES LIBRARY', card, '<!-- STATE HISTORIES LIBRARY START -->')

        shelf = '<a class="shelf-link" href="essays/cooperation-histories/index.html">' + loc('Real histories · Cooperation', '真实历史 · 国家间协作', conv, 'span', 'shelf-label') + loc(*TITLE, conv, 'h3') + loc('Fourteen histories: water, sanctions, borders, production change, vaccination, financial assistance and inspection. What makes action possible, and who can ask for another look?', '十四段历史读水流、制裁、边界、生产转型、疫苗、金融援助与现场检查。行动靠什么成为可能，又由谁来要求再看一次？', conv, 'p') + '<span class="shelf-arrow">→</span></a>'
        explore = block((ROOT/'explore.html').read_text(), 'COOPERATION HISTORIES EXPLORE', shelf, '<!-- STATE HISTORIES EXPLORE START -->')

        update = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-10-30-cooperation-histories')
        latest_card = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-cooperation-histories"><header class="updates-date"><h2 id="date-cooperation-histories"><time datetime="' + DATE + '">' + DATE + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + update['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('New historical series · First two essays', '新历史专题 · 首发两篇', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(*TITLE, conv, 'h3') + loc(update['summary']['en'], update['summary']['zh'], conv, 'p') + '<a href="essays/cooperation-histories/index.html">' + loc('Read the histories →', '进入真实案例专题 →', conv) + '</a></article></div></section></div></section>'
        latest = block((ROOT/'latest.html').read_text(), 'COOPERATION HISTORIES LATEST', latest_card, '<!-- INTERSTATE BATCH01 LATEST START -->')

        update2 = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-10-30-cooperation-histories-batch02')
        latest_card2 = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-cooperation-histories-batch02"><header class="updates-date"><h2 id="date-cooperation-histories-batch02"><time datetime="' + DATE + '">' + DATE + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + update2['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('Historical series · Iraq & Kadi', '历史专题 · 伊拉克与卡迪', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(update2['title']['en'], update2['title']['zh'], conv, 'h3') + loc(update2['summary']['en'], update2['summary']['zh'], conv, 'p') + '<a href="essays/cooperation-histories/index.html">' + loc('Read the histories →', '进入真实案例专题 →', conv) + '</a></article></div></section></div></section>'
        latest = block(latest, 'COOPERATION HISTORIES BATCH02 LATEST', latest_card2, '<!-- COOPERATION HISTORIES LATEST START -->')

        update3 = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-10-30-cooperation-histories-batch03')
        latest_card3 = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-cooperation-histories-batch03"><header class="updates-date"><h2 id="date-cooperation-histories-batch03"><time datetime="' + DATE + '">' + DATE + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + update3['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('Historical series · Kunduz & Northern Ireland', '历史专题 · 昆都士与北爱', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(update3['title']['en'], update3['title']['zh'], conv, 'h3') + loc(update3['summary']['en'], update3['summary']['zh'], conv, 'p') + '<a href="essays/cooperation-histories/index.html">' + loc('Read the histories →', '进入真实案例专题 →', conv) + '</a></article></div></section></div></section>'
        latest = block(latest, 'COOPERATION HISTORIES BATCH03 LATEST', latest_card3, '<!-- COOPERATION HISTORIES BATCH02 LATEST START -->')

        update4 = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-10-31-cooperation-histories-batch04')
        latest_card4 = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-cooperation-histories-batch04"><header class="updates-date"><h2 id="date-cooperation-histories-batch04"><time datetime="' + update4['date'] + '">' + update4['date'] + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + update4['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('Historical series · Turtles & a river', '历史专题 · 海龟与一条河', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(update4['title']['en'], update4['title']['zh'], conv, 'h3') + loc(update4['summary']['en'], update4['summary']['zh'], conv, 'p') + '<a href="essays/cooperation-histories/index.html#conditions-and-limits">' + loc('Read the new pair →', '阅读新增两篇 →', conv) + '</a></article></div></section></div></section>'
        latest = block(latest, 'COOPERATION HISTORIES BATCH04 LATEST', latest_card4, '<!-- INTERSTATE COMPLETE LATEST START -->')

        update5 = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-10-31-cooperation-histories-batch05')
        latest_card5 = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-cooperation-histories-batch05"><header class="updates-date"><h2 id="date-cooperation-histories-batch05"><time datetime="' + update5['date'] + '">' + update5['date'] + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + update5['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('Historical series · Montreal & smallpox', '历史专题 · 蒙特利尔与天花', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(update5['title']['en'], update5['title']['zh'], conv, 'h3') + loc(update5['summary']['en'], update5['summary']['zh'], conv, 'p') + '<a href="essays/cooperation-histories/index.html#capacity-and-evidence">' + loc('Read the new pair →', '阅读新增两篇 →', conv) + '</a></article></div></section></div></section>'
        latest = block(latest, 'COOPERATION HISTORIES BATCH05 LATEST', latest_card5, '<!-- COOPERATION HISTORIES BATCH04 LATEST START -->')

        update6 = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-10-31-cooperation-histories-batch06')
        latest_card6 = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-cooperation-histories-batch06"><header class="updates-date"><h2 id="date-cooperation-histories-batch06"><time datetime="' + update6['date'] + '">' + update6['date'] + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + update6['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('Historical series · COVAX & Greece', '历史专题 · COVAX与希腊', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(update6['title']['en'], update6['title']['zh'], conv, 'h3') + loc(update6['summary']['en'], update6['summary']['zh'], conv, 'p') + '<a href="essays/cooperation-histories/index.html#allocation-and-choice">' + loc('Read the new pair →', '阅读新增两篇 →', conv) + '</a></article></div></section></div></section>'
        latest = block(latest, 'COOPERATION HISTORIES BATCH06 LATEST', latest_card6, '<!-- COOPERATION HISTORIES BATCH05 LATEST START -->')

        update7 = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-11-01-cooperation-histories-batch07')
        latest_card7 = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-cooperation-histories-batch07"><header class="updates-date"><h2 id="date-cooperation-histories-batch07"><time datetime="' + update7['date'] + '">' + update7['date'] + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + update7['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('Historical series · Antarctica & the Iran nuclear agreement', '历史专题 · 南极检查与伊核协议', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(update7['title']['en'], update7['title']['zh'], conv, 'h3') + loc(update7['summary']['en'], update7['summary']['zh'], conv, 'p') + '<a href="essays/cooperation-histories/index.html#inspection-and-judgment">' + loc('Read the new pair →', '阅读新增两篇 →', conv) + '</a></article></div></section></div></section>'
        latest = block(latest, 'COOPERATION HISTORIES BATCH07 LATEST', latest_card7, '<!-- COOPERATION HISTORIES BATCH06 LATEST START -->')

        home_card = '<a class="home-update-row" href="essays/cooperation-histories/index.html#inspection-and-judgment"><time datetime="' + UPDATE_DATE + '">Nov 1</time><div>' + loc('More histories · Inspection & judgment · EN / 简 / 繁', '历史专题更新 · 检查与判断 · 英简繁', conv, 'span', 'home-update-kind') + loc(*TITLE, conv, 'h3') + '</div></a>'
        home_source = (ROOT/'index.html').read_text()
        assert home_source.count('<!-- COOPERATION HISTORIES HOME START -->') == 1
        home_source = re.sub(r'<!-- COOPERATION HISTORIES HOME START -->.*?<!-- COOPERATION HISTORIES HOME END -->\n?', '', home_source, flags=re.S)
        home = block(home_source, 'COOPERATION HISTORIES HOME', home_card, '<!-- INTERSTATE HOME START -->')
        return {ROOT/'library.html':library, ROOT/'explore.html':explore, ROOT/'latest.html':latest, ROOT/'index.html':home}
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
    print(('Checked' if args.check else 'Connected') + ' cooperation histories · Library / Explore / Latest / Home')


if __name__ == '__main__':
    main()
