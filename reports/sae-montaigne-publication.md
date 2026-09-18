# SAE Western Philosophy and Montaigne publication

Publication prepared: 2026-09-17. Local changes only; deployment remains with the author.

## Scope

- New `essays/sae-western/index.html` collection: Republic, Nicomachean Ethics, Consolation of Philosophy, and Montaigne.
- New `essays/sae-montaigne/`: introduction, five complete essays, and a series index, each with English, Simplified Chinese, and Traditional Chinese reading modes.
- English is an independent prose adaptation, not an abridgment or sentence-by-sentence translation. Traditional Chinese retains every Chinese paragraph and receives an editorial character review.
- Existing series URLs and article bodies are unchanged. Eighteen existing series indexes now return to the collection; the five other-language editions explicitly label the shared English collection.
- Library, Explore, Latest, search taxonomy, search indexes, and sitemap are integrated. Great Lives work remains paused.
- Author manuscripts in `Documents/SAE西哲/随笔集-蒙田/` were read, not edited. Publication source is `data/sae-montaigne.json`; shelf copy is `data/sae-western.json`.

## Editorial boundaries

The prose retains the manuscript scenes while separating evidence from interpretation:

1. An interrogative motto is not immune to criticism; unchanged wording does not prove continued assent.
2. The warning about abandoning one's weapons occurs within II.12, not at its end.
3. The cancelled marginal escape route is verifiable; its cancellation does not by itself disclose Montaigne's motive. Avoid an exact punctuation claim unsupported by the image.
4. Adding text is allowed by “I add; I do not correct.” The tension concerns deletion and replacement, not addition itself. The essay does not settle the author's continued assent to his printed rule.
5. Individual sequences of writing and cancellation do not establish a complete chronology for an entire leaf. Most, not all, of the printed sentence is crossed out. The 1595 edition is a comparison text, not evidence of handwritten alterations.
6. Unverified totals (260, 16, 280, 8000) and revision superlatives are omitted. Leaving office in 1570 is distinguished from the 1571 retirement inscription; retirement is not permanent isolation.

Optional SAE asides and source notes are collapsed after the complete prose. Specific Traditional Chinese corrections, including 發／髮, 幹／乾, 準／准, and 劃, are retained in the builder and regression tests.

## Primary-source checks

- MONLOE editorial introduction: <https://montaigne.univ-tours.fr/essais-1588-exemplaire-bordeaux/>
- MONLOE office records and library inscriptions: <https://www.bvh.univ-tours.fr/monloe/Arrets.asp> and <https://www.bvh.univ-tours.fr/monloe/Inscriptions.asp>
- Printed comparison texts: <https://hyperessays.net/gournay/book/II/chapter/12/>, <https://hyperessays.net/gournay/book/III/chapter/2/>, <https://hyperessays.net/gournay/book/III/chapter/9/>
- Chicago transcriptions derived from MONLOE XML: `annotation_0228.json`, `annotation_0358v.json`, `annotation_0432v.json`, `annotation_0433.json` under <https://artfl-iiif.uchicago.edu/montaigne_manifests/annotation_json/>. Direct links appear in the relevant essays.
- The manuscript reviewer also inspected images of f358v and f433r through Chicago's IIIF service. Exact stroke counts and an unverified total sequence were not inferred from them.

## Verification

- `scripts/test_sae_western.py`: 10 passing tests (all eight generated pages, complete three-language bodies, Traditional editorial fixes, metadata, local links, notes, previous/next, search taxonomy, Latest, sitemap).
- `scripts/test_sae_western_navigation.py`: 5 passing tests (category placement, four unique series, stable paths, old indexes, Explore).
- Builder reproducibility, content registry validation, update-ledger validation, JavaScript syntax, and `git diff --check` pass.
- Node VM smoke check: five language-initialization cases, including storage denial and invalid preferences, pass.
- Browser verification: all six articles in all three reading modes have one visible title and body, complete expected paragraph counts, closed optional notes, and no horizontal overflow. Desktop screenshots and a 390px-wide mobile layout were inspected. Language buttons, article navigation, note expansion, and mobile drawer behavior were exercised. Library English and Traditional category text was checked.
- Search generation: 9,992 source records. Sitemap: 9,840 canonical URLs. These counts include the eight new HTML pages, not separate URLs for the three embedded reading modes.

## Rebuild

```sh
python3 -B scripts/build_sae_western.py
python3 -B scripts/build_search_index.py
python3 -B scripts/build_sitemap.py
python3 -B scripts/test_sae_western.py
python3 -B scripts/test_sae_western_navigation.py
```

The rebuild reads checked-in editorial data and does not modify the external manuscript folder.
