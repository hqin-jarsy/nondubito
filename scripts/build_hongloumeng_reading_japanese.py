#!/usr/bin/env python3
"""Check the hand-edited Japanese HTML. This command never writes reader files.

The former JSON renderer was retired when HTML became the sole text source.
Use git history for the old renderer; archived drafts are not publishing inputs.
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Historical inventory, also used by the archived private-review helper.
PARTIAL = {6: 3, 9: 2, 12: 1, 65: 4, 75: 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check only (also the default)')
    parser.parse_args()
    from hongloumeng_japanese_availability import japanese_publication
    result = japanese_publication(ROOT)
    if result is None:
        raise SystemExit('Japanese reader is missing; restore HTML from git, not archived JSON.')
    print(f"Checked 80 hand-edited Japanese chapters; {result['ownerPlaceholders']} incomplete markers. No files written.")


if __name__ == '__main__':
    main()
