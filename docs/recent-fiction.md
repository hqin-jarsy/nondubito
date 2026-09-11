# Recent Fiction / 近年小说导读

The source manuscripts live in `/Users/hanqin/Documents/SAE介绍`.
This shelf is for introductions to recent novels, distinct from the longer
close-reading series in Literary Readings. Do not modify the source manuscripts
as part of a website build.

## Editorial source of truth

`data/recent-fiction/*.json` holds edited Chinese and independently written
English, plus source links and reading-scope notes. Traditional Chinese is
rendered using the existing converter from `build_ai_work_series.py` and checked
in the browser. Edit the JSON, not the generated HTML.

Keep these distinctions visible to readers:

- The book's original publication date is not the guide's publication date.
- Public excerpts support close discussion of those excerpts, not claims to
  have read or reviewed the full novel.
- Attribute authors' and reviewers' observations; distinguish them from the
  guide's own interpretations.
- Link directly to interviews, authorized excerpts, and relevant reviews.
- Preserve the book's major turns and ending. External links may reveal more.

## Build and integration

Run from the repository root on macOS:

```sh
python3 scripts/build_recent_fiction.py
python3 scripts/build_content_registry.py
python3 scripts/build_search_index.py
python3 scripts/build_sitemap.py
python3 scripts/audit_reader_context.py
```

The shelf order and topics are explicit in `build_recent_fiction.py`. The current
`DATE` is the publication date of the initial five guides; do not advance it to
date a later batch, since that would redate the existing guides. Add per-guide
publication dates when publishing a later batch.

New guides also need curated entries in Library, Explore, Latest, the update
ledger, and any relevant homepage or language-channel links. Keep the literary
shelf's Traditional Chinese text map in sync if its callout changes.

All five build scripts accept `--check`. Also run
`scripts/check_site_updates.py`, `scripts/normalize_canonicals.py --check`, and
`git diff --check`. Verify English, Simplified and Traditional Chinese modes,
mobile widths, the source-section anchor, and searches by both book and author.
