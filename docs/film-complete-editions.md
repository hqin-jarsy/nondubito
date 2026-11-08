# Three complete film readings

Films 50, 56 and 59: Raise the Red Lantern, Dead Poets Society and Parasite.

The three original routes contain the Chinese, Traditional Chinese and complete English readings. Five separate language directories provide German, French, Spanish, Japanese and Korean. Each collection has three essays and a series index: 72 published pages in total, including 60 new foreign-language pages.

## Checked-in sources

- `data/film-full/received/<film>/`: immutable received local manuscripts, original notes and checksum files.
- `data/film-full/reviewed/<film>/`: reviewed publication sources. `en` holds complete English readings and `zh` holds the Chinese text with the author's approved corrections. The five foreign-language directories retain the complete supplied readings, with the documented Japanese episode 2 wording repair in Dead Poets Society.
- `data/film-full/batch04-received.json`: a targeted batch for films 50, 56 and 59, not sequential films 16–20. It records source provenance and the original-page baseline.
- `data/film-full/review/*-approved-changes.json`: the exact 16 Chinese/English correction pairs approved by the author.
- `data/film-full/review/approved-traditional.json`: frozen dictionary deltas for the corresponding Traditional Chinese text nodes. Normal builds require no platform translation service.
- `data/film-full/review/release-summary.md`: review coverage and verification limits.

The source is the existing local directory selected by the author. The optional delivered ZIP is not a build dependency. Neither original source files outside the repository nor received manuscript copies are edited during normal builds.

## Build and verify

```sh
python3 -B scripts/build_film_full_editions.py
python3 -B scripts/refresh_film_full_discovery.py
python3 -B scripts/build_film_full_editions.py --check
python3 -B scripts/refresh_film_full_discovery.py --check
python3 -B -m unittest discover -s scripts -p test_film_full_editions.py
python3 -B -m unittest discover -s scripts -p test_film_targeted_english.py
python3 -B scripts/check_web_analytics.py
```

For primary-language-only maintenance, `build_film_primary_editions.py --check` verifies the primary pages and approved dictionaries without opening foreign sources.

For browser QA, serve the repository on localhost and use the existing Playwright installation:

```sh
python3 -m http.server 8796 --bind 127.0.0.1
NODE_PATH=/path/to/existing/node_modules node scripts/test_film_targeted_browser.cjs http://127.0.0.1:8796
NODE_PATH=/path/to/existing/node_modules node scripts/test_film_primary_browser.cjs http://127.0.0.1:8796
NODE_PATH=/path/to/existing/node_modules node scripts/test_film_full_browser.cjs http://127.0.0.1:8796
```

The ordinary renderer is deliberately scoped: other film bodies remain untouched. Discovery refresh replaces only the affected records, preserves unrelated sitemap dates, and keeps search results in the selected reading language. The legacy 50–59 importer reapplies the reviewed full-edition renderer at its end, so it cannot silently restore the superseded English summaries.

Local commits only. Do not push without the owner's instruction.
