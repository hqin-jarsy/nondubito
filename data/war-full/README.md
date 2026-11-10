# War Theory: complete multilingual readings

## Scope and editorial limits

This restoration covers seven main essays, eight interfaces and their conclusion, plus the complete series index. The 16 Chinese source bodies contain 1,121 units, including 12 complete tables. Japanese, German, French, Spanish and Korean are restored as complete readings rather than abbreviated adaptations. The existing English was read in full twice and repaired locally; intact passages were retained.

The immutable source capture records the local repository, not the live website. `sources/`, `translations/`, the raw English bodies and the index baseline are provenance, not generated caches to delete. Exact, source-bound before/after overlays carry corrections into the final pages. The 17 primary pages provide Simplified Chinese, Traditional Chinese and English; 85 separate foreign pages provide the other five languages, for 102 physical pages and 136 language/page readings.

The author approved five groups of historical clarifications across eight Chinese body units: Assyrian imperial collapse versus cultural continuity, Sparta's contraction and military defeat, the limited Spain–Netherlands comparison, Versailles Article 231, and the political coercion of the Tui'en arrangement. The last retains the analysis of an openly declared strategy and imperial pressure; it does not turn imperial permission into a cost-free modern choice. Only the unsupported universal legal claim about all sons was withdrawn. These changes are aligned in all eight readings. The English ep06 title was separately corrected from “Stalemate” to “Balance of Power”; its whole-title Traditional Chinese dictionary entry must follow the new English key without changing the Chinese title.

Unapproved source questions stay unchanged. In particular, the interface-three child's death and “all four questions pass” argument, the reference to a full treatment in interface two, the two-book reference, and the possible missing character in the Chinese title are not silently repaired. Additional classical-text ambiguities and historical scope cautions are recorded in the review receipts. A translation pass is not a certification that every factual assertion or source-level argument is settled. Two proposed French classical-text reinterpretations are explicitly deferred, not applied.

## Reading, review and integration

All five translators compared every article with Chinese and checked approximately five-article batches for conceptual drift. Independent reviewers then read every body unit, table, title, deck and the complete index. Individual receipts are in `reviews/`; separate final receipts bind the source, original manuscript, independent recommendations, author overlays and effective final body hashes.

English has a first full reading with 129 localized body candidates and ten deck candidates, plus twelve index nodes. The independent second reading accepted 127 body candidates, treated one as superseded by the author-approved historical correction, and replaced one narrowing of the general requirement to face questioning. Its additional changes are exact overlays, not a wholesale retranslation. The reports retain rejected and superseded decisions. They also distinguish source ambiguities from translation defects.

The independent foreign-language review proposed 176 exact changes: Japanese 10, German 27, French 30, Spanish 68 and Korean 41. All were replayed exactly; the two deferred French interpretations were excluded.

The final integration review does not pretend to be a fresh full semantic reading. It relies on the documented independent full readings and independently replays every exact correction, verifies the markup and source bindings, checks the approved historical mappings and Traditional Chinese dictionary changes, and binds the resulting edition. Original review receipts that say “changes requested” describe the earlier state and remain as evidence; final integration receipts record whether those changes were applied.

## Reproduction and safeguards

Run from the repository root with ordinary, non-optimized Python:

```
python3 -B scripts/prepare_war_author_traditional.py --check
python3 -B scripts/build_war_full_editions.py --check
python3 -B scripts/refresh_war_full_discovery.py --check
python3 -B scripts/test_war_full_editions.py --release
python3 -B scripts/test_war_browser_fixtures.py
python3 -B scripts/check_web_analytics.py
python3 -B scripts/test_web_analytics.py
```

The renderer rejects stale source/manuscript/review hashes, unknown current public-page edits and optimized Python. Exact overlays preserve tags, attributes, emphasis and complete table cells. The Traditional Chinese updater replaces complete text-node keys and values and preserves unrelated mappings and the JavaScript shell. The discovery updater changes only War search records and sitemap dates, and verifies all shared inputs before its first write. No homepage announcement or update-ledger item is part of this change.

The nine legacy interface primary pages had repeated closing head tags. Normalization is restricted to the head and does not rewrite body prose. All readers use the shared language controller, contain tables within horizontal scroll wrappers, retain the source links and have the correct analytics token.

## Final validation

The final code passed 33 release regression tests, seven browser-fixture tests and six analytics tests. All 102 generated pages and the three Traditional Chinese dictionaries were current on recheck. Scoped discovery had no stale output; all non-War search records and 13,701 non-War sitemap entries remained unchanged. The all-site analytics check covered 13,822 public pages with zero tracking errors and zero conflict copies. No analytics fixes were needed.

`qa/browser-final-2/run.json` records the complete successful automated browser run in isolated headless Chrome 157.0.8103.40:

- 408 viewport readings: 17 pages × eight languages × widths 320, 375 and 1440.
- 128 language selections across a main essay and an interface, including the already-active options.
- 16 directory/next/previous/return navigation chains and 16 actual search-result clicks.
- Six invalid-storage fallbacks, nine explicit-query overrides, 24 blocked-storage readings and 85 no-JavaScript foreign-language pages.
- All 96 language/table combinations at 320 pixels, checking complete rows/cells and reachability of the final column, without requiring a table that fits naturally to scroll.
- 456 screenshots: 240 paragraph starts, 192 left/right table views and 24 directory tops. These are captured evidence, not a claim that every screenshot was manually reviewed or that each long paragraph fits in one frame.

The final run recorded zero failures, unchanged source/runtime hashes and 193 served artifacts checked against the local bytes. The expectation fixture comes from reviewed source/manuscript overlays and final Traditional Chinese dictionaries, never from the output HTML it tests. External requests were blocked. The user's active browser profile was not used. These are desktop-Chromium viewport tests, not a claim of testing physical mobile hardware or every browser engine.

The independent visual sample covers 128 actual images, 16 per language: all eight amended historical paragraph starts at 320 pixels, one amended desktop paragraph, two ordinary desktop main/interface starts, two complete left/right table pairs and the directory top. This is a representative layout check, not manual inspection of all 456 captures. The visual reports and final engineering sign-off are recorded separately in `qa/visual-*.json` and `qa/engineering-final.json`. The raw automated run intentionally keeps its separate “visual review pending” marker; no one rewrites it to imply that the browser script performed visual judgment. The 128-image sample found no blocking visual defect. One low-severity German line-break observation remains: at ep03 u21 on the 320-pixel viewport, the long compound “Abschreckungsinstrumentariums” fills a line and its period begins the next. The text is complete and readable, with no overflow or occlusion; no semantic rewrite or global hyphenation change was made for this cosmetic issue.

The failed first run is retained in `qa/browser-final-1/`, including its original runtime copies. It exposed two actual reading defects: inline display rules let a second source note appear in the other language, and War search results did not carry the selected reading language. Both were fixed and the complete matrix rerun. It also exposed two test-harness defects: CSS capitalization confused button identity, and automatic favicon response bodies could disappear after navigation. The final harness matches the actual DOM label, captures the favicon explicitly once, marks automatic favicon responses as unread, and drains other response reads before navigation. None of the first run's failures is counted as a final pass.

This edition is prepared for a local commit only. It has not been pushed or published. Source-level questions listed above remain the author's decisions.
