# SAE’s Nicomachean Ethics: complete editions

The thirteen published Chinese essays are the canonical source. Their 778 paragraph bodies are byte-for-byte unchanged. Six complete foreign-language editions replace abbreviated or argument-changing reconstructions: English, Japanese, French, German, Spanish and Korean.

## Editorial record

Each translation JSON keeps one unit for each source paragraph, its source hash, a title, an index description and article-specific review notes. This correspondence detects omissions; it does not prove semantic fidelity. All six editions were compared with the Chinese text and reread in batches of five, five and three essays. The English edition also received a complete independent 778-paragraph review. A second cross-language argument review checked the exact passages listed in `reviews/independent-argument-review.json`; it is not represented as a second complete review of all 65 articles.

Review corrections include ability rather than permission to stop, intention rather than a new normative claim, exhaustive inquiry rather than bodily exhaustion, and preserving the number of questions where the argument explicitly counts them. English and Japanese argument drift and omissions in the former short reconstructions were repaired. The prose remains an essay translation, with no invented argument or added academic apparatus.

One inherited Chinese punctuation discrepancy remains recorded: essay 9 says “only a comma” but its following paraphrase uses a semicolon. This does not change the argument and was not silently assigned a new authorial meaning.

## Preservation and generation

`preservation.json` records the original Chinese body and traditional-Chinese dictionary hashes. Existing traditional translations are preserved; only the updated edition notice and the revised essay 12 English title mapping were added. The renderer reads Chinese from the canonical HTML and refuses changed sources or missing translation units. It writes only foreign bodies and the necessary titles, descriptions, edition labels and reading controls in the existing shells.

Run from the repository root:

```sh
python3 -B scripts/build_classic_full_editions.py sae-nicomachean --check
python3 -B scripts/refresh_classic_full_discovery.py sae-nicomachean --check
python3 -B -m unittest discover -s scripts -p test_classic_full_editions.py
```

Omit `--check` to regenerate. Search refresh is deliberately scoped to this series; unrelated global search drift is not overwritten. Navigation, canonical URLs, analytics and all eight language choices remain checked. `classic-reading.js` makes an explicit URL language take priority over saved preferences and tolerates unavailable storage.

For the optional browser regression, serve the repository locally and run `scripts/test_classic_full_browser.cjs` with a Playwright installation and Chrome available. The test blocks external requests. It checks 224 desktop/mobile language views, 64 directed language switches, sixteen first/last search-result links, index/neighbor/back routes, explicit URL language and reload, direct reading with blocked storage, and the five foreign editions without page JavaScript.

## Verification

`verification.json` records the actual commands and outcomes and seals the delivered translation files. The eleven new structural tests, renderer/discovery checks, browser checks and 46 of 49 repository regression commands passed. Three existing checks fail on the same pre-existing four invalid update-ledger language lists. The update ledger and unrelated series were left untouched. No remote push is part of this repair.
