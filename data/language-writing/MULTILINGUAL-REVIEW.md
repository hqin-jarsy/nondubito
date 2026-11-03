# Language & Writing — five new full-length editions

Prepared locally on 2026-11-03. The user retains the push/deployment step.

## Source and review

The user supplied `language-writing-8-languages.zip`. All 24 Markdown texts
plus README, manifest and checksum list are archived unchanged in `received/`.
Offline HTML wrappers and website snapshots are not imported as public pages.
The full 56-file checksum list was verified during review. The 27 imported
files were separately compared byte-for-byte with the archive. Their hashes
and the ZIP hash are recorded in `multilingual-publication.json`.

The lead read all fifteen new foreign essays against the approved Chinese.
Three user-authorized agents independently cross-reviewed German/French,
Spanish, and Japanese/Korean. All agreed that the main arguments, examples
and qualifications were retained. These were editorial language reviews,
not external human native-speaker certification.

The original Simplified Chinese, Traditional Chinese and independently written
English remain unchanged: three source JSONs, nine narrative bodies, titles,
decks and source notes. The SAE reading map, hub and existing URLs are retained.

## Twelve local corrections

`corrections.json` applies counted substitutions in memory, not to received files:

- Japanese, Spanish and Korean essay 02 distinguish taking ownership and
  responsibility for a present commitment from fulfilling a promise later.
  Korean also avoids adding a duty to make a promise.
- French essay 02 restores the evaluative question about a reason for sadness,
  repairs incompatible inverted-clause/`et que` coordination, and clarifies
  the human agent of inventing words.
- Japanese essay 01 repairs the construction for needing shared conventions;
  essay 02 makes the quoted objection to excessive formality more idiomatic.
- Spanish essay 01 corrects feminine article agreement with `palabras`.
- Korean essay 01 simplifies nested reported speech. The original was not a
  mechanically duplicated word or a substantive mistranslation.
- Spanish essay 03 specifies saying the difficult thing explicitly rather
  than using the broader `todo`. This is an optional precision improvement,
  not a major meaning correction.
- French essay 03 clarifies who would have needed time to discern differences.
  German prose is unchanged.

No paragraph is shortened, omitted or reordered. Each new language preserves
39/29/30 body units respectively, including three subheadings per essay:
36/26/27 prose paragraphs. Received source notes remain intact.

## Integration and preservation

Five localized indexes and fifteen essays use the existing reading design.
Eight-language dropdowns retain the current essay, with same-language contents
and previous/next navigation. Return links explicitly select the appropriate
legacy English or Chinese reading mode. Single-language pages do not load the
legacy preference script, so saved Chinese/English cannot override their URL.
The native dropdown and full prose work without JavaScript; the small script
controls only the optional mobile drawer and dismissal behavior.

Canonical and reciprocal hreflang links use actual public URLs. English and
Traditional remain modes of the legacy canonical; no query-string pseudo-
canonicals are invented. New editions are dated 2026-11-03; existing text
publication dates remain 2026-10-26.

Against baseline `a0a3d5f`, 386 unrelated Library cards, all five prior channel
inventories and 205 historical update entries are preserved. Only this series'
Library count changes, with new channel, home and Latest entries added.
Search and sitemap gain exactly 20 URLs; unrelated records and dates remain.

## Checks

- All 25 generated pages, including the unchanged SAE hub, match the builder.
- Complete source/rendered prose parity, immutable hashes and all corrections
  pass the 15 language-writing tests.
- Search: 12,071 records. Sitemap: 12,055 canonical URLs.
- Cloudflare: 12,074 public pages, zero tracking errors.
- Ledger, SAE navigation, original-fiction, political-economy and sitemap-date
  regression checks pass.
- Browser: French → Traditional → Japanese stays on essay 02; desktop Japanese
  typography and the corrected commitment wording were checked.
- All 20 new pages pass 320-pixel script-enabled and 768-pixel script-disabled
  frame checks: complete expected paragraph counts, eight menu links, and no
  horizontal overflow in all 40 views. These are fixed-width responsive checks,
  not physical-device emulation.
- The narrow Korean dropdown, mobile drawer and Escape dismissal work.

Archived formatting is preserved. Authored-file whitespace checks pass.
No media upload or remote deployment is included.
