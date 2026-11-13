"""Exact, uncached Japanese reader inventory; incomplete owner slots stay explicit.

This is structural/public-output validation, not new literary acceptance.
"""
import json
from pathlib import Path
import stat
from build_hongloumeng_reading import checked_input_paths

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'classics/hongloumeng/ja/'
NAMES = frozenset(('index.html', 'edition.html', 'reader.css', 'reader.js',
                   *(f'ch{n:03d}.html' for n in range(1, 81))))


def japanese_publication(root=None):
    root = Path(root) if root is not None else ROOT
    target = root / PREFIX
    if not target.exists():
        return None
    from build_hongloumeng_reading_japanese import PARTIAL, load_chapters, render
    from hongloumeng_japanese_pipeline import validate, validate_partial
    data = root / 'data/hongloumeng/first80-japanese'
    source = root / 'data/hongloumeng/first80-public/reading.zh.json'
    drafts = [data / 'chapters' / f'ch{n:03d}.{"partial" if n in PARTIAL else "draft"}.json'
              for n in range(1, 81)]
    checked_input_paths([source, *drafts])
    chapters = json.loads(source.read_bytes())['chapters']
    if len(chapters) != 80:
        raise ValueError('Japanese source must contain eighty chapters')
    for n, (chapter, path) in enumerate(zip(chapters, drafts), 1):
        (validate_partial if n in PARTIAL else validate)(chapter, json.loads(path.read_bytes()))
    plan = render(load_chapters(data))
    if set(plan) != NAMES:
        raise ValueError('Japanese output plan differs from exact inventory')
    checked_input_paths(target / name for name in NAMES)
    if target.is_symlink() or not target.is_dir():
        raise ValueError('Invalid Japanese reader directory')
    actual = set()
    for path in target.iterdir():
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError('Japanese reader contains directory, alias or nonregular file')
        actual.add(path.name)
    if actual != NAMES:
        raise ValueError('Japanese reader inventory differs from exact output plan')
    for name, value in plan.items():
        expected = value.encode('utf-8') if isinstance(value, str) else value
        if (target / name).read_bytes() != expected:
            raise ValueError('Stale Japanese reader output: ' + name)
    return dict(root=root.resolve(), paths=tuple(target / name for name in sorted(NAMES)
                                               if name.endswith('.html')),
                completeChapters=75, partialChapters=5, ownerPlaceholders=11,
                literaryAcceptance=False)


def japanese_published(root=None):
    try:
        return japanese_publication(root) is not None
    except (ValueError, KeyError, TypeError, OSError):
        return False
