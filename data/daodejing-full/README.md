# Reviewed Daodejing full editions

## Current progress: chapters 46–50 (tenth batch)

The tenth batch continues direct, full-length independent writing in Japanese,
Korean, German, French and Spanish. Chinese and English were edited alongside
them; Traditional Chinese is generated offline. The user wrote “45–50”; chapter
45 had already been completed, so its reviewed body remains unchanged and this
batch covers the five new chapters 46–50.

The 7/5/7/6/7-section argument sequences remain, with the original substantive
examples and all six DOI destinations. The prose now develops scenes and
connected paragraphs instead of repeating each inference as a separate slogan.
Necessary qualifications are integrated where they matter. The full closing
wording of chapter 49 is discussed rather than skipped.

`batch10-brief.json` records the shared coverage brief and consulted primary-text
transcriptions. `batch10-review.json` freezes the reviewed manuscripts and their
publication changes against the baseline commit; it is not generated until
editorial review is complete. No external translation package or service is used.

Key corrections: chapter 46's three moments do not make craving irreversible;
chapter 47 does not replace evidence with introspection; chapter 48 preserves
learning, protective boundaries and necessary action without promising automatic
success. Chapter 49 distinguishes respect from unchecked access or trust, and
support from infantilization. Chapter 50 compares Wang Bi's and Heshanggong's
readings of 十有三 without inventing fate statistics; it retains prudent avoidance
without immunity, victim-blaming or medical/financial prescriptions. The exact
Mencius precarious-wall wording is distinguished from the familiar paraphrase.

Classical source panels, source-paper website and chapter URLs are unchanged.
Localized headings, index cards, immediate-neighbour navigation, metadata,
Traditional reading dictionaries and search entries are synchronized. Earlier
review receipts stay intact through explicit before/after digest links.

```sh
python3 -B scripts/build_daodejing_batch10.py --check
python3 -B -m unittest discover -s scripts -p 'test_daodejing*.py'
python3 -B scripts/build_search_index.py --check
DDJ_BROWSER_CHANNEL=chrome node scripts/test_daodejing_batch10_browser.cjs http://127.0.0.1:8774
```

The browser test covers every chapter in all eight reading languages at 1440,
390 and 320 pixels, unchanged source passages, source-note keyboard access,
language switching, overflow and static reading without JavaScript. These are
technical regression checks, not substitutes for the prose review.

## Chapters 41–45 (ninth batch)

`batch09-review.json` freezes 25 locally authored full editions in Japanese,
Korean, German, French and Spanish, plus the corrected Chinese and English
editions. Unlike batches 1–8, this batch has no incoming translation ZIP:
the five languages were independently written here against the full Chinese
essays. The baseline Git commit preserves every previous page.

All original section counts remain (8/8/6/8/8), as do the principal arguments,
examples, three extended applications in chapter 43, and chapter 45's closing
review of chapters 37–45. Independent wording and paragraph counts differ by
language; these are full essays, not shorter summary tiers.

Editorial changes are shared across languages: adopted textual readings are
distinguished from manuscript transcription, immutable reader classes and
invented 强梁 etymology are removed, 金人铭 is not attributed to 周公训伯禽,
and the received chapter 43 also retains 知. Water is a bounded analogy, not a
proof that gentleness penetrates anything. Contentment does not make a person
immune to mistreatment; noncoercion still allows protection, boundaries and
exit. Maturity, finishing work and responsible institutions remain legitimate.
The source-paper website and all classical source panels are unchanged.

The builder renders only the frozen manuscripts, synchronizes localized titles
in indexes and immediate-neighbour navigation, and regenerates the offline
Traditional Chinese dictionaries. Previous receipts remain linked through
explicit before/after hashes, without resealing their manuscripts.

```sh
python3 -B scripts/build_daodejing_batch09.py --check
python3 -B -m unittest discover -s scripts -p 'test_daodejing*.py'
python3 -B scripts/build_search_index.py --check
DDJ_BROWSER_CHANNEL=chrome node scripts/test_daodejing_batch09_browser.cjs http://127.0.0.1:8774
```

The browser test covers every chapter and all eight reading languages at 1440,
390 and 320 pixels, unchanged classical passages, keyboard-accessible source
notes, language switching, overflow and reading without JavaScript.

## Initial chapter

Chapter 1 was the first chapter opted in. Its five manuscripts come from
`daodejing-ch01-translations.zip` in the author's multilingual flagship archive.
Simplified Chinese, Traditional Chinese and English are unchanged.

The editorial pass restores the visible Chinese variant comparisons in French,
German and Spanish (恒／常, 眇／妙, 所徼／徼). In all five languages, the author's
reading of 名 is expressed as “the name for …”, not as an act performed by
non-being or being. A few Korean sentences use more natural descriptions of
drawing distinctions; the established terms 여항, 착, 구 and 착구 순환 remain.
No sections, examples or arguments from the received manuscripts were removed.

`ch01-review.json` records package and manuscript checksums, reversible edits,
the original page shells, and the protected Chinese/English files. Existing
classical-text blocks, edition notes, metadata and navigation are preserved.
The text remains the author's philosophical reading, not a claim to provide a
new diplomatic transcription or philological consensus.

Build/check from the repository root:

```sh
python3 -B scripts/build_daodejing_full_editions.py
python3 -B scripts/build_daodejing_full_editions.py --check
python3 -B scripts/test_daodejing_full_editions.py
python3 -B scripts/test_daodejing_sources.py
```

The tests cover manuscript integrity, eight sections / 119 paragraphs / eight
quotations in each edition, unchanged shells, language choices and local links.
They are static checks, not browser layout verification.

## Introduction and chapters 2–5

The second package, `daodejing-batch01-daoyan-ch05.zip`, supplies 25 complete
manuscripts in Japanese, Korean, French, German and Spanish. No automatic
translation is used. Targeted edits correct the introduction's claim that the
silk manuscripts had no divisions, acknowledge the ritual use of straw dogs in
chapter 5, and distinguish a philosophical portrait of Laozi from established
biographical facts. These corrections also appear in the existing Chinese,
Traditional Chinese and English editions. Other Chinese/English chapter bodies
are not replaced. Classical source blocks remain unchanged.

Additional edits restore visible variant glyphs, smooth specific Korean and
Spanish phrases, and distinguish five thousand Chinese characters from five
thousand words. Spanish introduction/chapter-5 titles and English chapter-5
titles are synchronized with index and adjacent-page links. The chapter-1
receipt records the corresponding Spanish navigation-only amendment.

`batch01-review.json` records the baseline commit, package and manuscript
checksums, reversible editorial changes, and approved page checksums. Reversing
the ledger recovers each original manuscript exactly; differences in paragraph
counts between languages are retained rather than forcing a common template.

```sh
python3 -B scripts/build_daodejing_batch01.py --check
python3 -B scripts/test_daodejing_batch01.py
```

These checks complement the chapter-1 and classical-source regression tests.

## Chapters 6–10 and selective batch-01 revisions

`daodejing-batch02-ch06-ch10.zip` supplies 25 complete manuscripts plus five
revised Korean texts and localized app examples in French/German chapter 5.
The Korean revisions are merged selectively: the published introduction's
division correction and chapter 5's ritual/history corrections are retained.
The French/German updates change only the examples, not the corrected argument.

Chapter 6 separates the etymology of 浴 from this essay's stream imagery,
aligns the chapter-1 naming quotation, and replaces the obstetric analogy with
a child finding their own words. Chapter 8 corrects the 慈故能勇 reference to
chapter 67 and qualifies physical/historical overstatements. Chapter 9 separates
the Shiji account from the ox legend. Chapter 10 discusses the reading effect
of variant wording without asserting a verified editor, date or motive.
These source corrections are synchronized in Chinese, Traditional Chinese and
English. The adopted classical-text blocks remain untouched.

Visible variant glyphs are restored in German, French and Spanish; new titles
are synchronized in page headings, metadata, indexes and neighboring links.
`batch02-review.json` records reversible edits against all 32 incoming files.
The batch-01 receipt also preserves its older provenance through explicit
amendments, so both received versions remain recoverable. Text-node mappings
for the existing Traditional reader are updated offline.

```sh
python3 -B scripts/build_daodejing_batch02.py --check
python3 -B scripts/test_daodejing_batch02.py
```

Run these alongside the earlier batch and classical-source checks. These are
static content and navigation checks, not a browser rendering certification.

## Chapters 11–15

`daodejing-batch03-ch11-ch15.zip` supplies 25 full manuscripts in Japanese,
Korean, German, French and Spanish. The reviewed editions retain the chapter
structures, practical examples and philosophical arguments. Targeted editing
distinguishes the author's interpretation from lexical history, established
biography and claims about the motives behind textual variants.

Chapter 11 treats the 利/用 wordplay as a reading aid, not a proven etymology.
Chapter 12 separates attention narrowed by labels from physiological sensory
loss, qualifies the Five Phases chronology, and correctly identifies the five
pentatonic degrees. Chapters 12 and 13 retain the full Paper 2 discussion;
the previously missing English passages and the Wang Bi context are included.
Chapter 13 distinguishes the Shiji portrait from the later ox legend.
Chapter 14 retains the tool/world analogy without treating nonzero model error
or absent sensory responses as a proof of existence. The 呵/兮 discussion is
an adopted reading rather than a complete reconstruction of ancient speech.
Chapter 15 distinguishes active support from taking over another person's
decisions; water treatment itself is not called colonization. Its opening lists
all seven images in Chinese and English as well as the five incoming editions.

Shared corrections also appear in the existing Chinese/English bodies and the
offline Traditional Chinese mappings. The adopted classical-text blocks are
unchanged. Titles are synchronized through exact title nodes only, including
indexes and adjacent-page navigation; short titles never trigger a global
character replacement. `batch03-review.json` records recoverable incoming texts,
reversible edits and final page checksums. Earlier receipts record explicit
navigation/index amendments without changing their reviewed manuscripts.
The browser search indexes are regenerated; their changed records are confined
to these chapter pages and the affected German series index.

Review references:

- Author's interpretive conventions: https://self-as-an-end.net/papers/sae-daodejing-2.html
- Wang Bi text: https://zh.wikisource.org/wiki/道德經_(王弼本)
- Ancient sound/graph discussion: https://www.ccdbhk.com/demo/public/detail-page/290?txt=%E5%85%AE
- Bias, variance and irreducible noise: https://scikit-learn.org/stable/auto_examples/ensemble/plot_bias_variance.html

```sh
python3 -B scripts/build_daodejing_batch03.py --check
python3 -B scripts/test_daodejing_batch03.py
python3 -B scripts/test_daodejing_sources.py
```

These are static integrity/content/link checks, not a claim of browser layout
verification. No new URLs or routing scheme are introduced by this upgrade.

## Fourth batch: chapters 16–20

The 25 manuscripts from `daodejing-batch04-ch16-ch20.zip` were edited against
the existing Chinese essays, with shared corrections propagated to English
and the offline Traditional Chinese mappings. All chapter sections remain.
The received manuscripts are recoverable through the reversible edits in
`batch04-review.json`; the original ZIP is not modified.

- Chapter 16 no longer uses exhaustive lexical counts or the Guodian find to
  date the first appearance of an emotional sense of 情.
- Chapter 17 corrects the purported 下/不 contrast: the consulted Wang Bi text
  and commentary also read 下知有之. Repeated 其次 does not erase a ranking.
  Helpful speech, clear rules and responsibility are distinguished from control.
- Chapter 18 retains the four diagnostics, everyday examples and self-checks,
  but replaces the unsupported seven-edit history and claims about editors'
  intentions. This chapter is deliberately about one third shorter than the
  incoming drafts after removing that argument and its repeated conclusion.
  Virtue-talk is tested against conduct, not treated as automatic proof of vice;
  loyal remonstrance is not equated with obedience to a ruler's mistakes.
- Chapter 19 presents 利 and 學 connections as philosophical extensions, not
  settled etymology. French/German “remainder of the people” ambiguity is removed.
- Chapter 20 uses 有 as a name for the mother, not as an agent naming her.
  我/吾 is a reading of this portrait, not a universal pronoun rule or a condition
  for qualifying as a subject. The Chinese and English opening now includes the
  previously absent “fool's heart” in its inventory of six 我 occurrences.

German, French and Spanish include the characters under discussion, alongside
pronunciation and glosses. Titles, index cards, neighboring chapter navigation
and affected descriptions are synchronized. The classical source blocks and
all URLs are unchanged. The source paper's chapter 17 issue is documented in
the receipt but was not edited in the separate self-as-an-end project.

```sh
python3 -B scripts/build_daodejing_batch04.py --check
python3 -B scripts/test_daodejing_batch04.py
python3 -B -m unittest discover -s scripts -p 'test_daodejing*.py'
python3 -B scripts/build_search_index.py --check
```

These checks cover content integrity, eight language links, neighboring-page
navigation, source preservation, Traditional Chinese and search consistency;
they do not constitute browser layout verification.

## Fifth batch: chapters 21–25

The 25 manuscripts from `daodejing-batch05-ch21-ch25.zip` are reviewed and
rendered in full section structure. Shared substantive corrections also apply
to the existing Chinese and English essays and their Traditional Chinese maps.
`batch05-review.json` records the ZIP checksum, reversible manuscript edits,
baseline commit and checksums of all affected pages. The supplied ZIP is intact.

- Chapter 21 separates the mother's nourishing role from an equation with 无,
  consistent with chapter 1's naming by 有. The conflicting 绝 example, speculative
  graph-origin claims, mathematical proof analogy and 吾 occurrence count are
  corrected. The philosophical interpretation is retained as interpretation.
- Chapter 22 distinguishes the four reading prompts from universal grammar,
  replaces the wire/straightness analogy, and does not promise that non-contention
  prevents attacks or makes criticism invalid. Six pairs and seven self-checks
  remain. Repeated categorical arguments were replaced, making this chapter
  about 40% shorter than the incoming manuscripts; it is not a summary edition.
- Chapter 23 distinguishes room for another person's judgment from a soft voice
  or slow delivery. The weather image is not treated as a meteorological law;
  changed actions do not instantly erase earlier harm or consequences.
- Chapter 24 preserves the concrete examples while distinguishing self-assessment,
  rest and retirement from refusing present responsibilities. Prior contributions
  and personal worth are not erased by a pause in output. The cooking reading is
  explicitly adopted rather than claimed as settled philology. This chapter is
  roughly 25–35% shorter after removing repeated invalid implications.
- Chapter 25 distinguishes autonomy from exemption from reality. Conditions and
  institutions do not acquire ownership of a person's life. The relation to
  chapter 17's 我自然 is made explicit; sections 7–9 are substantively revised.

The four supplied `daoyan-updated` files were **not** used as replacement bases:
they revert previously reviewed claims about manuscript divisions. Only exact
chapter-title references were merged into the reviewed introductions. Earlier
receipts, including batch 02's supplementary Korean introduction record, retain
reversible edit provenance. Classical source panels and all URLs are unchanged.
Titles, descriptions, series cards, neighboring navigation and eight search
indexes are synchronized. The separate source-paper website was not modified.

```sh
python3 -B scripts/build_daodejing_batch05.py --check
python3 -B -m unittest discover -s scripts -p 'test_daodejing*.py'
python3 -B scripts/build_search_index.py --check
# With a local static server and Playwright:
DDJ_BROWSER_CHANNEL=chrome node scripts/test_daodejing_batch05_browser.cjs http://127.0.0.1:8766
```

Browser verification covers chapters 21–25 at widths 1440, 390 and 320,
Chinese/Traditional/English switching and five foreign-language chapter-25
pages: 75 language/viewport checks, source-panel bounds, keyboard disclosure,
JavaScript errors and a no-JavaScript source-reading check. Desktop chapter 24
and mobile chapter 25 screenshots were also visually inspected.

## Sixth batch: chapters 26–30

The 25 manuscripts from `daodejing-batch06-ch26-ch30.zip` have been edited
and integrated. All seven/eight/seven/six/seven section structures remain.
Shared corrections apply to the existing Chinese and English essays; Traditional
Chinese mappings, chapter titles, neighboring navigation, indexes and search
are synchronized. The supplied archive is untouched. `batch06-review.json`
records its checksum, the baseline commit, reversible manuscript changes,
published section/paragraph counts, length ratios and affected-page checksums.

- Chapter 26 distinguishes the traditional archivist portrait from verified
  biography; corrects the chapter-16 quotation and 昭 dictionary gloss; attributes
  the adopted night-camp reading and distinguishes 环官 from the Zhouli's 环人.
  Responsibility is not a deterministic law of dynastic collapse, and quick
  protective action is not automatically rashness.
- Chapter 27 retains the five images, Nan Huaijin quotation and credential
  examples. 善人 as an action is an explicitly philosophical rereading, not the
  only grammar. 才质/资质 are working concepts, not a claim about innate essence.
  Respect does not depend on productivity, and boundaries or exit do not deny
  another person's standing. The invalid 眇目-to-subtle-wisdom inference is removed.
- Chapter 28 attributes 君子不器 to Analects 2.12 and makes the interreading explicit.
  Neither accepting praise nor remaining in one profession erases personhood.
  Infant imagery is not a therapeutic promise. Concrete scenes of rest, interests
  outside work and a negotiated handover keep the argument accessible. Cooperation
  requires explanation, consent and room to leave, not unlimited availability.
- Chapter 29 does not rank negatives as a universal scale, turn 神器 into a proof
  of systems theory, or infer intentional rewriting from 大/泰 alone. The four
  images invite attention to change rather than prove a complete cosmic law.
  Its title now says “Act Without Owning the World”: non-possession is no guarantee
  against loss. Planning, maintenance and necessary collective action remain valid.
- Chapter 30 distinguishes limits on force from merely hiding its display.
  Fruit is an image of completion, not a naturalization of war. The unsupported
  soil-compaction explanation, etymological psychology and Jobs-as-total-exemplar
  ending are removed. Necessity requires justification; completion still permits
  review, repair and accountability; aging is not moral failure. The five 果而
  clauses are not incorrectly described as five occurrences of 毋.

Removing repeated arguments built on the rejected claims substantially shortens
these drafts: chapters 26–28 and 30 retain roughly half their incoming character
length; chapter 29 roughly two fifths. All chapter sections, principal questions
and practical applications remain, with new concrete explanations where needed.
This is substantive editing, not a verbatim import or an abridged-language tier.
The new language pages contain the same revised argument as Chinese and English.
The supplied glossaries were not imported over previously reviewed terminology.
Classical source panels, URLs and the separate source-paper website are unchanged.

```sh
python3 -B scripts/build_daodejing_batch06.py --check
python3 -B -m unittest discover -s scripts -p 'test_daodejing*.py'
python3 -B scripts/build_search_index.py --check
DDJ_BROWSER_CHANNEL=chrome node scripts/test_daodejing_batch06_browser.cjs http://127.0.0.1:8766
```

Browser checks cover widths 1440, 390 and 320, Chinese/Traditional/English
switching in chapters 26–30, five foreign-language chapter-30 pages, source-panel
bounds, keyboard disclosure and a no-JavaScript reading check. The script can
save desktop chapter-27 and mobile chapter-28 screenshots via `DDJ_SCREENSHOTS`.
