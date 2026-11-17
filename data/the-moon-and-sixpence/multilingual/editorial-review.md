# The Moon and Sixpence: editorial review

Date: 2026-11-17. Scope: four English restorations, five complete new language editions, and narrowly sourced Chinese factual errata. No commit or push performed by this series worker. Shared discovery changes belong to the coordinating worker.

## What was actually reviewed

The authoring AI read all four Chinese essays and their old English versions, then wrote complete English prose restoring the scenes and arguments omitted by the former short adaptations. It wrote and read Japanese, French, German, Spanish, and Korean against that corrected English and the Chinese scene/argument structure. Paragraphs are merged and rephrased for readable prose: this is **not** a one-to-one Chinese-paragraph translation claim. The six new drafts do share 32 / 39 / 35 / 33 blocks, including headings, as an auditable alignment aid, not as evidence of quality by itself.

The coordinating AI independently read all four English essays against all four Chinese originals. A second AI read all four French essays against the Chinese and corrected English. A third AI read all sixteen Japanese, German, Spanish, and Korean essays against the English, also read the four Chinese essays, and independently opened the source-novel passages below. These are actual additional model reviews, **not** native-speaker certification or independent scholarly review.

Issues found and fixed in that review:
- Removed explicit drafting/correction commentary from all six prose editions. The corrected events now appear naturally; the audit trail lives here.
- German: `Kinderwunsch` (desire to have children) corrected to `Wunsch aus der Kindheit`.
- Korean: `법원의 결심` corrected to `법원의 최종 판결`; ambiguous `먼 곳의 시정` replaced by `먼 곳의 시적 동경`; painting *the walls* made unambiguously painting *on* the walls.
- Spanish: clarified that the nude was painted in Stroeve's studio; `deseo de infancia` replaces potentially ambiguous `deseo infantil`.
- French: final agreement corrected to `Ces deux choses sont vraies. Elles...`; the son's interpretation of punishment is now `son récit du châtiment`, not a phrase that could imply punishment of the son.

## Verified factual errata and evidence

Primary evidence is Maugham's novel, read in public-domain English transcription. These are factual checks, not third-party interpretations of the novel.

1. [Chapter XII](https://en.wikisource.org/wiki/The_Moon_and_Sixpence/Chapter_XII): Strickland wanted to paint as a boy; his father directed him into business; he attended evening classes for a year while his wife thought he played bridge. The Chinese statements that he had no training, no childhood interest, and nobody had prevented him were corrected. Only the directly dependent categorical sentence about occupying none of the dream-story's stages was minimally qualified. The private necessity argument remains. Seventeen years describes the marriage, not an established duration of stockbroking.
2. [Chapter XXXIX](https://en.wikisource.org/wiki/The_Moon_and_Sixpence/Chapter_XXXIX): Stroeve seizes a large **scraper**, not an axe. A **dinner knife** appears in his later reenactment while telling the narrator. All Chinese axe references became 刮刀. Strickland gives him the single painting of Blanche; Stroeve takes his pictures home after selling his household belongings. The Chinese claim about shipping a whole abandoned Strickland collection was replaced with the supported events.
3. [Chapter LVI](https://en.wikisource.org/wiki/The_Moon_and_Sixpence/Chapter_LVI) and [Chapter LVII](https://en.wikisource.org/wiki/The_Moon_and_Sixpence/Chapter_LVII): Coutras sees the mural-covered rooms and learns that Strickland had been blind for almost a year. Chapter LVII explicitly describes him sitting blind in rooms he had already painted. The Chinese account of painting the murals by memory and touch after blindness was corrected. Ata and Coutras did see the murals; “nobody had seen them” was corrected. Other pictures survive, including the still life shown to the narrator.
4. [Chapter LVIII](https://en.wikisource.org/wiki/The_Moon_and_Sixpence/Chapter_LVIII): Robert appears in khaki and a parson's collar. Chinese now specifies a military clergyman, not merely an undifferentiated soldier. The mills-of-God saying is treated ironically as something the family may *mistake* for Scripture, not an actual biblical quotation. Corresponding Chinese references were corrected.
5. The departure letter's dinner arrangement is prospective, not a statement that dinner is already cooked. Chinese now says it will be ready on the wife and children's return. The English text is available in [Project Gutenberg's complete novel](https://www.gutenberg.org/cache/epub/222/pg222-images.html).

Traditional Chinese: existing curated variants were retained; newly changed text nodes received offline macOS Hans–Hant conversion. Every Chinese body text node is covered by the corresponding dictionary in the static test. Old unused dictionary entries can remain and are not rendered.

## Interpretive boundaries

The Chinese argument remains the author's argument. Except for the direct consequences of the verified childhood/training facts, this pass did not broadly rewrite Chinese judgments or turn them into academic caveats. In particular, categorical interpretations of Stroeve's forgiveness, the uniqueness of his recognition, the origins of necessity, and the significance of the burned mural remain in Chinese. Their status as interpretation should not be mistaken for checked plot fact.

The new prose editions qualify these carefully: the stopped blow need not settle forgiveness (Stroeve later invites Strickland to Holland); admitting the sick man is part of a causal chain, not proof that Stroeve alone caused Blanche's death; Strickland's account of what he promised is not an independent acquittal; the fire removes this final work's public future, not the usefulness or survival of all his art. These qualifications preserve the central non-offsetting argument without relying on unsupported absolutes. They are disclosed here rather than silently called literal translations.

Dialogues are paraphrases, not quotations borrowed from identified published Japanese/French/German/Spanish/Korean translations. Chinese names follow the existing Fu Weici convention.

## Coverage by essay

1. Departure letter, forty-year-old broker, wife/rival explanation, shabby Paris lodging, family and public opinion, childhood and evening study, drowning comparison, preference/ambition/authority distinctions, dream-story audience, mural destruction, apocryphal moon slogan, wife's typing business, introduction of Stroeve.
2. Blanche's nude and death, ridiculous painter and discerning eye, sickness and wife's refusal, nursing, departure and leaving the apartment/money, hospital refusal, scraper scene and dinner-knife retelling, single gifted painting, non-offsetting beauty and harm, no guaranteed reward, kindness overriding a refusal, transition to accounting defence.
3. Strickland's response to the death, genius-cost balance, no promise of compensatory masterpieces, no application for exemption, Tahiti/illness/Coutras, murals then blindness, Ata's promise and fire, survival of other work, completion without public inheritance, no purified excuse, unresolved judgment, first/second distinction.
4. London visit, typing business and inheritance, fame and reproductions, military clergyman and misattributed saying, society's domestication of the story, Ata's son as contrast, own necessity versus others', no total-human scorecard, both harm and necessity fully stated, limits of kindness and intelligence, Stroeve's stopped hand, conclusion without offset.

## Reproduction and checks

- Drafts: `data/the-moon-and-sixpence/multilingual/{en,ja,fr,de,es,ko}.txt` (`@@slug`, blank-line-separated prose).
- `python3 scripts/build_moon_languages.py` builds durable JSON, profile metadata, repaired English bodies, language controls, and 25 standalone localized pages using the Moon-specific adapter.
- `python3 scripts/repair_moon_source_facts.py` applies idempotent narrow Chinese corrections and adds new Traditional variants. Uses the existing repository's offline macOS converter; do not use it as a general essay rewrite.
- `python3 scripts/test_moon_languages.py` checks all 30 HTML pages, 490 local links, eight alternate language routes per page, canonical uniqueness, lang attributes, exact rendered-body agreement with drafts, source-fact regressions, and Chinese text-node coverage. Results: `validation.json`.
- `git diff --check` passed for this series and its dedicated scripts.
- Two consecutive builds were byte-identical across the series HTML/Traditional data and generated JSON (43 files checked at that point).
- No visual browser/viewport inspection was performed by this worker. Pages reuse the existing literary responsive template; structural checks are not a substitute for visual or human literary review.

Deliverable: 4 restored English essays plus 20 new complete essays and 5 localized indexes. Shared navigation, search, sitemap, and activity integration are intentionally left to the coordinator, using profile.json and discovery.json.
