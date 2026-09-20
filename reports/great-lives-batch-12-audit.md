# Great Lives — batch 12 editorial audit

Date: 2026-09-20. Scope: 034 Lincoln, 035 Galileo, 036 Wittgenstein, movement 3.

## Scope and editorial result

The worktree was clean at the start, at `7f98ef45126f8816dc35796ff24e3c55a0935667`. This batch upgrades the three existing articles; it does not add URLs, rearrange movements or rename the Chinese/English articles. It brings the full-edition program to 37/108: 001–036 plus 085 Weil. Next in canonical order: 037 Augustine, 038 Bada Shanren, 039 Su Shi.

Each article retains nine narrative sections. Revised Chinese and English have 60, 49 and 54 paragraphs respectively. Traditional Chinese preserves every section and paragraph. Japanese, French, German, Spanish and Korean are full reading editions, not summaries; each follows the complete narrative, argument, comparisons and imagined bridgehead ending. Counts are regression guards, not literary-quality measurements.

### Lincoln

Preserves the divided house, inherited institution, war, emancipation, Reconstruction, Washington, Gettysburg, Marx and Ford's Theatre. Separates congressional passage from state ratification and Lee's surrender from the end of all fighting. Restores enslaved people's own actions, abolitionists, Black soldiers and subsequent communities. Does not turn oppression into an inevitable conserved quantity, equate political secession with individual exit, or treat the dead as material for a state. Two correction-heavy sentences were rewritten positively: the continuing work toward ratification and the names, families and unlived days of the dead.

### Galileo

Preserves the recantation, telescope, observations, conflict over interpretation, survival, ongoing inquiry, Copernicus, the world's independence from judgment and the bridge. Distinguishes observations against the Ptolemaic arrangement from proof of Earth's motion; retains Tycho, Harriot, Osiander and the limitations of Galileo's own tide argument. No claim that Copernicus narrowly escaped a trial or that Galileo single-handedly invented an unchangeable method. Surviving under coercion does not require redemption through a later book. The new-instrument and Newton-calendar passages were made positive rather than corrections addressed to readers of an unseen older draft.

### Wittgenstein

Preserves both books, the return to Cambridge, picture theory, value and silence, language-games, revising oneself, Kant and the reported last message. Adds everyday examples without replacing the argument with slogans. Corrects the claim that the Investigations has no numbering, respects §43's qualification, distinguishes sense from truth and empirical reporting from ethical value, and avoids reading his final words as a refutation of the Tractatus. Ramsey, Sraffa and Engelmann remain visible. The imagined bridge offers an open page, not a hierarchy in which everyone else has stopped thinking.

## Reading and sources

Root read the original and revised Chinese/English for all three articles. Root fully read the Traditional Chinese, French and German editions of Lincoln and Galileo, and supplied wording and character-level corrections. The authors reviewed all their editions. The Lincoln editor independently read Galileo's Japanese, Spanish and Korean; the Galileo editor independently read Lincoln's Japanese, Spanish and Korean. Root wrote Wittgenstein's revised Chinese/English and German, read and corrected the complete mechanically converted Traditional Chinese, and fully read the French, Spanish, Japanese and Korean editions supplied by the two editors. All eighteen additional-language editions received complete reading review.

Final cross-reading changes include Korean border-state and Lincoln Memorial references; Japanese formulations of Galileo's lost freedom and the needs of inquiry; Korean preface authorship; Wittgenstein's Japanese reopening of thought rather than defiant justification; clearer Spanish book references; and precise Kant wording across languages. These corrections were integrated before the final build.

Individual source and editing records: [034](great-lives-034-editor-notes.md), [035](great-lives-035-editor-notes.md), [036](great-lives-036-editor-notes.md). Public-domain philosophical texts and primary/institutional historical materials are linked in the articles. Root additionally checked the National Archives amendment record, Museo Galileo's Venus entry, the 1992 papal address, Wittgenstein's original texts, the Wien Museum account and the cited scholarly discussion of the final message. The Library of Congress emancipation article returned 403 on root's direct fetch; no claim of root reading that blocked page in full.

No external translation service was used. Foundation's script conversion was followed by contextual Traditional Chinese review, not treated as a finished edition. Separate localized display labels are provided for every source link.

## Integration and verification

- `scripts/build_great_lives_languages.py`: rebuilt 762 pages; `--check` passes.
- `scripts/test_great_lives_full_editions.py`: all 102 tests pass. The first run exposed two short legacy source meta descriptions, now replaced with substantive Lincoln and Galileo synopses; the rerun passes.
- `scripts/build_search_index.py`: regenerated from 9,997 source records; `--check` passes. Record sets are unchanged in all eight language indexes; only the three target articles' records changed.
- `scripts/build_sitemap.py`: regenerated and verified 9,845 canonical URLs. No URLs added or removed.
- `scripts/check_site_updates.py --check`: update ledger and Latest agree.
- Independent read-only workspace verifier `verify-great-lives-batch12.py`: all 108 slugs retained; the other 105 editorial objects unchanged; 37 full editions. The 21 target article pages have balanced markup and unique IDs. Twelve neighboring pages changed only inside their navigation. All six language indexes retain 108 cards, seven movements and the updated full-edition count; indexes and Latest also pass markup checks.
- `git diff --check`: passes. Full-edition data was migrated to three dedicated files; the old movement envelope and remaining entries are preserved. Progress report and update records are synchronized.

No browser visual verification was completed; structural checks are not a substitute for a rendered-page inspection. No commit, push or deployment was performed. HEAD remains at the starting revision.
