#!/usr/bin/env python3
"""Render a bounded, static homepage digest from the full publication ledger."""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- HOME UPDATES START -->'
END = '<!-- HOME UPDATES END -->'
RECENT_LIMIT = 4
LANGS = {'en': 'en', 'zh': 'zh', 'zh-hant': 'hant'}
KINDS = {
    'new': {'en': 'New', 'zh': '新作', 'zh-hant': '新作'},
    'expanded': {'en': 'Expanded', 'zh': '拓展', 'zh-hant': '拓展'},
    'revised': {'en': 'Revised', 'zh': '修订', 'zh-hant': '修訂'},
}


def series_key(item: dict) -> str:
    """Group chapters, translations and nested companions, not unrelated works.

    A ledger item may set series_key explicitly for a nonstandard URL layout.
    Otherwise the normal essays/<series>/ root is the grouping boundary.
    """
    if item.get('series_key'):
        return item['series_key']
    path = unquote(urlsplit(item['url']).path).strip('/')
    parts = path.split('/')
    # Work-based collections have one extra directory level.
    collections = {'literature', 'science-fiction', 'anime', 'tv', 'games', 'wuxia', 'everyday', 'art'}
    depth = 3 if len(parts) > 3 and parts[0] == 'essays' and parts[1] in collections else 2
    return '/'.join(parts[:depth])


def select_updates(updates: list[dict], config: dict) -> tuple[dict, list[dict]]:
    if len({u['id'] for u in updates}) != len(updates):
        raise ValueError('Duplicate update IDs')
    # Stable date ordering keeps editorial order for updates on the same day.
    ordered = sorted(updates, key=lambda u: date.fromisoformat(u['date']), reverse=True)
    feature = next((u for u in ordered if u['id'] == config['feature_id']), None)
    if feature is None:
        raise ValueError('Editorial feature_id is not in the publication ledger')
    seen = {series_key(feature)}
    recent = []
    for item in ordered:
        key = series_key(item)
        if key not in seen:
            seen.add(key)
            recent.append(item)
            if len(recent) == RECENT_LIMIT:
                break
    return feature, recent


def localized(values: dict, tag: str = 'span', css: str = '') -> str:
    return ''.join(f'<{tag} class="lang-{suffix}{" " + css if css else ""}">{escape(values[lang])}</{tag}>'
                   for lang, suffix in LANGS.items())


def render_section(updates: list[dict], config: dict) -> str:
    feature, recent = select_updates(updates, config)
    if len(recent) != RECENT_LIMIT:
        raise ValueError('Homepage requires four distinct recent series')
    title = localized({'en': 'New & reconsidered', 'zh': '最近值得一读', 'zh-hant': '最近值得一讀'}, 'h2')
    intro = localized({'en': 'One reading to linger with, plus a few recent arrivals. The full update history is one click away.', 'zh': '一篇值得慢读的推荐，几条最近的更新。想接着逛，完整记录就在下一页。', 'zh-hant': '一篇值得慢讀的推薦，幾條最近的更新。想接著逛，完整記錄就在下一頁。'}, 'p')
    pick = localized({'en': 'Editor’s pick', 'zh': '本期推荐', 'zh-hant': '本期推薦'}, css='home-update-kind')
    cta = localized({'en': 'Read the series →', 'zh': '进入系列 →', 'zh-hant': '進入系列 →'})
    more = localized({'en': 'All updates →', 'zh': '查看全部更新 →', 'zh-hant': '查看全部更新 →'})
    rows = []
    for item in recent:
        # Titles, dates and destinations come from the ledger, not duplicate copy.
        rows.append(f'          <a class="home-update-row" data-update-id="{escape(item["id"], quote=True)}" href="{escape(item["url"], quote=True)}"><time datetime="{item["date"]}">{item["date"][5:].replace("-", ".")}</time><div>{localized(KINDS[item["kind"]], css="home-update-kind")}{localized(item["title"], "h3")}</div></a>')
    return '\n'.join([
        START,
        '    <section class="home-section alt" id="home-latest"><div class="home-inner">',
        f'      <div class="home-section-heading"><div><p class="home-section-kicker">Latest</p>{title}</div>{intro}</div>',
        '      <div class="home-updates">',
        f'        <article class="home-update-feature" data-update-id="{escape(feature["id"], quote=True)}"><div class="home-update-meta">{pick}<time datetime="{feature["date"]}">{feature["date"]}</time></div>{localized(feature["title"], "h3")}{localized(config["feature_deck"], "p")}<a href="{escape(feature["url"], quote=True)}">{cta}</a></article>',
        '        <div class="home-update-list">',
        *rows,
        '        </div>',
        '      </div>',
        f'      <div class="home-section-more"><a href="latest.html">{more}</a></div>',
        '    </div></section>',
        END,
    ])


def replace_section(source: str, section: str) -> str:
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError('Expected exactly one HOME UPDATES marker pair')
    return re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: section, source, flags=re.S)


def render_home(source: str | None = None) -> str:
    updates = json.loads((ROOT/'data/site-updates.json').read_text())['updates']
    config = json.loads((ROOT/'data/home-updates.json').read_text())
    return replace_section(source if source is not None else (ROOT/'index.html').read_text(), render_section(updates, config))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    page = ROOT/'index.html'
    source = page.read_text()
    rendered = render_home(source)
    if args.check:
        if source != rendered or source.count('class="home-update-row"') != RECENT_LIMIT or source.count('class="home-update-feature"') != 1:
            print('ERROR: homepage digest is stale or exceeds its cap; run scripts/build_home_updates.py')
            return 1
    else:
        page.write_text(rendered)
    print('OK: homepage has one editorial pick and four distinct recent series')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
