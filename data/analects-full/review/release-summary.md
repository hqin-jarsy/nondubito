# Complete Analects editions: release checks

Date: 2026-11-08. Baseline: 10bfd10ee723b4d3ba5778319bf49ed1eb95b1b1.

## Delivered

- Fifty complete English translations, approximately 53,000 words including titles and source notes, replacing five-paragraph versions.
- The existing 250 complete v0.2 German, French, Spanish, Japanese and Korean manuscripts imported with provenance. Nine exact new target-language corrections; no wholesale retranslations.
- Seventeen explicit minor Chinese corrections, synchronized in simplified/traditional web text and the six translations. Original Chinese and received drafts remain immutable.
- All 306 existing article/index URLs rebuilt. Fifty essays remain available in eight reading languages. Titles, adjacent-essay navigation, indexes, source notes, language menus, search, library, language hubs, homepage and sitemap are connected.
- Older builders use the complete inputs, update overwrite receipts and fail closed if those inputs are unavailable. Builds no longer require a Mac-only Chinese converter or external Documents paths.

## Editorial depth

All fifty English essays were compared in full against Chinese in ten five-essay batches. An independent review compared 21 complete Chinese–English pairs, including one from every batch and additional risky passages. It detected and resolved a weakened claim in English03 before release.

The five-language review read every supplied editorial note, 54 complete translated essays and cross-language risk passages. Checks specifically revisited 37's exclusive/superlative wording, 20's Japanese/Korean interpretation wording and claim strength, 35's Yan/Ziyou identity, and 50's literary phrasing. It did not perform a new line-by-line final edit of all 250 target texts, and is not represented as native-speaker expert certification.

Eleven source-level author decisions remain recorded separately. Their theoretical/evidential issues were not silently resolved through translation. No comprehensive external re-verification of all historical claims, manuscript variants or external links is claimed.

## Verification passed

- Eight focused Python tests: immutable source hashes; all 300 foreign article bodies; Chinese changes restricted to recorded fixes; legacy-build safety; links, metadata and analytics; exact supplied-copy corrections; exact scoped search records and unique page counts; discovery completeness.
- Complete renderer and both legacy commands pass on-disk `--check`; 306 generated pages are reproducible.
- Browser: 800 article views (50 × eight reading languages × desktop/mobile), 49 navigation/language/search clicks, no JavaScript errors, no horizontal overflow. Includes language persistence through reload, previous/next and Back, repeated mobile-menu opening/Escape, and opening search results in the selected language.
- Visual screenshots inspected at 1440px and 390px. Fixed the pre-existing series-return link being partially covered by the fixed header; visibility now asserted on all article views.
- All 13,632 public pages pass analytics verification, with zero tracking errors and zero conflict-copy pages.
- Shared-file scope checked against the baseline: existing update entries and previous Latest content are unchanged; only the designated homepage and Analects language-hub regions changed. All search changes are within Analects. Sitemap retains the same URLs, changing only 311 relevant dates.

## Existing failures retained, not concealed

The repository integrity workflow was run in full. Nineteen of 22 commands pass. Three commands fail for the same pre-existing four ledger entries lacking `languages`: fairy-tales, laughter, cooperation-histories and aesthetics-core, all dated 2026-11-04. The failures are `check_site_updates.py`, one `test_home_updates.py` assertion and one `test_method_introduction.py` assertion. These four original entries were verified unchanged from baseline. The present Analects entry has all eight language codes.

The broad search-index byte-for-byte freshness check also remains non-green: existing record ordering differs from a fresh whole-site build, and the English `koe/index.html` record has pre-existing stale content. Every Analects record matches the full generator exactly. Unrelated search records and their order were deliberately preserved; `global-search-status.json` records the comparison. This release does not claim all-site CI is green.

See `regression-results.json`, `browser-results.json`, `scope-verification.json`, `global-search-status.json`, the independent review and the per-batch language reviews for exact evidence.

## Preserved received-file formatting

A full staged `git diff --check` reports ten extra final blank lines in received `notes.zh.md` files (11, 12, 14, 15, 16, 17, 18, 41, 43, 44). These bytes belong to the supplied immutable v0.2 package and are intentionally retained so its hashes remain exact. The whitespace check passes for every staged file outside the immutable `received/` package. No newly authored code or manuscript whitespace error is hidden by this exception.
