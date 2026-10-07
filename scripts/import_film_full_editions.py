#!/usr/bin/env python3
"""One-time, byte-preserving import of film batch 01; never edit the delivery."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'data/film-full'
SOURCE = Path('/Users/hanqin/Documents/SAE旗舰系列多语言/电影解读/多语言')
LANGS = ('de','fr','es','ja','ko')
FILMS = ('shawshank','farewell-concubine','forrest-gump','titanic','leon')
def sha(raw): return hashlib.sha256(raw).hexdigest()

def main():
    receipt = DATA/'batch01-received.json'
    assert not receipt.exists(), 'Import already exists; do not overwrite reviewed manuscripts.'
    result = {'baseline_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'films':[], 'protected':{}, 'files':{}}
    for number,slug in enumerate(FILMS,1):
        source = SOURCE/f'F{number:02}_{slug}'
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
            if relative.parts[0] in LANGS or path.name=='README.md':
                target=DATA/'reviewed'/slug/relative
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Imported five films; immutable received files, editable review copies, original-site baseline recorded.')

if __name__=='__main__':main()
