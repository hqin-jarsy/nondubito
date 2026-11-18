# Black Myth: Wukong multilingual expansion — 2026-11-18

## Scope

Four essays, existing independent English plus simplified/traditional Chinese, and complete Japanese, French, German, Spanish, and Korean editions. No push. Shared discovery changes are limited to this series and its containing game/channel/home/library surfaces.

## Source and editorial decisions

Frozen corrected Chinese: 351 blocks, distributed 90 / 87 / 89 / 85. The original 353 Chinese blocks and all 134 English blocks remain in `data/black-myth-wukong/multilingual/source-original.json`. Two exactly duplicated paragraphs were removed. `source-corrections.json` records 86 changed source positions, including repetitions and dependent passages; this is not 86 independent factual discoveries. Corrected source SHA256: `d5340902c7c6b9ee182bf59f6cff89da2702572d0b3d0a6e61e7e7ad3a4484ce`.

The original English essays were read as independent prose, not automatically treated as incomplete because they are shorter. Their 134 blocks (32 / 34 / 33 / 35) are retained, with 20 documented local corrections. Final English SHA256: `9b52eb31c07f1a59ab54dd84b184b200044b7da10612eabdd99a1d16def5a5e0`. All four essays and the complete corrected Chinese source were independently read for English review.

Representative Chinese changes:
- The Old Monkey's six-root assessment is located inside the stone egg, not asserted as an inscription at each chapter's beginning.
- The Destined One hears about the missing sixth root. Missing Wukong's memory does not mean the protagonist himself has no will. The circlet occupying the place of purpose is retained as a reading, not stated as a game mechanic.
- Competing endings and partly concealed cooperation are not expanded into two fully documented, omniscient master plans. Erlang's post-battle explanations are acknowledged without pretending they reveal everyone's motives.
- Kang-Jin, Turtle/Snake, and the Pansi/Ziyun characters are no longer collapsed into one set of Yellowbrow prisoners. The Yulan debate speaker is not falsely identified as the Buddha.
- Yellowbrow's manufactured-evidence argument is retained without relying on an unverified shot of him physically blocking an escape route or standing on shore.
- Jinchi's death follows the original novel's wall-striking scene, not burning to death; his age is not treated as the length of an abbot's tenure. The Great Sage title is proposed by the one-horned demon king and claimed by Wukong, rather than invented in isolation.
- Chapter title 未竟 and final animation title 未尽 are distinguished. The Destined One opening his eyes is separated from remembered Wukong leaving the cave; an empty gathering is not evidence that every guest died.

The independent source audits in `black-myth-wukong-audits/` and the multilingual data directory preserve evidence and limits. Official page/title material, original-novel text, and game dialogue transcriptions have different evidentiary status. Community transcriptions are not official publications. No reviewer claims a fresh complete playthrough or full frame-by-frame viewing of the animations. Unverified, nonessential cinematic details were removed rather than asserted as newly verified.

## Verification

All six English/new-language editions passed independent full reading, including metadata. New language coverage is 351 source units each: JA/FR retain all 351 in body; DE/ES/KO retain 347 body units plus four separately rendered source notes. Local review fixes: JA 4, FR 6, DE 5, ES 11, KO 30. Final `cross-review-*.json` records agree with actual source and target file hashes; author self-reviews retain their original history and point to the subsequent final independent review.

- 30 series HTML pages, including 25 new language pages; all final body prose rendered, 491 local links valid, one canonical and eight language alternates each.
- Eight-language primary selectors and language-channel entries; category/library labels, Home, Latest, site-update ledger, search, and sitemap updated.
- The same ending-description correction also reaches the game category, Library, Traditional Chinese global entrance, and their Traditional dictionaries. Exact shared changes are separately logged and regression checked.
- 80 offline browser cases at 390 px and 1440 px across all eight language views; no horizontal overflow or language-selection failure. Final mobile screenshot inspected for wrapping, legibility and spacing. External fonts blocked during the isolated-profile smoke run.
- All 30 final HTML files byte-identical after a repeated normal build; connector and scoped discovery `--check` pass.
- Unrelated search records and sitemap dates preserved from preceding commit `e8dfa08`. Shared category logic now follows the series directory, avoiding a hard-coded literature index; an explicitly declared extra discovery path includes the Traditional global entrance.
- 19 existing reader/supplement/home/sitemap regression tests pass. The preceding Don expansion also passes the generic expansion test after support was added for explicitly rendered source-note coverage.

Paragraph coverage and link tests are not a substitute for full editorial reading. No native-human or scholarly certification is claimed. No commit in this batch has been pushed.
