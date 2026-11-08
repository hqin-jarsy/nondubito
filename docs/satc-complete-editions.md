# Sex and the City: ten complete readings

The eleven original routes retain Simplified Chinese, Traditional Chinese and independent English editions. German, French, Spanish, Japanese and Korean each have a localized index and ten complete translations: 66 HTML pages, 88 language-specific views including indexes.

## Sources and editorial scope

- `data/satc-full/source/` and `received/` preserve the published baseline at de72136. No matching manuscript was found in `Documents/SAE旗舰系列多语言`. Archive HTML has `.txt` suffixes so it is not treated as public pages.
- `review/approved-chinese.json` records 350 exact block-level revisions within the author-approved thirteen correction directions and ten small continuity fixes. Chinese arguments remain essays, not research reports.
- `review/author-decision.md` records approval. `facts-01-05.md` and `facts-06-10.md` document scene/timeline sources and the limits of transcript-based checking. They do not claim every visual detail was verified frame by frame.
- The five translations each preserve all 1,119 source blocks, including headings, emphasis, examples, qualifications, questions and source notes. English consists of ten substantial independent essays, not the original short summaries.
- Reviews cover 01–05, then 06–10, and cross-essay consistency. Independent readings check the final prose as well as structural validation. Earlier proposal files are retained as provenance, not active alternatives to approved source.

## Reproducible builds

```sh
python3 -B scripts/build_satc_full_editions.py
python3 -B scripts/refresh_satc_full_discovery.py
python3 -B scripts/build_satc_full_editions.py --check
python3 -B scripts/refresh_satc_full_discovery.py --check
python3 -B scripts/build_collection_languages.py --only sex-and-the-city --check
python3 -B -m unittest discover -s scripts -p test_satc_full_editions.py
python3 -B scripts/check_web_analytics.py
```

The renderer rejects pending editorial acceptance, incomplete acceptance receipts, source/hash drift and unknown changes to generated pages. `last-build.json` records outputs. The compact collection builder applies the full renderer last, so it cannot replace full essays with summaries. Traditional Chinese mappings are frozen offline; normal builds use no translation service.

The scoped language controller honors an explicit URL language over saved preferences, preserves it through neighboring and index links, updates the document title, and tolerates blocked browser storage. Search retains the selected reading language. Discovery refresh touches this series and the necessary homepage/Latest records, search chunks and sitemap dates.

## Browser regression

```sh
python3 -m http.server 8798 --bind 127.0.0.1
NODE_PATH=/path/to/existing/node_modules node scripts/test_satc_full_browser.cjs http://127.0.0.1:8798
```

Covers all 88 reading views at 375, 768 and 1440px, eight-language switching, first/last article search results, neighboring/index navigation, language hubs, denied storage and foreign editions without JavaScript. External requests are blocked. Screenshots are saved in the system temporary directory for visual inspection.

Local commit only. No push.

## Verification on 2026-11-08

- Fourteen focused unit tests passed, including four fail-closed guard tests and final-essay source-note completeness. Full renderer, compact renderer (82 outputs) and scoped discovery checks passed.
- Browser regression passed 264 views and 40 navigation/actions at 375, 768 and 1440px with no page errors. Desktop English and mobile Korean screenshots were visually inspected. A copied obsolete route selector in the first browser-test run was corrected before the complete passing rerun.
- Analytics: 13,692 public pages checked, zero errors, zero repairs and zero conflict copies.
- All 39 integrity workflow verification commands were run locally: 36 passed and three failed. The failures are check_site_updates.py, test_home_updates.py and test_method_introduction.py, all caused by the same four pre-existing ledger entries missing language lists. Checking the unchanged ledger at baseline de72136 reproduces these errors; every previous ledger entry is unchanged. This is not a fully green aggregate CI result.
- The final independent integration review found no release-blocking defect. Full command outputs, baseline comparison and scope are recorded in data/satc-full/review/verification.json.
