# Meaning Theory: independent language editions

Write one UTF-8 JSON file per edition in `data/meaning/{ja,fr,de,es,ko}.json`.
The source is the **current polished** Chinese and independent English in
`essays/meaning/ep01.html` through `ep08.html`, not the older academic-style
prose. Read `docs/meaning-series.md` for boundaries that simplification must keep.

Each language file is hand-authored prose, rendered by the shared publisher.
Do not call a translation service. Do not replace a full essay with an abstract.
Native paragraph order and sentence rhythm can differ. Preserve the actual
argument and its important limits, the imagined nature of the examples, and
the first-seven-plus-optional-eighth reading route. Use ordinary language;
avoid DD numbering and imported jargon that the current prose has removed.

## File structure

All prose fields contain plain text, not HTML or Markdown. Use typographic
quotation marks as appropriate. `heading` may be an empty string for an opening
scene; all other fields below are required and nonempty. Articles must be in
the order ep01–ep08, with unique titles and descriptions.

```json
{
  "language": "fr",
  "series_label": "Native name for SAE Meaning Theory",
  "series_title": "Native title for The Meaning of a Life Lies Outside It",
  "description": "A short native-language search/social summary",
  "intro": ["Three natural paragraphs introducing the life questions."],
  "reading_note": "Read from the start or choose a question; first seven complete the main argument, eighth optional; no prior theory required.",
  "start_label": "Begin with the notebook →",
  "source_note": "Eight essays drawn from five academic papers; each links to its source for the fuller argument.",
  "edition_note": "An independent edition written for readers of this language.",
  "count_label": "8 essays · 8 languages",
  "ui": {
    "home": "Essays",
    "start": "Start here",
    "library": "Library",
    "about": "About",
    "theory": "SAE Theory",
    "language": "Language",
    "contents": "Series contents",
    "previous": "Previous essay",
    "next": "Next essay",
    "further": "Further reading",
    "academic_source": "Academic source"
  },
  "articles": [
    {
      "slug": "ep01",
      "title": "Native essay title",
      "description": "A concrete, inviting 1–2 sentence description, not a technical abstract.",
      "sections": [
        {"heading": "A native section heading", "paragraphs": ["A complete prose paragraph.", "Another."]}
      ]
    }
  ]
}
```

This schema is illustrated in English for clarity; replace every reader-facing
field with the target language. Keep `language`, keys, and `ep01`…`ep08` as shown.
Do not copy the placeholder text. Do not edit generated HTML, other languages,
or shared navigation while authoring one edition.
