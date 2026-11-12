# Independent English translation work in progress

This directory is project data, not a published English reading edition. Chapters 1–35 have passed chapter-level and cumulative model editorial review: 1,885 units are accepted and 2,590 remain pending. The frozen norm is english-1-110-v0.9, with scoped standards ready for chapters 36–40. Their chapter and cumulative English acceptance is a separate integration step. This is not native-human publication sign-off; publication remains disabled.

## Frozen source and stable alignment

`source-map.json` is reproducible from the already-public `../first80-public/reading.zh.json`. It freezes the file and manifest hashes and maps 80 titles plus 4,395 source blocks. Each unit has a stable chapter/position ID, exact source-text SHA-256, Unicode code-point count, and original layout flags. IDs are scoped to this frozen source; a future Chinese revision requires an explicit source migration, not silent renumbering or acceptance of changed hashes. No private manuscript or editorial approval is copied here.

The full body contains 586,222 code points: 3,399 prose blocks, 929 verse lines, 54 couplet lines, 8 diagram lines, and 5 letter blocks. Chapters 1–5 contain 378 blocks / 35,513 body code points plus five titles (383 units). This is a workload inventory, not an estimate of English word count or translation quality.

## Working records

`progress.json` is the versioned working corpus. Keep one record for every source ID, in exact source order. Do not remove untranslated records. `pending` records have empty segments and reviews. `draft` means independently composed English exists, not that it has passed review. Prose and letters may use multiple ordered English paragraphs in `segments`; every segment retains the source kind and all paragraphs remain mapped to that one source unit. Title, verse, couplet and diagram units retain one segment each. Original layout flags travel with each assembled record. This first schema does not merge multiple source units into one English segment. Revisit the schema explicitly if cross-source paragraph grouping is needed.

`reviewed` and `accepted` require separate `bilingual`, `literary`, and `consistency` review records, each bound to the exact translated content hash and current standard snapshot. A reference must identify an actual review, not an automated test. Detailed review discussions stay in ignored local QA; published references should be neutral editorial IDs with no private transcript, personal metadata, or internal tooling information. Reviewed means those reviews have been performed; accepted means the resulting wording was explicitly accepted in the editorial workflow. The validator checks recorded evidence bindings, not the truth or quality of a review. Never promote status merely to pass a build.

Current frozen normative files are english-standard.md, english-terms.json, english-voices.json, eight batch files covering chapters 1–40, and CHANGELOG.md, under english-1-110-v0.9. The twelve-file snapshot is 5ec8290e4b6188b2746a7582b541cb0cf207b64bf11b6151519febcbb2b45fd5. The eighth batch is a scoped standard, not acceptance of chapters 36–40. Current prior-review bindings preserve every original reference and append the actual 41-unit targeted semantic review and exact public-locator follow-up; this is not a new complete reread of the earlier corpus. Historical snapshots and provenance remain intact.

Every five chapters require an accepted batch checkpoint bound to all translated units and the current standard snapshot. Expansion into the next batch is blocked until that checkpoint exists. Review complete Chinese-English coverage, literary flow, names and terminology, character voices, poems, allusions, diagrams, and consistency with 81–85 and previous accepted batches. Search the entire aligned corpus for terms and voice decisions during this review. Character counts, English-letter presence, structural coverage, or matching paragraph counts do not establish semantic completeness or literary quality.

## Commands

Run from the repository root:

- `python3 -B scripts/hongloumeng_english_pipeline.py validate`
- `python3 -B scripts/test_hongloumeng_english_pipeline.py`
- `python3 -B scripts/hongloumeng_english_pipeline.py assemble --output data/hongloumeng/first80/qa/english/assembly.json`

Parallel chapter drafts may be written as ordered arrays to `chapters/ch001.draft.json` (likewise other chapter numbers), using the same unit record schema. `python3 -B scripts/hongloumeng_english_pipeline.py import-draft --chapter 1` validates the entire resulting corpus before saving, accepts only draft records with no review claims, and refuses to overwrite any non-pending unit. Keep a single editor responsible for importing into `progress.json`; concurrent imports are not supported. The chapter files are author or historical draft working copies, not additional canonical corpus units or current acceptance authority. Older chapter 6, 8 and 10 draft copies may retain former gaps. The current complete English text, review records and accepted checkpoints for chapters 1–35 are in `progress.json`.

Initialization is deliberately non-overwriting. Assembly is deterministic JSON, preserves unfilled source locations, marks itself `translation-work-in-progress` and `publishable: false`, and is confined to the ignored English QA directory. There is no HTML output or website integration. The `release` action always fails closed. A later publication implementation needs separate review, exact approved scope (selected chapters or all eighty), and explicit authorization; incomplete or unreviewed work must never be silently fed to the public renderer. Existing public reading renderers continue to reject unsupported English input.

## Source questions and safe saves

The global `sourceIssues` registry records explicit source questions, not guesses based on punctuation. Each entry has an `id`, mapped `unitId`, current `sourceHash`, `state` (`open` or `resolved`), plain `description`, and `resolution` (null while open; a specific verified outcome when resolved). An open issue blocks unit acceptance and therefore batch acceptance. Issue content and state participate in the affected unit's review hash and batch hash: changing, resolving, or removing an issue invalidates earlier review bindings. Closing an issue requires actual source and translation review; no automatic status promotion occurs. Ordinary narrative ellipses are allowed.

Progress imports use a complete same-directory temporary write, flush/fsync, and atomic replacement. A failed write or replacement preserves the previous canonical file. This remains a single-editor workflow, not concurrent merge support. Earlier private reviews remain historical evidence; never mechanically regenerate their hashes to imply a new review.

The prior frozen source incorporated six corrected blocks without changing any stable ID or layout. The six English alignment issues are recorded as resolved after the corresponding draft revisions and independent review; their reviewed revisions are now included in the accepted first batch. Source correction alone does not resolve an English draft issue; old per-unit hashes in draft files must not be mechanically rewritten.

Twenty reviewed translator notes are held separately in `reader-notes.json`, bound to their source units and clearly labelled as translator commentary. They are not original narrative, are not inserted into translation segments, and are not yet integrated into a reading presentation.

## Editorial and source history

The following sections retain historical as-of observations. Earlier “now”, pending counts, version labels and drafting gates describe their stated stage, not the current summary above.

The v0.3 standard was frozen on 2026-11-11 after a normative-delta review of the accepted first batch. The later v0.4 standard recorded a limited isolated-drafting exception for chapters 11–15 while four source gaps prevented second-batch acceptance. The 589 then-existing translations retained their wording and original review references alongside dated standard-regression references. These normative-delta checks were not new full bilingual or literary rereads. The seven-file v0.4 snapshot is retained as historical evidence.

Seven author-approved readability decisions subsequently changed seven stable Chinese source units (eight textual occurrences) in chapters 6, 8, 10, 17 and 18. Simplified and Traditional data and the corresponding ten chapter pages were rebuilt, with all other source units, titles and layouts unchanged. These are edition-specific readability choices informed by public Chinese transcriptions, not claims of historical-original verification. The source map, canonical progress and translator-note global bindings migrated to that frozen source without changing the 589 existing English translations or their actual review evidence. Historical source-query reports retain their original as-of findings.

The source migration initially left seven English alignment issues open. Four complete new translations in chapters 6–10 have now received independent bilingual, literary and consistency review against the corrected Chinese. Their exact issue resolutions and twelve actual review records are preserved in canonical progress. The three later issues in chapters 17–18 are now resolved after complete source-unit translation, independent bilingual/literary/consistency review, and fourth-batch cumulative review. Their exact reviewed resolution objects participate in the current content and batch hashes.

## Completed chapters 6–10

All 210 units are accepted. The existing 206 translations and their actual review evidence are unchanged; four complete source units, comprising 20 English prose segments, fill the former gaps. `EN-B006-010-COMPLETED-CUMULATIVE-20261111` records a fresh sequential English reading of all 210 units, with targeted Chinese rereads and sampled earlier/later continuity checks. It is not a new complete bilingual reread of all 210 units or of earlier and later chapters. The accepted checkpoint binds the complete ordered batch and the four resolved issue records. No required changes remain from that review.

## Integrated chapters 11–15

The five `chapters/ch011.draft.json` through `ch015.draft.json` files preserve 158 independently composed units. Their author records remain `draft` with empty `reviews`; their exact manuscript bytes are unchanged. `isolated-review-011-015.json` preserves the original isolated-review evidence, all 474 bilingual, literary and consistency review records, and source-alignment provenance. Its current integration metadata now records that these exact units and reviews are also in canonical progress. This is no longer an unimported isolated batch.

The preserved cumulative review, `EN-B011-015-CUMULATIVE-20261111`, read all 158 English units sequentially alongside Chinese, with targeted earlier-text continuity checks and no required changes outstanding. Its batch hash binds their ordered content hashes. The source migration changed only global source and source-map bindings: all 158 local source hashes, five manuscript hashes, review records and cumulative evidence remained unchanged. Controlled canonical integration reused that exact evidence after second-batch acceptance; it does not claim a fresh full reread.

Canonical progress now includes all 158 units as accepted, with an accepted third-batch checkpoint. Review and cumulative evidence must be rechecked if manuscript, relevant source issue, source-unit or normative bindings change. These are model editorial acceptances, not native-human publication sign-off. The eighty-chapter work remains unfinished, and the English publication pipeline remains disabled. No English reading page is published by these data changes.

## Integrated chapters 16–20 and the v0.5 standard

The five `chapters/ch016.draft.json` through `ch020.draft.json` files preserve the exact independently reviewed manuscripts: 305 units with author records still marked `draft` and empty `reviews`. Canonical progress now includes the same translation segments as accepted, with all 915 original bilingual, literary and consistency review records. The fourth checkpoint is accepted against their ordered content hash, the three exact reviewed source-issue resolutions, and the official frozen v0.5 snapshot.

`EN-B016-020-CUMULATIVE-V05-20261111` records an actual consecutive English reading of all 305 units with complete current Chinese comparison. It additionally checked 38 complete earlier canonical units and 21 complete paired prose units from chapters 81–85. It is not a fresh full reread of all earlier 751 units or of chapters 81–85, and is not native-human publication sign-off. All ten chapter-18 poems and 68 poem-body lines were checked. No required manuscript changes remain.

Three separately labelled translator notes explain chapter 19’s two retained textual lacunae and chapter 20’s kinship saying and pronunciation play. The original two notes are unchanged. All five remain source-bound and outside narrative segments and any reading presentation. The chapter-19 `glossaryId` explicitly locates the frozen batch standard’s source-treatment entry rather than inventing a glossary number. No optional notes were added. The two `[text missing]` markers preserve real gaps in the chosen Chinese source; acceptance does not claim the missing wording has been recovered.

The eight-file v0.5 standard was frozen after the actual normative-delta review `EN-V05-R2-DELTA-20261111`, including the corrected inherited Mackerel identity. This fourth-batch integration leaves that standard unchanged. All earlier 751 complete accepted unit records, 2,253 review records, and three accepted checkpoints are unchanged. The chapter 11–15 review manifest and all chapter 21–80 pending records are also unchanged.

The fourth checkpoint enabled drafting chapters 21–25. The fifth-batch acceptance below satisfies the preceding-batch gate for chapters 26–30; drafting still depends on the applicable next-batch standard and source decisions being ready. Chapter 31 remains blocked until the sixth checkpoint is accepted. The eighty-chapter work is unfinished. Publication remains disabled and no English reading page is published by these data changes. Any later manuscript, relevant issue, source or normative change requires suitable re-review before its evidence can be rebound.

## Chapter 24 source alignment

One explicitly approved edition-specific readability correction changes only hlm-c024-b0034, from 恰当很走来 to 恰值焙茗走来, with the corresponding Traditional text. All 4,474 IDs, source order, kinds and layout flags remain unchanged. Current global source and source-map bindings migrate; the 1,056 accepted translations, their 3,168 review records, four accepted checkpoints, five translator notes, thirteen resolved issues and frozen eight-file v0.5 standard remain unchanged. Historical drafts, review reports and normative provenance retain their as-of bindings. The chapter 11–15 manifest updates only current global source bindings and appends explicit provenance; earlier evidence is preserved.

alignment-c024-b0034 is now resolved by its exact independently reviewed resolution after complete English translation and chapter-level and cumulative review. The existing description is retained as historical provenance; its state and resolution record the completed English work. Chinese approval alone was not English acceptance. No English reading page is produced.

## Chapter 21–25 and the v0.6 standard

The frozen v0.6 standard adds scoped fifth-batch execution rules. The 1,056 accepted translations, all 3,168 review content hashes and original references, four accepted batch hashes, five translator notes and fourteen source issues remain unchanged. The standard bindings and appended delta references are the only changes to the existing review records. At the v0.6 freeze, chapters 21–25 were pending in canonical progress and the accepted fourth checkpoint permitted their drafting. Their later acceptance is recorded below; publication remains disabled.

Actual independent normative-delta and targeted earlier-text review EN-V06-R4-DELTA-20261111 supports this standard migration. The chapter 11–15 manifest synchronises its 474 current review bindings while preserving the original content hashes, references and historical source-alignment, canonical-integration and earlier normative-migration provenance. New provenance is appended separately. This is not a fresh full 1,056-unit or 158-unit reread, new acceptance, or publication.

## Integrated chapters 21–25

The five `chapters/ch021.draft.json` through `ch025.draft.json` files preserve 309 independently composed units and 920 segments, with the author records still marked `draft` and their reviews empty. Canonical progress contains the same wording as accepted, with 927 exact-content-bound bilingual, literary and consistency records from the actual independent chapter reviews. The fifth checkpoint binds the complete ordered batch, the exact chapter-24 resolved source issue and the unchanged nine-file v0.6 standard.

`EN-B021-025-CUMULATIVE-V06-20261111` records a fresh complete Chinese-English comparison of all 309 units and a separate consecutive English reading of all five chapters. It also checked 23 complete earlier accepted units and 33 complete bilingual pairs from chapters 81–85. This is not a fresh full reread of the earlier 1,056 units or of chapters 81–85, and it is not native-human publication sign-off. All four chapter-23 seasonal poems, their 32 body lines, the four chapter-25 quatrains and the embedded literary works were reviewed in context.

That cumulative reading found a real terminology drift missed by the initial chapter review: three occurrences of sea-lamp in chapter 25. The author changed only those occurrences to votive lamp, matching chapter 22 and the frozen standard. The chapter reviewer then reread the complete affected scene, its earlier comparator and the full normative entry; the cumulative reviewer independently reread the scene and final whole-chapter flow. Earlier reports and draft bytes remain historical evidence. No required changes remain from the cumulative review.

Eight separately labelled translator notes were approved unchanged in that cumulative reading, supplementing the five preserved notes: two chapter-21 name/imagery notes, two chapter-22 sound notes, two chapter-23 poem-image notes, the chapter-24 Bu Shi-ren pun and chapter 25's tea-betrothal joke. The riddle sound notes belong only after the answers. Their source hashes and actual frozen glossary, literary-mechanism or source-anchor locators are retained. Optional Zhuangzi bibliography and Western Chamber alias notes were not added. All thirteen notes remain outside translation segments and are not integrated into any reading presentation.

Only alignment-c024-b0034 changes from open to its exact reviewed resolved object; the other thirteen issue records are unchanged. All earlier 1,056 complete accepted unit records, 3,168 review records and four checkpoints, all 3,109 later pending records, the five old notes, source map, Chinese and frozen standards remain unchanged. The 309 new unit records are accepted without changing their chapter-review evidence. The fifth checkpoint satisfies the preceding-batch gate for chapters 26–30; drafting still depends on the applicable next-batch standard and source decisions being ready. Chapter 31 remains blocked until actual sixth-batch acceptance. The eighty-chapter work is unfinished, publication remains disabled and no English reading page is produced.

## Chapter 28 source alignment

Two approved readability corrections are now reflected in both Chinese scripts: the independent verse 开不完春柳春花满画楼， is inserted after 滴不尽相思血泪抛红豆，, and 玉诀扇坠 becomes 玉玦扇坠. The line is supported by [Wikisource’s fixed chapter 28 transcription](https://zh.wikisource.org/w/index.php?title=紅樓夢/第028回&oldid=2588440) and [Shidian’s chapter 28 text](https://www.shidianguji.com/book/SWX0004/chapter/1l2i7la0e62ie), not claimed to have come from the original TXT/PDF or an examined ancient facsimile. The comma is the reading edition’s line punctuation. All other wording and punctuation, including 相思 and 照不见, are unchanged.

The frozen alignment now contains 4,475 units. New hlm-c028-b0045 is a pending verse unit. Every old chapter-28 b0045–b0136 maps to the next number, b0046–b0137; old b0125/new b0126 is the sole existing unit with changed text. The chapter gains one block and eleven body code points. Other chapters’ IDs, text and layout do not change. The first 25 chapters’ 1,365 accepted units, 4,095 reviews, five accepted checkpoints, thirteen notes and fourteen earlier issue resolutions remain exact. The nine-file v0.6 normative snapshot remains unchanged. Historical source and normative evidence retains its as-of bindings; only current global source bindings migrate. The complete earlier chapter 11–15 canonical-integration history is preserved.

Two open alignment issues mark the inserted verse and corrected pendant unit. Neither has English content or review yet; source correction does not confer English acceptance. Current progress is 1,365 accepted and 3,110 pending. No English reading page is produced.


## v0.7 scoped standard and current review bindings

The frozen v0.7 standard adds reviewed chapter 26–30 execution rules. Actual normative-delta and exact final-status reviews EN-V07-PROJECTION-R3-V1-DELTA-20261111, EN-V07-FREEZE-STATUS-R2-DELTA-20261111 support keeping all 1,365 accepted English units unchanged. All 4,095 original review content hashes and reference prefixes, five accepted corpus hashes, thirteen notes, fourteen resolved source issues and two open chapter 28 English-alignment issues are preserved. Current normative snapshot fields and appended actual references are updated; the chapter 11–15 historical canonicalIntegration and all earlier provenance are unchanged. This is not a full earlier-corpus reread or new chapter acceptance.

Reviewed semantic rules and a matching Chinese source may support isolated drafting. Canonical import and acceptance require the frozen standard and current bindings, with rechecking against the final version. Chapter 31 remains blocked until actual cumulative chapter 26–30 acceptance. Publication is disabled. Public readiness validates exact configuration, source/map hashes, snapshot and review identifiers; the controlled installation contract separately authenticates the genuine editorial and technical review evidence.


## Integrated chapters 26–30

The five chapter draft files preserve the exact independently reviewed manuscripts: 328 units and 1,108 English segments, with author states still draft and review arrays empty. Canonical progress contains the same wording as accepted, with 984 exact-content-bound bilingual, literary and consistency review records. The sixth checkpoint binds the complete ordered batch, the two exact chapter-28 issue resolutions and the current, independently clarified ten-file v0.7 standard.

EN-B026-030-CUMULATIVE-V07-20261111 records a fresh full Chinese-English comparison of all 328 current units and a separate consecutive English reading of all five chapters, including all four chapter joins. It also checked 47 complete earlier accepted units and 32 bilingual passages from the current project chapters 81–85. This is not a full reread of the earlier 1,365 accepted units or of chapters 81–85, and it is not native-human publication sign-off. No required manuscript changes remain.

Individual chapter-27 and chapter-28 final reviews combine their actual full first readings with narrowly documented revised-scene rereads and exact unchanged-content checks. They do not claim a second whole-chapter reading. The cumulative review separately read both complete revised manuscripts. The accepted references retain these distinct sources of evidence.

Seven separately labelled translator notes explain the Tang Yin visual/sound joke, chapter-27 title beauties, the unresolved co-listing of Qiao-jie and Da-jie, bao plus bei, yuanjia, the Dong Shi frown allusion and the text’s eighteen-stroke count for qiang. The co-listing note appears at its first batch occurrence, rather than being duplicated later. Optional Aroma recall, chronology and double-hour notes were omitted. All thirteen earlier note objects are unchanged; the combined twenty notes remain outside narrative segments and are not integrated into a reading presentation.

Only alignment-c028-b0045 and alignment-c028-b0126 change to their exact independently reviewed resolved records. Their descriptions remain historical provenance, while their resolutions record completed English review of the inserted Red Bean Song line and open-ring jade pendant. No Chinese source or source-map change is made.

The separate factual clarification now attributes the eighteen-stroke count to the selected narrative. Its genuine normative and cumulative delta reviews support the current snapshot without relabelling historical full readings. The cumulative supplement actually reread thirteen local units, the nine changed normative fields and the changelog. The two chapter-28 issue resolutions retain their truthful historical snapshot references; their current compatibility is recorded by the supplementary review. The earlier stroke-count note and unsealed integration candidate are retained as historical evidence and are not used for installation.

All earlier 1,365 accepted unit records, 4,095 review records, five accepted checkpoints, fourteen resolved issues and the entire historical chapter 11–15 integration are unchanged. All 2,782 later pending units are unchanged. Current progress is 1,693 accepted and 2,782 pending, with six accepted checkpoints. The sixth checkpoint satisfies the preceding-batch gate for chapters 31–35; drafting still requires its applicable next-batch standard and source decisions to be ready. The eighty-chapter work remains unfinished, publication is disabled and no English reading page is produced. Any later manuscript, relevant issue, source or normative change requires suitable re-review before evidence can be rebound.


## v0.8 current normative bindings

Chapters 1-30 remain accepted: 1,693 units, 5,079 unchanged review content hashes and six unchanged checkpoint corpus hashes. The 20 separate notes, 16 resolved source issues and all later pending units are preserved. Current snapshot fields and appended actual review references EN-V08-PROJECTION-R3-LISTENER-R4-DELTA-20261111, EN-V08-G07-11-QUANTITY-FINAL-STATUS-DELTA-20261111 bind the reviewed seventh-batch rules and final status. All original reference prefixes, the complete chapter 11-15 canonicalIntegration and all historical provenance remain unchanged. These are scoped delta reviews and targeted accepted-evidence checks, not a full earlier-corpus reread or acceptance of new prose. Publication remains disabled.


## Integrated chapters 31–35

The five chapter files retain the exact independently reviewed manuscripts: 192 units and 905 English segments, with archived states still draft and empty review arrays. Canonical progress contains those same words as accepted, with 576 new exact-content-bound bilingual, literary and consistency review records. The seventh checkpoint binds the complete ordered corpus to the installed v0.8 standard.

EN-B031-035-CUMULATIVE-R2-FINAL-20261111 binds the genuine complete 192-unit Chinese-English comparison, separate complete English reading and all four chapter joins recorded in cumulative r1. The final r2 closes the quantity and normative gate through an actual narrow reread of complete chapter-34 units b0042–b0045 and the exact normative delta. It does not claim a second full cumulative reread. Targeted earlier and later comparisons cover 22 earlier accepted units and 11 bilingual passages from chapters 81–85, not complete rereads of either corpus.

The full individual chapter-34 r1 review remains historical and correction-required. Its later four-field delta closes those corrections; only the cumulative review independently read the complete revised chapter. All original manuscripts, individual reviews and cumulative reports remain unchanged. Optional stylistic suggestions were not applied. No reader note or Chinese-source repair is added.

The cumulative report's earlier accepted-baseline hash records its real reading context before v0.8 installation. This integration instead preserves every current installed chapter 1–30 unit object, all 5,079 earlier review records and six old checkpoint objects exactly. It does not rebind historical reading claims. The twenty notes, sixteen resolved source issues, prior integrations, source, source map, normative files, code and website are unchanged.

Current progress is 1,885 accepted and 2,590 pending units, with seven accepted checkpoints and 5,655 current review records. The seventh checkpoint satisfies the preceding-batch structural gate for chapters 36–40; it does not approve a future batch's terminology or prose. The eighty-chapter work remains unfinished, publication is disabled and no English reading page is produced. This is not native-human publication sign-off. Relevant later changes require suitable actual re-review.


## Isolated ch38/ch42/ch45 source and current-binding amendment

This candidate follows the explicit ch38 author choice 几霜痕 and the bounded ch42/ch45 source repairs. Chapter40 桃杏树 stays. It preserves all 4,475 IDs and all accepted English wording. Chapters1–35 remain the only accepted corpus: 1,885 accepted, 2,590 pending, 5,655 existing reviews and seven checkpoints. The four changed source units remain pending. Twenty note objects, sixteen source issues, all historical review evidence and chapter11–15 integration records are retained. No B8 acceptance or publication is included.

Actual independent scoped review SOURCE-CH38-42-45-INDEPENDENT-SEMANTIC-R1-20261111 supports current snapshot migration and appended references only. This does not claim a whole earlier-corpus reread.


## Integrated chapters 36–40

The five draft archives retain the independently reviewed wording and segment layout: 376 units and 1,140 segments. Their author states remain draft and review arrays empty. Chapter38 b0060 carries the author-approved 几霜痕 source hash with no English wording change. Chapter40 b0002 uses Felicity in the two independently reviewed name positions; all other English words remain exact to the complete final reading.

EN-036-040-CUMULATIVE-FINAL-STATUS-R1-20261111 preserves the actual full bilingual reading, separate complete final English reading, four chapter joins and targeted earlier/81–85 comparisons at their historical source and normative bindings. EN-036-040-CURRENT-BINDING-INDEPENDENT-R1-20261111 adds a real limited current-source, naming, normative and note review: 49 complete bilingual units, the actual own85 identity passage, all fourteen selected notes and the exact changed normative content. It is not a new complete 376-unit or earlier-corpus reread. The distinct chapter38 author-choice and chapter40 naming reviews remain authenticated evidence, rather than being relabelled as older reviewers seeing later bytes.

Canonical progress adds 1,128 exact-content-bound bilingual, literary and consistency records and the eighth cumulative checkpoint at the installed normative snapshot. All 1,885 previous accepted unit objects, 5,655 current review records, seven earlier checkpoints, sixteen source issues, Felicity historical preimage and source/normative history remain exact. All 2,214 later pending units are unchanged.

Fourteen separately labelled translator notes are included exactly as selected, with valid current glossary or literary pointers and placed-unit source hashes. All twenty earlier note objects remain exact. The thirty-four notes remain outside translation segments and are not integrated into a reading presentation. No additional explanatory material is introduced.

Current progress is 2,261 accepted and 2,214 pending units, with 6,783 current reviews and eight accepted checkpoints. Later chapters still require their own applicable standards, source decisions and actual reviews. No later batch is accepted, publication remains disabled and no public English reading page is produced. This is not native-human publication sign-off; relevant later changes require suitable actual re-review.


## Integrated chapters41–45 and scoped v0.10 binding

The exact five draft archives contain200 units and894 segments. Their author states remain draft and review arrays empty. Chapter41 b0002 uses Felicity in the two independently reviewed name positions; every other manuscript object remains exact to the historical complete bilingual and continuous English reading. The current source is unchanged.

EN-041-045-CUMULATIVE-20261111 retains its authentic200-unit/894-segment full bilingual and separate continuous-English reading at its historical source/norm/file hashes. EN-041-045-CURRENT-BINDING-INDEPENDENT-R1-20261111 authenticates the current exact body and note bindings using that reading plus the actual naming and public-projection reviews. The latest scoped review reread the complete41b0002 Chinese and seven English segments, allnine note anchors and the final-status difference. It is not a new whole-batch or earlier-corpus reading.

EN-V010-CURRENT-1-40-NORM-MIGRATION-INDEPENDENT-R1-20261111 and EN-V010-FINAL-STATUS-INDEPENDENT-R1-20261111 support limited new-norm applicability to the unchanged2,261 prior accepted bodies,6,783 review content hashes and eight checkpoint corpora. Every previous reference remains intact with these scoped references appended. The complete pre-migration progress is preserved in v010-20261111.before.json; original source and Felicity histories remain independently enforced.

The current records add600 exact-content-bound reviews and the ninth cumulative checkpoint. Nine selected translator notes remain separate from translation segments; all34 earlier note objects and16 source issues are unchanged. Current totals are2,461 accepted and2,014 pending units,7,383 current reviews,nine accepted checkpoints and43 notes. Notes are not integrated into a reading presentation. Later batches retain their ordinary five-chapter gates.

The normative checkpoint describes scoped internal editorial readiness, not native-human publication sign-off. Technical installation checks remain separately required. Publication remains disabled, no public English reading page is produced and no later batch is accepted by this change.


## Chapters 46–50: current v0.11 checkpoint

This internal work-in-progress corpus carries the exact reviewed chapter 46 r3, 47 r2, 48 r4, 49 r5 and 50 r4 drafts: 402 units and 1,083 English segments. The full prior bilingual and continuous-English reading plus actual scoped revisions remain bound to their own hashes. The current binding is a limited source2/final-state and normative-applicability review, not another whole-corpus reading.

The current source includes the separately reviewed chapter 2 author ending and chapters 46–55 source repairs. Their authentic prior validators, source choices and archived review evidence remain in place. B10 changes no Chinese or previously accepted English, including the chapter 2 ending and Felicity names. Its 18 selected translator notes retain their exact texts and local anchors, separately from prose; the 43 earlier notes and 16 source issues remain unchanged.

The ten accepted five-chapter checkpoints cover 2,863 accepted units, leaving 1,612 pending units. There are 8,589 current review slots and 61 separate reader notes. Later batches retain the ordinary draft, content-review and five-chapter checkpoint gates. The public normative proposal’s old snapshot is historical; all 16 current normative inputs and the exact source/map require their separately authenticated current-binding receipt. English publication remains disabled.


## Prospective B11 current-binding checkpoint

The B11 preparation proposes 3,155 accepted units through chapter 55, with 1,320 pending units and 66 separate notes. Normal readiness remains closed until a genuine independent current-binding and technical receipt covers the exact final merged norm, the 292-unit B11 corpus and five selected notes, and the two chapter 25 accepted-content changes with the limited batch 21–25 delta. Historical reviews remain in their original contexts; no fresh complete reread or production installation is claimed. Later chapter drafting and subsequent five-chapter review gates are not capped at chapter 55. Publication remains disabled.


## Prospective B12 checkpoint

Exact drafts for chapters 56–60 and three selected notes are proposed for acceptance over the receipt-bound source56–65 predecessor. Normal readiness is closed pending genuine independent current-binding and technical receipts. Historical full readings retain their original scope; no fresh whole-corpus reread is claimed. Prior accepted bodies and notes remain unchanged. Later drafting and five-chapter gates continue beyond chapter 60. English publication remains disabled.


## B13 checkpoint

Exact chapters 61-65 and three selected notes are prepared over the installed B12 predecessor. Normal readiness requires genuine independent current-binding semantic and technical receipts. Historical full readings retain their original scope. Earlier accepted bodies and notes remain unchanged. Later drafting and five-chapter gates continue beyond chapter65. English publication remains disabled.


## B14 checkpoint

Final chapters 66-70 and four separate notes are bound to the corrected Chinese source. Current readiness requires genuine independent binding receipts. Earlier English and historical reviews remain unchanged in their original contexts. English publication remains disabled.
