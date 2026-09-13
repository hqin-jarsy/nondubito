# Book Introductions / 书籍导读

The discovery entrance is `essays/books/index.html`. Its sibling shelves are
Recent Fiction (`essays/recent-fiction/`, existing URLs unchanged) and Nonfiction
(`essays/nonfiction/`). This is distinct from the long-form Literary Readings
and Science Fiction close-reading series. Nonfiction is not limited to new books.

## Editorial source and scope

Manuscripts live in `/Users/hanqin/Documents/SAE介绍`; do not edit those sources
when building the site. `data/nonfiction/*.json` holds the lightly edited Chinese,
independently written English, book metadata, sources and reading-scope notes.
Traditional Chinese is rendered with the existing converter and visually checked.

- Keep first publication separate from the guide date. A year-only book date
  such as `1973` stays a year; never manufacture January 1 to fit a schema.
- Distinguish author claims, later research, institutional self-descriptions,
  and the guide's own arguments or illustrative examples.
- Do not imply a full-book reading when the basis is original excerpts and
  supporting research. Explain scope in the source note; any practical safety
  boundary should also be apparent before reading the article.
- Sources can be `excerpt`, `interview`, `publisher`, `review`, `research`, or
  `institution`. An author interview is not compulsory. Original excerpts are
  required by the presently supported reading bases (`excerpt`,
  `excerpts-and-interviews`, `excerpts-and-research`). If introducing another
  basis, implement its visible reading limits and tests first.
- A source described as an opening must actually be an opening, not an arbitrary
  selected passage. Contemporary editions, translations and adaptations have
  their own dates and titles.
- Every inline HTTPS source is registered in the source cards. Do not fabricate
  interviews, trial passages, book names or unverified source descriptions.

## Adding a book

Add one JSON and register its slug in `scripts/build_book_introductions.py:ORDER`.
Include `topic_en`, `topic_zh`, `genre_en`, `genre_zh` alongside the fields used by
Recent Fiction. The nonfiction shelf uses editorial order, with genres as labels;
it does not split two books into separate year/category sections. Expand browsing
only when the collection warrants it.

The hub counts the two inventories automatically. Its featured block shows the
first two nonfiction books; reconsider editorial order when a new batch arrives.
The nonfiction Library block is generated between `NONFICTION CATEGORY` markers;
the fiction builder independently owns `RECENT FICTION CATEGORY` markers.
Curated homepage/Explore/Latest updates and overall Library statistics remain manual.

## Build and verify

```sh
python3 scripts/build_recent_fiction.py
python3 scripts/build_book_introductions.py
python3 scripts/build_content_registry.py
python3 scripts/build_search_index.py
python3 scripts/build_sitemap.py
python3 scripts/audit_reader_context.py
python3 scripts/test_book_introductions.py
python3 scripts/test_recent_fiction.py
python3 scripts/check_site_updates.py
python3 scripts/normalize_canonicals.py --check
git diff --check
```

All build commands support `--check`. Browser QA covers the two entrances, both
articles, the three reading languages, the mobile menu, source anchors, and search
by title/author. Search uses localized visible decks and preserves the selected
language on result links for both new paths.

Rendering reuses the safe prose helpers, language script, typography and document
shell from Recent Fiction. Only `head()` has collection parameters; the novel
builder's editorial content, source rules, date ordering and 43 URLs remain separate.
