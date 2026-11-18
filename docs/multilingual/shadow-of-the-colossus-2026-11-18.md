# Shadow of the Colossus multilingual expansion — 2026-11-18

## Scope and source review

Three essays. Existing simplified/traditional Chinese and independent English are retained and locally corrected; Japanese, French, German, Spanish and Korean cover the full corrected Chinese, not the shorter independent English. No push.

Corrected Chinese has 326 units (104 / 104 / 118), with all original positions preserved. The ledger records 69 changed positions, including repeated facts and dependent wording, not 69 separate discoveries. Final source SHA256: `00583d7d6fbe984de01ad63b0a78bbb1a523ea60b6c0f9bfa291cdc22c9a9d7a`. Original source remains in `source-original.json`.

English retains its 101 original units (34 / 32 / 35), with 12 local corrections rather than a paragraph-aligned rewrite. Final SHA256: `e721c602894d107cb2594efe27c966241ab6406efc2732abf87bb978de15f9e6`. All three English essays and all 326 corrected Chinese units were independently read.

Representative factual and dependent corrections:
- The game speaks names such as Dormin; it is Wander and Mono whose names are not explicitly introduced in dialogue. Mono's gradually audible voice is not the same as participation in the bargain, nor proof that a particular name was audibly called.
- Emon performs the ending seal, but is not established as the person who performed the ancient first sealing. Parallels among taboo, classification and exclusion remain readings, not a newly invented fully documented doctrine.
- Agro throws Wander to safety before falling with the bridge fragments. The horse survives injured; the account does not invent a death and resurrection.
- The horned infant is Wander. Mono's act of care remains the ending's focus; the young man no longer stands beside her in his former shape, rather than simply ceasing to exist. No theory of unpurified residue or a new infant identity was added.
- Final resistance to the seal is player-controllable, not a uniquely fixed cinematic path. The high garden can be reached through optional exploration, though it is not a goal on the giant-killing list.
- Unverified exact heights, precise ancient ages, sacrificial-site theft, and absolute music/camera claims were removed or narrowed. The thirteenth giant is one completed item, not one third of a sixteen-item list. Phalanx is described as a common name rather than an official individual name.

## Evidence and limits

The source audit and independent review record distinctions between released-game script, official guidebook/artbook material reproduced through a transcription/translation mirror, and abandoned ending concepts. The director's statements establish the infant's identity and the injured horse's survival; unused dialogue was not silently treated as released dialogue. No fresh full playthrough, complete frame-by-frame review, native-human review or scholarly certification is claimed.

Primary mirrored materials consulted:
- [Director interview](https://glitterberri.com/shadow-of-the-colossus/artbook/the-ending-made-clear/)
- [Guidebook story synopsis](https://glitterberri.com/shadow-of-the-colossus/artbook/story-synopsis/)
- [Artbook character pages](https://glitterberri.com/shadow-of-the-colossus/artbook/character-pages/)
- [Script comparison, with unused material explicitly distinguished](https://glitterberri.com/shadow-of-the-colossus/script-analysis/unused-text-in-the-ending/)

## Integration verification

All six English/new-language editions passed independent full reading, including metadata. JA and FR retain 326 body units; DE, ES and KO retain 323 body units plus three separately rendered source notes. Independent local fixes: JA 4, FR 16, DE 2, ES 8 and KO 19. Final review hashes match actual frozen source and target files; author self-review history is retained with a link to the subsequent independent review.

- 24 HTML pages, including 20 new language pages; all prose rendered, 387 local links valid, one canonical and eight language alternates on each page.
- Eight-language selectors, language-channel entries, game category, Library, Home, Latest, update ledger, search and sitemap synchronized. Existing shared descriptions remain accurate and were not gratuitously rewritten.
- 64 isolated offline browser cases across all eight language views at 390 px and 1440 px; no overflow or selector failure. The mobile screenshot was visually inspected for readable line wrapping and spacing.
- All 24 HTML files byte-identical after a repeated normal build; connector and scoped discovery check modes pass.
- Unrelated search entries and sitemap dates preserved against preceding commit `dbcb5bc`.
- 19 existing reader/supplement/home/sitemap regression tests pass. Whitespace checks pass.

Mechanical coverage is not a replacement for the full editorial readings above. No native-human or scholarly certification is claimed. No push.
