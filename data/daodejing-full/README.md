# Reviewed Daodejing full editions

Chapter 1 is the only chapter opted in. The five manuscripts come from
`daodejing-ch01-translations.zip` in the author's multilingual flagship archive.
Simplified Chinese, Traditional Chinese and English are unchanged.

The editorial pass restores the visible Chinese variant comparisons in French,
German and Spanish (恒／常, 眇／妙, 所徼／徼). In all five languages, the author's
reading of 名 is expressed as “the name for …”, not as an act performed by
non-being or being. A few Korean sentences use more natural descriptions of
drawing distinctions; the established terms 여항, 착, 구 and 착구 순환 remain.
No sections, examples or arguments from the received manuscripts were removed.

`ch01-review.json` records package and manuscript checksums, reversible edits,
the original page shells, and the protected Chinese/English files. Existing
classical-text blocks, edition notes, metadata and navigation are preserved.
The text remains the author's philosophical reading, not a claim to provide a
new diplomatic transcription or philological consensus.

Build/check from the repository root:

```sh
python3 -B scripts/build_daodejing_full_editions.py
python3 -B scripts/build_daodejing_full_editions.py --check
python3 -B scripts/test_daodejing_full_editions.py
python3 -B scripts/test_daodejing_sources.py
```

The tests cover manuscript integrity, eight sections / 119 paragraphs / eight
quotations in each edition, unchanged shells, language choices and local links.
They are static checks, not browser layout verification.
