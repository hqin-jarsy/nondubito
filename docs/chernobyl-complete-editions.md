# Chernobyl: six complete readings

The seven original routes retain Simplified Chinese, Traditional Chinese and the independent English editions. German, French, Spanish, Japanese and Korean each have a localized index and six complete translations: 42 HTML pages and 56 language-specific reading views including indexes.

## Sources and review

- `data/chernobyl-full/source/` and `received/` preserve the published source at baseline ae1b687. Received HTML uses `.txt` so archives are not indexed as public pages.
- `review/approved-chinese.json` records exact author-approved corrections by article and block. `approved-english.json` records revisions and completeness restorations in the independent English readings.
- `de`, `fr`, `es`, `ja`, `ko` contain complete paragraph-aligned translations: 672 source blocks per language, including all headings, emphases, examples, qualifications, questions and transitions.
- Reviews cover 01–05 as a batch, then 06 and whole-series consistency, with independent comparisons. The author explicitly asked that factual precision remain integrated into readable essays, not turn them into academic papers.
- `review/fact-check-sources.md` documents focused scene and historical checks and their limits. Original manuscripts outside the repository were not changed.

## Build and checks

```sh
python3 -B scripts/build_chernobyl_full_editions.py
python3 -B scripts/refresh_chernobyl_full_discovery.py
python3 -B scripts/build_chernobyl_full_editions.py --check
python3 -B scripts/refresh_chernobyl_full_discovery.py --check
python3 -B scripts/build_collection_languages.py --only chernobyl --check
python3 -B -m unittest discover -s scripts -p test_chernobyl_full_editions.py
python3 -B scripts/check_web_analytics.py
```

The full renderer rejects changed source snapshots, incomplete or stale editorial acceptance hashes, and unexpected manual changes to generated pages. `last-build.json` records output hashes so an intentional reviewed source revision can advance the generated pages without overwriting unknown work. The compact builder applies this renderer last and cannot replace full essays with summaries.

Traditional Chinese mappings are frozen offline; normal builds require no translation service. Scoped language routing gives explicit URL language precedence, preserves language on neighboring links, and tolerates blocked browser storage. Search results preserve the selected reading language. Discovery refresh touches only this series and the necessary homepage/Latest records and sitemap dates.

## Browser regression

Serve the repository on localhost, then use an existing Playwright installation:

```sh
python3 -m http.server 8798 --bind 127.0.0.1
NODE_PATH=/path/to/existing/node_modules node scripts/test_chernobyl_full_browser.cjs http://127.0.0.1:8798
```

Covers all 56 reading views at widths 375, 768 and 1440; eight-language switching; first/last essay search results; neighboring and index navigation; language hubs; denied storage; and foreign editions without JavaScript. External network requests are blocked. Screenshots are written to the system temporary directory.

Local commit only. No push.

## Final verification and existing limitation

The local workflow run executed 36 check commands: 33 passed. The three failures (`check_site_updates.py`, `test_home_updates.py`, `test_method_introduction.py`) all report the same four pre-existing update records without language lists. The baseline HEAD reproduces these errors, and every pre-existing ledger record is unchanged. This is not a clean aggregate CI pass. The Chernobyl-specific nine tests, full-render and discovery checks, compact-builder protection, analytics check, and browser regression all passed. Detailed output is saved in `data/chernobyl-full/review/verification.json`. No unrelated ledger entries were repaired in this series commit.
