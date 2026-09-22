# Great Lives 044 — Hume, full-edition upgrade

Reviewed 2026-09-21. Starting HEAD: `3c11e78` (`zhuangzi last batch`), with the previous Plato upgrade already present as uncommitted work. That work is preserved. This turn completes **044 Hume**, not the entire planned batch 15: 043 Plato and 044 Hume are complete; 045 Schopenhauer is next. Progress **45/108** full editions; **63** remain. No commit, push or deployment.

## Editorial scope

Read both earlier Chinese and English essays in full, then revised their nine-section argument and narrative before writing the six additional editions. This is a full essay, not an expanded synopsis: the publishing disappointment, causation, personal identity, Plato comparison, dinner and game, Kant, Socrates, ethical limits and the Edinburgh/imaginary-bridge ending all remain developed.

The five foreign-language editions were independently written for their readers; no external translation service was used. Traditional Chinese began with character conversion of the revised Chinese, followed by complete reading and contextual correction. Each of the eight reading versions contains nine sections and 56 body paragraphs (eight sections of six paragraphs, then an eight-paragraph ending). Paragraph counts are preservation guards, not literary-quality scores.

## Corrections and content coverage

1. **Publication and awakening:** the Treatise appeared in 1739–1740 while Hume was in his twenties; remove the incorrect blanket age of 28 for 1739. His later account of an unsuccessful reception is a retrospective, not evidence of no readers. Kant's acknowledgment does not justify inventing a single reading event that instantly generated all three Critiques.
2. **Causation:** distinguish observation, expectation, empirical support and demonstrative necessity. The circular appeal to past success is explained through a billiard example. No claim that science is useless, every prediction is equally unsupported, or the world's causal structure has conclusively been disproved. Habit explains expectation without justifying every habitual belief.
3. **Self:** the target is supposed introspective acquaintance with a simple, unchanging self-substance, not the existence or moral standing of people. Preserve Hume's admitted difficulty about the connection of perceptions in the Appendix. The friendship analogy is explicitly not a proof of his account.
4. **Plato:** comparison is the essay's interpretation, not a quotation or historical conversation. Avoid caricaturing Plato as incapable of questioning and Hume as believing nothing. Questioning a claim to final assurance does not establish that everything is only shadows.
5. **Backgammon:** Treatise 1.4.7.9 concerns dinner, backgammon and friends, not billiards. Keep the billiard example in the causal discussion separate. The return to company changes the hold of sceptical distress; it does not refute the philosophical question. Include Hume's return to inquiry in 1.4.7.12; no permanent abandonment of philosophy or remote clinical diagnosis.
6. **Kant and later questions:** causality is a category of understanding; space and time are forms of sensible intuition. A priori is not reduced to innate brain hardware. Conditions of possible experience do not confer knowledge of everything beyond it or replace empirical investigation. Nishida is a comparative change of direction, not a conclusive refutation.
7. **Socrates:** questioning does not erase ethical commitments or evidential distinctions. The shared posture does not collapse different periods and philosophical projects. Preserve the transition from interrogation to sitting beside another person.
8. **Gentleness and blind spots:** add Hume's racist judgment in the footnote to Of National Characters as a substantive limit on the earlier idealised portrait. Do not reproduce the slur, excuse it as mere historical atmosphere, or imply that all his work is therefore cancelled. His evidential standards must apply to his own claims; familiar prejudice is not made legitimate by familiarity.
9. **Death and bridge:** Smith's letter includes personal recollection and Black's report. Distinguish friendly testimony from exhaustive access to Hume's inner state. Deathbed serenity proves neither all of a person's beliefs nor a religious conclusion; fear does not diminish a person's worth. The final bridge meeting is explicitly invented. Hume brings backgammon, offers another person a seat, and waits; he does not play a two-person game alone or defeat Plato by authorial decree.

## Materials checked

Primary texts are linked on all seven HTML reading pages, with localized labels:

- Hume, [My Own Life](https://davidhume.org/texts/mol/), composed in 1776 and published in 1777.
- Hume, Enquiry concerning Human Understanding, [IV](https://davidhume.org/texts/e/4) and [V](https://davidhume.org/texts/e/5).
- Hume, Treatise [1.4.6](https://davidhume.org/texts/t/1/4/6), [1.4.7](https://davidhume.org/texts/t/1/4/7), and [Appendix](https://davidhume.org/texts/t/app), especially paragraphs 10–21.
- Kant, [Prolegomena](https://www.gutenberg.org/files/52821/52821-h/52821-h.htm), preface and the first two main parts; public-domain English edition.
- Hume, [Of National Characters](https://davidhume.org/texts/empl1/nc), including the racist footnote.
- [Adam Smith to William Strahan, 9 November 1776](https://en.wikisource.org/wiki/The_Life_of_David_Hume,_Esq./Letter_from_Adam_Smith,_LL.D._to_William_Strahan).

Comparisons to other series essays and the final imaginary scene are identified as interpretation, not additional documentary evidence.

## Editions and preservation

Body-only counts: Simplified Chinese **4,059** non-whitespace characters; Traditional Chinese **4,059**; Japanese **5,372**; Korean **4,977**. English **2,198** whitespace-delimited words; French **2,150**; German **2,001**; Spanish **2,166**.

Traditional Chinese review corrected 想像、很準、撞球、反覆、帳 and 依據, retaining all source sections and paragraphs. The existing localized titles, numbering and URLs remain unchanged. Decks no longer misidentify the return-to-life game as billiards.

The Hume entry moves from `movement-04a.json` to `movement-04c-hume.json`. Schopenhauer is the sole remaining entry in the former collection and compares exactly equal to the turn's starting snapshot. Every other pre-existing Great Lives editorial data file has an unchanged SHA-256 hash. All seven Plato reading pages and its editor report also have unchanged hashes. Thus the other 107 editorial entries are preserved relative to the working-tree baseline, not merely compared against HEAD.

## Integration and checks

- Updated the shared Chinese/English Hume source and six separate language pages. Six language indexes now display 45 fuller editions. Fixed the source's malformed description attribute, whose nested quotation marks previously produced stray attributes.
- Added one matching Hume update to Latest and its ledger; the historical Plato update retains its historical 44/108 count. Progress ledger records 045 as next.
- **124 Great Lives regression tests pass**. New guards cover full length and section coverage, source corrections, all-language game names, Traditional Chinese forms and parsed metadata. Existing Plato's progress check is a lower bound so later editions do not invalidate it.
- Builder check passes for **762** outputs. Update-ledger check passes. **29 Zhuangzi tests pass**.
- Balanced markup, unique IDs and resolving local links checked for **14 pages**: Hume source, six editions, six indexes and Latest.
- Search generation and check: **10,068 source records**. Compared with the pre-Hume working snapshot, each of the eight language indexes changes only its Hume record; no records are added or removed.
- Sitemap generation and check: **9,916 canonical URLs**, unchanged as a set. Only the seven Hume reading-page entries change relative to that snapshot. Other lastmod values remain unchanged; language-index dates were already current from Plato.
- `git diff --check` passes. No browser-rendered visual QA was performed; structural checks are not a claim about rendered appearance.
- No commit, push or deployment.
