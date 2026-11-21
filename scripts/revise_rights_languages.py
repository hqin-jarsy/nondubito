#!/usr/bin/env python3
"""Restore the complete seven Rights essays in their existing five editions."""
from revise_quanli_languages import Series, main

RIGHTS = Series('Rights', 'rights', 'rights', 'h2')


if __name__ == '__main__':
    main(RIGHTS)
