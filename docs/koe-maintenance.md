# KOE artist hub

Public URL: `https://nondubito.net/koe/`.

- `data/koe.json`: public English group/member copy and song catalogue.
- `scripts/build_koe.py`: complete-page renderer using `tracked_html`; reuses the current homepage header and footer, keeping English text and omitting language selectors.
- `koe/koe.css`: artist-page layout; scoped to KOE to preserve the rest of the site.
- `data/koe-image-hosting.json`: public URLs, SHA-256 checksums, dimensions, format, and byte lengths of the nine R2 images.
- Images are served from `https://images.nondubito.net/koe/` in the existing `nondubito-images` bucket. Image binaries and upload staging stay outside Git; `/koe/assets/` is ignored.
- `scripts/verify_koe_images.py`: verify staged files or actual public R2 bytes. Do not add video masters to this static repository.
- The homepage entrance is in `index.html` and its styles are at the end of `home.css`.

Regenerate after changing public copy or the homepage shell:

```sh
python3 -B scripts/verify_koe_images.py
python3 -B scripts/build_koe.py
python3 -B scripts/check_web_analytics.py --fix
python3 -B scripts/check_web_analytics.py
python3 -B scripts/build_sitemap.py
```

`channel_url` is the public YouTube channel supplied by Han: `https://www.youtube.com/channel/UC_KRpnKkRw0MJCfLH4ncReQ`. Both groups share this channel. The renderer validates an HTTPS YouTube URL. Song titles currently describe the completed creative catalogue; no per-video URLs have been guessed.

## Character and asset provenance

The six performers and their biographies are fictional adults. Public copy follows the approved Kingdom-of-Ends creative bible (Bloom) and KOE Pulse member concepts, rather than inferring a biography from generated images. Musical labels describe creative interests, not verified individual vocal allocations. Nationalities, exact locations, birth dates, and unapproved future releases are omitted.

- Nari, Rin, Sena portraits: crops of `Nari-Portrait-Canon-01.jpg`, `Rin-Portrait-Canon-01.jpg`, `Sena-Portrait-Canon-01.jpg` from the retained Girl-Group-Canon-2026 set.
- Jae portrait: cropped frame at 46.5 seconds of `Who-Wrote-the-Rules-MV-Final-01.mp4`.
- Ivo portrait: cropped frame at 25.5 seconds of the same approved final MV.
- Leon portrait: cropped frame at 37.2 seconds of the same approved final MV.
- Bloom current release artwork: `Laugh-With-Me-YouTube-Thumbnail-01.jpg`.
- Pulse current release artwork: `Before-the-Stamp-YouTube-Cover-01.jpg`.
- `koe-social.jpg`: editorial composition of the six portraits, for link previews.

These are format conversions and crops of existing approved material; no new faces were generated. Bloom's long-haired Rin canon remains distinct from Nari's bob. Outfits can change by song without rewriting identity.

Before publication, verify English rendering regardless of incoming language parameters or saved site language, member-story disclosures, section anchors, mobile navigation, visible image loads, and all new local links. Keep the repository's `CLAUDE.md` no-push rule: local work is reviewable before asking Han to confirm the remote push.

## Image updates

Follow `docs/art-image-hosting.txt`: prepare images outside the repository, upload to R2, verify actual public bytes, then update references. `data/koe-image-hosting.json` is the KOE image ledger. Use versioned, content-hashed filenames to avoid stale caches. All page images, including the Open Graph image, use this ledger.

For local staging validation, use the bundled Python with Pillow:

```sh
python3 -B scripts/verify_koe_images.py --local-dir /absolute/outside-repo/upload/koe
```

For publication verification, omit `--local-dir`. Never put credentials in this repository. Keep offline copies of the exact uploaded images. The first nine images were uploaded and publicly verified on 2026-10-29 (593,612 bytes total). The initial local artist-page commit had not been pushed; it was amended so these image binaries will not enter the published branch history.

The artist page is English-only by owner request. `koe/koe.js` handles mobile navigation without reading or changing the site-wide language preference. The main Non Dubito homepage remains multilingual.

## Catalogue update — 2026-11-06

The public catalogue now contains eleven Bloom songs and five Pulse songs, all reported published by Han. Seven additions cover different budgets, the value of a past relationship, shared humour, support and control, repair after an apology, the purposes and costs of saving, and a life waiting between institutions. The six member biographies remain the approved fiction; song narrators are not new member biographies.

`latest_release` in each group’s `data/koe.json` entry owns its title, image-ledger key and short description. The renderer no longer hardcodes a release title. Current spotlights are **Laugh With Me** (Bloom) and **Before the Stamp** (Pulse). Update the image ledger together with this field so cover/title/alt text stay aligned. Per-video URLs remain unspecified; the owner-supplied shared YouTube channel remains the watch destination.

Two versioned WebP covers (182,854 bytes) were added to the existing R2 `koe/` prefix and all nine current public images passed byte/content-type/format/dimension verification. The page’s nine image objects now total495,672 bytes. The previous release objects are left in R2 and recorded under `previous_release_images`; images and staging remain outside Git. Public verification record: `data/koe-image-verification-2026-11-06.json`. Exact offline upload files: `/Users/hanqin/Documents/Codex/2026-10-20/wo-x20/outputs/KOE-Website-Update-2026-11-06/upload/koe`.
