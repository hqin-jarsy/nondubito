# The Analects, Reopened: complete reading editions

This release replaces fifty abbreviated English essays and 250 compact foreign-language web essays with complete manuscripts at the existing URLs. It does not publish new URLs or push to the remote repository.

## Inputs and reproducible build

- `chinese/`: the fifty original Chinese Markdown manuscripts, preserved unchanged.
- `received/`: the complete `NonDubito_Analects_01-50_DE-FR-ES-JA-KO_v0.2` revision package, including all 250 original translated manuscripts, editorial notes, coverage files and supplied checksums. Never overwrite these provenance files.
- `english/`: fifty new complete English translations. This is the editable English source.
- `source-corrections.json`: seventeen exact, limited Chinese name, character-count, speaker-attribution and chronology corrections. Both Chinese web editions apply these recorded corrections; the raw originals remain available.
- `review/five-language-corrections.json`: nine exact corrections layered over the received manuscripts. No entire foreign-language essay was retranslated.
- `snapshots/`: the original 306 public HTML pages, stored as `.txt` so discovery tools do not index build inputs.
- `manifest.json`: hashes for original manuscripts, package files and snapshots.
- `last-build.json`: overwrite-protection receipts. Unrecognized manual page changes stop a rebuild instead of being discarded.

Run from the repository root:

```
python3 -B scripts/build_analects_full_editions.py
python3 -B scripts/refresh_analects_full_discovery.py
python3 -B scripts/build_sitemap.py
python3 -B scripts/build_analects_full_editions.py --check
python3 -B -m unittest discover -s scripts -p test_analects_full_editions.py
```

Both older Analects build commands now delegate to the complete-edition renderer and update the same receipts. Missing complete-edition inputs fail closed. A future rebuild needs only repository files, not the original Mac Documents folders or a macOS Traditional Chinese converter.

Browser checks use an existing local Playwright installation, Chrome, and a local static server:

```
NODE_PATH=/path/to/existing/node_modules node scripts/test_analects_full_browser.cjs http://127.0.0.1:8795
```

## Editorial coverage and limits

All fifty English translations received a full source comparison and a five-essay-batch review. A separate review fully compared 21 Chinese–English pairs, including one from every five-essay batch and additional high-risk passages.

The received five-language package was not retranslated. The new review read all fifty editorial notes, 54 complete target-language essays, and cross-language risk passages including essays 20, 35, 37 and 50. This is not a claim of a new line-by-line review of all 250 essays, nor a native-speaker expert final edit.

Eight source-level interpretation or evidence questions remain for the author in `review/source-issues.json`. Translation is not permission to rewrite an author's theoretical position. The surviving questions are recorded, not silently resolved or passed off as independently established philology. Classical quotations are translations of the supplied Chinese, not credited to a modern translator. This release does not claim a fresh external investigation of every historical statement, DOI destination or textual variant.

See `review/` for specific language checks, reproducibility, browser results, regression results and scoped-change evidence. File counts and hashes establish completeness and provenance, not literary quality.

## Author decisions, 2026-11-08

The author retained essay39 unchanged, approved narrowing essay44 to accounts about the teacher while retaining Zengzi’s own judgments, and approved presenting essay19’s ruler-addressee as a reading without adding scholarly disclaimers. The approved changes are recorded in `review/author-decisions-20261108.json`, applied to all eight reading languages, and tested explicitly. The original seventeen minor source corrections are unchanged; three short approved editorial replacements are added separately.
