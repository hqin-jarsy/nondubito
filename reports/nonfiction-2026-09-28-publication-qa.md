# Nonfiction publication QA — 2026-09-28

## Scope

- Replace the existing Small Is Beautiful introduction with the approved rewrite, retaining its URL and 2026-09-13 publication date; record the revision as 2026-09-28.
- Add How to Do Nothing, Seeing Like a State, and Being Mortal, each dated 2026-09-28.
- Preserve Raising Hare's source JSON, three article bodies, notices and publication date. Its related-reading navigation now includes the new articles.
- Preserve all source manuscripts in `/Users/hanqin/Documents/SAE介绍`.
- Publish complete English, Simplified Chinese and Traditional Chinese reading modes. Keep research links in the separate source section, outside the four approved article bodies.

The shelf now contains five nonfiction guides; the parent entrance contains 48 books, including the existing 43 recent novels. Homepage, Explore, Library, Latest, the editorial update ledger, search and sitemap are integrated. The old generated category numbers were brought into line with the existing 17-category Library (Recent Fiction 08; Nonfiction 09), without changing novel content.

## Editorial checks

The four Chinese bodies were compared exactly with the approved manuscripts after removing only the title and bibliographic paragraph. Fixed SHA256 expectations are recorded in `scripts/test_book_introductions.py`, so tests do not depend on access to the external manuscript folder.

English prose was independently reviewed against the Chinese for omissions, changed facts and lost qualifications. Three small wording corrections were made to the Small Is Beautiful translation before the final build. Reading notices distinguish publicly available passages and research from a complete reading. Being Mortal preserves the distinctions between palliative care, hospice and euthanasia; no treatment decision is prescribed to readers.

## Automated checks

Passed:

- `python3 scripts/test_book_introductions.py` — 15 tests.
- `python3 scripts/test_recent_fiction.py` — 13 tests.
- `node scripts/test_recent_fiction_language.cjs`.
- `python3 scripts/build_recent_fiction.py --check`.
- `python3 scripts/build_book_introductions.py --check`.
- `python3 scripts/build_content_registry.py --check`.
- `python3 scripts/build_search_index.py --check`.
- `python3 scripts/build_sitemap.py --check`.
- `python3 scripts/audit_reader_context.py --check`.
- `python3 scripts/check_site_updates.py`.
- `python3 scripts/normalize_canonicals.py --check`.
- `git diff --check`.

The generated registry and audit reports also catch up with already-committed changes elsewhere in the library. No unrelated article source files were edited.

## Browser checks

`scripts/test_book_introductions_browser.cjs` passed 93 checks in isolated headless Chrome against the local build:

- 63 combinations: two entrances and five articles, three reading modes, widths 1440 / 390 / 320.
- Complete visible bodies, four sections in each new/revised article, one visible page title, no horizontal overflow.
- Visible Small Is Beautiful revision date, source anchors, mobile menus, language switching and reloads preserving the selected language and fragment.
- Hub → shelf → article → related article navigation.
- 18 searches: each new book's title and author in each reading language; results open the matching language.
- No page JavaScript errors or failed local resources.

Desktop Simplified Chinese and mobile Traditional Chinese screenshots were visually inspected. Screenshots remain in the writing workspace's `work` directory, outside this repository.

These are local pre-publication checks. Remote deployment and live-page verification are separate from this report.
