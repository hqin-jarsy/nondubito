# Eight-language reader maintenance — 2026-11-15

Scope: publication notices, directory typography, metadata and navigation. Translation prose was not regenerated.

- Removed five obsolete Japanese incomplete-translation badges; normalized the affected Japanese chapter numbers and Korean directory separators.
- Corrected Spanish chapter 79 `Jia Yingchun` capitalization in directory/title, and traditional edition `復刻`.
- Corrected exactly five opening single quotation marks in each Chinese chapter 1 (simplified and traditional). All other novel article content is unchanged.
- Updated current availability to continuation chapters 81–86; removed reader-facing HTML maintenance instructions. Historical references to the 81–85 naming baseline remain historical references.
- Made the Chinese directory brand links point home and verified chapter 80↔81 navigation in all eight languages.
- Added reciprocal eight-language plus x-default metadata to all 656 reader HTML pages. Restored 13 missing canonical tags (11 French, two Spanish). Directory canonicals use trailing-slash URLs.
- Added exactly 328 missing French, German, Spanish and Korean sitemap entries; existing entries and dates are unchanged.
- Kept affected generator chrome in sync without running prose regeneration or rebuilding unrelated site data.

## Validation

- `test_hongloumeng_reader_links.py`: 4 tests passed, covering all 656 pages, canonical/sitemap/local targets, round-trip navigation, notices and directory formatting.
- `test_hongloumeng_ch086.py`: 5 tests passed.
- `test_hongloumeng_discovery_scope.py`: 13 tests passed.
- `test_hongloumeng_japanese_navigation_binding.py`: 10 passed; one pre-existing reversible-navigation test fails on the Japanese continuation index/chapter 81. Both also fail against the pre-change HEAD (3e5b440). Current English publication validation passes.
- `test_hongloumeng_french_navigation.py`: 3 passed; one pre-existing test expects a directory URL written explicitly as `index.html` in the unchanged French continuation index instead of its existing equivalent directory link.
- All modified Python modules parse; `git diff --check` passes. Independent review confirmed sitemap-only additions, reciprocal metadata and unchanged article content except the authorized quotation marks.
- Link validation used the actual local HTML and filesystem; no visual browser review or live-deployment check was performed. Push remains the owner's action.
