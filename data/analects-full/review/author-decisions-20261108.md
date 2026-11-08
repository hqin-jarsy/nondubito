# Analects: approved editorial follow-up, 2026-11-08

## Decisions and wording

- Essay 39 is retained unchanged in every language, as requested by the author. Six published HTML files match their baseline SHA-256 hashes.
- Essay 19 presents the ruler-addressee as the essay’s reading, using two brief connected phrases rather than a scholarly disclaimer: “合起来，我把这句话读作对统治者说的：” and “回到这句话本身。这样读，对面坐的便是有权力的人。”
- Essay 44 limits the statement to Zengzi’s accounts about the teacher and retains his own judgments: “所以，他关于老师的转述，我们不直接拿来认识老师，也不反对；他自己的判断，好的仍然是好的。这里只标出：一个好学生把活的记成了条目。”

All three approved replacements are synchronized across Simplified and Traditional Chinese, English, German, French, Spanish, Japanese, and Korean. The exact 24 language-level replacements and preservation hashes are recorded in `author-decisions-20261108.json`. Received manuscripts and Chinese source snapshots remain immutable; approved overlays drive generation.

## Review and verification

- Independent read-only review checked all 24 replacements and their surrounding passages. It confirmed natural reading-level phrasing in essay 19 and the distinction between accounts about the teacher and Zengzi’s own judgments in essay 44.
- Applying only the recorded replacements to baseline commit `162a74f479fc45ff7a9edbd36d2e726f03398779` reproduces all 12 changed published pages byte for byte. No other Analects HTML changed.
- Original correction entries are retained unchanged. Three approved Chinese editorial replacements and 15 corresponding received-language overlay replacements were appended; the English source edits match the receipt.
- Nine automated tests pass, including complete-source checks, canonical bodies, Chinese correction boundaries, exact author decisions, essay 39 preservation, portable generation, navigation, search, and discovery.
- All three generation checks pass: complete renderer (306 pages), legacy primary entry point (51 pages), and legacy five-language entry point (255 pages).
- Full browser regression: 800 reading views, 49 navigation/language clicks, desktop and mobile widths (1440 and 390), zero errors. See `author-decisions-browser-results.json`.

## Scope and limits

This follow-up reviews the approved passages across all eight reading languages. It does not claim a new full rereading or native-speaker review of all 250 received translations. Existing broader source questions are not silently revised. Previously documented unrelated site-wide baseline issues remain outside this correction.

Only Analects source, generated-page, review, and test paths belong to this follow-up. Concurrent film and shared-site working-tree edits are excluded. No push is performed.
