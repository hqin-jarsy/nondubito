# Five-series language publication: final validation

Date: 2026-11-17. Local commits only; no push or deployment performed.

## Delivered scope

- Catch-22, The Moon and Sixpence, A Tale of Two Cities: four English essays restored per series; four complete essays and an index in each of Japanese, French, German, Spanish and Korean.
- A Way Out, a Way Forward; More Than a Win for Both: three essays and an index in each new language. Existing English fully read, with four limited paragraph corrections in the former and one sentence correction in the latter.
- Total: 90 new article editions, 25 new language indexes, 115 new HTML pages. 138 series pages checked including the existing primary pages. All five series expose eight language modes.
- Language channels, collection counts where applicable, Latest, bounded Home, search and sitemap are connected. Supplements remain within their original parent topics rather than gaining duplicate Library cards.

Series commits: `7c03e2e` Catch-22; `13b84ee` choices; `4b781c9` positive-sum; `9421fd8` Moon; `6996a77` Two Cities.

## Editorial evidence and limits

The durable per-series reports describe the actual reviews and corrections. They are model reviews, not external native-speaker certification. Paragraph counts establish coverage units, not translation quality by themselves. The literary versions merge short rhetorical paragraphs into readable prose where appropriate; they are not all sentence-by-sentence replicas.

Catch-22 received full additional French and Spanish readings; German, Japanese and Korean each received independent review of 29 specified key paragraphs in addition to the writer's complete review. The other four series received complete additional readings of all five new languages. The Moon English restoration was also read in full against all four Chinese originals by the coordinator.

Source-novel checks led to narrow Chinese corrections, with Traditional Chinese synchronized: Snowden's revelation belongs to chapter 41; Strickland's childhood interest, evening study, scraper, murals-before-blindness and son's clerical role; Two Cities' murder timing, sibling identities, seamstress encounter and conditional narrative ending. Two Cities retains 36 factual correction entries, often repeated occurrences of the same error, while 12 interpretive rewrites were explicitly not applied. Reports preserve the evidence and the limits of each correction.

## Final tests

- `test_expanded_series.py` passed for all five series: 138 pages, exact rendered new bodies, eight language alternates, canonical/sitemap inclusion, local asset/navigation targets, analytics, search and channel entries.
- Dedicated Catch-22, Moon and Two Cities checks passed; the latter verifies all five final independent-review input hashes. Repeated builds were checked by the series workers.
- Full-language renderer `--primary --check` passed for both supplements. Shared integration and scoped discovery `--check` passed for all five series.
- Final offline headless-browser run: **368 cases, zero failures**, eight language modes at 390 and 1440 px. A fresh isolated profile was used with external network/fonts blocked. This checks geometry and language selection, not online font delivery or literary quality. The coordinator also inspected each series' Japanese first-essay mobile screenshot.
- Regression suites passed: reader series (4), reader supplements (5), home updates (8), recorded sitemap dates (2), totaling **19 tests**.
- Existing classical-concepts, teacher-student, university and own-faith multilingual checks passed for **135 existing translated pages**, plus their primary rendering and discovery.
- Scoped refreshes preserved out-of-scope search records; no unrelated source pages or existing Library cards were rewritten. `git diff --check` passed.

## Final regression corrections

The whole-reader regression found two stale original publication word counts after the limited English edits: positive-sum ep02 1727 → 1728; choices ep03 1466 → 1484. These counts were updated with an explicit subsequent-update note, preserving the original publication record's other historical evidence.

The same regression found that the two supplement index pages retained the old three-language availability line despite working eight-language controls. Rebuilding with the original reader generator changed only those three localized availability labels per index to eight languages. Subsequent renderer, discovery, regression and final 368-case browser checks all passed. This small cross-series QA correction is separate from the five content commits.
