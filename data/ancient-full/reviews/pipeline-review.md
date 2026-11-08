# Ancient Stories full-edition pipeline review

Reviewed 2026-11-08 before final rendering. No commit or push performed.

Historical review note: after this preflight, the author approved episode 04 block 104’s specific wording correction. The additional exact-change receipt and regression coverage are described in `../README.md` and the final integration report; statements below describe the earlier reviewed state.

## Finding

No concrete integration defect found in the reviewed code. This is a code and focused read-only validation result, not a claim that the final rendered site or complete translation set has passed. Translation delivery was still in progress: 98 of the expected 114 foreign arrays existed during the checks.

## Scope

Reviewed `scripts/build_ancient_full_editions.py`, `scripts/test_ancient_full_editions.py`, `scripts/test_ancient_full_browser.cjs`, the Ancient Stories hook in `scripts/build_collection_languages.py`, the new `search.js` route branch, and `.github/workflows/site-integrity.yml`. Also inspected shared inline/body/title/navigation helpers, query-language persistence, collection rendering, search collection, and the structural test parser. Followed `CLAUDE.md`.

## Checks completed

- Verified all 38 immutable Chinese source-file hashes and 120 original HTML snapshot hashes against the manifest.
- Validated all 38 Chinese arrays have one opening heading and only paragraph/separator body blocks. Confirmed episode 04 block 104 retains 回头看.
- Confirmed the recorded source correction is constrained to episode 15 block 31 and inserts only 被 in 善待拒绝者 / 善待拒絕者. Source files remain immutable; the correction is applied to copies and the matching preserved Chinese HTML paragraph.
- Validated all 98 available foreign arrays against Chinese block order, nonempty text, separator handling, emphasis counts, and the fixed Self-as-an-End term. This checks structure, not translation meaning or literary quality.
- Exercised escaping and rejection of raw HTML, unsupported link syntax, and unbalanced emphasis.
- Exercised 12 sentinel mutations: body and title edits in each of six foreign editions. All were rejected by the preservation guard. The compact-builder hook guards the actual file on disk rather than trusting its newly generated abridged input.
- Exercised the scoped search refresh in memory for all eight indexes. Every non-Ancient record remained identical, and each language retained exactly 20 existing Ancient Stories routes.
- Node syntax checks passed for both the browser test and search.js.

## Code coverage observations

- Chinese HTML regions must match the immutable baseline or the single recorded correction before replacement. Foreign article titles and bodies must match the original snapshot, current canonical blocks, or last successful build receipt. Other manually edited page chrome is outside the foreign-prose guard scope.
- The renderer computes all outputs and validates guards before its write loop. Shared escaping prevents translation strings becoming executable HTML.
- The collection builder invokes the full-edition overlay after preparing compact output. The checked-in suite explicitly requires byte-for-byte equality for both direct rendering and collection rendering.
- Existing routes, canonical URLs, language choices, local links, article navigation, card titles, analytics count, Chinese ancillary copy, search titles, and batch-review receipts have structural regression coverage.
- Search routing adds only the Ancient Stories prefix to the existing primary-language query behavior. The scoped search refresh does not regenerate other series or change their records.
- Browser test design covers 456 article language/viewport combinations plus 24 index combinations, exact visible paragraph content, horizontal overflow, language-query persistence, reload, repeated toggles, previous/next/index navigation, history back/forward, invalid stored language, and eight search-result click-throughs. External requests are blocked. These checks were inspected, not run in this review.
- CI adds the Ancient structural suite and stale-output check. Browser coverage remains a separate local validation, not a GitHub Actions step.

## Pending final validation

After all 114 translations and four batch reviews are present, run the authorized final render and scoped search refresh, then the complete Ancient unittest suite, renderer `--check`, compact-builder idempotence assertion, analytics checks, and local browser test. Final browser execution, screenshots and reading-quality review belong to the subsequent integration stage. No HTML was rebuilt and no source or translation prose was edited during this review. A full-series or browser pass must not be inferred from the focused checks above.
