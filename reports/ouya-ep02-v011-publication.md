# Eurasian Emperors EP02 — full eight-language publication

2026-09-27. Baseline: `48677ad`, clean before this task. Local publication preparation; the user pushes.

## Source and editorial scope

Received `NonDubito_Ouya_EP02_8languages_v0.1.1_2026-09-27.zip`. The package and manuscript hashes are recorded in `data/ouya-full/ep02-review.json`. Eight complete manuscripts are retained, with nine reversible local replacements:

- Section 4, paragraph 4: in all eight languages, replace the surviving assertion that every satrap immediately became independent when Alexander died. Follow the preceding paragraph's account of succession settlements, wars and the loss of a common centre. This closes the seam without rewriting the section.
- German section 5, paragraph 4: clarify that small transactions need not always be **recorded in writing**, rather than suggesting they required no contractual agreement.

All other received manuscript text is unchanged. Reversing these nine replacements exactly reproduces each received v0.1.1 manuscript hash. The original delivery package was not modified.

Each language renders 131 prose paragraphs and nine numbered sections, with an unnumbered introduction: 1,048 prose paragraphs in total. The public reading notes and source links are additional. The notes distinguish the essay's interpretive vocabulary from ancient testimony and distinguish cultural mixing from political equality.

This is a targeted closure of the previous editorial review, not exhaustive historical clearance or native-speaker certification.

## Pages and navigation

- Existing bilingual `essays/ouya/ep02.html` retains both complete Chinese and English editions.
- Existing Japanese, French, German, Spanish and Korean URLs receive the complete manuscripts.
- New `essays/ouya/zh-hant/ep02.html` provides the complete Traditional Chinese edition.
- All seven URLs use the shared eight-option language dropdown. Bilingual return links explicitly select `?lang=en` or `?lang=zh`.
- Traditional EP01 now links directly to Traditional EP02; EP02 links back to EP01. The next chapter still points to the existing bilingual EP03 with an explicit Simplified Chinese label. No nonexistent Traditional EP03 or directory is invented.
- No other episode's prose or series-directory content was changed.
- Search indexes contain 10,122 source records; sitemap contains 9,970 canonical URLs. Sitemap changes concern only EP02.

## Verification

- EP01 regression suite: six tests passed.
- EP02 suite: five tests passed (complete rendering, reversible receipts, scope/idempotence, local links/canonicals/IDs/attributes, Traditional neighbors).
- Actual inline language scripts and shared dropdown controller: 54 minimal-DOM unit scenarios passed across EP01 and EP02, including query/stored language handling and denied storage on initial load.
- Both edition renderers pass `--check`.
- Search-index and sitemap `--check` passed; structured comparison of all eight search chunks confirms that only EP02 records changed. `git diff --check` passed.
- No new browser visual/responsive inspection was performed. Prior local-preview access was blocked by browser URL policy; this task does not claim a workaround or a visual pass. Tests cover generated HTML, navigation and controller behavior, not browser layout.

## Rebuild

Run `python3 -B scripts/build_ouya_ep02.py`. EP01's separate renderer owns its Traditional next-chapter link. Both renderers validate source receipts before rendering. Then rebuild search indexes and sitemap with the existing project scripts.
