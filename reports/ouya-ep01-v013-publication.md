# Eurasian Emperors EP01 — full-edition publication

Date: 2026-09-27. Baseline: `7cd1a7c` (clean worktree after the user's Action Theory and aesthetics commits). Local publication preparation; user pushes.

## Source and scope

Received `NonDubito_Ouya_EP01_8languages_v0.1.3_2026-09-26.zip`, SHA-256 `24faeab770565c042cbd2ab136dcad28214ac7929169b5267fde18959a4cc345`.

The eight full manuscripts, not the former compact foreign-language pages, are now stored in `data/ouya-full/`. `ep01-review.json` records source/published hashes and every local replacement. Reversing those replacements reproduces the received v0.1.3 hashes exactly.

Seven URLs carry eight editions: the existing bilingual root URL; existing Japanese, French, German, Spanish and Korean URLs; new `essays/ouya/zh-hant/ep01.html`. No EP02–22 or series directory pages were regenerated. Chinese and English continue to share their existing URL; this is not a site-wide language-URL migration.

| Edition | Body paragraphs | Section headings |
| --- | ---: | ---: |
| Simplified Chinese | 122 | 7 |
| Traditional Chinese | 122 | 7 |
| English | 132 | 7 |
| Japanese | 121 | 7 |
| French | 135 | 7 |
| German | 134 | 7 |
| Spanish | 120 | 7 |
| Korean | 121 | 7 |

All 1,007 manuscript paragraphs are rendered. Public source notes are additional and excluded from these counts.

## Local editorial decisions

- Preserve the complete essay, narrative order, examples, and argumentative ending. Do not turn the foreign editions into summaries.
- Clarify that Athenian participation concerned men qualifying for citizenship, not all free-born adult male residents. The relevant citizenship/descent distinction is in [Athenian Constitution 42](https://classics.mit.edu/Aristotle/athenian_const.2.2.html).
- Replace the unsupported claim that Spartan men normally married after thirty. Discuss young husbands' communal residence and visits to their wives without inferring a typical marriage age; distinguish family continuity, property distribution and pro-natal incentives. See [Plutarch, Lycurgus 15](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Lycurgus*.html) and [Aristotle, Politics II.9](https://classics.mit.edu/Aristotle/politics.2.two.html).
- Present Aristotle's evaluation as mixed: participation in government supports stability, but his criticisms of magistracies and property distribution remain. Do not describe Sparta as an unqualified ideal endorsed by Aristotle.
- Align outstanding translation-strength differences with the Chinese argument (including actual expansion versus attempted expansion, core versus relative value, and the source of judgement versus needing permission). These are translation-alignment decisions, not independent proof of every historical generalization.
- Qualify the empirical claim that one soldier stepping back necessarily collapses the whole line. Distinguish Socrates being killed from his questions/remainder being extinguished.
- Add localized source/interpretation notes in all eight editions. The essay's structural vocabulary is explicitly its interpretive lens, not attributed to ancient speakers.

This publication is **not** a claim of exhaustive historical clearance or native-speaker certification. Remaining specialist review topics include population estimates, military-to-political causation, changing Spartan membership rules and dates, and broad civilizational generalizations. The source list supports further checking; it is not a blanket citation proving every paragraph.

## Navigation and discovery

- Use the existing shared native language dropdown on all seven URLs.
- Bilingual links accept `?lang=en` and `?lang=zh`; unsupported stored language values fall back to Chinese instead of exposing both bodies.
- The new Traditional Chinese page points to the existing bilingual directory and explicitly labels the next chapter as Simplified Chinese. No missing Traditional Chinese EP02 or directory link is invented.
- Regenerated search indexes: 10,121 source records. Sitemap: 9,969 canonical URLs.
- These generated files also pick up the already-committed `essays/aesthetics/2026-09-27.html` and its directory date. No aesthetics or Action Theory source file was edited. All other search-record changes concern EP01.

## Verification

- `python3 -B scripts/test_ouya_full_editions.py`: six tests passed (complete prose, reversible provenance, exact output scope/idempotence, links/canonicals/IDs/attributes, Traditional navigation, correction receipts).
- `node scripts/test_ouya_language.cjs`: 27 minimal-DOM unit scenarios passed, using the actual inline and shared scripts. Covers saved/query language combinations, both inline options, all six standalone menus, return links and denied-storage initial load. This does not emulate layout or certify every browser behavior.
- Full-edition renderer, search index and sitemap `--check`: passed.
- `git diff --check`: passed.
- Browser visual/responsive QA was not completed: the browser URL safety policy rejected the local file preview. No alternate route was attempted to bypass that restriction. HTML, navigation, script behavior and existing CSS integration were checked separately; rendered appearance still needs a normal browser look after push.

## Rebuilding

Run `python3 scripts/build_ouya_full_editions.py`, then the search-index and sitemap builders. The renderer is explicitly limited to EP01 and validates manuscript hashes and paragraph counts. Future authorized editorial changes must update the receipt rather than silently replacing a manuscript.
