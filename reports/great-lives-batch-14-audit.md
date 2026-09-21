# Great Lives — batch 14 (040–042)

Date: 2026-09-20. Clean starting HEAD: `676b6d693c96b55d4e4ad6ccee733f95b1304569`. No commit or push was performed.

## Scope and completeness

Revised the existing Chinese and English sources for Nishida Kitarō, the Japanese imperial institution and Homer; replaced their six short localized editions with full Traditional Chinese, Japanese, French, German, Spanish and Korean prose. No translation service was used. The narrative, philosophical comparisons and explicitly imagined bridge endings remain.

| Article | Sections | Traditional paragraphs | JA / FR / DE / ES / KO paragraphs | References |
| --- | ---: | ---: | ---: | ---: |
| 040 Nishida Kitarō | 9 | 63 | 21 / 21 / 21 / 21 / 21 | 2 |
| 041 Japanese imperial institution | 9 | 79 | 21 / 21 / 21 / 21 / 21 | 4 |
| 042 Homer | 9 | 79 | 20 / 20 / 20 / 20 / 20 | 5 |

Full editions are now **43/108**: the first 41 entries, Homer at 042, and the earlier Weil pilot at 085. The third movement is complete. Next: 043 Plato, 044 Hume and 045 Schopenhauer.

The new files `movement-03h-nishida.json`, `movement-03h-emperor.json` and `movement-04b-homer.json` replace the corresponding entries in `movement-03c2.json` and `movement-04a.json`. All other 105 editorial objects remain byte-equivalent as parsed JSON to the starting commit. Stable article URLs are retained.

## Editorial decisions

- **Nishida:** Western philosophy is not reduced to one doctrine of Being, Japanese philosophy does not begin with one man, and William James is not demoted to preliminary psychology. Pure experience, place and absolute nothingness remain distinct stages. Huineng, Kant and Wittgenstein are bounded comparisons. Nishida’s opposition to fascism does not erase his wartime responses to the state or the ambiguity of language available for imperial use.
- **Japanese imperial institution:** mythical genealogy and documented continuity are separated. “Empty” does not mean emperors never governed or ritual did nothing. The postwar settlement is not attributed to MacArthur alone; the Humanity Declaration is not the sentence “I am not a god.” Popular sovereignty, Article 4, cabinet responsibility and concrete wartime actors prevent the metaphor from concealing law or responsibility.
- **Homer:** the article is retitled **荷马，声音进入文字的门槛 / Homer, at the Threshold of Voice and Text**. The blind poet and single-author images remain traditions, not secure biography. Oral-formulaic composition does not mean every performance was wholly new. Dictation is one disputed textualization model, not a recovered day on which voice became writing. Briseis, Priam, Penelope, *polytropos* and Plato’s complicated dependence on poetry remain visible.

Individual research and source limits are recorded in [040](great-lives-040-editor-notes.md), [041](great-lives-041-editor-notes.md) and [042](great-lives-042-editor-notes.md). All references have localized display labels in the six generated languages.

## Integration and verification

- Great Lives generator: **762** language pages generated; check mode passes.
- Full-edition regression suite: **116 tests pass**, including source digests, content maps, localized references, metadata, title synchronization and navigation.
- Latest update ledger and `latest.html` agree.
- Search rebuilt from **10,004 source records**. URL sets are unchanged. Per-language record counts: EN 3,207; ZH 3,210; TC 2,684; JA 1,338; FR 1,326; DE 1,326; ES 1,325; KO 1,325. The bilingual search records change only for Homer, whose source title and body changed; the six expanded languages change only for the three batch articles.
- Sitemap rebuilt with **9,852 canonical URLs**; no URLs were added or removed.
- Read-only scope verification confirms 108 slugs, the other 105 editorial objects unchanged, 43 full editions, balanced HTML and unique IDs on 21 article pages, the six language indexes and Latest.
- The six language indexes still contain 108 cards in seven movements and display progress 43. Twelve generated neighbour pages change only in navigation. The bilingual Plato page changes only its adjacent Homer title.
- `git diff --check` passes. HEAD remains at the clean starting commit.

QA limitation: this batch received static content, structure, link and generator checks, not a browser-rendered visual pass. No deployment was performed.
