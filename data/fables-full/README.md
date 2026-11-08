# Complete Fables editions

The twenty-three Chinese essays are the source. Each of the six foreign editions
is translated in full, paragraph by paragraph. The existing bilingual URLs and
five language subdirectories remain the reading destinations.

## Inputs and preservation

- `manifest.json` records the clean starting commit, original page hashes, Chinese
  region hashes, and the source text counts.
- `snapshots/*.html.txt` and language subdirectories hold immutable page backups.
  The `.txt` extension prevents the site collectors treating them as public pages.
- `source/NN.json` holds the Chinese title and every paragraph, with a separate
  ordered layout retaining quotations, rules, emphasis, and internal line breaks.
- `translations/LANG/NN.json` is the authoritative complete translated text array.
  Its index matches `source/NN.json` exactly. Do not replace it with a summary.
- `reviews/LANG-RANGE.md` records the five-essay review batches, then 21–23.
  These distinguish translator self-review from additional independent checks.
- `last-build.json` is the body/title receipt from the previous successful render.
  The builder refuses unrecognized manual changes to foreign HTML. Preserve
  intentional edits in the canonical translation before rebuilding.

Chinese text is unchanged except the missing negation in essay 06 and the
author-approved command/coercion revision in essay 20. Both are recorded in
`source-corrections.json`; the essay-06 negation was independently checked
against the source text.
The original source JSON files and every original page snapshot remain preserved. Potential source-level questions are reported rather
than silently resolved through translation. A fluent idiomatic translation may
recast a sentence, but may not omit its conditions, examples, or argumentative role.

## Rebuild and checks

From the repository root:

    python3 -B scripts/build_fables_full_editions.py --refresh-search
    python3 -B scripts/build_fables_full_editions.py --check
    python3 -B -m unittest discover -s scripts -p test_fables_full_editions.py
    python3 -B scripts/check_web_analytics.py

The scoped search refresh updates only the existing Fables records in the eight
language indexes, leaving unrelated stale entries alone. The general search
builder also understands the resulting pages. There was no pre-existing Fables
renderer in this checkout to amend; this is the complete-edition source of truth.

Browser tests use `scripts/test_fables_full_browser.cjs` against a local HTTP
server. Playwright is available in `/private/tmp/nondubito-reading-paths-qa/node_modules`
on the author's Mac. Set `NODE_PATH` to that directory. The test uses installed
Chrome, blocks all external requests, and covers all essays at 1440, 390 and 320
pixels, every language index, repeated language switching, browser back/forward,
invalid stored language fallback, and real next/previous/index navigation.

No commit, push, or publication is implied by a successful build.

## Final verification record

The completed integration and review scope are recorded in
`../../reports/fables-full-integration-20261108.md`.
`validation-browser.json` records the final 568-view run and 345 computed
hero-subtitle contrast checks. `validation-workflow.json` retains all outputs,
including the three pre-existing site-update failures rather than hiding them.

The subsequently approved essay-20 revision and its preservation audit are in
`../../reports/fables-approved-correction-20-20261108.md`. Its final reruns are
recorded separately in `validation-approved20-browser.json` and
`validation-approved20-workflow.json`, so the original validation history remains intact.
