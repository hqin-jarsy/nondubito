# Relationships full editions

Independent repair for `essays/everyday/relationships/` only. Not the eight
series in daily-full and not the separate philosophical Relation series.
Original baseline commit and all 186 original HTML file hashes are recorded in
preservation.json. Sources hold 30 essays, 1,237 ordered paragraphs, plus index.
Both Chinese regions are preserved verbatim, including inline HTML, titles,
decks, reading doors, source URLs and chapter metadata. No Chinese decision is
implicitly approved by creating a snapshot or translation.

## Article translation contract

`translations/{en,ja,fr,de,es,ko}/{slug}.json`:

- `language`, `slug`, `source_sha256`: exact matching source identifiers.
- `title`, `deck`, `chapter`: translated strings, not HTML.
- `body`: full HTML paragraph strings (`<p>…</p>`), one per source paragraph,
  in original order. Never merge quotations or insert headings.
- `entry_door`: translated inner HTML, retaining original link target.
- `review`: a truthful description of writer review, not a quality certification.

Preserve all argument, examples, qualifications, emphasis and source links.
Never summarize to achieve apparent paragraph coverage. Keep Self-as-an-End
unchanged. HTML is restricted and source-relative links are rebased by renderer.

## Index contract

`translations/{lang}/index.json` has language, slug (`index`), source_sha256,
title, deck, route_title, route_intro, chapters (six strings in order),
theory_label, theory_intro (inner HTML with source link), and review.
Cards use the reviewed article titles/decks. Existing site labels and language
navigation shells are retained. The six chapter-entry route defect is repaired
only with final `--complete --fix-routes`, using 01,06,11,16,21,27 in eight views.

## Review gates

Writer self-reports: `reviews/self-review-batch01-en-de.json` (or fr-es, ja-ko).
Fields: episodes, languages, status (`self-reviewed`), reviewer, review_scope,
limitations, findings, translation_sha256. Hash map keys are relative to
translations, e.g. `en/01-when-care-becomes-control.json`; values are SHA256 of
exact UTF-8 file bytes, including final newline. Scope describes actual checks.
A self-report does not unlock publication and is not an independent review.

Independent acceptance: `reviews/batch01.json` through batch06.json. Fields:
episodes (consecutive five, starts 1/6/11/16/21/26), status (`reviewed`),
independent_semantic_review (true), reviewer, review_scope, limitations, and
translation_sha256 (all 30 exact files). Include source findings, resolutions,
and links to supporting reports as additional fields. Structural tests alone
are never grounds for independent_semantic_review=true. An altered translation
invalidates its review hash. `reviews/index.json` uses the same review fields
and exact six index translation hashes, without episodes.

`render(preview=[('en','01-when-care-becomes-control')])` returns in-memory
outputs for specified structurally valid drafts, without a review receipt.
It writes nothing. Do not claim preview output is accepted or published.
`--check` verifies only independently accepted batches. Default writes only
accepted batches. While source observations remain unresolved, actual publication
requires the explicit `--preserve-pending-source` option. It publishes only faithful
reviewed translations of the unchanged Chinese; it neither approves a suggested
Chinese amendment nor marks an observation resolved. Source snapshots and Chinese
regions are still verified, and the two author questions remain recorded as pending.
Actual Chinese amendments require explicit author evidence and coordinated source/hash
updates, never merely a status change. `--complete` requires all 180 articles and six
index reviews.

No public pages, search data or sitemap were changed during infrastructure
preparation. Tests are structural and cannot certify semantic completeness.

For local UI review before publication, run `python3 -B scripts/serve_relationships_preview.py`. It serves current article/index drafts in memory on 127.0.0.1 without writing public HTML. Draft preview is not semantic acceptance. `test_relationships_full_browser.cjs` accepts RELATIONSHIPS_EPISODES=1,2,3,4,5 for a batch, and RELATIONSHIPS_SEARCH=1 only after final discovery publication.

## Completion — 2026-11-09

All30 essays now have complete, independently reviewed English, Japanese, French,
German, Spanish and Korean editions: 1,237 source paragraphs and7,422 translated
paragraphs. Six five-essay checkpoints and the index have exact final review seals.
The186 local HTML pages and scoped discovery records have been generated. The
simplified/traditional Chinese article regions remain verbatim; only the index
reading route was structurally corrected. Source questions03 and10 remain pending.

Final validation:20 tests passed without skips;496 responsive reader views,64
directed language transitions and16 actual search-result clicks passed. Full
workflow rerun passed53 of56 checks with only the same three pre-existing failures
caused by four unrelated update-ledger entries missing languages. See
`reviews/final-validation.json` for exact scope, commands, limitations and failures.
No push or deployment was performed.
