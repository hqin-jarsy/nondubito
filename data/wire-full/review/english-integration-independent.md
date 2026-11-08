# Independent English and integration review

Reviewed the complete current English bodies for essays 01–09 against data/wire-full/source and all 29 exact author-approved Chinese block corrections. Reviewed build_wire_full_editions.py, refresh_wire_full_discovery.py, test_wire_full_editions.py, test_wire_full_browser.cjs, wire-language.js, and the limited shared changes in search.js, build_collection_languages.py, and site-integrity.yml.

## Result

No blocking translation, argument-chain, routing, or builder defect found. The independent English editions preserve the major arguments, examples, qualifications, and reader questions without requiring paragraph alignment. Approved factual corrections are reflected, including Wallace and Brandon, the container deaths, Ziggy’s wounded employee, the teacher-role limitation, Bunk’s visit to Randy, Namond’s penultimate-episode debate, the prison yard, Poot, Greggs and Walon, and the season-four Colvin/Wee-Bey meeting. The incorrect classroom episode number is not asserted in English.

## Narrow addition

Essay 08 omitted source block 50 between school exclusion and the later request for money. Added two sentences about Dukie’s scrap-cart work as the only place willing to take him and its eventual loss. This supports the existing argument that care needs a place to land. Exact changes are recorded in en-08-two-boys-changes.json and en-batch02.md. No Chinese, generated HTML, or shared code was changed by this reviewer.

## Checks and finalization

At the time of the read-only checks, refresh_wire_full_discovery.py --check passed. Eight of nine Python unit tests passed; test_build_matches_checked_in_pages failed only because de/05-the-school.html lacked a newly added comma in its canonical JSON. Rebuild and rerun after all workers finish.

The editorial accepted.json receipt was absent at review time, so its optional hash gate was not active. Freeze the final receipt after acceptance. The browser test’s search loop covered only the first article despite its first-and-last comment; the coordinator is extending it. Browser code was inspected, not executed by this reviewer.

This is a source-to-edition and integration review, not a new frame-by-frame verification of all factual claims in the published Chinese essays. No commit or push performed.
