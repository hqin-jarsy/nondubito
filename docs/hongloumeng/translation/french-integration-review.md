# French reader integration review

2026-11-14. Local working tree only; no push or deployment.

## Changes

- Added bounded, reversible French links to the 82 pages of each existing Chinese, Traditional Chinese, English and Japanese reader. French contents/edition pages now expose the same five-language navigation. Chapter bodies are unchanged.
- Added French entries to the three project hubs already reachable from library.html. The hub builder retains this entry. Added original-text return links to the French continuation contents and chapter 81; chapter 80 already links forward to 81.
- Repaired the missing French 23-to-24 link. Added a French contents-page search entrance using the existing ui=fr and in=fr parameters.
- Added exactly 82 French search records: contents, edition, and 80 chapters. Other French records and other language chunks remain unchanged. Search indexes titles/headings/descriptions, not full novel text.
- Kept all existing external-script blocks unchanged. No analytics was added.

## Automated verification

31 focused navigation/discovery tests pass, including existing Japanese navigation and discovery-scope tests. All 410 reader pages have five-language destinations; all 80 French chapters have their applicable previous/next and contents links. English and Japanese publication validation each return 82 HTML pages. French structure/local-link validation passes for 4,395 source blocks. The scoped French search refresh is current and idempotent. All 322 affected chapter bodies were compared with HEAD and remain unchanged (the chapter 81 return nav is the sole addition inside its article container).

## Actual browser verification

Mac Chrome native UI with DevTools Responsive mode, against a local preview. External scripts were stripped from later preview responses only, not from repository files.

- 390x844: French contents, chapter001, chapter080 and continuation081; headings, text and navigation wrap normally, with no visible horizontal clipping in inspected regions. The continuation language dropdown fits.
- 1280x800: chapters001,080,081 render normally. Contents was not separately checked at this width.
- Clicks verified: contents to1,80 to 81,81 back to80,French1 toEnglish1, and search result to French 80. The English-to-French link was visible but not separately clicked; static tests verify its destination.
- Search with ui=fr&in=fr displays French UI and the French index. Corniole returns chapters 80 and 62; chapter 80 opens. Pavillon rouge returns French chapters including 41-80. Osmanthe returns no result, consistent with metadata rather than full-text search.

Limits: desktop viewport emulation, not a physical phone; representative pages/regions rather than every chapter at every width. Chrome automatic translation was temporarily returned to original French for inspection, without changing saved preferences. Console observation included favicon.ico 404 and browser-extension warnings. No production deployment was tested.
