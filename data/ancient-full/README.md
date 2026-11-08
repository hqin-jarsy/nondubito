# Ancient Stories: complete editions

The Chinese full texts are the source for 19 essays in English, Japanese,
French, German, Spanish and Korean. Existing URLs are retained. The initial
source has 2,448 blocks (19 titles, 2,267 paragraphs and 162 separators),
including the final source notes and the original emphasis.

## Inputs

- `source/NN.zh-Hans.json` and `NN.zh-Hant.json`: complete Chinese blocks.
- `translations/NN.LANG.json`: complete foreign blocks, aligned one-to-one.
  Preserve `{ "tag": ..., "text": ... }`, block order and emphasis.
- `source-snapshots/`: original 120 HTML files, stored as `.txt` so they cannot
  become additional public pages or search results.
- `source-manifest.json`: base commit and immutable source/snapshot hashes.
- `chinese-baseline.json`: complete Simplified/Traditional regions, including
  their original navigation and reading entrances.
- `reviews/`: translation and batch review records. Structural tests do not
  substitute for editorial reading or imply independent native-speaker review.

Chinese source changes require an explicit record of the exact change and its
scope. Do not quietly re-baseline snapshots or source hashes. Two narrowly
recorded corrections are applied to copies of the original inputs:

- Essay 15, block 31: add 被 to 善待拒绝者 (Traditional synchronized), correcting
  the reversed participant role. Exact before/after: `minor-source-correction.json`.
- Essay 04, block 104: the author approved 回头看了 → 违约看了她 (Traditional
  synchronized). The six translations now describe breaking the promise by
  looking at her, not a backward glance. Exact authorization, Chinese changes,
  and six translated sentences: `approved-source-corrections.json`.

The original Chinese inputs and HTML snapshots remain immutable. The renderer
and tests permit only these exact recorded edits, not arbitrary source changes.

## Build and test

```sh
python3 -B scripts/build_ancient_full_editions.py --refresh-search
python3 -B -m unittest discover -s scripts -p test_ancient_full_editions.py
python3 -B scripts/build_ancient_full_editions.py --check
python3 -B scripts/check_web_analytics.py
```

The compact collection renderer calls the full-edition overlay, so an ordinary
rebuild cannot restore abbreviated articles. `last-build.json` records rendered
foreign titles and bodies; the renderer refuses to silently discard a manual
HTML change. Transfer intentional prose changes into the canonical translation
first. The scoped search refresh changes only this series' 160 existing records
in the eight language chunks and preserves every unrelated record.

Run `scripts/test_ancient_full_browser.cjs` against a local HTTP server, using
installed Chrome and Playwright. On the author's Mac, Playwright is already at
`/private/tmp/nondubito-reading-paths-qa/node_modules`; set `NODE_PATH` to that
folder. The test blocks external requests and covers all 19 essays and their
indexes at 1440, 390 and 320 pixels, every paragraph in all eight languages,
repeated language switching, query persistence, real navigation, browser
back/forward, invalid saved-language fallback and language-specific search.

The original compact decks and index descriptions remain useful reading aids;
the article text beneath them is now complete, not an expanded summary.
