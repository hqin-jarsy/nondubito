# Ordinary World: editorial scope and reproducibility

## Source and coverage

The five complete Chinese essays were read alongside the five old English essays before drafting. The old English had only eight blocks per essay and was not used as a translation authority. In particular, its opening converted the students’ **nicknames for three kinds of steamed bun** into an invented geographical zoom through continents, country, province and village. The restored editions retain the meal, shame, ranking and two brothers’ contrasted choices.

`source-original.json` preserves the received Chinese and English. `source.json` contains the corrected Chinese, with the same 93 / 123 / 111 / 115 / 129 block positions (headings and terminal bibliography included). Translations follow the full sequence rather than replacing it with a synopsis. A language may store the last bibliographic block in `source_note`; the builder and validator explicitly account for that option.

## Factual corrections and interpretive boundaries

The authorized Chinese and Traditional Chinese revisions are itemized in `../source-corrections.json`; original wording is preserved there. At this stage 43 block positions are revised. The independent primary-text evidence is in `independent-source-review.md`.

Important changes include:

- Brickmaking begins in 1980 and Xiulian’s diagnosis appears in 1985. “Over ten years” at the kiln was removed. The juxtaposition of exhausting labor and lung cancer remains a literary reading, not a demonstrated medical cause.
- Xu Aiyun and her father Xu Guoqiang apply marriage pressure invoking Tian Fujun’s future. Tian Fujun initially does not know the coercion. Xu Guoqiang is not Runye’s maternal grandfather.
- Xiaoxia really does help secure Shaoping’s recruitment to the mine using her father’s name without his knowledge, and proposes asking for a later transfer. The original claims that she never arranged anything, and that he never accepted connected help, were withdrawn. Books, conversation and recognition beyond a job remain central.
- Jin Xiu offers to work at the mine hospital. Lanxiang and Wu Zhongping separately propose a transfer to the provincial capital. Her affection is not silently reclassified as a promotion package.
- Wang Shicai saves An Suozi; Shaoping witnesses the rescue. It is not a personal rescue of Shaoping. The concluding arrival has Huiying, Mingming and the dog, not an invented final spoken line.
- Completion in 1988 and death in 1992 are four years apart. Writing through exhaustion is not presented as proof of a medical cause of death.

The Chinese essays contain strong critical interpretations. Apart from conclusions dependent on the corrected factual premises, these have not been replaced wholesale by a new thesis. Translations mark the readings as readings where needed, especially the claim that the hospital scene interrupts the giving/debt relationship. Disability does not generally remove a person’s capacity to give, love, ask or act. Social pressure against divorce is not converted into a legal prohibition. The counterfactual routes for Xiaoxia and Shaoping are an essay’s structural argument, not a verified assertion that no other couple could have lived differently.

## Rebuild

1. `python3 -B scripts/compile_ordinary_world_english.py` imports the five reviewed English paragraph drafts into persistent `en.json`.
2. `python3 -B scripts/build_ordinary_world_languages.py` renders English into the five primary pages and renders 30 Japanese/French/German/Spanish/Korean article and index pages from JSON. It writes only this series and its profile.
3. `python3 -B scripts/validate_ordinary_world_languages.py` checks source coverage, rendered bodies, alternates/canonicals, local links, analytics, heading structure, documented Chinese changes and nonempty Traditional Chinese mappings for those changes.

The corrective source-preparation script is retained for provenance; it is not part of the normal renderer and does not reset later language edits. Shared navigation, discovery integration, search and sitemap are handled separately by the coordinator.

## Review honesty

Language-specific self-review and independent cross-review files record who read which complete texts and what changed. Their final hashes, not an undated claim of approval, identify the reviewed versions. Structural tests are not evidence of literary accuracy. AI cross-review is not external human native-speaker certification, nor a claim that every reviewer independently reread the whole novel. Browser and responsive-layout validation are recorded separately by the coordinator.
