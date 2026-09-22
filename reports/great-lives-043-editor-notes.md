# Great Lives 043 — Plato, full-edition upgrade

Reviewed 2026-09-21. Clean starting HEAD: `3c11e78` (`zhuangzi last batch`). This completes **one article**, the opening of planned batch 15, not all three. Hume (044) and Schopenhauer (045) remain for continuation. Progress **44/108** full editions, **64** still awaiting this upgrade. No commit, push, or deployment performed.

## Editorial scope

Read both previous Chinese and English essays completely. Reworked the nine-section source in both languages before producing the six additional editions. The point is a full essay, not a synopsis: absence, narrated voice, the search for a standard, the cave's painful ascent and return, political authority, the author's disagreement, transmission, later thinkers, the Academy and the imaginary bridge all remain developed. No external translation service was used. Automatic conversion was used only for a Traditional Chinese draft, followed by complete review.

The former article treated conjectural psychology as explanation, made demonstrably excessive claims about every dialogue and the Academy, and used the series' own premise as a proof against Plato. The revised criticism focuses on the passage from a claim to better understanding to authority over others' lives. It retains disagreement without reducing Plato to a closed-system caricature.

### Nine-section coverage

1. **Absent witness:** Phaedo's “I think” belongs to the narrator; it is not Plato's uncertainty about his own illness. Preserve the prison, friends, conversation, poison and cock, but distinguish narrated composition from an eyewitness transcript. Do not diagnose emotional illness. Socrates appears in many dialogues, not every one; the Laws is an explicit counterexample.
2. **Dialogue voices:** early/middle/late and the Socrates–Plato transition are interpretations, not a sentence-level attribution chart. Socrates has ethical commitments; questioning does not amount to having no positive convictions. The architectural metaphor does not exhaust either thinker.
3. **Forms and loss:** distinguish conviction from sentencing and remove the disputed vote tally. Explain a standard beyond changing opinion without asserting ordinary things are nonexistent or that a personal Form houses the dead Socrates. Reading the death beside the theory is an interpretive choice, not a verified single psychological cause.
4. **Cave and return:** preserve gradual adaptation, painful learning, ridicule, the conditional threat of killing a liberator, the Good, the learner's existing capacity and the return to common life. An echo of Socrates is not literal reportage or an excuse for his execution. Make the contemporary question about the guide's corrigibility explicit.
5. **City and Syracuse:** retain differentiated tasks and the reluctant ruler's public obligation, not just the aspiration to control. Ask who hears a person who cannot be reduced to an assigned role. Qin is a comparison, not historical equivalence. Distinguish the three journeys and two Dionysii; attach the enslavement tradition to the first trip and qualify both ancient testimony and the Seventh Letter.
6. **Critical position:** opposition to finality is argued as the author's philosophical stance, not statistically proved by earlier biographies. Do not infer ontological falsity from an empire's collapse or automatic political causation from later crimes. Do not attribute philosophical disagreement to a psychological diagnosis.
7. **Teacher/student:** the living Socrates' response is unknowable. Keep the Parmenides' substantive challenges about the scope of Forms and participation. Neither wholesale abandonment nor knowingly clinging to error follows automatically. Confucian transmission also includes selection and development, not mere recording.
8. **Inheritance:** retain Aristotle, Hegel and Kant while declining the one-building account as literal history. Hume's inference, Schopenhauer's wanting and debt to Plato, and Kierkegaard's existing individual receive separate treatment. They are not three witnesses for one slogan.
9. **Academy/bridge:** distinguish an intellectual tradition from uninterrupted institutional identity up to 529, and legendary mottos/death stories from verified scenes. Preserve the roughly eighty-year life and continuing dialogues. Mark the bridge explicitly as invented: the person whose life does not fit the drawing can speak, and Plato looks up to listen.

## Sources actually checked

- [Plato, Phaedo](https://classics.mit.edu/Plato/phaedo.html), especially the narrative at 59b and final scene; public-domain Jowett translation.
- [Republic VII](https://classics.mit.edu/Plato/republic.8.vii.html), cave, adaptation, education and return. Also consulted the retrieved text of [Republic V](https://classics.mit.edu/Plato/republic.6.v.html) and [Apology](https://classics.mit.edu/Plato/apology.html).
- [Parmenides](https://classics.mit.edu/Plato/parmenides.html), the young Socrates' account of Forms and the ensuing challenges.
- [Diogenes Laertius, Book III](https://en.wikisource.org/wiki/Lives_of_the_Eminent_Philosophers/Book_III), including the biographical traditions of death and Sicilian journeys. These are later ancient accounts, not certified contemporary records.
- [Internet Encyclopedia of Philosophy, Plato's Academy](https://iep.utm.edu/plato-academy/), distinction between institutional history and later Platonist teaching.
- [Stanford Encyclopedia of Philosophy, Plato](https://plato.stanford.edu/entries/plato/), the dialogue voices, chronology and disputed correspondence.

A Cambridge book-excerpt PDF appeared in search results but failed to open. It is not represented as a fully consulted source. Neither the original page's named modern biographies nor the complete Seventh Letter was newly read in this pass; the new notes do not claim otherwise. Sources displayed on the six editions have localized labels.

## Language review and extent

All editions retain nine sections. Traditional Chinese preserves **59 source paragraphs**; Japanese, French, German, Spanish and Korean each contain **56** paragraphs. Section organization follows the common narrative map; length does not certify quality.

Body-only counts: Traditional Chinese **3,951** non-whitespace characters; Japanese **4,795**; Korean **4,704**. French **1,919** whitespace-delimited words; German **1,805**; Spanish **1,947**. Each independently rewritten language retains the unfolding scenes, distinctions, comparisons and full ending rather than replacing them with section summaries.

Traditional Chinese was reviewed throughout, including 克里托、那隻雞、記得準、沉思、西西里、身分、證明了、想像、亞里斯多德 and 核實. The parser retains each source paragraph and checks source revision hashes. Only Plato's editorial entry was changed; all 107 other entries compare equal to HEAD.

## Integration and checks

- New editorial source: `data/great-lives/movement-04c-plato.json`. The former collection loses only Plato, retaining the other entry unchanged. Existing article URLs, titles, canonical numbering and movement organization remain unchanged.
- Seven reading pages (shared Chinese/English plus six language pages) updated; six language indexes show 44 full editions. Latest and its ledger share a matching one-article update; historical cards retain their historical counts.
- **120 Great Lives regression tests pass**. Builder check passes for **762** generated/source page outputs. New guards cover the full nine-section map, sustained body/ending, localized sources, corrected claims and Traditional Chinese forms; counts are regression safeguards, not literary certification.
- Source, six editions, six indexes and Latest have balanced markup and unique IDs. Six-edition local links resolve. The 29 Zhuangzi regression tests also pass; its source content is unchanged.
- Search generation/check reports **10,068** source records; each of the eight language indexes changes only its Plato record, with no additions or removals. Sitemap generation/check reports **9,916** canonical URLs, unchanged as a set; lastmod changes only for the seven Plato reading pages and six Great Lives language indexes. Other dates remain unchanged. `git diff --check` passes.
- No browser-rendered visual QA was performed. Structural checks do not establish visual appearance. No commit, push or deployment.
