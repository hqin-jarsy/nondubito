# Foundation Paper 6 v2: reader-facing synchronization

Editorial date: 2026-09-19.

## Source and scope

The author confirmed that the corrected paper was pushed to Self-as-an-End.
The live HTML at <https://self-as-an-end.net/papers/sae-institution.html> was checked directly, because the web reader initially returned an older cached edition. The Chinese community paragraph now locates cohesion in the community's intrinsic value rather than enforcement. The company appendix now separates rights from role accountability and identifies the founder's heavier accountability as a design choice, not a proportionality theorem.

The source for this revision is §§1.3, 3.3, 5.2, 7 and the explicit v1–v2 version note. No changes were made to the paper repository.

- Essay 12: revise only its final section, preserving the preceding three sections, title, metadata, navigation and source links. Simplified Chinese and independent English, Traditional Chinese mapping, and independently edited Japanese, French, German, Spanish and Korean are synchronized.
- Essay 13: revise one paragraph in Chinese/English and one in each of Japanese, French, German and Spanish; update its Traditional Chinese mapping. Korean has no corresponding obsolete claim and is deliberately unchanged.
- Preserve ordinary references to parents' responsibilities and the optional essays' lack of additional ethical duties. This is not a global replacement of words meaning duty or obligation.
- No new essays, language editions, URLs or Latest publication entries. The changes affect 11 HTML files and two Traditional Chinese maps. The existing structure of the five foreign-language editions is unchanged; patching also added missing final newlines.

## Editorial boundaries

The revised section begins with someone responsible for a work schedule or shared rota, not a taxonomy. A role may require records, reasons and review. These demands are distinct from a person's own self-given duty, even when both concern the same act. An enforceable requirement does not thereby become justified or become the member's own law.

Leaving the role terminates the continuing and new demands supported by that position. It does not erase past action or omission, or cancel scrutiny or remedies resting on independent grounds. Leaving the position does not by itself discharge a duty under one's own law; this is not a claim that every particular self-given rule must remain forever unchanged.

Rights are not payment for performing duties. Effective protection, a genuine position from which to refuse and exit, and the limits on role demands must be checked separately. These are necessary checks, not an exhaustive account of legitimacy. Greater outward power does not automatically establish actual scrutiny: specific mechanisms are needed. Where foreign-language prose retains the paper's stability prediction, it is explicitly an empirical prediction rather than a proven structural theorem.

Traditional Chinese changes were generated offline and then read and edited, including 複核 and 抵帳. Existing translations outside the changed text were preserved. Both script references have a new cache version. No external translation service was used.

## Verification

- Independent read-only review of the complete Chinese and English essays and the changed Essay 13 passages found no remaining conceptual correction required. The main editor reviewed all five foreign-language changes.
- Seven focused tests in `scripts/test_institution_revision.py`: article structure and language, canonical/source/local targets, all existing language routes, exclusion of withdrawn pairing claims, explicit accountability/exit boundaries, full Traditional Chinese body-map coverage, and search/sitemap inclusion.
- Node syntax checks for both changed Traditional Chinese scripts; `git diff --check`.
- A separate comparison against the clean initial HEAD verified that Essay 12 changes are confined to its final section and Essay 13 changes to one paragraph per affected body. The only changes outside prose are the two intentional script cache versions and final newlines. Korean Essay 13 is byte-for-byte unchanged.
- Rebuilt all eight search indexes and the sitemap: 9,996 search records and 9,844 canonical URLs, with no additions or removals. Search changes are limited to the revised Essay 12 heading in each language. Sitemap changes are limited to the 11 revised pages' modification dates.
- Browser checks: one visible body per Chinese/English mode, correct revised Traditional Chinese text without Simplified Chinese fallback, reversible switching, and Traditional Chinese retained on navigation from Essay 12 to Essay 13. All five foreign-language pages load their revised headings without page overflow at the desktop width. Desktop Traditional Chinese and narrow-screen Korean body text were visually inspected; the temporary viewport is restored after testing.

No commit or push is performed by this task. No Git lock was removed or altered.
