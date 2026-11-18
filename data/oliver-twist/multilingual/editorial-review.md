# Oliver Twist: full-language editorial record

## Scope and fixed sources

All four received Chinese essays and all four shorter English essays were read in full. The old English versions each contained eight blocks and were not used as a substitute for the Chinese argument. The restored English and new editions retain the scenes, argumentative transitions, Nancy’s complicity and the final essay’s **nonexchange** reading, rather than replacing that reading with a generic essay about abuse or escape.

`source-original.json` preserves the received text. `source.json` holds the authorized corrected Chinese in the same 105 / 135 / 119 / 143 block positions: 502 total, including headings and final bibliographic paragraphs. A final bibliography may instead be held in `source_note`; the renderer and validator account for either representation. Body length alone is not proof of completeness or quality.

## Corrections to Chinese and Traditional Chinese

`../source-corrections.json` preserves before/after text and reasons for all 110 affected block positions. Many are short dependent references or transitions, not separate factual discoveries. The independent chapter-by-chapter evidence and verification limits are in `independent-source-review.md`. Both original and corrected sources remain in the repository.

Principal factual repairs:

- The workhouse ration includes onions twice weekly, not a second allowance of bread. Physical punishment by the master and Bumble is real; the argument now concerns cruelty coexisting with ordinary procedure, not a fictional absence of cruelty.
- Gamfield’s price is agreed at £3 10s. The magistrate, noticing Oliver’s terror, refuses the indenture. The reported deaths of apprentices remain accusations, not certified recent killings.
- The doctor comforts the mother before her death and comments on the absent ring afterward. Sally steals and later pawns the keepsake, leaving a pawn ticket; she does not retain the original object throughout.
- Fagin deceives Oliver about the handkerchiefs and actually locks him in. Food, shelter, companionship and praise still have force, but they coexist with deception and confinement. The metaphor is “locks doors and dismantles bridges,” not the denial of a locked door.
- Brownlow is uncertain rather than an eyewitness to another boy’s theft. The bookstall keeper provides that evidence; Fang tries to dismiss him, not fine him. Clothes and the five-pound note follow the original division of possession and purpose.
- Nancy’s police errand follows threats and inducements. She remains responsible for active participation, but is not presented as wholly uncoerced. She escorts Oliver to Sikes, not to the burglary itself. The bruises and previous defense are not merged into an invented argument during burglary planning. Bates’s later reform is retained.
- The hotel and bridge meetings are separated. Rose’s compassionate offer starts before complete disclosure; she meets Brownlow afterward. Brownlow’s express overseas offer belongs to the bridge.
- Nancy refuses payment but requests Rose’s keepsake. She limits the disclosure of Fagin’s location; an invented broad demand for courtroom testimony is removed. She expresses attachment, fear and the grip of her old life, not a complete absence of reasons.
- Her final plea asks to survive and points Sikes toward repentance. Their possible better lives would be far apart, without meeting again, not a shared new beginning. Fagin’s warning is linked to caution and self-protection, not an invented narrator’s aside.

## Minimum changes to dependent interpretation

The coordinator approved correction of the premises supporting the final essay, while retaining its central literary claim. Rose’s early concern cannot be rewritten as assistance exclusively earned by information. The revised argument therefore examines the redemptive language within genuine compassion; it does not equate every part of Rose’s offer with Fagin’s transaction.

Nancy does not make helping Oliver conditional upon reward. That is different from saying she receives no gratitude, refuses every object, has no reasons, or would necessarily corrupt her act by accepting rescue. The essay’s reading of nonexchange remains explicit and contestable, alongside her stated attachment. Sikes’s imagined response under a different final encounter is a counterfactual reading, not a proven psychological law. None of these changes transfers responsibility for murder to Nancy.

## Reproducible workflow

- `python3 -B scripts/compile_oliver_twist_english.py`: import reviewed `en-1.txt` through `en-4.txt` into persistent English JSON.
- `python3 -B scripts/build_oliver_twist_languages.py`: render four restored primary English essays and 25 foreign-language article/index pages from persistent JSON. No shared navigation, search or sitemap writes.
- `python3 -B scripts/validate_oliver_twist_languages.py`: verify all 30 public pages, body coverage, heading alignment, canonical/alternate links, local links, analytics and the recorded Chinese/Hant correction scope.

`prepare_oliver_twist_sources.py` is retained to apply the recorded corrections reproducibly; it is not called by the ordinary language renderer. Language drafts, source snapshots, chapter evidence and cross-reviews are necessary build/editorial inputs, not disposable temporary files.

## Review limits

The language-specific self-reviews and independent full-read cross-reviews state their actual coverage, findings and final JSON hashes. English was restored by one writer and independently read in full by the primary-text reviewer. The coordinator assigns full independent readings of the additional editions. Approval refers to the recorded hash, not every future revision.

These are AI editorial reviews, not external human native-speaker or scholarly certification. The primary-text audit covers identified passages, not a fresh line-by-line audit of every statement about Dickens. Structural validation is not a language-quality test. Responsive layout, language switching and shared discovery integration are tested separately by the coordinator before the local commit. Nothing here authorizes a push.
