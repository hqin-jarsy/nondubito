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

## Other five languages: unchanged

Japanese, French, German, Spanish and Korean retain their existing Markdown,
notes and rendering. They have not been re-reviewed against the restored
originals in this change; no claim of current cross-language equivalence is made.

## Checks

```sh
python3 -B scripts/test_emperor_full_editions.py
python3 -B scripts/build_emperor_full_editions.py --check
python3 -B scripts/build_emperor_traditional.py --check
python3 -B scripts/build_collection_languages.py --only chinese-emperors --check
```
