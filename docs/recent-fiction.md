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
- For translated novels, `book` and `book_date` describe the original edition,
  and `book_language` records its language (`en` is the legacy default).
  Optional `book_en` / `book_zh` supply reader-facing names; use verified edition
  titles where available and identify any working title in the reading notice.
  Do not present an explanatory English title as a published translation.
- `search_aliases` holds additional original titles, translated titles, and author
  names for search. Only localized book names become Book `alternateName` values;
  author-name search aliases must not be presented as alternate book titles.
  A translated edition's year must never replace the original publication year.
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

The shelf topics and reading recommendations are explicit in
`build_recent_fiction.py`. The shelf groups books by year, newest publication
first. Each JSON has a `guide_date` independent of `book_date`; optional
`updated_date` records a substantive editorial revision. Do not redate older
guides when adding a batch. The collection preserves its initial publication
date and takes its modification date from its guides.

The builder also updates only the marked Recent Fiction section of
`library.html`, so book titles, descriptions and links stay consistent. Do not
edit those generated cards separately. The Library's overall statistics and the
other curated site entrances remain manual.

Search snippets for this shelf come from each language's visible hero deck,
so Simplified and Traditional Chinese results do not inherit the English meta
description. Other shelves keep their existing search-description behavior.
Search result links for this shared-URL shelf carry `?lang=en`, `?lang=zh`, or
`?lang=zh-hant` so the selected result language also opens in the article.

New guides also need curated entries in Library, Explore, Latest, the update
ledger, and any relevant homepage or language-channel links. Keep the literary
shelf's Traditional Chinese text map in sync if its callout changes.

All five build scripts accept `--check`. Also run
`scripts/check_site_updates.py`, `scripts/normalize_canonicals.py --check`, and
`git diff --check`. Verify English, Simplified and Traditional Chinese modes,
mobile widths, the source-section anchor, and searches by both book and author.
Run `python3 scripts/test_recent_fiction.py` for focused checks of dates,
source links, the three editions, generated Library cards and HTML structure.
