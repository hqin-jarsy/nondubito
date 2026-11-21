#!/usr/bin/env python3
"""Restore complete First Critique essays within their existing page shells."""
from revise_quanli_languages import Series, main

CRITIQUE = Series('First Critique', 'sae-first-critique', 'critique', 'h2',
                  count=12, reference_emphasis=('ep03',))


if __name__ == '__main__':
    main(CRITIQUE)
