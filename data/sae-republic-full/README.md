# SAE’s Republic: complete editions

The thirteen published Chinese essays are the canonical source. Their 707 paragraph bodies are byte-for-byte unchanged. Six complete foreign-language editions replace shortened or argument-changing reconstructions: English, Japanese, French, German, Spanish and Korean. The result contains 78 article translations, 4,242 translated paragraphs and 84 rendered pages including series indexes.

## Editorial record

Each article translation keeps one unit per Chinese paragraph, a source hash, its title, its index description and review notes. Paragraph correspondence detects omissions; it does not establish semantic fidelity. All six editions were compared with the source and reread in batches of five, five and three essays. English also received a complete independent review of all 707 paragraphs and thirteen title/description pairs. The independent cross-language review read all Chinese essays and compared 1,000 explicitly listed high-risk passages across the other five languages, plus all 65 title/description pairs. That targeted review is not represented as a second complete reading of all five editions.

The repair restores omitted steps and examples, removes invented answers to questions the author leaves open, and preserves distinctions between ability and permission, external coercion and the subject’s own necessity, finite number and numbering, and legitimacy and quality. The philosophical essays remain readable prose rather than new academic reconstructions.

The source snapshots retain the former English bodies for comparison. Two source uncertainties are documented without changing the author’s text: an ambiguous pronoun in essay 6 and an uncertain sibling-age description in essay 4. Neither was silently resolved by adding a new factual or interpretive assertion.

## Preservation and generation

`preservation.json` records the Chinese body and traditional-Chinese dictionary hashes. All 858 existing traditional-Chinese dictionary entries remain identical. Ten dictionaries receive only compatibility additions for revised English title keys; their earlier entries remain available. The renderer rejects changed source hashes or missing translation units and retains the existing page shells, canonical URLs, analytics and eight language choices.

Run from the repository root:

```sh
python3 -B scripts/build_classic_full_editions.py sae-republic --check
python3 -B scripts/refresh_classic_full_discovery.py sae-republic --check
python3 -B -m unittest discover -s scripts -p test_republic_full_editions.py
```

Omit `--check` to regenerate. Discovery refresh is scoped to this series and preserves unrelated global search drift. `classic-reading.js` honors explicit URL language before stored preferences and tolerates unavailable storage.

For the optional browser regression, serve the repository locally and run `CLASSIC_SERIES=sae-republic node scripts/test_classic_full_browser.cjs` with Playwright and Chrome available. External requests are blocked during the test.

## Verification

`verification.json` records actual commands and outcomes and seals the delivered translation files. All eleven Republic structural tests, renderer and scoped-discovery checks pass. Browser verification covers 224 mobile/desktop views, 64 directed language switches, sixteen first/last search-result links, sixteen index/neighbor/back routes, URL precedence and reload, blocked storage, and the five foreign editions with JavaScript disabled. English and German mobile views and a Japanese desktop view were also visually reviewed.

Of 52 repository regression commands, 49 pass. Three checks retain the same pre-existing failures caused by four invalid update-ledger language lists. The ledger was not changed. The earlier Nicomachean renderer and tests still pass; its only editorial-record change here replaces an internal attribution phrase with neutral review wording. No remote push is part of this repair.
