#!/usr/bin/env python3
"""Import delivered anime manuscripts without modifying the delivery packages."""
import hashlib
import os
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/anime-full'
SOURCE = Path('/Users/hanqin/Documents/SAE旗舰系列多语言/动漫解读')
LANGS = ('de', 'fr', 'es', 'ja', 'ko')
BATCH = os.environ.get('ANIME_BATCH', '01')
assert BATCH in ('01', '02', '03'), BATCH
PACKAGES = {
    'kimetsu': 'Demon_Slayer_Five_Languages.zip',
    'frieren': 'Frieren_Five_Languages.zip',
    'aot': 'Attack_on_Titan_Five_Languages.zip',
    'geass': 'A04_Code_Geass_DE_FR_ES_JA_KO.zip',
    'monster': 'Monster_five_languages.zip',
}
if BATCH == '02':
    PACKAGES = {
        'psycho-pass': 'A06_PSYCHO-PASS_DE-FR-ES-JA-KO.zip',
        'run-with-the-wind': 'A07_Run_with_the_Wind_DE_FR_ES_JA_KO.zip',
        'parasyte': 'A08_Parasyte_DE_FR_ES_JA_KO.zip',
        'chainsaw-man': 'A09_chainsaw-man_five-language.zip',
        'legend-of-the-galactic-heroes': 'A10_legend-of-the-galactic-heroes_five_languages.zip',
    }

if BATCH == '03':
    PACKAGES = {
        'in-this-corner-of-the-world': 'A11_in-this-corner-of-the-world_five_languages.zip',
        'ghost-in-the-shell-sac': 'A12_ghost-in-the-shell-sac_five_languages.zip',
        'neon-genesis-evangelion': 'A13_neon-genesis-evangelion_5lang.zip',
        'march-comes-in-like-a-lion': 'A14_march-comes-in-like-a-lion_5lang.zip',
        'the-tatami-galaxy': 'A15_the-tatami-galaxy_5lang.zip',
    }

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main():
    receipt = DATA / f'batch{BATCH}-received.json'
    assert not receipt.exists(), 'Do not overwrite reviewed copies.'
    result = {'baseline_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
              'series': [], 'protected': {}, 'files': {}, 'packages': {}}
    for slug, name in PACKAGES.items():
        package = SOURCE / name
        result['packages'][name] = sha(package.read_bytes())
        category = 'anime' if BATCH == '03' or slug in ('parasyte','chainsaw-man','legend-of-the-galactic-heroes') else 'literature'
        root = ROOT / 'essays' / category / slug
        chapters = [p.stem for p in sorted(root.glob('[1-9]*.html'))]
        assert len(chapters) == {'frieren':4,'in-this-corner-of-the-world':3,'the-tatami-galaxy':4}.get(slug,5), (slug, chapters)
        result['series'].append({'slug': slug, 'route': str(root.relative_to(ROOT)), 'chapters': chapters})
        for p in sorted(root.rglob('*')):
            if not p.is_file(): continue
            relative = p.relative_to(root)
            if relative.parts[0] in LANGS:
                if p.suffix == '.html':
                    dest = DATA / 'templates' / slug / relative
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(p.read_bytes())
            else:
                result['protected'][str(p.relative_to(ROOT))] = sha(p.read_bytes())
                if BATCH in ('02', '03') and p.suffix == '.html':
                    dest = DATA / 'templates' / slug / relative
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(p.read_bytes())
        with ZipFile(package) as z:
            names = set(z.namelist())
            for n in sorted(names):
                if PurePosixPath(n).name != 'SHA256SUMS.txt': continue
                for line in z.read(n).decode().splitlines():
                    m = re.fullmatch(r'([0-9a-f]{64})\s+\*?(.+)', line)
                    assert m, (name, line)
                    choices = [m[2], str(PurePosixPath(n).parent / m[2])]
                    target = next(v for v in choices if v in names)
                    assert sha(z.read(target)) == m[1], (name, target)
            for n in sorted(names):
                parts = PurePosixPath(n).parts
                assert not n.startswith('/') and '..' not in parts
                if not n.endswith('.md'): continue
                raw = z.read(n)
                dest = DATA / 'received' / slug / n
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
                result['files'][str(dest.relative_to(DATA))] = sha(raw)
                lang = next((p.lower() for p in parts[:-1] if p.lower() in LANGS), None)
                if lang:
                    match = re.match(r'(?:EP)?(\d+)', parts[-1], re.I)
                    assert match, n
                    ep = int(match[1])
                    assert 1 <= ep <= len(chapters), n
                    target = DATA / 'reviewed' / slug / lang / f'EP{ep:02}.md'
                    assert not target.exists(), target
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(raw)
        for lang in LANGS:
            assert len(list((DATA/'reviewed'/slug/lang).glob('EP*.md'))) == len(chapters)
    receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('Imported',len(result['series']),'series;',sum(len(s['chapters'])*len(LANGS) for s in result['series']),'manuscripts; received copies and original editions protected.')

if __name__ == '__main__': main()
