# The Wire full-edition repair

## Delivered

- Nine independent English readings fully compared with the Chinese argument and supplemented where examples or transitions were missing. Final English bodies range from 1,169 to 1,546 words.
- Forty-five complete German, French, Spanish, Japanese, and Korean translations replace the former short summaries. Every language retains the source's 1,226 blocks across all nine essays, including the final sections and reader questions.
- Two editorial checkpoints per language (01–05 and 06–09), followed by full-series independent comparison. This includes the ninth essay, not merely sampling opening paragraphs.
- Thirteen author-approved factual correction groups synchronized across all applicable editions; a final canonical given-name typo is corrected separately under the minor-edit scope. Exact Chinese changes total 31 block substitutions, including the remaining occurrence of the already-approved Bodie duration issue. No broad Chinese rewrite or import of the later v2 manuscripts.
- Eight-language switching, neighboring articles, series indexes, search results, homepage, Latest, sitemap dates, and existing foreign-language hubs verified. The sixty HTML pages preserve the existing routes and design.
- Immutable received snapshots, accepted-input hashes, generated-output guards, Traditional Chinese mappings, repeatable build/discovery tools, dedicated tests, and maintenance documentation.

## Verification

- 10 Wire integrity tests pass; full renderer, discovery refresh, and legacy compact generator checks pass.
- Browser regression: 240 views (80 reading views at three widths) and 40 interactions pass, without page errors. Search covers both first and last articles in all eight languages. Storage-denied and foreign-language no-JavaScript behavior are included.
- Desktop and mobile screenshots visually checked for typography, navigation, and overflow.
- All public-page analytics checks pass: 13,692 public pages, no tracking errors or conflicting copies.
- The 33-command repository workflow has 30 passes and three existing failures. All three concern four unchanged older publication-ledger entries lacking `languages`; the same failures were reproduced against the starting ledger. They are outside this repair. Exact commands and affected IDs are recorded in `verification.json`.
- Search records outside The Wire, homepage, and Latest remain identical to the baseline. Unrelated sitemap dates remain unchanged. `git diff --check` passes.

## Verification limits

Plot checking is targeted to the identified factual issues, not a fresh shot-by-shot review of sixty episodes. Interpretive claims and explicitly uncertain source recollections remain the author's. The English editions deliberately reorganize material for their audience rather than mirror Chinese paragraph counts. All five other translations are complete paragraph-aligned readings, not independently shortened adaptations.
