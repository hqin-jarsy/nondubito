# Daodejing: chapter texts before the essays

Added 2026-09-15. This feature quotes the Chinese text adopted by Han Qin's
nine-volume commentary, not a newly reconstructed critical edition.

## Editorial source and boundaries

- `data/daodejing-chapter-texts.json` contains all 81 chapters in the site's
  existing received-text numbering. Chapter 28 has four paragraphs; no
  paragraph may be dropped. Each record links to its source paper.
- The source papers are `https://self-as-an-end.net/papers/sae-daodejing-1.html`
  through `sae-daodejing-9.html`, nine chapters per paper. Only their Chinese
  **原文 / 帛书本** blocks were extracted, not their received-text comparisons.
- HTML tags, entities, and a leading Markdown quote marker were removed.
  The adopted characters and punctuation were otherwise preserved. These
  are modern edited readings, not diplomatic transcriptions of manuscript A
  or B, and not photographs of the ancient characters.
- The pasted compilation supplied by the author was checked as a secondary
  comparison, not used as the publication source. Its chapter numbers differ
  at 22–24, 40–41, and 67–81. Existing URLs and navigation are unchanged.
- Classical Chinese text stays identical in every reading mode, including
  Traditional Chinese. The interface and editorial notes are localized;
  the quoted source is deliberately excluded from automatic conversion.
  No new foreign-language translation of the ancient text is implied.

## Targeted checks and unresolved limits

1. Chapter 1's `无，名…；有，名…` is the author's punctuation, not punctuation
   recovered from the silk. Chapter 4 follows the author's choice `道冲`.
2. Chapter 14 uses the paper's `听之而弗闻，名之曰希`; the pasted compilation
   misplaced the comma after `弗`.
3. Chapter 25 retains the paper's normalized `寂兮寥兮`. Public transcriptions
   of A and B use differing characters. Do not label the chosen wording a
   literal transcription shared by both witnesses. The pasted `渊呵寥呵`
   was not established as a preferable reading.
4. Chapter 42 retains `夕议`. The character 夕 does not by itself establish
   the meaning “at dusk.” Liao Ya-hui, *〈老子〉的道、德論* (2010), p. 68,
   note 85, cites Gao Ming's *帛书老子校注*, pp. 33–34, reading the characters
   as loans for `亦我`. The dusk interpretation belongs to the author's
   commentary, not an uncontested philological conclusion. The institutional
   PDF is at <https://irlib.pccu.edu.tw/retrieve/58136/gsweb.pdf#page=75>.
   This is a checked secondary citation of Gao, not a claim to have consulted
   those pages of Gao's book firsthand.
5. Chapter 67 follows B's `不宵` read as `不肖`. A is damaged and its surviving
   word order differs. Do not copy the source paper's overly broad claim that
   the two manuscripts are identical at this point. The source paper itself
   was not modified in this task.
6. Chapter 80's `使民重死而远徙` was preserved, not silently changed to the
   familiar received `不远徙`. Chapter 81 likewise preserves `人之道`.

Auxiliary A/B transcription: <https://zh.wikisource.org/zh-hans/老子_(帛書本)>.
This openly editable transcription is useful for comparison; it is not a
substitute for manuscript images or a scholarly critical edition.

Fudan's [2024 revised-edition announcement](https://wmzx.fudan.edu.cn/81/91/c20566a688529/page.htm)
confirms substantive revisions to *长沙马王堆汉墓简帛集成*, including the Laozi
A-text notes. The complete 2024 edition was **not** collated for this feature.
Do not describe the publication text as “the latest definitive silk text” or
“all 81 chapters verified against the 2024 edition.”

## Build and verification

```sh
python3 scripts/build_daodejing_sources.py
python3 scripts/build_daodejing_sources.py --check
python3 -m unittest discover -s scripts -p 'test_daodejing_sources.py'
```

For a browser check, serve the repository locally, make Playwright available
to Node, and run `node scripts/test_daodejing_sources_browser.cjs <local-url>`.
`DDJ_BROWSER_CHANNEL=chrome` selects an installed Chrome when needed.
The test checks eight reading languages at desktop, 390px, and 320px widths,
keyboard-operated notes, unchanged quotations during language switching, and
static reading without JavaScript. `DDJ_SCREENSHOTS` may name an existing
directory for optional visual samples; no screenshots are needed in the repo.

The build updates a marked section and one CSS reference in each of the 486
chapter HTML files (81 × six physical editions), plus the conversion guard in
81 chapter-local Traditional Chinese scripts. It does not regenerate essays,
indexes, introductions, site-wide search data, or navigation. All quotations
and labels are static HTML; there is no runtime translation or fetch service.

`data/daodejing-source-ui.json` supplies labels and short notes in eight
reading languages. Longer source explanations live in native `<details>`;
the chapter text itself remains visible without JavaScript or expansion.

When changing a source reading, compare its source paper and editorial note
first. Amend the JSON explicitly and rebuild; do not manually edit hundreds
of generated quotations or normalize their ancient variant characters.
