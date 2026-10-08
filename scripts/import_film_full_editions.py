#!/usr/bin/env python3
"""One-time, byte-preserving import of numbered film batches; never edit delivery."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'data/film-full'
SOURCE = Path('/Users/hanqin/Documents/SAE旗舰系列多语言/电影解读/多语言')
LANGS = ('de','fr','es','ja','ko')
def sha(raw): return hashlib.sha256(raw).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--batch',type=int,default=1);args=parser.parse_args()
    assert args.batch>0
    assert (args.batch-1)*5 < 59, 'No source films in this batch.'
    receipt = DATA/f'batch{args.batch:02}-received.json'
    assert not receipt.exists(), 'Import already exists; do not overwrite reviewed manuscripts.'
    result = {'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'films':[], 'protected':{}, 'files':{}}
    for number in range((args.batch-1)*5+1,min(args.batch*5,59)+1):
        matches=list(SOURCE.glob(f'F{number:02}_*'));assert len(matches)==1
        source=matches[0];slug=source.name.split('_',1)[1]
        # Verify the producer's checksum manifest before copying any manuscript.
        for line in (source/'SHA256SUMS.txt').read_text().splitlines():
            if not line.strip():continue
            digest,relative=line.split(maxsplit=1);p=source/relative.lstrip('*')
            assert p.resolve().is_relative_to(source.resolve())
            assert sha(p.read_bytes())==digest,(p,'checksum mismatch')
        film = {'slug':slug,'number':number,'chapters':[]}
        for path in sorted((ROOT/'essays/film'/slug).rglob('*')):
            if path.is_file(): result['protected'][str(path.relative_to(ROOT))] = sha(path.read_bytes())
        for n in range(1,4):
            matches=list((ROOT/'essays/film'/slug).glob(f'{n}-*.html'))
            assert len(matches)==1
            film['chapters'].append(matches[0].stem)
        result['films'].append(film)
        for path in sorted(source.rglob('*.md')):
            relative=path.relative_to(source)
            raw=path.read_bytes();dest=DATA/'received'/slug/relative
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
            result['files'][str(dest.relative_to(DATA))]={'source':str(path.relative_to(SOURCE)),'sha256':sha(raw)}
            if relative.parts[0].lower() in LANGS or path.name in ('README.md','INDEX.md'):
                normalized=Path(relative.parts[0].lower(),*relative.parts[1:]) if len(relative.parts)>1 else relative
                target=DATA/'reviewed'/slug/normalized
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f'Imported {len(result["films"])} films; immutable received files, editable review copies, original-site baseline recorded.')

if __name__=='__main__':main()
