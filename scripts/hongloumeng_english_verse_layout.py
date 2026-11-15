"""Presentation-only verse layout for the approved English reader HTML.

Apply after rendering: content is taken exclusively from the supplied HTML.
Source approvals, paragraph anchors and the translated wording stay unchanged.
"""
import re


_INVOCATION_STYLE = (
    '<style id="invocation-song-layout">'
    'article p.invocation-stanza{margin-top:0;margin-bottom:0;text-indent:0}'
    'article p.invocation-intro{margin-bottom:0}'
    'article span.invocation-verse{display:block;white-space:pre-line;text-indent:0}'
    '.novel-text span.invocation-verse{margin-left:1.5em}'
    'article span.invocation-first{margin-top:1.1em}'
    'article span.invocation-last{margin-bottom:1.4em}'
    '@media(max-width:540px){.novel-text span.invocation-verse{margin-left:.5em}}'
    '</style>'
)


def _paragraph(text, anchor, transform):
    """Transform exactly one anchored paragraph, failing on renderer drift."""
    pattern = re.compile(
        r'(<p\b(?=[^>]*\bid="' + re.escape(anchor) + r'")[^>]*>)(.*?)(</p>)',
        re.DOTALL,
    )
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise ValueError('Expected one English verse paragraph: ' + anchor)
    return pattern.sub(lambda m: transform(*m.groups()), text)


def _verse_paragraph(position):
    def transform(opening, body, closing):
        opening, count = re.subn(
            r'\bclass="[^"]*"', 'class="verse layout-' + position + '"', opening
        )
        if count != 1:
            raise ValueError('Expected an English paragraph class')
        return opening + body + closing
    return transform


def _invocation_stanza(position):
    def transform(opening, body, closing):
        # A second application must leave all whitespace and markup untouched.
        if re.search(r'<span\b[^>]*\bclass="[^"]*\binvocation-verse\b', body):
            return opening + body + closing
        opening, count = re.subn(
            r'\bclass="([^"]*)"',
            lambda m: 'class="' + m.group(1) + ' invocation-stanza"', opening,
        )
        if count != 1:
            raise ValueError('Expected an English paragraph class')
        classes = 'verse invocation-verse' + (' invocation-' + position if position else '')
        return opening + '<span class="' + classes + '">' + body.strip() + '</span>' + closing
    return transform


def apply(text, name):
    """Return an idempotent presentation repair; never read files or mutate input.

    ``name`` may be a chapter filename or its relative/absolute path. The English
    source already supplies the poetic line breaks; keep those rather than
    re-translating, copying a live page, or hard-coding any poem text.
    """
    name = str(name).replace('\\', '/').rsplit('/', 1)[-1]
    if name == 'ch005.html':
        for anchor, position in (('hlm-c005-b0117-s1', 'first'), ('hlm-c005-b0118-s1', 'last')):
            text = _paragraph(text, anchor, _verse_paragraph(position))
    elif name == 'ch078.html':
        for anchor, position in (
            ('hlm-c078-b0089-s2', 'first'),
            ('hlm-c078-b0090-s1', ''),
            ('hlm-c078-b0091-s1', ''),
            ('hlm-c078-b0092-s1', 'last'),
        ):
            text = _paragraph(text, anchor, _invocation_stanza(position))
        if 'id="invocation-song-layout"' not in text:
            if text.count('</head>') != 1:
                raise ValueError('Expected one English HTML head')
            text = text.replace('</head>', _INVOCATION_STYLE + '</head>', 1)
    return text
