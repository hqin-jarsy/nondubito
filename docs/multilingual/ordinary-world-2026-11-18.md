# Ordinary World: multilingual delivery

Status: all six complete language editions independently reviewed; final integration and reproducibility checks passed. Local commit only; no push.

## Scope

Five complete essays, restoring the compressed English editions and adding Japanese, French, German, Spanish and Korean. The corrected Chinese source contains 93 / 123 / 111 / 115 / 129 blocks (571 total). Counts trace coverage; they do not certify literary quality.

## Editorial boundary

The former English essays were short adaptations; their opening geographical zoom was not a translation of the Chinese steamed-bun scene. The restored editions follow the Chinese scenes and argument. Interpretations remain the essay author's readings. Medical causation, motives and counterfactual routes are not silently promoted into verified plot facts.

The original Chinese source is retained in `data/ordinary-world/multilingual/source-original.json`. Confirmed changes and their directly dependent argument repairs are recorded in `data/ordinary-world/source-corrections.json`. Primary Chinese and Traditional Chinese are synchronized. In particular, Xiaoxia's practical recruitment help and Jin Xiu's willingness to work at the mine cannot support the former claims that Xiaoxia never intervened or that Jin Xiu offered a city-promotion package. The repaired argument distinguishes receiving help from surrendering one's decisions, and distinguishes the love proposal from the separate city-transfer proposal.

See `data/ordinary-world/multilingual/independent-source-review.md` for precise original-novel chapters, primary-text links and verification limits. These are online text witnesses, not a claim to have compared a physical printed edition.

## Review records

Authoring and independent AI reviews are recorded alongside the six durable language JSON files. This is not external native-speaker or scholarly certification. Final review hashes and structural/browser results will be checked before the series commit.

## Integration checks completed

- Scoped publication validation: 36 primary/new pages, 30 new standalone language pages, 594 local targets, eight alternate editions per page, canonical uniqueness and analytics.
- Corrected Chinese body matches the durable source; all changed Traditional Chinese nodes are mapped; no unrecorded Chinese source edits.
- Mobile (390 px) and desktop (1440 px) isolated offline browser pass: 96 page/language checks, zero failures. The first Japanese mobile viewport was also visually inspected: title, eight-language control and prose fit without clipping. External fonts/network were blocked; this is a fallback-font layout check, not an online deployment test.
- Repository regression tests: 4 reader-series, 5 reader-supplement, 8 Home-update and 2 sitemap-date tests, all passing (19 total).
- Scoped discovery reproducibility passes. Compared against the preceding HEAD: unrelated search records are byte-equivalent as parsed records, no old sitemap URL removed, and no out-of-scope sitemap date changed. Canonical directory URLs were used to identify homepage/channel scope.

All six final translation hashes and the final corrected-source hash match their independent review records. A repeated build was byte-identical, and the final 96 mobile/desktop checks again reported zero failures. The series is committed independently; see the repository history for the exact commit.

## Final review coverage

EN and DE: independent full review by moon. FR and ES: independent full review by cities. JA: independent full review by catch22. KO: independent full review by cities. Each scope covers all five essays, not a sample. EN/JA/FR/DE/ES have 571 body blocks; KO has 566 body blocks and five corresponding source notes, with no prose omitted. Self-review receipts retain historical draft counts and point to subsequent final independent reviews.
