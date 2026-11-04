# Homepage updates

The homepage is a reading entrance, not a second archive: **one editorial pick
and four recent updates from distinct series**. `latest.html` retains every
entry in `data/site-updates.json`; rotating a homepage link never removes an
article or an archive record.

## Publishing

1. Add the dated update to `data/site-updates.json` and to `latest.html` as usual.
   Use genuine editorial publication/revision dates, not file modification dates.
2. Run `python3 -B scripts/build_home_updates.py`.
3. Run `python3 -B scripts/check_site_updates.py`,
   `python3 -B scripts/build_home_updates.py --check` and
   `python3 -B -m unittest discover -s scripts -p test_home_updates.py`.

Do not append homepage cards by hand or reuse historical one-off patches with
old `… HOME START` markers. Repeatable connectors for political economy,
cooperation histories, interstate cooperation, marriage and state histories now
use the shared homepage renderer. CI rejects an outdated or over-cap digest.

## Editorial pick and grouping

`data/home-updates.json` chooses an existing ledger `feature_id` and provides a
short English / simplified Chinese / traditional Chinese introduction. Its
title, destination and date still come from the ledger. A pick need not be new:
the label is explicitly “Editor’s pick,” with the original update date.

The four recent entries are the newest distinct series, excluding the featured
series. Same-day ties retain ledger order. Chapters, translations and nested
companions such as political-economy theory/cases are grouped together; work-based
collections retain separate works. For unusual URL layouts, set an optional
`series_key` on each relevant ledger entry. The renderer changes no ledger data.

All five entries are static HTML in all three homepage reading languages. No
JavaScript, hidden overflow or “load more” interaction is needed to read them.
