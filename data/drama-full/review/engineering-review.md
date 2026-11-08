# Independent engineering review

Reviewed on 2026-11-08 against source commit `c7492b9f80d5ef587b95a1dc7017456ba212e4e4`.

## Scope and conclusion

Reviewed the drama generator, language labels, translation audit, discovery refresh, scoped JavaScript/CSS, search and content-registry changes, Python/browser tests, and CI additions. No remaining concrete blocking defect was identified in the reviewed code. This review does not repeat the translators' semantic review.

One P2 issue was identified and corrected: the actual header Search link originally lost the selected German, French, Spanish, Japanese or Korean edition. The corrected `drama.js` now sets the search URL's `lang`, `in`, and, where applicable, `ui` parameters on every language application, and clears stale foreign `ui` when switching back to English or Chinese. The browser test now exercises the real header link for all eight languages, in addition to the independently selected result-language flow. The fix and added assertions were inspected; browser execution is not claimed by this review.

## Independently executed verification

- Compared all 69 original English, Simplified Chinese and Traditional Chinese prose-block hashes in the manifest directly with the specified Git baseline: all matched.
- Rendered all 24 pages with `ctypes.CDLL` patched to reject framework loading: output matched the published files, demonstrating that ordinary rendering uses the frozen Traditional Chinese dictionary rather than CoreFoundation.
- `python3 -B scripts/audit_drama_translations.py`: passed, 115 translation files and 2,375 paragraphs.
- `python3 -B scripts/build_drama_series.py --check`: passed, all 24 pages current.
- `python3 -B -m unittest discover -s scripts -p test_drama_series.py`: all eight tests passed.
- `python3 -B scripts/refresh_drama_discovery.py --check`: passed, discovery and scoped search current.
- `node --check` for `drama.js` and `test_drama_browser.cjs`: passed.

Earlier missing-receipt/discovery failures were temporary generation states and disappeared in the final rerun.

## Verification boundaries

This reviewer did not execute Playwright, inspect screenshots, run the complete repository CI workflow, or execute on Linux. Mobile rendering, interactive browser behavior and the full CI outcome therefore require the release owner's separate final checks. The no-CoreFoundation test establishes renderer independence from the macOS conversion framework; it is not a claim of an actual Linux run.

Only this report was written by the reviewer. No source files were changed, committed or pushed.

## Final fixture follow-up

Reviewed the two-line fixture correction at `scripts/test_home_updates.py:61–62`. Removing the copied `series_key` before assigning a synthetic `essays/future/epN.html` URL is appropriate: the fixture represents a different series, while the inherited explicit override would otherwise keep identifying it as drama. The production grouping behavior and all four existing assertions remain unchanged, including the assertion that 200 synthetic updates produce only one future-series entry and four homepage rows. Independently reran `PYTHONPATH=scripts python3 -B -m unittest test_home_updates.HomeUpdates.test_hundreds_of_updates_cannot_expand_home`: passed.

Separately, the release owner reported a successful browser run with 384 views, 65 actions and zero page errors, and inspection of German desktop and Korean mobile screenshots. The owner also reported that 23 of 26 CI checks passed, with the remaining three attributable to four historical ledger entries missing `languages`. These are owner-reported results, not checks independently rerun in this review; they do not change the verification boundaries above.
