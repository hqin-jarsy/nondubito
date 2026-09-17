# SAE Meaning Theory

The public entrance is `essays/meaning/index.html`. There are eight essays with
English, Simplified Chinese, and an offline Traditional Chinese reading mode,
plus separate Japanese, French, German, Spanish, and Korean editions. All five
are independently written, full-length essays from the polished Chinese and
English, not automatic translations. Their authored sources live in
`data/meaning/{ja,fr,de,es,ko}.json`; see `docs/meaning-localization.md` for schema.
Do not expose a language link before its target is published. Each new foreign
edition should be an independent essay, checked against the Chinese meaning,
not a translation of the English vocabulary alone.

Run `python3 -B scripts/build_meaning_languages.py` to publish all five editions,
their language-hub cards and reciprocal per-essay menus. `--check` verifies
reproducibility. Run `build_meaning_traditional.py`, `build_search_index.py` and
`build_sitemap.py` after publication. Regression checks are `test_meaning.py`,
`check_site_updates.py --check`, and `test_meaning_browser.cjs` against a local
server. The native dropdown preserves the original links in the HTML;
foreign-edition links remain usable without JavaScript. EN/Simplified/Traditional
use the existing inline-mode script and remain modes of the same canonical URL;
hreflang describes only independently addressable editions, not query variants.

## Editorial approach

The September prose revision replaces definition-first exposition with imagined
people and ordinary situations. The notebook, an inherited career, a drawing
book, a missed conversation, and a distant friend carry the distinctions. They
are illustrative scenes, not reported cases. The first seven essays complete the
main argument; essay eight is optional philosophical dialogue. Academic sources
remain linked after each article. Preserve the existing publication date rather
than deriving it from file changes.

- Meaning here concerns how someone relates to their own life across time. It
  is not a score, and this deliberately limited question does not invalidate
  other questions about worthwhile lives, happiness, ethics, or suffering.
- Something genuinely chosen then, something mistakenly taken as one's own,
  and what one says about either today are different. A new understanding does
  not retroactively make a choice happen or erase the years that followed it.
- Clearing away imposed expectations can help without revealing a fully made
  self. Better self-understanding is possible without a final, unrevisable self.
- No universal outside certification does not mean all evidence is useless or
  that the person cannot be wrong. Strong universal claims belong to the source
  theory; examples illustrate them, rather than proving them on their own.
- A life may turn outward without having to earn its worth through usefulness.
  An open place for another is not assumed to have formed in everyone already.
  Care must leave room for refusal, changed direction, and exit. Practical
  dependence does not give the supporter ownership of another person's value.
- Later benefits do not, by themselves, justify earlier harm. An opportunity
  that cannot return is not made interchangeable with a similar new one.
- Disability or inability to communicate is not proof of a subject's absence.
  The series' reservation about death and the ultimate first-person boundary
  is a philosophical limit, not medical guidance or evidence of an afterlife.
  Surviving works and influence do not demonstrate the author's continued
  first-person life or ownership of what later readers make their own.
- Dialogue with another philosopher is not a victory by definition. Preserve
  Kant's distinction between a practical postulate and theoretical proof,
  Ricoeur's sameness/selfhood distinction, and the distinction between lasting
  deeds or words and the original person's continued first-person experience.

The episode-three example enters the profession at twenty-two and changes it at
forty-two, after twenty years. Keep this consistent across editions.

## Publishing and checks

After editing the Chinese, regenerate the dictionaries on macOS using the same
offline CoreFoundation conversion already used elsewhere on the site, then
proofread them. No translation service is involved.

```sh
python3 -B scripts/build_meaning_languages.py
python3 -B scripts/build_meaning_traditional.py
python3 -B scripts/build_search_index.py
python3 -B scripts/build_sitemap.py
python3 -B scripts/test_meaning.py
python3 -B scripts/check_site_updates.py --check
python3 -B scripts/build_search_index.py --check
python3 -B scripts/build_sitemap.py --check
```

Start a local static server and run the browser checks with Playwright available:

```sh
MEANING_BROWSER_CHANNEL=chrome node scripts/test_meaning_browser.cjs http://127.0.0.1:8768
```

They cover all 54 pages at desktop, mobile, and narrow-mobile widths; language
switches and round trips; explicit query-language priority; and reading when
local storage is unavailable. `MEANING_SCREENSHOTS` can name an existing output
directory for representative visual checks. The test also follows all eight
language-specific search results into an essay and checks the Library card in
Traditional Chinese. Foreign editions remain readable without JavaScript;
the three inline editions preserve their mode when following series links even
if local storage is blocked.
