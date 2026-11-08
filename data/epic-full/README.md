# Epic Traditions: complete multilingual editions

This additive integration keeps the 20 existing article URLs and six existing
series-index URLs. Each primary page continues to switch between English,
Simplified Chinese and Traditional Chinese. Japanese, French, German, Spanish
and Korean retain their existing companion URLs.

## Canonical inputs

- `received/alignment/`: all 160 ordered documents from the delivered archive.
  The six foreign languages are complete translations of the Chinese, not
  expansions of the former English summaries.
- `received/source-snapshots/`: the 20 received primary-page snapshots, stored
  as `.html.txt`. All matched the local repository before integration.
- `received.json`: original archive SHA-256, Git baseline, per-file hashes,
  source URLs and integration review receipts.
- `chinese-baseline.json`: immutable hashes of the original Simplified and
  Traditional Chinese regions, including titles and navigation, on all 21
  primary pages. The renderer accepts only those originals or their exact
  explicitly approved replacements, and refuses other Chinese source drift.
- `author-corrections-20261108.json`: the five accepted source corrections in
  both Chinese scripts and six translations, plus restoration of the original
  rhetorical wording in foreign versions of essays 14 and 15.
- `reviews/`: targeted bilingual semantic-review coverage and limitations.
- `received/PRIMARY_SOURCE_POINTS*.zh.txt`: proposed Chinese-source corrections,
  not changes applied by this integration.
- `received/QUALITY_REVIEW*.txt`: original delivery review records.

The original archive checksum list is retained as provenance. It also lists
offline-reader/Markdown files not duplicated here. `received.json.files`
identifies the exact received subset kept in this repository.

## Build and check

Use Python 3.10 or later; the new renderer uses only the standard library.

```sh
python3 -B scripts/build_epic_full_editions.py
python3 -B scripts/build_epic_full_editions.py --check
python3 -B scripts/build_collection_languages.py --only epic-traditions --check
python3 -B -m unittest discover -s scripts -p test_epic_full_editions.py
```

The legacy collection renderer applies the complete-edition overlay. It cannot
silently publish its older three-paragraph foreign summaries over these texts.
The overlay preserves existing card descriptions, page furniture, reading doors,
source links, canonical URLs, language controls and analytics.
Before either rebuild path writes, the overlay checks existing foreign article
bodies and titles against the received or approved editions. Unrecognized manual
prose changes stop the build instead of being silently replaced.

For local browser regression, start a static server on port 8795, make
Playwright available to Node, and run `node scripts/test_epic_full_browser.cjs`.
The test blocks external requests, including analytics. It checks 336 reading
views at desktop/mobile widths, repeated language selection, cross-language
navigation, browser Back/Forward, invalid stored language and overflow.

## Editorial boundary

On 2026-11-08 the author accepted only the first five proposed source fixes:
the funeral-truce day, Dido's falling in love, Grendel's fatal wound, the
giant-forged sword, and the source-note chronology of Satan and Abdiel. Only
those five paragraph positions change in each Chinese script. All other
source wording remains, including the literary images and rhetorical
questions the author chose to preserve.

Foreign editions are synchronized to those five changes. Their essay 14
question again asks who will die, and their essay 15 titles retain first
return without adding before continuing the journey. No other foreign prose
is rewritten in this pass. Natural pronoun resolution and existing literary
terms are not mechanically replaced.

The received package records full translator self-review. This integration adds
automated full-block checks and targeted Chinese-aligned semantic sampling in
all six foreign languages, including every title and final source note.
No necessary translation-only fix was identified in those samples. This is
not exhaustive independent sentence-level review or native-editor certification.

Keep received files immutable. A future approved translation edit may be recorded
in a review JSON's `edits` array with `episode`, `lang`, zero-based `block`,
`before`, `after` and `reason`, updating the receipt hash. The renderer checks
the exact previous text and rejects duplicate coordinates. Chinese changes need
separate editorial approval recorded in a scoped correction receipt. The
original received Chinese and its baseline must remain immutable.
