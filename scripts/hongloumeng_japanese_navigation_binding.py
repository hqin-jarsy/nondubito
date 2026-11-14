"""Bounded, reversible Japanese navigation in the existing reader pages.

The hash-pinned navigation binding and its predecessor replay were retired on
2026-11-13 with the rest of the binding chain; its record
(data/hongloumeng/first80-english/japanese-navigation-binding.json) stays as
historical evidence. Current checks: the hand-edited Japanese reader must pass structural checks
(require_japanese_reader), and other language builder outputs, including these exact
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
    from integrate_hongloumeng_french import navigation_outputs as french_navigation
    from integrate_hongloumeng_german import navigation_outputs as german_navigation
    from integrate_hongloumeng_spanish import navigation_outputs as spanish_navigation
    from integrate_hongloumeng_korean import navigation_outputs as korean_navigation
    return korean_navigation(prefix, spanish_navigation(prefix, german_navigation(prefix, french_navigation(prefix, {name: (transform(prefix+name, value.encode() if isinstance(value, str) else value).decode()
                   if name.endswith('.html') else value) for name, value in pages.items()}))))
