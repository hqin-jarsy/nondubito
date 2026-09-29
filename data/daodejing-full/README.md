# Reviewed Daodejing full editions

Chapter 1 was the first chapter opted in. Its five manuscripts come from
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

## Introduction and chapters 2–5

The second package, `daodejing-batch01-daoyan-ch05.zip`, supplies 25 complete
manuscripts in Japanese, Korean, French, German and Spanish. No automatic
translation is used. Targeted edits correct the introduction's claim that the
silk manuscripts had no divisions, acknowledge the ritual use of straw dogs in
chapter 5, and distinguish a philosophical portrait of Laozi from established
biographical facts. These corrections also appear in the existing Chinese,
Traditional Chinese and English editions. Other Chinese/English chapter bodies
are not replaced. Classical source blocks remain unchanged.

Additional edits restore visible variant glyphs, smooth specific Korean and
Spanish phrases, and distinguish five thousand Chinese characters from five
thousand words. Spanish introduction/chapter-5 titles and English chapter-5
titles are synchronized with index and adjacent-page links. The chapter-1
receipt records the corresponding Spanish navigation-only amendment.

`batch01-review.json` records the baseline commit, package and manuscript
checksums, reversible editorial changes, and approved page checksums. Reversing
the ledger recovers each original manuscript exactly; differences in paragraph
counts between languages are retained rather than forcing a common template.

```sh
python3 -B scripts/build_daodejing_batch01.py --check
python3 -B scripts/test_daodejing_batch01.py
```

These checks complement the chapter-1 and classical-source regression tests.
