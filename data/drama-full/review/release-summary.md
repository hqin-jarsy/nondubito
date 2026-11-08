# Drama language expansion: release verification

2026-11-08. Baseline: c7492b9f80d5ef587b95a1dc7017456ba212e4e4. Local work only; no push or production deployment.

## Content and review

- 23 essays in five new languages: German, French, Spanish, Japanese and Korean, giving 115 full translations and 2,375 translated body paragraphs. Together with the existing Simplified Chinese, Traditional Chinese and independent English editions, all 23 essays now have eight editions at the existing URLs.
- The 475 Chinese paragraphs retain their order and one-to-one paragraph coverage in each new language. Titles, decks, original work and author names, source notes and source labels are localized; source URLs are preserved.
- Every target paragraph and all metadata received translator self-review plus independent Chinese-to-target cross-review in batches 01–05, 06–10, 11–15, 16–20 and 21–23. This was complete paragraph reading, not a sample or a length-only check. Local corrections were applied and reread before acceptance receipts were recorded.
- The original 23 JSON inputs are unchanged. All 69 previously published English, Simplified Chinese and Traditional Chinese body blocks match their original Git baseline byte-for-byte. An independent engineering reviewer separately verified those baseline hashes.
- Existing English was sampled as documented in english-sample.md, not rewritten or exhaustively certified. This work translates the accepted Chinese articles; it does not claim fresh scholarly verification of every statement against primary play editions.

## Build and browsing

- Full translation audit passed: 115 files / 2,375 paragraphs; five signed-off batch receipts match current file hashes.
- All eight drama unit tests pass. Full generation produces 24 pages; build and scoped-discovery checks are repeatable and current.
- Normal rendering succeeds with ctypes.CDLL forbidden. The frozen Traditional Chinese dictionary preserves all 23 original Traditional Chinese bodies. This proves independence from CoreFoundation in the renderer, not an actual Linux execution.
- Local Chrome/Playwright passed 384 page-language-viewport views (24 pages × 8 languages × desktop 1440 / mobile 390) and 65 interaction flows/checks. Additional narrow-width testing used 320 pixels. No page JavaScript errors or tested horizontal overflow.
- Coverage includes one visible edition, paragraph counts, breadcrumb/header clearance, all language switches, copyable language URLs, reload/back, next/previous/index links, repeated mobile menu dismissal, real language-aware header search entries, separately selected search-result language, all five language-hub entries and denied-storage direct navigation.
- Off-origin browser traffic was blocked; this was localhost testing, not a live production or external-font availability test. German desktop and Korean mobile screenshots were visually inspected for wrapping, spacing and navigation clearance.
- Independent engineering review identified a real search-entry language reset; the link parameters were corrected, independently inspected and then exercised in all eight languages by the final browser run.
- The content registry check passed: 496 canonical records from its 1,475-page registry scan, 18 categories. Analytics verification passed across all 13,632 public pages with zero errors or conflict copies; no analytics repairs were needed.

## Existing repository issues and scope

- All 26 workflow commands were run locally. 23 pass; three fail only on four pre-existing 2026-11-04 update-ledger entries missing language arrays: fairy-tales-eight-languages, laughter-eight-languages, cooperation-histories-eight-languages and aesthetics-core-eight-languages. The same four errors were reproduced against the pre-work Git ledger. They were not silently repaired as part of this project. Detailed outputs are in workflow-results.json.
- The new explicit drama series key exposed a homepage test-fixture assumption: a copied synthetic future entry kept the drama key after its URL was changed. The fixture now removes that inherited key, preserving every original assertion. The targeted test passes; independent review confirmed the fix.
- Scoped search/discovery checks pass, and every changed search record belongs to drama or its affected entry pages. A strict whole-site rebuild still differs in record ordering and in the unrelated English koe/index.html search-label field. The latter also differs under the baseline generator and was left untouched. The full search manifest agrees with a fresh build.
- The Analects generator, edition tests and discovery check still pass. Its discovery upsert now preserves the position of an existing update so a later same-day drama release does not reorder it. No Analects prose changed.
- Git whitespace checks passed. No Chinese interpretation changes, unrelated content cleanup, remote push or publication were performed.
