"""Root-scoped, uncached English publication validation. Never trusts existence."""
import json
from pathlib import Path
import stat
from build_hongloumeng_reading import checked_input_paths

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'classics/hongloumeng/en/'
NAMES = frozenset(('index.html', 'edition.html', 'reader.css', 'reader.js', *(f'ch{n:03d}.html' for n in range(1,81))))


def validate_english_inventory(root, plan):
    """Pure exact-inventory gate; also used by explicitly synthetic layout tests.

    A caller-supplied plan is not acceptance. Production calls only use the plan
    returned by the real current validator and exact-input approval below.
    """
    root=Path(root).absolute(); target=root/PREFIX
    if set(plan) != {PREFIX+n for n in NAMES}:
        raise ValueError('English plan must contain exactly eighty chapters and four reader files')
    checked_input_paths(root/name for name in plan)
    if target.is_symlink() or not target.is_dir():
        raise ValueError('Invalid English reader directory')
    actual=set()
    for path in target.rglob('*'):
        info=path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError('English reader contains directory, alias or nonregular file')
        actual.add(path.relative_to(target).as_posix())
    if actual != NAMES:
        raise ValueError('English reader inventory differs from exact output plan')
    for name,value in plan.items():
        expected=value.encode('utf-8') if isinstance(value,str) else value
        if (root/name).read_bytes() != expected:
            raise ValueError('Stale English reader output: '+name)
    return tuple(root/PREFIX/n for n in sorted(NAMES) if n.endswith('.html'))


def english_publication(root=None):
    """Validate once per operation; no permanent cache or import-time result."""
    root=Path(root) if root is not None else ROOT
    marker=root/'data/hongloumeng/first80-english/reading-publication.json'
    if not marker.exists():
        return None
    checked_input_paths([marker])
    approval=json.loads(marker.read_text())
    from build_hongloumeng_reading_english import production_plan
    plan=production_plan(approval, root=root)
    paths=validate_english_inventory(root,plan)
    from hongloumeng_reading_presentation_binding import binding
    presentation=binding(root)
    modified=[name for name,row in presentation['changedRootWitnesses'].items() if row['kind']=='html']
    modified.append(presentation['continuationDirectoryDisplay']['path'])
    return dict(root=root.resolve(), date=approval['publicationDate'], paths=paths, modifiedPaths=tuple(modified))


def english_published(root=None):
    try:
        return english_publication(root) is not None
    except (ValueError,KeyError,TypeError,OSError):
        return False
