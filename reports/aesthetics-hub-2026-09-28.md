# Aesthetics hub and introductory essay

2026-09-28. Local publication preparation; the user pushes.

## Editorial scope

- Replaced the old daily-log-only landing page with an aesthetics hub in Simplified Chinese, Traditional Chinese and English, each with its own URL.
- Added the introductory essay “我不喜欢它，但我看得出它的美” / “I Don’t Like It. But I Can See Its Beauty.” English is independently phrased for English readers; Traditional Chinese derives from the Chinese manuscript with contextual corrections.
- The introduction follows the v2 judgment/aesthetics paper: liking is not identical to recognizing beauty; authority cannot recognize it on a reader's behalf; pleasure is neither necessary nor sufficient; achieved form is not dead; different directions of beauty do not form a compulsory ranking. Illustrative reading, film and pottery scenes are identified as invented examples, not reported events.
- Linked the framework paper and all thirteen ray papers. The hub explicitly distinguishes these academic sources from the thirteen companion essays, which are not published in this batch.
- Retained all 150 daily articles, log.json and artist_dead.html byte-for-byte against the pre-publication HEAD. Existing daily articles remain Simplified Chinese/English; Traditional hub links explicitly disclose the Simplified fallback.
- The hub shows six recent daily posts and an expandable archive grouped by month. The complete archive retains all 150 distinct daily URLs.

## Sources and discovery

The fourteen public source pages were checked against their local theory-repository counterparts before implementation. The v2 framework, rather than the web tool's stale v1 text, was used. No theory-repository files were changed.

Library, Explore, homepage updates, Latest and the updates ledger now expose the new hub/guide. Aesthetics has been assigned to the SAE philosophy search domain so existing daily posts can be found through that filter.

Search contains 10,148 source records; sitemap contains 9,996 canonical URLs. There are five new physical HTML pages plus the rebuilt existing landing page. Regeneration also picks up the already-committed 2026-09-28 daily article previously missing from those generated indexes; that article is not newly authored or edited by this batch. No sitemap URL was removed. The English search chunk now points to the dedicated English hub instead of the old bilingual hub.

## Verification

- Five Python tests: deterministic rendering; IDs, headings, language metadata, schema, canonical/hreflang; local links and anchors; full archive coverage; truthful paper/essay status; discovery, search and sitemap integration.
- Browser checks: six pages at four widths (1440, 768, 390, 320); no horizontal overflow; keyboard language dropdown; archive and paper-map disclosure; section anchors; saved language and legacy fallback; reading/navigation with JavaScript disabled.
- Desktop hub, mobile English hub and mobile Traditional guide screenshots visually inspected.
- Builder freshness, sitemap freshness, updates-ledger consistency and git whitespace checks passed.
- Preservation check: all 152 pre-existing article/input files listed above are unchanged.

## Maintenance

The hub is generated; do not add daily cards directly to index.html. Add the daily HTML article and its log.json entry, then run:

```sh
python3 scripts/build_aesthetics_hub.py
python3 scripts/build_search_index.py
python3 scripts/build_sitemap.py
python3 scripts/test_aesthetics_hub.py
python3 scripts/check_site_updates.py
```

Update the Library card's displayed daily-post count when adding entries. Edit guide source manuscripts in data/aesthetics/; the builder owns all six hub/guide HTML outputs. Add future ray essays deliberately, changing their publication status only once the articles exist. Browser tests are in scripts/test_aesthetics_hub_browser.cjs and accept a local server URL as their first argument.
