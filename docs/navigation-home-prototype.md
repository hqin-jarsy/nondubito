# Navigation and home prototype notes

Prototype: `prototypes/home-v1.html`  
Status: archived prototype, `noindex`, not linked from public pages. Its tested
navigation and homepage hierarchy have since been implemented on the public
site; the current state is recorded in `information-architecture-rollout.md`.

## What this prototype tests

- A six-item global shell: Start Here, Explore, Latest, Search, About, Language;
- Search remains visible on mobile while the longer navigation collapses;
- Language selection becomes one stable utility instead of a wide row;
- The homepage changes from a complete catalogue to an editorial reception page;
- Five interest-led doors replace dozens of top-level series sections;
- Latest distinguishes new work, substantive revisions, and language expansions;
- Reading paths provide sequence without forcing readers through the full Library;
- Full Library remains available as the exhaustive inventory.

## Deliberate non-decisions

- The cards in Latest demonstrate hierarchy only; the final order and dates must
  come from the reviewed content registry.
- The five Explore cards are not yet linked to public pages because those pages
  do not exist.
- Japanese, French, German, Spanish, and Korean labels use their current language
  hubs; localized versions of the new global shell belong to the later language
  rollout.
- The prototype does not implement real search.

## Responsive behavior

- Desktop: primary navigation, search, and compact language picker share one row.
- Tablet and mobile: primary navigation moves into a drawer; search remains in
  the fixed header; the eight-language row scrolls only inside the drawer.
- At 660px and below, all content grids become a single column and calls to
  action become full width.

## Before public rollout

1. Render at desktop, tablet, and phone widths.
2. Confirm there is no horizontal overflow.
3. Confirm keyboard access to the language picker and mobile menu.
4. Replace placeholder Explore links with the new Explore page.
5. Replace prototype Latest cards with registry-backed data.
6. Remove the prototype banner only when the public page is ready.

## Prototype QA completed

| Viewport | Result |
| --- | --- |
| 390 × 844 | No horizontal overflow; single-column cards; search and menu remain visible |
| 768 × 1024 | No horizontal overflow; collapsed primary navigation |
| 1440 × 1000 | No horizontal overflow; full primary navigation and language utility visible |

Interaction checks passed for opening the mobile drawer, updating
`aria-expanded`, switching from Chinese to English, hiding the inactive
language, updating the current-language label, and avoiding duplicate element
IDs.
