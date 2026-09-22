# Great Lives 045 — Schopenhauer, full-edition upgrade

Reviewed 2026-09-21. Starting HEAD remains `3c11e78` (`zhuangzi last batch`); the working tree already contained the completed, uncommitted Plato and Hume upgrades. Those changes were preserved. This turn completes **045 Schopenhauer**, closing planned batch 15 (043–045). Progress **46/108** full editions, **62** remaining. Next: 046 Kierkegaard, then 047 Turing and 048 Chekhov. No commit, push or deployment.

## Scope and reading standard

Read both earlier Chinese and English essays completely. Reworked the nine-section source before independently writing Japanese, French, German, Spanish and Korean; no external translation service. Traditional Chinese uses a converted first draft followed by complete contextual review. Every reading version retains nine sections and 60 body paragraphs, arranged 6/6/6/6/8/6/6/7/9. Counts guard against regression to synopsis; they do not certify literary quality.

The previous source had a strong desire/pendulum/dog through-line but exaggerated biography, conflated philosophical positions and turned personal moral failure into a proof that renunciation was impossible. The revised essay retains the narrative and explicit authorial disagreement while giving compassion its missing place. Familiar scenes—reaching for a glass, waiting for a reply, helping someone who falls, responding to an animal—carry the argument without front-loading SAE terminology.

## Nine-section map and corrections

1. **Berlin and recognition:** retain the 1820 scheduling confrontation. Say few listeners, not none; include later attempts to teach in Berlin. Do not treat an imagined humiliation as a verified diagnosis of all subsequent hostility. Popularity and self-described persecution do not settle an argument.
2. **Representation and Kant:** date the first edition as 1818/1819, with 1819 on the title page. Representation is not arbitrary fabrication or the ability to abolish objects by closing one's eyes. Kant's boundary is not a ban on further thinking.
3. **Body and will:** the bodily act and volition are one act known in different ways, not two causally connected events or an experiment proving movement precedes decision. Identify the extension from embodied willing to the nature of the world as metaphysical argument, not demonstrated physical measurement. Distinguish particular purposes from a final universal goal. The beast is a literary image.
4. **Pendulum:** develop the pain/boredom cycle through ordinary expectations, then state the author's reservation: impermanent satisfactions and incomplete improvements need not be valueless. Hume's return to dinner and backgammon remains a different emphasis, not an admission that all foundations are meaningless.
5. **Art, compassion and renunciation:** retain aesthetic release without reducing it to entertainment. Music's distinctive relation to will is included. Nishida's pure experience is not declared identical to Schopenhauer's aesthetic account. Restore compassion and concern for animals, alongside rather than collapsed into aesthetic respite or ascetic release. No instructions to stop living or claims of an effortless psychological cure.
6. **Hegel:** remove the thesis–antithesis–synthesis caricature, automatic improvement at every step, and the author's unsupported verdict that one method is simply true and its endpoint false. Preserve the disagreement about history and the warning against treating suffering as an automatically justified expenditure. Rejecting automatic progress need not deny particular improvements.
7. **Freud:** world-will and the psychoanalytic unconscious are not the same concept. Freud's 1925 self-report acknowledges similarities while describing his reading as late; this neither proves a simple inheritance nor resolves the entire influence history. The basement remains a metaphor, not proof that rational agency is wholly fictitious or that analysis guarantees a cure.
8. **Buddhism and personal responsibility:** take Schopenhauer's engagement with Indian thought seriously without calling him the first Western philosopher to do so. Do not identify Buddhism with will-metaphysics, rūpa with illusion, or the middle way with suppression of every aspiration. Keep the neighbour injury/payment episode without the staircase embellishment; secondary biographical evidence is not presented as inspected court records. Insight does not excuse harm, and personal failure does not prove universal impossibility or superiority to the Buddha.
9. **Reception and dog:** correct the age at the 1851 Parerga publication to 63; avoid “all Europe knew him” as literal fact. Preserve 21 September 1860, Frankfurt, age 72, without a fabricated minute-by-minute deathbed sequence. Remove blanket dog-name and Sanskrit world-soul claims. The bridge, Hume's backgammon invitation and the dog's gaze are explicitly literary invention. The ending turns toward a particular waiting life rather than awarding a metaphysical victory.

## Sources actually consulted

- Schopenhauer, [The World as Will and Representation, I](https://www.gutenberg.org/files/38427/38427-h/38427-h.html), public-domain English translation titled *The World as Will and Idea*: §§18–23, 34, 38, 52, 57 and 66–69.
- Schopenhauer, [The Basis of Morality](https://www.gutenberg.org/files/44929/44929-h/44929-h.htm), for compassion and animals.
- [Schopenhauer Society chronology](https://www.schopenhauer.de/zeittafel), for the Berlin attempts, work chronology and later life.
- Margrieta Beer, [Schopenhauer (1914)](https://www.gutenberg.org/files/47136/old/47136-h/47136-h.htm), a secondary biography, for the neighbour dispute and regular life. No claim to have directly reviewed litigation records.
- Freud, [Selbstdarstellung (1925), V](https://www.freudedition.net/werke/v/druckschrift-81), original-language account of the parallels and late reading.
- [SN 56.11](https://accesstoinsight.org/tipitaka/sn/sn56/sn56.011.than.html) and [SN 22.59](https://accesstoinsight.org/tipitaka/sn/sn22/sn22.059.than.html), for the middle way, craving and material form/non-self distinction.
- City of Frankfurt, [Ein urbanes Hundeleben](https://frankfurt.de/service-und-rathaus/presse/texte-und-kampagnen/features/ein-urbanes-hundeleben), for documented canine companionship.

All eight sources have localized labels in the six additional reading editions. Notes distinguish primary philosophy, retrospective testimony, secondary biography, the author's comparison and invented scenes.

## Edition size and Traditional Chinese review

Body only: Simplified Chinese **4,509** and Traditional Chinese **4,509** non-whitespace characters; Japanese **5,701**, Korean **5,378**. Whitespace-delimited words: English **2,416**, French **2,457**, German **2,260**, Spanish **2,431**. Each edition retains a nine-paragraph ending.

Traditional Chinese corrections include 想像、回覆、帳、沉溺、尼采 and 樓梯 in the editorial note. Every source paragraph is retained. Existing titles, article URLs, canonical numbers and movement positions are unchanged.

## Integration and verification

- New editorial source: `data/great-lives/movement-04c-schopenhauer.json`. The former `movement-04a.json` is now an empty collection, retained rather than deleted.
- Chinese/English shared source and six additional reading pages updated. Six language indexes now report 46 full editions. Latest and its ledger have one matching Schopenhauer card; historical Plato and Hume cards retain their historical counts.
- The other 107 editorial entries are unchanged relative to this turn's working-tree baseline: every pre-existing data-file hash except the collection losing Schopenhauer is identical. All fourteen Plato/Hume reading-page hashes are also unchanged.
- **128 Great Lives regression tests pass**. New checks cover content-map order, full body/ending, corrections, compassion and game names in all editions, Traditional Chinese context, and valid metadata.
- Builder check passes for **762** outputs; Latest-ledger check passes; **29 Zhuangzi tests pass**.
- Balanced markup, unique IDs and resolving local links checked on **14 pages**: shared source, six editions, six indexes and Latest.
- Search generation/check: **10,068 source records**. Each of eight language indexes changes only its Schopenhauer record against the working baseline; no additions or removals.
- Sitemap generation/check: **9,916 canonical URLs**, same set as before. Only the seven Schopenhauer reading-page entries change against the snapshot; unrelated lastmod values remain intact.
- `git diff --check` passes. No browser-rendered visual QA; structural validation is not a claim about rendered appearance.
- No commit, push or deployment.
