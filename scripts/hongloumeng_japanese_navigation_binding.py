"""Bounded, reversible Japanese navigation in the existing reader pages.

The hash-pinned navigation binding and its predecessor replay were retired on
2026-11-13 with the rest of the binding chain; its record
(data/hongloumeng/first80-english/japanese-navigation-binding.json) stays as
historical evidence. Current checks: the Japanese reader must validate exactly
(require_japanese_reader), and every builder output, including these exact
reversible insertions, must equal the files on disk.
"""
from pathlib import Path
from integrate_hongloumeng_japanese import transform

ROOT = Path(__file__).resolve().parents[1]


def require_japanese_reader(root=ROOT):
    from hongloumeng_japanese_availability import japanese_publication
    if japanese_publication(root) is None:
        raise ValueError('Japanese navigation requires a verified Japanese reader')


def navigation_outputs(prefix, pages):
    """Pure postprocessing; callers retain their independent publication gates."""
    return {name: (transform(prefix+name, value.encode() if isinstance(value, str) else value).decode()
                   if name.endswith('.html') else value) for name, value in pages.items()}
