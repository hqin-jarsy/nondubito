# Korean regression boundaries

Verified 2026-11-14. Comparison baseline: `f7a25db` (before Korean work); comparison target: `be7319a` (Korean chapters 1–70). This is a focused regression diagnosis, not a claim that all historical tests pass.

## Isolated baseline reproduction

The baseline was materialized with `git archive f7a25db` into `/tmp/nondubito-baseline-f7a25db.p4FMf4`. No checkout/reset or source edits were made in the live repository. Representative tests ran with Python bytecode generation disabled.

1. `PYTHONPATH=scripts python3 -B -m unittest test_hongloumeng_b16_binding.B16Tests.test_preparation_counts_and_no_approval`
   - Baseline result: ERROR, `B16 unchanged predecessor changed: classics/hongloumeng/ch001.html`.
   - The B16 historical validator hashes complete files listed in its unchangedRootFiles manifest. The identical failure therefore predates Korean navigation.
2. `PipelineTests.test_frozen_inventory`, extracted using the existing prefix of `scripts/test_hongloumeng_english_pipeline.py` before its suite execution.
   - Baseline result: FAIL, `586252 != 586250`.
   - Companion extracted tests `test_pending_corpus_is_valid_but_not_publishable` and `test_review_binds_exact_text_and_standard` passed.
3. `PYTHONPATH=scripts python3 -B -m unittest test_hongloumeng_b16_binding.B16Tests.test_wrong_kind_still_rejected_by_strict_validator`
   - Baseline result: FAIL. Expected `Verse, diagram, or prose kind lost`, but validation first raised `Review is stale after standard change`.
   - This error-order/snapshot mismatch also predates Korean changes.
4. A single current-presentation test was additionally attempted at baseline: `test_hongloumeng_reading_presentation.PresentationTests.test_real_complete_accepted_input_and_projection`.
   - Its class setup failed with `B16 incomplete semantic current-binding receipt`; zero test methods ran. This is not a successful projection check.

The coordinator stopped the broad historical discovery run with SIGINT (exit 130). It was not completed and must not be reported as a full-suite pass or as a complete inventory of failures. The findings above establish only these representative baseline failures, not that every observed failure is historical.

## Whole-file snapshots versus article bindings

A read-only comparison of Git blobs between `f7a25db` and `be7319a` examined all 504 changed existing, non-Korean HTML files under `classics/hongloumeng`:

- Every extracted `<article ...>...</article>` sequence remained byte-identical. Pages without an article remained without one.
- For 503 files, deleting the exact bounded `KOREAN-NAV` insertion restored the entire baseline file exactly.
- The sole additional difference was `classics/hongloumeng/es/index.html`: four labels changed from `Pasajes pendientes` to `Adaptación no explícita`. Reversing these four replacements as well as removing Korean navigation restored that entire file exactly. This is an index-label change, not a chapter article change.

Korean language links intentionally change complete HTML hashes. Consequently a historical whole-file hash check can fail even when chapter prose is untouched. This does not justify repinning historical evidence or assuming other mismatches harmless.

`scripts/check_hongloumeng_korean.py` instead authenticates the exact article hashes in `data/hongloumeng/first80-korean/source-bindings.json`, then checks each Korean chapter against current Chinese block counts, order, kinds, layout classes, nonempty Korean text, canonical metadata, and local links. It explicitly does not certify translation accuracy. The coordinator reported the through-70 check still passing with 3,826 blocks after stopping the broad run; that result is separate from the baseline reproductions above.

## Continuing verification

Preserve old snapshots, manifests, receipts, and validators as historical evidence. Use the Korean article bindings, focused discovery tests, reader generation checks, and independent chapter reviews for the new work. Classify any additional historical failure individually against the pre-Korean commit before calling it preexisting. If whole-page current-presentation verification is needed, add a separately reviewed successor or bounded reversible navigation proof rather than changing historical hashes or weakening content checks.
