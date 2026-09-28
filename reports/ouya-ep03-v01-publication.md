# Eurasian Emperors EP03 — complete eight-language editions

2026-09-28. Baseline: `d97ecb4`, clean at the start. Local publication preparation; the user pushes.

## Source and editorial scope

Source: `NonDubito_Ouya_EP03_8languages_v0.1_2026-09-28.zip`. Package and manuscript hashes are recorded in `data/ouya-full/ep03-review.json`. The received archive was not changed.

The previous review's content corrections remain intact: the escalation leading to Gaius Gracchus's death, qualifications around the legal effect of plebiscites before 287 BCE, ordinary citizens' political agency, and the author's affirmative person-as-end interpretation.

This publication adds 28 reversible, local copyedits:

- Japanese: 18 contextual distinctions between an office and the magistrate holding it; three further edits clarify the actors choosing violence, the expression for retirement, and the verb for reopening a political path. Institutional uses of 官職 remain intact; no global substitution was made.
- Spanish: correct `disponer de` and remove an unnecessary reflexive form that could suggest reciprocal killing.
- French: three idiomatic improvements concerning a disputed question, mutually constraining requirements, and arrangements surviving Sulla's retirement.
- English: clarify an awkward expression for killing and the referent of the later transfer of power.

Simplified Chinese, Traditional Chinese, German and Korean are byte-identical to the received manuscripts. Reversing the offset-based edit ledger exactly reproduces the received hashes for all eight languages. The ledger is also checked by automated tests.

All eight editions render 128 prose paragraphs and ten section headings, in addition to the unnumbered introduction's place in the paragraph count: 1,024 prose paragraphs total. Reading notes and three Plutarch source links are additional, not replacements for manuscript text. Notes distinguish the essay's interpretive vocabulary from ancient testimony.

This closes the local language issues identified in the prior review. It is not an exhaustive new historical audit or native-speaker certification of every sentence.

## Pages and navigation

- The established bilingual `essays/ouya/ep03.html` keeps complete Simplified Chinese and English editions.
- Japanese, French, German, Spanish and Korean retain their existing URLs and receive the complete texts.
- New `essays/ouya/zh-hant/ep03.html` contains the Traditional Chinese edition.
- All seven URLs use the existing eight-option language dropdown. Links back to the bilingual page explicitly choose English or Simplified Chinese.
- Traditional EP02 now links directly to Traditional EP03; EP03 links back to EP02. Its next-chapter link clearly says Simplified Chinese and points to the existing bilingual EP04, with the stored-language handoff needed by that older page.
- No other episode's prose or series directory was rewritten. EP02's builder and navigation test were updated so rebuilding will preserve the new link.

## Verification

- 17 Python tests passed across EP01, EP02 and EP03: full prose rendering, reversible edits, unchanged-language hashes, deterministic builds, IDs, attributes, canonical URLs, local links and neighboring chapters.
- 81 minimal-DOM scenarios passed for the actual inline language scripts and the shared dropdown controller across EP01–03, including saved preferences, explicit language queries and denied storage at initial load.
- All three edition builders passed `--check`.
- Search indexes: 10,123 source records. Structured comparison shows changes only to the EP03 record in each of the eight language chunks.
- Sitemap: 9,971 canonical URLs. Structured comparison shows changes only to EP03 URLs and the updated Traditional EP02 page.
- Search-index and sitemap freshness checks and `git diff --check` passed before commit.
- No new browser visual/responsive acceptance was performed. These checks do not claim screenshot or layout verification.

## Rebuild

Run `python3 -B scripts/build_ouya_ep03.py`; EP02's separate builder owns its Traditional next-chapter link. Rebuild search indexes and sitemap with the existing project scripts afterward. The EP03 builder verifies all published manuscript hashes before rendering.
