> Final update 2026-11-08: All approved primary-language corrections and the separately authorized local five-language integration are complete and verified. This is a historical checkpoint; earlier pending or paused descriptions are no longer the current status. See release-summary.md for the final scope, checks and limits.

# Approved primary-language film revisions

Status: Chinese, Traditional Chinese and English corrections complete locally; foreign-language integration remains paused. No commit or push.

The author approved the previously proposed film correction directions on 2026-11-08. Six affected essays now contain only the bounded revisions below. All nine complete English essays remain in place, with their sections, emphasis, closing notes and prose rhythm preserved.

- Raise the Red Lantern: nine paired edits across three essays. Doctor Gao diagnoses the false pregnancy rather than assists it; Meishan has a son; sons are leverage rather than protection; leaving the gate differs from escaping the rules; Zhuoyun's earlier arrival is relative to Songlian; she cries out when cut; questioning and repeated commands do not become equal dialogue; the opening road is stated as an exception.
- Dead Poets Society: two paired edits in essay one. Neil's forged consent is an earlier action, not a consequence of Keating's advice. The distinction between encouragement and a workable way forward remains.
- Parasite: five paired edits across essays one and two. The brief inquiry about the former driver, unverified reassurance and retreat to family concerns replace absolute claims that the Kims never thought of the displaced people. Responsibility and limited vision remain the argument; no explanatory footnotes were added to the essays.

## Preservation and review

All 16 corresponding Chinese/English edits were independently checked against their approved directions and surrounding argument. The per-film JSON files record exact before/after phrases. Chinese page bodies equal their original committed versions plus those recorded replacements, with no other prose edits. The Traditional Chinese dictionaries changed only 19 corresponding text nodes across six files; all unrelated mappings were preserved. Other scene-level uncertainties remain unchanged and are not presented as newly fact-checked.

No foreign manuscript or original package note was read or used in this revision phase. The previously paused integration files remain preserved as unfinished work. No new external fact checking or frame-by-frame viewing was performed.

## Verification

- `python3 -B scripts/build_film_primary_editions.py --check`: passed for 12 primary pages and six changed dictionaries; no foreign sources opened.
- `python3 -B -m unittest discover -s scripts -p test_film_targeted_english.py`: two tests passed, including complete structural coverage, exact preservation outside approved changes, and dictionary deltas.
- `scripts/test_film_primary_browser.cjs`: 81 page/language/viewport checks, 13 switch/history/storage-denial interactions, 153 checks that approved Simplified/Traditional/English copy is actually displayed; zero page errors. Desktop and mobile screenshots visually inspected.
- `git diff --check`: passed.
- Foreign generation, eight-language navigation/search, complete film regression and whole-site aggregate checks remain unrun for this unfinished project. No commit or push was made. The local test server was stopped.

## Resumption

Run the primary-only builder above to reproduce these authorized changes without foreign input. Continue the five-language stage only after the parent resolves its source-access scope. Do not describe this partial project as eight-language integration complete or ready to push.

Checkpoint manifest: `primary-approved-checkpoint-hashes.json` (40 files).
SHA256: bef3715633c9e3140a2cae7c5d802869ae62506eba99da977af6e37bad6a9ddd
