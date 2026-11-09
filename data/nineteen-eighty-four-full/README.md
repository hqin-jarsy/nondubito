# Nineteen Eighty-Four: complete translation repair

## Status: complete

The four essays now have complete English, Japanese, French, German, Spanish and Korean translations. The author approved the Chinese factual corrections, which are synchronized across Simplified Chinese, Traditional Chinese and all six translations. This work is intended for one local project commit; no push or public deployment is part of this repair.

## Coverage and editorial review

The four Chinese essays retain all 390 paragraphs and 32 section headings: 422 source units and 2,532 translated units across 24 article translations. Six translated indexes preserve the series introduction, article titles and descriptions. The former editions abbreviated, reordered or added arguments. These complete versions restore the narrative, examples, qualifications, open questions and essay-to-essay links.

Each language was compared with the complete Chinese essays and reread as one four-essay batch. The original English review compared all 422 units; the original cross-language review compared 650 distinct units in the other five languages. Those reports remain historical evidence, not claims that every unchanged unit was independently reread after the approved amendments.

The final independent amendment review compared all 31 revised units in each of six languages: 186 changed-unit comparisons, with 71 units per language including neighboring prose, all 24 title/description pairs and six index introductions. No unresolved translation issue remained. Its final file hashes are checked by the test suite.

## Approved source corrections

The 31 revised units address the consciously destroyed photograph, Julia's intended dress and actual makeup, the lovers' attempted political participation, deliberate suppression of sexual pleasure, Julia's distinct statements about hope, surveillance and literacy among the proles, the documented appendix-deletion request, and the related cross-reference, book-delivery, final-words and pain-apparatus copy corrections.

`reviews/approved-source-changes.json` records every old and new unit. Reversing those exact changes reproduces all four original Chinese body hashes. No unrecorded Chinese change, unit removal, heading change or emphasis change is allowed. The author's philosophical judgments remain intact, including the qualified reading of the appendix and the argument that past experience cannot be made not to have happened.

`preservation.json` retains the original evidence alongside the approved amendment. All 554 original Traditional-Chinese dictionary entries remain unchanged. The five browser-title mappings and new exact text-node mappings make the revised source accessible in Traditional Chinese. The unchanged Chinese index remains sealed.

## Page and discovery integrity

The renderer edits the existing shells and does not generate prose. Foreign culture-page shells retain their neighboring-essay navigation. Complete-translation labels replace the old independent-rewriting labels. Canonical URLs, analytics, all eight reading choices, first/last routes and local assets are tested.

The local browser review also verified the scoped layout repair that clears the fixed header from foreign-language menus. No global stylesheet or unrelated series was changed. Search changes are limited to five records per language for this series, and sitemap changes to its thirty page dates.

## Reproduction

```sh
python3 -B scripts/build_1984_full_editions.py --check
python3 -B scripts/refresh_1984_full_discovery.py --check
python3 -B -m unittest discover -s scripts -p test_1984_full_editions.py
```

Omit `--check` to regenerate. For local browser QA, serve the repository on localhost and run `node scripts/test_1984_full_browser.cjs` with Playwright and Chrome available. It uses a temporary clean profile and blocks external requests.

## Final verification

All fifteen structural/source/review tests pass. Thirty rendered pages and scoped discovery are current. The final browser run passed eighty mobile/desktop views, 64 directed language transitions, sixteen search-result clicks and sixteen index/neighbor/back routes, explicit URL-language precedence and reload, blocked storage, and the five foreign editions without JavaScript. English and Chinese mobile views and a Japanese desktop view were visually reviewed.

Of 55 regression commands, 52 pass. The same three pre-existing checks still report four invalid language lists in the update ledger. The ledger was not modified; these failures are disclosed rather than represented as a clean full-site pass. `verification.json` contains the exact commands, results, review scope and final translation hashes.
