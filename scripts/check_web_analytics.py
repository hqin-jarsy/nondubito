#!/usr/bin/env python3
"""Check every public page; --fix repairs analytics without editing page copy."""
import argparse
from web_analytics import ROOT, audit, conflict_copies, ensure_analytics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fix', action='store_true')
    args = parser.parse_args()
    count, errors = audit()
    if args.fix:
        for path, _ in errors:
            path.write_text(ensure_analytics(path.read_text(encoding='utf-8')), encoding='utf-8')
        print(f'Repaired {len(errors)} public pages')
        count, errors = audit()
    for path, problem in errors:
        print(f'ERROR: {path.relative_to(ROOT)}: {problem} Cloudflare Web Analytics')
    copies = conflict_copies()
    for path in copies:
        print(f'ERROR: {path.relative_to(ROOT)}: unpublished filesystem conflict copy; back up and remove manually')
    failed = bool(errors or copies)
    print(f'{"FAIL" if failed else "OK"}: {count} public pages checked; {len(errors)} tracking errors; {len(copies)} conflict copies')
    return failed


if __name__ == '__main__':
    raise SystemExit(main())
