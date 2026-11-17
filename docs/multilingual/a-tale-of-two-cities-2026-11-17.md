# A Tale of Two Cities: complete literary editions

## Scope

- Four English essays expanded to 893–1,021 words, replacing the former abbreviated bodies.
- Four full essays each in Japanese, French, German, Spanish and Korean, plus five localized series indexes: 25 new pages.
- Eight-way language navigation and alternate metadata on all 30 series pages. Only this series was edited; shared discovery/search/sitemap integration belongs to the coordinating task.
- No commit or push performed by the series worker.

## Editorial method

The published Chinese HTML was read in full. The translations retain the narrative chain and argument, combining the original's short rhetorical paragraphs into sustained prose. They are not paragraph-for-paragraph replicas. English, French, German and Spanish contain roughly 770–1,021 words per essay; Japanese about 1,800–2,050 characters; Korean about 2,200–2,520 characters. Word counts across these scripts are not comparable.

Scene review covered the carriage and returned coin; Gaspard and the gallows; the peasant household and cart yoke; the doctor's complaint and captivity; Darnay's renunciation, Gabelle and both trials; testimony severed from its author; the Defarges' disagreement; Pross's confrontation and deafness; the London resemblance, Stryver and the promise; Barsad's coerced cooperation; the nonconsensual drugging; the seamstress's recognition, hand and final farewell; the narrator's conditional closing vision.

The foreign editions qualify interpretive absolutes where necessary, notably the suggestion that Carton has literally no identity or ties and that no one else bears any cost. The Chinese interpretation has not been generally rewritten. Twelve proposed interpretive adjustments were reverted at the coordinator's request. `source-corrections.json` classifies all 48 proposals and marks the 36 retained factual corrections versus the 12 unapplied interpretive adjustments. Its old/new passages are an audit trail, not additional published prose.

## Source-verified corrections

The public-domain novel, not a plot summary or a modern translated edition, was checked through these chapter texts:

- [II.9, The Gorgon's Head](https://americanliterature.com/author/charles-dickens/book/a-tale-of-two-cities/book-ii-chapter-ix-the-gorgons-head): the return to the château, uncle–nephew conversation and ensuing murder belong to the same evening/night, not months later. The Marquis says he left Paris the previous day, so translations do not assert that the child's death and murder occurred on the same calendar day.
- [III.10, The Substance of the Shadow](https://americanliterature.com/author/charles-dickens/book/a-tale-of-two-cities/book-iii-chapter-x-the-substance-of-the-shadow): the brother takes the younger sister to safety; the husband is yoked and worked to death before the abduction; the doctor is compelled into the carriage, not blindfolded for the medical visit. The brothers' later deaths are not both natural deaths.
- [II.21, Echoing Footsteps](https://americanliterature.com/author/charles-dickens/book/a-tale-of-two-cities/book-ii-chapter-xxi-echoing-footsteps): little Lucie is already six in July 1789; the execution-era child is not five. Exact later age was replaced with “child,” rather than adding unnecessary precision. Carton visits the family and the children are attached to him, contradicting a literal assertion that nobody cares about him.
- [III.8, A Hand at Cards](https://americanliterature.com/author/charles-dickens/book/a-tale-of-two-cities/book-iii-chapter-viii-a-hand-at-cards): Barsad's compromising identities and espionage, rather than merely his sibling relationship, provide leverage.
- [III.13, Fifty-two](https://americanliterature.com/author/charles-dickens/book/a-tale-of-two-cities/book-iii-chapter-xiii-fifty-two): the forced substitution, dictated letter, helpers and seamstress dialogue. The novel does not establish that exposing Carton would save her or benefit her. Her request for courage was previously replaced by a materially different invented question; recognition takes place in the assembly of prisoners before the tumbril journey.
- [III.15, The Footsteps Die Out For Ever](https://americanliterature.com/author/charles-dickens/book/a-tale-of-two-cities/book-iii-chapter-xv-the-footsteps-die-out-for-ever): The Vengeance is an individual nickname, not the name of every knitting woman; the final vision is introduced conditionally by the narrator, not an independently recorded inner monologue or spoken final statement. The seamstress and Carton exchange a kiss and blessings.

Traditional Chinese mappings were updated offline using the repository's existing macOS converter, retaining existing mappings where the text was unchanged and removing unused old keys. New passages were reviewed against the corrected Simplified Chinese for meaning. This is not a claim of independent native-speaker certification.

## Reproduction and checks

```sh
python3 scripts/build_a_tale_of_two_cities_languages.py
python3 scripts/test_a_tale_of_two_cities_languages.py
```

Persistent inputs: `data/a-tale-of-two-cities/multilingual/{en,ja,fr,de,es,ko}.json`. No `/tmp` source dependency. Chinese HTML remains its editable source. `multilingual/profile.json` declares `source_format: literary-html` and supplies the shared integration directory and slugs.

Passed: four articles per language, nonempty prose blocks, every input paragraph present in rendered output, eight alternates per article, 490 local asset/navigation references resolving, and byte-identical second build. `qa-report.json` records per-article sizes. `git diff --check` passed at series handoff.

Independent internal cross-review: separate reviewers read all four essays in each of the five new languages, against the revised English, Chinese and correction log. Each language has a `multilingual/cross-review-*.json` receipt with scope, fixes and the final input hash. Corrections include the seamstress’s recognition before the tumbril journey and her own statement that she is not afraid; explicit uncertainty about any benefit from exposing Carton; the older brother’s sheltering of his youngest sister; named Lucie/daughter references; and local idiom/title refinements. Chinese sibling references were synchronized in three additional locations. All 36 applied factual corrections and every Chinese text node’s Traditional mapping were subsequently checked.

Limits: these are independent AI cross-reviews, not external native-speaker certification. Browser checks are performed by the coordinating task and are not claimed as work of this series worker.
