#!/usr/bin/env python3
"""Verify KOE's R2 objects, or the exact outside-repository upload files."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from io import BytesIO
import json
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def check(record, local_dir=None):
    try:
        if local_dir:
            raw = (local_dir / record['filename']).read_bytes()
        else:
            request = Request(record['url'], headers={'User-Agent': 'NonDubito-Image-Verification/1.0'})
            with urlopen(request, timeout=30) as response:
                if response.headers.get_content_type() != record['content_type']:
                    raise ValueError('Content type mismatch')
                raw = response.read()
        if len(raw) != record['bytes']:
            raise ValueError('Byte length mismatch')
        if hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('SHA-256 mismatch')
        with Image.open(BytesIO(raw)) as image:
            if list(image.size) != record['dimensions'] or image.format != record['format']:
                raise ValueError('Image format/dimensions mismatch')
        return None
    except Exception as exc:
        return f"{record['filename']}: {exc}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT / 'data/koe-image-hosting.json')
    parser.add_argument('--local-dir', type=Path, help='Exact flat upload directory outside Git')
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    records = list(manifest['images'].values())
    if not records:
        parser.error('No images to verify')
    keys = [record['object_key'] for record in records]
    if len(keys) != len(set(keys)):
        parser.error('Duplicate object keys')
    with ThreadPoolExecutor(max_workers=4) as pool:
        errors = [error for error in pool.map(lambda record: check(record, args.local_dir), records) if error]
    for error in errors:
        print('FAIL', error)
    print(f"{len(records)-len(errors)}/{len(records)} images verified; {sum(r['bytes'] for r in records):,} expected bytes; SHA-256, format and dimensions checked.")
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
