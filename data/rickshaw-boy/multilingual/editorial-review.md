# Rickshaw Boy: editorial and source record

## Scope

The received Chinese essays were preserved, together with the old short independent English texts, in `source-original.json`. The Chinese source has 119, 142 and 138 blocks, respectively (399 including headings and bibliographic notes). Existing English consisted of eight blocks per essay and did not cover the complete Chinese narrative and argument. New English drafts therefore restore every Chinese block; they are not presented as a published English translation of Lao She.

`source.json` preserves the same 399-block structure after 68 documented, authorized changes. Each change records original text, revised text, Traditional Chinese and rationale in `../source-corrections.json`. The local series index also required a separate factual correction, recorded in `index-source-corrections.json`. No original physical book edition was independently inspected: the bibliographic notes report the Chinese author's identified edition. Original-text checks and their limits are recorded by the independent reviewer in `independent-source-review.md`.

## Substantive corrections and dependent interpretation

- The three losses are a rickshaw seized by soldiers, savings extorted by police, and Huniu's secondhand rickshaw sold for her funeral. They are not three bought rickshaws or one rickshaw confiscated three times. The index now says this explicitly.
- Xiangzi's initial aim is not asserted to remain his only ambition forever. Sun extorts savings from the money jar, invokes an old acquaintance rather than shared hometown, and assumes savings rather than knowing their exact amount. Xiangzi's desire for another vehicle is distinguished from his dislike of Er Qiangzi's particular rickshaw and its history.
- The drinking episode retains both Huniu's pressure and Xiangzi's desire; it does not invent unconsciousness or first awareness the following morning. Desire is not treated as consent or as erasing the unequal position of the yard owner's daughter and a worker without backing. False pregnancy and pressure to marry remain explicit. No modern legal determination is asserted.
- Huniu's constrained control of her life is not misstated as absence of any money. Her private savings are retained. Her conduct is not excused as the objectively only possible choice. Childbirth assistance follows midwife, ritual practitioner, then Xiaofuzi's hospital inquiry, not an invented home doctor visit; the novel's account is not presented as a clinical causal diagnosis.
- Er Qiangzi sells his daughter before his wife's death. Xiaofuzi returns the following spring, not two years later. The room arrangement changes from Huniu's room at a charge to Xiaofuzi's own poor room. The unsupported sick-father nursing scene is removed, while the burden of supporting him remains. The father's second sale is not asserted as established when the relevant passage only conjectures who arranged it. Xiangzi weeps in a burial ground, not after a search for the hanging tree.
- Xiangzi's illness and treatment precede the news of Xiaofuzi's death. His initial meeting with Old Ma and the later grasshopper conversation are separated. He understands the latter; the essay can argue that he fails to find another road without inventing forgetfulness. Shared poverty does not make Old Ma's moral outcome identical to Xiangzi's informing.
- Ruan Ming is paraded and shot; the sixty-dollar betrayal remains central. Xiangzi's absence of regret is distinguished from his fear. The original does not support a confident itemized claim that he spends every dollar on food, drink and sex. His final procession work is done poorly, not steadily and without effort.
- The institutional critique, self-reliance analysis and account of care without a return remain the author's argument. Corrections remove false supports, not replace the essays with a different thesis. Interpretive claims not established as plot facts remain readings; not every rhetorical assertion is independently certified.

## Reproducible sources and checks

- `scripts/prepare_rickshaw_boy_sources.py` applies the recorded Chinese and Traditional changes from the original snapshot; it is not invoked by the normal language renderer.
- `scripts/compile_rickshaw_boy_english.py` imports the complete line-aligned English drafts and checks block counts and heading positions.
- `scripts/build_rickshaw_boy_languages.py` reads persistent language JSON, patches English and renders five language editions. It does not write shared discovery/navigation/search files.
- `scripts/validate_rickshaw_boy_languages.py` checks complete body coverage, heading alignment, rendered content, all 24 local pages, language alternates, canonicals, analytics and local paths. It also compares current Chinese to recorded changes and verifies changed Traditional mappings.

Before language generation, all 399 Chinese HTML blocks matched the source exactly, all 68 changed Traditional mappings matched their recorded wording, script syntax passed, and scoped `git diff --check` passed. These checks do not substitute for translation review or browser layout inspection. Independent language reviews and final browser/structure results are recorded separately. No push is authorized or performed here.
