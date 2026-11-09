# Final local release verification — 2026-11-09

The accepted mathematics release has now been generated locally: 156 HTML pages / 208 language views. This supersedes the pending-status notes below, which are retained as historical engineering records. No commit, push or external deployment was performed.

- All five mathematics release checks passed; full suite 18/18 and legacy suite 10/10. Library typography 8/8 passed.
- All 44 workflow commands were actually rerun after compatibility fixes: 41 passed, 3 inherited ledger failures, 0 skips and 0 new unresolved failures. The three failures match the isolated 18af703 baseline by the four affected record IDs, not shifted list indexes.
- Earlier film, Wire, Chernobyl and SATC discovery checks initially exposed a real compatibility bug: they lowered shared sitemap dates to 11-08. Each old script has one monotonic-date assignment fix; math discovery uses the same protection. Two new tests cover retaining newer dates and upgrading older dates. Only check mode was rerun for the other series; no other series was regenerated.
- Both real browser suites passed: 225 legacy article views plus 9 indexes; 832 full views, 64 directed switches, 16 hub/navigation routes, 16 real search-result clicks, no-JS and storage-failure cases. All browser contexts blocked external requests. Ten final screenshots were actually inspected, including English/German at 375/1440, Japanese mobile prose and Traditional Chinese mobile contents.
- All 239 pre-existing ledger records and their order remain identical. 19,948 unrelated search records remain identical. Sitemap changes comprise 130 new math URLs plus 34 authorized math/shared-page dates; other entries are unchanged.
- Analytics repair changed zero pages; 13,822 public pages checked with zero tracking errors/conflict copies. Acceptance remains valid for all 253 hashed input files.

Full per-command output, initial failures, final rerun, baseline details and screenshot inventory: `verification.json` in this directory. The actual CI workflow now includes the five mathematics checks. Remote Ubuntu CI has not run; local offline-cache tests explicitly prohibit CoreFoundation initialization.

---

# Final mathematics integration plan

Status: engineering readiness review only, 2026-11-09. Editorial acceptance is still pending. Final prose and synchronized editions are not yet accepted. No final browser run or release pass is claimed here.

## CI proposal, not applied

`review/ci-final-proposal.patch` adds five checks to `.github/workflows/site-integrity.yml`, immediately after SATC and after the existing `Markdown==3.9` installation:

1. `python -B scripts/build_math_history_full_editions.py --check`
2. `python -B scripts/test_math_history_full_editions.py --release`
3. `python -B scripts/build_math_history.py --check --complete`
4. `python -B scripts/test_math_history.py --release`
5. `python -B scripts/refresh_math_full_discovery.py --check`

`git apply --check data/math-history-full/review/ci-final-proposal.patch` passed. The actual workflow is unchanged. Apply the proposal only after final inputs, the offline Traditional cache, acceptance and generated outputs are ready. Existing workflow: 39 validation commands. Proposed workflow: 44. Neither the added release commands nor the 44-command workflow has passed against final accepted mathematics content yet.

The browser script remains a required local release check, rather than silently adding uninstalled Chrome/Playwright dependencies to existing Ubuntu CI. Its last real mock-preview run passed 832 responsive views, 64 directed switches, 16 complete hub/navigation routes and 16 actual search-result clicks. Rerun against final accepted outputs after manuscript synchronization. Do not reuse that mock result as final-content approval.

## Confirmed pending-source publication bug, now fixed

Previously the old builder could still emit changed primary prose while the full-edition receipt was pending, because unchanged published pages had valid baseline hashes. The pending overlay now permits only byte-identical already-published primary output. A changed source causes an explicit refusal before any page write. The full renderer also requires exactly 26 primary pages and exactly 156 total HTML outputs (208 language views).

The regression suite now contains 15 tests: 14 passed, and the real released-output assertion is intentionally skipped in non-release preview mode. New coverage exercises the actual old-builder `outputs()` path with a changed source item and temporary published page fixtures, and verifies all 26 fixture files remain unchanged. It also checks the unchanged pending path, edited pending outputs, and incomplete primary inventory.

Read-only checks against the current working tree confirm:

- Old builder `--check --complete` refuses current unaccepted primary changes, first reported at ep04.
- Full builder `--check` refuses pending acceptance.
- Discovery `--check` refuses pending acceptance.
- All 26 published primary HTML files still match frozen snapshot hashes; there are zero foreign public HTML pages.
- Editorial receipt remains pending. No receipt, prose, public HTML, actual workflow, discovery output, or Git commit was changed by this review.

`outputs(full=False)` is an internal rendering hook for memory-only/explicit temporary previews. No command-line publishing path selects it. Do not write its output to public paths while pending.

## Reproduced baseline failures

An isolated `git archive` of commit `18af703` was extracted to `/tmp/nondubito-baseline-18af703.9Pf3Vp`. The following baseline commands were actually rerun and each exited 1:

- `python3 -B scripts/check_site_updates.py`: four `invalid language list` errors, baseline updates[8]–[11].
- `python3 -B -m unittest discover -s scripts -p test_home_updates.py`: 8 tests, one failure in `test_latest_keeps_the_whole_ledger`, caused by those same four ledger errors.
- `python3 -B -m unittest discover -s scripts -p test_method_introduction.py`: 10 tests, one failure in `test_update_and_library_entries`, caused by those same four ledger errors.

The four pre-existing IDs are:

- 2026-11-04-fairy-tales-eight-languages
- 2026-11-04-laughter-eight-languages
- 2026-11-04-cooperation-histories-eight-languages
- 2026-11-04-aesthetics-core-eight-languages

Reproduction in a fresh temporary directory:

```
baseline=$(mktemp -d /tmp/nondubito-baseline-18af703.XXXXXX)
git archive 18af703 | tar -x -C "$baseline"
cd "$baseline"
python3 -B scripts/check_site_updates.py
python3 -B -m unittest discover -s scripts -p test_home_updates.py
python3 -B -m unittest discover -s scripts -p test_method_introduction.py
```

This pass reproduced the three known failing commands, not all 39 baseline commands. Preserve the old ledger records; do not silently correct them in the mathematics commit. When comparing final failures, identify records by ID, because adding the mathematics entry shifts their numeric positions.

## Final release sequence

1. Finish approved Chinese and English prose revisions, synchronize all five new languages, and complete editorial review.
2. Record approved changed original primary inputs in `review/approved-primary.json` with baseline `before_hash` and final `after_hash`. Never refresh the frozen manifest or received sources to hide changes.
3. Explicitly run `python3 -B scripts/build_math_history.py --refresh-hant-cache` on macOS. This writes only the conversion cache, including the two synthetic regression inputs, and returns before page generation.
4. Verify offline generation with CoreFoundation initialization forbidden. Missing cache keys must continue to fail closed. The final receipt must hash the cache along with all actual primary inputs, 125 foreign manuscripts, five UI files, 25 frozen source snapshots, manifest and all approved-* records.
5. Write a real accepted receipt only after review. Run full builder, then full `--check`; run the old builder `--check --complete` to prove its final overlay is stable.
6. Run scoped discovery, then discovery `--check`. Discovery verifies all accepted public mathematics pages match before linking them from hubs, ledger, Latest, homepage, sitemap or search. Preserve other series and metadata-only search scope.
7. Apply the CI proposal, run all five mathematics checks, analytics checks, the real browser script and all workflow validation commands. Report inherited ledger failures separately and disclose any new failures.
8. Commit only after final editorial review is complete. Never push.
