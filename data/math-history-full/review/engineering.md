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

# Mathematics full-edition engineering review

Date: 2026-11-09. Editorial status remains **pending**. No full foreign public HTML, discovery records, source manuscripts, or received originals were changed by this engineering task. No commit or push was made.

## Checks completed

- `python3 -B scripts/test_math_history_full_editions.py`: 12 tests, 11 passed and one release-output assertion intentionally skipped. Preview renders are explicitly mocked in memory only. Covers 156 HTML pages / 208 language views, all 125 complete foreign texts, all 9 section headings including sources, inline code/formulas, unchanged three-language bodies, eight-language routes, unique IDs, canonical metadata and analytics, first/last episode and index metadata search, complete receipt coverage, hash drift, unknown manual edits, pending-release rollback prevention, and offline cache behavior.
- Cache test captures existing Mac conversions in temporary memory/files, then forbids CoreFoundation initialization and reproduces all 26 primary pages. A missing cache key fails closed. Once the final cache exists this test itself is portable without CoreFoundation.
- `python3 -B scripts/test_math_history.py --release`: 10 tests passed against the existing three-language release.
- `python3 -B scripts/build_math_history.py --check --complete`: passed against unchanged published three-language pages.
- `python3 -B scripts/build_math_history_full_editions.py --check`: intentionally rejects with `Editorial acceptance is pending`.
- `NODE_PATH=/Users/hanqin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules node scripts/test_math_history_full_browser.cjs http://127.0.0.1:8787`: passed against an explicitly mocked temporary preview outside the repository. 832 page/language/viewport combinations at 320, 375, 768 and 1440 pixels; same-essay eight-language switching; all five foreign languages with JavaScript disabled; all eight with localStorage throwing; no page errors or horizontal overflow.
- `git diff --check` and syntax checks for all new JS and changed `search.js` passed.

## Release sequence after editorial approval

1. Finish actual manuscript/UI review and apply only approved Chinese/English edits in `data/math-history/NN.json`. Do not change frozen `source/epNN.json`, `received`, or the original source manifest.
2. Record any changed original primary input in `review/approved-primary.json`, a repository-relative filename map with exact `before_hash` from manifest.primary_inputs and the approved current `after_hash`.
3. On the Mac, run `python3 -B scripts/build_math_history.py --refresh-hant-cache`. This explicit step writes `data/math-history/traditional-cache.json` only and returns without changing public HTML. Ordinary builds thereafter use this cache and refuse missing keys. It is required by the final receipt, together with all actual primary inputs.
4. After human/editorial acceptance, write `review/accepted.json` with `status: accepted` and a `files` map covering every path from `build_math_history_full_editions.required_inputs()`. Keys are repository-relative, not relative to math-history-full. Values are current SHA-256 hashes. This includes all 125 manuscripts, five UIs, 25 frozen source JSONs, manifest, current primary inputs, Traditional cache and every approved-* file. Engineering mocks do not authorize this step.
5. Run `python3 -B scripts/build_math_history_full_editions.py`, then its `--check`; run the old builder `--check --complete` to verify the final overlay cannot regress the new pages.
6. Run `python3 -B scripts/refresh_math_full_discovery.py`, then `--check`. It requires accepted, up-to-date public math pages before changing five language hubs, the new 2026-11-09 ledger record, Latest, homepage digest, sitemap and scoped search chunks. Other series and old ledger records are preserved. Search remains metadata-only and bounded at 700 characters per q field.
7. Run both Python suites with `--release`, the browser suite against the actual site tree, analytics checks and broader repository checks. After the final cache and acceptance exist, add full-builder `--check`, full-suite `--release`, and discovery `--check` to Ubuntu CI. No math CI command was added prematurely while publication is pending.

Generated primary pages use a series-local, storage-safe site-shell copy. Foreign pages are static with no JavaScript reading dependency. Existing three-language prose and its exact heading/source structures remain intact; duplicate Markdown anchor elements and redundant old-language navigation are presentation-only normalization in the renderer.

## Extended browser review (2026-11-09)

This second pass used a fresh, explicitly mocked temporary preview, including isolated generated math pages, language hub cards and metadata-only search records. The repository's editorial receipt stayed pending. No manuscript, primary prose input, acceptance state, or public HTML was changed.

Command:

`NODE_PATH=/Users/hanqin/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules MATH_SCREENSHOTS=/tmp/math-qa-v2 node scripts/test_math_history_full_browser.cjs http://127.0.0.1:8788`

Result: passed all 832 responsive views, all 64 directed same-essay language transitions, 16 hub/first-or-last/neighbor/contents/browser-Back routes, and 16 actual search-result clicks (EP01 and EP25 in every language). Every view and switch checks the actual document `lang`, `data-lang`, visible title edition, visible prose `lang`, and expected section count. All three browser contexts, including JavaScript-disabled and storage-blocked contexts, block external network requests. The no-JS checks cover both first and last foreign-language essays; storage failures cover all eight languages. No page errors occurred.

Eight screenshots were saved in `/tmp/math-qa-v2` and actually opened for visual review: `math-ep01-{en,de}-{375,1440}.png` and `math-prose-{en,de}-{375,1440}.png`.

Visual inspection found a real issue not detected by the former horizontal-overflow-only check: the foreign header inherited the site's fixed 54px height, so wrapped language links overlapped the breadcrumb at 375px. The series-local `.math-full-header` now sets `height:auto`. The expanded suite explicitly asserts that the main content starts below the language navigation at every viewport, and the entire suite was rerun after this fix. Reviewed replacement screenshots show separated navigation and breadcrumbs, readable headings and body columns, and no clipping or horizontal overflow.

This is engineering validation of a pending-content preview, not editorial acceptance or a final publication check. Repeat the same suite against the accepted build after final manuscript changes.
