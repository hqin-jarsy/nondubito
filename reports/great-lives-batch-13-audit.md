# Great Lives — batch 13 (037–039)

Date: 2026-09-20. Clean starting HEAD: `ad416072e985dca8ce2f96eae6affd9c85c39f24` (`reading zhuangzi`). No commit or push was performed.

## Scope and completeness

Revised the existing Chinese and English sources for Augustine, Bada Shanren and Su Shi; replaced their six short localized editions with full Traditional Chinese, Japanese, French, German, Spanish and Korean prose. No translation service was used. The narrative, philosophical comparisons and explicitly imagined bridge endings remain.

| Article | Sections in each edition | Narrative paragraphs in each edition | References |
| --- | ---: | ---: | ---: |
| 037 Augustine | 9 | 51 | 10 |
| 038 Bada Shanren | 9 | 54 | 6 |
| 039 Su Shi | 9 | 57 | 10 |

Full editions are now 40/108: the first 39 entries plus the earlier Weil pilot. Next: 040 Nishida, 041 the Japanese imperial institution, 042 Homer. This batch does not revise those essays.

The three new `movement-03g-*.json` files replace the corresponding entries in `movement-03c1.json` and `movement-03c2.json`. All other 105 editorial objects remain identical to the baseline. The empty 03c1 envelope remains valid. Existing URLs are retained.

## Editorial decisions

- Augustine is retitled **奥古斯丁，但不要现在 / Augustine, But Not Yet**. Conversion does not close off subsequent thought. The distribution of topics across the thirteen books of the Confessions, pear theft and companionship, grace, time, the two cities, religious coercion and late revisions are distinguished. The Huineng comparison does not erase either tradition's differences. The title is synchronized in the main index, structured data and adjacent navigation.
- Bada Shanren is not described as literally silent for 61 years, diagnosed from anecdotes, or painting without deliberation. Surviving calligraphy, working relationships, seven fish in the Met painting and the extended making of Flowers on a River support a portrait of artistic agency. Pain is neither the whole explanation nor a necessary price of art.
- Su Shi's successive exiles are separated from intervening appointments. Farming, Ma Zhengqing, neighbours and shared enjoyment remain concrete parts of his life. Ding Feng Bo continues through cold, sunlight and looking back; Cold Food retains grief. Rounu owns the home-and-heart answer in the lyric and preface. Equanimity is not invulnerability, and suffering is not the victim's failure of attitude.

Individual research, source limits and language counts are recorded in [037](great-lives-037-editor-notes.md), [038](great-lives-038-editor-notes.md) and [039](great-lives-039-editor-notes.md).

## Reading and source checks

Each author read the existing Chinese/English source and their six complete editions. Root read all three revised Chinese/English texts and all three Traditional Chinese, French and German editions. Independent cross-readers read all Japanese, Spanish and Korean sections and notes: 037 author reviewed 038, 038 author reviewed 039, and 039 author reviewed 037. Final sentence-level changes were integrated, including the Japanese Augustine sentences on Monica's wish and rhetorical self-evasion, and the Korean Su Shi qualification about injury not necessarily writing one's remaining life. Production-process claims were removed from Su Shi's reader-facing notes.

Root additionally checked these relevant source passages:

- Augustine's garden scene in [Confessions VIII](https://www.newadvent.org/fathers/110108.htm), the present self and continuing temptation in [Confessions X](https://www.newadvent.org/fathers/110110.htm), and two loves in [City of God XIV](https://www.newadvent.org/fathers/120114.htm).
- The Met's [Fish and Rocks](https://www.metmuseum.org/art/collection/search/41491) record: seven fish, two rocks and the unpainted water; the Nankai [Flowers on a River discussion](https://art.nankai.edu.cn/2013/0630/c11137a112361/page.htm): date, scroll length, inscription and extended commission. Psychological diagnoses or automatic-enlightenment claims were not adopted.
- Rounu's reply and the distinction between preface and lyric at [Long Yusheng's text](https://longyusheng.org/ci/sushi/29.html).

Root's Palace Museum page fetch timed out; the Bada author had consulted its returned catalogue text. This report does not claim root independently read that full page or inspected physical artworks or manuscripts.

## Integration and verification

- Great Lives generator: 762 language pages generated; check mode passes.
- Full-edition regression suite: **109 tests pass**, including source digests, complete section/paragraph coverage, localized references, valid metadata and navigation.
- Latest update ledger and `latest.html` agree; the Zhuangzi update remains intact beneath this batch's new entry.
- Search rebuilt from **10,004 source records**. Eight language URL sets are unchanged; only the three articles' records changed. Per-language record counts: EN 3,207; ZH 3,210; TC 2,684; JA 1,338; FR 1,326; DE 1,326; ES 1,325; KO 1,325.
- Sitemap rebuilt with **9,852 canonical URLs**; no URLs added or removed.
- Read-only batch verifier confirms all 108 slugs, other 105 editorial objects unchanged, 40 full editions, balanced HTML and unique IDs on 21 article pages, six language indexes and Latest. The six indexes still contain 108 cards in seven movements.
- Twelve generated neighbour pages change only their navigation. The bilingual Wittgenstein page changes only its adjacent-article navigation title; its prose is unchanged.
- `git diff --check` passes. HEAD remains at the clean starting commit.

QA limitation: this batch received static structure, content, link and generator checks, not browser-rendered visual inspection. No local-file browser-access restriction was bypassed. No deployment was performed.
