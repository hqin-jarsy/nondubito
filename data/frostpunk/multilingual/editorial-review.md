# Frostpunk editorial scope and handoff

## Preserved material

- Four complete original Chinese and independent English essays are preserved in `source-original.json`: Chinese 64/63/63/64 (254 blocks), English 19/19/21/24 (83 blocks), including headings and final bibliography.
- Exact original article HTML, including the old edition notes, is retained under `original-html/`; each file SHA-256 was checked against the original snapshot. `index-original.html` and `metadata-original.json` preserve pre-edit index/metadata evidence.
- No English block was removed or added merely to match Chinese. `../english-corrections.json` records every retained original block and its revised counterpart.

## Actual review and material changes

The source editor read all four original Chinese and English essays. Moon independently read all 254 candidate Chinese blocks and reviewed the final 14-block difference. The coordinator also read all 254 candidate Chinese blocks and the remaining changes. English was independently read in full by the coordinator, followed by final local-change and metadata verification. These are editorial reviews, not native-language or exhaustive game-mechanics certification.

There are 103 revised Chinese block positions and 33 locally revised English blocks. These counts are not counts of independent discoveries. Most related changes follow from a smaller set of evidenced corrections:

- Heat is not permanently limited to concentric generator rings. Child shelters and later apprenticeships are distinct. Safe child labor does not directly staff engineering workshops or every dangerous workplace.
- Management foregrounds totals, but building-level choices and help for particular individuals exist. The captain's lack of a managed citizen body is limited to normal management, not a claim that no ending can depict the captain.
- The wall-writing example is the Propaganda Centre's Act of vandalism, not a prison protest. The inspected original-game screenshot shows the two choices and a slight hope increase for removing the writing; the punishment tooltip was not inspected and is not quantified.
- The same signing gesture can precede an overtly violent aftermath. New Faith's night of changes is not described as no scene/no consequence. Replacing Hope does not remove Discontent.
- The final-law discussion is an interpretation of authority and answerability, not an exhaustive certified ending-flag table. Not every successful ending asks whether survival was worth it.
- Winterhome permits authoritarian lawmaking despite the doomed generator. Evacuation uses a land dreadnought with limited capacity, not a guaranteed train to New London. The old assertion that absolute desperation cannot generate overreach is withdrawn with its false factual premise; no opposite claim that authoritarianism saves the city is introduced.

## Evidence boundaries

See `independent-source-review.md` and the archived primary-evidence audits for exact attribution. The source editor actually inspected the full New Faith event screenshot, the Propaganda Centre vandalism screenshot, the limited Winterhome storyboard sheet and the original developer slide 35. Other images are attributed to the colleagues who actually viewed them. No new playthrough, complete video/audio viewing, code audit or exhaustive ending algorithm verification is claimed. Game names and meaningful translations do not certify every phrase as official localized UI dialogue.

## Frozen source and English

- Chinese source SHA-256: `5d2c81df235859906cb43d3c3a2a0b36fc4f7c45b0618bfda4fb8cda26625d33`.
- English SHA-256: `dc3aa528e8a11a7f36deef315f9a54fbae4fe76ed640593837b50aeac3fc4ecf`.
- New five-language manuscripts are translated from the frozen Chinese, not by extrapolating from shorter independent English.

## Pre-build checks completed

Actual checks passed for primary Chinese equality with source (254 blocks), English prose rendered in the primary pages (83 blocks), all 103 changed Traditional-Chinese mappings, Python syntax, and `git diff --check`. The dedicated full validator additionally covers language coverage, heading positions, English block mapping, metadata, shared-summary correction assertions, alternate/canonical links, local links and analytics. Full multilingual build and browser QA are pending the remaining manuscripts; these are not represented as already passed here.
