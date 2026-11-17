# Catch-22 editorial review — 2026-11-17

## Scope and provenance

Four existing Chinese literary essays are the source, not the novel's prose. The previous English versions were short independent adaptations. The restored English and five new editions each retain **29 / 28 / 32 / 36 narrative and argumentative paragraphs**, 125 units per language, in source order. Edition/source notes are separate from this count. Equal counts are a coverage aid, not a quality score.

The reading-edition credit (Nan Wen, Zhao Shouyin, Wang Deming; revision by Zhu Wan; Shanghai Translation Publishing House) remains in the Chinese and is stated in the new editions. Dialogue is our rendering for these essays, not a claimed quotation from a published target-language translation. Self-as-an-End branding is unchanged.

## Actual review performed

- Implementation worker: read the complete Chinese four essays; restored English scene by scene; wrote and read Japanese, German, Spanish and Korean in full. Checked the six versions' ordered paragraphs, characters, causal links and interpretive claims, not just word counts.
- French worker: wrote all 125 French paragraphs and compared the whole draft with Chinese and restored English. This is translator self-review.
- Implementation worker: subsequently read **all 125 French paragraphs**, including the two regulation versions, Captain Black/de Coverley, the ledger's exclusion, morphine, Chapter 41, acceptance of the bargain before departure, Danby/chaplain and the last knife. Replaced awkward literal reassurance “Là, là” with “Ça va, ça va”.
- Coordinator: independently read all **125 Spanish paragraphs** against English/Chinese. Restored the visible repeated reassurance “Ya, ya” in essay 3, replaced “traje antiaéreo” by “chaleco antiesquirlas”, and repaired “Nada encuentra dónde servir”. All fixes are in drafts and generated HTML.
- Coordinator: checked **29 key paragraphs in each of German, Japanese and Korean**, not full independent linguistic review: essay 1 paragraphs 7,8,9,14,20,22,26; essay 2 paragraphs 11,13,15,16,21,22,26; essay 3 paragraphs 9,14,15,17,24,27; essay 4 paragraphs 7,8,16,17,28,29,30,32,36. The German “vom Dienst befreit” wrongly broadened grounding to exemption from service; corrected to “vom Fliegen freigestellt”.

These are AI editorial checks. **No native-speaker certification, independent scholarly review or line-by-line collation against an authoritative printed novel is claimed.** The source itself is an interpretive essay; its broad readings are presented as such, not as separately established historical facts.

## Restored content

1. Rome's old woman and the doctor's circular exemption; Clevinger, Black's oaths, de Coverley, the soldier in white, Daneeka, Mudd, the chaplain, increasing missions, the motive/execution membrane, and return to the eggs.
2. Raid at cost plus six percent; eggs and Mediterranean offices; Orvieto's two contracts; self-law versus space for others; shares replacing persons; cotton; proxy missions, flotation cylinders, missing morphine, aspirin and the burial/tree scene.
3. Correct treatment of the thigh wound; concealed fatal injury; matter versus recurrent narration; question at instruction; repeated empty reassurance; category of cowardice; Hungry Joe and Dunbar; naked medal ceremony; missing biography and irreducible name.
4. Michaela and the arrest; Aarfy's portable justification; the offer and initial acceptance; rejected safe missions; honest Danby; Orr's practiced route; money/clothes and support; leaving/staying without a ranking; knife and misdirected accountability.

## Factual correction and scope adjustments

- The source twice places the full Snowden revelation in the last chapter. It is **Chapter 41, “Snowden”**, followed by Chapter 42, “Yossarian”. Corrected both occurrences in Simplified Chinese and their complete Traditional Chinese dictionary keys/values. All six non-Chinese editions agree. Verification: novel contents at https://shermankeene.com/catch-22/catch-22.pdf ; corroborating chapter reference https://www.sparknotes.com/lit/catch22/section8/ . Only this factual check used external browsing; the translations derive from the authorized Chinese essays.
- Corrected the old English attribution of loyalty oaths to Major Major: **Captain Black** launches the campaign, **Major de Coverley** ends it.
- Avoided repeating the Chinese's unsupported “many years later” for Cathcart's grievance list. English/new languages simply retain the remembered grievance. Chinese remains otherwise untouched.
- Several absolute statements were narrowed without deleting the argument: “nobody hates Milo” becomes the anger not lasting; “he never lies/never breaks a rule” becomes serious contractual fidelity; “only one person ever seeks accountability” becomes the most determined seeker and a largely unbegun search elsewhere. The MPs need not regard themselves as villains rather than being certified good men. These are deliberate interpretive-scope adjustments, not word-for-word identity.
- Omitted unverified precise recurrence and crash counts while retaining repeated structure and practice. Retained the source's scenes as the essay's reading, not a comprehensive factual audit of all claims in the novel.

## Preservation, rendering, limitations

- Compared each primary Chinese essay-body against Git HEAD: byte-identical after allowing exactly the two authorized Chapter 41 substitutions. Hant index updates only add labels for the expanded language availability; essay 3 dictionary is updated to match corrected source text nodes.
- Text source: six `*.txt` files with `@@slug` and one complete paragraph per line. French metadata is `fr-meta.json`; other metadata is in the series builder. JSON and HTML are generated artifacts.
- Rebuild: `python3 scripts/build_catch22_languages.py`. It imports the dedicated literary renderer and changes only this series' data/pages. It does not touch global discovery, search or sitemap, and does not commit or push.
- 25 new language pages, 4 repaired English bodies, primary 8-language controls, query-selected primary routes, canonical/alternate links, localized index context, adjacent-essay navigation and existing Cloudflare analytics are generated. Primary toggles explicitly wrap for narrow screens.
- Structural/link/paragraph/analytics tests are recorded in `validation.json`. Coordinator performs separate browser and shared discovery checks; this report does not imply those tests were run by the translation worker.

## Coordinator integration evidence

The coordinator reports 30-page body/alternate/local-link/analytics/search/sitemap checks passed; 80 browser cases (8 language modes × 5 pages × desktop/mobile widths) passed with no overflow or switching defect. The coordinator inspected the 390 px Japanese first-essay screenshot. A non-blocking single-character title line was subsequently improved with `text-wrap: balance` in the dedicated renderer; structural validation and byte-identical second rebuild then passed. Browser evidence belongs to the coordinator's checks, not an independent human language review.

Coordinator also compared all 21,997 preexisting search records: records outside this series and explicit collection-entry scope remained unchanged. No old sitemap entry was deleted; out-of-scope lastmod values were preserved.
