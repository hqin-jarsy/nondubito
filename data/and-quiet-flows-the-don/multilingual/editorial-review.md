# And Quiet Flows the Don: editorial scope

The editor read all five original Chinese essays (580 blocks) and all five independently structured English essays (40 blocks), not a sample. Original prose remains in `source-original.json`; revised Chinese and its unchanged block ordering are in `source.json`. Edition banners are excluded from prose counts.

## Material corrections disclosed

- The original's uninterrupted moral sensitivity and never-crossed boundary were contradicted by the novel's account of Grigori's hardening. The essays now keep hardening, violence, remorse and unresolved conflict together. They do not claim a permanently pure protagonist or that every change of camp has one witnessed atrocity as its direct cause.
- The unverified generic women-with-shovels scene is not used as a witnessed cause of departure. The verified Daria/Ivan scene is explicitly part of the household narrative, not a substitute event invented in Grigori's presence.
- Late family support matters. Dunyashka remains attached to her brother, offers him the house, and encourages marriage to Aksinia, reporting their mother's support. Political hostility and arrest risk make the home unsafe; they do not mean every family tie has been severed. Lack of institutional protection is distinguished from lack of any private blessing.
- Petro's appeal is to Ivan, not Koshevoi. Koshevoi's bodily trembling is retained without claiming it proves remorse. Surrender, execution and battle are distinguished.
- The death list includes two deaths by gunfire, not only Petro. Aksinia dies after the sentries fire on the fleeing pair; no unsupported claim of an unaimed bullet is retained. Polyushka dies of diphtheria, and Dunyashka survives. Both children were not raised to adulthood.
- Natalia's constrained choices are not replaced by a claim that she never made decisions. Her pregnancy is not called a third pregnancy. The essay keeps the injuries around abortion without inventing a single medical or wartime cause.
- Final return: rifle, revolver and ammunition; March ice; hoped-for amnesty, not guaranteed pardon; recognized but frightened child; meeting near the landing and final embrace at the home. The future remains open, not a narrated execution. The last sentence is identified as a paraphrase rather than certified wording of a print translation.

The source ledger records every altered Chinese block and Traditional equivalent. Specific evidence and limits appear in `independent-source-review.md`. No claim is made to have verified every fact in the whole novel or inspected a physical Jin Ren edition. Authorial interpretations not dependent on refuted plot premises are retained.

## English treatment

The original 40 blocks were preserved as independent arguments, with local factual/clarity repairs. Twenty-three narrative and background blocks were added to support those arguments: Cossack land/service, prisoner violence, the women's marriages and losses, named family deaths, late surviving ties, political danger and the final return. The result is 63 blocks (13/13/13/12/12), not a mechanical 580-block translation. `english-corrections.json` records full old/new bodies and maps every original and additional block. The independent critical endings are not quietly removed.

## Build and review boundaries

Five new languages are to cover all corrected Chinese blocks with aligned headings; bibliography may be in the final body block or a separate `source_note`. `build_don_languages.py` and `don_literary_render.py` write only this series. `validate_don_languages.py` checks exact rendered text, recorded source/English changes, links, alternates, canonical URLs and analytics. Structural checks are not native literary certification. Final language reviews and browser checks are separately recorded by their actual reviewers.

No push is performed. Shared discovery and the serial commit are handled by the coordinator.
