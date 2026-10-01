# Nonfiction publication QA — 2026-09-30

## Scope and editorial checks

Seven new guides: The Art of Gathering, Four Thousand Weeks, The Craftsman,
The Serviceberry, The Sound of a Wild Snail Eating, Palaces for the People,
and The Other Significant Others. The nonfiction shelf now contains 12 books;
the parent Book Introductions entrance contains 55, including 43 existing novels.

All seven approved Chinese manuscripts from the writing workspace's `outputs/`
folder were imported without changes after removing only their title and italic
bibliographic paragraph. Fixed SHA256 expectations protect those bodies in the
regression tests. Complete English renderings contain 1,417–1,753 words each;
Traditional Chinese is generated through the existing converter. Source links
remain outside the prose. The original five guides' three rendered article
bodies were also compared directly with HEAD and are unchanged. Their related
navigation now includes the seven new guides; their editorial dates are retained.

The reading notices distinguish excerpts, later interviews, and the guide's
own discussion from full-book reading. Palaces for the People uses the new
`interviews-and-research` basis with a publisher CTA, not an invented excerpt.
The Serviceberry identifies its precursor essay explicitly. The Craftsman
source note identifies the later Arabia tureen correctly and does not conflate
it with a book episode. Individual reader reviews are not described as platform
consensus. Unverified Chinese editions and medical or legal conclusions are
not invented.

Homepage, Latest, the update ledger, book hub, nonfiction shelf, Library, search,
and sitemap are integrated. The two featured nonfiction cards now introduce
gathering and time. No existing novel or other essay source was changed.

## Automated checks

- Nonfiction regression suite: 17 tests passed, including exact source hashes,
  language editions, source validation, publication metadata, discovery, and
  the interview-only reading basis.
- Recent Fiction regression suite: 13 tests passed.
- Recent Fiction, Book Introductions, content registry, search index, sitemap,
  and reader-context audit all pass their build `--check` modes.
- Update ledger and Latest agree; canonical URL normalization check passes.
- `git diff --check` passes.

An initial sitemap assertion ran before the concurrent sitemap build finished;
the completed build and repeated regression suite pass. The generated audit
also catches up with previously committed changes elsewhere in the site, and
the sitemap includes an already-committed September 30 aesthetics page. These
are generated inventory changes, not edits to those essays.

## Browser and visual checks

The isolated local Chrome run passed 205 checks:

- 126 combinations: two entrances plus 12 articles, three languages, widths
  1440 / 390 / 320 pixels.
- One visible language body and title, all manuscript sections, source anchors,
  working mobile menus, and no horizontal overflow.
- Language changes and reloads preserve language selection and URL fragments.
- Hub, shelf, article, related article, and return navigation work.
- 60 title/author searches cover ten recently added guides in three languages;
  result links open the chosen reading edition.
- No page JavaScript errors or failed local resources.

The desktop Simplified Chinese hub and mobile Traditional Chinese friendship
article (hero and prose) were visually inspected. Screenshots remain outside
the repository in the writing workspace's `work/nonfiction-publication/screenshots`.
Chrome initially failed to launch in the sandbox; the isolated test succeeded
with the required execution permission and did not access a personal browser profile.

## Deployment boundary

These are local pre-publication checks. The repository requires separate user
confirmation before pushing, including when the request says to publish. No
remote push or live deployment is claimed by this report; those must be checked
after confirmation.
