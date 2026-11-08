# The Wire: nine complete readings

The existing ten primary routes retain Simplified Chinese, Traditional Chinese, and the independent English editions. German, French, Spanish, Japanese, and Korean each have an index and nine complete translations: 60 HTML pages, presenting 80 language-specific reading views including the indexes.

## Editorial sources

- `data/wire-full/source/`: immutable Chinese block snapshots and the received English body, taken from the published site at commit `c954eda06921fafc9cb18fd9d6839f4ed05912a6`.
- `data/wire-full/received/`: the 60 original HTML templates, stored with a `.txt` suffix so search and analytics do not mistake archives for public pages, plus ten original Traditional Chinese dictionaries.
- `data/wire-full/en/`: all nine independent English readings, reviewed and supplemented rather than replaced with literal translations.
- `data/wire-full/{de,fr,es,ja,ko}/`: complete paragraph-aligned translations. Each language retains all 1,226 source blocks, section headings, examples, qualifications, emphasis, reader questions, and chapter transitions.
- `data/wire-full/review/`: two review batches per language (01–05, then 06–09), independent full-series reviews, exact Chinese and English correction records, frozen Traditional Chinese mappings, and the editorial acceptance hashes.

The later local “v2” manuscripts were inspected but not imported: they substantially rewrite the published essays. Original files outside this repository are unchanged. Chinese changes are limited to the approved factual correction records and the documented minor proper-name correction. The interpretive argument and the author's explicitly uncertain recollection in essay 04 are preserved. The factual review is targeted, not a claim of exhaustive shot-by-shot verification.

## Build and verify

```sh
python3 -B scripts/build_wire_full_editions.py
python3 -B scripts/refresh_wire_full_discovery.py
python3 -B scripts/build_wire_full_editions.py --check
python3 -B scripts/refresh_wire_full_discovery.py --check
python3 -B scripts/build_collection_languages.py --only the-wire --check
python3 -B -m unittest discover -s scripts -p test_wire_full_editions.py
python3 -B scripts/check_web_analytics.py
```

The renderer rejects unreviewed source changes and unexpected edits to generated pages or dictionaries. After editorial changes have been reviewed, update the corresponding hashes in `review/accepted.json`, then rebuild. `last-build.json` records the previous generated outputs, so a deliberate source revision can advance them without discarding manual changes. The legacy compact-language builder reapplies this full renderer and cannot restore the old summaries. Traditional Chinese changes are frozen offline; normal builds need no translation service.

Discovery refresh updates only this series, the homepage digest, Latest, their search records, and the corresponding sitemap dates. It leaves unrelated search records and publication dates unchanged. The language controller is scoped to The Wire; query language wins over saved preferences, neighboring links retain the reading language, and blocked browser storage does not break navigation. The shared search change is restricted to the original Wire routes.

## Browser regression

Serve the repository on localhost and use an existing Playwright installation:

```sh
python3 -m http.server 8797 --bind 127.0.0.1
NODE_PATH=/path/to/existing/node_modules node scripts/test_wire_full_browser.cjs http://127.0.0.1:8797
```

The browser test covers all 80 reading views at widths 375, 768, and 1440; eight-language switching; first and last article search results in every language; index and neighbor links; foreign-language hubs; denied storage; and foreign editions without JavaScript. External network requests are blocked. It writes desktop and mobile screenshots to the system temporary directory.

Local commit only. Do not push without the owner's instruction.
