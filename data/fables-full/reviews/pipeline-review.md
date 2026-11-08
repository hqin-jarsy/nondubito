# Independent Fables pipeline review

Reviewed 2026-11-08. Engineering review only; this is not an independent native-language editorial review. No translation or source files were changed by this reviewer.

## Findings and repairs

1. **Language query was not retained through reading navigation.** With stored Chinese, German essay 01 → EN correctly opened the English text, but Next opened essay 02 in Chinese. The primary bootstrap consumed `?lang=en` without saving it. The integrator added valid-query persistence in both existing storage keys. Independently retested in Chrome for EN, Simplified Chinese, and Traditional Chinese: foreign-language entry → Next → Previous → series index → card all retained the selected language.
2. **A language-button change was lost on reload.** Entering `?lang=zh-hant`, choosing EN, then reloading restored Traditional Chinese because the old query remained in the URL. The integrator synchronized the query using `history.replaceState`. Independently retested all three primary modes through toggle → reload → Next → browser Back. Unrelated query parameters, fragment, history state, and history length were preserved.

No further confirmed integration defect was found in the reviewed code and focused probes. The previously identified foreign-index Stories-back correction is present in the renderer; the final build/browser run must verify its generated pages.

## Independently verified coverage

- Read CLAUDE.md, the Fables renderer and Python/browser tests, manifest, README, source-correction receipt, source questions, shared Epic rendering/navigation helpers, search builder/parser, and relevant CSS.
- All 144 original snapshot files are byte-identical to the recorded baseline Git commit, in addition to passing manifest hashes.
- All 48 primary Chinese regions (23 essays plus index, Simplified and Traditional) match their preserved snapshots with only the recorded episode 06 missing-negation correction. All 23 extracted source bodies match their expected Chinese DOM. The preserved original episode 06 source hash and exact correction passed. Episode 20 text 90 remains unchanged.
- At the last input checkpoint, 137 existing arrays were verified: 23 each in English, Japanese, French, German, Spanish and 22 in Korean. Every paragraph rendered with exactly the supplied text; paragraph, quotation, separator, emphasis, and line-break counts matched the Chinese source structure. The missing final Korean input was expected ongoing work, not a defect.
- For those 137 editions, the prose guard accepted the existing original/current title and body, then rejected independent injected manual-title and manual-body edits: 274 rejection probes. Probes were in memory and did not alter HTML or translations.
- The current public file set exactly matches the 144 expected paths. All 144 canonical URLs and all 3,036 local href/src targets resolve correctly; index directory canonicals were treated as equivalent to index.html.
- The scoped search refresh preserved every unrelated record, its order, and index metadata across all eight indexes. Each language retained the same 24 Fables routes.
- Chrome probes blocked every non-local request. The two language-navigation regressions above were reproduced before repair and passed after repair.

## Remaining final-run boundary

The complete final build, full 138-translation unit suite, final rebuild-idempotence check, generated search-title comparison, and full desktop/mobile browser matrix were intentionally left to the integrator after the final Korean input. This reviewer did not duplicate the full browser run or claim its responsiveness/screenshots were independently verified.

No commit, push, or publication was performed.

## Follow-up: hero-subtitle contrast

The integrator spotted a dark subtitle in the Japanese mobile screenshot after the first full browser geometry run. Computed styles confirmed the shared `.story-deck` rule was applying #4a4a42 text on the #1e4035 article-head background: 1.28:1 contrast. The same structure appears on all 115 Japanese, French, German, Spanish, and Korean articles. English and both Chinese article modes have no such subtitle.

Applied the minimal fix in the Fables renderer only: `.article-head .story-deck{color:var(--cream)}`. This leaves the indexes, shared site CSS, typography, and geometry unchanged. Added `assertHeroDeckContrast` to the browser suite, requiring at least 4.5:1 for every visible article-head subtitle at 1440, 390, and 320 pixels. The final JSON now includes `heroDeckChecks`, expected to be 345 after the full run.

Focused Chrome validation used the actual new regression helper on essay 01 in all five affected languages at all three widths. All 15 unpatched cases failed and all 15 CSS-preview cases passed at 10.06:1. Title, card, subtitle, and body bounding boxes were identical before and after. The Japanese index subtitle retained its original color. All three primary-language views had no affected subtitle. The corrected Japanese 320-pixel screenshot was inspected visually at `/tmp/fables-full-ja-mobile-contrast-fixed.png`. JavaScript and Python syntax checks passed.

No pages were rebuilt during this follow-up, avoiding interference with concurrent Korean prose edits. The integrator owns the single final rebuild and full browser rerun against generated files. Only the renderer CSS, browser test, and this review report were edited by this reviewer.
