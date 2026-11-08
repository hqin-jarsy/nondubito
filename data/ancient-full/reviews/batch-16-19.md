# Ancient stories, episodes 16–19: translation review

## Coverage and result

Complete translations and full saved-text editorial review for all four essays in English, Japanese, French, German, Spanish, and Korean.

- Episode 16: 126 source-aligned blocks per language.
- Episode 17: 122 source-aligned blocks per language.
- Episode 18: 128 source-aligned blocks per language.
- Episode 19: 142 source-aligned blocks per language.
- Deliverables: 24 JSON files under `data/ancient-full/translations/`, named `16.LANG.json` through `19.LANG.json`, where LANG is en, ja, fr, de, es, or ko.
- Total: 3,108 translated blocks, corresponding to 518 Chinese source blocks in six languages.

All 24 JSON files parse successfully. Every block matches its source tag and sequence, empty/nonempty status, emphasis-marker count, and Self-as-an-End occurrence count. Each object contains exactly `tag` and `text`. All source paragraphs, separators, titles, and italicized textual-basis notes are retained. No Chinese text was changed in this translation batch.

## Review method

Each translation was composed directly against the complete Chinese source, not from a summary or a shortened intermediary. After saving, all 24 complete translation files were read back in numbered blocks and compared against their Chinese source. Episodes 16–17 also received a printed Chinese/English alignment. The review addressed narrative sequence, agency, qualifications, counterarguments, questions, paragraph rhythm, and closing images as well as structural checks.

Read-back refinements removed awkward literal phrasing and clarified ambiguous pronoun or modifier scope without dropping claims or combining source blocks. Examples include the closing weaving metaphor in episode 16, personhood terminology in episode 17, independent seeing and complete knowledge in episode 18, and distinctions between ethical justification and legal validity in episode 19. Episode 18’s English title explicitly says “Limit Their Sight” to avoid suggesting mere permission.

This is a full-text translation and editorial review, not independent native-speaker certification or a new critical edition of the ancient sources. Primary editions and manuscript claims in the source notes were not independently re-collated. Rendering, HTML integration, and site-level validation fall outside this report.

## Episode 16: Arachne

Preserved the actual weaving contest before its institutional interpretation; the two distinct tapestries; the lack of a technical fault; the destruction and assault; and the later transformation into a spider. Preserved Arachne’s arrogance, the distinction between judging the work and judging its author, Minerva’s genuine expertise, and the warning against automatically treating suppressed criticism as true. The ending preserves the difference between retaining control and answering the work. No substantive source correction identified.

## Episode 17: the wooden people

Preserved both warnings: humanlike performance is not sufficient on its own, while declarations of missing interiority can authorize destructive power. Kept the animals’ and objects’ counterclaims, the distinction between reversal and justice, the questions about collective destruction and creators’ responsibility, and the caution against treating a particular K’iche’ narrative as all Maya belief or as a direct modern technological analogy.

Minor source wording: zero-based JSON block 71 (72nd array item), a p block, reads “创造者既然知道这次造物没有形成所期待的心智，为何直接毁弃，而不是改变条件、教导或重新关系？” Block 70 asks “他们缺少理解，是自己的选择，还是创造本身的限制？” and block 72 says “这些问题在文本中没有得到回答。” The phrase “重新关系” is compressed wording, not an established substantive error. Translations render its evident sense as forming or establishing a new relationship. Chinese remains unchanged.

## Episode 18: the maize people

Preserved successful creation, near-complete vision, the creators’ anxiety, and the misted-mirror restriction before the philosophical discussion. Kept the paired warnings: finite perspective may make relationships and inquiry necessary, yet those benefits do not automatically justify limits imposed to preserve hierarchy. Preserved the four men’s exclusion from the decision, the refusal to invent their earlier communal life, and mutual need as a possible consequence rather than a certainty. No substantive source correction identified.

## Episode 19: Isis and Ra

Preserved the full causal sequence: Isis makes the snake, places it on Ra’s route, then demands the secret name as a condition of healing. Kept the distinction between consent under pressure and absence of all agency; between knowledge and control; between explaining a weaker party’s tactics and excusing harm; and between genuine healing and justification of the situation that made healing necessary. The later ritual context is retained, including the explicit warning against equating a divine name with a modern password.

Optional interpretive wording note, not a mandatory correction: zero-based block 100 says “这件事使她与单纯的勒索者仍有差别。” It follows blocks 98–99, where Isis receives the name and keeps her promise rather than letting Ra die. Extortion can also involve fulfilling a promise, so fulfillment alone is not a categorical distinction from extortion. Here “单纯” supports a narrower rhetorical reading: Isis is not reducible to that single role. Translations preserve “mere,” “simple,” or the equivalent qualification, along with blocks 103–108, which explicitly deny that fulfilling the bargain justifies its creation. No factual error is established and no Chinese revision was made.

## Combined editorial assessment

The four essays retain distinct stories rather than becoming repetitions of a generic critique of power. Episode 16 separates evaluation from punishment; episode 17 keeps recognition and exclusion in tension; episode 18 examines both the constitutive and hierarchical roles of limits; episode 19 separates real care from manufactured dependence. Counterarguments remain visible in each essay, and the endings retain their questions, qualifications, and concrete images.

Names and recurrent concepts are consistent within each language. The wooden and maize people use matching terminology across episodes 17–18. Ra is localized conventionally as Rê in French and Re in German, while English and Spanish retain Ra; Japanese and Korean use their standard transliterations. No protected Self-as-an-End wording was translated.

No translation files remain pending in this batch. All 24 files passed the final structural validation after editorial changes. Only these translations and this review were edited; no HTML, build scripts, or git operations were part of this batch.
