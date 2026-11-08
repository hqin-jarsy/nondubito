# Ancient stories 01–05: translation and editorial review

## Coverage and saved-file verification

All thirty full translations are present in `translations/`: episodes 01–05 in en, ja, fr, de, es, ko. Episode 01 has 130 blocks, 02 has 98, 03 has 122, 04 has 131, and 05 has 139: 620 source blocks and 3,720 translated blocks. The complete saved arrays were checked against the Chinese for block count, tag sequence, empty separators, emphasis-marker sequence, and preservation of any `Self-as-an-End` occurrences. All passed. No source block was merged or replaced with a summary.

Episodes 01–04 were translated directly from the full Chinese, block by block in all six languages. A post-translation saved-file comparison reread every Chinese/English paragraph across 01–05; the initially truncated combined display was followed by separate complete reads of 02 and 03. This led to small English fluency refinements, not cuts. The six-language review of 05 also draws on its translator’s complete comparison recorded in `episode-05.md`; this batch review independently reread the entire Chinese/English pair and checked twenty high-risk paragraphs in each of the other five languages. These are translation/editorial checks, not a claim of thirty independent native-speaker copyedits.

## Batch-level editorial assessment

The five pieces remain distinct stories rather than interchangeable philosophical summaries. Short paragraphs, pauses, questions, concessions, and the closing turns remain in their original order. The source’s hedges and counterarguments have been retained rather than replaced with categorical moral lessons.

- **01, Hundun:** Retained goodwill rather than hostility as the source of harm; the transition from difference to presumed deficiency; genuine aid versus remaking; the emergency-protection exception; the cumulative force of seven seemingly small changes; and the refusal to invent Hundun’s own preferences from his silence. EN/FR/JA titles were clarified to mean using one’s own wholeness as a standard *for* others, not a standard others independently adopt. German paragraph 10 was smoothed to avoid a clumsy double negative.
- **02, Pandora:** Retained jar versus later box; creation within Zeus’s prior plan; layered responsibility without either total exoneration or sole blame; the second use of Pandora as a misogynistic example; the refusal to invent a modern resistance narrative; and the explicit admission that Hesiod’s world does not already share the essay’s contemporary judgment. Both Works and Days and Theogony references remain distinct.
- **03, Nachiketa:** Retained the worthless old cows versus genuinely valuable later offers; all three wishes; the first two wishes’ worldly attachments; the distinction between a valuable answer and an answer to this question; the warning that persistence does not prove truth; rewards that need not be malicious; and the absence of any guarantee of a final answer. No generalized ascetic moral or summary of the whole Upanishad was substituted.
- **04, Izanagi/Izanami:** Retained the unfinished joint creation, eating the food of Yomi, her wish to negotiate a return, the specific temporary restriction, the distinction from unrestricted secrecy in ordinary relationships, the partner’s genuine losses, and the possibility of separation even after acknowledging change. Yomi and the Kojiki’s ritual/death context remain explicit. The source wording identified below has now been corrected with the author’s approval.
- **05, Enkidu:** Retained both the civilizing-progress and corrupting-domestication readings without adopting either; loss of the animals and new understanding; incomplete prior consent and the difficulty of consenting to the very capacities needed for consent; opposition to Gilgamesh; friendship and shared violence; curse and blessing; Shamhat’s power and responsibility; and education that must enable refusal and a new choice. Standard and Old Babylonian versions remain distinguished.

## Source issue resolved with author approval

**04, zero-based block 104:** `伊邪那岐的悲剧，或许不只在于他回头看了。`

The wording “回头看” suggests turning back to look. Yet this essay’s own opening at block 11 says he breaks a comb tooth, lights it, and enters to look, and its final source note specifies the Kojiki. The prohibition-breaking discovery in the Kojiki is entering and looking with a light, not a backward glance of the Orpheus type.

Primary-text support: Kokugakuin University, *Studies on the Kojiki*, Chapter 9, translated narrative describes breaking a comb tooth, lighting it, entering the hall, and looking around: https://kojiki.kokugakuin.ac.jp/wp-content/uploads/2025/07/09-Studies-on-the-Kojiki-Chapter-9-The-Land-of-Yomi-1.pdf . Chamberlain’s translation, section IX, likewise has entering and looking: https://en.wikisource.org/wiki/Kojiki_(Chamberlain,_1882)/Section_9 . These sources were found and checked through web search for this specific issue, not for a wholesale rewriting of the essay.

The author explicitly approved the proposed correction: `伊邪那岐的悲剧，或许不只在于他违约看了她。` It is now applied to both Chinese editions and block 104 in all six translations. The following argument is unchanged. `approved-source-corrections.json` preserves the exact approval, original sentence, corrected sentence and six translated changes; immutable original source inputs and snapshots remain unchanged.

The updated translations retain “perhaps” and “not only,” identify looking at her as the breach of the promise, and do not imply a backward glance. A separate six-language sentence review confirmed the wording; English makes the causal relation explicit with “by looking at her,” and Korean preserves the tentative claim with its sentence ending. No other substantive source issue was identified in this batch.

## Limits and integration handoff

All 30 JSON translations are complete. The previously flagged source wording is resolved through the recorded author-approved correction. This review is not a full philological verification of every historical claim against original-language critical editions. HTML generation, browser layout inspection, analytics checks, and site-wide link/build validation belong to the integration stage. No HTML, scripts, or git state were changed during this translation review.
