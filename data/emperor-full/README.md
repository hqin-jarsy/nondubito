# Chinese Emperors content sources

## Chinese and English: restored originals

On 2026-09-25 the author requested restoration of Simplified Chinese, Traditional
Chinese and English, leaving the five other languages unchanged.

`ep01.zh.md`–`ep25.zh.md` and their `.en.md` counterparts now contain the original
article title followed by `<!-- emperor-original-html -->` and the original
HTML prose. The HTML is intentional: it preserves wording, emphasis, paragraph
boundaries and section headings without a lossy HTML-to-Markdown conversion.

The source is the website immediately before the September 24 multilingual
upgrade, commit `325373e198a1df9bb701b1891ee4a819ccd746ba`. `original-zh-en.json`
records its titles, directory summaries and SHA-256 hashes of the 50 bodies.
The builder rejects changes to these originals unless the baseline is explicitly
updated after editorial approval. Multilingual work alone is not authorization
to revise the Chinese or English originals.

Traditional Chinese is generated offline from the restored Chinese by
`scripts/build_emperor_traditional.py`; it is not a separately rewritten edition.

This is version restoration, not a claim that all historical assertions have
been newly verified. Later factual corrections should be reviewed individually.
The September 24 rewritten sources remain recoverable in Git history.

## 2026-10-01: faithful five-language replacement and authorized local corrections

The author's `多语言新版` packages now replace all 125 Japanese, French, German,
Spanish and Korean manuscripts. The prose follows the restored Chinese section
and paragraph sequence. Old expanded rewrites and their different footnotes
remain in Git history; obsolete notes are not attached to the new prose.

The author explicitly approved small Chinese/English corrections on 2026-10-01.
`new-edition-copyedits.json` records exact before/after replacements. Paragraph
boundaries, argument structure, titles and directory summaries are preserved.
`original-zh-en-2026-09-25.json` keeps the original uncorrected lock snapshot;
`original-zh-en.json` remains an enforced lock for the now-corrected editions.
The language update does not authorize any further unlogged source rewriting.

`new-edition-review.json` records archive/manuscript hashes, received editorial
notes, removed submission headers/footers, expected blocks per section, and all
local edits. Received notes are historical records, not instructions, proof of
author approval, or a claim that every assertion has been independently checked.
The review covers full structure, cross-language targeted reading and local
factual checks; it is not a new exhaustive historical audit of all 125 texts.

`scripts/import_emperor_new_editions.py` was the explicit one-time import. It
refuses to run over an existing receipt. Normal builds use only the checked-in
manuscripts and require no ZIPs or translation service. Site templates supply
language-aware navigation; submission links back to Chinese are not inserted
into foreign article bodies. Traditional Chinese is regenerated from Chinese.

## Checks

```sh
python3 -B scripts/test_emperor_full_editions.py
python3 -B scripts/build_emperor_full_editions.py --check
python3 -B scripts/build_emperor_traditional.py --check
python3 -B scripts/build_collection_languages.py --only chinese-emperors --check
```
