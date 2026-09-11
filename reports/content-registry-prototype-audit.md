# Content registry prototype audit

Generated from the public HTML snapshot dated 2026-09-05. The scanner is
read-only with respect to published pages.

## Coverage

| Measure | Count |
| --- | ---: |
| Scanned HTML pages | 1229 |
| Canonical candidate records | 345 |
| Library categories parsed | 15 |
| Library series cards parsed | 235 |

## Record types

| Type | Count |
| --- | ---: |
| collection-index | 6 |
| essay | 325 |
| series-index | 9 |
| site-page | 4 |
| story | 1 |

## Language editions represented

This counts canonical records with an edition in the named language, not raw
HTML files.

| Language | Records |
| --- | ---: |
| de | 179 |
| en | 216 |
| es | 179 |
| fr | 179 |
| ja | 179 |
| ko | 179 |
| zh-Hans | 214 |
| zh-Hant | 219 |

## Editions per canonical record

| Edition count | Records |
| ---: | ---: |
| 1 | 131 |
| 3 | 39 |
| 7 | 104 |
| 8 | 71 |

## Missing canonical links

None in prototype scope.

## Essay records without a detected public date

- `essays/ai-work/01-writing-is-not-the-danger.html`
- `essays/ai-work/02-prompting-is-not-judgment.html`
- `essays/ai-work/03-efficiency-chooses-direction.html`
- `essays/ai-work/04-options-and-stakes.html`
- `essays/ai-work/05-memory-is-not-answerability.html`
- `essays/ai-work/06-the-last-five-percent.html`
- `essays/ai-work/07-three-ais-agree.html`
- `essays/ai-work/08-working-together.html`
- `essays/ai_companion.html`
- `essays/ai_crisis.html`
- `essays/ethics.html`
- `essays/everyday/relationships/01-when-care-becomes-control.html`
- `essays/everyday/relationships/02-for-your-own-good.html`
- `essays/everyday/relationships/03-solving-your-problem-for-you.html`
- `essays/everyday/relationships/04-help-must-be-refusable.html`
- `essays/everyday/relationships/05-protection-from-every-consequence.html`
- `essays/everyday/relationships/06-boundaries-are-not-distance.html`
- `essays/everyday/relationships/07-does-love-entitle-total-knowledge.html`
- `essays/everyday/relationships/08-explanation-is-not-permission.html`
- `essays/everyday/relationships/09-disappointment-is-not-a-command.html`
- `essays/everyday/relationships/10-refusal-must-be-real.html`
- `essays/everyday/relationships/11-when-understanding-suffocates.html`
- `essays/everyday/relationships/12-heard-but-not-seen.html`
- `essays/everyday/relationships/13-do-not-explain-someone-for-them.html`
- `essays/everyday/relationships/14-making-someone-familiar.html`
- `essays/everyday/relationships/15-when-your-reasons-never-count.html`
- `essays/everyday/relationships/16-does-giving-earn-repayment.html`
- `essays/everyday/relationships/17-when-sacrifice-keeps-accounts.html`
- `essays/everyday/relationships/18-debts-compensation-cannot-settle.html`
- `essays/everyday/relationships/19-responsibility-for-an-adult.html`
- `essays/everyday/relationships/20-when-cleaning-up-makes-things-worse.html`
- `essays/everyday/relationships/21-apology-cannot-end-it-for-them.html`
- `essays/everyday/relationships/22-i-did-not-mean-it.html`
- `essays/everyday/relationships/23-forgiveness-does-not-erase-harm.html`
- `essays/everyday/relationships/24-reconciliation-is-not-resolution.html`
- `essays/everyday/relationships/25-does-calmness-make-you-right.html`
- … 251 additional paths in the generated audit JSON

## Unmapped primary domains

None in prototype scope.

## Edition collisions

- `essays/mingren/buddha.html` / `ja`: `essays/ja/buddha.html` and `essays/mingren/ja/buddha.html`
- `essays/mingren/einstein.html` / `ja`: `essays/ja/einstein.html` and `essays/mingren/ja/einstein.html`
- `essays/mingren/godel.html` / `ja`: `essays/ja/godel.html` and `essays/mingren/ja/godel.html`
- `essays/mingren/jesus.html` / `ja`: `essays/ja/jesus.html` and `essays/mingren/ja/jesus.html`
- `essays/mingren/kant.html` / `de`: `essays/de/kant.html` and `essays/mingren/de/kant.html`
- `essays/mingren/kant.html` / `fr`: `essays/fr/kant.html` and `essays/mingren/fr/kant.html`
- `essays/mingren/kant.html` / `ja`: `essays/ja/kant.html` and `essays/mingren/ja/kant.html`
- `essays/mingren/laozi.html` / `ja`: `essays/ja/laozi.html` and `essays/mingren/ja/laozi.html`
- `essays/mingren/zhuangzi.html` / `ja`: `essays/ja/zhuangzi.html` and `essays/mingren/ja/zhuangzi.html`

## Interpretation

- The prototype proves that per-series language directories can be merged into
  one canonical content identity without changing their URLs.
- Same-page English, Simplified Chinese, and Traditional Chinese modes can be
  represented as editions of that same identity.
- Missing dates and canonical links remain explicit audit findings instead of
  being silently guessed.
- A full-site registry will need a reviewed exception map for legacy language
  hubs and older top-level series.
