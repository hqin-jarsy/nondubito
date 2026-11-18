# Rickshaw Boy: multilingual delivery

Status: complete, independently reviewed and locally verified. No push.

## Scope

Three Chinese essays, restored complete English and five new complete editions in Japanese, French, German, Spanish and Korean. Source counts: 119 / 142 / 138 blocks, 399 total including three source notes. Counts support traceability; independent reading, not counts alone, establishes coverage.

## Chinese source corrections

Original Chinese and old English are retained in `data/rickshaw-boy/multilingual/source-original.json`. The 68 touched short-block positions are itemized in `data/rickshaw-boy/source-corrections.json`; repeated recaps are included, not counted as separate factual discoveries. Primary Chinese and Traditional Chinese are synchronized. Index-level changes are separately recorded.

- Distinguish the first owned rickshaw seized by soldiers, the savings for another extorted by Sun, and Huniu's used rickshaw sold for her funeral. They are not the same vehicle lost three times, nor three purchases.
- Savings are kept in an earthenware container, not on his person. Sun invokes prior acquaintance, not a common hometown, and guesses at savings rather than knowing the exact amount.
- Xiangzi initially welcomes the prospect of a rickshaw but dislikes Er Qiangzi's particular used vehicle and its history. Huniu has savings despite lacking control of the family business. The drinking scene retains pressure, desire and unequal power without treating desire as consent or inventing unconsciousness. Fake pregnancy and pressure to marry remain explicit.
- Birth assistance starts with a midwife, then ritual help, then Xiaofuzi's inquiry at the hospital. No doctor has already arrived to announce the price. Medical factors are attributed to the novel's narration rather than asserted as a modern diagnosis.
- Xiaofuzi's sale precedes her mother's fatal beating. Initially she rents Huniu's room for clients and later returns to her own. Her father's supposed second sale is not promoted from suspicion to fact. Xiangzi mourns in a pine graveyard, not while unsuccessfully searching for the particular hanging tree.
- Illness and paid treatment precede the news of Xiaofuzi's death. The grasshopper conversation is the later reunion with old Ma, after his grandson's death; Xiangzi understands it. Old Ma's hardship is not equated with Xiangzi's subsequent betrayal of another person.
- Late ceremonial work goes badly; it is not effortless, competent standing around. Ruan Ming is publicly paraded and shot. Xiangzi does not repent the denunciation but does feel fear; the book does not say he immediately spends every coin.

The central readings remain: virtues do not secure the fruits of work; people subjected to calculation can learn to calculate others; unremunerated care cannot be exhausted by that calculation. Assertions of absolute self-sufficiency are narrowed without deleting the author's individualism analysis or introducing a replacement thesis.

Original-novel chapter references and uncertainties appear in `data/rickshaw-boy/multilingual/independent-source-review.md`. Online text witnesses are not a claim to have collated a physical printed edition. Reviews are internal AI editorial work, not external native-speaker or scholarly certification.

## Final verification

All six final language hashes and the corrected-source hash match their independent full-reading reports. EN and DE were independently read by moon; FR, ES and KO by cities; JA by catch22. All three essays were read in every language, not sampled. EN/JA/FR/DE have 399 body blocks; ES/KO have 396 body blocks plus three source notes.

- Dedicated and generic checks passed: 24 pages, 386 local links, eight alternate editions, canonical and analytics integrity, complete rendering and source coverage.
- Navigation/discovery check modes passed. Unrelated search records and sitemap dates preserved against preceding commit f14086b; no prior sitemap URLs removed.
- 19 reader, supplement, Home and sitemap regression tests passed.
- Offline Chromium: 64 responsive checks at 390/1440 widths with zero failures, repeated after final JA/KO edits. The Japanese mobile screenshot was manually inspected: legible title and prose, wrapping language navigation, no visible clipping. External network/fonts were blocked; not an online deployment test.
- A repeated build produced byte-identical series files.

The exact independent series commit is available in repository history. No push performed.
