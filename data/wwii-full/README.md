# WWII complete-edition restoration

Status: complete local restoration. All 35 translation/conversion files have current independent semantic review receipts. All 36 reader pages are generated and the series-specific build, discovery and browser checks pass. No deployment or push performed.

Base commit: 26e9f4976392b6516aab5eb9198e48d4c532bef4. Original 36 HTML pages were captured from the local MacBook Pro checkout on 2026-11-09. Baseline hashes were rechecked against HEAD on 2026-11-10 and all match. The website was not substituted for uncommitted local work.

## Sources and amendments

The author approved five argument adjustments and ten factual corrections, then seven additional corrections. approved-amendments.md retains the original proposed changes and evidence. amendment-log.json records the initial changes; additional-amendments.json records the ten paragraphs affected by the seven later decisions and their immediate transitions. The final Chinese bodies contain 47, 51, 45, 56 and 54 units, 253 in total.

sources/ holds the frozen Chinese text. source-finalization.json hashes every source file. Each source_sha256 is the SHA-256 of UTF-8 canonical JSON containing title and body, with ensure_ascii=False and compact separators. Existing unrelated Chinese arguments were not silently rewritten.

## Translation and review

translations/ contains the five reviewed complete essays in English, Japanese, French, German, Spanish, Korean and Traditional Chinese. Each follows the same heading/paragraph units. German retains explicit distinctions between the Nazi regime, responsible actors and German people, including qualifications already present in the earlier German edition. Explanation is not exculpation or collective guilt.

Traditional Chinese was prepared with the site's existing offline CoreFoundation Hans-Hant engine and independently read against all source units, including index copy. Contextual and boundary-conversion errors were corrected. Conversion alone is not semantic review.

The *-preliminary and *-completion records are historical/editorial work records, not final independent certificates. Final reviews/<language>.json receipts identify the precise reviewed file hashes and honest limitations. The publication renderer accepts only all seven current independent receipts, an approved source snapshot, and the Traditional index hash. These are AI semantic/linguistic reviews, not an independent professional historical audit of every source claim.

## Build and checks

- python3 -B scripts/build_wwii_full_editions.py
- python3 -B scripts/build_wwii_full_editions.py --check
- python3 -B scripts/test_wwii_full_editions.py
- python3 -B scripts/refresh_wwii_full_discovery.py
- python3 -B scripts/refresh_wwii_full_discovery.py --check

The renderer produces 36 physical pages containing 40 full article readings and eight series reading routes. It preserves the reviewed text and has a separate preview mode. The discovery updater changes only this series' search/sitemap entries and library description; the baseline folder is excluded from search collection.

## Final verification, 2026-11-10

reviews/final-site-qa.json records exact page, source, translation, review and script hashes. All nine WWII tests pass without skips. Build and scoped discovery checks produce zero changes. Browser QA covered 144 route/language/viewport combinations (320/375/1440 px), 64 directed language switches, all eight navigation routes, and 16 search-result clicks. Storage-blocked primary readers and JavaScript-disabled foreign readers passed. German and Traditional Chinese screenshots were inspected at 320/1440 px.

The public analytics repair found zero changes; the check covered 13,822 pages with zero tracking errors or conflict copies, and six analytics tests passed. The bounded homepage digest is current. The new WWII update/card and all prior ledger entries are preserved.

Global update-ledger validation remains blocked by four pre-existing records without a languages field, confirmed in the baseline HEAD: fairy-tales, laughter, cooperation-histories, and aesthetics-core (all dated 2026-11-04). The related homepage suite passes seven tests and fails its ledger-integrity test for precisely those records. These unrelated records were not changed. This does not affect the WWII reader/search tests. See reviews/integration-qa.json.

minor-corrections.json records the verified Korematsu arrest-city correction to San Leandro, applied under the author's permission for small source corrections and synchronized across all editions. The German edition is a historically qualified adaptation. Independent semantic review is not a claim that every sweeping source assertion has received a new archival audit.

Local commit only. Never push.
