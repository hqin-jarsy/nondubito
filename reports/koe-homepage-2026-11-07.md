# KOE artist hub refresh — 2026-11-07

Expanded the English-only catalogue from nine songs to sixteen: eleven Bloom and five Pulse songs, all reported published by Han. Added Somewhere We Can Go, It Was Real, Laugh With Me, Not in the Deal, Still Living Here, What Are We Saving For?, and Before the Stamp, each with a short thematic line.

Refreshed group descriptions to reflect the wider emotional range of Bloom and the funk, breakbeat and rock vocabulary of Pulse. The six member biographies and formation stories remain unchanged. No new migration or nationality biography is assigned from Before the Stamp’s fictional narrator.

Latest release artwork and copy are now data-driven: Laugh With Me for Bloom and Before the Stamp for Pulse. The two versioned WebP files were uploaded to the existing Cloudflare R2 koe/ prefix after Han granted Chrome control. All nine current image objects passed public content-type, byte-length, SHA-256, format and dimension checks (495,672bytes in total;182,854new bytes). Previous release objects remain in R2 and in the ledger history. No image/audio/video binaries were added to Git.

Validation:
- Browser checked at390px,820px and1280px; no horizontal overflow.
- Both current covers loaded from their actual publicR2URLs; no broken visible images or captured browser-console errors.
- English remains selected with an incoming?lang=zh-hant query. No language selector is rendered.
- Mobile menu open/Escape close and member-story expansion worked.
- One H1, unique IDs,34valid local links/anchors,16song entries and14R2image references.
- Analytics audit:13,624public pages,0tracking errors,0conflict copies;fix repaired0pages. Six existing analytics tests passed.
- Sitemap regenerated; only the KOE entry’s modification date changes.
- git diff --check passed.

Exact offline upload files, source snapshots and screenshots:
/Users/hanqin/Documents/Codex/2026-10-20/wo-x20/outputs/KOE-Website-Update-2026-11-06/

No per-video YouTube IDs were supplied or guessed; the owner-supplied shared channel remains the watch destination. HTML publication awaits Han’s remote-push confirmation under CLAUDE.md. Image upload is complete; website hosting remains GitHub Pages.
