# Theatre & Musicals

The shelf at `essays/theatre/index.html` contains thirty-five musical-theatre essays.
Hamilton was published on 2026-10-13; the other nineteen have their first website
publication date of 2026-10-18, regardless of drafting date. No new category is
created: Library category 18 is expanded.

On 2026-11-15, fifteen reviewed essays from three writing batches were added.
By the author's explicit choice, these fifteen have complete Simplified and
Traditional Chinese editions only. The first twenty retain their eight complete
language editions. Availability is marked per card; the Chinese-only articles
have no empty English body or nonexistent edition links. Their `data-editions`,
schema, hreflang and search records declare only Chinese.

The shared language shell falls back locally to Simplified Chinese when an incoming
English preference is unavailable, without overwriting the wider-site preference,
including on reload. An explicit Traditional Chinese choice does persist.
`recent-fiction.js` preserves an unsupported incoming query until the reader makes
a supported choice. Existing three-language switching behavior is unchanged.
This is an explicit `data-reader-languages` opt-in on the fifteen new pages;
older pages' differing edition-metadata conventions are not reinterpreted.

`data/theatre/catalog.json` is the ordered inventory, creator credits, topic labels,
publication dates and discovery copy. Each `<slug>.zh.md` and available `<slug>.en.md` has a
main title, an italic version/spoiler notice and the complete body. The English is
independently edited continuous prose preserving each Chinese paragraph’s argument,
not an excerpt or a shorter selection of sections. Traditional Chinese is rendered
using the existing CoreFoundation converter. Available same-page bodies share one
canonical URL and the existing language-selection shell. The newer Chinese-only
works set `languages: ["zh", "zh-hant"]` explicitly in the catalog.

The nineteen approved Chinese bodies are imported from the writing workspace’s
reviewed Markdown, moving title and any bibliographic footer to metadata. Three
early manuscripts received small argumentative additions during publication QA:
Hadestown distinguishes ongoing security from initial payment; Into the Woods
restores the child’s longer attachment within a quick exchange; Sunday in the Park
with George distinguishes appreciation of a whole from consenting to a fixed place.
Every new Chinese body exceeds 3,000 Han characters, excluding headings and notices.
The original Hamilton EN/Chinese manuscripts and publication date are unchanged.

`scripts/fixtures/theatre-2026-10-18-approved.json` fixes manuscript provenance,
Chinese and English body hashes, section counts and word/character counts. Research
and prior editorial checks are retained under `data/theatre/research/`. Public prose
does not carry external links or quoted lyrics. The final about note discloses the
research basis and absence of full-performance viewing; these are introductions and
analyses, not firsthand performance reviews.

`scripts/fixtures/theatre-2026-11-15-approved.json` records the fifteen source and
imported hashes, notice paragraph positions and conservative Han counts. Exact
received manuscripts remain under `data/theatre/received/20261115/`. Only the title
and existing bibliographic/version paragraph are moved to the reader-page header;
all prose is retained. The final five use the structural revisions approved after
the quality review, not the earlier ZIP. The fixture also protects 164 existing
files byte-for-byte: 40 original manuscripts, 105 separate foreign-language pages,
and 19 existing primary pages. Falsettos alone gains a next-article link.

Version distinctions must survive future editing: Cabaret uses the 1998 stage text;
Company uses male Bobby and the revised sequence including Marry Me a Little;
West Side Story, Wicked, Sweeney Todd and A Chorus Line must not silently import film
alterations. Clinical storylines in Next to Normal and Falsettos are not treatment
recommendations. The 1832 uprising in Les Misérables is not the 1789 Revolution.

Build and check:

```sh
python3 -B scripts/build_theatre.py
python3 -B scripts/build_home_updates.py
python3 -B scripts/refresh_theatre_discovery.py
python3 -B scripts/check_web_analytics.py --fix
python3 -B scripts/build_theatre.py --check
python3 -B scripts/refresh_theatre_discovery.py --check
python3 -B scripts/test_theatre.py
python3 -B scripts/check_site_updates.py
python3 -B scripts/check_web_analytics.py
```

The builder also owns only the marked theatre block in Library; other Library
content remains untouched. Homepage, Explore, Latest and `data/site-updates.json`
contain the editorial discovery update. Browser QA uses
`scripts/test_theatre_browser.cjs` with a loopback server: all thirty-five articles
in their available same-page languages and the shelf, mobile/desktop, language
switching and title searches. It also tests English-preference fallback and reload,
hidden unavailable controls, explicit Hant persistence, and return to English.
No command in this workflow commits or pushes.

Sitemap regeneration preserves the committed sitemap’s recorded dates for pages
not being changed. New/dirty pages get the current date, with Git dates as fallback
only for URLs without recorded dates. This prevents earlier analytics-only commits
from making thousands of untouched pages appear newly revised in this publication.
