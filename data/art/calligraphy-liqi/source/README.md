# 中国书法细读 12 / Close Readings of Chinese Calligraphy 12

**《礼器碑》：细线如何托住突然变重的一笔**

Open `READ.html` in a browser. All eight complete articles (简体中文、繁體中文、English、Deutsch、Français、Español、日本語、한국어) are available as standalone Markdown and HTML. Four genuine rubbing photographs are embedded locally, with official high-resolution viewer links beside them. Articles and small images work offline; external museum viewers need internet access.

## Version and rights

Original stone: Eastern Han, 156 CE; formerly at Qufu's Confucian temple and now in the Han and Wei Stone Inscriptions Exhibition Hall, Qufu. Reproduced paper object: Ming rubbing album, Palace Museum accession 新00044512. The museum records front, back and sides of the stele and Zhang Boying's title label. Stone, paper, mounting and photography are distinguished.

**No image republication permission has been obtained; no open license is claimed.** Further public or commercial redistribution requires separate clearance. This release contains only the four reading-size photographs. Research screenshots, source webpage texts and thumbnail reference sets are not included.

## Rebuild and verify

Requires Python 3 and Markdown as specified in requirements.txt. Run `python build.py` to regenerate all article HTML, READ.html, MANIFEST.json and SHA256SUMS.txt from the eight Markdown files and included images. This rendering step is offline. IMAGE_NOTES and IMAGE_MANIFEST document the source viewers and actual screenshot/cropping process; the included reading-size images are the local build inputs.

On systems with sha256sum, run `sha256sum -c SHA256SUMS.txt`. Checksums establish integrity, not rights clearance or art-historical correctness.

## Review status

The Chinese essay and all four actual figures received full editorial and independent source review. Source review checked the original stone's present location, the particular Ming album, glyph positions and quote meanings. English was read fully against Chinese. Traditional Chinese was read and corrected semantically, including 鐘, 製作, 採用, 複雜 and 攝影後. All other languages are complete translations, not summaries.

The source reviewer independently recreated all four reading figures from the retained original browser captures using the documented crop boxes and JPEG quality, and obtained exact file-hash matches. This verifies the described cropping process. It is separate from final article layout testing.

- Eight-language cross-reading completed on 2026-10-19 against the Chinese text, four included figures, and the source-review record. The earlier 33 targeted glossary and Japanese naming corrections were verified in place; five further Korean particle corrections were made. This is editorial review, not native-speaker certification.
- Final article browser rendering: not completed. A local HTTP preview returned connection refused in the cloud browser; the browser rejected the file URL under its protocol policy. No alternate route bypassing that rejection was used. Local image, HTML-structure, relative-link and checksum checks are separate and passed.
- No in-person examination, native-speaker certification, identification of an unknown writer or image republication license is claimed.
