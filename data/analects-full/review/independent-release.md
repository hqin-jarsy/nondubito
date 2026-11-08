# Independent Analects full-edition review

Reviewed 2026-11-08 in nondubito; supplied baseline 10bfd10ee. Read CLAUDE.md and SAE-TERMINOLOGY.md. Reviewer changed no canonical manuscript, builder, generated page, or Git state.

## Substantive coverage

Full Chinese–English comparisons completed for 21 essays:
- One in five: 01, 06, 11, 16, 21, 26, 31, 36, 41, 46.
- Additional high-risk: 03, 04, 19, 20, 35, 37, 39, 44, 48, 49, 50.

Compared data/analects-full/chinese/NN.md with english/NN.md, alongside source-corrections.json and review/source-issues.json. The reviewed essays retain their arguments, examples, rhetorical movement, endings, and qualifications. They are complete essays rather than summaries. No unresolved translation blocker remains in this sample. This is not independent literary certification of all 300 translations.

## Findings and fixes

1. English03 initially weakened “六艺里排在最末的一项” to “One of the practical Six Arts,” silently correcting an unresolved author claim. Reported immediately. Final draft rechecked: “The last-ranking of the Six Arts.” The underlying claim remains an author-decision issue; this review does not authenticate it.
2. Legacy main() write loops initially failed to advance last-build.json after rendering complete editions, potentially rejecting a later legitimate canonical edit as an outside page change. Reported; fixed by shared write_outputs() with merged per-file receipts. Inspected both legacy main() functions and the helper after the fix.
3. Legacy renderers initially fell back to summaries if manifest.json was missing. Reported; both now delegate unconditionally. Independently mocked the manifest reader to raise FileNotFoundError and confirmed both entry points fail closed.
4. Source-note research titles varied across batches (Reading/Interpreting; Scene/Scenes/On the Scene; Vein/Veins). Reported. Lead is normalizing to Interpreting the Analects: Legislation / The Vein / On the Scene / Discernment / The Cultivator and making plain DOI URLs clickable. Final normalization remains an integration check.

## High-risk review notes

- 01: distinct names and the three separately addressed prescriptions remain intelligible.
- 04: approved teacher–student exchange correction incorporated; Zengzi supplies the “wholeheartedness and reciprocity, and nothing more” explanation.
- 19: ruler-addressee reconstruction and Laozi assertion preserve source force; their historical support remains an author-decision question.
- 20: new-reading label, three interpretive changes, lack of supporting variant manuscripts, inference/proof distinction, potential archaeological refutation, and reader's judgment remain explicit.
- 21: preserves the distinction between revisable scaffolding and a checklist treated as final authority, rather than declaring all positive lists bad.
- 31: preserves the asserted bird-flight etymology without silently substituting a different account.
- 35: both historical-use assertion and absence-of-evidence caveat survive; their registered tension remains.
- 36: distinguishes remembering predecessors from exclusive succession, content from later use, and interpretation from authorship judgment.
- 37: strong opposition to gender-essentializing readings survives alongside uncertainty over attribution and refusal to choose one uniquely charitable reading.
- 39: broad no-questioner claim and discussion of 16.1 both survive. Registered scope tension is not silently repaired.
- 41: possible misuse is not grounds for preemptive condemnation; ten/five/four overview remains the source's unresolved accounting.
- 44: praise of specific Zengzi sayings and later blanket non-use claim remain, with their registered tension intact.
- 46: Guan Zhong chronology correctly says more than a century earlier.
- 48: gatekeeper, not Confucius, is credited with “knows it cannot be done.”
- 49/50: “There is no way to follow” attributed to Yan Hui. Essay49 retains literary-juxtaposition versus causal-proof caveat; essay50 retains possible refutation and revision of individual judgments.

## Independent read-only implementation checks

Read complete renderer, legacy entry points, and regression/browser test code. Executed:
- All255 foreign outputs rendered with immutable hash verification and overwrite protection.
- All250 foreign H1, meta descriptions, OG descriptions, and applicable JSON-LD headlines matched canonical title/deck: zero discrepancies.
- All250 foreign previous/next labels and targets matched adjacent canonical essays: zero discrepancies.
- Both legacy renderers failed closed under missing-manifest simulation.
- Once all50 English drafts arrived, all306 pages rendered successfully in memory.
- All300 foreign-language H1s matched canonical manuscript titles.
- All100 simplified/traditional Chinese article regions equaled snapshots plus exactly the recorded corrections.
- All306 pages had one analytics beacon; all JSON-LD parsed; every relative href target existed locally. Zero failures.

Escaping occurs before Markdown substitutions. JSON-LD replacements are parsed and reserialized. Immutable source snapshots and received manuscripts are digest-checked. Existing pages are protected against unrecognized outside edits.

## Release boundary

These independent checks inspect rendered outputs in memory. Reviewer did not run the browser suite or write generated pages. At the last on-disk --check before the lead's integration rebuild, 51 primary pages were stale as expected immediately after English drafts arrived.

Before committing, lead must finish bibliography normalization, rebuild pages/discovery data, and obtain green final on-disk regression, analytics, discovery, and browser checks. This report does not substitute for those checks. The author-decision issues remain unresolved.

## Integration lead update

After the checks above, the lead reported a passing browser run: 800 article views (50 essays × 8 languages × 2 widths), 41 navigation/language clicks, and no JavaScript errors. This is lead-reported execution, not a second run by this reviewer. Final rebuild and discovery refresh were still underway at that update.
