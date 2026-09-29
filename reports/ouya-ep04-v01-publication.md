# Eurasian Emperors EP04 — complete eight-language editions

2026-09-29. Baseline: `45f6a61`, clean at the start. Local publication preparation; the user pushes.

## Source and copyediting

Source: `NonDubito_Ouya_EP04_8languages_v0.1_2026-09-29.zip`. Its hash, the eight received manuscript hashes, published hashes, and five reversible copyedits are recorded in `data/ouya-full/ep04-review.json`. The received archive remains untouched.

- Korean 7.5: clarify that Labeo nominated Lepidus during the Senate roll revision, not that Labeo conducted the reorganization.
- English and German 0.4: political legitimacy, not specifically legitimate succession, preserves the scope of 正统话语.
- English 6.10: idiomatic wording for Augustus's building projects.
- French 8.8: distinguish Tiberius's refusal from the senators' insistence; remove the suggestion of mutual shirking.

Simplified Chinese, Traditional Chinese, Japanese, and Spanish are byte-identical to the received manuscripts. Reversing the offset-based ledger reproduces every received manuscript hash. There are 132 prose paragraphs and ten numbered sections per language (1,056 prose paragraphs altogether). Source notes are additional. Manuscripts retain their original Markdown heading levels; the renderer alone maps numbered sections to HTML h2.

The prior review's narrower definition of the Octavian technique, distinction between comparative cases and historical transmission, restored affirmative conclusion, and corrections to Chinese 2.5/2.10 remain intact. No new historical interpretation was introduced in this publication pass. This is not a new exhaustive historical audit or native-speaker certification of every sentence.

## Pages and navigation

- Existing bilingual `essays/ouya/ep04.html` contains complete Simplified Chinese and English texts.
- Existing Japanese, French, German, Spanish and Korean URLs receive the complete editions.
- New `essays/ouya/zh-hant/ep04.html` supplies the Traditional Chinese edition.
- Seven URLs offer eight languages through the established dropdown controller. Explicit English/Simplified links and storage-denied fallback use the already tested shared script.
- Traditional EP03 links directly to Traditional EP04; EP04 links back to EP03. EP05 remains a clearly labelled Simplified-Chinese fallback, with language handoff.
- Descriptions are updated to the reviewed essay's argument rather than the older universal-transmission claim.

## Verification and scope

- 23 Python tests passed across EP01–04: manuscript hashes, reversible edits, complete rendered prose, deterministic builds, IDs, attributes, canonical URLs, local targets, language links, and neighboring chapters.
- 108 minimal-DOM language/menu scenarios passed across EP01–04, including saved preferences, explicit queries, and denied storage at initial load.
- EP04 builder freshness check passed.
- Search indexes rebuilt from 10,191 source records; sitemap rebuilt with 10,039 canonical URLs.
- Structured search comparison shows EP04 changes in each of the eight language chunks. Rebuilding also picks up the already committed aesthetics essay `essays/aesthetics/2026-09-29.html`, whose index entry was stale at baseline. Sitemap additionally picks up that existing page and the already committed aesthetics directory dates. No aesthetics source was edited.
- Search/sitemap freshness and whitespace checks are run before commit.
- Browser preview was attempted but local-file navigation was blocked by the browser's security policy. No workaround was attempted; no visual/responsive browser acceptance is claimed.

## Rebuild

Run `python3 -B scripts/build_ouya_ep04.py`. EP03's own builder owns its updated Traditional next-chapter link. Then run the existing search-index and sitemap builders. EP04 rendering verifies published hashes and paragraph counts before writing pages.
