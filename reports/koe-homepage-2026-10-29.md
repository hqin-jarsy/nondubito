# KOE homepage review — 2026-10-29

Prepared `/koe/` with Bloom/Pulse sections, six character profiles with native expandable stories, formation stories, nine completed-song entries, the shared owner-supplied YouTube channel, and the project's philosophical/fictional context. Added a discoverable homepage entrance. The artist page is English-only, including its shared-shell navigation. Non Dubito’s main homepage remains multilingual.

Validation:
- Local HTTP preview returned 200.
- Browser checked at 390 px, 820 px, and the default desktop viewport; no horizontal overflow.
- Initial trilingual draft was checked before the owner requested English-only. The revised page has one English H1, no translation markup or language controls, and renders in English even with an old `?lang=zh-hant` URL. Its navigation script never reads or changes site-wide language preferences.
- Tested mobile menu, language switching, Escape, homepage entrance, group/member anchors, and member-story expansion.
- Checked portrait/release images when in view; no broken visible images or browser error logs.
- Three watch buttons use the exact channel supplied by Han. No per-video IDs invented.
- Validated 59 local links, assets, and anchors; IDs are unique.
- Analytics audit: 11,981 public pages, zero tracking errors and zero conflict copies; six existing analytics tests passed. `--fix` repaired zero pages.
- Sitemap: 11,962 canonical URLs; only the KOE entry and homepage modification date changed.
- `git diff --check` passed.

Preview screenshots retained outside the website repository in the KOE-Website-Preview-01 output folder. All public image files together are under 1 MB. The nine images (593,612 bytes) are hosted on Cloudflare R2 at `images.nondubito.net/koe/`; each public file passed content-type, byte length, SHA-256, format, and dimension checks. Homepage portraits, artist portraits, release covers, and Open Graph metadata use these URLs. Only text and the image ledger remain in Git; the unpushed initial commit is amended to exclude image binaries. Exact images and offline backups stay outside the repository. No source videos or audio masters were added to the website.

Publication remains subject to Han's confirmation under the repository's explicit no-push instruction in `CLAUDE.md`.
