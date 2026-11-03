#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add current discovery entries without rewriting old update blocks."""
import argparse
import json

from build_political_economy import ROOT, DATE, TITLE, loc, PoliticalTraditionalConverter
from connect_state_transitions import block


def dated_card(text, date):
    """Earlier update cards keep their publication dates as the shelf grows."""
    current = '<time datetime="' + DATE + '">' + DATE + '</time>'
    assert text.count(current) == 1
    return text.replace(current, '<time datetime="' + date + '">' + date + '</time>')


def render():
    conv = PoliticalTraditionalConverter()
    try:
        update = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-11-01-political-economy-batch01')
        latest_card = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-political-economy"><header class="updates-date"><h2 id="date-political-economy"><time datetime="' + DATE + '">' + DATE + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + update['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('New series · Political economy · Real cases', '新专题 · 政治经济学真实案例', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(*TITLE, conv, 'h3') + loc(update['summary']['en'], update['summary']['zh'], conv, 'p') + '<a href="essays/political-economy/index.html">' + loc('Read the introduction and cases →', '读导读与真实案例 →', conv) + '</a></article></div></section></div></section>'
        latest = block((ROOT/'latest.html').read_text(), 'POLITICAL ECONOMY BATCH01 LATEST', dated_card(latest_card, update['date']), '<!-- COOPERATION HISTORIES BATCH07 LATEST START -->')
        expansion = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-11-01-political-economy-batch02')
        expansion_card = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-political-economy-batch02"><header class="updates-date"><h2 id="date-political-economy-batch02"><time datetime="' + DATE + '">' + DATE + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + expansion['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('Expanded · Political economy · Real cases', '专题扩展 · 政治经济学真实案例', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(expansion['title']['en'], expansion['title']['zh'], conv, 'h3') + loc(expansion['summary']['en'], expansion['summary']['zh'], conv, 'p') + '<a href="essays/political-economy/steward-hospitals.html">' + loc('Read the hospital essay →', '从医院篇读起 →', conv) + '</a></article></div></section></div></section>'
        latest = block(latest, 'POLITICAL ECONOMY BATCH02 LATEST', dated_card(expansion_card, expansion['date']), '<!-- POLITICAL ECONOMY BATCH01 LATEST START -->')
        batch03 = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-11-02-political-economy-batch03')
        batch03_card = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-political-economy-batch03"><header class="updates-date"><h2 id="date-political-economy-batch03"><time datetime="' + DATE + '">' + DATE + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + batch03['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('Expanded · Political economy · Real cases', '专题扩展 · 政治经济学真实案例', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(batch03['title']['en'], batch03['title']['zh'], conv, 'h3') + loc(batch03['summary']['en'], batch03['summary']['zh'], conv, 'p') + '<a href="essays/political-economy/google-adtech.html">' + loc('Read the ad auction essay →', '从广告竞价篇读起 →', conv) + '</a></article></div></section></div></section>'
        latest = block(latest, 'POLITICAL ECONOMY BATCH03 LATEST', dated_card(batch03_card, batch03['date']), '<!-- POLITICAL ECONOMY BATCH02 LATEST START -->')
        batch04 = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-11-03-political-economy-batch04')
        batch04_card = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-political-economy-batch04"><header class="updates-date"><h2 id="date-political-economy-batch04"><time datetime="' + DATE + '">' + DATE + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + batch04['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('Expanded · Political economy · Real cases', '专题扩展 · 政治经济学真实案例', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(batch04['title']['en'], batch04['title']['zh'], conv, 'h3') + loc(batch04['summary']['en'], batch04['summary']['zh'], conv, 'p') + '<a href="essays/political-economy/foxconn-wisconsin.html">' + loc('Read the promised-jobs essay →', '从招商承诺篇读起 →', conv) + '</a></article></div></section></div></section>'
        latest = block(latest, 'POLITICAL ECONOMY BATCH04 LATEST', dated_card(batch04_card, batch04['date']), '<!-- POLITICAL ECONOMY BATCH03 LATEST START -->')
        batch05 = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-11-03-political-economy-batch05')
        batch05_card = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-political-economy-batch05"><header class="updates-date"><h2 id="date-political-economy-batch05"><time datetime="' + DATE + '">' + DATE + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + batch05['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('Political economy · Group one closing interlude', '政治经济学 · 第一组收尾间奏', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(batch05['title']['en'], batch05['title']['zh'], conv, 'h3') + loc(batch05['summary']['en'], batch05['summary']['zh'], conv, 'p') + '<a href="essays/political-economy/jimmy-johns.html">' + loc('Read the closing interlude →', '读收尾间奏 →', conv) + '</a></article></div></section></div></section>'
        latest = block(latest, 'POLITICAL ECONOMY BATCH05 LATEST', dated_card(batch05_card, batch05['date']), '<!-- POLITICAL ECONOMY BATCH04 LATEST START -->')
        theory = next(u for u in json.loads((ROOT/'data/site-updates.json').read_text())['updates'] if u['id'] == '2026-11-03-political-economy-theory')
        theory_card = '<section class="updates-section"><div class="latest-inner"><section class="updates-day" aria-labelledby="date-political-economy-theory"><header class="updates-date"><h2 id="date-political-economy-theory"><time datetime="' + DATE + '">' + DATE + '</time></h2></header><div class="updates-grid"><article class="update-card" data-update-id="' + theory['id'] + '"><div class="update-meta"><span class="update-kind">' + loc('Political economy · Eight theoretical readings', '政治经济学 · 八篇理论导读', conv) + '</span><span>EN / 简 / 繁</span></div>' + loc(theory['title']['en'], theory['title']['zh'], conv, 'h3') + loc(theory['summary']['en'], theory['summary']['zh'], conv, 'p') + '<a href="essays/political-economy/theory/index.html">' + loc('Understand the argument →', '进入理论导读 →', conv) + '</a></article></div></section></div></section>'
        latest = block(latest, 'POLITICAL ECONOMY THEORY LATEST', theory_card, '<!-- POLITICAL ECONOMY BATCH05 LATEST START -->')
        home_row = '<a class="home-update-row" href="essays/political-economy/theory/index.html"><time datetime="' + DATE + '">Nov 3</time><div>' + loc('SAE political economy · Eight readings · EN / 简 / 繁', 'SAE 政治经济学 · 八篇导读 · 英简繁', conv, 'span', 'home-update-kind') + loc(theory['title']['en'], theory['title']['zh'], conv, 'h3') + '</div></a>'
        home = block((ROOT/'index.html').read_text(), 'POLITICAL ECONOMY HOME', home_row, '<!-- COOPERATION HISTORIES HOME START -->')
        explore_source = (ROOT/'explore.html').read_text()
        start = explore_source.index('<section class="domain-section" id="sae">')
        end = explore_source.index('</section>', start) + len('</section>')
        section = explore_source[start:end]
        direct = '<p class="sae-map-link"><a href="essays/political-economy/index.html">' + loc('SAE political economy: theory & real cases →', 'SAE 政治经济学：理论导读与真实案例 →', conv) + '</a></p>'
        section = block(section, 'POLITICAL ECONOMY EXPLORE', direct, '<div class="shelf-grid">')
        explore = explore_source[:start] + section + explore_source[end:]
        return {ROOT/'index.html':home, ROOT/'latest.html':latest, ROOT/'explore.html':explore}
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
    print(('Checked' if args.check else 'Connected') + ' Political Economy · Home / Latest / Explore')


if __name__ == '__main__':
    main()
