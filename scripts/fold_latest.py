#!/usr/bin/env python3
"""Fold older Latest entries into collapsed month groups.

latest.html keeps every update card: data/site-updates.json is checked against
it card by card, several tests look up their own card, and some build scripts
write into it. Only the most recent days stay expanded; older update sections
are wrapped, in their existing order, in <details class="updates-month"> groups,
one per month. The script is rerunnable: existing folds are removed and rebuilt
from the given date, so new entries can keep being added at the top as before.

    python3 scripts/fold_latest.py             # keep the last 14 days expanded
    python3 scripts/fold_latest.py --days 21 --today 2026-10-22
    python3 scripts/fold_latest.py --check     # fail if latest.html is not folded
"""
from __future__ import annotations

import argparse
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "latest.html"
FOLDS_START = "<!-- LATEST FOLDS START -->"
FOLDS_END = "<!-- LATEST FOLDS END -->"
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
HEADING = (
    '<section class="updates-earlier"><div class="latest-inner">'
    '<h2 class="lang-en">Earlier updates</h2><h2 class="lang-zh">更早的更新</h2><h2 class="lang-hant">更早的更新</h2>'
    '<p class="lang-en">Grouped by month. Open a month to see what was published, revised or translated.</p>'
    '<p class="lang-zh">按月收起。展开一个月份，可以看到那个月的发布、修订与语言拓展。</p>'
    '<p class="lang-hant">按月收起。展開一個月份，可以看到那個月的發佈、修訂與語言拓展。</p>'
    '</div></section>'
)


def unfold(text: str) -> str:
    if FOLDS_START not in text:
        return text
    text = re.sub(r'<!-- FOLD \d{4}-\d{2} START -->\s*<details class="updates-month"[^>]*>\s*<summary.*?</summary>\s*',
                  '', text, flags=re.S)
    text = re.sub(r'\s*</details>\s*<!-- FOLD \d{4}-\d{2} END -->', '', text)
    text = re.sub(re.escape(FOLDS_START) + r'\s*<section class="updates-earlier">.*?</section>\s*', '', text, flags=re.S)
    return text.replace(FOLDS_END, '')


def split_feed(feed: str) -> list[dict]:
    """Top-level nodes of the feed: update sections with the marker comments around them."""
    nodes, pos = [], 0
    while True:
        while pos < len(feed) and feed[pos].isspace():
            pos += 1
        if pos >= len(feed):
            break
        if feed.startswith('<!--', pos):
            end = feed.index('-->', pos) + 3
            nodes.append(('comment', feed[pos:end]))
        elif feed.startswith('<section', pos):
            depth, cursor = 0, pos
            for match in re.finditer(r'<section\b|</section>', feed[pos:]):
                depth += 1 if match.group(0) != '</section>' else -1
                if depth == 0:
                    cursor = pos + match.end()
                    break
            else:
                raise ValueError('Unbalanced <section> in the update feed')
            nodes.append(('section', feed[pos:cursor]))
            end = cursor
        else:
            raise ValueError('Unexpected content in the update feed: ' + feed[pos:pos + 80])
        pos = end
    blocks, pending = [], []
    for kind, value in nodes:
        if kind == 'comment':
            if 'END' in value and blocks and not pending:
                blocks[-1]['post'].append(value)
            else:
                pending.append(value)
            continue
        found = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})"', value)
        if not found:
            raise ValueError('Update section without a date: ' + value[:120])
        blocks.append({'pre': pending, 'html': value, 'post': [], 'date': date.fromisoformat(found.group(1)),
                       'cards': value.count('data-update-id="')})
        pending = []
    if pending:
        raise ValueError('Marker comments without an update section: ' + ' '.join(pending))
    return blocks


def summary(year: int, month: int, days: list[int], partial: bool, cards: int) -> str:
    if partial:
        lo, hi = min(days), max(days)
        span = str(lo) if lo == hi else f'{lo}–{hi}'
        en = f'{span} {MONTHS[month - 1]} {year}'
        zh = f'{year} 年 {month} 月 {lo} 日' if lo == hi else f'{year} 年 {month} 月 {lo}—{hi} 日'
    else:
        en, zh = f'{MONTHS[month - 1]} {year}', f'{year} 年 {month} 月'
    count_en = f'{cards} update' + ('' if cards == 1 else 's')
    return (f'<summary class="updates-month-summary"><span class="latest-inner updates-month-row">'
            f'<span class="updates-month-title"><span class="lang-en">{en}</span><span class="lang-zh">{zh}</span><span class="lang-hant">{zh}</span></span>'
            f'<span class="updates-month-count"><span class="lang-en">{count_en}</span><span class="lang-zh">{cards} 条更新</span><span class="lang-hant">{cards} 條更新</span></span>'
            f'</span></summary>')


def fold(text: str, today: date, days: int) -> str:
    text = unfold(text)
    hero_start = text.index('<section class="latest-hero"')
    feed_start = text.index('</section>', hero_start) + len('</section>')
    feed_end = text.index('<section class="latest-archive"')
    blocks = split_feed(text[feed_start:feed_end])
    cutoff = today - timedelta(days=days)
    render = lambda b: '\n    '.join(b['pre'] + [b['html']] + b['post'])
    recent = [b for b in blocks if b['date'] >= cutoff]
    older = [b for b in blocks if b['date'] < cutoff]
    parts = [render(b) for b in recent]
    if older:
        groups: list[list[dict]] = []
        for block in older:
            key = (block['date'].year, block['date'].month)
            if groups and (groups[-1][0]['date'].year, groups[-1][0]['date'].month) == key:
                groups[-1].append(block)
            else:
                groups.append([block])
        folded = [FOLDS_START, HEADING]
        for group in groups:
            year, month = group[0]['date'].year, group[0]['date'].month
            label = f'{year}-{month:02d}'
            partial = (year, month) == (cutoff.year, cutoff.month)
            day_list = [b['date'].day for b in group]
            folded.append(f'<!-- FOLD {label} START --><details class="updates-month" id="updates-{label}">'
                          + summary(year, month, day_list, partial, sum(b['cards'] for b in group)))
            folded.extend(render(b) for b in group)
            folded.append(f'</details><!-- FOLD {label} END -->')
        folded.append(FOLDS_END)
        parts.append('\n    '.join(folded))
    return text[:feed_start] + '\n    ' + '\n    '.join(parts) + '\n    ' + text[feed_end:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=14, help='days kept expanded (default 14)')
    parser.add_argument('--today', type=date.fromisoformat, default=date.today())
    parser.add_argument('--check', action='store_true', help='fail if latest.html would change')
    args = parser.parse_args()
    current = PAGE.read_text(encoding='utf-8')
    result = fold(current, args.today, args.days)
    before = re.findall(r'data-update-id="([^"]+)"', current)
    after = re.findall(r'data-update-id="([^"]+)"', result)
    if before != after:
        raise SystemExit('ERROR: folding changed the update cards or their order')
    if args.check:
        if result != current:
            print('ERROR: latest.html is not folded for this date; run scripts/fold_latest.py')
            return 1
        print('OK: latest.html folds are current')
        return 0
    PAGE.write_text(result, encoding='utf-8')
    groups = re.findall(r'<details class="updates-month" id="updates-([0-9-]+)">', result)
    print(f'OK: {len(after)} cards; expanded since {args.today - timedelta(days=args.days)}; folded months: {", ".join(groups) or "none"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
