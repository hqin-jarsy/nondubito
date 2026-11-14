"""Bounded validation of the current French reader, never archived review data.

Publication means structurally available, not literary acceptance or a claim
that explicitly marked author passages have been completed.
"""
from pathlib import Path
from build_hongloumeng_reading import checked_input_paths
from hongloumeng_japanese_availability import ReaderHTML

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'classics/hongloumeng/fr/'
HTML_NAMES = frozenset(('index.html', 'edition.html',
                        *(f'ch{n:03d}.html' for n in range(1, 81))))
NAMES = HTML_NAMES | {'reader.css', 'reader.js'}


def french_publication(root=None):
    root = Path(root) if root is not None else ROOT
    target = root / PREFIX
    if not target.exists():
        return None
    # Validate all names and ancestors before opening any page, including aliases.
    checked_input_paths(target / name for name in NAMES)
    if {path.name for path in target.iterdir()} != NAMES:
        raise ValueError('French reader inventory differs from expected files')
    for name in sorted(HTML_NAMES):
        doc = ReaderHTML((target / name).read_text(encoding='utf-8'))
        if doc.language != 'fr' or len(doc.ids) != len(set(doc.ids)):
            raise ValueError('Invalid French language or duplicate IDs: ' + name)
        if not name.startswith('ch'):
            continue
        number = int(name[2:5])
        if doc.articles != 1 or doc.closed_articles != 1 or not ''.join(doc.body).strip():
            raise ValueError('Missing French article: ' + name)
        required = {'index.html'}
        if number > 1:
            required.add(f'ch{number-1:03d}.html')
        if number < 80:
            required.add(f'ch{number+1:03d}.html')
        else:
            required.add('/originals/hongloumeng/fr/ch081.html')
        if not required <= doc.links:
            raise ValueError('Missing French chapter navigation: ' + name)
    return dict(root=root.resolve(), paths=tuple(target / name for name in sorted(HTML_NAMES)),
                literaryAcceptance=False)


def french_published(root=None):
    try:
        return french_publication(root) is not None
    except (ValueError, TypeError, OSError):
        return False
