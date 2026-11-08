# Independent Korean review: Fables 01–05

Reviewed on 2026-11-08 in `/Users/hanqin/Documents/GitHub/nondubito`.

## Scope and method

Read `CLAUDE.md` and the writing-style guidance. Independently read every Chinese source string against its Korean counterpart, in order: 555 of 555 strings, including titles, narrative, argument, emphasized passages, embedded multi-line paragraphs, and all source notes. This is a full bilingual editorial pass, not sampling or a structure-only check. It is not external historical fact-checking or rendered-page/browser QA.

- 01: 91 / 91 strings reviewed; changed indices: -.
- 02: 167 / 167 strings reviewed; changed indices: [108].
- 03: 96 / 96 strings reviewed; changed indices: -.
- 04: 97 / 97 strings reviewed; changed indices: [71].
- 05: 104 / 104 strings reviewed; changed indices: [79].

## Findings and changes

No concrete omission, reversed negation, or mistaken agency was found in this pass. The argument boundaries, caveats, narrative rhythm, and contrast between observed outcomes and warranted conclusions are preserved. Sound sentences were left alone.

Three local fluency repairs were made, using zero-based text-array indices:

1. `02[108]`: `이 결과가 나는 기쁘다.` → `나는 이 결과가 기쁘다.` Reordered the Korean subject and complement naturally without changing the first-person response to the result.
2. `04[71]`: `절차 한 벌이다.` → `일련의 절차다.` Removed a literal Chinese classifier rendering for `一套程序`; the explanation/label/procedure list and meaning are unchanged.
3. `05[79]`: `어떤 것은 정말 더 힘을 쓴다고 얻을 수 있지 않다.` → `어떤 것은 정말 더 힘을 쓴다고 해서 얻어지는 게 아니다.` Repaired the awkward Korean negative construction while retaining the claim that some outcomes cannot be obtained merely by applying more force.

No changes to 01 or 03. No substantive reinterpretations, Chinese edits, or changes to other translations, HTML, scripts, manifests, or indexes. No commit or push.

## Verification

All five Korean files parse as JSON. Counts match the Chinese arrays: 91, 167, 96, 97, and 104 (555 total). The exact sequence of asterisk-marker runs and each paragraph’s embedded newline count match the Chinese source and were preserved from the pre-edit Korean files. Only the three listed array entries changed; 01 and 03 remain byte-for-byte unchanged. All five Chinese source files remain byte-for-byte unchanged. Korean 02, 04, and 05 need re-rendering after these edits.
