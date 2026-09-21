# The Zhuangzi, Reopened / 大知解庄子

## Status — 2026-09-20

First batch ready in the local repository, not deployed: the series index, guide (00), and essays 01–05. All six reading pages contain Simplified Chinese, Traditional Chinese, and complete independently written English. The full request is not yet complete: 62 numbered essays (06–67) remain to be edited and adapted.

The original folder contains 68 Markdown files, continuously numbered 00–67. The manifest records the filenames and SHA-256 hashes. None of the original Documents files was changed. The repository was clean at the start of this work, at `3a5d81a4a2b068fa01d5d6d47fbee006ecd37d1e`.

## Reading map and integration

- Preserve the original essay numbers rather than silently renumbering the later return to the third group.
- Introductory encounters: 01–10; Inner Chapters route: 11–29; textual discernment: 30–41 and 59–65; Outer Chapters: 42–58; closing reflections: 66–67.
- Four suggested entrances, six available-page cards, compact grouped contents, and an optional original-order list.
- Unedited titles appear as “in preparation,” without article links or empty placeholder pages. Pending English titles are provisional catalogue labels, not claims that the corresponding English essays exist.
- Link the new series alongside the Analects and Daodejing in Library; add Explore and Latest entrances. Include sibling series links and four companion-volume DOI links at the series landing page.
- Reuse the established language dropdown and three-reading-mode URL convention. No sitewide language-URL migration is attempted.
- The series has its own scoped layout. Content headings do not use unscoped `header` elements, avoiding the fixed-header collision seen in earlier layouts.

## Editorial decisions in this batch

The guide and 01–05 were read in full. The initial inspection also read 30, 44, 65 and 67, but this is not an assertion that all 67 numbered manuscripts have completed editorial review.

### 00 — Guide

Preserve independence of individual essays and the four entrances. Distinguish writing, philosophical value, and historical authorship. The teaching sequence is identified as this series' proposed reading, not an established ancient syllabus. Replace the claim that a 52-chapter authorial original simply lost nineteen chapters with a cautious distinction between an early recorded collection and the received 33-chapter text.

### 01 — Hundun

Retain the visitors' gratitude, the seven-day process, the common human template, the performance-review example, the lost relationship, and the question addressed to a person with power. Remove invented successive acquisitions of sight and hearing. Having a different body is not already a proven deficiency. Do not treat each operation as objectively correct, or extrapolate an inevitable death law. Workplace claims are grounded in the author's experience, not assertions about every company. Recognition of a form's limits does not require abandoning evaluation. The other side's loss is not a claim that domination never benefits a controller.

### 02 — Seabird

Retain the feast, habitat and diet, the difference between personalization and responsive care, golden handcuffs, the right to refuse, and Confucius's framing conversation with Zigong about Yan Hui. Do not infer a dose-response law from three days versus seven. Do not invent a digestive mechanism or a unique physiological cause of death. The text's absence of a bargain does not prove the ruler's every private motive. Employment remains a genuine exchange, not literally the same situation as the bird; staying may be prudent and the metaphor does not make the reader's decision. Retitle the Chinese essay to “这份好，为什么海鸟受不了——鲁侯养鸟” to avoid an absolute claim about the ruler's benefit.

### 03 — River Lord

Retain genuine success as the ground from which overconfidence can grow, the three contrasting responses, the well/season/education limits, replacing one measure with another, success insulating its holder, and the sea's own limit. The inference to “all” exceeds real evidence; it is not wholly correct even within the River Lord's experience. Embarrassment is not a prerequisite for deserving instruction, and failure is not the only route to learning. Correct the narrative timing of subsequent questions versus earlier remarks. Avoid treating an argument about relative comparisons as a physical proof. Retitle the Chinese essay to “看见海之后，他又问了一句——河伯望洋.”

### 04 — Axe and partner

Retain the grave setting, unnoticed stationary partner, ruler's request, Hui Shi's role, success and organizational silence, two forms of a lost counterpart, and the irreplaceable relationship. Outward composure does not prove an absence of inner fear. “Swinging like wind” does not establish maximal force or a mechanical necessity. Trust is not physical safety. A moment of mutual reliance does not prove perfect trust in every matter throughout a relationship (consistent with the user's 15DD/16DD distinction, without putting DD terminology into the essay). Asking for advice or inviting objections is not inherently wrong; the relationship's conditions matter.

### 05 — Yang Ziju

Retain the outward/return contrast, five actions in the inn, the interval before a requested explanation, ordinary equality, meeting-room analogy, and the ending's effect on the reader. Do not invent a procession, a fixed length of travel, the identical individuals on both visits, or access to everyone's motives. Silence is read with the later request, not as automatic proof of insight or a demand to accept unjust criticism. Distinguish informality from abuse. An open invitation can help when subsequent behavior supports it. A restrained ending is not proof of historical authorship, and explicit explanation does not automatically refute itself.

## Language and prose

The English guide is approximately 800 words, and the five English essays about 1,400–1,560 words each (8,308 whitespace-delimited words in all six files). These counts are scope checks, not measures of quality. Stories, contemporary applications, comparisons, and ending questions remain; the English is not a synopsis.

Chinese source sections are retained. Excessive bold and X-specific footer furniture are removed. The renderer consolidates adjacent short Chinese prose blocks, preserves quotations and section breaks, and omits horizontal-rule remnants. “See the pinned post” is replaced with actual research navigation.

All six Traditional Chinese manuscripts received full reading review, followed by contextual corrections and inspection of later changed passages. Script conversion was only a first pass. Corrections include 餘項, 舍者/客舍/至舍, 九萬里, 反覆, 矽谷, 校準 and 了望洋. Later builds use the committed Traditional Chinese manuscripts; they do not convert over them silently. `--refresh-hant` is an explicit draft-generation command and must be followed by review.

## Sources and limits of verification

The source manuscripts supply the classical passages. Original-text links are provided at each article. During initial review, the complete [Su Shi memorial text](https://zh.wikisource.org/zh-hans/莊子祠堂記) was checked; his reasons for doubting the four chapters must not all be reduced to the phrase about shallow writing. [Stanford's discussion of the evolving text](https://plato.stanford.edu/entries/zhuangzi/#EvoTexThe) informed the caution about editions and authorship. Primary passage excerpts in public-domain texts and source-search results confirmed the central incidents and the bird's framing conversation. A [National Taiwan University course handout](https://ocw.aca.ntu.edu.tw/uploads/course_item_file/file/6163/104S102_AA14L01.pdf) also reproduces that framing passage in the retrieved excerpt.

Direct ctext.org chapter fetches failed with 403/inaccessible results; no claim is made to have read those pages in full. Companion DOI links come from the author's supplied manuscripts; this batch did not re-review all four theoretical books or collate every textual variant.

## Verification

- 14 Zhuangzi tests pass: complete inventory, grouping, publication boundary, three reading editions, Traditional Chinese coverage, contextual characters, balanced HTML, unique IDs, language bodies, local links and fragments, pending entries, canonicals/schema, editorial safeguards, search metadata, original-file hashes, and site entrances.
- Builder `--check` passes for all seven pages; update ledger matches Latest.
- Search rebuilt and checked: 10,004 source records. Exactly seven new records in each of EN / zh-Hans / zh-Hant, all in the stories domain; no existing search records changed.
- Sitemap rebuilt and checked: 9,852 canonical URLs, seven more than the starting state.
- Library, Explore, and Latest pass balanced-markup/unique-ID checks. `git diff --check` passes.
- Method-introduction regression suite: 10/10 pass.
- Book-introductions regression suite: 12/13 pass. The existing `test_library_categories_and_generated_cards` fails on the nonfiction generated-card block. Re-running that exact test with the unchanged HEAD `library.html` supplied read-only reproduces the same failure. No unrelated nonfiction data or builder was changed.
- No browser-rendered visual QA was completed. Structural tests are not presented as visual verification.
- No commit, push, or deployment performed.

## Next batch and later editorial flags

Continue 06–10: 庖丁解牛、凡君、惠子相梁、列子门外的鞋、庄子将死. Read and edit each Chinese essay, write its complete English counterpart, review Traditional Chinese, then expand the publication manifest and source links. Update progress labels in Library/Explore/Latest and tests together. Do not generate all remaining pages from unreviewed text.

When reaching 30, 65 and 67, preserve the author's reading criterion while distinguishing it from proof of authorship. “Only internal evidence exists,” “forms of address make this impossible,” and “stopping cannot be imitated” need specific evidence or qualification. Essay 65 promises a return to the series' own use of explanation; ensure the ending actually answers that question without claiming that every explicit explanation is coercive. Those essays are not published in this batch.
