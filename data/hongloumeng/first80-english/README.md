# Independent English translation work in progress

This directory is project data, not a published English reading edition. Chapters 1–15 have passed chapter-level and cumulative model editorial review: 751 units are **accepted** and 3,723 remain **pending**. This is not native-human publication sign-off; the eighty-chapter translation is unfinished and has no public English reading presentation. Chapters 81, 82, 84 and 85 remain unchanged; chapter 83 has one separately reviewed funeral-procession correction.

## Frozen source and stable alignment

`source-map.json` is reproducible from the already-public `../first80-public/reading.zh.json`. It freezes the file and manifest hashes and maps 80 titles plus 4,394 source blocks. Each unit has a stable chapter/position ID, exact source-text SHA-256, Unicode code-point count, and original layout flags. IDs are scoped to this frozen source; a future Chinese revision requires an explicit source migration, not silent renumbering or acceptance of changed hashes. No private manuscript or editorial approval is copied here.

The full body contains 586,209 code points: 3,399 prose blocks, 928 verse lines, 54 couplet lines, 8 diagram lines, and 5 letter blocks. Chapters 1–5 contain 378 blocks / 35,513 body code points plus five titles (383 units). This is a workload inventory, not an estimate of English word count or translation quality.

## Working records

`progress.json` is the versioned working corpus. Keep one record for every source ID, in exact source order. Do not remove untranslated records. `pending` records have empty segments and reviews. `draft` means independently composed English exists, not that it has passed review. Prose may use multiple ordered English paragraphs in `segments`; title, verse, couplet, letter, and diagram units retain one segment each, with the original kind. Original layout flags travel with each assembled record. This first schema does not merge multiple source units into one English segment. Revisit the schema explicitly if cross-source paragraph grouping is needed.

`reviewed` and `accepted` require separate `bilingual`, `literary`, and `consistency` review records, each bound to the exact translated content hash and current standard snapshot. A reference must identify an actual review, not an automated test. Detailed review discussions stay in ignored local QA; published references should be neutral editorial IDs with no private transcript, personal metadata, or internal tooling information. Reviewed means those reviews have been performed; accepted means the resulting wording was explicitly accepted in the editorial workflow. The validator checks recorded evidence bindings, not the truth or quality of a review. Never promote status merely to pass a build.

Normative files live in `docs/hongloumeng/translation/`: `english-standard.md`, `english-terms.json`, and `english-voices.json`, `english-batch-001-005.json`, `english-batch-006-010.json`, `english-batch-011-015.json`, `english-batch-016-020.json`, and `CHANGELOG.md`, under `english-1-110-v0.5`. Review snapshots hash all eight files. Any change invalidates prior review records, including those in already accepted batches, until actual regression review. Preserve changes through git history and the standard's change log; do not rewrite old review evidence to make it appear current.

Every five chapters require an accepted batch checkpoint bound to all translated units and the current standard snapshot. Expansion into the next batch is blocked until that checkpoint exists. Review complete Chinese-English coverage, literary flow, names and terminology, character voices, poems, allusions, diagrams, and consistency with 81–85 and previous accepted batches. Search the entire aligned corpus for terms and voice decisions during this review. Character counts, English-letter presence, structural coverage, or matching paragraph counts do not establish semantic completeness or literary quality.

## Commands

Run from the repository root:

- `python3 -B scripts/hongloumeng_english_pipeline.py validate`
- `python3 -B scripts/test_hongloumeng_english_pipeline.py`
- `python3 -B scripts/hongloumeng_english_pipeline.py assemble --output data/hongloumeng/first80/qa/english/assembly.json`

Parallel chapter drafts may be written as ordered arrays to `chapters/ch001.draft.json` (likewise other chapter numbers), using the same unit record schema. `python3 -B scripts/hongloumeng_english_pipeline.py import-draft --chapter 1` validates the entire resulting corpus before saving, accepts only draft records with no review claims, and refuses to overwrite any non-pending unit. Keep a single editor responsible for importing into `progress.json`; concurrent imports are not supported. The chapter files are author or historical draft working copies, not additional canonical corpus units or current acceptance authority. Older chapter 6, 8 and 10 draft copies may retain former gaps. The current complete English text, review records and accepted checkpoints for chapters 1–15 are in `progress.json`.

Initialization is deliberately non-overwriting. Assembly is deterministic JSON, preserves unfilled source locations, marks itself `translation-work-in-progress` and `publishable: false`, and is confined to the ignored English QA directory. There is no HTML output or website integration. The `release` action always fails closed. A later publication implementation needs separate review, exact approved scope (selected chapters or all eighty), and explicit authorization; incomplete or unreviewed work must never be silently fed to the public renderer. Existing public reading renderers continue to reject unsupported English input.

## Source questions and safe saves

The global `sourceIssues` registry records explicit source questions, not guesses based on punctuation. Each entry has an `id`, mapped `unitId`, current `sourceHash`, `state` (`open` or `resolved`), plain `description`, and `resolution` (null while open; a specific verified outcome when resolved). An open issue blocks unit acceptance and therefore batch acceptance. Issue content and state participate in the affected unit's review hash and batch hash: changing, resolving, or removing an issue invalidates earlier review bindings. Closing an issue requires actual source and translation review; no automatic status promotion occurs. Ordinary narrative ellipses are allowed.

Progress imports use a complete same-directory temporary write, flush/fsync, and atomic replacement. A failed write or replacement preserves the previous canonical file. This remains a single-editor workflow, not concurrent merge support. Earlier private reviews remain historical evidence; never mechanically regenerate their hashes to imply a new review.

The prior frozen source incorporated six corrected blocks without changing any stable ID or layout. The six English alignment issues are recorded as resolved after the corresponding draft revisions and independent review; their reviewed revisions are now included in the accepted first batch. Source correction alone does not resolve an English draft issue; old per-unit hashes in draft files must not be mechanically rewritten.

Two frozen translator notes are held separately in `reader-notes.json`, bound to their source units and clearly labelled as translator commentary. They are not original narrative, are not inserted into translation segments, and are not yet integrated into a reading presentation.

## Editorial and source history

The v0.3 standard was frozen on 2026-11-11 after a normative-delta review of the accepted first batch. The later v0.4 standard recorded a limited isolated-drafting exception for chapters 11–15 while four source gaps prevented second-batch acceptance. The 589 then-existing translations retained their wording and original review references alongside dated standard-regression references. These normative-delta checks were not new full bilingual or literary rereads. The seven-file v0.4 snapshot is retained as historical evidence.

Seven author-approved readability decisions subsequently changed seven stable Chinese source units (eight textual occurrences) in chapters 6, 8, 10, 17 and 18. Simplified and Traditional data and the corresponding ten chapter pages were rebuilt, with all other source units, titles and layouts unchanged. These are edition-specific readability choices informed by public Chinese transcriptions, not claims of historical-original verification. The source map, canonical progress and translator-note global bindings migrated to that frozen source without changing the 589 existing English translations or their actual review evidence. Historical source-query reports retain their original as-of findings.

The source migration initially left seven English alignment issues open. Four complete new translations in chapters 6–10 have now received independent bilingual, literary and consistency review against the corrected Chinese. Their exact issue resolutions and twelve actual review records are preserved in canonical progress. The other three issues in chapters 17–18 remain open and their units remain pending.

## Completed chapters 6–10

All 210 units are accepted. The existing 206 translations and their actual review evidence are unchanged; four complete source units, comprising 20 English prose segments, fill the former gaps. `EN-B006-010-COMPLETED-CUMULATIVE-20261111` records a fresh sequential English reading of all 210 units, with targeted Chinese rereads and sampled earlier/later continuity checks. It is not a new complete bilingual reread of all 210 units or of earlier and later chapters. The accepted checkpoint binds the complete ordered batch and the four resolved issue records. No required changes remain from that review.

## Integrated chapters 11–15

The five `chapters/ch011.draft.json` through `ch015.draft.json` files preserve 158 independently composed units. Their author records remain `draft` with empty `reviews`; their exact manuscript bytes are unchanged. `isolated-review-011-015.json` preserves the original isolated-review evidence, all 474 bilingual, literary and consistency review records, and source-alignment provenance. Its current integration metadata now records that these exact units and reviews are also in canonical progress. This is no longer an unimported isolated batch.

The preserved cumulative review, `EN-B011-015-CUMULATIVE-20261111`, read all 158 English units sequentially alongside Chinese, with targeted earlier-text continuity checks and no required changes outstanding. Its batch hash binds their ordered content hashes. The source migration changed only global source and source-map bindings: all 158 local source hashes, five manuscript hashes, review records and cumulative evidence remained unchanged. Controlled canonical integration reused that exact evidence after second-batch acceptance; it does not claim a fresh full reread.

Canonical progress now includes all 158 units as accepted, with an accepted third-batch checkpoint. Review and cumulative evidence must be rechecked if manuscript, relevant source issue, source-unit or normative bindings change. These are model editorial acceptances, not native-human publication sign-off. The eighty-chapter work remains unfinished, and the English publication pipeline remains disabled. No English reading page is published by these data changes.

## Chapters 16–20 and the v0.5 standard

Chapter 16–20 drafting and review are underway; this batch is not canonically accepted. The first three accepted checkpoints permit work on the fourth batch. Chapters 21 onward remain blocked until the fourth checkpoint is accepted, and publication remains disabled.

The eight-file v0.5 standard was frozen after the actual normative-delta review EN-V05-R2-DELTA-20261111, including the corrected inherited Mackerel identity. All 751 accepted translations, 2,253 review content hashes, original review references, and three accepted batch content hashes are preserved. Only standard bindings and appended delta references migrate; this is not a fresh full bilingual or literary reread of the 751 units. The matching chapter 11–15 review manifest records this migration separately from its preserved source-alignment and canonical-integration provenance. All three chapter 17–18 English alignment issues remain open until actual translation review resolves them.
