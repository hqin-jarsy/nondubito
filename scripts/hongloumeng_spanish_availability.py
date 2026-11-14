"""Expose only the completed Spanish batches, without reading archived manuscripts."""
import json
from pathlib import Path
from build_hongloumeng_reading import checked_input_paths
from hongloumeng_japanese_availability import ReaderHTML
ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'classics/hongloumeng/es/'

def spanish_publication(root=None):
    root = Path(root) if root is not None else ROOT
    progress = root / 'data/hongloumeng/first80-spanish/progress.json'
    if not progress.exists():
        return None
    checked_input_paths([progress])
    last = json.loads(progress.read_text())['reviewed_through']
    if type(last) is not int or not 5 <= last <= 80 or last % 5:
        raise ValueError('Invalid Spanish batch boundary')
    names = ('index.html', 'edition.html', *(f'ch{n:03}.html' for n in range(1,last+1)))
    paths = tuple(root / PREFIX / name for name in names)
    checked_input_paths(paths)
    for path in paths:
        doc = ReaderHTML(path.read_text())
        if doc.language != 'es' or len(doc.ids) != len(set(doc.ids)):
            raise ValueError('Invalid Spanish page: ' + path.name)
        if path.name.startswith('ch') and (doc.articles != 1 or doc.closed_articles != 1 or not ''.join(doc.body).strip()):
            raise ValueError('Missing Spanish chapter text: ' + path.name)
    return dict(root=root.resolve(), paths=paths, reviewed_through=last)

def spanish_available(name, root=None):
    try:
        publication = spanish_publication(root)
        return publication is not None and name in {p.name for p in publication['paths']}
    except (ValueError, TypeError, KeyError, OSError):
        return False
