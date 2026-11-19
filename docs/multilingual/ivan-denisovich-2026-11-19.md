# One Day in the Life of Ivan Denisovich: eight-language edition

## Editorial scope

Three complete Chinese essays (42 / 47 / 46 blocks) are the source for the five new language editions. The 35-block English version remains an independent essay sequence, not a shortened translation to be mechanically expanded. Original Chinese and English are retained in `source-original.json`, with original page hashes. The frozen source and the correction ledger distinguish fact corrections from the author's interpretation.

The source specialist checked the novel passages behind the corrections: repeated uses of the name and patronymic; Senka's earlier hearing injury; Tyurin's expulsion in the thirties; ownership of the unregistered trowel; boards used to secure window covering; the five-day ration claim and the usual deduction; the office pause while hoping for tobacco; the extra porridge's bowl-count trick; and the captain's morning search rather than the evening blade search. The English version receives four matching local corrections. An unsupported specific use of the power station's electricity is removed without altering the craftsmanship argument. The authorized Willetts translation is identified with the final uncensored text, not the earliest manuscript; claims about Chinese readership are scoped to the edition discussed.

This is editorial/source checking, not exhaustive collation of all Russian and Chinese editions. Individual language receipts describe the actual full-read review and final hashes; they are not native-editor certification. New five-language prose follows the whole Chinese source, including dividers and bibliographical notes. A note may be rendered separately, but it remains part of coverage.

Traditional-Chinese changes preserve the corresponding source emphasis and text-node lookup keys; context-dependent 幹/裡 were reviewed rather than accepting automatic conversion blindly. Unchanged primary prose/markup is retained.

## Reproduction

```
python3 -B scripts/build_reviewed_literary_languages.py one-day-in-the-life-of-ivan-denisovich
python3 -B scripts/connect_full_series_languages.py one-day-in-the-life-of-ivan-denisovich
python3 -B scripts/refresh_literary_discovery.py one-day-in-the-life-of-ivan-denisovich
```

The renderer checks source identity and complete translated block/heading coverage and fails closed on changed paragraphs with unhandled inline markup. Shared discovery is separate and scoped; it must preserve unrelated search records and sitemap dates.

## Verification

Completion results and exact page/link/layout counts are recorded in the accompanying multilingual validation record after the final rendered edition is checked. No publication or push is part of this task.
