# Gone with the Wind: eight-language edition

Four essays, 122 / 162 / 162 / 190 Chinese blocks, with five complete new-language editions. English remains its 108-block independent essay sequence, not a forced paragraph-by-paragraph rewrite. Each language has a full-read independent receipt. Exact final manuscripts and original primary-page hashes are retained.

## Corrections and their boundaries

The source review checked particular disputed scenes against the novel, not every sentence against every edition. Corrections distinguish novel from film: the party dress is jade-green watered silk; the hunger scene takes place at ruined Twelve Oaks, involves a radish, and the vow follows her standing up. The novel names stealing and killing. Lying and cheating remain the essay's subsequent classification of her conduct, not words inserted into that vow. Recaps were synchronized.

Other repairs: first-mill financing comes from Rhett's loan; marriage to Rhett follows Frank's death by almost a year, not weeks; Scarlett disposes of the soldier's body while Melanie cleans blood; Wade is among the escape passengers; Melanie's care for Scarlett's children replaces a reversed claim about why she stayed during the siege. The story runs from sixteen to nineteen at the hunger scene, not four elapsed years; an already-thirty-year-old method is removed at age twenty-eight. Social preparation is distinguished from an absolute legal inability to inherit. Mammy's caregiving role does not prove lactation or childbirth, so the questions about her own family no longer assume that.

The final source echo only synchronizes Chinese IV's “family” and English IV's “family life.” Translations already used this narrower reading. `final-source-echo-review.json` preserves the previous and final source hashes; earlier full-read receipts plus this exact delta describe the real review, without claiming an unnecessary fresh full review.

## Reproduction and validation

Run `scripts/build_reviewed_literary_languages.py gone-with-the-wind`, then `connect_full_series_languages.py gone-with-the-wind` and `refresh_literary_discovery.py gone-with-the-wind`. The renderer preserves source emphasis explicitly and fails on changed inline markup lacking a reviewed mapping. The corresponding `validation.json` records final checks and their limits. No push or publication is included.
