# We Three: local editorial repair, not a replacement English edition

## Preserved material and actual scope

The four original Chinese and English essays are frozen in `source-original.json`. Chinese contains 36/40/42/38 blocks (156 with headings and bibliographic notes). Existing English contains 14 blocks per essay (56 total, seven headings and seven substantial prose paragraphs per essay). Full reading showed that its principal scenes and argument were already present, in an independent sequence and phrasing. Shorter block counts were not treated as proof of summarization.

Chinese corrections and their Traditional equivalents are individually recorded in `../source-corrections.json`. Current source maintains the original 156-block structure. English retains all 56 original blocks and their heading positions. Only specific factual premises, source attributions, and a small close reading of the third-part title were revised or restored within existing paragraphs. Exact original/revised English blocks are in `../english-corrections.json`. No comprehensive English retranslation or Chinese–English block equality is claimed.

## What changed and what did not

- The hospital and bereavement passage concerns several years, not two; illness onset and hospital admission are distinguished. The deaths were over a year and nine months apart. The memoir was written several years after them.
- The dream does not impose a one-night-only rule on every inn. Its changing inns still support the author's reading of an unsettled carer's route; the timetable interpretation was not replaced with a different thesis.
- Housing claims were narrowed to repeated moves during shared life. The essay still argues that home is made by people, not a building. It no longer asserts lifelong absence of ownership as proof.
- Breakfast is a long-standing practice with the memoir's three exceptions, not uninterrupted daily service. The painted face is one incident, followed by a reprimand from Qian Zhongshu's mother, not a daily prank continued despite protests. Unverified geographical and table-message details were removed without deleting the private-language argument.
- Spanish study began in Yang's forties. The book is not her last publication. Precise unmeasured page fractions and exhaustive claims of no grief or complaint were narrowed while preserving the author's analysis of proportion and tone.
- Haircut and wig details are explicitly from the separate memoir *Bingwu Dingwei Nian Jishi*. Qian's cross-shaved head and Yang's half-shaved head are distinguished; the daughter's saved braid, husband's cap and pot used as a form replace incorrect materials.
- The vegetable-garden encounter remains as a concrete scene, now explicitly attributed to *Six Chapters from My Life Downunder*, “Learning Gardening at Leisure.” Qian's short walk, messenger duties, brief conversations and the letters handed over are supported by the separately recorded original-text check. It is not falsely located in *We Three*. “Anxiety and loneliness” is commentary, not an authenticated exact quotation.
- The office stay belongs to later moves after returning to Beijing, specifically 1974, not immediate homelessness on return. Qian's 1982 vice-presidency and unsuccessful resignation qualify the erroneous account of refusing every position. Scholarship remains central to the author's noninstrumental reading.

These repairs do not certify every interpretation as an objective fact. The claims about a household without a ledger, useless acts, noninstrumental affection and the allocation of memory remain the essay author's readings. The quoted physical Sanlian edition was not inspected page by page; the source audits distinguish accessible original-text transcriptions and excerpts from unverified details.

## Reproduction and review boundaries

`prepare_we_three_sources.py` applies recorded Chinese/Traditional corrections from the original snapshot. `prepare_we_three_english.py` applies local English replacements while preserving original structure. Neither source preparation step is automatically invoked during page generation. `build_we_three_languages.py` reads persistent language JSON. Its English branch checks the original English structure; the five new language branches check full Chinese coverage and heading alignment. `validate_we_three_languages.py` separately verifies these two contracts, exact recorded English edits, rendered bodies, documented Chinese changes, Traditional mappings, local links, analytics, canonicals and eight language alternates.

Independent full-text language review, final generated-page checks and browser/layout QA are recorded separately. Structural checks are not native-speaker certification. No shared navigation or search is edited by these dedicated scripts, and no push is performed.
