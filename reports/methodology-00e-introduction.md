# Methodology 00E: an accessible introduction

Editorial date: 2026-09-19.

## Published scope

- `essays/method/00e.html`: **意见收到了，然后呢？ / We’ve Received Your Feedback. Now What?**
- Complete Simplified Chinese, edited Traditional Chinese, and independently written English in one reading-mode page. No external translation service or runtime Chinese conversion.
- Source editions: `data/method-introduction/{zh,zh-hant,en}.json`.
- Rebuild: `python3 -B scripts/build_method_introduction.py`; verify with `--check`.
- The five other language editions are **not** part of this update. Existing twelve-essay editions remain available; directory and Library distinguish their eight languages from the new introduction's three.

## Source and editorial approach

Based on Han Qin, *Remainder: A Portable Method* (M-00E),
<https://self-as-an-end.net/papers/sae-methodology-00e.html>,
DOI <https://doi.org/10.5281/zenodo.22849616>.

The complete Chinese paper was read and the introduction independently reviewed against it. The English rewrite received a separate complete review. The daily-life situations are explicitly invented examples, not reporting about a real employer or course.

The essay follows a scheduling request, a piano practice log, and a course-admission decision. It introduces the term “remainder” only after readers have followed the examples. A five-question note at the end makes the method usable without importing the paper's full apparatus.

Boundaries preserved:

- Relevance is assessed against an independently specified purpose, not inferred from the recorded classification or final result. Selecting the highest-scoring applicant is explicitly a **new purpose**, distinct from admitting everyone able to follow the course.
- The candidate is a particular item and variation, not a whole person. An irrelevant detail need not be recorded.
- Receipt and effective use differ, but archiving can itself complete an archiving task. Information used through another actual route cannot be called missing merely because one form omitted it.
- An unchanged or disappointing result does not establish non-use; a favorable result does not establish use. Evidence may be insufficient.
- A candidate can cease to be remainder when it actually enters handling. Finding an omission does not itself establish unfairness, require action, or cause another cycle.
- Four diagnostic types remain optional, non-exhaustive further reading rather than a checklist the essay forces onto every example.

## Integration

- Recommended starting point on the methodology index; formal order **00 → 00E → VIII**.
- Existing 00 and X gain short, separately styled notes distinguishing their ontological/structural arguments from this operational diagnostic. Their original Chinese and English article bodies are unchanged.
- Library preserves its original whole-card link to the series, with accurate edition counts. Its directory leads directly to the recommended introduction.
- Updated Latest entry, publication ledger, three localized search entries/descriptions, and sitemap. The new URL is canonical and is not advertised as having five nonexistent editions.
- Updated Traditional Chinese dictionaries for the existing index, 00, VIII, X and Library; versioned script references avoid stale navigation text.

## Verification

- Nine focused tests: complete prose, deterministic rendering, real language editions, local targets and source, directory order, previous/next links, registry metadata, localized search, sitemap, and update/Library integration.
- Builder freshness checks, publication-ledger consistency, content-registry validation, and `git diff --check`.
- Browser checks at 1280×800 and 390×844: one visible title/body per mode, 51 paragraphs and five checklist items per visible edition, no horizontal page overflow, localized document titles, and a usable mobile footer.
- Browser navigation verified: Library → methodology index → 00E; 00E → VIII → 00E retains Traditional Chinese. Existing 00's new note is constrained to the reading column. Temporary viewport reset and language returned to the initial English mode.

No commit or push performed by this task.
