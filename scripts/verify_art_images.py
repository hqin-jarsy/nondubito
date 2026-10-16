#!/usr/bin/env python3
"""Check R2 images (or staged files) against the committed provenance ledger.

No credentials or writes. Default: fetch each published image over HTTPS.
--local-dir /outside/repo/upload/art validates the exact files to upload.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from io import BytesIO
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import time
from PIL import Image
import build_art as b


def entries(work_id=None):
    for key,entry in json.loads((b.DATA/'web-images.json').read_text()).items():
        wid,name=key.split('/',1)
        if work_id and wid!=work_id: continue
        for width,preview in entry['previews'].items():
            yield {'id':wid},name,int(width),preview
    legacy=b.ROOT/'data/legacy-image-hosting.json'
    if work_id=='legacy':
        for record in json.loads(legacy.read_text()).values():
            yield {'id':'legacy'},record['filename'],0,record


def check(item,local_dir=None):
    work,name,width,expected=item
    label=expected.get('filename') or b.preview_filename(work,name,width)
    try:
        if local_dir:
            data=(local_dir/label).read_bytes()
        else:
            request=Request(expected.get('url') or b.preview_url(work,name,width),headers={'User-Agent':'NonDubito-Image-Verification/1.0'})
            for attempt in range(3):
                try:
                    with urlopen(request,timeout=30) as response:
                        if response.headers.get_content_type()!=expected.get('content_type','image/webp'):
                            raise ValueError('Unexpected image content type')
                        data=response.read()
                    break
                except HTTPError:
                    raise
                except (URLError,ConnectionError,TimeoutError):
                    if attempt==2: raise
                    time.sleep(.5*(attempt+1))
        if len(data)!=expected['bytes']: raise ValueError('Byte length mismatch')
        if hashlib.sha256(data).hexdigest()!=expected['sha256']: raise ValueError('SHA-256 mismatch')
        with Image.open(BytesIO(data)) as image:
            if image.format!=expected.get('format','WEBP') or list(image.size)!=expected['dimensions']:
                raise ValueError('Image format/dimensions mismatch')
        return label,None,len(data)
    except Exception as exc:
        return label,str(exc),0


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-dir',type=Path)
    parser.add_argument('--work',help='Only validate one work ID')
    args=parser.parse_args()
    items=list(entries(args.work))
    if not items: parser.error('No matching images')
    names=[p.get('filename') or b.preview_filename(w,n,width) for w,n,width,p in items]
    if len(names)!=len(set(names)): parser.error('Duplicate object keys')
    with ThreadPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(lambda item:check(item,args.local_dir),items))
    failures=[(name,error) for name,error,_ in results if error]
    for name,error in failures: print(f'FAIL {name}: {error}')
    print(f'{len(results)-len(failures)}/{len(results)} images verified; {sum(size for _,_,size in results):,} bytes; SHA-256, image format/dimensions and content type checked.')
    raise SystemExit(bool(failures))


if __name__=='__main__': main()
