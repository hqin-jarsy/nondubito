# Aesthetic rays 01–03: publication QA

2026-09-28. Baseline `f28c3b8`; working tree clean at start. Local commit only; the user pushes.

## Content and boundaries

Three independently developed essays, each in Simplified Chinese, Traditional Chinese and English:

1. Naming the Stars Does Not Finish the Sky — grounded distinctions do not acquire final authority over everything. Not praise of ignorance, disorder, or direct mystical access to an undivided whole.
2. The House Is Still Unsold. The Argument Has Changed. — a question opens a space for reasons, including revision of its own initial distinction. The money/home distinction is challenged inside the story; no forced sale or reconciliation.
3. Both Answers Are Right. Why Is This One Beautiful? — correctness versus a reason becoming visible. Pairing, odd-length sequences, and a finite-list proof for primes can be retraced. Explicitly states that multiplying listed primes and adding one need not yield a prime.

Chinese manuscripts are approximately 1,850–1,950 CJK characters each; English manuscripts are approximately 1,300 words each. English is independently phrased; no translation service was used. All three Traditional bodies were read in full, with contextual corrections for 螢幕, 帳單, 沉默, 鬆口氣 and 餘一, among others.

The three source papers were retrieved read-only from self-as-an-end.net: HTTP 200 and byte-identical to local theory-repository files. No source-theory files were edited. The public web-reading tool could not access those URLs, so direct HTTPS was used for verification.

The Riemann-hypothesis status was checked against the Clay Mathematics Institute's current page, which labels it unsolved. This advanced topic is linked as further reading, not explained by an inadequate analogy or treated as proved. All numerical examples were recomputed. Invented people, dialogue and scenes are disclosed in localized endnotes; the worksheet scene is explicitly not claimed as a historical reconstruction of Gauss's childhood.

This is the first batch, not all thirteen essays. The remaining ten are planned in `data/aesthetics/rays-editorial-plan.md`; no pending essay has a public article link.

## Integration and preservation

- Nine new HTML pages at `essays/aesthetics/{ray01,ray02,ray03}.html` and their `en/` and `zh-hant/` counterparts.
- Published-only `rays.json` drives hub cards, manuscript rendering, source citations and chapter links. Three language URLs per essay, with canonical and reciprocal hreflang metadata.
- Opening essay leads to ray 01; rays 01–03 link in sequence; ray 03 returns to the directory with an explicit remaining-publication note.
- Library, homepage and Latest expose the batch. The earlier hub-launch news now uses historical wording to avoid contradicting the newer availability status.
- All 150 daily articles, log.json, artist_dead.html, and both opening-essay manuscript files are byte-identical to the baseline (154 files). All three rendered opening-essay bodies are also unchanged; their end navigation is extended.

## Verification

- Seven Python tests passed: deterministic generation of fifteen hub/guide/ray pages; language metadata, canonical/hreflang and source schema; local links and anchors; archive and publication status; source-to-page completeness; chapter links; Traditional regressions; arithmetic; discovery/search/sitemap inclusion.
- Sixty browser combinations passed: fifteen pages at widths 1440, 768, 390 and 320. No horizontal overflow; one visible title; dropdown keyboard use; archive and source-map disclosures; section anchors; language switches with preserved anchors; next/back navigation; legacy-language fallback; no-JavaScript reading and chapter navigation.
- Desktop Chinese hub, mobile English ray 02 and mobile Traditional ray 03 screenshots visually inspected.
- Search: 10,157 source records. Sitemap: 10,005 canonical URLs. Nine article URLs added. No pre-existing URL removed from sitemap; search changes remain within aesthetics.
- Updates ledger/order check and git whitespace check passed. Final builder, search-index and sitemap freshness checks run before commit.

## Rebuild

Edit individual `data/aesthetics/rayNN-zh.md` and `rayNN-en.md` manuscripts, and the completed-only `rays.json` metadata. Run `build_aesthetics_hub.py`, `build_search_index.py`, `build_sitemap.py`, `test_aesthetics_hub.py` and `check_site_updates.py`. Browser tests use `test_aesthetics_hub_browser.cjs` with a local server URL. The builder does not rewrite daily post bodies.
