#!/usr/bin/env python3
"""Read-only archive import; prepare original snapshots and editable full texts.

Never executes archive contents, overwrites reviewed files, or publishes pages.
Archive headers/footers are retained in the receipt rather than article bodies.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile

from test_daodejing_sources import Page

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/president-full'
LANGS = ('de', 'fr', 'es', 'ja', 'ko')


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode()).hexdigest()


def body_fragment(source, lang):
    node = next(n for n in Page(source).nodes
                if n.has_class('essay-body') and n.has_class('lang-' + lang))
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    start = offsets[node.start[0]-1] + node.start[1]
    end = offsets[node.end[0]-1] + node.end[1]
    return source[source.index('>', start)+1:end]


def prepare(folder, start, end, batch):
    receipt = {'batch': batch, 'episodes': list(range(start, end+1)),
               'baseline_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
               'archives': {}, 'manuscripts': {}, 'originals': {}}
    pending = {}
    for number in range(start, end+1):
        ep = f'ep{number:02}'
        page = ROOT / f'essays/president/{ep}.html'
        for lang in ('zh','en'):
            fragment = body_fragment(page.read_text(), lang)
            key = f'{ep}.{lang}'
            pending[DATA / f'{key}.json'] = json.dumps(fragment, ensure_ascii=False)+'\n'
            receipt['originals'][key] = {'sha256':sha(fragment), 'page_sha256':sha(page.read_bytes())}
        archive = folder / f'NonDubito_President_EP{number:02}_DE_FR_ES_JA_KO_v1.0.zip'
        with ZipFile(archive) as zipped:
            assert zipped.testzip() is None, archive
            receipt['archives'][ep] = {'name':archive.name, 'sha256':sha(archive.read_bytes()),
                'notes': {n:zipped.read(n).decode('utf-8-sig') for n in zipped.namelist() if n == 'notes.md'}}
            for lang in LANGS:
                names = [n for n in zipped.namelist() if n.endswith('_'+lang+'.md')]
                assert len(names)==1, (ep,lang)
                raw = zipped.read(names[0]); source = raw.decode('utf-8-sig')
                titles = re.findall(r'^# (.+)$',source,re.M)
                assert len(titles)==1, (ep,lang,'title')
                blocks = list(re.finditer(r'\S[\s\S]*?(?=\n\s*\n|\Z)',source))
                # Some batches start immediately with section I, and East Asian
                # opening paragraphs can be shorter than 160 characters.
                first = next(m for m in blocks if m[0].startswith('## ') or
                             (len(m[0])>160 and not m[0].startswith(('#','['))
                              and 'https://' not in m[0] and 'Han Qin' not in m[0]))
                footer = next(m for m in blocks if m.start()>first.end()
                              and re.search(r'\]\(https://nondubito.net/essays/president/ep\d+\.html\)',m[0]))
                body = source[first.start():footer.start()].strip()
                expected = len(re.findall(r'<h3\b', body_fragment(page.read_text(), 'zh')))
                assert len(re.findall(r'^## ',body,re.M)) == expected, (ep,lang,'sections')
                text = '# '+titles[0]+'\n\n'+body+'\n'
                key = f'{ep}.{lang}'
                pending[DATA / f'{key}.md'] = text
                receipt['manuscripts'][key] = {'archive_member':names[0], 'received_sha256':sha(raw),
                    'normalized_sha256':sha(text), 'removed_header':source[:first.start()],
                    'removed_footer':source[footer.start():], 'sections':len(re.findall(r'^## ',body,re.M))}
    pending[DATA / f'{batch}-received.json'] = json.dumps(receipt,ensure_ascii=False,indent=2)+'\n'
    return pending


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path); parser.add_argument('--start',type=int,required=True)
    parser.add_argument('--end',type=int,required=True); parser.add_argument('--batch',required=True)
    parser.add_argument('--prepare',action='store_true'); args=parser.parse_args()
    pending=prepare(args.folder,args.start,args.end,args.batch)
    assert not any(p.exists() for p in pending), 'Already imported; never overwrite reviewed prose'
    for path,text in pending.items():
        if path.suffix=='.md': print(path.name, len(text), text.splitlines()[2][:65])
    if args.prepare:
        DATA.mkdir(parents=True,exist_ok=True)
        for path,text in pending.items(): path.write_text(text)
    print(('Prepared' if args.prepare else 'Validated')+f' {len(pending)} files')


if __name__=='__main__': main()
